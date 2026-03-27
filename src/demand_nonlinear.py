from dataclasses import dataclass
from typing import Dict, Tuple

Key = Tuple[str, str]

@dataclass
class DemandModel:
    x_old: Dict[Key, float]
    n_old: Dict[Key, int]
    T_rt: Dict[Key, float]
    elasticity: float = 0.5

    def frequency(self, r: str, t: str, n: int) -> float:
        return n / self.T_rt[(r, t)]

    def ridership_from_buses(self, r: str, t: str, n_new: int) -> float:
        return self.x_old[(r, t)] * (self.n_old[(r, t)] / n_new) ** self.elasticity

    def ridership_from_frequency(self, r: str, t: str, f_new: float) -> float:
        f_old = self.frequency(r, t, self.n_old[(r, t)])
        return self.x_old[(r, t)] * (f_old / f_new) ** self.elasticity
