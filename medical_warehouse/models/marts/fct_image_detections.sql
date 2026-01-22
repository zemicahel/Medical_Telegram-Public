WITH yolo_raw AS (
    SELECT 
        message_id::INT as message_id,
        channel as channel_name,
        image_category,
        detected_objects,
        -- Take the highest confidence score if available
        SPLIT_PART(confidence_scores, ',', 1)::FLOAT as confidence_score
    FROM {{ source('detection', 'yolo_results') }}
)

SELECT
    y.message_id,
    m.channel_key,
    m.date_key,
    y.image_category,
    y.detected_objects,
    y.confidence_score,
    m.view_count,
    m.forward_count
FROM yolo_raw y
JOIN {{ ref('fct_messages') }} m ON y.message_id = m.message_id