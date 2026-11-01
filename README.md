# Customer Engagement & Product Utilization Analytics for Retention Strategy

## Included
- `Research_Report.docx` — full research report with methodology, findings, KPIs, recommendations and limitations.
- `Executive_Summary.docx` and `.pdf` — concise stakeholder brief.
- `app.py` — Streamlit dashboard with filters, churn analysis, high-value disengaged detector and relationship score.
- `European_Bank.csv` — supplied source dataset.
- `customer_retention_enriched.csv` — dataset with derived segments and scores.
- `requirements.txt` — Python dependencies.

## Run the dashboard
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run `pip install -r requirements.txt`
4. Run `streamlit run app.py`
5. Open the local URL Streamlit prints (usually http://localhost:8501).

## Key findings from the supplied dataset
- Customers: 10,000; observed churn: 20.4%.
- Active churn: 14.3%; inactive churn: 26.9%.
- One-product churn: 27.7%; two-product churn: 7.6%.
- Inactive high-balance customers (>= 75th percentile, 127,644.24 balance units): 1,247; segment churn: 30.5%.

## Important interpretation notes
The supplied file does not specify balance currency. The analysis is descriptive, based on a one-year snapshot. Product count is available, but product names/mix and actual usage events are not. The Relationship Strength Index is a transparent heuristic, not a validated predictive model or causal estimate. Do not use outputs for automated adverse decisions; apply privacy, fairness, suitability and regulatory review.
