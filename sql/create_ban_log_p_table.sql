-- Sequence: neogeo.ban_log_p_id_seq

-- DROP SEQUENCE neogeo.ban_log_p_id_seq;

CREATE SEQUENCE neogeo.ban_log_p_id_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 728967
  CACHE 1;
ALTER TABLE neogeo.ban_log_p_id_seq
  OWNER TO gis_admin;

-- Table: neogeo.ban_log_p

-- DROP TABLE neogeo.ban_log_p;

CREATE TABLE neogeo.ban_log_p
(
  id integer NOT NULL DEFAULT nextval('neogeo.ban_log_p_id_seq'::regclass),
  message_date date,
  code_insee character varying(6),
  message character varying(512),
  code_erreur smallint,
  geometrie geometry(Point,27572),
  CONSTRAINT ban_log_p_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE neogeo.ban_log_p
  OWNER TO gis_admin;

-- Index: neogeo.sidx_ban_log_geom

-- DROP INDEX neogeo.sidx_ban_log_geom;

CREATE INDEX sidx_ban_log_p_geom
  ON neogeo.ban_log_p
  USING gist
  (geometrie);
