-- Sequence: neogeo.fantoir_id_seq

-- DROP SEQUENCE neogeo.fantoir_id_seq;

CREATE SEQUENCE neogeo.fantoir_id_seq
  INCREMENT 1
  MINVALUE 1
  MAXVALUE 9223372036854775807
  START 728967
  CACHE 1;
ALTER TABLE neogeo.fantoir_id_seq
  OWNER TO gis_admin;

-- Table: neogeo.fantoir

-- DROP TABLE neogeo.fantoir;

CREATE TABLE neogeo.fantoir
(
  id integer NOT NULL DEFAULT nextval('neogeo.fantoir_id_seq'::regclass),
  rivo character varying(11),
  dept character varying(3),
  comm character varying(3),
  insee character varying(6),
  way character varying(4),
  natu character varying(4),
  name character varying(26),
  type char(1),
  priv char(1),
  cat_code char(1),
  cat character varying(19),
  comp_name character varying(254),
  CONSTRAINT fantoir_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE neogeo.fantoir
  OWNER TO gis_admin;
