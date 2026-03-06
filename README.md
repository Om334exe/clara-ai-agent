# Clara Answers – Zero-Cost Automation Pipeline

> AI-powered voice agent onboarding automation for service trade businesses.
> Built for the Clara Answers Intern Assignment.

---

## What This Does

This pipeline converts messy, real-world demo and onboarding call transcripts into production-ready **Retell AI Voice Agent** configurations — automatically, at zero cost.

```
Demo Call Transcript   →  Account Memo v1  →  Retell Agent Spec v1 (Draft)
Onboarding Transcript  →  Account Memo v2  →  Retell Agent Spec v2 (Production)
                                              + changes.md (Changelog)
```

---

## Architecture & Data Flow

```
data/
  demo/          ← Drop .txt transcripts (or audio files) here
  onboarding/    ← Drop .txt transcripts here

scripts/
  extract_memo_v1.py      ← Demo transcript → memo_v1.json
  generate_agent_v1.py    ← memo_v1.json → agent_v1.json (Retell Draft)
  update_memo_v2.py       ← Onboarding transcript + memo_v1 → memo_v2 + changes.md
  generate_agent_v2.py    ← memo_v2.json → agent_v2.json (Retell Production)
  process_all.sh          ← Orchestrator: runs all accounts end-to-end
  generate_synthetic_data.py ← Generates sample transcripts for testing

workflows/
  clara_pipeline.json     ← n8n workflow export (importable)

outputs/
  accounts/
    <account_id>/
      v1/ memo_v1.json, agent_v1.json
      v2/ memo_v2.json, agent_v2.json, changes.md

task_tracker.log          ← Audit log for all pipeline runs
```

---

## Quick Start

### Prerequisites
- Python 3.8+
- bash

### 1. Install Dependencies
```bash
pip install openai-whisper  # Only needed if transcribing audio
```

### 2. Add Your Input Files

**If you have transcripts (`.txt`):**  
Place demo transcripts as: `data/demo/account_<id>_demo.txt`  
Place onboarding transcripts as: `data/onboarding/account_<id>_onboarding.txt`

**If you have audio files (`.mp3`, `.m4a`, `.mp4`):**  
Place audio in `data/demo/` or `data/onboarding/`, then run:
```bash
python3 scripts/transcribe_audio.py data/demo/account_1_demo.m4a
```

**To use sample synthetic data:**
```bash
python3 scripts/generate_synthetic_data.py
```

### 3. Run the Full Pipeline
```bash
chmod +x scripts/process_all.sh
./scripts/process_all.sh
```

The script will automatically detect all accounts in `data/demo/` and process them end-to-end.

### 4. View Outputs
```
outputs/accounts/1/v1/memo_v1.json     ← Extracted account memo (demo)
outputs/accounts/1/v1/agent_v1.json    ← Retell agent spec (draft)
outputs/accounts/1/v2/memo_v2.json     ← Updated memo (post-onboarding)
outputs/accounts/1/v2/agent_v2.json    ← Retell agent spec (production)
outputs/accounts/1/v2/changes.md       ← Changelog (what changed & why)
```

---

## Retell Integration

Since Retell's programmatic agent creation requires a paid plan, use the **manual import method**:

1. Open your [Retell Dashboard](https://retell.ai/)
2. Click **Create Agent**
3. Open `outputs/accounts/<id>/v2/agent_v2.json`
4. Copy the value of `system_prompt` → paste into Retell's System Prompt field
5. Set the voice to match `voice` field
6. Save — your agent is production-ready!

---

## n8n Setup

1. Install n8n locally: `npx n8n` or via Docker:
   ```bash
   docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
   ```
2. Open `http://localhost:5678`
3. Import `workflows/clara_pipeline.json`
4. The workflow calls `process_all.sh` to run the full batch

---

## Account Memo Schema

```json
{
  "account_id": "1",
  "company_name": "...",
  "business_hours": "Mon-Fri, 8am-5pm ET",
  "office_address": "...",
  "services_supported": ["...", "..."],
  "emergency_definition": ["...", "..."],
  "emergency_routing_rules": "...",
  "non_emergency_routing_rules": "...",
  "call_transfer_rules": "...",
  "integration_constraints": ["..."],
  "after_hours_flow_summary": "...",
  "office_hours_flow_summary": "...",
  "questions_or_unknowns": ["..."],
  "notes": "..."
}
```

---

## Agent Prompt Flows

Every generated agent strictly follows:

**Business Hours:**  
Greeting → Ask purpose → Name & Number → Transfer → Fallback if fail → Anything else? → Close

**After Hours:**  
Greeting → Ask purpose → Confirm emergency → (Emergency) Collect name/number/address → Transfer → Fallback → (Non-Emergency) Collect & confirm follow-up → Anything else? → Close

---

## Known Limitations

| Limitation | Notes |
|---|---|
| Transcript quality | Extraction is heuristic-based. High-quality transcripts improve accuracy. |
| Audio transcription | Whisper `base` model is used for free local STT. Slower on CPU. |
| Retell API | Free tier does not support programmatic agent creation. Manual import required. |
| Fireflies.ai | Transcripts cannot be scraped automatically (JS-gated). Manual export needed. |

---

## What I'd Improve with Production Access

1. **Use Retell's API** to auto-deploy agent specs directly
2. **Use Fireflies or AssemblyAI API** for faster, higher-quality transcription
3. **Add an LLM extraction pass** (e.g., GPT-4o with structured output) for better NLP
4. **Supabase storage** for multi-user, multi-tenant account management
5. **Webhook triggers** so onboarding form submissions auto-trigger v2 generation

---

## Zero-Cost Stack Summary

| Component | Tool | Cost |
|---|---|---|
| Transcription | OpenAI Whisper (local) | $0 |
| Extraction | Python regex + heuristics | $0 |
| Agent templating | Python f-strings | $0 |
| Orchestration | bash + n8n (local Docker) | $0 |
| Storage | Local JSON files | $0 |
| Task tracking | Local log file | $0 |
| Repository | GitHub (public) | $0 |

---

## Repository Structure

```
.
├── data/
│   ├── demo/            ← Demo call transcripts
│   └── onboarding/      ← Onboarding call transcripts
├── scripts/
│   ├── extract_memo_v1.py
│   ├── generate_agent_v1.py
│   ├── update_memo_v2.py
│   ├── generate_agent_v2.py
│   ├── process_all.sh
│   └── generate_synthetic_data.py
├── workflows/
│   └── clara_pipeline.json
├── outputs/
│   └── accounts/<id>/v1 and v2
├── .gitignore
└── README.md
```
