# Column Mapping: plm_part → plm_part (ClickHouse)

## Select SQL

```sql
SELECT
    part_id        AS part_id,
    cust_code      AS cust_cd,
    tech_code      AS tech_cd,
    part_desc      AS part_desc,
    customer_id    AS cust_id,
    cust_part_no   AS cust_part_no,
    status         AS status,
    crea_date      AS create_dt,
    updt_date      AS update_dt
FROM plm_part
```

## Column Name Mapping Table

| Original Oracle Column | New ClickHouse Column | Change? |
|---|---|---|
| part_id | part_id | — |
| cust_code | cust_cd | ✅ |
| tech_code | tech_cd | ✅ |
| part_desc | part_desc | — |
| customer_id | cust_id | ✅ |
| cust_part_no | cust_part_no | — |
| status | status | — |
| crea_date | create_dt | ✅ |
| updt_date | update_dt | ✅ |

## Type Mapping Reference Table

| Original Oracle Column | New ClickHouse Column | Oracle Type | ClickHouse Type | Nullable | New Column Desc |
|---|---|---|---|---|---|
| part_id | part_id | VARCHAR2(50) NOT NULL | String | No | [Definition] Unique identifier for a part or product master record in the PLM system. Serves as the primary key for all part-related data entities. [Reference] Referenced by PLM_MTN_LOG.PART_ID and PLM_SERVICE_ROUTE.PART_ID. [Sample Data] e.g. 'P-2024-001', 'A-IC-99923' |
| cust_code | cust_cd | VARCHAR2(20) NOT NULL | String | No | [Definition] Code identifying the customer associated with this part. Used to link the part master to customer-specific configurations. [Reference] References CUSTOMER_MASTER.CUST_CODE. [Sample Data] e.g. 'TSMC01', 'NVDA02' |
| tech_code | tech_cd | VARCHAR2(30) | Nullable(String) | Yes | [Definition] Technology or process node code assigned to this part, indicating the manufacturing process generation or technology family. [Reference] References TECHNOLOGY_MASTER.TECH_CODE. [Sample Data] e.g. 'N5', 'N3E', 'N7P' |
| part_desc | part_desc | VARCHAR2(200) | Nullable(String) | Yes | [Definition] Free-text description or specification summary for the part, covering design intent, functional purpose, or material specification. [Sample Data] e.g. '5nm Logic Die - High Performance', 'Package Substrate Rev B' |
| customer_id | cust_id | VARCHAR2(20) NOT NULL | String | No | [Definition] Foreign identifier of the owning customer entity, used to enforce customer-level data isolation and access control. [Reference] References CUSTOMER.CUSTOMER_ID. [Sample Data] e.g. 'CUST-001', 'CUST-042' |
| cust_part_no | cust_part_no | VARCHAR2(50) | Nullable(String) | Yes | [Definition] Customer-assigned part number used by the customer's own internal systems. Enables cross-reference between customer BOM and PLM part master. [Sample Data] e.g. 'CPN-A-00123', 'NVDA-X-99021' |
| status | status | VARCHAR2(10) | Nullable(String) | Yes | [Definition] Lifecycle status of the part, indicating its current state in the PLM workflow. Allowable values: ACTIVE, INACTIVE, OBSOLETE. [Sample Data] e.g. 'ACTIVE', 'OBSOLETE' |
| crea_date | create_dt | DATE NOT NULL | DateTime | No | [Definition] Timestamp recording when this part master record was first created in the system. [Sample Data] e.g. 2024-01-15 08:30:00 |
| updt_date | update_dt | DATE NOT NULL | DateTime | No | [Definition] Timestamp recording the most recent update to this part master record. Automatically updated on any field change. [Sample Data] e.g. 2024-11-20 14:05:33 |
