# GNSS Station Ranking

This repo provides a pipeline for ranking a set of GNSS stations based on metrics derived from Ginan PPP processing.

## Getting Started

This command generates a query cache for postfit residudals over the full time series.

```
python -m query postfit_residuals 2019-01-01 2025-12-25
```