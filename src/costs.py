from dataclasses import dataclass
from typing import Dict, Tuple

Key = Tuple[str, str]

@dataclass
class CostModel:
    H_block: Dict[str, float]
    W_driver: float
    L_r: Dict[str, float]
    T_rt: Dict[Key, float]
    P_fuel: float
    fuel_consumption: float
    P_maintenance: float
    n_old: Dict[Key, int]

    def delta_n(self, r: str, t: str, n_new: int) -> int:
        return n_new - self.n_old[(r, t)]

    def labour(self, r: str, t: str, n_new: int) -> float:
        return self.delta_n(r, t, n_new) * self.H_block[t] * self.W_driver

    def fuel(self, r: str, t: str, n_new: int) -> float:
        return (
            self.delta_n(r, t, n_new)
            * self.L_r[r]
            * (self.H_block[t] / self.T_rt[(r, t)])
            * self.P_fuel
            * self.fuel_consumption
        )

    def maintenance(self, r: str, t: str, n_new: int) -> float:
        return (
            self.delta_n(r, t, n_new)
            * self.L_r[r]
            * (self.H_block[t] / self.T_rt[(r, t)])
            * self.P_maintenance
        )

    def total(self, r: str, t: str, n_new: int) -> float:
        return (
            self.labour(r, t, n_new)
            + self.fuel(r, t, n_new)
            + self.maintenance(r, t, n_new)
        )

    def total_operating_cost(self, n_new: Dict[Key, int]) -> float:
        return sum(self.total(r, t, n_new[(r, t)]) for (r, t) in n_new)
