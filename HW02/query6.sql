SELECT COUNT(DISTINCT u.user_id) AS sellers_and_bidders
FROM USERS u
WHERE u.user_id IN (SELECT seller_id FROM ITEM)
  AND u.user_id IN (SELECT user_id FROM BIDS);