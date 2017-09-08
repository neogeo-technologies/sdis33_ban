-- Table: neogeo.ban_p

-- DROP TABLE neogeo.ban_p;

CREATE TABLE neogeo.ban_p
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
  nom_afnor character varying(254),
  libelle_ac character varying(254),
  x double precision,
  y double precision,
  lon double precision,
  lat double precision,
  nom_commun character varying(254),
  geometrie geometry(Point,27572),
  CONSTRAINT ban_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE neogeo.ban_p
  OWNER TO gis_admin;

-- Index: neogeo.sidx_ban_the_geom

-- DROP INDEX neogeo.sidx_ban_the_geom;

CREATE INDEX sidx_ban_the_geom
  ON neogeo.ban_p
  USING gist
  (geometrie);
