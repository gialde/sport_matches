import logging
import sqlite3

from django.shortcuts import render

from matches import db

logger = logging.getLogger(__name__)


def home(request):
    """Главная страница с общим числом матчей из SELECT COUNT(*)."""
    total_matches = None
    error = None
    try:
        total_matches = db.count_matches()
    except sqlite3.Error:
        logger.exception('Ошибка SQLite при подсчёте матчей на главной странице')
        error = db.DB_ERROR_MESSAGE

    context = {'total_matches': total_matches, 'error': error}
    status = 500 if error else 200
    return render(request, 'homepage/home.html', context, status=status)