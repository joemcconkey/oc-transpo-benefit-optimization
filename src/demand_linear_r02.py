from dataclasses import dataclass
from typing import Dict, Tuple

Key = Tuple[str, str]

# Nonlinear elasticity-based demand model used as the reference function for the Taylor linearization,
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

    # delta_n calculates the change in the number of buses for a given route and time period.
    def delta_n(self, r: str, t: str, n_new: int) -> int:
        return n_new - self.n_old[(r, t)]

    # ridership calculates the new ridership based on the old ridership and the change in the number of buses, using the linear approximation.
    def ridership(self, r: str, t: str, n_new: int) -> float:
        return self.x_old[(r, t)] + self.alpha[(r, t)] * self.delta_n(r, t, n_new)

    # delta_ridership calculates the change in ridership based on the change in the number of buses, using the linear approximation.
    def delta_ridership(self, r: str, t: str, n_new: int) -> float:
        return self.alpha[(r, t)] * self.delta_n(r, t, n_new)

    # ridership_linear_coeff returns the linear coefficient (alpha) for the ridership change with respect to the change in the number of buses for a given route and time period.
    def ridership_linear_coeff(self, r: str, t: str) -> float:
        return self.alpha[(r, t)]


# Backward-compatible alias so older code can still import LinearDemandModel.
LinearDemandModel = TaylorLinearDemandModel
