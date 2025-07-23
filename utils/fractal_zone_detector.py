def detect_fractal_zones(df, threshold=0.05, min_range_width=5.0, recent_days=90):
    df = df.copy()
    df_recent = df.tail(recent_days).reset_index()

    highs = df_recent['high'].tolist()
    lows = df_recent['low'].tolist()
    dates = df_recent['date'].tolist() if 'date' in df_recent.columns else df_recent.index.tolist()

    def get_fractals(highs, lows, dates):
        supports, resistances = [], []
        for i in range(2, len(highs)-2):
            if highs[i] > highs[i-2] and highs[i] > highs[i-1] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                resistances.append((highs[i], dates[i]))
            if lows[i] < lows[i-2] and lows[i] < lows[i-1] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                supports.append((lows[i], dates[i]))
        return supports, resistances

    supports_raw, resistances_raw = get_fractals(highs, lows, dates)

    def cluster_zones(levels_with_dates):
        clusters = []
        for price, date in sorted(levels_with_dates, key=lambda x: x[0]):
            added = False
            for cluster in clusters:
                avg_price = sum(p for p, _ in cluster) / len(cluster)
                if abs(price - avg_price) / price < threshold:
                    cluster.append((price, date))
                    added = True
                    break
            if not added:
                clusters.append([(price, date)])

        final_zones = []
        for cluster in clusters:
            prices = [p for p, _ in cluster]
            dates = [d for _, d in cluster]
            low, high = min(prices), max(prices)
            if len(prices) >= 2:
                recency = max(dates)
                final_zones.append({'range': (round(low, 2), round(high, 2)), 'recency': recency})
        return sorted(final_zones, key=lambda x: x['recency'], reverse=True)

    support_zones = cluster_zones(supports_raw)[:3]
    resistance_zones = cluster_zones(resistances_raw)[:3]

    return support_zones, resistance_zones

def format_zone_ranges(zones):
    return ", ".join([f"{z['range'][0]:.2f} - {z['range'][1]:.2f}" for z in zones])