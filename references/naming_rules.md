# Column Naming Rules

## Core Principles

1. **Readability first**: Words with 6 or fewer characters are generally NOT abbreviated
2. **Positive-list rules are mandatory**: Any rule explicitly listed below MUST be applied without exception
3. **Segment-level application**: Apply rules to each underscore-separated word segment independently
4. **Suffix rules take priority**: Date/time suffix rules (_dt vs _date) are evaluated first

---

## Positive-List Rules (Mandatory)

These MUST always be applied:

📝 Exception Rule:
If the prefix or suffix attached to code consists of two characters or fewer (≤ 2 characters), do not abbreviate it to cd. It must remain unchanged (e.g., l_code remains l_code, and bp_code remains bp_code)

| Original Segment | Replacement | Notes |
|---|---|---|
| `code` | `cd` | e.g. `cust_code` → `cust_cd` |
| `change` | `chg` | e.g. `change_control` → `chg_control` |
| `account` | `acct` | e.g. `account_no` → `acct_no` |
| `busi` | `biz` | e.g. `busi_unit` → `biz_unit` |
| `quantity` | `qty` | e.g. `product_quantity` → `prod_qty` |
| `fact` | `fab` | e.g. `fact_code` → `fab_cd` |
| `quantity` | `qty` | e.g. `product_quantity` → `prod_qty` |
| `stat` | `status` | e.g. `stat_code` → `status_cd` |
| `serv` | `service` | e.g. `serv_flow` → `service_flow` |
| `stag` | `stage` | e.g. `serv_stag` → `service_stage` |
| `maintain` | `mtn` | e.g. `maintain_eng` → `mtn_user` |
| `product` | `prod` | e.g. `product_type` → `prod_type` |
| `customer` | `cust` | e.g. `customer_id` → `cust_id` |
| `proc` | `process` | expand abbreviation |
| `indu` | `industry` | expand abbreviation |
| `crea` | `create` | expand abbreviation |
| `remk` | `remark` | expand abbreviation |
| `updt` | `update` | expand abbreviation |
| `cnfm` | `confirm` | expand abbreviation |
| `cnfrm` | `confirm` | expand abbreviation |
| `rlse` | `release` | expand abbreviation |
| `mkt` | `market` | expand abbreviation |
| `eng` | `user` | engineer, replace with user |
| `function` | `func` | product_function → prod_func|
| `manufactor` | `mfg` | also covers `manufacturer` |
| `is_` prefix | remove `is_`, add `_flag` or `_type` suffix | see flag/type rule below |

---

## Date / Time Suffix Rules (Applied after column rename)

| Condition | Suffix | Example |
|---|---|---|
| Column holds **date + time** (timestamp) | `_dt` | `create_datetime` → `create_dt` |
| Column holds **date only** | `_date` | `birth_date` → stays `birth_date` |
| `crea_date` / `create_date` ambiguous → check Oracle type: if `DATE` or `TIMESTAMP` with time | `_dt` | `crea_date` → `create_dt` |
| Oracle type is `DATE` with name suffix `_date` and context is clearly date-only | `_date` | keep as-is |

**Detection heuristic for ambiguous Oracle `DATE` columns:**
- Name ends in `_dt`, `_datetime`, `_timestamp` → use `DateTime` + `_dt`
- Name ends in `_date`, `_day` → use `Date` + `_date`
- Name has no date suffix → default to `DateTime` + rename to `_dt`

---

## Flag / Boolean Rules

| Pattern | Rule | Example |
|---|---|---|
| `is_<something>` where value is boolean (Y/N, 0/1) | `<something>_flag` | `is_dummy_part` → `dummy_part_flag` |
| `is_<something>` where value is an enum/category | `<something>_type` | `is_active` (with values like ACTIVE/INACTIVE/PENDING) → `active_type` |

When ambiguous, prefer `_flag`. Note the assumption in the description.

---

## Common Abbreviation Table (Apply only when segment matches exactly)

These are applied only when a segment matches the exact word — NOT as substring matches within longer words.

| Original | Replacement | Rationale |
|---|---|---|
| `code` | `cd` | Mandatory (positive list) |
| `product` | `prod` | Mandatory (positive list) |
| `function` | `func` | Mandatory (positive list) |
| `manufactor` / `manufacturer` | `mfg` | Mandatory (positive list) |
| `indu` | `industry` | Mandatory (positive list) — expand not shrink |
| `description` | `desc` | Common, improves readability |
| `number` | `no` | Only when used as identifier suffix (e.g. `part_number` → `part_no`) |
| `quantity` | `qty` | Common in manufacturing/PLM |
| `amount` | `amt` | Finance/ERP convention |
| `transaction` | `txn` | Common in ERP |
| `organization` | `org` | Common |
| `department` | `dept` | Common |
| `sequence` | `seq` | Common |
| `version` | `ver` | When used as suffix |
| `status` | `sts` | ❌ DO NOT abbreviate — keep as `status` (6 chars, high readability) |
| `type` | `type` | ❌ DO NOT abbreviate |
| `name` | `name` | ❌ DO NOT abbreviate |
| `date` | `date` | ❌ DO NOT abbreviate (see suffix rules for `_dt`) |
| `time` | `time` | ❌ DO NOT abbreviate |
| `flag` | `flag` | ❌ DO NOT abbreviate |
| `id` | `id` | ❌ DO NOT abbreviate |
| `no` | `no` | ❌ DO NOT abbreviate further |

---

## Do-Not-Abbreviate List (Words ≤ 6 chars, high readability)

These words should never be abbreviated:
`type`, `name`, `date`, `time`, `flag`, `id`, `no`, `key`, `ref`, `code` (already mapped), `val`, `unit`, `class`, `group`, `level`, `order`, `rank`, `rate`, `ratio`, `src`, `tag`

---

## Examples

| Original Column | Segmented | Rule Applied | New Column |
|---|---|---|---|
| `CUST_CODE` | `cust` + `code` | code→cd | `cust_cd` |
| `IS_DUMMY_PART` | `is_dummy_part` | is_→flag | `dummy_part_flag` |
| `INDU_TYPE` | `indu` + `type` | indu→industry | `industry_type` |
| `PRODUCT_DESC` | `product` + `desc` | product→prod | `prod_desc` |
| `FUNC_NAME` | `func` + `name` | function→func (already func) | `func_name` |
| `MANUFACTOR_ID` | `manufactor` + `id` | manufactor→mfg | `mfg_id` |
| `SERV_FLOW_CD` | compound: `serv_flow` + `cd` | serv_flow→service_flow | `service_flow_cd` |
| `SERV_STAG_NO` | compound: `serv_stag` + `no` | serv_stag→service_stage | `service_stage_no` |
| `CREA_DATE` | `crea` + `date` | crea→create, date→dt (has time) | `create_dt` |
| `PART_NUMBER` | `part` + `number` | number→no | `part_no` |
| `TXN_AMOUNT` | `txn` + `amount` | amount→amt | `txn_amt` |
| `DEPT_CODE` | `dept` + `code` | code→cd | `dept_cd` |