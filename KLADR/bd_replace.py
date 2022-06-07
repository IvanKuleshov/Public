def create_db(con):
    print(f"{time.strftime('%X')} Create database...", end='', flush=True)
    query = """
            DROP TABLE IF EXISTS info;
            CREATE TABLE IF NOT EXISTS info(
            id INTEGER PRIMARY KEY,
            symbol TEXT UNIQUE,
            status TEXT,
            baseAsset TEXT,
            quoteAsset TEXT,
            isSpotTradingAllowed BOOLEAN,
            isMarginTradingAllowed BOOLEAN,
            minQty FLOAT,
            minPrice FLOAT);
            """
    con.cursor().executescript(query)
    con.commit()
    print('Done')

def select_symbols(con):
    query = """
    SELECT symbol
    FROM info
    WHERE quoteAsset = 'USDT' and status = 'TRADING' and isSpotTradingAllowed = 1"""
    return [i[0] for i in con.cursor().execute(query).fetchall()]

query = f"""INSERT INTO info ({', '.join([f"{i}" for i in fields])})
            VALUES ({', '.join([f":{i}" for i in fields])})"""
cur.executemany(query, symbols)

con = sqlite3.connect("binance.db", isolation_level=None)

sql = '''SELECT * FROM debtors'''
df = pd.read_sql_query(sql=sql, con=conn)


UPDATE data
SET
STREET = replace(STREET,'Геодезческая','!Я улицо')