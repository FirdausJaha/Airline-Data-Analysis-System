import numpy as np
import pandas as pd


def _first_existing(df, names):
    return next((name for name in names if name in df.columns), None)


def add_features(df):
    df = df.copy()
    created = []

    date_column = _first_existing(df, ['Departure Date', 'Date', 'DepartureDate'])
    if date_column:
        dates = pd.to_datetime(df[date_column], errors='coerce')
        df['Departure Year'] = dates.dt.year
        df['Departure Month'] = dates.dt.month
        df['Departure Month Name'] = dates.dt.month_name()
        df['Departure Day'] = dates.dt.day
        df['Day of Week'] = dates.dt.day_name()
        df['Day Type'] = np.where(dates.dt.dayofweek >= 5, 'Weekend', 'Weekday')
        created.extend([
            'Departure Year', 'Departure Month', 'Departure Month Name',
            'Departure Day', 'Day of Week', 'Day Type'
        ])

    if 'Age' in df.columns:
        bins = [0, 17, 26, 35, 44, 53, 62, 71, 80, 100]
        labels = ['1-17', '18-26', '27-35', '36-44', '45-53', '54-62', '63-71', '72-80', '81-100']
        df['Age Group'] = pd.cut(
            pd.to_numeric(df['Age'], errors='coerce'),
            bins=bins, labels=labels, include_lowest=True
        )
        created.append('Age Group')

    if 'Nationality' in df.columns and 'Country Name' in df.columns:
        nationality = df['Nationality'].astype('string').str.lower().str.strip()
        country = df['Country Name'].astype('string').str.lower().str.strip()
        df['Travel Type (Approx.)'] = np.where(
            nationality.notna() & country.notna() & (nationality == country),
            'Domestic (Approx.)',
            np.where(nationality.notna() & country.notna(), 'International (Approx.)', 'Unknown')
        )
        created.append('Travel Type (Approx.)')

    return df, created
