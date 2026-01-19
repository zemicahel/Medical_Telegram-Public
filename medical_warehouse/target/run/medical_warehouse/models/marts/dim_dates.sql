
  
    

  create  table "medical_db"."public"."dim_dates__dbt_tmp"
  
  
    as
  
  (
    SELECT
    TO_CHAR(datum, 'YYYYMMDD')::INT AS date_key,
    datum AS full_date,
    EXTRACT(DOW FROM datum) AS day_of_week,
    TO_CHAR(datum, 'Day') AS day_name,
    EXTRACT(WEEK FROM datum) AS week_of_year,
    EXTRACT(MONTH FROM datum) AS month,
    TO_CHAR(datum, 'Month') AS month_name,
    EXTRACT(YEAR FROM datum) AS year,
    CASE WHEN EXTRACT(ISODOW FROM datum) IN (6, 7) THEN TRUE ELSE FALSE END AS is_weekend
FROM (
    SELECT generate_series('2020-01-01'::DATE, '2025-12-31'::DATE, '1 day'::INTERVAL)::DATE AS datum
) t
  );
  