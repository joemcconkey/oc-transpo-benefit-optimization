from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import math
import pandas as pd

DEFAULT_TIME_BLOCKS = ['Early AM', 'AM Peak', 'Midday', 'PM Peak', 'Evening', 'Night']

DEFAULT_ROUTE_DATA_CANDIDATES = [
    'data/route_timeblock_v03.csv',
    '/mnt/data/route_timeblock_v03.csv',
    'data/route_timeblock_v02.csv',
    'data/route_timeblock_subset_v02.csv',
    'data/route_timeblock_subset_v01.csv',
    '/mnt/data/route_timeblock_subset_v01.csv',
]

COLUMN_MAP = {
    'Route (r)': 'route',
    'Time Block (t)': 'time_block',
    'Route type': 'route_type',
    'Old ridership (x_old,r,t)': 'x_old',
    'Trip length km (L_r)': 'L_r',
    'Average length hr (T_r,t)': 'T_rt',
    'Old frequency of buses (f_old,r,t)': 'f_old',
    'Old number of buses (n_old,r,t) - continuous': 'n_old_cont',
    'Old number of buses (n_old,r,t) - discrete': 'n_old',
    'Time block hr (H_block,t)': 'H_block',
    'Driver horuly wage rate $/hr (W_driver)': 'W_driver',
    'Price of fuel $/litre (P_fuel)': 'P_fuel',
    'Fuel consumption (FC)': 'fuel_consumption',
    'Maintenace cost $/km (P_maintenance)': 'P_maintenance',
    'Passenger hourly wage rate $/hr (W_passenger)': 'W_passenger',
    'VTTS fraction of passenger wage (F_wage)': 'F_wage',
    'Emission intensity of a car kgCO2eq/KPT (I_GHG,car)': 'I_GHG_car',
    'Average Length of passenger trip (L_avg_trip)': 'L_avg_trip',
    'Social cost of carbon $/tonne CO2eq (SCC)': 'SCC',
    ' Vehicle-miles saved per 1 km  of passenger km travelled (V_km,saved)': 'V_km_saved',
}

REQUIRED_COLUMNS = [
    'route', 'time_block', 'route_type',
    'x_old', 'L_r', 'T_rt', 'f_old',
    'n_old_cont', 'n_old',
    'H_block', 'W_driver', 'P_fuel',
    'fuel_consumption', 'P_maintenance',
    'W_passenger', 'F_wage',
    'I_GHG_car', 'L_avg_trip', 'V_km_saved', 'SCC',
]

NUMERIC_COLUMNS = [
    'x_old', 'L_r', 'T_rt', 'f_old',
    'n_old_cont', 'n_old',
    'H_block', 'W_driver', 'P_fuel',
    'fuel_consumption', 'P_maintenance',
    'W_passenger', 'F_wage',
    'I_GHG_car', 'L_avg_trip', 'V_km_saved', 'SCC',
]


def first_existing_path(candidates: Sequence[str]) -> Path:
    path = next((Path(p) for p in candidates if Path(p).exists()), None)
    if path is None:
        raise FileNotFoundError(f'Could not find any of: {list(candidates)}')
    return path


def load_and_clean_route_data(
    time_blocks: Sequence[str] = DEFAULT_TIME_BLOCKS,
    route_data_candidates: Optional[Sequence[str]] = None,
) -> Tuple[pd.DataFrame, Path]:
    route_data_path = first_existing_path(route_data_candidates or DEFAULT_ROUTE_DATA_CANDIDATES)
    raw_df = pd.read_csv(route_data_path)
    df = raw_df.rename(columns=COLUMN_MAP).copy()

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise KeyError(f'Missing expected columns: {missing}')

    df['route'] = df['route'].astype(str).str.strip()
    df['time_block'] = df['time_block'].astype(str).str.strip()
    df['route_type'] = df['route_type'].astype(str).str.strip()

    cancelled_mask = df['route_type'].str.lower().eq('cancelled')
    df = df.loc[~cancelled_mask].copy()

    for c in NUMERIC_COLUMNS:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    df['n_old'] = df['n_old'].round().astype(int)
    df['time_block'] = pd.Categorical(df['time_block'], categories=list(time_blocks), ordered=True)
    df = df.sort_values(['route', 'time_block']).reset_index(drop=True)
    df['key'] = list(zip(df['route'], df['time_block'].astype(str)))
    return df, route_data_path


def compute_baseline_fleet_caps(df: pd.DataFrame) -> Dict[str, int]:
    return (
        df.groupby('time_block', observed=True)['n_old']
        .sum()
        .astype(int)
        .to_dict()
    ) # type: ignore


def compute_expanded_fleet_caps(
    baseline_fleet_caps: Dict[str, int],
    expansion_factor: float,
    time_blocks: Sequence[str] = DEFAULT_TIME_BLOCKS,
) -> Dict[str, int]:
    return {
        t: int(math.ceil(baseline_fleet_caps[t] * expansion_factor))
        for t in time_blocks
    }
