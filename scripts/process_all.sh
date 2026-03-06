#!/bin/bash
set -e

# Setup mock task tracker
TASK_LOG="outputs/task_tracker.log"
mkdir -p outputs/accounts
echo "Clara Answers Automation Run - $(date)" > $TASK_LOG

echo "Starting Orchestration Pipeline..."

for demo_file in data/demo/account_*_demo.txt; do
  # Extract account ID from filename
  filename=$(basename "$demo_file")
  i=$(echo "$filename" | grep -o -E '[0-9]+')

  echo "--- Processing Account $i ---"
  
  # Pipeline A: Demo Call -> Preliminary Agent
  echo "[Pipeline A] Extracting Demo info for Account $i..."
  python3 scripts/extract_memo_v1.py "$i" "data/demo/account_${i}_demo.txt"
  
  echo "[Pipeline A] Generating Retell Agent v1 for Account $i..."
  python3 scripts/generate_agent_v1.py "$i"
  
  # Log task
  echo "Task created: Review Demo Agent v1 for Account $i" >> $TASK_LOG
  
  # Pipeline B: Onboarding Call -> Agent Modification
  echo "[Pipeline B] Extracting Onboarding modifiers for Account $i..."
  python3 scripts/update_memo_v2.py "$i" "data/onboarding/account_${i}_onboarding.txt"
  
  echo "[Pipeline B] Generating Retell Agent v2 for Account $i..."
  python3 scripts/generate_agent_v2.py "$i"
  
  # Log task update
  echo "Task completed/updated: Agent v2 generated for Account $i" >> $TASK_LOG
done

echo ""
echo "Pipeline execution finished successfully."
echo "Check outputs/accounts/ for the generated memos, agents, and changelogs."
