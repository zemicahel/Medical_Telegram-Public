
  
    

  create  table "medical_db"."public"."fct_messages__dbt_tmp"
  
  
    as
  
  (
    SELECT
    m.message_id,
    MD5(m.channel_name) AS channel_key,
    TO_CHAR(m.message_date, 'YYYYMMDD')::INT AS date_key,
    m.message_text,
    m.message_length,
    m.view_count,
    m.forward_count,
    m.has_image
FROM "medical_db"."public"."stg_telegram_messages" m
  );
  