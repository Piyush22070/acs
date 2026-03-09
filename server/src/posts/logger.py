import logging
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinel_target_app")

def log_event(level, event_type, message, data=None):
    """
    Creates a structured JSON log that the Agent can easily parse.
    """
    log_entry = {
        "event": event_type,      # e.g., "DB_ERROR", "PAYMENT_INIT"
        "message": message,       # Human readable
        "data": data or {},       # Context (IDs, amounts, IPs)
        "severity": level         # INFO, WARNING, ERROR, CRITICAL
    }

    if level == "ERROR":
        logger.error(json.dumps(log_entry))
    elif level == "WARNING":
        logger.warning(json.dumps(log_entry))
    else:
        logger.info(json.dumps(log_entry))