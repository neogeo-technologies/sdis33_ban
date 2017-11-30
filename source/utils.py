# -*- coding: utf-8 -*-


import psycopg2
import psycopg2.extras
from datetime import datetime

import shapely.wkt

import param


def build_db_connect_string():
    db_conn_str = ""
    db_conn_str += "host='{}' ".format(param.DB_HOST)
    db_conn_str += "port={} ".format(param.DB_PORT)
    db_conn_str += "dbname='{}' ".format(param.DB_NAME)
    db_conn_str += "user='{}' ".format(param.DB_USER)
    db_conn_str += "password='{}' ".format(param.DB_PWD)
    db_conn_str += ' connect_timeout=10'

    return db_conn_str


def get_all_city_insee(db_connection):

    insee_codes = set()

    # Boucle sur les tables du réseau routier
    for table_name in param.DB_ROAD_TABLES:

        # Boucle sur les codes insee présents dans la base sdis
        sql = u"""
            SELECT distinct({0})
                FROM {1}.{2}
                ORDER BY {0} ASC;
        """.format(param.DB_SDIS_ROAD_INSEE, param.DB_SCHEMA, table_name)
        with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            records = cur.fetchall()

            for r in records:
                insee_codes.add(r[param.DB_SDIS_ROAD_INSEE])

    return list(insee_codes)


def get_ban_way_dict_for_city(db_connection, insee, ban_table_name, max_nb_roads=None):
    ban_way_dict = {}

    sql = u"""
        SELECT
          {0},
          {2}
        FROM {3}.{4}
        WHERE {1} = '{5}'
            AND substring({0}, 1, 1) IN ({6})
            AND {0} IS NOT NULL AND {2} IS NOT NULL
        GROUP BY {0}, {2}
        ORDER BY {0}
         """.format(param.DB_BAN_RIVOLI, param.DB_BAN_INSEE, param.DB_BAN_NAME,
                    param.DB_SCHEMA, ban_table_name, insee,
                    ",".join(["'{}'".format(t) for t in param.FANTOIR_USED_WAY_TYPES]))

    if max_nb_roads is not None:
        sql += u"""LIMIT {0};
            """.format(max_nb_roads)

    sql += u";"

    # print(sql)

    with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql)
        records = cur.fetchall()

        for r in records:
            id_fantoir = r[param.DB_BAN_RIVOLI]
            ban_way_name = r[param.DB_BAN_NAME]
            if ban_way_name:
                ban_way_name = ban_way_name.decode("utf-8")

            ban_way_dict[id_fantoir] = ban_way_name

    return ban_way_dict


def get_way_names_from_rivoli_code_from_ban(db_connection, ban_table_name, insee, rivoli):
    way_names = set()

    sql = u"""
        SELECT distinct({0})
            FROM {1}.{2}
            WHERE {3} = '{4}' AND {5} = '{6}'
            ORDER BY {0} ASC;
    """.format(param.DB_BAN_NAME,
               param.DB_SCHEMA,
               ban_table_name,
               param.DB_BAN_INSEE,
               insee,
               param.DB_BAN_RIVOLI,
               rivoli)
    with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql)
        records = cur.fetchall()

        for r in records:
            if r[0]:
                way_names.add(r[0])

    result_list = list(way_names)
    result_list.sort()
    return result_list


def get_known_rivoli_codes_for_city(db_connection, insee):

    rivoli_codes = set()

    # Boucle sur les tables du réseau routier
    for table_name in param.DB_ROAD_TABLES:

        # Boucle sur les codes Rivoli présents sur les tronçons de la base SDIS
        sql = u"""
            SELECT distinct({0})
                FROM {1}.{2}
                WHERE {3} = '{4}'
                ORDER BY {0} ASC;
        """.format(param.DB_SDIS_ROAD_RIVOLI,
                   param.DB_SCHEMA,
                   table_name,
                   param.DB_SDIS_ROAD_INSEE,
                   insee)
        with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            records = cur.fetchall()

            for r in records:
                # On ne retient que les enregistrements qui ne contiennent qu'une seule valeur du code Rivoli
                # Les valeurs sont séparées par des virgules. On cherche donc l'absence de virgule.
                if len(r) == 1 and r[0] is not None and "," not in r[0]:
                    rivoli_codes.add(r[0])

    result_list = list(rivoli_codes)
    result_list.sort()
    return result_list


