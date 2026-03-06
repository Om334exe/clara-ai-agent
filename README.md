# Clara Answers Zero-Cost Automation Pipeline

This project simulates the automation pipeline for Clara Answers, migrating raw demo and onboarding transcripts into structured Retell Agent constraints.

## Goal
To predictably ingest client requirements and generate a customized, prompt-hygienic AI Voice Agent configuration for Retell. This implementation is constrained to be strictly **zero-cost**.

## Architecture

This pipeline avoids expensive LLM calls by leveraging robust Python scripts with heuristic extraction and template generation.
1. `generate_synthetic_data.py`: A helper script that populated our `/data/demo` and `/data/onboarding` directories with 5 realistic transcripts each.
2. `extract_memo_v1.py`: Parses Demo call transcripts to extract rules, business hours, and routing into `memo_v1.json`.
3. `generate_agent_v1.py`: Uses `memo_v1.json` to generate the Retell Agent Spec (`agent_v1.json`).
4. `update_memo_v2.py`: Parses Onboarding updates, diffs them against `memo_v1.json`, generates `memo_v2.json`, and records differences in `changes.md`.
5. `generate_agent_v2.py`: Generates the production-ready `agent_v2.json`.

Outputs are robustly stored in `outputs/accounts/<account_id>/`.
Task creation is mocked via `outputs/task_tracker.log`.

## Setup & Running

**Prerequisites:** Python 3.

### 1. Generating Data
The dataset of 5 demo and 5 onboarding files is already provided in `data/demo` and `data/onboarding`. If missing, simply run:
```bash
python3 scripts/generate_synthetic_data.py
```

### 2. Execution (Bash Orchestrator)
You can run the full end-to-end pipeline instantly via:
```bash
chmod +x scripts/process_all.sh
./scripts/process_all.sh
```

### 3. Execution (n8n Execution)
We have included a mock `workflows/clara_pipeline.json`. To use:
1. Import into a local free-tier n8n Docker instance.
2. The pipeline triggers the bash fallback script to sequentially extract, update, and deploy. 

## Retell Setup Directions
Since programmatic access to Retell requires a paid plan, configuring the agent is a simple manual copy-paste:
1. Log into your Retell Dashboard.
2. Hit "Create Agent".
3. For Account 1, open `outputs/accounts/1/v2/agent_v2.json`. 
4. Copy the `system_prompt` value into the Retell System Prompt Field.
5. Select the exact voice logged in the JSON.
6. The agent is now production-ready and fully aligned with onboarding! 
