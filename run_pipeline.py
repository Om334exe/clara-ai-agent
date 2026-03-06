#!/usr/bin/env python3
"""
Clara AI Pipeline - Master Batch Orchestrator
Runs the full pipeline on all accounts. Idempotent, logged, retry-safe.
Usage: python run_pipeline.py [demo_dir] [onboarding_dir]
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from scripts.extract_memo_v1 import extract_memo_v1
from scripts.update_memo_v2 import update_memo_v2
from scripts.generate_agent import generate_agent_spec

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("outputs/pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("clara.pipeline")

def get_account_id(filename):
    """Extract account ID from filename like account_3_demo.txt → '3'"""
    import re
    m = re.search(r"account[_\-](\d+)", filename)
    return m.group(1) if m else None

def run_pipeline(demo_dir="data/demo", onboarding_dir="data/onboarding", force=False):
    os.makedirs("outputs/accounts", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    summary = {
        "started_at": datetime.now().isoformat(),
        "accounts": [],
        "total": 0,
        "succeeded": 0,
        "failed": 0,
        "skipped": 0,
    }

    # Find all demo files
    if not os.path.isdir(demo_dir):
        log.error(f"Demo directory not found: {demo_dir}")
        sys.exit(1)

    demo_files = sorted([
        f for f in os.listdir(demo_dir)
        if f.endswith((".txt", ".md")) and "demo" in f.lower()
    ])

    log.info(f"Found {len(demo_files)} demo transcripts in {demo_dir}")

    for demo_file in demo_files:
        account_id = get_account_id(demo_file)
        if not account_id:
            log.warning(f"Skipping {demo_file} – could not extract account ID")
            summary["skipped"] += 1
            continue

        demo_path = os.path.join(demo_dir, demo_file)
        onboarding_pattern = f"account_{account_id}_onboarding.txt"
        onboarding_path = os.path.join(onboarding_dir, onboarding_pattern)

        account_result = {
            "account_id": account_id,
            "demo_file": demo_file,
            "onboarding_file": onboarding_pattern if os.path.exists(onboarding_path) else None,
            "v1_status": None,
            "v2_status": None,
            "errors": [],
        }
        summary["total"] += 1

        log.info(f"═══ Account {account_id} ═══")

        # ── Pipeline A: Demo → v1 ──────────────────────────────────────────────
        v1_memo_path = f"outputs/accounts/{account_id}/v1/memo_v1.json"
        if os.path.exists(v1_memo_path) and not force:
            log.info(f"[{account_id}] v1 already exists (idempotent). Skipping extraction.")
            account_result["v1_status"] = "skipped (already exists)"
        else:
            try:
                extract_memo_v1(account_id, demo_path)
                generate_agent_spec(account_id, "v1")
                account_result["v1_status"] = "success"
                log.info(f"[{account_id}] ✅ v1 complete")
            except Exception as e:
                account_result["v1_status"] = f"FAILED: {e}"
                account_result["errors"].append(str(e))
                log.error(f"[{account_id}] v1 FAILED: {e}")
                summary["failed"] += 1
                summary["accounts"].append(account_result)
                continue

        # ── Pipeline B: Onboarding → v2 ───────────────────────────────────────
        v2_memo_path = f"outputs/accounts/{account_id}/v2/memo_v2.json"
        if os.path.exists(v2_memo_path) and not force:
            log.info(f"[{account_id}] v2 already exists (idempotent). Skipping onboarding update.")
            account_result["v2_status"] = "skipped (already exists)"
        elif not os.path.exists(onboarding_path):
            log.warning(f"[{account_id}] No onboarding file found at {onboarding_path} – skipping v2")
            account_result["v2_status"] = "skipped (no onboarding file)"
        else:
            try:
                update_memo_v2(account_id, onboarding_path)
                generate_agent_spec(account_id, "v2")
                account_result["v2_status"] = "success"
                log.info(f"[{account_id}] ✅ v2 complete")
            except Exception as e:
                account_result["v2_status"] = f"FAILED: {e}"
                account_result["errors"].append(str(e))
                log.error(f"[{account_id}] v2 FAILED: {e}")
                summary["failed"] += 1
                summary["accounts"].append(account_result)
                continue

        summary["succeeded"] += 1
        summary["accounts"].append(account_result)

    summary["finished_at"] = datetime.now().isoformat()

    # Write summary
    with open("outputs/batch_summary.json", "w") as f:
        json.dump(summary, f, indent=4)

    # Print table
    log.info("\n" + "═" * 60)
    log.info(f"{'ACCOUNT':<12} {'V1':<20} {'V2':<20}")
    log.info("═" * 60)
    for a in summary["accounts"]:
        log.info(f"{a['account_id']:<12} {str(a['v1_status']):<20} {str(a['v2_status']):<20}")
    log.info("═" * 60)
    log.info(f"Total: {summary['total']}  ✅ Succeeded: {summary['succeeded']}  ❌ Failed: {summary['failed']}  ⏭ Skipped: {summary['skipped']}")
    log.info("Batch summary written → outputs/batch_summary.json")

    return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clara AI – Batch Pipeline Runner")
    parser.add_argument("--demo-dir", default="data/demo", help="Path to demo transcripts directory")
    parser.add_argument("--onboarding-dir", default="data/onboarding", help="Path to onboarding transcripts directory")
    parser.add_argument("--force", action="store_true", help="Reprocess even if outputs already exist")
    args = parser.parse_args()
    run_pipeline(args.demo_dir, args.onboarding_dir, args.force)