def get_rivoli_codes_for_city_from_ban(db_connection, insee, ban_table_name, only_used_fantoir_way_types=False):

    rivoli_codes = set()

    sql = u""

    if only_used_fantoir_way_types:
        sql = u"""
            SELECT DISTINCT({0})
                FROM {1}.{2}
                WHERE {3} = '{4}'
                    AND substring({0}, 1, 1) IN ({5})
                ORDER BY {0} ASC, {1} ASC;
        """.format(param.DB_BAN_RIVOLI,
                   param.DB_SCHEMA,
                   ban_table_name,
                   param.DB_BAN_INSEE,
                   insee,
                   ",".join(["'{}'".format(t) for t in param.FANTOIR_USED_WAY_TYPES]))
    else:
        sql = u"""
            SELECT DISTINCT ({0})
                FROM {1}.{2}
                WHERE {3} = '{4}'
                ORDER BY {0} ASC;
        """.format(param.DB_BAN_RIVOLI,
                   param.DB_SCHEMA,
                   ban_table_name,
                   param.DB_BAN_INSEE,
                   insee)

    with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql)
        records = cur.fetchall()

        for r in records:
            if len(r) == 1 and r[0] is not None:
                rivoli_codes.add(r[0])

    result_list = list(rivoli_codes)
    result_list.sort()
    return result_list


def get_rivoli_codes_and_way_names_for_city_from_ban(
        db_connection, insee, ban_table_name, only_used_fantoir_way_types=False):

    results = {}

    sql = u""

    if only_used_fantoir_way_types:
        sql = u"""
            SELECT DISTINCT ON ({0}) {0}, {1}
                FROM {2}.{3}
                WHERE {4} = '{5}'
                    AND substring({0}, 1, 1) IN ({6})
                ORDER BY {0} ASC, {1} ASC;
        """.format(param.DB_BAN_RIVOLI,
                   param.DB_BAN_NAME,
                   param.DB_SCHEMA,
                   ban_table_name,
                   param.DB_BAN_INSEE,
                   insee,
                   ",".join(["'{}'".format(t) for t in param.FANTOIR_USED_WAY_TYPES]))
    else:
        sql = u"""
            SELECT DISTINCT ON ({0}) {0}, {1}
                FROM {2}.{3}
                WHERE {4} = '{5}'
                ORDER BY {0} ASC, {1} ASC;
        """.format(param.DB_BAN_RIVOLI,
                   param.DB_BAN_NAME,
                   param.DB_SCHEMA,
                   ban_table_name,
                   param.DB_BAN_INSEE,
                   insee)

    with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql)
        records = cur.fetchall()

        for r in records:
            if r[0] is not None:
                results[r[0]] = r[1].decode("utf-8")

    return results


