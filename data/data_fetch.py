from configuration.config import Config
import pandas as pd
import psycopg2.extras
from dotenv import load_dotenv
import os

load_dotenv()

def fetch_stock_data(symbol):
    conn = psycopg2.connect(
        host=Config.get_host_name(),
        dbname=Config.get_database_name(),
        user=Config.get_username(),
        password=Config.get_password(),
        port=Config.get_port_id(),
        sslmode='require'
    )
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = """
    SELECT date, open, high, low, close, volume 
    FROM public.daily_data
    WHERE symbol = %s
    AND date >= '2023-01-01'
    ORDER BY date ASC
    """
    cur.execute(query, (symbol,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    df = pd.DataFrame(rows, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df