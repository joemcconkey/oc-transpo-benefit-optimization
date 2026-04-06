from dataclasses import dataclass
from typing import Dict, Tuple

Key = Tuple[str, str]


@dataclass
class TaylorLinearBenefitModel:
    """
    First-order Taylor linearization of the nonlinear benefit terms around n_old.

    The linearized forms are:
        ΔB_time ≈ beta_time * (n_new - n_old)
        ΔB_emissions ≈ beta_emissions * (n_new - n_old)

    The coefficients beta_time and beta_emissions should be constructed from
    the derivatives of the corresponding nonlinear expressions evaluated at n_old.
    """
    beta_time: Dict[Key, float]
    beta_emissions: Dict[Key, float]
    n_old: Dict[Key, int]

    def delta_n(self, r: str, t: str, n_new: int) -> int:
        return n_new - self.n_old[(r, t)]

    def benefit_time(self, r: str, t: str, n_new: int) -> float:
        return self.beta_time[(r, t)] * self.delta_n(r, t, n_new)

    def benefit_emissions(self, r: str, t: str, n_new: int) -> float:
        return self.beta_emissions[(r, t)] * self.delta_n(r, t, n_new)

    def benefit_total(self, r: str, t: str, n_new: int) -> float:
        return self.benefit_time(r, t, n_new) + self.benefit_emissions(r, t, n_new)

    def benefit_linear_coeff(self, r: str, t: str) -> float:
        return self.beta_time[(r, t)] + self.beta_emissions[(r, t)]

    def total_objective_contribution(self, n_new: Dict[Key, int]) -> float:
        return sum(
            self.benefit_total(r, t, n_new[(r, t)])
            for (r, t) in n_new
        )


# Backward-compatible alias so older code can still import LinearBenefitModel.
LinearBenefitModel = TaylorLinearBenefitModel
