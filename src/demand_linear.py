from dataclasses import dataclass
from typing import Dict, Tuple

Key = Tuple[str, str]

@dataclass
class LinearDemandModel:
    alpha: Dict[Key, float]
    n_old: Dict[Key, int]
    x_old: Dict[Key, float]

    def delta_n(self, r: str, t: str, n_new: int) -> int:
        return n_new - self.n_old[(r, t)]

    def ridership(self, r: str, t: str, n_new: int) -> float:
        return self.x_old[(r, t)] + self.alpha[(r, t)] * self.delta_n(r, t, n_new)

    def delta_ridership(self, r: str, t: str, n_new: int) -> float:
        return self.ridership(r, t, n_new) - self.x_old[(r, t)]

    def ridership_linear_coeff(self, r: str, t: str) -> float:
        return self.alpha[(r, t)]
