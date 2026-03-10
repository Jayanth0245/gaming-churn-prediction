import sqlite3
import random
import pandas as pd
from datetime import datetime, timedelta

random.seed(27)

#Creating the Database
conn = sqlite3.connect("gaming_churn.db")
cursor = conn.cursor()

print("✅ Database created!")

#Droping old tables
cursor.executescript("""
    DROP TABLE IF EXISTS players;
    DROP TABLE IF EXISTS sessions;
    DROP TABLE IF EXISTS transactions;
    DROP TABLE IF EXISTS churn;
""")

#Creating the Players Table
cursor.execute("""
CREATE TABLE players (
    player_id     INTEGER PRIMARY KEY,
    username      TEXT,
    age           INTEGER,
    country       TEXT,
    device        TEXT,
    account_type  TEXT,
    join_date     TEXT
)
""")
print("✅ Players table created!")

#Adding session table
cursor.execute("""
CREATE TABLE sessions (
    session_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id     INTEGER,
    session_date  TEXT,
    duration_mins INTEGER,
    level_reached INTEGER,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
)
""")
print("✅ Sessions table created!")

#Adding Transaction table
cursor.execute("""
CREATE TABLE transactions (
    transaction_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id       INTEGER,
    purchase_date   TEXT,
    item_name       TEXT,
    amount_usd      REAL,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
)
""")
print("✅ Transactions table created!")

#Adding Churn tABLE
cursor.execute("""
CREATE TABLE churn (
    player_id   INTEGER PRIMARY KEY,
    churned     INTEGER,
    churn_date  TEXT,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
)
""")
print("✅ Churn table created!")

#Defining your options
countries =["USA", "UK", "Germany", "Brazil", "India", "Canada", "Australia"]
devices   =["PC", "Mobile", "Console"]
acc_types =["Free", "Premium"]

base_date = datetime(2023, 1, 1)

players_data = []

for pid in range(1,1001):
    join_date    = base_date + timedelta(days=random.randint(0,180))
    account_type = random.choices(acc_types, weights=[70,30])[0]
    device       = random.choice(devices)
    country      = random.choice(countries)
    age          = random.randint(14,45)

    players_data.append((
        pid,
        f"player_{pid}",
        age,
        country,
        device,
        account_type,
        join_date.strftime("%Y-%m-%d")
    ))

cursor.executemany(
    "INSERT INTO players VALUES (?,?,?,?,?,?,?)", players_data)

conn.commit()
print(f"✅ {len(players_data)} players inserted!")

#GENERATING realistic gaming sessions and purchase history
items = ["Skin Pack", "XP Boosg", "Character Unlock", "Season Pass", "Loot Box"]

# Reset lists
sessions_data     = []
transactions_data = []
churn_data        = []

# One single loop for everything
for pid in range(1, 1001):

    # Get this player's info from players_data
    account_type = players_data[pid - 1][5]
    join_date    = datetime.strptime(players_data[pid - 1][6], "%Y-%m-%d")

    # ── Churn logic ──────────────────────────────
    churn_prob  = 0.35 if account_type == "Premium" else 0.60
    did_churn   = 1 if random.random() < churn_prob else 0
    last_active = join_date + timedelta(days=random.randint(30, 365))
    churn_date  = last_active.strftime("%Y-%m-%d") if did_churn else None
    days_active = max((last_active - join_date).days, 1)

    churn_data.append((pid, did_churn, churn_date))

    # ── Sessions ─────────────────────────────────
    n_sessions = random.randint(2, 15) if did_churn else random.randint(10, 80)

    for _ in range(n_sessions):
        sdate = join_date + timedelta(days=random.randint(0, days_active))
        sessions_data.append((
            pid,
            sdate.strftime("%Y-%m-%d"),
            random.randint(5, 180),
            random.randint(1, 50)
        ))

    # ── Transactions ──────────────────────────────
    n_txn = random.randint(0, 2) if did_churn else random.randint(0, 8)
    if account_type == "Premium":
        n_txn = int(n_txn * 1.5)

    for _ in range(n_txn):
        tdate = join_date + timedelta(days=random.randint(0, days_active))
        transactions_data.append((
            pid,
            tdate.strftime("%Y-%m-%d"),
            random.choice(items),
            round(random.uniform(0.99, 29.99), 2)
        ))

# ── Insert all data ───────────────────────────
cursor.executemany(
    "INSERT INTO sessions (player_id, session_date, duration_mins, level_reached) VALUES (?,?,?,?)",
    sessions_data)

cursor.executemany(
    "INSERT INTO transactions (player_id, purchase_date, item_name, amount_usd) VALUES (?,?,?,?)",
    transactions_data)

cursor.executemany(
    "INSERT INTO churn VALUES (?,?,?)",
    churn_data)

conn.commit()
print(f"✅ {len(sessions_data)} sessions inserted!")
print(f"✅ {len(transactions_data)} transactions inserted!")
print(f"✅ {len(churn_data)} churn records inserted!")

conn.commit()
print(f"✅ {len(sessions_data)} sessions inserted!")
print(f"✅{len(transactions_data)} transactions inserted!")
print(f"✅{len(churn_data)} churn records inserted!")

#Helper function
def run_query(title,sql):
    print("=" * 50)
    print(f"📌 {title}")
    print(f"SQL: {sql}")
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    print()
    return df

run_query(
    "First 5 players",
    "SELECT * FROM players LIMIT 5;"
)    

run_query(
    "How many players?",
    "SELECT COUNT(*) AS total_players FROM players;"
)

run_query(
    "Churned vs Stayed",
    """
    SELECT churned, COUNT(*) AS num_players
    FROM churn
    GROUP BY churned;
    """
)

run_query(
    "Churn rate by account type",
    """
    SELECT p.account_type,
    COUNT(*) AS total_players,
    ROUND(100.0 * SUM(c.churned) / COUNT(*), 1) AS churn_rate_pct
    FROM players p
    JOIN churn c ON p.player_id = c.player_id
    GROUP BY p.account_type;
    """
)

#Saving Master DATASET
master_query = """
SELECT
    p.player_id,
    p.age,
    p.country,
    p.device,
    p.account_type,
    p.join_date,
    COUNT(DISTINCT s.session_id) AS total_sessions,
    ROUND(AVG(s.duration_mins), 1) AS avg_session_mins,
    ROUND(SUM(s.duration_mins), 1) AS total_playtime_mins,
    MAX(s.level_reached) AS max_level,
    COALESCE(COUNT(DISTINCT t.transaction_id), 0) AS num_purchases,
    COALESCE(ROUND(SUM(t.amount_usd), 2), 0) AS total_spent_usd,
    c.churned

FROM players p
LEFT JOIN sessions s ON p.player_id = s.player_id
LEFT JOIN transactions t ON p.player_id = t.player_id
LEFT JOIN churn c ON p.player_id = c.player_id
GROUP BY p.player_id
"""

master_df = pd.read_sql_query(master_query, conn)
master_df.to_csv("gaming_master.csv", index = False)
print(f"✅ Master Dataset saved!")
print(f"  Shape: {master_df.shape[0]} player * {master_df.shape[1]} columns")
print(f"  Churn rate: {master_df['churned'].mean() * 100:.1f}%")

conn.close()
