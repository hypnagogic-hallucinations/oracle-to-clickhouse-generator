CREATE TABLE plm_mtn_log (
    log_id       VARCHAR2(50)  NOT NULL,
    part_id      VARCHAR2(50)  NOT NULL,
    mtn_eng      VARCHAR2(50)  NOT NULL,
    action_type  VARCHAR2(30)  NOT NULL,
    log_desc     VARCHAR2(500),
    crea_date    DATE          DEFAULT SYSDATE NOT NULL,
    CONSTRAINT pk_plm_mtn_log PRIMARY KEY (log_id),
    CONSTRAINT fk_log_part FOREIGN KEY (part_id) REFERENCES plm_part (part_id)
);

COMMENT ON TABLE plm_mtn_log IS 'PLM Engineering Maintenance and Change Log';
COMMENT ON COLUMN plm_mtn_log.log_id IS 'Log ID (Primary Key)';
COMMENT ON COLUMN plm_mtn_log.part_id IS 'Associated Part ID (Foreign Key)';
COMMENT ON COLUMN plm_mtn_log.mtn_eng IS 'Maintenance/Responsible Engineer Code';
COMMENT ON COLUMN plm_mtn_log.action_type IS 'Action Type (REPAIR/UPDATE/INSPECT)';
COMMENT ON COLUMN plm_mtn_log.log_desc IS 'Detailed Maintenance Description';
COMMENT ON COLUMN plm_mtn_log.crea_date IS 'Creation Date';