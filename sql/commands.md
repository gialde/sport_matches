# показывает список матчей с названиями площадок через JOIN
SELECT m.id, m.title, m.status, c.name AS court_name
FROM matches AS m
JOIN courts AS c ON c.id = m.court_id
ORDER BY m.match_date ASC;

# Изменить запись в таблице
UPDATE matches 
SET status = 'нет' 
WHERE slug = 'rostov-sochi';

# Добавление матчей и проверка их статистики с HAVING
INSERT INTO matches (title, slug, sport_type, match_date, duration, tickets, status, court_id) 
VALUES 
('Зенит-Казань — Кузбасс', 'zenit-kazan-kuzbass', 'волейбол', '2026-12-01 18:00:00', 120, 150, 'запланирован', 4),
('Белогорье — Динамо', 'belogorie-dinamo', 'волейбол', '2026-12-05 19:00:00', 130, 180, 'запланирован', 4);ыы