# v1.0 final visual and AI polish

- Kept daily analytics at daily grain while reducing date-axis labels to approximately 7–9 readable ticks.
- Added a latest-day data-quality warning to the Executive Overview and grounded AI trend context.
- Removed percentage deltas from Customer Intelligence priority cards where they could be misread as period-over-period changes; shares are now shown as captions.
- Hardened local AI Markdown rendering against malformed emphasis markers and compact metric names.
- Instructed the local assistant not to use bold/italic Markdown and to treat the latest daily observation as potentially partial.
- Preserved the existing dark aviation theme, navigation, analytics, ML, governance, and local Ollama architecture.

## Daily trend and customer-page fix

- Changed portfolio line charts from weekly to daily aggregation because the dataset covers a relatively short period.
- Added `get_daily_trends()` as the UI-facing time-series source.
- Updated Executive Overview to show Daily Revenue and Daily Unique Customers.
- Updated Revenue & Fare Class to show Daily Average Ticket-Flight Price.
- Updated the grounded AI trend context and suggested question to use daily trends.
- Fixed the Customer Detail `revenue_per_flight` KeyError by ensuring the customer feature query returns that field.
- Kept presentation-safe customer IDs (`C000001`, etc.) instead of exposing raw passenger identifiers in customer visuals/tables.
- Replaced deprecated Streamlit `use_container_width` usage with `width="stretch"`.

# Portfolio Release Notes

## Final portfolio pass

### Analytics
- Retained weekly analytics services for reuse and testing while using daily series in the portfolio UI.
- Preserved monthly trend services for longer-horizon analysis.
- Standardised weekly chart labels to Monday week starts.
- Corrected fare-class volume presentation to use ticket-flight records and reconciled shares to 100 percent.
- Standardised customer city coverage across departure and arrival airports.
- Added transparent customer priority bands using observed value, flight frequency, and recency.
- Added route commercial profiles using relative revenue and load-factor signals.
- Expanded fleet reporting with revenue per flight and revenue per available seat.

### Customer Intelligence
- Replaced arbitrary customer labels with presentation-safe ranked customer identifiers.
- Added value, frequency, and recency KPIs.
- Replaced the crowded customer scatter with a customer-value-by-flight-frequency box plot.
- Added customer priority counts and an expanded customer detail table.

### Customer Segmentation
- Retained the persisted K-Means model and Joblib loading.
- Fixed the live input design to respect the model's four required features.
- Disabled editing of booking frequency because the persisted training feature has zero variance.
- Initialised live inputs from observed customer medians rather than arbitrary values.
- Added segment profile metrics after live inference.
- Kept segment names explicitly labelled as business interpretations of unsupervised clusters.

### CLV
- Presented CLV as a directional what-if model.
- Retained model performance metrics and governance warning.
- Clarified that Customer Value Band is a presentation aid, not a trained classification output.

### Route and Fleet
- Added route-level commercial performance profiles.
- Clarified that revenue is not profitability.
- Added flight-frequency context to route and aircraft scatter plots.
- Replaced the six-category flight-status donut with a more readable horizontal bar chart.

### Generative AI
- Retained intent-based analytics routing.
- Updated route grounding to use the route commercial-performance context.
- Updated trend grounding to daily analytics.
- Added customer priority context.
- Tightened instructions against unsupported profitability, causal, route-distance, and customer-intent claims.
- Kept Ollama optional so non-AI dashboard pages remain usable.

### Interface
- Retained the dark executive aviation theme.
- Aviation blue is used for analytics and active navigation.
- Red is reserved for risk/alerts and green for positive outcomes.
- Removed decorative emoji branding from the application.
- Kept the single grouped sidebar navigation.

### Testing
- Added a small deterministic SQLite fixture for automated analytics and AI-context tests.
- Expanded tests for weekly aggregation, fare-share reconciliation, customer priority logic, and targeted AI context.
- The final test suite passes in the supplied development environment: 16 passed.


## v1.0 Final Fixed v2

### Customer Segmentation layout
- Updated the Segment Behaviour Distribution section so Customer Share by Segment, Median Observed Value by Segment, and Median Recency by Segment render in one horizontal three-column row.
- Standardised the three charts to a compact 320px height for a cleaner dashboard view.
- Added value labels to the observed-value and recency charts for faster comparison.
- Disabled the Plotly mode bar on these compact portfolio charts to reduce visual clutter.

### Validation
- Python compilation check passed for the updated Streamlit files.
- Full automated test suite passes: 16 tests passed.
