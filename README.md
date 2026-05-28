# GNSS Station Ranking

This repo provides a pipeline for ranking a set of GNSS stations based on metrics derived from Ginan PPP processing. All plots and results used in the SBBE4402 journal paper are available in `paper_plots.ipynb`.

## Getting Started

1.  Install Python 3, create a virtualenv and install requirements.txt

```         
python3 -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
```

2.  Run scoring and plotting for the ppp config

```         
python -m score --config scenarios/ppp.yaml && python -m plot --config scenarios/ppp.yaml
```

3.  View results in results/ppp.

## Project structure

```
scenarios - YAML config files for scoring (inputs, outputs, metrics, weights, aggregation methods)
query - SQL queries to create daily values for each metric for each station. Runs on the HPC against raw metric parquet files.
cache - Daily aggregated metrics from raw metric parquet files created using the query/ module.
score - Scoring and ranking using data from the cache. Configured in scenarios.
plot - Plots to assess scores and ranks over time and geography.
```

## Generating query cache

This command generates a query cache all metrics over the full timeseries. Each metric is generated individually. These commands were run on the HPC to generate the cache from raw parquet files.

```
python -m query postfit_residuals 2019-01-01 2025-12-31
python -m query amb_resets 2019-01-01 2025-12-31
python -m query linear_combinations 2019-01-01 2025-12-31
python -m query position 2019-01-01 2025-12-31
python -m query satellite_gaps 2019-01-01 2025-12-31
python -m query observations 2019-01-01 2025-12-31
```