def get_all_adp_for_way(db_connection, insee, ban_table_name, rivoli):
    records = None

    addr_points = []

    sql = u"""
        SELECT {0},
               {1},
               {2},
               {3},
               {4},
               {5},
               ST_AsText({6}) AS geom
          FROM {7}.{8}
         WHERE {2} = '{9}' AND
               {3} = '{10}';
        """.format(param.DB_BAN_ID,
                   param.DB_BAN_NAME,
                   param.DB_BAN_RIVOLI,
                   param.DB_BAN_INSEE,
                   param.DB_BAN_NUM,
                   param.DB_BAN_REP,
                   param.DB_BAN_GEOM,
                   param.DB_SCHEMA,
                   ban_table_name,
                   rivoli,
                   insee)

    if db_connection is None:
        print("Absence de connexion")
        return

    with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql)
        records = cur.fetchall()

        col_names = [desc[0] for desc in cur.description]

        for r in records:
            adp = {col_name: r[col_name] for col_name in col_names}
            adp["shapely_geom"] = shapely.wkt.loads(adp["geom"])
            # num_comp = composant du numéro d'adresse ["1", "BIS"] pour le num_rep = "1 BIS" par exemple
            num_comp = []
            # num_comp_sort = composant du numéro d'adresse pour réaliser un tri logique par ordre alphabétique
            # ["000001", "B"] pour le num_rep = "1 BIS" et donc le num_rep_sort =  "000001 B" par exemple
            num_comp_sort = []
            if adp.get(param.DB_BAN_NUM) is not None:
                num_comp.append(str(adp.get(param.DB_BAN_NUM)))
                num_comp_sort.append(u"{:06d}".format(adp.get(param.DB_BAN_NUM)))

            if adp.get(param.DB_BAN_REP) is not None:
                num_comp.append(adp.get(param.DB_BAN_REP))
                rep_sort = adp[param.DB_BAN_REP]
                if rep_sort == u"BIS":
                    rep_sort = u"B"
                elif rep_sort == u"TER":
                    rep_sort = u"C"
                elif rep_sort == u"QUATER":
                    rep_sort = u"D"
                elif rep_sort == u"﻿QUINQUIES":
                    rep_sort = u"E"
                num_comp_sort.append(rep_sort)

            adp["num_rep"] = u" ".join(num_comp)
            adp["num_rep_sort"] = u" ".join(num_comp_sort)
            addr_points.append(adp)

    # Returns a list of address points records related to the same road segment
    return addr_points


def get_multipoint_geom_for_way(db_connection, insee, ban_table_name, rivoli):

    sql = u"""
        SELECT
          ST_AsText(ST_Union({0})) AS geometrie
        FROM {1}.{2}
        WHERE {3} = '{4}'
            AND {5} = '{6}'
         """.format(param.DB_BAN_GEOM,
                    param.DB_SCHEMA, ban_table_name,
                    param.DB_BAN_RIVOLI, rivoli,
                    param.DB_BAN_INSEE, insee)

    with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql)
        records = cur.fetchall()

        return records[0][0]


def get_all_segments_for_way_with_rivoli(db_connection, insee, rivoli):

    segments = {}

    # Boucle sur les tables
    individual_sql_selects = []
    for table_name in param.DB_ROAD_TABLES:
        individual_select = u"""
        SELECT {0},
               {1},
               {2},
               {3},
               {4},
               {5},
               {6},
               {7},
               {8},
               ST_AsText({9}) AS geom,
               '{11}' AS table_name
          FROM {10}.{11}
         WHERE {1} = '{13}' AND
               {2} = '{12}'
        """.format(param.DB_SDIS_ROAD_ID,
                   param.DB_SDIS_ROAD_INSEE,
                   param.DB_SDIS_ROAD_RIVOLI,
                   param.DB_SDIS_ROAD_NUM_DEB_GAU,
                   param.DB_SDIS_ROAD_NUM_DEB_DRO,
                   param.DB_SDIS_ROAD_NUM_FIN_GAU,
                   param.DB_SDIS_ROAD_NUM_FIN_DRO,
                   param.DB_SDIS_ROAD_SRC_NUM,
                   param.DB_SDIS_ROAD_COTE_IMPAIR,
                   param.DB_SDIS_ROAD_GEOM,
                   param.DB_SCHEMA,
                   table_name,
                   rivoli,
                   insee)
        individual_sql_selects.append(individual_select)

    sql = u"\nUNION\n".join(individual_sql_selects)
    sql += ";"

    # print(sql)

    if db_connection is None:
        print("Absence de connexion")
        return

    with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql)
        records = cur.fetchall()

        col_names = [desc[0] for desc in cur.description]

        for r in records:
            segment = {col_name: r[col_name] for col_name in col_names}
            segment["shapely_geom"] = shapely.wkt.loads(segment["geom"])
            segment["adps"] = []
            segments[segment[param.DB_SDIS_ROAD_ID]] = segment
            # Liste des points adresse associés au tronçon de voie (liste vide à son initialisation ici)

    # Returns a list of road segments records
    return segments


