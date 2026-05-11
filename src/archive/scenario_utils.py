

import copy
import math
from typing import Dict, Sequence

# Utility functions for handling scenario data, including resolving fleet caps based on scenario settings and creating modified scenarios with parameter overrides for sensitivity analysis

# Fleet cap resolution logic based on scenario settings and fleet mode (baseline or expanded), with support for explicit fleet caps in the scenario or scaling based on an expansion factor
def resolve_fleet_caps(
    scenario: Dict,
    baseline_fleet_caps: Dict[str, int],
    fleet_mode: str,
    time_blocks: Sequence[str],
) -> Dict[str, int]:
    if scenario.get('fleet_caps') is not None:
        return copy.deepcopy(scenario['fleet_caps'])

    if fleet_mode == 'baseline':
        return copy.deepcopy(baseline_fleet_caps)

    if fleet_mode == 'expanded':
        expansion = scenario.get('expansion_factor', 1.0)
        return {
            t: int(math.ceil(baseline_fleet_caps[t] * expansion))
            for t in time_blocks
        }

    raise ValueError("fleet_mode must be 'baseline' or 'expanded'")

# Function to create a new scenario based on a base scenario, with the ability to override specific parameters (including fleet caps for all blocks or specific blocks) for sensitivity analysis, while ensuring that fleet caps are properly resolved based on the scenario settings and fleet mode
def activate_base_scenario(
    base_scenario: Dict,
    baseline_fleet_caps: Dict[str, int],
    fleet_mode: str,
    time_blocks: Sequence[str],
) -> Dict:
    scenario = copy.deepcopy(base_scenario)
    scenario['fleet_caps'] = resolve_fleet_caps(
        scenario=scenario,
        baseline_fleet_caps=baseline_fleet_caps,
        fleet_mode=fleet_mode,
        time_blocks=time_blocks,
    )
    return scenario

# Function to create a modified scenario with a specific parameter override for sensitivity analysis, handling both general parameters and fleet cap overrides for all blocks or specific blocks, while ensuring that fleet caps are properly resolved based on the scenario settings and fleet mode
def scenario_with_override(
    base_scenario: Dict,
    parameter_name: str,
    parameter_value,
    baseline_fleet_caps: Dict[str, int],
    fleet_mode: str,
    time_blocks: Sequence[str],
) -> Dict: # Returns a new scenario dict with the specified parameter override, while ensuring fleet caps are properly resolved based on the scenario settings and fleet mode
    scenario = copy.deepcopy(base_scenario) 

    if parameter_name == 'fleet_cap_all_blocks':
        scenario['fleet_caps'] = resolve_fleet_caps(
            scenario=scenario,
            baseline_fleet_caps=baseline_fleet_caps,
            fleet_mode=fleet_mode,
            time_blocks=time_blocks,
        )
        for t in scenario['fleet_caps']:
            scenario['fleet_caps'][t] = int(parameter_value)
        return scenario

    if parameter_name.startswith('fleet_cap_'):
        scenario['fleet_caps'] = resolve_fleet_caps(
            scenario=scenario,
            baseline_fleet_caps=baseline_fleet_caps,
            fleet_mode=fleet_mode,
            time_blocks=time_blocks,
        )
        block = parameter_name.replace('fleet_cap_', '', 1)
        if block not in scenario['fleet_caps']:
            raise KeyError(f'Unknown time block in parameter name: {parameter_name}')
        scenario['fleet_caps'][block] = int(parameter_value)
        return scenario

    if parameter_name not in scenario: 
        raise KeyError(f'Unsupported parameter: {parameter_name}')

    scenario[parameter_name] = parameter_value
    scenario['fleet_caps'] = resolve_fleet_caps(
        scenario=scenario,
        baseline_fleet_caps=baseline_fleet_caps,
        fleet_mode=fleet_mode,
        time_blocks=time_blocks,
    )
    return scenario
