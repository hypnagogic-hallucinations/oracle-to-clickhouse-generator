# Column Mapping: plm_service_route → plm_service_route (ClickHouse)

## Select SQL

```sql
SELECT
    route_id     AS route_id,
    part_id      AS part_id,
    fact_code    AS fab_cd,
    serv_flow    AS service_flow,
    serv_stag    AS service_stage,
    seq_num      AS seq_no,
    crea_date    AS create_dt
FROM plm_service_route
```

## Column Name Mapping Table

| Original Oracle Column | New ClickHouse Column | Change? |
|---|---|---|
| route_id | route_id | — |
| part_id | part_id | — |
| fact_code | fab_cd | ✅ |
| serv_flow | service_flow | ✅ |
| serv_stag | service_stage | ✅ |
| seq_num | seq_no | ✅ |
| crea_date | create_dt | ✅ |

## Type Mapping Reference Table

| Original Oracle Column | New ClickHouse Column | Oracle Type | ClickHouse Type | Nullable | New Column Desc |
|---|---|---|---|---|---|
| route_id | route_id | VARCHAR2(50) NOT NULL | String | No | [Definition] Unique identifier for a service or production route configuration record. Serves as the primary key of the route table. [Sample Data] e.g. 'RT-2024-001', 'SR-N5-0042' |
| part_id | part_id | VARCHAR2(50) NOT NULL | String | No | [Definition] Foreign key referencing the part master record that this service route is configured for. [Reference] References PLM_PART.PART_ID. [Sample Data] e.g. 'P-2024-001' |
| fact_code | fab_cd | VARCHAR2(20) NOT NULL | String | No | [Definition] Code identifying the fabrication facility (fab) where this service route operation is executed. [Reference] References FACTORY_MASTER.FACT_CODE. [Sample Data] e.g. 'FAB12', 'FAB18A' |
| serv_flow | service_flow | VARCHAR2(50) NOT NULL | String | No | [Definition] Name of the service or production flow that this route belongs to, defining the high-level process sequence for the associated part. [Sample Data] e.g. 'LOGIC_N5_FLOW', 'BACKEND_ASSY' |
| serv_stag | service_stage | VARCHAR2(20) NOT NULL | String | No | [Definition] Specific stage within the service flow at which this route step is performed, enabling granular process step traceability. [Sample Data] e.g. 'ETCH', 'CMP', 'FINAL_TEST' |
| seq_num | seq_no | NUMBER(3) NOT NULL | Int16 | No | [Definition] Integer sequence number defining the execution order of this route stage within its service flow. Lower numbers execute first. [Sample Data] e.g. 1, 2, 10 |
| crea_date | create_dt | DATE NOT NULL | DateTime | No | [Definition] Timestamp recording when this service route configuration record was first created. [Sample Data] e.g. 2024-02-01 10:00:00 |
