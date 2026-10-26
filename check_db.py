import sqlite3

# Подключаемся к нашей базе данных
conn = sqlite3.connect('data/matches.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- 1. Список площадок (SELECT * FROM courts) ---")
cursor.execute("SELECT * FROM courts;")
for row in cursor.fetchall():
    print(dict(row))

print("\n--- 2. Список матчей с JOIN (Критерий 1) ---")
cursor.execute("""
    SELECT m.title, m.tickets, c.name AS court_name 
    FROM matches AS m 
    JOIN courts AS c ON c.id = m.court_id 
    LIMIT 3;
""")
for row in cursor.fetchall():
    print(dict(row))

print("\n--- 3. Статистика с GROUP BY и HAVING (Критерий 8) ---")
cursor.execute("""
    SELECT sport_type, COUNT(*) AS match_count 
    FROM matches 
    GROUP BY sport_type 
    HAVING COUNT(*) >= 2;
""")
for row in cursor.fetchall():
    print(dict(row))

conn.close()