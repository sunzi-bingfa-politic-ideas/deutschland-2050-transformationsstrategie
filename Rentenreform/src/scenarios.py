# Rentenreform/RSSP_v2/src/scenarios.py
from __future__ import annotations
from typing import Dict, List, Any


def load_scenarios_const(obj: Dict[str, Any]) -> Dict[str, List[float]]:
    out = {}
    for s in obj.get("scenarios", []):
        name = s["name"]
        rr = float(s["real_return"])
        out[name] = [rr]
    return out


def load_scenarios_paths(obj: Dict[str, Any]) -> Dict[str, List[float]]:
    out = {}
    for s in obj.get("scenarios", []):
        name = s["name"]
        path = [float(x) for x in s["path"]]
        out[name] = path
    return out
