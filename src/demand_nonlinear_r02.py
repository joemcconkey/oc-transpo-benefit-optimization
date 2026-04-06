from dataclasses import dataclass
from typing import Dict, Tuple

Key = Tuple[str, str]


@dataclass
class DemandModel:
    """
    Nonlinear elasticity-based demand model used as the reference function for
    the Taylor linearization.

    x_new = x_old * (n_new / n_old) ** elasticity
    """
    x_old: Dict[Key, float]
    n_old: Dict[Key, int]
    T_rt: Dict[Key, float]
    elasticity: float = 0.5

    def frequency(self, r: str, t: str, n: int) -> float:
        return n / self.T_rt[(r, t)]

    def ridership_from_buses(self, r: str, t: str, n_new: int) -> float:
        return self.x_old[(r, t)] * (n_new / self.n_old[(r, t)]) ** self.elasticity

    def ridership_from_frequency(self, r: str, t: str, f_new: float) -> float:
        f_old = self.frequency(r, t, self.n_old[(r, t)])
        return self.x_old[(r, t)] * (f_new / f_old) ** self.elasticity
