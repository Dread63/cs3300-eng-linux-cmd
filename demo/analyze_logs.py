"""
Log analysis script for demo server logs.
Reads server.log and error.log from the same directory.
"""

import os
import re
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_LEVELS = ["INFO", "WARN", "ERROR"]

def parse_log(filepath):
    entries = []
    pattern = re.compile(r"\[(.+?)\] (\w+)\s+(.+)")
    with open(filepath) as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                entries.append({"timestamp": m.group(1), "level": m.group(2), "message": m.group(3)})
    return entries

def level_counts(entries):
    return Counter(e["level"] for e in entries)

def errors_only(entries):
    return [e for e in entries if e["level"] == "ERROR"]

if __name__ == "__main__":
    server_log = os.path.join(SCRIPT_DIR, "server.log")
    error_log = os.path.join(SCRIPT_DIR, "error.log")

    entries = parse_log(server_log)
    counts = level_counts(entries)

    print("=== Server Log Summary ===")
    print(f"Total entries: {len(entries)}")
    for level in LOG_LEVELS:
        print(f"  {level}: {counts.get(level, 0)}")

    print("\nErrors:")
    for e in errors_only(entries):
        print(f"  [{e['timestamp']}] {e['message']}")

    print("\n=== Dedicated Error Log ===")
    errs = parse_log(error_log)
    print(f"Total errors recorded: {len(errs)}")
