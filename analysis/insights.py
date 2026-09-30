import numpy as np
import pandas as pd


def _counts(series, limit=12):
    if series is None:
        return {'labels': [], 'values': []}
    values = series.dropna().astype(str).value_counts().head(limit)
    return {'labels': values.index.tolist(), 'values': [int(v) for v in values.values]}


def generate_insights(df, monthly):
    insights = []
    if 'Age' in df.columns:
        age = pd.to_numeric(df['Age'], errors='coerce').dropna()
        if len(age):
            insights.append(
                f'The average passenger age is {age.mean():.2f} years, with a median of {age.median():.0f} years.'
            )

    if 'Flight Status' in df.columns:
        values = _counts(df['Flight Status'])
        if values['labels']:
            insights.append(
                f"'{values['labels'][0]}' is the most common flight-status category with {values['values'][0]:,} records."
            )

    for column, label in [
        ('Gender', 'gender category'),
        ('Continents', 'continent'),
        ('Nationality', 'nationality'),
    ]:
        if column in df.columns:
            values = df[column].value_counts()
            if len(values):
                insights.append(
                    f"'{values.index[0]}' is the most frequent {label} in the dataset ({int(values.iloc[0]):,} records)."
                )

    if monthly['labels']:
        index = int(np.argmax(monthly['values']))
        insights.append(
            f"{monthly['labels'][index]} has the highest number of departure records in the available data."
        )

    if 'Airport Name' in df.columns:
        values = df['Airport Name'].value_counts()
        if len(values):
            insights.append(
                f"'{values.index[0]}' is the most frequently represented departure airport."
            )

    return insights[:8]
