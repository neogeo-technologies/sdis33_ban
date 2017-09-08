DELETE FROM neogeo.rerouprima_l;
DELETE FROM neogeo.rerousecon_l;
DELETE FROM neogeo.rerouterti_l;
DELETE FROM neogeo.rerouquate_l;
DELETE FROM neogeo.rerouauacc_l;
DELETE FROM neogeo.rerouvonoc_l;

INSERT INTO neogeo.rerouprima_l
SELECT *
FROM gces.rerouprima_l
WHERE commune_insee IN ('33316','33424','33241','33149','33154','33245','33268','33553','33072','33359','33296','33341','33060','33250','33374','33027','33395','33054','33132');

INSERT INTO neogeo.rerousecon_l
SELECT *
FROM gces.rerousecon_l
WHERE commune_insee IN ('33316','33424','33241','33149','33154','33245','33268','33553','33072','33359','33296','33341','33060','33250','33374','33027','33395','33054','33132');

INSERT INTO neogeo.rerouterti_l
SELECT *
FROM gces.rerouterti_l
WHERE commune_insee IN ('33316','33424','33241','33149','33154','33245','33268','33553','33072','33359','33296','33341','33060','33250','33374','33027','33395','33054','33132');

INSERT INTO neogeo.rerouquate_l
SELECT *
FROM gces.rerouquate_l
WHERE commune_insee IN ('33316','33424','33241','33149','33154','33245','33268','33553','33072','33359','33296','33341','33060','33250','33374','33027','33395','33054','33132');

INSERT INTO neogeo.rerouauacc_l
SELECT *
FROM gces.rerouauacc_l
WHERE commune_insee IN ('33316','33424','33241','33149','33154','33245','33268','33553','33072','33359','33296','33341','33060','33250','33374','33027','33395','33054','33132');

INSERT INTO neogeo.rerouvonoc_l
SELECT *
FROM gces.rerouvonoc_l
WHERE commune_insee IN ('33316','33424','33241','33149','33154','33245','33268','33553','33072','33359','33296','33341','33060','33250','33374','33027','33395','33054','33132');