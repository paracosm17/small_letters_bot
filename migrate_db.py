import asyncio
import asyncpg
import sqlite3
import datetime


async def migrate_data():
    # Подключение к базе данных SQLite3
    sqlite_conn = sqlite3.connect('database.db')
    sqlite_cursor = sqlite_conn.cursor()

    # Подключение к базе данных PostgreSQL
    postgres_conn = await asyncpg.connect(
        user="alex",
        password=__import__("os").environ["POSTGRES_PASSWORD"],
        database="small_letters_bot_db",
        host="postgres"
    )

    try:
        # Получение данных из SQLite3 и их перенос в PostgreSQL
        sqlite_cursor.execute('SELECT user_id, username, full_name, language, created_at, updated_at FROM user')
        rows = sqlite_cursor.fetchall()
        for row in rows:
            try:
                created_at = datetime.datetime.strptime(row[-2], '%Y-%m-%d %H:%M:%S.%f')
            except:
                created_at = datetime.datetime.strptime(row[-2], '%Y-%m-%d %H:%M:%S')
            try:
                updated_at = datetime.datetime.strptime(row[-1], '%Y-%m-%d %H:%M:%S.%f')
            except:
                updated_at = datetime.datetime.strptime(row[-1], '%Y-%m-%d %H:%M:%S')
            try:
                await postgres_conn.execute('''
                    INSERT INTO "user" (user_id, username, full_name, language_code, created_at, last_active, 
                    banned, active)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ''', *row[:-2], created_at, updated_at, False, True)
            except Exception as e:
                print(e)
                continue

    finally:
        # Закрытие соединений
        await postgres_conn.close()
        sqlite_conn.close()

# Запуск асинхронной функции
asyncio.run(migrate_data())
