#!/usr/bin/env python3

import subprocess

def das_go_query(query):
    proc = subprocess.run(
        ["dasgoclient", "--query", query],
        stdout=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(f"Could not run DAS Go client query: {query}")
    rawlines =  proc.stdout.splitlines()
    lines = list(map(lambda x: x.decode("utf-8").strip(), rawlines))
    lines = [l for l in lines if l]

    return lines
