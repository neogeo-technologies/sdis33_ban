DELETE FROM neogeo.rerouprima_l;
DELETE FROM neogeo.rerousecon_l;
DELETE FROM neogeo.rerouterti_l;
DELETE FROM neogeo.rerouquate_l;
DELETE FROM neogeo.rerouauacc_l;
DELETE FROM neogeo.rerouvonoc_l;

INSERT INTO neogeo.rerouprima_l
SELECT *
FROM gces.rerouprima_l;

INSERT INTO neogeo.rerousecon_l
SELECT *
FROM gces.rerousecon_l;

INSERT INTO neogeo.rerouterti_l
SELECT *
FROM gces.rerouterti_l;

INSERT INTO neogeo.rerouquate_l
SELECT *
FROM gces.rerouquate_l;

INSERT INTO neogeo.rerouauacc_l
SELECT *
FROM gces.rerouauacc_l;

INSERT INTO neogeo.rerouvonoc_l
SELECT *
FROM gces.rerouvonoc_l;