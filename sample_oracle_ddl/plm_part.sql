CREATE TABLE plm_part (
    part_id      VARCHAR2(50)  NOT NULL,
    cust_code    VARCHAR2(20)  NOT NULL,
    tech_code    VARCHAR2(30),
    part_desc    VARCHAR2(200),
    customer_id  VARCHAR2(20)  NOT NULL,
    cust_part_no VARCHAR2(50),
    status       VARCHAR2(10)  DEFAULT 'ACTIVE',
    crea_date    DATE          DEFAULT SYSDATE NOT NULL,
    updt_date    DATE          DEFAULT SYSDATE NOT NULL,
    CONSTRAINT pk_plm_part PRIMARY KEY (part_id)
);

COMMENT ON TABLE plm_part IS 'PLM Part/Product Master';
COMMENT ON COLUMN plm_part.part_id IS 'Part ID (Primary Key)';
COMMENT ON COLUMN plm_part.cust_code IS 'Customer Code';
COMMENT ON COLUMN plm_part.tech_code IS 'Technology/Process Code';
COMMENT ON COLUMN plm_part.part_desc IS 'Part Description/Specification';
COMMENT ON COLUMN plm_part.status IS 'Status (ACTIVE/INACTIVE/OBSOLETE)';
COMMENT ON COLUMN plm_part.crea_date IS 'Creation Date';
COMMENT ON COLUMN plm_part.updt_date IS 'Update Date';