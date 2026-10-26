"""Создаёт таблицы и вставляет тестовые данные в data/matches.db.

Запуск из корня проекта:  python data/seed.py
Скрипт можно запускать повторно: обе таблицы пересоздаются.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'matches.db'

SCHEMA = """
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS courts;

CREATE TABLE courts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    surface_type TEXT NOT NULL
);

CREATE TABLE matches (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    sport_type TEXT NOT NULL,
    match_date TEXT NOT NULL,
    duration INTEGER NOT NULL,
    tickets INTEGER NOT NULL,
    status TEXT NOT NULL,
    court_id INTEGER NOT NULL REFERENCES courts(id)
);
"""

COURTS = [
    (1, 'Арена «Север»', 45000, 'натуральный газон'),
    (2, 'Дворец спорта «Олимп»', 12000, 'паркет'),
    (3, 'Центральный стадион', 30000, 'натуральный газон'),
    (4, 'Спорткомплекс «Волна»', 3500, 'синтетическое покрытие'),
]

MATCHES = [
    (1, 'Зенит — Динамо', 'zenit-dinamo', 'футбол',
     '2026-03-14 18:00:00', 110, 500, 'завершён', 1),
    (2, 'ЦСКА — Спартак', 'cska-spartak', 'футбол',
     '2026-05-09 19:30:00', 105, 350, 'завершён', 3),
    (3, 'Краснодар — Ахмат', 'krasnodar-akhmat', 'футбол',
     '2026-10-24 15:00:00', 100, 200, 'идёт', 1),
    (4, 'Ростов — Сочи', 'rostov-sochi', 'футбол',
     '2026-11-15 17:00:00', 95, 120, 'запланирован', 3),
    (5, 'ЦСКА — Химки', 'cska-khimki', 'баскетбол',
     '2026-02-21 19:00:00', 130, 450, 'завершён', 2),
    (6, 'УНИКС — Локомотив-Кубань', 'unics-lokomotiv-kuban', 'баскетбол',
     '2026-12-06 18:30:00', 125, 80, 'запланирован', 2),
    (7, 'Парма — Зенит', 'parma-zenit', 'баскетбол',
     '2026-07-12 17:00:00', 140, 280, 'завершён', 2),
    (8, 'Динамо — Зенит-Казань', 'dinamo-zenit-kazan', 'волейбол',
     '2026-01-17 17:00:00', 135, 50, 'завершён', 4),
    (9, 'Локомотив — Белогорье', 'lokomotiv-belogorie', 'волейбол',
     '2026-12-20 16:00:00', 120, 160, 'запланирован', 4),
]


def seed():
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute('PRAGMA foreign_keys = ON')
        connection.executescript(SCHEMA)
        connection.executemany(
            'INSERT INTO courts (id, name, capacity, surface_type) '
            'VALUES (?, ?, ?, ?)',
            COURTS,
        )
        connection.executemany(
            'INSERT INTO matches (id, title, slug, sport_type, match_date, '
            'duration, tickets, status, court_id) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            MATCHES,
        )
        connection.commit()

        courts_total = connection.execute('SELECT COUNT(*) FROM courts').fetchone()[0]
        matches_total = connection.execute('SELECT COUNT(*) FROM matches').fetchone()[0]
        print(f'База данных создана: {DB_PATH}')
        print(f'Площадок: {courts_total}, матчей: {matches_total}')
    finally:
        connection.close()


if __name__ == '__main__':
    seed()