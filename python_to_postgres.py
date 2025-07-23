import psycopg2
import psycopg2.extras
from configuration.config import Config
conn=None
cur=None

try:
    conn = psycopg2.connect(
        host = Config.get_host_name(),
        dbname = Config.get_database_name(),
        user = Config.get_username(),
        password = Config.get_password(),
        port = Config.get_port_id(),
        sslmode='require' 
    )

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT * FROM public.daily_data ORDER BY open DESC LIMIT 1")
    for record in cur.fetchall():
        print(record['symbol'], record['open'])

    conn.commit()
except Exception as e:
    print(e)

finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()