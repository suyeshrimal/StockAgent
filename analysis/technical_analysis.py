import pandas as pd
import numpy as np
import ta
from langchain import LLMChain, PromptTemplate
from data.data_fetch import fetch_stock_data
from utils.rsi_calculation import calculate_rsi
from utils.json_serializable import make_json_serializable
from lang_graph.state import State

def technical_analysis(state: dict) -> dict:
    symbol = state["symbol"]
    llm = state["llm"]

    hist = fetch_stock_data(symbol)

    # Clean and prepare data
    hist['high'] = pd.to_numeric(hist['high'], errors='coerce')
    hist['low'] = pd.to_numeric(hist['low'], errors='coerce')
    hist['close'] = pd.to_numeric(hist['close'], errors='coerce')
    hist['volume'] = pd.to_numeric(hist['volume'], errors='coerce')
    hist.fillna(method='ffill', inplace=True)
    hist.fillna(method='bfill', inplace=True)

    # Technical indicators
    sma_20 = hist['close'].rolling(window=20).mean()
    sma_50 = hist['close'].rolling(window=50).mean()
    rsi = calculate_rsi(hist['close'])

    exp1 = hist['close'].ewm(span=12, adjust=False).mean()
    exp2 = hist['close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()

    std_20 = hist['close'].rolling(window=20).std()
    upper_band = sma_20 + (2 * std_20)
    lower_band = sma_20 - (2 * std_20)

    adx = ta.trend.ADXIndicator(hist['high'], hist['low'], hist['close'], window=14).adx()

    low_14 = hist['low'].rolling(14).min()
    high_14 = hist['high'].rolling(14).max()
    k = 100 * ((hist['close'] - low_14) / (high_14 - low_14))
    d = k.rolling(3).mean()

    closing_prices = hist['close'].tail(30).tolist()

    # Fractal support/resistance detection
    def get_fractal_levels_with_dates(highs, lows, dates):
        support_levels, resistance_levels = [], []
        for i in range(2, len(highs) - 2):
            if all(highs[i] >= highs[j] for j in [i-2, i-1, i+1, i+2]):
                resistance_levels.append((highs[i], dates[i]))
            if all(lows[i] <= lows[j] for j in [i-2, i-1, i+1, i+2]):
                support_levels.append((lows[i], dates[i]))
        return support_levels, resistance_levels

    def cluster_levels_with_dates(levels_with_dates, threshold=0.05):
        clusters = []
        levels_with_dates = sorted(levels_with_dates, key=lambda x: x[0])
        for price, date in levels_with_dates:
            added = False
            for cluster in clusters:
                avg_price = sum(p for p, _ in cluster) / len(cluster)
                if abs(price - avg_price) / price < threshold:
                    cluster.append((price, date))
                    added = True
                    break
            if not added:
                clusters.append([(price, date)])

        zone_ranges = []
        for cluster in clusters:
            prices = [p for p, _ in cluster]
            dates = [d for _, d in cluster]
            low, high = round(min(prices), 2), round(max(prices), 2)
            if len(prices) >= 2:  # key change here
                zone_ranges.append({'range': (low, high), 'recency': max(dates)})
        return sorted(zone_ranges, key=lambda x: x['recency'], reverse=True)


    # Apply fractal detection
    recent_hist = hist.tail(90).reset_index()
    date_col = 'date' if 'date' in recent_hist.columns else recent_hist.index
    supports_fd, resistances_fd = get_fractal_levels_with_dates(
        recent_hist['high'].tolist(),
        recent_hist['low'].tolist(),
        recent_hist[date_col].tolist()
    )
    fractal_support_zones = cluster_levels_with_dates(supports_fd)
    fractal_resistance_zones = cluster_levels_with_dates(resistances_fd)

    def format_zone_ranges(zones):
        return ", ".join([f"{zone['range'][0]:.2f} - {zone['range'][1]:.2f}" for zone in zones[:3]])

    raw_data = {
        'current_price': hist['close'].iloc[-1],
        'sma_20': sma_20.iloc[-1],
        'sma_50': sma_50.iloc[-1],
        'rsi': rsi.iloc[-1],
        'volume_trend': hist['volume'].iloc[-5:].mean() / hist['volume'].iloc[-20:].mean(),
        'macd': macd.iloc[-1],
        'macd_signal': signal.iloc[-1],
        'bollinger_upper': upper_band.iloc[-1],
        'bollinger_lower': lower_band.iloc[-1],
        'adx': adx.iloc[-1],
        'stochastic_k': k.iloc[-1],
        'stochastic_d': d.iloc[-1],
        'closing_prices': closing_prices,
        'fractal_support_zones': format_zone_ranges(fractal_support_zones),
        'fractal_resistance_zones': format_zone_ranges(fractal_resistance_zones),
    }

    data = make_json_serializable(raw_data)

    prompt = PromptTemplate(
        input_variables=[
            "symbol", "current_price", "sma_20", "sma_50", "rsi",
            "volume_trend", "macd", "macd_signal", "bollinger_upper",
            "bollinger_lower", "adx", "stochastic_k", "stochastic_d",
            "closing_prices", "fractal_support_zones", "fractal_resistance_zones"
        ],
        template="""
            You are a highly skilled stock technical analyst.

            Analyze the technical data for the stock symbol **{symbol}**:

            ---
            Technical Indicators:
            - Current Price: {current_price}
            - 20-day SMA: {sma_20}
            - 50-day SMA: {sma_50}
            - RSI: {rsi}
            - Volume Trend (5-day / 20-day avg): {volume_trend:.2f}
            - MACD: {macd}
            - MACD Signal Line: {macd_signal}
            - Bollinger Upper Band: {bollinger_upper}
            - Bollinger Lower Band: {bollinger_lower}
            - ADX: {adx}
            - Stochastic %K: {stochastic_k}
            - Stochastic %D: {stochastic_d}

            Recent Closing Prices (last 30 days):
            {closing_prices}
            ---
            **Fractal-Based Support/Resistance Zones:**
            - Support Zones: {fractal_support_zones}
            - Resistance Zones: {fractal_resistance_zones}

            Provide a structured analysis with the following:

            **1. Trend Direction:**
            Interpret SMA, MACD, ADX, and Bollinger Bands to describe the market trend (bullish, bearish, sideways). Justify your analysis.

            **2. Support and Resistance Levels (Fractal-Based Only):**
            - Do NOT refer to any indicator (Bollinger Bands, RSI, MACD, SMA, ADX, etc.) in your support/resistance analysis.
            - ONLY use the **fractal-based support and resistance zones** listed above.
            - Identify at least **3 key support** and **3 key resistance ranges** (price intervals) from those zones.
            - Use the exact ranges as provided (e.g., 230.50 - 233.00), do NOT pick single prices.
            - For each range, mention how many times the price zone was tested or why it is significant (e.g., reversal zone, psychological round number).
            - Distinguish between **strong** and **weak** levels.
            - Mention **psychological levels** (e.g., round numbers like 100, 200) if applicable.
            - Present the levels in descending order of importance.

            **3. Indicator Insights:**
            - RSI status (overbought/oversold/neutral).
            - Bollinger Band squeeze or breakout.
            - MACD crossovers or divergence.
            - Stochastic crossover interpretation.
            - ADX trend strength (>25 = strong trend).

            **4. Volume & Momentum:**
            Evaluate volume trend and how it supports or contradicts price movements.

            Keep your response concise, focused, and trader-friendly.
        """
    
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    analysis = chain.run(
        symbol=symbol,
        current_price=data["current_price"],
        sma_20=data["sma_20"],
        sma_50=data["sma_50"],
        rsi=data["rsi"],
        volume_trend=data["volume_trend"],
        macd=data["macd"],
        macd_signal=data["macd_signal"],
        bollinger_upper=data["bollinger_upper"],
        bollinger_lower=data["bollinger_lower"],
        adx=data["adx"],
        stochastic_k=data["stochastic_k"],
        stochastic_d=data["stochastic_d"],
        closing_prices=", ".join([f"{x:.2f}" for x in data["closing_prices"]]),
        fractal_support_zones=data["fractal_support_zones"],
        fractal_resistance_zones=data["fractal_resistance_zones"],
    )

    state["results"]["technical"] = {
        "data": data,
        "analysis": analysis
    }
    return state
