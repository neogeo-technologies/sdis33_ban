DELETE FROM neogeo.ban_p;

COPY neogeo.ban_p (id,nom_voie,id_fantoir,numero,rep,code_insee,code_post,alias,nom_ld,nom_afnor,libelle_ac,x,y,lon,lat,nom_commun)
    FROM '/Users/benji/dev/projects_current/sdis33/2017_outils_prod/data/ban/BAN_licence_gratuite_repartage_33.csv' DELIMITER ';' CSV HEADER;

UPDATE neogeo.ban_p
    SET rep = NULL
    WHERE rep = '';

UPDATE neogeo.ban_p
    SET alias = NULL
    WHERE alias = '';

UPDATE neogeo.ban_p
    SET nom_ld = NULL
    WHERE nom_ld = '';

UPDATE neogeo.ban_p
    SET geometrie = ST_Transform(ST_SetSRID(ST_Point(x, y), 2154), 27572);
