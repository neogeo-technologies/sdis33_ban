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

DB_SDIS_ROAD_ID = "fk_sdis33_prevision"
DB_SDIS_ROAD_GEOM = "geometrie"
DB_SDIS_ROAD_NAMES = ["nom_origine", "nom_2", "nom_3", "nom_4"]
DB_SDIS_ROAD_INSEE = "commune_insee"
DB_SDIS_ROAD_RIVOLI = "rivoli"
DB_SDIS_ROAD_RIVOLI_DIST = "rivoli_dist"
DB_SDIS_ROAD_SRC_RIVOLI = "src_rivoli"
DB_SDIS_ROAD_NUM_DEB_GAU = "num_deb_gau"
DB_SDIS_ROAD_NUM_DEB_DRO = "num_deb_dro"
DB_SDIS_ROAD_NUM_FIN_GAU = "num_fin_gau"
DB_SDIS_ROAD_NUM_FIN_DRO = "num_fin_dro"
DB_SDIS_ROAD_SRC_NUM = "src_num"
DB_SDIS_ROAD_COTE_IMPAIR = "cote_impair"

DB_SDIS_ROAD_SRC_NUM_NEOGEO_VALUE = "a"
DB_SDIS_ROAD_SRC_RIVOLI_NEOGEO_VALUE = "a"

DB_FANTOIR_TABLE = "fantoir"
DB_BAN_TABLE = "ban_p"
DB_BANO_TABLE = "bano_p"

DB_BAN_ID = "id"
DB_BAN_GEOM = "geometrie"
DB_BAN_RIVOLI = "id_fantoir"
DB_BAN_INSEE = "code_insee"
DB_BAN_NAME = "nom_voie"
DB_BAN_NUM = "numero"
DB_BAN_REP = "rep"

DB_FANTOIR_INSEE = "insee"
DB_FANTOIR_RIVOLI = "rivo"
DB_FANTOIR_WAY = "way"
DB_FANTOIR_NATURE = "natu"
DB_FANTOIR_TYPE = "type"
DB_FANTOIR_NAME = "name"
DB_FANTOIR_COMP_NAME = "comp_name"

DB_BAN_LOG_P_TABLE = "ban_log_p"
DB_BAN_LOG_L_TABLE = "ban_log_l"
DB_BAN_LOG_DATE = "message_date"
DB_BAN_LOG_INSEE = "code_insee"
DB_BAN_LOG_MESSAGE = "message"
DB_BAN_LOG_ERROR = "code_erreur"
DB_BAN_LOG_GEOM = "geometrie"

FANTOIR_USED_WAY_TYPES = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X', 'Y', 'Z')

MAX_DIST_WITH_NAME = 300
MAX_DIST_WITH_NO_NAME = 10
DROITE_GAUCHE_DIST = 2
LEVEN_DIST_MAX = 7