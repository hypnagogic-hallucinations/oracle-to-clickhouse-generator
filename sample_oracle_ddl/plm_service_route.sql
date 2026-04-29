CREATE TABLE plm_service_route (
    route_id     VARCHAR2(50)  NOT NULL,
    part_id      VARCHAR2(50)  NOT NULL,
    fact_code    VARCHAR2(20)  NOT NULL,
    serv_flow    VARCHAR2(50)  NOT NULL,
    serv_stag    VARCHAR2(20)  NOT NULL,
    seq_num      NUMBER(3)     NOT NULL,
    crea_date    DATE          DEFAULT SYSDATE NOT NULL,
    CONSTRAINT pk_plm_serv_route PRIMARY KEY (route_id),
    CONSTRAINT fk_route_part FOREIGN KEY (part_id) REFERENCES plm_part (part_id)
);

COMMENT ON TABLE plm_service_route IS 'PLM Service/Production Route Configuration';
COMMENT ON COLUMN plm_service_route.route_id IS 'Route ID (Primary Key)';
COMMENT ON COLUMN plm_service_route.part_id IS 'Associated Part ID (Foreign Key)';
COMMENT ON COLUMN plm_service_route.fact_code IS 'Factory Code';
COMMENT ON COLUMN plm_service_route.serv_flow IS 'Service/Production Flow Name';
COMMENT ON COLUMN plm_service_route.serv_stag IS 'Service/Production Stage';
COMMENT ON COLUMN plm_service_route.seq_num IS 'Stage Sequence Number';
COMMENT ON COLUMN plm_service_route.crea_date IS 'Creation Date';