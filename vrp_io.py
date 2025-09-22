from __future__ import annotations

import json
from typing import List, Dict, Any
from vrp_models import Client, Vehicle


def load_vrp_from_json(path: str) -> tuple[List[Client], List[Vehicle]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    clients: List[Client] = []
    for c in data.get("clients", []):
        clients.append(
            Client(
                id=int(c["id"]),
                x=float(c["x"]),
                y=float(c["y"]),
                demand=float(c.get("demand", 0.0)),
                service_time=float(c.get("service_time", 0.0)),
                tw_start=c.get("tw_start", None),
                tw_end=c.get("tw_end", None),
                requires_refrigeration=bool(c.get("requires_refrigeration", False)),
            )
        )
    vehicles: List[Vehicle] = []
    for v in data.get("vehicles", []):
        start = tuple(v.get("start_depot", [0.0, 0.0]))
        end = tuple(v.get("end_depot", start))
        vehicles.append(
            Vehicle(
                id=int(v["id"]),
                capacity=float(v.get("capacity", 0.0)),
                max_route_time=v.get("max_route_time", None),
                has_refrigeration=bool(v.get("has_refrigeration", False)),
                start_depot=(float(start[0]), float(start[1])),
                end_depot=(float(end[0]), float(end[1])),
            )
        )
    return clients, vehicles


def save_vrp_to_json(path: str, clients: List[Client], vehicles: List[Vehicle]) -> None:
    data: Dict[str, Any] = {
        "clients": [
            {
                "id": c.id,
                "x": c.x,
                "y": c.y,
                "demand": c.demand,
                "service_time": c.service_time,
                "tw_start": c.tw_start,
                "tw_end": c.tw_end,
                "requires_refrigeration": c.requires_refrigeration,
            }
            for c in clients
        ],
        "vehicles": [
            {
                "id": v.id,
                "capacity": v.capacity,
                "max_route_time": v.max_route_time,
                "has_refrigeration": v.has_refrigeration,
                "start_depot": [v.start_depot[0], v.start_depot[1]],
                "end_depot": [v.end_depot[0], v.end_depot[1]],
            }
            for v in vehicles
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
