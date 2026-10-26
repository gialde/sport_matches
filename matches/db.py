"""Слой доступа к данным: «сырой» SQL через стандартный модуль sqlite3.

Django ORM в проекте намеренно не используется.
Тексты запросов хранятся в sql/queries.sql и загружаются по имени.
"""

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

DB_ERROR_MESSAGE = (
    'Не удалось получить данные из базы данных. '
    'Попробуйте обновить страницу немного позже.'
)

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

QUERY_MARKER = '-- name:'
ORDER_BY_PLACEHOLDER = '{order_by}'

# Белые списки. Пользователь передаёт только ключ, а фрагмент SQL — это
# константа, заданная здесь, поэтому текст пользователя не попадает в SQL.
SORT_FIELDS = {
    'date': 'm.match_date',
    'tickets': 'm.tickets',
    'title': 'm.title',
    'duration': 'm.duration',
}
SORT_LABELS = {
    'date': 'дата матча',
    'tickets': 'количество билетов',
    'title': 'название',
    'duration': 'длительность',
}
SORT_DIRECTIONS = {
    'asc': 'ASC',
    'desc': 'DESC',
}
DIRECTION_LABELS = {
    'asc': 'по возрастанию',
    'desc': 'по убыванию',
}
DEFAULT_SORT = 'date'
DEFAULT_DIRECTION = 'asc'


def load_queries():
    """Читает sql/queries.sql и возвращает словарь {имя запроса: текст SQL}."""
    text = Path(settings.SQL_QUERIES_PATH).read_text(encoding='utf-8')
    queries = {}
    current_name = None
    current_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(QUERY_MARKER):
            if current_name is not None:
                queries[current_name] = '\n'.join(current_lines).strip()
            current_name = stripped[len(QUERY_MARKER):].strip()
            current_lines = []
        elif current_name is not None and not stripped.startswith('--'):
            current_lines.append(line)
    if current_name is not None:
        queries[current_name] = '\n'.join(current_lines).strip()
    return queries


def get_query(name):
    """Возвращает текст SQL-запроса по его имени."""
    return load_queries()[name]


def get_connection():
    """Открывает соединение с файлом SQLite только для чтения.

    Режим «только чтение» гарантирует, что при отсутствии файла возникнет
    ошибка sqlite3.OperationalError, а пустая база не будет создана молча.
    """
    db_uri = Path(settings.MATCHES_DB_PATH).resolve().as_uri() + '?mode=ro'
    connection = sqlite3.connect(db_uri, uri=True)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def database_connection():
    """Контекстный менеджер: соединение всегда закрывается."""
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()


def _row_to_dict(row):
    """Преобразует sqlite3.Row в словарь и разбирает match_date в datetime."""
    record = dict(row)
    raw_date = record.get('match_date')
    if isinstance(raw_date, str):
        try:
            record['match_date'] = datetime.strptime(raw_date, DATE_FORMAT)
        except ValueError:
            logger.warning('Неожиданный формат даты матча: %r', raw_date)
    return record


def fetch_all(sql, params=()):
    """Выполняет параметризованный SELECT и возвращает все строки как словари."""
    with database_connection() as connection:
        cursor = connection.execute(sql, params)
        return [_row_to_dict(row) for row in cursor.fetchall()]


def fetch_one(sql, params=()):
    """Выполняет параметризованный SELECT и возвращает одну строку или None."""
    with database_connection() as connection:
        cursor = connection.execute(sql, params)
        row = cursor.fetchone()
        return _row_to_dict(row) if row is not None else None


def build_order_by(sort, direction):
    """Возвращает константный фрагмент ORDER BY, выбранный из белых списков."""
    if sort not in SORT_FIELDS:
        raise ValueError('Недопустимое поле сортировки')
    if direction not in SORT_DIRECTIONS:
        raise ValueError('Недопустимое направление сортировки')
    return f'{SORT_FIELDS[sort]} {SORT_DIRECTIONS[direction]}, m.id ASC'


def get_matches():
    """Критерий SQL 1: все матчи с названием площадки (JOIN)."""
    return fetch_all(get_query('matches_all'))


def get_matches_by_min_tickets(min_tickets):
    """Критерий SQL 2: матчи, у которых tickets >= min_tickets."""
    return fetch_all(get_query('matches_min_tickets'), (min_tickets,))


def get_match_by_slug(slug):
    """Критерий SQL 3: один матч с данными площадки или None."""
    return fetch_one(get_query('match_by_slug'), (slug,))


def get_matches_sorted(min_tickets, sort, direction):
    """Критерий SQL 4: отфильтрованные матчи с проверенным ORDER BY."""
    order_by = build_order_by(sort, direction)
    sql = get_query('matches_sorted').replace(ORDER_BY_PLACEHOLDER, order_by)
    return fetch_all(sql, (min_tickets,))


def get_matches_limited(min_tickets, sort, direction, limit):
    """Критерий SQL 5: отфильтрованные, отсортированные матчи с LIMIT-параметром."""
    order_by = build_order_by(sort, direction)
    sql = get_query('matches_limited').replace(ORDER_BY_PLACEHOLDER, order_by)
    return fetch_all(sql, (min_tickets, limit))


def count_matches():
    """Критерий SQL 6: общее количество матчей."""
    row = fetch_one(get_query('matches_count'))
    return row['total']


def get_sport_counts():
    """Критерий SQL 7: количество матчей по видам спорта (GROUP BY)."""
    return fetch_all(get_query('sport_counts'))


def get_sport_counts_having(min_count):
    """Критерий SQL 8: виды спорта, у которых не менее min_count матчей (HAVING)."""
    return fetch_all(get_query('sport_counts_having'), (min_count,))


def get_courts():
    """Критерий SQL 9: список площадок."""
    return fetch_all(get_query('courts_all'))


def find_matches(min_tickets=None, sort=None, direction=None, limit=None):
    """Выбирает наиболее подходящий запрос для проверенных параметров страницы.

    Все аргументы должны быть заранее проверены представлением. Без сортировки
    и ограничения используются запросы 1 и 2, иначе — запросы 4 и 5.
    """
    if sort is None and direction is None and limit is None:
        if min_tickets is None:
            return get_matches()
        return get_matches_by_min_tickets(min_tickets)

    threshold = 0 if min_tickets is None else min_tickets
    sort = sort or DEFAULT_SORT
    direction = direction or DEFAULT_DIRECTION
    if limit is None:
        return get_matches_sorted(threshold, sort, direction)
    return get_matches_limited(threshold, sort, direction, limit)