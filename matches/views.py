"""Функциональные представления приложения matches."""

import logging
import sqlite3

from django.http import Http404
from django.shortcuts import render

from . import db

logger = logging.getLogger(__name__)

MAX_LIMIT = 100
DEFAULT_HAVING_THRESHOLD = 3
MAX_DIGITS = 9


def clean(value):
    """Возвращает строку без пробелов по краям; None превращается в пустую строку."""
    return (value or '').strip()


def parse_int(raw):
    """Возвращает целое число >= 0 для строки из ASCII-цифр, иначе None."""
    text = clean(raw)
    if not text or len(text) > MAX_DIGITS:
        return None
    if not (text.isascii() and text.isdigit()):
        return None
    return int(text)


def match_list(request):
    """Список матчей с GET-фильтром, проверенной сортировкой и ограничением."""
    warnings = []

    tickets_text = clean(request.GET.get('tickets'))
    sort_text = clean(request.GET.get('sort'))
    direction_text = clean(request.GET.get('dir'))
    limit_text = clean(request.GET.get('limit'))

    min_tickets = None
    if tickets_text:
        min_tickets = parse_int(tickets_text)
        if min_tickets is None:
            warnings.append('Минимальное количество билетов должно быть целым неотрицательным числом. Фильтр не применён.')

    sort = None
    if sort_text:
        if sort_text in db.SORT_FIELDS:
            sort = sort_text
        else:
            warnings.append('Неизвестное поле сортировки. Применена сортировка по умолчанию.')

    direction = None
    if direction_text:
        if direction_text in db.SORT_DIRECTIONS:
            direction = direction_text
        else:
            warnings.append('Неизвестное направление сортировки. Применено направление по умолчанию.')

    limit = None
    if limit_text:
        parsed_limit = parse_int(limit_text)
        if parsed_limit is not None and 1 <= parsed_limit <= MAX_LIMIT:
            limit = parsed_limit
        else:
            warnings.append(f'Ограничение должно быть целым числом от 1 до {MAX_LIMIT}. Ограничение не применено.')

    matches = []
    error = None
    try:
        matches = db.find_matches(min_tickets, sort, direction, limit)
    except sqlite3.Error:
        logger.exception('Ошибка SQLite при чтении списка матчей')
        error = db.DB_ERROR_MESSAGE

    selected_sort = sort or db.DEFAULT_SORT
    selected_direction = direction or db.DEFAULT_DIRECTION

    context = {
        'matches': matches,
        'error': error,
        'warnings': warnings,
        'min_tickets': min_tickets,
        'limit': limit,
        'max_limit': MAX_LIMIT,
        'selected_sort': selected_sort,
        'selected_direction': selected_direction,
        'sort_label': db.SORT_LABELS[selected_sort],
        'direction_label': db.DIRECTION_LABELS[selected_direction],
        'sort_options': [{'value': key, 'label': label} for key, label in db.SORT_LABELS.items()],
        'direction_options': [{'value': key, 'label': label} for key, label in db.DIRECTION_LABELS.items()],
    }
    status = 500 if error else 200
    return render(request, 'matches/match_list.html', context, status=status)


def match_detail(request, slug):
    """Страница одного матча по slug; если матча нет, возвращается 404."""
    try:
        match = db.get_match_by_slug(slug)
    except sqlite3.Error:
        logger.exception('Ошибка SQLite при чтении матча %r', slug)
        context = {'match': None, 'error': db.DB_ERROR_MESSAGE}
        return render(request, 'matches/match_detail.html', context, status=500)

    if match is None:
        raise Http404('Матч не найден')

    context = {'match': match, 'error': None}
    return render(request, 'matches/match_detail.html', context)


def statistics(request):
    """Статистика: таблица GROUP BY и таблица HAVING с проверенным порогом."""
    warnings = []

    threshold = DEFAULT_HAVING_THRESHOLD
    threshold_text = clean(request.GET.get('min'))
    if threshold_text:
        parsed_threshold = parse_int(threshold_text)
        if parsed_threshold is None or parsed_threshold < 1:
            warnings.append('Порог должен быть целым положительным числом. Использовано значение по умолчанию.')
        else:
            threshold = parsed_threshold

    total_matches = None
    sport_counts = []
    sport_having = []
    error = None
    try:
        total_matches = db.count_matches()
        sport_counts = db.get_sport_counts()
        sport_having = db.get_sport_counts_having(threshold)
    except sqlite3.Error:
        logger.exception('Ошибка SQLite при построении статистики')
        error = db.DB_ERROR_MESSAGE

    context = {
        'total_matches': total_matches,
        'sport_counts': sport_counts,
        'sport_having': sport_having,
        'threshold': threshold,
        'warnings': warnings,
        'error': error,
    }
    status = 500 if error else 200
    return render(request, 'matches/statistics.html', context, status=status)