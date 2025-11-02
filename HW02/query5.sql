SELECT COUNT(DISTINCT user_id) AS high_rating_sellers
FROM USERS
WHERE rating > 1000
  AND user_id IN (SELECT DISTINCT seller_id FROM ITEM);