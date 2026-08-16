# CLV Model Card

## Purpose

Estimate Customer Lifetime Value (CLV) from observed customer booking and flight behaviour for portfolio demonstration and analytical experimentation.

## Selected model

**XGBoost regression**, selected after comparison with Linear Regression and Random Forest in the analytical notebook.

## Input features

- Booking frequency
- Flight frequency
- Business-class flights
- Economy-class flights
- Comfort-class flights
- Cities visited
- Days since last booking

## Saved evaluation results

| Metric | Value |
|---|---:|
| MAE | 28,071.87 |
| RMSE | 41,197.63 |
| R² | 0.275 |
| Training records | 293,386 |
| Testing records | 73,347 |

## Interpretation and limitations

An R² of approximately 0.275 means the current feature set explains only part of the variation in CLV. The model should therefore be treated as an experimental baseline, not a production-grade pricing or customer-management model.

Potential improvements include richer temporal behaviour, route mix, fare history, customer tenure, seasonality, interaction features, stronger validation and model monitoring.

## Intended use

- Portfolio demonstration of an end-to-end regression workflow
- Interactive what-if exploration in the Streamlit application
- Basis for future feature-engineering experiments

## Not intended for

- Automated customer treatment decisions
- Production pricing decisions
- Financial forecasting without further validation
