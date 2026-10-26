import logging
import sqlite3

from django.shortcuts import render

from matches import db

logger = logging.getLogger(__name__)


def court_list(request):
    """Список площадок, прочитанный из SQLite."""
    courts = []
    error = None
    try:
        courts = db.get_courts()
    except sqlite3.Error:
        logger.exception('Ошибка SQLite при чтении списка площадок')
        error = db.DB_ERROR_MESSAGE

    context = {'courts': courts, 'error': error}
    status = 500 if error else 200
    return render(request, 'courts/court_list.html', context, status=status)