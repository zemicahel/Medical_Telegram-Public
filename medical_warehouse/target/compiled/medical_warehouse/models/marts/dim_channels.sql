SELECT
    MD5(channel_name) AS channel_key, -- Surrogate Key
    channel_name,
    MIN(message_date) AS first_post_date,
    MAX(message_date) AS last_post_date,
    COUNT(message_id) AS total_posts,
    AVG(view_count) AS avg_views
FROM "medical_db"."public"."stg_telegram_messages"
GROUP BY 1, 2