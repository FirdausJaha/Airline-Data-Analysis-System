# Airline Data Analysis System

A student-friendly web application for uploading an uncleaned airline CSV and completing a dynamic data-analysis workflow.

## What it does

1. Data Collection
2. Data Loading
3. Data Exploration
4. Data Cleaning
5. Feature Engineering
6. Exploratory Data Analysis
7. Data Visualization
8. Statistical Analysis
9. Data Interpretation / Insights
10. Reporting / Presentation

The application also includes a Data Explorer with search, filters, pagination, and Add/Edit/Delete record operations. After a record change, the analysis is recalculated so the dashboard, statistics, insights, and report stay synchronized.

## Project structure

```text
Airline-Data-Analysis-System/
├── app.py
├── requirements.txt
├── README.md
├── PROJECT_INFO.txt
├── .gitignore
├── analysis/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── cleaner.py
│   ├── feature_engineering.py
│   ├── insights.py
│   └── statistics.py
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/app.js
└── uploads/
    └── .gitkeep
```

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`.

## Deployment

GitHub Pages cannot execute the server-side application. The source can be stored on GitHub, but the live application needs a hosting service that can run a Python/Flask application. Use the included `requirements.txt` and a Python-capable service with Gunicorn support.

## Notes

- CSV uploads are limited to 50 MB.
- The application removes identifiers/redundant fields used by the supplied airline dataset from the analytical dataset.
- `Travel Type (Approx.)` is an approximate analytical feature based on nationality and airport country; it is not a true ticket-level domestic/international classification.
- Uploaded data is kept in the application's `uploads/` directory for the current analysis session.