def get_all_segments_for_way_with_name(db_connection, insee, way_name, select_only_not_modified=True):

    segments = {}

    # Boucle sur les tables
    individual_sql_selects = []

    escaped_way_name = way_name.replace("'", "''")
    name_filters = [u"{} = '{}'".format(name_col, escaped_way_name) for name_col in param.DB_SDIS_ROAD_NAMES]
    name_filter = u" OR ".join(name_filters)
    if select_only_not_modified:
        filter = u"({}) AND {} IS NULL".format(name_filter, param.DB_SDIS_ROAD_SRC_NUM)
    else:
        filter = u"()".format(name_filter)

    for table_name in param.DB_ROAD_TABLES:
        individual_select = u"""
        SELECT {0},
               {1},
               {2},
               {3},
               {4},
               {5},
               {6},
               {7},
               {8},
               ST_AsText({9}) AS geom,
               '{11}' AS table_name
          FROM {10}.{11}
         WHERE {1} = '{12}' AND
               {13}
        """.format(param.DB_SDIS_ROAD_ID,
                   param.DB_SDIS_ROAD_INSEE,
                   param.DB_SDIS_ROAD_RIVOLI,
                   param.DB_SDIS_ROAD_NUM_DEB_GAU,
                   param.DB_SDIS_ROAD_NUM_DEB_DRO,
                   param.DB_SDIS_ROAD_NUM_FIN_GAU,
                   param.DB_SDIS_ROAD_NUM_FIN_DRO,
                   param.DB_SDIS_ROAD_SRC_NUM,
                   param.DB_SDIS_ROAD_COTE_IMPAIR,
                   param.DB_SDIS_ROAD_GEOM,
                   param.DB_SCHEMA,
                   table_name,
                   insee,
                   filter)
        individual_sql_selects.append(individual_select)

    sql = u"\nUNION\n".join(individual_sql_selects)
    sql += ";"

    # print(sql)

    if db_connection is None:
        print("Absence de connexion")
        return

    with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql)
        records = cur.fetchall()

        col_names = [desc[0] for desc in cur.description]

        for r in records:
            segment = {col_name: r[col_name] for col_name in col_names}
            segment["shapely_geom"] = shapely.wkt.loads(segment["geom"])
            # Liste des points adresse associés au tronçon de voie (liste vide à son initialisation ici)
            segment["adps"] = []
            segments[segment[param.DB_SDIS_ROAD_ID]] = segment

    # Returns a list of road segments records
    return segments


