MECH 5800 — OC Transpo Optimization Model
=========================================

OVERVIEW
--------
This project develops a mixed-integer optimization model to allocate buses
across OC Transpo routes and time blocks.

The objective is to maximize net social benefit:
    (ridership + time savings + emissions benefits) 
    − (labour + fuel + maintenance costs)

Decision variable:
    n_new[r, t] = number of buses assigned to route r at time block t


PROJECT STRUCTURE
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

MECH 5800 OC TRANSPO OPTIMIZATION/
│
├── data/                      # Input datasets (CSV)
│   ├── ridership data
│   ├── route/timeblock data
│   └── timeblock parameters
│
├── src/                       # Core model components
│   ├── data_loading.py        # Data import + cleanup (USED)
│   ├── plotting_helpers.py    # Graphing functions (USED)
│   │
│   ├── costs.py               # Cost equations
│   ├── benefits_linear_r03.py # Benefit equations
│   ├── demand_linear_r02.py   # Linearized demand model
│   ├── constraints.py         # Optional constraint helpers
│   │
│   ├── scenario_utils.py      # (NOT USED in final notebooks)
│   └── archive/               # Old / unused code
│
├── optimizer_r13.ipynb        # MAIN model (single run)
├── optimizer_s02_sensitivity_runner.ipynb   # Sensitivity analysis
│
├── results/                   # Output tables / figures
│
├── MECH_5800___Final_Report.pdf
└── README.md / readme.txt


WORKFLOW (HIGH LEVEL)
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

1. Load and clean data
        ↓
2. Initialize model parameters
        ↓
3. Build optimization model (Gurobi)
        ↓
4. Solve model
        ↓
5. Extract results
        ↓
6. Generate tables and plots


MORE DETAILED FLOW
------------------

DATA → MODEL → RESULTS

[ data/ CSV files ]
        ↓
src.data_loading.py
        ↓
(clean dictionaries: x_old, n_old, parameters, etc.)
        ↓
optimizer_r13.ipynb
    - defines decision variables
    - builds objective
    - adds constraints
        ↓
src.costs / src.benefits / src.demand
    (called inside objective construction)
        ↓
Gurobi solver
        ↓
solution: n_new[r,t]
        ↓
post-processing + plots
    (src.plotting_helpers.py)


KEY NOTEBOOKS
-------------

optimizer_r13.ipynb
    - Main optimizer
    - Runs ONE configuration
    - Builds full model explicitly in notebook
    - Best file to read for understanding formulation

optimizer_s02_sensitivity_runner.ipynb
    - Runs multiple scenarios (e.g. budget, fleet caps)
    - Calls the same model repeatedly
    - Produces comparative plots


KEY SRC FILES (ACTIVE)
----------------------

data_loading.py
    - Handles all CSV reading and preprocessing
    - Converts data into dictionaries indexed by (route, timeblock)

plotting_helpers.py
    - Standardized plotting functions for:
        - route/timeblock bar charts
        - sensitivity comparisons

costs.py
    - Implements:
        ΔClabour, ΔCfuel, ΔCmaintenance
    - Used directly in objective function

benefits_linear_r03.py
    - Implements:
        ΔB_time, ΔB_emissions
    - Uses linearized approximations

demand_linear_r02.py
    - Linear demand model:
        x_new = x_old + α * Δn
    - α derived from earlier linearization work

constraints.py
    - Optional helper functions for constraints
    - Some constraints may still be written directly in notebook


HOW TO RUN
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

1. Ensure Python environment has:
        - gurobipy
        - pandas
        - numpy
        - matplotlib

2. Open and run:
        optimizer_r13.ipynb

3. For sensitivity analysis:
        run optimizer_s02_sensitivity_runner.ipynb


IMPORTANT ASSUMPTIONS
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

- Demand is linearized around baseline:
        x_new ≈ x_old + α Δn

- Costs scale linearly with additional buses

- Benefits include:
        - reduced wait time
        - reduced emissions

- Fleet constraints apply per time block

- Budget constraint limits total operating cost increase


NOTES FOR REVIEWER
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

- The model is intentionally structured so that:
    → equations are visible in the notebook
    → supporting math is modularized in src/

- The notebooks are the best place to understand:
    → how the model is assembled
    → how Gurobi is used

- src/ files act as clean implementations of equations from the report

- Sensitivity analysis is separated from the main optimizer for clarity


CONTACT
-------
Joseph McConkey
Jessica Chiappetta
MECH 5800 — Advanced Optimization Modelling