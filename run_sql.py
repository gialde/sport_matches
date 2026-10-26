import sqlite3

def main():
    conn = sqlite3.connect('data/matches.db')
    print("Введи SQL-запрос (или 'exit' для выхода):")
    while True:
        query = input("\nSQL> ")
        if query.lower() == 'exit':
            break
        try:
            cursor = conn.execute(query)
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                for row in rows:
                    print(row)
            else:
                conn.commit()
                print("Успешно выполнено. Изменения сохранены.")
        except Exception as e:
            print("Ошибка:", e)
    conn.close()

if __name__ == '__main__':
    main()