def get_stats_for_named_ways(db_connection, insee, table_name):

    stats = {}
    stats["wkt_geometries"] = []
    named_ways_has_numbers = {}

    name_fields_list = ", ".join(param.DB_SDIS_ROAD_NAMES)
    name_fields_filter = "({})".format(" OR ".join(["{} IS NOT NULL".format(f) for f in param.DB_SDIS_ROAD_NAMES]))
    number_sum_fields_list = "SUM(LENGTH({0})) as sum_{0}, SUM(LENGTH({1})) as sum_{1}," \
                             "SUM(LENGTH({2})) as sum_{2}, SUM(LENGTH({3})) as sum_{3}".format(
        param.DB_SDIS_ROAD_NUM_DEB_DRO,
        param.DB_SDIS_ROAD_NUM_FIN_DRO,
        param.DB_SDIS_ROAD_NUM_DEB_GAU,
        param.DB_SDIS_ROAD_NUM_FIN_GAU
    )

    sql = u"""
        SELECT {0}, {1}, ST_AsText(ST_Union({2})) AS geometrie
            FROM {3}.{4}
            WHERE {5} = '{6}'
                AND {7}
            GROUP BY {0}
            ;
        """.format(name_fields_list,
                   number_sum_fields_list,
                   param.DB_SDIS_ROAD_GEOM,
                   param.DB_SCHEMA, table_name,
                   param.DB_SDIS_ROAD_INSEE, insee,
                   name_fields_filter)

    with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql)
        records = cur.fetchall()

        for record in records:
            way_name = u"/".join([record[field_name].decode("utf-8") for field_name in param.DB_SDIS_ROAD_NAMES
                                 if record[field_name] is not None and record[field_name].strip])
            has_numbers = record["sum_{}".format(param.DB_SDIS_ROAD_NUM_DEB_DRO)] > 0 or \
                          record["sum_{}".format(param.DB_SDIS_ROAD_NUM_FIN_DRO)] > 0 or \
                          record["sum_{}".format(param.DB_SDIS_ROAD_NUM_DEB_GAU)] > 0 or \
                          record["sum_{}".format(param.DB_SDIS_ROAD_NUM_DEB_GAU)] > 0

            named_ways_has_numbers[way_name] = has_numbers
            if not has_numbers:
                stats["wkt_geometries"].append(record["geometrie"])

    stats["nb_of_named_ways"] = len(named_ways_has_numbers)
    stats["ways_with_no_numbers"] = sorted([k for k, v in named_ways_has_numbers.iteritems() if v is False])
    stats["nb_of_named_ways_with_no_numbers"] = len(stats["ways_with_no_numbers"])

    return stats


def clear_records_in_log(db_connection, table, insee, error_codes):
    sql = u"""
        DELETE FROM {}.{}
        WHERE {} = '{}'
            AND {} IN ({});
        """.format(
            param.DB_SCHEMA,
            table,
            param.DB_BAN_LOG_INSEE,
            insee,
            param.DB_BAN_LOG_ERROR,
            ", ".join([str(e) for e in error_codes])
        )

    with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql,)
    db_connection.commit()


def copy_adp_with_rivoli_to_log(db_connection, insee, message, error_code, ban_table_name, rivoli_codes):

    wkt_geometries = []
    rivoli_codes_list = ", ".join(["'{}'".format(r) for r in rivoli_codes])
    sql = u"""
        SELECT {0}, {1}, {2}, ST_AsText({3}) AS geometrie
            FROM {4}.{5}
            WHERE {6} = '{7}'
                AND {8} IN ({9})
            ;
        """.format(param.DB_BAN_NAME,
                   param.DB_BAN_NUM,
                   param.DB_BAN_REP,
                   param.DB_BAN_GEOM,
                   param.DB_SCHEMA, ban_table_name,
                   param.DB_BAN_INSEE, insee,
                   param.DB_BAN_RIVOLI, rivoli_codes_list)

    with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql)
        records = cur.fetchall()

        for r in records:
            wkt_geometries.append(r["geometrie"])

    insert_records_in_log(
        db_connection=db_connection,
        table=param.DB_BAN_LOG_P_TABLE,
        insee=insee,
        message=message,
        error_code=error_code,
        geometries=wkt_geometries)


def insert_records_in_log(db_connection, table, insee, message, error_code, geometries):

    cols = (
        param.DB_BAN_LOG_DATE,
        param.DB_BAN_LOG_INSEE,
        param.DB_BAN_LOG_MESSAGE,
        param.DB_BAN_LOG_ERROR,
        param.DB_BAN_LOG_GEOM
    )
    cols_list = ", ".join(cols)
    vals_list = []

    for wkt_geom in geometries:
        vals_list.append(u"({}, '{}', '{}', {}, {})".format(
            "NOW()",
            insee,
            message,
            error_code,
            "ST_GeomFromText('{}', 27572)".format(wkt_geom)
        ))

    all_vals_string = u", ".join(vals_list)

    # Insertion d'un nouvel enregistrement
    sql = u"""
        INSERT INTO {0}.{1} ({2})
        VALUES {3};
    """.format(
        param.DB_SCHEMA,
        table,
        cols_list,
        all_vals_string)

    with db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute(sql,)
    db_connection.commit()
