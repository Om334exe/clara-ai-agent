import os
import sys
import json
import re
from datetime import datetime

def update_memo_v2(account_id, transcript_path):
    v1_path = f"outputs/accounts/{account_id}/v1/memo_v1.json"
    if not os.path.exists(v1_path):
        print(f"Error: Memo v1 not found for account {account_id}")
        sys.exit(1)

    with open(v1_path, 'r') as f:
        memo_v1 = json.load(f)

    with open(transcript_path, 'r') as f:
        text = f.read()

    memo_v2 = memo_v1.copy()
    changes = []
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_lower = line.lower()

        # Update Emergency Routing
        if "emergency" in line_lower and ("route" in line_lower or "number" in line_lower or "directly to" in line_lower):
            if "client:" in line_lower:
                new_val = line.replace("Client:", "").strip()
                if new_val != memo_v1.get("emergency_routing_rules"):
                    changes.append(f"- **Emergency Routing**: Changed from '{memo_v1.get('emergency_routing_rules')}' to '{new_val}'")
                    memo_v2["emergency_routing_rules"] = new_val
            elif i + 1 < len(lines) and "client:" in lines[i+1].lower():
                new_val = lines[i+1].replace("Client:", "").strip()
                if new_val != memo_v1.get("emergency_routing_rules"):
                    changes.append(f"- **Emergency Routing**: Changed from '{memo_v1.get('emergency_routing_rules')}' to '{new_val}'")
                    memo_v2["emergency_routing_rules"] = new_val

        # Update Transfer Fallbacks
        if "fallback" in line_lower or "transfer fails" in line_lower:
            if "client:" in line_lower:
                new_val = line.replace("Client:", "").strip()
                changes.append(f"- **Call Transfer Rules / Fallback**: Updated to '{new_val}'")
                memo_v2["call_transfer_rules"] = new_val
            elif i + 1 < len(lines) and "client:" in lines[i+1].lower():
                new_val = lines[i+1].replace("Client:", "").strip()
                changes.append(f"- **Call Transfer Rules / Fallback**: Updated to '{new_val}'")
                memo_v2["call_transfer_rules"] = new_val

        # Update Constraints
        if "don't" in line_lower or "never" in line_lower or "make sure" in line_lower:
            if "client:" in line_lower:
                constraint = line.replace("Client:", "").strip()
                memo_v2["integration_constraints"].append(constraint)
                changes.append(f"- **Integration Constraints**: Added '{constraint}'")
            elif i + 1 < len(lines) and "client:" in lines[i+1].lower():
                pass

        # Update Hours
        if "hours" in line_lower and "actually" in line_lower:
            if "client:" in line_lower:
                new_val = line.replace("Client:", "").strip()
                changes.append(f"- **Business Hours**: Changed from '{memo_v1.get('business_hours')}' to '{new_val}'")
                memo_v2["business_hours"] = new_val
                
        # Non emergencies
        if "non-emergencies" in line_lower or "non emergencies" in line_lower:
            if i + 1 < len(lines) and "client:" in lines[i+1].lower():
                new_val = lines[i+1].replace("Client:", "").strip()
                changes.append(f"- **Non-Emergency Routing**: Updated to '{new_val}'")
                memo_v2["non_emergency_routing_rules"] = new_val
                
        # Services removed
        if "don't do" in line_lower and "anymore" in line_lower:
            if "client:" in line_lower:
                new_val = line.replace("Client:", "").strip()
                changes.append(f"- **Services**: Noted removal constraint '{new_val}'")
                memo_v2["integration_constraints"].append(new_val)

    memo_v2["notes"] = "Updated from Onboarding call"
    
    output_dir = f"outputs/accounts/{account_id}/v2"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/memo_v2.json", "w") as f:
        json.dump(memo_v2, f, indent=4)
        
    changelog_path = f"{output_dir}/changes.md"
    with open(changelog_path, "w") as f:
        f.write(f"# Changelog for Account {account_id}\n\n")
        f.write(f"Generated on: {datetime.now().isoformat()}\n\n")
        if not changes:
            f.write("No changes detected from onboarding.\n")
        else:
            f.write("\n".join(changes) + "\n")
            
    print(f"[{account_id}] Generated memo v2 to {output_dir}/memo_v2.json and changelog to {output_dir}/changes.md")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_memo_v2.py <account_id> <transcript_path>")
        sys.exit(1)
    update_memo_v2(sys.argv[1], sys.argv[2])
