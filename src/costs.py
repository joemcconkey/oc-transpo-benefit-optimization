from dataclasses import dataclass
from typing import Dict, Tuple

Key = Tuple[str, str]

# This class models the costs associated with changes in the number of buses on each route and time period.
# It calculates the labor, fuel, and maintenance costs based on the change in the number of buses (delta_n) and the parameters provided.

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

# The delta_n function calculates the change in the number of buses for a given route and time period.
    def delta_n(self, r: str, t: str, n_new: int) -> int:
        return n_new - self.n_old[(r, t)]

# The labour function calculates the labor cost based on the change in the number of buses, the block hours for the time period, and the wage rate for drivers.
    def labour(self, r: str, t: str, n_new: int) -> float:
        return self.delta_n(r, t, n_new) * self.H_block[t] * self.W_driver

# The fuel function calculates the fuel cost based on the change in the number of buses, the block hours for the time period, the fuel price, and the fuel consumption rate.
    def fuel(self, r: str, t: str, n_new: int) -> float:
        return (
            self.delta_n(r, t, n_new)
            * self.L_r[r]
            * (self.H_block[t] / self.T_rt[(r, t)])
            * self.P_fuel
            * self.fuel_consumption
        )

# The maintenance function calculates the maintenance cost based on the change in the number of buses, the block hours for the time period, and the maintenance cost per hour.
    def maintenance(self, r: str, t: str, n_new: int) -> float:
        return (
            self.delta_n(r, t, n_new)
            * self.L_r[r]
            * (self.H_block[t] / self.T_rt[(r, t)])
            * self.P_maintenance
        )

# The total function calculates the total cost (labor + fuel + maintenance) for a given route, time period, and new number of buses.
    def total(self, r: str, t: str, n_new: int) -> float:
        return (
            self.labour(r, t, n_new)
            + self.fuel(r, t, n_new)
            + self.maintenance(r, t, n_new)
        )

# The total_operating_cost function calculates the total operating cost for a given dictionary of new bus counts (n_new) by summing the total costs for each route and time period.
    def total_operating_cost(self, n_new: Dict[Key, int]) -> float:
        return sum(self.total(r, t, n_new[(r, t)]) for (r, t) in n_new)
