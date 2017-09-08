# -*- coding: utf-8 -*-

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "sdis33"
DB_USER = "utilisateur"
DB_PWD = "mot_de_passe"

DB_SCHEMA = "neogeo"
DB_ROAD_TABLE_PRIMA = "rerouprima_l"
DB_ROAD_TABLE_SECON = "rerousecon_l"
DB_ROAD_TABLE_TERTI = "rerouterti_l"
DB_ROAD_TABLE_QUATE = "rerouquate_l"
DB_ROAD_TABLE_AUACC = "rerouauacc_l"
DB_ROAD_TABLE_VONOC = "rerouvonoc_l"
DB_ROAD_TABLES = (DB_ROAD_TABLE_PRIMA, DB_ROAD_TABLE_SECON, DB_ROAD_TABLE_TERTI,
                  DB_ROAD_TABLE_QUATE, DB_ROAD_TABLE_AUACC, DB_ROAD_TABLE_VONOC)

DB_SDIS_ROAD_GEOM = "geometrie"
DB_SDIS_ROAD_NAME = "nom_origine"
DB_SDIS_ROAD_INSEE = "commune_insee"
DB_SDIS_ROAD_RIVOLI = "rivoli"
DB_SDIS_ROAD_RIVOLI_DIST = "rivoli_dist"

DB_FANTOIR_TABLE = "fantoir"
DB_BAN_TABLE = "ban_p"
DB_BANO_TABLE = "bano_p"

DB_BAN_GEOM = "geometrie"
DB_BAN_RIVOLI = "id_fantoir"
DB_BAN_INSEE = "code_insee"
DB_BAN_NAME = "nom_voie"

BAN_INSEE_COL = "code_insee"

MAX_DIST = 300