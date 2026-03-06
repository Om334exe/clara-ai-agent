import os
import sys
import json
import re

def extract_memo_v1(account_id, transcript_path):
    with open(transcript_path, 'r') as f:
        text = f.read()

    memo = {
        "account_id": account_id,
        "company_name": "Unknown",
        "business_hours": "Unknown",
        "office_address": "Unknown",
        "services_supported": [],
        "emergency_definition": [],
        "emergency_routing_rules": "Unknown",
        "non_emergency_routing_rules": "Take a message",
        "call_transfer_rules": "Default 30s timeout",
        "integration_constraints": [],
        "after_hours_flow_summary": "Route emergencies, take message for others",
        "office_hours_flow_summary": "Handle calls according to routing rules",
        "questions_or_unknowns": [],
        "notes": "Generated from Demo call"
    }

    # very simple heuristic extraction
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if "from" in line_lower and "client:" in line_lower and len(memo["company_name"]) == 7: # unknown
            match = re.search(r"from\s+([a-zA-Z0-9\s']+)", line)
            if match:
                memo["company_name"] = match.group(1).split('.')[0].strip()
            elif "with" in line_lower:
                match = re.search(r"with\s+([a-zA-Z0-9\s']+)", line)
                if match:
                    memo["company_name"] = match.group(1).split('.')[0].strip()

        if "hours" in line_lower or "overnight" in line_lower or "open" in line_lower:
            if "client:" in line_lower:
                memo["business_hours"] = line.replace("Client:", "").strip()
            elif i + 1 < len(lines) and "client:" in lines[i+1].lower():
                memo["business_hours"] = lines[i+1].replace("Client:", "").strip()

        if "emergency" in line_lower or "emergencies" in line_lower:
            if "route" in line_lower or "routing" in line_lower or "send" in line_lower:
                if "client:" in line_lower and len(line) > 15:
                    memo["emergency_routing_rules"] = line.replace("Client:", "").strip()
                elif i + 1 < len(lines) and "client:" in lines[i+1].lower():
                    memo["emergency_routing_rules"] = lines[i+1].replace("Client:", "").strip()
            elif "what" in line_lower or "?" in line_lower:
                if i + 1 < len(lines) and "client:" in lines[i+1].lower():
                    memo["emergency_definition"].append(lines[i+1].replace("Client:", "").strip())
            elif "client:" in line_lower:
                memo["emergency_definition"].append(line.replace("Client:", "").strip())

        if "services" in line_lower:
            if "client:" in line_lower and len(line) > 15:
                memo["services_supported"].append(line.replace("Client:", "").strip())
            elif i + 1 < len(lines) and "client:" in lines[i+1].lower():
                memo["services_supported"].append(lines[i+1].replace("Client:", "").strip())
                
        if "non-emergencies" in line_lower:
             if i + 1 < len(lines) and "client:" in lines[i+1].lower():
                 memo["non_emergency_routing_rules"] = lines[i+1].replace("Client:", "").strip()

    if memo["company_name"] == "Unknown":
        # fallback
        for line in lines:
            if "Client:" in line:
                memo["company_name"] = line.replace("Client:", "").strip()
                break

    output_dir = f"outputs/accounts/{account_id}/v1"
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/memo_v1.json", "w") as f:
        json.dump(memo, f, indent=4)
        
    print(f"[{account_id}] Extracted memo v1 to {output_dir}/memo_v1.json")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_memo_v1.py <account_id> <transcript_path>")
        sys.exit(1)
    extract_memo_v1(sys.argv[1], sys.argv[2])
