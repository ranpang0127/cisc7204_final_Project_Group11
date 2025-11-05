import pandas as pd
import numpy as np
import ast


def analyze_climate_data(climate_data):
    df = pd.DataFrame(climate_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp').sort_index()
    df['month'] = df.index.month
    df['day'] = df.index.day
    df['hour'] = df.index.hour

    def calc_feels_like(row):
        temp, wind = row['temperature'], row['wind_speed']
        if temp < 10 and wind > 5:
            v = wind ** 0.16
            return 13.12 + 0.6215 * temp - 11.37 * v + 0.3965 * temp * v
        return temp
    df['feels_like'] = df.apply(calc_feels_like, axis=1)

    def calc_heat_index(row):
        temp, hum = row['temperature'], row['humidity']
        if temp > 25 and hum > 40:
            return -8.784 + 1.61 * hum + 2.338 * temp - 0.14 * hum * temp
        return temp
    df['heat_index'] = df.apply(calc_heat_index, axis=1)

    def get_weather_cond(row):
        precip = row['precipitation']
        if precip > 10: return 'Storm'
        if precip > 0: return 'Rain'
        if row['wind_speed'] > 20: return 'Windy'
        if row['humidity'] > 85: return 'Humid'
        return 'Clear'
    df['weather_condition'] = df.apply(get_weather_cond, axis=1)

    def mode_safe(x):
        if x.empty or pd.isna(x).all(): return np.nan
        m = x.mode()
        if m.empty: return x.dropna().iloc[0]
        return m.iloc[0]

    agg_dict = {
        'station_id': 'first', 'region': 'first', 'elevation': 'first',
        'temperature': 'mean', 'humidity': 'mean', 'pressure': 'mean',
        'precipitation': 'sum', 'wind_speed': 'max',
        'feels_like': 'mean', 'heat_index': 'mean',
        'month': 'first', 'day': 'first', 'hour': 'first',
        'wind_direction': mode_safe, 'weather_condition': mode_safe
    }

    hourly_dfs = []
    for station_id, group in df.groupby('station_id'):
        group_resampled = group.resample('h').agg(agg_dict)
        group_resampled['station_id'] = station_id
        hourly_dfs.append(group_resampled)

    hourly_df = pd.concat(hourly_dfs).sort_index()

    def window_diff(window):
        n = len(window)
        if n > 1: return window.iloc[-1] - window.iloc[0]
        return 0.0

    def window_rate(window):
        n = len(window)
        if n > 1: return (window.iloc[-1] - window.iloc[0]) / (n - 1)
        return 0.0

    hourly_df['temperature_trend'] = hourly_df.groupby('station_id')['temperature'].transform(
        lambda x: x.rolling(3, min_periods=1).apply(window_diff, raw=False)
    )

    hourly_df['pressure_change_rate'] = hourly_df.groupby('station_id')['pressure'].transform(
        lambda x: x.rolling(3, min_periods=1).apply(window_rate, raw=False)
    )

    station_stats = hourly_df.groupby('station_id')['temperature'].agg(['mean', 'std']).reset_index()
    hourly_df = hourly_df.reset_index().merge(station_stats, on='station_id').set_index('timestamp')
    hourly_df['std'] = hourly_df['std'].replace(0, 1e-6)
    hourly_df['temperature_anomaly'] = np.abs(hourly_df['temperature'] - hourly_df['mean']) > 2 * hourly_df['std']

    hourly_df['date'] = hourly_df.index.date

    grouped = hourly_df.groupby(['region', 'date']).agg(
        daily_temp_range=('temperature', lambda x: round(x.max() - x.min(), 2)),
        precip_total=('precipitation', 'sum'),
        hours_with_precip=('precipitation', lambda x: (x > 0).sum()),
        wind_direction_mode=('wind_direction', mode_safe),
        avg_wind_speed=('wind_speed', lambda x: round(x.mean(), 2))
    ).reset_index()

    grouped['precipitation_intensity'] = np.where(
        grouped['hours_with_precip'] == 0, 0.0,
        round(grouped['precip_total'] / grouped['hours_with_precip'], 2)
    )

    def normalize(series):
        min_val, max_val = series.min(), series.max()
        if max_val == min_val: return pd.Series(0.0, index=series.index)
        return round((series - min_val) / (max_val - min_val), 2)

    grouped['norm_range'] = normalize(grouped['daily_temp_range'])
    grouped['norm_intensity'] = normalize(grouped['precipitation_intensity'])
    grouped['norm_wind'] = normalize(grouped['avg_wind_speed'])
    grouped['regional_severity_index'] = round(
        0.3 * grouped['norm_range'] + 0.3 * grouped['norm_intensity'] + 0.4 * grouped['norm_wind'], 2
    )

    grouped = grouped.drop(['precip_total', 'hours_with_precip', 'date', 'norm_range', 'norm_intensity', 'norm_wind', 'avg_wind_speed'], axis=1)
    grouped = grouped.sort_values(['regional_severity_index', 'region'], ascending=[False, True]).reset_index(drop=True)

    result = grouped[['region', 'daily_temp_range', 'precipitation_intensity', 'wind_direction_mode', 'regional_severity_index']]

    result['daily_temp_range'] = result['daily_temp_range'].round(2)
    result['precipitation_intensity'] = result['precipitation_intensity'].round(2)
    result['regional_severity_index'] = result['regional_severity_index'].round(2)

    return result


climate_data = ast.literal_eval(input().strip())
result_df = analyze_climate_data(climate_data)
print(result_df.to_string(float_format=lambda x: f"{x:.2f}"))
