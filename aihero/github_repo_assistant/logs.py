import json
import os
import secrets
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(os.getenv('LOGS_DIRECTORY', 'logs'))
LOG_DIR.mkdir(exist_ok=True)


def log_entry(agent, messages, source: str="user"):
    tools = []
    for ts in agent.toolsets:
        tools.extend(ts.tools.keys())
    
    messages = json.loads(messages)

    return {
        "agent_name": agent.name,
        "system_prompt": agent._instructions,
        "provider": agent.model.system,
        "model": agent.model.model_name,
        "tools": tools,
        "messages": messages,
        "source": source
    }

def serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def log_interaction(agent, messages, source: str="user"):

    entry = log_entry(
        agent=agent,
        messages=messages,
        source=source
    )

    ts = entry["messages"][-1]['timestamp']
    ts_obj = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    ts_str = ts_obj.strftime("%Y%m%d_%H%M%S")
    rand_hex = secrets.token_hex(nbytes=3)

    filename = f"{agent.name}_{ts_str}_{rand_hex}.json"
    filepath = LOG_DIR / filename

    with open(filepath, mode='w', encoding='utf-8') as f_out:
        json.dump(obj=entry, fp=f_out, default=serializer)

    return filepath
