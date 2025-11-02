SELECT COUNT(*) 
FROM (
    SELECT i.item_id
    FROM item i
    JOIN item_categories c ON i.item_id = c.item_id
    GROUP BY i.item_id
    HAVING COUNT(c.category) = 4
) AS sub;