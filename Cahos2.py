import asyncio
import aiohttp
import subprocess
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000/"

def log(tag: str, msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    colors = {
        "CHAOS": "\033[91m",
        "INFO":  "\033[94m",
        "SCALE": "\033[92m",
        "WARN":  "\033[93m",
        "RESET": "\033[0m",
    }
    color = colors.get(tag, colors["INFO"])
    print(f"{color}[{ts}][{tag}]{colors['RESET']} {msg}")

def kubectl(cmd: str) -> str:
    try:
        result = subprocess.run(
            f"kubectl {cmd}", shell=True,
            capture_output=True, text=True, timeout=15
        )
        return result.stdout.strip() or result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "kubectl timeout"

async def attack_traffic(session: aiohttp.ClientSession, duration_seconds: int = 10):
    log("CHAOS", f"Sending attack traffic for {duration_seconds} seconds to generate error logs...")
    end_time = time.time() + duration_seconds
    
    async def single_request():
        try:
            async with session.get(f"{BASE_URL}/payments?page=1", timeout=1) as r:
                return r.status
        except Exception:
            return 0

    while time.time() < end_time:
        tasks = [single_request() for _ in range(20)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.5)

async def nuke_database(session: aiohttp.ClientSession):
    log("INFO", "\nSCENARIO 1: Nuking the database + Traffic Attack...")
    out = kubectl("delete pod postgres-0 -n default --grace-period=0 --force")
    log("CHAOS", f"   DB NUKE: {out}")
    log("CHAOS", "   StatefulSet will recreate it — hitting backend to force DB errors...")
    await attack_traffic(session, duration_seconds=15)

async def crash_backend(session: aiohttp.ClientSession):
    log("INFO", "\nSCENARIO 2: Crashing the backend pod + Traffic Attack...")
    pod = kubectl("get pods -l app=acs-backend -n default -o jsonpath='{.items[0].metadata.name}'")
    if pod:
        out = kubectl(f"delete pod {pod} -n default --grace-period=0 --force")
        log("CHAOS", f"   BACKEND CRASH: {out}")
        log("CHAOS", "   Deployment will recreate it — hitting frontend to force 502/503 errors...")
        await attack_traffic(session, duration_seconds=15)
    else:
        log("WARN", "   No acs-backend pod found")

async def trigger_hpa(session: aiohttp.ClientSession):
    log("INFO", "\nSCENARIO 3: Triggering HPA (Elasticity/Scalability test)...")
    log("CHAOS", "   Flooding backend with requests to spike CPU...")
    end_time = time.time() + 30
    
    async def fast_request():
        try:
            async with session.get(f"{BASE_URL}/", timeout=0.5) as r:
                return r.status
        except Exception:
            return 0

    while time.time() < end_time:
        tasks = [fast_request() for _ in range(100)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.1)

async def sql_injection_attack(session: aiohttp.ClientSession):
    log("INFO", "\nSCENARIO 4: SQL Injection Attack...")
    payloads = [
        "' OR '1'='1",
        "\" OR \"1\"=\"1",
        "admin' --",
        "' OR SLEEP(5) --",
        "1; DROP TABLE users",
        "' UNION SELECT null, null, null --"
    ]
    log("CHAOS", f"   Sending {len(payloads)} SQLi payloads to backend...")
    
    async def send_sqli(payload):
        try:
            async with session.post(f"{BASE_URL}/login", json={"username": payload, "password": "pwd"}, timeout=2) as r:
                return r.status
        except Exception:
            return 0

    tasks = [send_sqli(p) for p in payloads]
    await asyncio.gather(*tasks)

def observe_scale():
    log("SCALE", "Current cluster state:")
    pods = kubectl("get pods -n default")
    for line in pods.splitlines():
        log("SCALE", f"   {line}")

async def run_chaos():
    log("INFO", "=" * 60)
    log("INFO", "  CHAOS RUNNER — Agentic Infra Stress Test (Focused Mode)")
    log("INFO", "  Target: Minikube transaction app")
    log("INFO", "  Agent:  Sentinel ACS (Must be running)")
    log("INFO", "=" * 60)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/sentinel/health", timeout=aiohttp.ClientTimeout(total=3)) as r:
                log("INFO", f"App reachable — HTTP {r.status}")
    except Exception:
        log("WARN", f"Cannot reach {BASE_URL}. Run:")
        log("WARN", "   kubectl port-forward svc/acs-backend 8000:8000")
        sys.exit(1)

    observe_scale()

    connector = aiohttp.TCPConnector(limit=500)
    async with aiohttp.ClientSession(connector=connector) as session:
        await nuke_database(session)
        log("INFO", "   Waiting 45s — Sentinel should detect DB_CONNECTION_FAIL and restart backend...")
        for i in range(9):
            await asyncio.sleep(5)
            if i % 3 == 0:
                observe_scale()

        await crash_backend(session)
        log("INFO", "   Waiting 45s — Sentinel should detect cascading failures...")
        for i in range(9):
            await asyncio.sleep(5)
            if i % 3 == 0:
                observe_scale()

        await trigger_hpa(session)
        log("INFO", "   Waiting 30s — HPA should scale up pods...")
        for i in range(6):
            await asyncio.sleep(5)
            if i % 3 == 0:
                observe_scale()

        await sql_injection_attack(session)
        await asyncio.sleep(5)

    log("INFO", "\nChaos run complete. Final cluster state:")
    observe_scale()

if __name__ == "__main__":
    asyncio.run(run_chaos())