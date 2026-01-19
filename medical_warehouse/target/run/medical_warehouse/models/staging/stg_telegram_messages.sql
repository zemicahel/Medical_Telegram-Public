
  create view "medical_db"."public"."stg_telegram_messages__dbt_tmp"
    
    
  as (
    WITH raw_data AS (
    SELECT * FROM "medical_db"."raw"."telegram_messages"
)

SELECT
    message_id::INT AS message_id,
    channel AS channel_name,
    date::TIMESTAMP AS message_date,
    text AS message_text,
    COALESCE(views, 0) AS view_count,
    COALESCE(forwards, 0) AS forward_count,
    CASE 
        WHEN image_path IS NOT NULL THEN TRUE 
        ELSE FALSE 
    END AS has_image,
    LENGTH(text) AS message_length
FROM raw_data
WHERE message_id IS NOT NULL 
  AND text IS NOT NULL
  );