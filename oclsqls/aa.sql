SELECT sequence_name
FROM user_sequences s
WHERE NOT EXISTS (
    SELECT 1 
    FROM user_dependencies d
    WHERE d.referenced_type = 'SEQUENCE'
    AND d.referenced_name = s.sequence_name
);


SELECT sequence_name
FROM all_sequences s
WHERE s.sequence_owner = USER
AND NOT EXISTS (
    -- 检查依赖关系
    SELECT 1 FROM all_dependencies d
    WHERE d.referenced_type = 'SEQUENCE'
    AND d.referenced_name = s.sequence_name
)
AND NOT EXISTS (
    -- 检查列默认值
    SELECT 1 FROM all_tab_columns
    WHERE (data_default LIKE '%'||s.sequence_name||'.NEXTVAL%'
    OR data_default LIKE '%'||s.sequence_name||'.CURRVAL%')
)
AND NOT EXISTS (
    -- 检查源代码
    SELECT 1 FROM all_source
    WHERE (upper(text) LIKE '%'||s.sequence_name||'.NEXTVAL%'
    OR upper(text) LIKE '%'||s.sequence_name||'.CURRVAL%')
);
