import re
import pandas as pd

AIRLINE_DROP_COLUMNS = {
    'Passenger ID', 'First Name', 'Last Name', 'Pilot Name',
    'Airport Continent', 'Airport Country Code'
}


def clean_dataset(df):
    df = df.copy()
    actions = []
    original_shape = (len(df), len(df.columns))

    # Normalize column names.
    df.columns = [re.sub(r'\s+', ' ', str(c).strip()) for c in df.columns]

    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    actions.append(['All columns', 'Duplicate rows', duplicate_count, 0,
                    f'Removed {duplicate_count} duplicate row(s).'])

    missing_markers = ['', 'NA', 'N/A', 'NULL', 'null', 'None', 'none', '-', '?']
    for column in df.columns:
        if df[column].dtype == 'object' or str(df[column].dtype).startswith('string'):
            df[column] = (df[column].astype('string').str.strip()
                          .replace(missing_markers, pd.NA))

    # Numeric conversion for columns that are overwhelmingly numeric.
    for column in list(df.columns):
        if column == 'Age' or pd.api.types.is_numeric_dtype(df[column]):
            continue
        converted = pd.to_numeric(df[column], errors='coerce')
        if len(df) and converted.notna().sum() >= max(10, int(len(df) * 0.90)):
            df[column] = converted

    if 'Age' in df.columns:
        age = pd.to_numeric(df['Age'], errors='coerce')
        invalid = int(((age < 1) | (age > 100)).sum())
        age = age.mask((age < 1) | (age > 100))
        missing_or_invalid = int(age.isna().sum())
        median = float(age.median()) if age.notna().any() else 0.0
        df['Age'] = age.fillna(median)
        actions.append(['Age', 'Missing / invalid ages', missing_or_invalid, invalid,
                        f'Filled invalid/missing ages with median ({median:.2f}).'])

    # Parse likely date/time fields only when parsing succeeds for most rows.
    for column in list(df.columns):
        if 'date' in column.lower() or 'time' in column.lower():
            parsed = pd.to_datetime(df[column], errors='coerce')
            if parsed.notna().sum() >= max(3, int(len(df) * 0.50)):
                df[column] = parsed

    for column in ['Gender', 'Flight Status', 'Nationality', 'Country Name', 'Continents']:
        if column in df.columns:
            df[column] = df[column].astype('string').str.strip()

    removed = []
    for column in list(df.columns):
        if column in AIRLINE_DROP_COLUMNS:
            removed.append(column)
            df.drop(columns=column, inplace=True)
            actions.append([column, 'Identifier / redundant field', 'present', 'removed',
                            'Removed from analytical dataset.'])

    # Fill remaining missing values with simple, reproducible rules.
    for column in df.columns:
        missing = int(df[column].isna().sum())
        if not missing:
            continue
        if pd.api.types.is_numeric_dtype(df[column]):
            value = float(df[column].median()) if df[column].notna().any() else 0.0
            df[column] = df[column].fillna(value)
            action = f'Filled with median ({value:.2f}).'
        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            mode = df[column].mode()
            value = mode.iloc[0] if len(mode) else pd.Timestamp('2000-01-01')
            df[column] = df[column].fillna(value)
            action = 'Filled missing dates with the most frequent date.'
        else:
            mode = df[column].mode()
            value = mode.iloc[0] if len(mode) else 'Unknown'
            df[column] = df[column].fillna(value)
            action = 'Filled with the most frequent category.'
        actions.append([column, 'Missing values', missing, 0, action])

    return df, actions, original_shape, removed
