-- SQL-запросы проекта «Спортивные матчи».
-- Каждый запрос начинается с маркера "-- name:"; файл matches/db.py загружает запросы по имени.
-- Запросы 4 и 5 содержат заполнитель {order_by}: db.py заменяет его константным
-- фрагментом, выбранным из белого списка (никогда не текстом пользователя).

-- Критерий SQL 1: список матчей с JOIN к площадкам.
-- name: matches_all
SELECT m.id, m.title, m.slug, m.sport_type, m.match_date, m.duration,
       m.tickets, m.status, c.name AS court_name
FROM matches AS m
JOIN courts AS c ON c.id = m.court_id
ORDER BY m.match_date ASC;

-- Критерий SQL 2: фильтр по минимальному количеству билетов (параметр ?).
-- name: matches_min_tickets
SELECT m.id, m.title, m.slug, m.sport_type, m.match_date, m.duration,
       m.tickets, m.status, c.name AS court_name
FROM matches AS m
JOIN courts AS c ON c.id = m.court_id
WHERE m.tickets >= ?
ORDER BY m.match_date ASC;

-- Критерий SQL 3: один матч по slug с данными площадки.
-- name: match_by_slug
SELECT m.id, m.title, m.slug, m.sport_type, m.match_date, m.duration,
       m.tickets, m.status, c.name AS court_name,
       c.capacity AS court_capacity, c.surface_type AS court_surface_type
FROM matches AS m
JOIN courts AS c ON c.id = m.court_id
WHERE m.slug = ?;

-- Критерий SQL 4: сортировка ORDER BY (поле и направление из белого списка).
-- name: matches_sorted
SELECT m.id, m.title, m.slug, m.sport_type, m.match_date, m.duration,
       m.tickets, m.status, c.name AS court_name
FROM matches AS m
JOIN courts AS c ON c.id = m.court_id
WHERE m.tickets >= ?
ORDER BY {order_by};

-- Критерий SQL 5: ограничение количества записей LIMIT (параметр ?).
-- name: matches_limited
SELECT m.id, m.title, m.slug, m.sport_type, m.match_date, m.duration,
       m.tickets, m.status, c.name AS court_name
FROM matches AS m
JOIN courts AS c ON c.id = m.court_id
WHERE m.tickets >= ?
ORDER BY {order_by}
LIMIT ?;

-- Критерий SQL 6: общее количество матчей.
-- name: matches_count
SELECT COUNT(*) AS total
FROM matches;

-- Критерий SQL 7: количество матчей по видам спорта (GROUP BY).
-- name: sport_counts
SELECT sport_type, COUNT(*) AS match_count
FROM matches
GROUP BY sport_type
ORDER BY match_count DESC, sport_type ASC;

-- Критерий SQL 8: виды спорта с количеством матчей не менее N (HAVING).
-- name: sport_counts_having
SELECT sport_type, COUNT(*) AS match_count
FROM matches
GROUP BY sport_type
HAVING COUNT(*) >= ?
ORDER BY match_count DESC, sport_type ASC;

-- Критерий SQL 9: список площадок.
-- name: courts_all
SELECT id, name, capacity, surface_type
FROM courts
ORDER BY name ASC;