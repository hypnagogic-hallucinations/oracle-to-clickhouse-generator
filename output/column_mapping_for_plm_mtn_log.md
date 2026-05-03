# Column Mapping: plm_mtn_log → plm_mtn_log (ClickHouse)

## Select SQL

```sql
SELECT
    log_id       AS log_id,
    part_id      AS part_id,
    mtn_eng      AS mtn_user,
    action_type  AS action_type,
    log_desc     AS log_desc,
    crea_date    AS create_dt
FROM plm_mtn_log
```

## Column Name Mapping Table

| Original Oracle Column | New ClickHouse Column | Change? |
|---|---|---|
| log_id | log_id | — |
| part_id | part_id | — |
| mtn_eng | mtn_user | ✅ |
| action_type | action_type | — |
| log_desc | log_desc | — |
| crea_date | create_dt | ✅ |

## Type Mapping Reference Table

| Original Oracle Column | New ClickHouse Column | Oracle Type | ClickHouse Type | Nullable | New Column Desc |
|---|---|---|---|---|---|
| log_id | log_id | VARCHAR2(50) NOT NULL | String | No | [Definition] Unique identifier for each maintenance log entry, serving as the primary key of the maintenance change log. [Sample Data] e.g. 'LOG-2024-00001', 'MTN-0099234' |
| part_id | part_id | VARCHAR2(50) NOT NULL | String | No | [Definition] Foreign key referencing the part master record that this maintenance log entry is associated with. [Reference] References PLM_PART.PART_ID. [Sample Data] e.g. 'P-2024-001' |
| mtn_eng | mtn_user | VARCHAR2(50) NOT NULL | String | No | [Definition] Employee code or login ID of the maintenance engineer responsible for performing or logging the maintenance action. [Reference] References EMPLOYEE_MASTER.EMP_CODE. [Sample Data] e.g. 'ENG001', 'JOHN.SMITH' |
| action_type | action_type | VARCHAR2(30) NOT NULL | String | No | [Definition] Categorizes the type of maintenance action performed on the associated part. Allowable values: REPAIR, UPDATE, INSPECT. [Sample Data] e.g. 'REPAIR', 'INSPECT' |
| log_desc | log_desc | VARCHAR2(500) | Nullable(String) | Yes | [Definition] Free-text narrative describing the maintenance work performed, findings, or corrective actions taken during the maintenance event. [Sample Data] e.g. 'Replaced damaged substrate layer; re-tested OK' |
| crea_date | create_dt | DATE NOT NULL | DateTime | No | [Definition] Timestamp recording when this maintenance log entry was created in the system. [Sample Data] e.g. 2024-03-10 09:15:42 |
