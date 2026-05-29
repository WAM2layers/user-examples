#!/usr/bin/env python3

from pathlib import Path
import yaml
from datetime import datetime, timedelta
import subprocess
import shutil

TEMPLATE_YAML = Path("eif2.yaml")        
DATES_FILE = Path("dates_pers_d0-1.txt")
OUT_DIR = Path("configs_output”)                 
CALL_DOWNLOADER = True                    
DOWNLOADER_CMD = ["python", "download_preprocessed.py"] 

TRACKING_CMD_TEMPLATE = ["wam2layers", "track", "{cfg}"]  

OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_template(path: Path) -> dict:
    with open(path, "r") as fh:
        return yaml.safe_load(fh)

def save_config(cfg: dict, outpath: Path):
    with open(outpath, "w") as fh:
        yaml.safe_dump(cfg, fh, sort_keys=False)

def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M")

def main():
    if not TEMPLATE_YAML.exists():
        raise FileNotFoundError(f"Template YAML not found: {TEMPLATE_YAML}")

    template = load_template(TEMPLATE_YAML)

    if not DATES_FILE.exists():
        raise FileNotFoundError(f"Dates file not found: {DATES_FILE}")

    with open(DATES_FILE, "r") as fh:
        date_lines = [ln.strip() for ln in fh if ln.strip()]

    for line in date_lines:
        try:
            day = datetime.strptime(line, "%Y-%m-%d")
        except ValueError:
            print(f"Skipping invalid date line: {line}")
            continue

        tag_start = day.replace(hour=0, minute=0)
        tag_end = tag_start + timedelta(days=1)          
        track_end = tag_end                                    #
        track_start = tag_end - timedelta(days=15)     

        cfg = dict(template) 
        cfg["preprocess_start_date"] = iso(track_start)
        cfg["preprocess_end_date"] = iso(track_end)
        cfg["tracking_start_date"] = iso(track_start)
        cfg["tracking_end_date"] = iso(track_end)
        cfg["tagging_start_date"] = iso(tag_start)
        cfg["tagging_end_date"] = iso(tag_end)

        dd = day.strftime("%Y%m%d")
        outcfg = OUT_DIR / f"event_{dd}.yaml"
        save_config(cfg, outcfg)
        print(f"Wrote config: {outcfg}  (track {iso(track_start)} → {iso(track_end)}, tag {iso(tag_start)})")

if __name__ == "__main__":
    main()
