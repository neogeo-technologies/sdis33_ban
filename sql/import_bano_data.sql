DELETE FROM neogeo.bano_p;

COPY neogeo.bano_p (id,nom_voie,id_fantoir,numero,rep,code_insee,code_post,alias,nom_ld,x,y,commune,fant_voie,fant_ld,lat,lon)
    FROM '/Users/benji/dev/projects_current/sdis33/2017_outils_prod/data/bano/BAN_odbl_33-csv' DELIMITER ',' CSV HEADER;

UPDATE neogeo.bano_p
    SET rep = NULL
    WHERE rep = '';

UPDATE neogeo.bano_p
    SET alias = NULL
    WHERE alias = '';

UPDATE neogeo.bano_p
    SET nom_ld = NULL
    WHERE nom_ld = '';

UPDATE neogeo.bano_p
    SET geometrie = ST_Transform(ST_SetSRID(ST_Point(x, y), 2154), 27572);
