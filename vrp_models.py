from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import math


Point = Tuple[float, float]


def euclidean(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


@dataclass(frozen=True)
class Client:
    id: int
    x: float
    y: float
    demand: float = 0.0
    service_time: float = 0.0
    tw_start: Optional[float] = None
    tw_end: Optional[float] = None
    requires_refrigeration: bool = False

    @property
    def pos(self) -> Point:
        return (self.x, self.y)


@dataclass(frozen=True)
class Vehicle:
    id: int
    capacity: float
    max_route_time: Optional[float] = None
    has_refrigeration: bool = False
    start_depot: Point = (0.0, 0.0)
    end_depot: Point = (0.0, 0.0)


@dataclass
class Route:
    vehicle: Vehicle
    clients: List[Client] = field(default_factory=list)

    def distance(self) -> float:
        if not self.clients:
            return 0.0
        d = 0.0
        # depot to first
        d += euclidean(self.vehicle.start_depot, self.clients[0].pos)
        # between clients
        for a, b in zip(self.clients[:-1], self.clients[1:]):
            d += euclidean(a.pos, b.pos)
        # last to depot end
        d += euclidean(self.clients[-1].pos, self.vehicle.end_depot)
        return d

    def total_demand(self) -> float:
        return sum(c.demand for c in self.clients)


@dataclass
class Solution:
    routes: List[Route] = field(default_factory=list)

    def total_distance(self) -> float:
        return sum(r.distance() for r in self.routes)

    def all_clients(self) -> List[Client]:
        out: List[Client] = []
        for r in self.routes:
            out.extend(r.clients)
        return out
