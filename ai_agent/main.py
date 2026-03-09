import os
import time
import logging
from typing import TypedDict, Dict
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import httpx
from langgraph.graph import StateGraph, END

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("sentinel")

API_URL = os.getenv("API_URL", "http://acs-backend-service:8000")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NAMESPACE = os.getenv("NAMESPACE", "default")
SLEEP_INTERVAL = int(os.getenv("SLEEP_INTERVAL", "15")) 
LOG_LINES = int(os.getenv("LOG_LINES", "500"))

WATCHED_DEPLOYMENTS = ["acs-backend", "acs-frontend"]
WATCHED_PODS_PREFIX = ["acs-backend", "acs-frontend", "postgres", "redis"]


NOISE_PATTERNS = [
    "/sentinel/health", "/health", "GET /metrics", "200 OK",
    "Transparent Huge Pages", "overcommit_memory", "tcp-backlog"
]

CRITICAL_PATTERNS = [
    "ERROR", "Exception", "Traceback", "500", "503", "502",
    "OOMKilled", "CrashLoopBackOff", "Connection refused", "FATAL",
    "DB_CONNECTION_FAIL", "SQL injection", "SQLi", "syntax error"
]

GROQ_MODEL = "llama-3.3-70b-versatile"


last_restart_time = {}

class AgentState(TypedDict):
    logs_data: Dict[str, str]
    flagged_logs: Dict[str, str]
    is_issue: bool
    actions: str

def call_groq(prompt: str) -> str:
    r = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        },
        timeout=20
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def collect_node(state: AgentState) -> AgentState:
    v1 = client.CoreV1Api()
    logs_data = {}
    pods = v1.list_namespaced_pod(NAMESPACE)
    for pod in pods.items:
        name = pod.metadata.name
        if any(name.startswith(p) for p in WATCHED_PODS_PREFIX) and pod.status.phase == "Running":
            try:
                logs_data[name] = v1.read_namespaced_pod_log(name, NAMESPACE, tail_lines=LOG_LINES)
            except:
                continue
    return {"logs_data": logs_data}

def triage_node(state: AgentState) -> AgentState:
    flagged = {}
    for pod, text in state.get("logs_data", {}).items():
        if not text:
            continue
        criticals = [l for l in text.splitlines() if any(c in l for c in CRITICAL_PATTERNS) and not any(n in l for n in NOISE_PATTERNS)]
        if criticals:
            flagged[pod] = "\n".join(criticals)
            log.warning(f"Anomalies in {pod}")
    return {"flagged_logs": flagged, "is_issue": bool(flagged)}

def route_triage(state: AgentState) -> str:
    if state.get("is_issue"):
        return "analyze"
    return END

def analyze_node(state: AgentState) -> AgentState:
    system_instruction = (
        "You are an AGGRESSIVE Sentinel K8s AI. Analyze logs and output ONLY ACTIONS in this format:\n"
        "1) ACTIONS: restart_pod:<pod_name>\n"
        "2) ACTIONS: scale_deployment:<deployment_name>:<count>\n"
        "3) ACTIONS: log_attack:<details>\n"
        "\nRULES:\n"
        "- If you see 'DB_CONNECTION_FAIL', 'FATAL', or '502/503', you MUST RESTART.\n"
        "- If you see high load logs, you MUST SCALE to 3.\n"
        "- If you see ANY 'SQLi', you MUST output 'log_attack'.\n"
        "- DO NOT say 'no_action' if there is a warning."
    )
    prompt = f"{system_instruction}\nLogs:\n{state.get('flagged_logs')}"
    res = call_groq(prompt)
    if res:
        log.info(f"AI Strategy: {res}")
    return {"actions": res or ""}

def execute_node(state: AgentState) -> AgentState:
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()
    current_time = time.time()
    
    for line in state.get("actions", "").splitlines():
        if "ACTIONS:" in line:
            actions_part = line.split("ACTIONS:")[1].strip()
            actions_list = [a.strip() for a in actions_part.split(",")]
            for action in actions_list:
                if "restart_pod:" in action:
                    p_name = action.split(":")[1]
                    
                    # COOLDOWN: Extract pod type (e.g., redis) and check timer
                    pod_type = p_name.split("-")[0]
                    if current_time - last_restart_time.get(pod_type, 0) < 300:
                        log.info(f"Skipping restart for {p_name} (Cooldown active for {pod_type})")
                        continue
                    
                    try:
                        v1.delete_namespaced_pod(p_name, NAMESPACE, body=client.V1DeleteOptions(grace_period_seconds=0))
                        log.info(f"Restarted {p_name}")
                        last_restart_time[pod_type] = current_time
                    except ApiException:
                        log.error(f"Could not find {p_name}")
                elif "scale_deployment:" in action:
                    parts = action.split(":")
                    if len(parts) == 3:
                        d_name, count = parts[1], parts[2]
                        try:
                            apps_v1.patch_namespaced_deployment_scale(d_name, NAMESPACE, body={"spec": {"replicas": int(count)}})
                            log.info(f"Scaled {d_name} to {count}")
                        except ApiException:
                            log.error(f"Scaling failed for {d_name}")
                elif "log_attack:" in action:
                    msg = action.split(":", 1)[1]
                    log.critical(f"ATTACK DETECTED: {msg}")
    return state

def run():
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()

    workflow = StateGraph(AgentState)
    workflow.add_node("collect", collect_node)
    workflow.add_node("triage", triage_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("execute", execute_node)

    workflow.set_entry_point("collect")
    workflow.add_edge("collect", "triage")
    workflow.add_conditional_edges("triage", route_triage)
    workflow.add_edge("analyze", "execute")
    workflow.add_edge("execute", END)

    app = workflow.compile()
    log.info("Sentinel ACS Active (Aggressive Mode + Cooldown).")

    while True:
        log.info("--- SCANNING CLUSTER ---")
        app.invoke({"logs_data": {}, "flagged_logs": {}, "is_issue": False, "actions": ""})
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    run()