from dataclasses import dataclass
from typing import Dict, Tuple

Key = Tuple[str, str]


@dataclass
class TaylorLinearDemandModel:
    """
    First-order Taylor linearization of the elasticity-based demand model
    around the baseline bus count n_old.

    Nonlinear reference model:
        x_new = x_old * (n_new / n_old) ** elasticity

    First-order Taylor expansion about n_new = n_old:
        x_new ≈ x_old + alpha * (n_new - n_old)

    where
        alpha = d x_new / d n_new |_(n_old)
              = elasticity * x_old / n_old
    """
    alpha: Dict[Key, float]
    n_old: Dict[Key, int]
    x_old: Dict[Key, float]

    def delta_n(self, r: str, t: str, n_new: int) -> int:
        return n_new - self.n_old[(r, t)]

    def ridership(self, r: str, t: str, n_new: int) -> float:
        return self.x_old[(r, t)] + self.alpha[(r, t)] * self.delta_n(r, t, n_new)

    def delta_ridership(self, r: str, t: str, n_new: int) -> float:
        return self.alpha[(r, t)] * self.delta_n(r, t, n_new)

    def ridership_linear_coeff(self, r: str, t: str) -> float:
        return self.alpha[(r, t)]


# Backward-compatible alias so older code can still import LinearDemandModel.
LinearDemandModel = TaylorLinearDemandModel
