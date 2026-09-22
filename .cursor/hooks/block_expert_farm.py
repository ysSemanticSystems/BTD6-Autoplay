#!/usr/bin/env python3
"""Stop the unattended Expert collection loop until it is explicitly allowed."""
import json
import sys

def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"permission": "allow"}))
        return
    command = str(payload.get("command") or "")
    blocked = "play_collection_event.py" in command and "BTD6_ALLOW_FARM=1" not in command
    if blocked:
        print(json.dumps({
            "permission": "deny",
            "user_message": "The Expert collection loop is blocked. Expert maps were locked at 10/20. Prefix the command with BTD6_ALLOW_FARM=1 only after a success log says an Expert map opened.",
            "agent_message": "Blocked play_collection_event.py. Read knowledge/failures and knowledge/meta.json. Do not farm Expert until unlock progress says otherwise.",
        }))
        return
    print(json.dumps({"permission": "allow"}))


if __name__ == "__main__":
    main()
