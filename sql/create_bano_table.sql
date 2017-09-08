-- Table: neogeo.bano_p

-- DROP TABLE neogeo.bano_p;

CREATE TABLE neogeo.bano_p
(
  id character varying(254),
  nom_voie character varying(254),
  id_fantoir character varying(254),
  numero integer,
  rep character varying(254),
  code_insee  character varying(6),
  code_post  character varying(6),
  alias character varying(254),
  nom_ld character varying(254),
  x double precision,
  y double precision,
  commune character varying(254),
  fant_voie character varying(254),
  fant_ld character varying(254),
  lat double precision,
  lon double precision,
  geometrie geometry(Point,27572),
  CONSTRAINT bano_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE neogeo.bano_p
  OWNER TO gis_admin;

-- Index: neogeo.sidx_bano_the_geom

-- DROP INDEX neogeo.sidx_bano_the_geom;

CREATE INDEX sidx_bano_the_geom
  ON neogeo.bano_p
  USING gist
  (geometrie);