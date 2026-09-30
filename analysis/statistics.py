import pandas as pd
from scipy.stats import chi2_contingency


def descriptive_statistics(df):
    result = {}
    for column in df.select_dtypes(include='number').columns:
        series = df[column].dropna()
        result[str(column)] = {
            'count': int(series.count()),
            'mean': round(float(series.mean()), 4),
            'median': round(float(series.median()), 4),
            'min': round(float(series.min()), 4),
            'max': round(float(series.max()), 4),
            'std': round(float(series.std()), 4) if len(series) > 1 else 0.0,
        }
    return result


def chi_square_tests(df, alpha=0.05):
    preferred_pairs = [
        ('Gender', 'Flight Status'),
        ('Continents', 'Flight Status'),
        ('Age Group', 'Flight Status'),
        ('Travel Type (Approx.)', 'Flight Status'),
        ('Day Type', 'Flight Status'),
    ]
    results = []
    for first, second in preferred_pairs:
        if first not in df.columns or second not in df.columns:
            continue
        table = pd.crosstab(df[first], df[second])
        if table.shape[0] < 2 or table.shape[1] < 2:
            continue
        chi, p_value, dof, _ = chi2_contingency(table)
        significant = bool(p_value < alpha)
        results.append({
            'variable_1': first,
            'variable_2': second,
            'chi_square': round(float(chi), 4),
            'p_value': round(float(p_value), 6),
            'degrees_of_freedom': int(dof),
            'significant': significant,
            'interpretation': (
                f'Statistically significant association at alpha = {alpha:.2f}.'
                if significant else
                f'No statistically significant association at alpha = {alpha:.2f}.'
            )
        })
    return results
