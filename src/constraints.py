from typing import Dict, Iterable, Tuple

from gurobipy import GRB, Model, quicksum

from src.costs import CostModel

Key = Tuple[str, str]

def add_budget_constraint(
    model: Model,
    n_new,
    RT: Iterable[Key],
    cost_model: CostModel,
    budget_total: float,
    name: str = "budget_total_operational",
):
    expr = quicksum(cost_model.total(r, t, n_new[r, t]) for r, t in RT)
    return model.addConstr(expr <= budget_total, name=name)

# def add_fleet_constraints(
#     model: Model,
#     n_new,
#     R,
#     T,
#     buses_total: int,
#     name_prefix: str = "fleet",
# ):
#     return {
#         t: model.addConstr(quicksum(n_new[r, t] for r in R) <= buses_total, name=f"{name_prefix}[{t}]")
#         for t in T
#     }

def add_fleet_constraints(
    model: Model,
    n_new,
    R,
    T,
    buses_total,
    name_prefix: str = "fleet",
):
    fleet_caps = (
        {t: buses_total for t in T}
        if not isinstance(buses_total, dict)
        else buses_total
    )

    return {
        t: model.addConstr(
            quicksum(n_new[r, t] for r in R) <= fleet_caps[t],
            name=f"{name_prefix}[{t}]"
        )
        for t in T
    }

def add_bounds(
    model: Model,
    n_new,
    RT: Iterable[Key],
    n_min: Dict[Key, int],
    n_max: Dict[Key, int],
    name_prefix: str = "bounds",
):
    lower = {
        (r, t): model.addConstr(n_new[r, t] >= n_min[(r, t)], name=f"{name_prefix}_lb[{r},{t}]")
        for r, t in RT
    }
    upper = {
        (r, t): model.addConstr(n_new[r, t] <= n_max[(r, t)], name=f"{name_prefix}_ub[{r},{t}]")
        for r, t in RT
    }
    return lower, upper

def add_integer_bus_vars(
    model: Model,
    RT: Iterable[Key],
    n_min: Dict[Key, int],
    n_max: Dict[Key, int],
    name: str = "n_new",
):
    return model.addVars(
        list(RT),
        vtype=GRB.INTEGER,
        lb={k: n_min[k] for k in RT},
        ub={k: n_max[k] for k in RT},
        name=name,
    )
