import math
from pathlib import Path
import numpy as np
import pandas as pd

from .cleaner import clean_dataset
from .feature_engineering import add_features
from .insights import _counts, generate_insights
from .statistics import descriptive_statistics, chi_square_tests


def jsonable(value):
    if pd.isna(value):
        return None
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, (np.floating, float)):
        value = float(value)
        return value if math.isfinite(value) else None
    if isinstance(value, pd.Timestamp):
        return value.strftime('%Y-%m-%d')
    return str(value)


def table_payload(df, limit=12):
    sample = df.head(limit)
    return {
        'columns': [str(c) for c in sample.columns],
        'rows': [[jsonable(v) for v in row] for row in sample.itertuples(index=False, name=None)]
    }


def cross_tab_payload(df, column):
    if column not in df.columns or 'Flight Status' not in df.columns:
        return {'labels': [], 'datasets': []}
    table = pd.crosstab(df[column], df['Flight Status'])
    table['__total'] = table.sum(axis=1)
    table = table.sort_values('__total', ascending=False).head(10).drop(columns='__total')
    return {
        'labels': [str(x) for x in table.index],
        'datasets': [
            {'label': str(col), 'values': [int(v) for v in table[col].values]}
            for col in table.columns
        ]
    }


def monthly_payload(df):
    if 'Departure Month' not in df.columns:
        return {'labels': [], 'values': []}
    values = pd.to_numeric(df['Departure Month'], errors='coerce').dropna().astype(int).value_counts().sort_index()
    names = {i: pd.Timestamp(2020, i, 1).strftime('%B') for i in range(1, 13)}
    return {
        'labels': [names.get(i, str(i)) for i in values.index],
        'values': [int(v) for v in values.values]
    }


def analyze_csv(input_path, output_path, filename, analysis_id):
    raw = pd.read_csv(input_path, low_memory=False)
    if raw.empty or len(raw.columns) < 2:
        raise ValueError('The CSV must contain records and at least two columns.')

    raw_missing = int(raw.isna().sum().sum())
    raw_duplicates = int(raw.duplicated().sum())
    raw_dtypes = {str(c): str(t) for c, t in raw.dtypes.items()}
    raw_unique = {str(c): int(raw[c].nunique(dropna=True)) for c in raw.columns}
    raw_missing_by_column = {
        str(c): int(v) for c, v in raw.isna().sum().items() if v
    }

    cleaned, actions, _, removed = clean_dataset(raw)
    cleaned, created = add_features(cleaned)
    cleaned.to_csv(output_path, index=False)

    age = pd.to_numeric(cleaned['Age'], errors='coerce').dropna() if 'Age' in cleaned.columns else pd.Series(dtype=float)
    age_summary = {}
    if len(age):
        age_summary = {
            'mean': round(float(age.mean()), 2),
            'median': round(float(age.median()), 2),
            'min': round(float(age.min()), 2),
            'max': round(float(age.max()), 2),
            'std': round(float(age.std()), 2) if len(age) > 1 else 0.0,
        }

    monthly = monthly_payload(cleaned)
    status = _counts(cleaned['Flight Status']) if 'Flight Status' in cleaned.columns else {'labels': [], 'values': []}

    kpis = {
        'records': len(cleaned),
        'average_age': age_summary.get('mean'),
        'median_age': age_summary.get('median'),
        'nationalities': int(cleaned['Nationality'].nunique()) if 'Nationality' in cleaned.columns else 0,
        'airports': int(cleaned['Airport Name'].nunique()) if 'Airport Name' in cleaned.columns else 0,
        'arrival_airports': int(cleaned['Arrival Airport'].nunique()) if 'Arrival Airport' in cleaned.columns else 0,
        'continents': int(cleaned['Continents'].nunique()) if 'Continents' in cleaned.columns else 0,
    }

    steps = [
        'Data Collection', 'Data Loading', 'Data Exploration', 'Data Cleaning',
        'Feature Engineering', 'Exploratory Data Analysis', 'Data Visualization',
        'Statistical Analysis', 'Data Interpretation / Insights',
        'Reporting / Presentation'
    ]

    return {
        'analysis_id': analysis_id,
        'filename': filename,
        'steps': [
            {'number': i, 'name': name, 'status': 'complete'}
            for i, name in enumerate(steps, 1)
        ],
        'raw': {
            'rows': len(raw),
            'columns': len(raw.columns),
            'names': [str(c) for c in raw.columns],
            'dtypes': raw_dtypes,
            'unique': raw_unique,
            'missing_by_column': raw_missing_by_column,
            'preview': table_payload(raw, 12)['rows'],
            'preview_columns': table_payload(raw, 12)['columns'],
        },
        'quality': {
            'raw_missing': raw_missing,
            'clean_missing': int(cleaned.isna().sum().sum()),
            'raw_duplicates': raw_duplicates,
            'clean_duplicates': int(cleaned.duplicated().sum()),
            'raw_rows': len(raw),
            'clean_rows': len(cleaned),
            'raw_columns': len(raw.columns),
            'clean_columns': len(cleaned.columns),
        },
        'cleaning': {
            'actions': actions,
            'removed': removed,
            'created': created,
        },
        'kpis': kpis,
        'age': age_summary,
        'charts': {
            'status': status,
            'continent': _counts(cleaned['Continents']) if 'Continents' in cleaned.columns else {'labels': [], 'values': []},
            'gender': _counts(cleaned['Gender']) if 'Gender' in cleaned.columns else {'labels': [], 'values': []},
            'nationality': _counts(cleaned['Nationality'], 10) if 'Nationality' in cleaned.columns else {'labels': [], 'values': []},
            'arrival': _counts(cleaned['Arrival Airport'], 10) if 'Arrival Airport' in cleaned.columns else {'labels': [], 'values': []},
            'airport': _counts(cleaned['Airport Name'], 10) if 'Airport Name' in cleaned.columns else {'labels': [], 'values': []},
            'monthly': monthly,
            'age_dist': _counts(cleaned['Age Group'], 12) if 'Age Group' in cleaned.columns else {'labels': [], 'values': []},
            'day': _counts(cleaned['Day of Week']) if 'Day of Week' in cleaned.columns else {'labels': [], 'values': []},
        },
        'flights': {
            'gender': cross_tab_payload(cleaned, 'Gender'),
            'age_group': cross_tab_payload(cleaned, 'Age Group'),
            'continent': cross_tab_payload(cleaned, 'Continents'),
            'travel': cross_tab_payload(cleaned, 'Travel Type (Approx.)'),
        },
        'statistics': {
            'descriptive': descriptive_statistics(cleaned),
            'chi_square': chi_square_tests(cleaned),
        },
        'insights': generate_insights(cleaned, monthly),
        'preview_cleaned': table_payload(cleaned, 500),
        'columns_cleaned': [str(c) for c in cleaned.columns],
        'download_url': f'/api/download/{analysis_id}',
    }
