# -*- coding: utf-8 -*-

import utils

import psycopg2
import psycopg2.extras

import time
import click

import param
import fantoir


class FantoirUpdater(object):
    def __init__(self):

        # fantoir data
        self.fantoir_data = None

        # db connection
        db_conn_str = utils.build_db_connect_string()
        self.db_connection = psycopg2.connect(db_conn_str)
        self.db_connection.set_client_encoding('UTF8')

    def load_fantoir_table(self, fantoir_data):

        # fantoir data
        self.fantoir_data = fantoir_data

        cur = self.db_connection.cursor()
        # Nettoyage de la table
        sql = u"""
            DELETE FROM {}.{};
            """.format(param.DB_SCHEMA, param.DB_FANTOIR_TABLE)
        cur.execute(sql)

        # Boucle sur les villes
        for k, v in self.fantoir_data.iteritems():

            # Boucle sur les voies
            for record in v["city_ways"]:

                cols = (
                    'rivo', 'dept', 'comm', 'insee', 'way', 'natu', 'name', 'type', 'priv', 'cat_code', 'cat',
                    'comp_name')
                for comp_name in record['comp_names']:
                    vals = ["'{}'".format(record[col].replace("'", "''")) for col in cols[:-1]]
                    vals.append("'{}'".format(comp_name.replace("'", "''")))

                    # Insertion d'un nouvel enregistrement
                    sql = u"""
                        INSERT INTO {}.{} ({})
                        VALUES ({});
                    """.format(param.DB_SCHEMA, param.DB_FANTOIR_TABLE, ",".join(cols), ",".join(vals))
                    cur.execute(sql)

        self.db_connection.commit()
        cur.close()

    def update(self, use_ban=False, use_bano=False):
        insee_codes = utils.get_all_city_insee(self.db_connection)

        click.echo(u"Nombre de communes à traiter : {}".format(len(insee_codes)))
        for insee in insee_codes:
            click.echo(u"Traitement de la commune : {}".format(insee))
            self.update_for_one_city(insee, use_ban=use_ban, use_bano=use_bano)

    def clear_rivoli_codes(self):
        for table_name in param.DB_ROAD_TABLES:
            sql = """
                UPDATE {0}.{1}
                SET {2} = DEFAULT, {3} = DEFAULT, {4} = DEFAULT
                WHERE ({4} = '{5}' OR {4} IS NULL);
            """.format(param.DB_SCHEMA,
                       table_name,
                       param.DB_SDIS_ROAD_RIVOLI,
                       param.DB_SDIS_ROAD_RIVOLI_DIST,
                       param.DB_SDIS_ROAD_SRC_RIVOLI,
                       param.DB_SDIS_ROAD_SRC_RIVOLI_NEOGEO_VALUE)
            with self.db_connection.cursor() as cur:
                cur.execute(sql)

        self.db_connection.commit()

    def clear_rivoli_codes_for_one_city(self, insee):
        # Suppression des informations sur les codes rivoli pour la commune en question
        for table_name in param.DB_ROAD_TABLES:
            sql = """
                UPDATE {0}.{1}
                SET {2} = DEFAULT, {3} = DEFAULT, {4} = DEFAULT
                WHERE ({4} = '{5}' OR {4} IS NULL) AND {6} = '{7}';
            """.format(param.DB_SCHEMA,
                       table_name,
                       param.DB_SDIS_ROAD_RIVOLI,
                       param.DB_SDIS_ROAD_RIVOLI_DIST,
                       param.DB_SDIS_ROAD_SRC_RIVOLI,
                       param.DB_SDIS_ROAD_SRC_RIVOLI_NEOGEO_VALUE,
                       param.DB_SDIS_ROAD_INSEE,
                       insee)
            with self.db_connection.cursor() as cur:
                cur.execute(sql)

        self.db_connection.commit()

    def update_for_one_city(self, insee, use_ban=False, use_bano=False):
        result_dict = {}

        time1 = time.time()
        self.find_rivoli_from_fantoir_for_one_city(insee, result_dict)
        # time2 = time.time()
        # print(u"    find_rivoli_from_fantoir_for_one_city : {}".format(time2-time1))
        # print(result_dict)

        if use_ban:
            self.find_rivoli_from_ban_for_one_city(insee, ban_table_name=param.DB_BAN_TABLE, result_dict=result_dict)
        # time3 = time.time()
        # print(u"    find_rivoli_from_ban_for_one_city (ban) : {}".format(time3-time2))
        # print(result_dict)

        if use_bano:
            self.find_rivoli_from_ban_for_one_city(insee, ban_table_name=param.DB_BANO_TABLE, result_dict=result_dict)
        # time4 = time.time()
        # print(u"    find_rivoli_from_ban_for_one_city (bano) : {}".format(time4-time3))

        # print(result_dict)

        # Suppression des informations sur les codes rivoli pour la commune en question
        # self.clear_rivoli_codes_for_one_city(insee=insee)

        # time5 = time.time()
        # print(u"    delete : {}".format(time5-time4))

        # Mise à jour de la base

        for name_field in param.DB_SDIS_ROAD_NAMES:

            for way_name, results in result_dict.iteritems():
                min_dist = min(results.values())
                rivoli_codes = [k for k,v in results.iteritems() if v == min_dist]

                for table_name in param.DB_ROAD_TABLES:
                    sql = u"""
                        UPDATE {0}.{1}
                        SET {2} = '{3}', {4} = {5}, {6} = '{7}'
                        WHERE {8} = '{9}' AND {10} = '{11}' AND ({6} = '{7}' OR {6} IS NULL);
                    """.format(param.DB_SCHEMA,
                               table_name,
                               param.DB_SDIS_ROAD_RIVOLI,
                               ', '.join(rivoli_codes),
                               param.DB_SDIS_ROAD_RIVOLI_DIST,
                               min_dist,
                               param.DB_SDIS_ROAD_SRC_RIVOLI,
                               param.DB_SDIS_ROAD_SRC_NUM_NEOGEO_VALUE,
                               param.DB_SDIS_ROAD_INSEE,
                               insee,
                               name_field,
                               way_name.replace("'", "''"))
                    with self.db_connection.cursor() as cur:
                        cur.execute(sql)

        self.db_connection.commit()
        time6 = time.time()
        # print(u"    update : {}".format(time6-time5))

        click.echo(u" temps de traitement pour {} : {} s".format(insee, time6-time1))

    def add_results_to_dict(self, result_dict, way_name, results):
        if way_name in result_dict:
            for k, v in results.iteritems():
                if k in result_dict[way_name]:
                    if results[k] < result_dict[way_name][k]:
                        result_dict[way_name][k] = results[k]
                else:
                    result_dict[way_name][k] = results[k]
        else:
            result_dict[way_name] = results

    def find_rivoli_from_fantoir(self):
        for insee in utils.get_all_city_insee(self.db_connection):
            self.find_rivoli_from_fantoir_for_one_city(insee)

    def find_rivoli_from_fantoir_for_one_city(self, insee, result_dict):
        # Résultat : dictionnaire :
        #   - clef : nom de la voie dans la base du sdis
        #   - valeur : liste de couples du type (identifiant rivoli, distance de levenshtein)

        for name_field in param.DB_SDIS_ROAD_NAMES:

            sql = u"""
                SELECT distinct({0})
                    FROM (
            """.format(name_field)

            # Boucle sur les tables
            individual_sql_selects = []
            for table_name in param.DB_ROAD_TABLES:
                individual_select = """
                    SELECT {0}
                        FROM {1}.{2}
                        WHERE {3} = '{4}' AND {0} IS NOT NULL
                """.format(name_field, param.DB_SCHEMA, table_name, param.DB_SDIS_ROAD_INSEE, insee)
                individual_sql_selects.append(individual_select)

            sql += u"\nUNION\n".join(individual_sql_selects)

            sql += u""") as reseau
                ORDER BY reseau.{0} ASC;
            """.format(name_field)

            with self.db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql)
                records = cur.fetchall()

                for r in records:
                    way_name = r[0]
                    if way_name:
                        way_name = way_name.decode("utf-8")
                        self.find_rivoli_from_fantoir_for_one_way(insee=insee, way_name=way_name,
                                                                  result_dict=result_dict)

    def find_rivoli_from_fantoir_for_one_way(self, insee, way_name, result_dict):

        results = {}
        DB_FANTOIR_INSEE = "insee"
        DB_FANTOIR_RIVOLI = "rivo"
        DB_FANTOIR_WAY = "way"
        DB_FANTOIR_NATURE = "natu"
        DB_FANTOIR_TYPE = "type"
        DB_FANTOIR_NAME = "name"
        DB_FANTOIR_COMP_NAME = "comp_name"

        escaped_way_name = way_name.replace("'", "''")
        leven_dist_max = max(5, int(len(way_name)/5))
        # Recherche des noms de voies de la base Fantoir qui sont les plus proches du nom de la voie dans la base du SDIS
        sql = u"""
            SELECT {0}, {1}, {2}, {3}, {4}, levenshtein(upper(comp_name), '{5}', 1, 1, 2) as leven_dist
                FROM {6}.{7}
                WHERE
                levenshtein(upper({4}), '{5}') < {11}
                AND {8} = '{9}'
                AND {10} IN('1', '4', '5')
                ORDER BY leven_dist ASC
                LIMIT 20;
            """.format(
            param.DB_FANTOIR_RIVOLI,
            param.DB_FANTOIR_WAY,
            param.DB_FANTOIR_NATURE,
            param.DB_FANTOIR_NAME,
            param.DB_FANTOIR_COMP_NAME,
            escaped_way_name,
            param.DB_SCHEMA,
            param.DB_FANTOIR_TABLE,
            param.DB_FANTOIR_INSEE,
            insee,
            param.DB_FANTOIR_TYPE,
            leven_dist_max)
        with self.db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            records = cur.fetchall()
            if len(records) == 1:
                r = records[0]
                dist = r["leven_dist"]
                if dist > 0 and r[param.DB_FANTOIR_NAME].decode("utf-8") in way_name:
                    dist = dist - 1
                results[r[param.DB_FANTOIR_RIVOLI][-5:-1]] = dist
            elif len(records) > 1:
                for r in records:
                    dist = r["leven_dist"]
                    if dist > 0 and r[param.DB_FANTOIR_NAME].decode("utf-8") in way_name:
                        dist = dist - 1
                    results[r[param.DB_FANTOIR_RIVOLI][-5:-1]] = dist

        if results:
            self.add_results_to_dict(result_dict, way_name, results)

    def find_rivoli_from_ban(self, ban_table_name):

        for insee in utils.get_all_city_insee(self.db_connection):
            self.find_rivoli_from_ban_for_one_city(insee, ban_table_name)

    def find_rivoli_from_ban_for_one_city(self, insee, ban_table_name, result_dict, max_nb_roads=None):
        # Résultat : dictionnaire :
        #   - clef : nom de la voie dans la base du sdis
        #   - valeur : liste de couples du type (identifiant rivoli, distance de levenshtein)

        sql = u"""
            SELECT
              ST_AsText(ST_Union({0})) AS geometrie,
              {1},
              {2},
              {3}
            FROM {4}.{5}
            WHERE {2} = '{6}'
                AND substring({1}, 1, 1) IN ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X', 'Y', 'Z')
                AND {1} IS NOT NULL AND {3} IS NOT NULL
            GROUP BY {1}, {2}, {3}
            ORDER BY {1}
             """.format(param.DB_BAN_GEOM, param.DB_BAN_RIVOLI, param.DB_BAN_INSEE, param.DB_BAN_NAME,
                        param.DB_SCHEMA, ban_table_name, insee)

        if max_nb_roads is not None:
            sql += u"""LIMIT {0};
                """.format(max_nb_roads)

        sql += u";"

        with self.db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            records = cur.fetchall()

            for r in records:
                wkt_geom = r[param.DB_BAN_GEOM]
                id_fantoir = r[param.DB_BAN_RIVOLI]
                ban_way_name = r[param.DB_BAN_NAME]
                if ban_way_name :
                    ban_way_name = ban_way_name.decode("utf-8")

                self.find_rivoli_from_ban_for_one_way(ban_table_name=ban_table_name, insee=insee,
                                                      id_fantoir=id_fantoir, ban_way_name=ban_way_name,
                                                      wkt_geom=wkt_geom, result_dict=result_dict)

    def find_rivoli_from_ban_for_one_way(
            self, ban_table_name, insee, id_fantoir, ban_way_name, wkt_geom, result_dict):

        results = {}

        max_dist = param.MAX_DIST_WITH_NAME
        leven_dist_max = max(5, int(len(ban_way_name)/5))

        for name_field in param.DB_SDIS_ROAD_NAMES:

            # Récupération des tronçons situés à proximité de la géométrie
            # Pour assurer une certaine continuité seuls les tronçons portant un nom sont récupérés
            # Les résultats sont groupés par nom de voie
            # Les plus grands ensembles de voies portant le même nom sont recherchés
            # Si des ensembles de voies de longueurs similaires sont détectés la proximité orthographique est étudiée

            sql = u"""
                SELECT reseau.{0}, count(*) as {1}, SUM(length) as {2},
                    levenshtein(upper(reseau.{0}),'{3}', 1, 1, 2) as {4}
                FROM(
                """.format(name_field, 'count', 'length', ban_way_name.upper().replace("'", "''"), 'leven_dist')

            individual_sql_selects = []
            for table_name in param.DB_ROAD_TABLES:
                individual_select = """
                    (SELECT {0}, {1}, ST_Length({2}) as length
                        FROM {3}.{4}
                    WHERE {0} = '{6}'
                        AND {1} IS NULL
                        AND ST_Distance({2}, ST_GeomFromText('{5}', 27572)) < {7})
                    """.format(
                        param.DB_SDIS_ROAD_INSEE,
                        name_field,
                        param.DB_SDIS_ROAD_GEOM,
                        param.DB_SCHEMA,
                        table_name,
                        wkt_geom,
                        insee,
                        max_dist)
                individual_sql_selects.append(individual_select)

            sql += u"\nUNION\n".join(individual_sql_selects)

            sql += u""") as reseau
                GROUP BY reseau.{0}, reseau.{1}
                ORDER BY {2} DESC;
                """.format(param.DB_SDIS_ROAD_INSEE, name_field, 'length')

            with self.db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(sql)
                records = cur.fetchall()

                # Parmi tous les résultats retournés on ne retient que les ensembles de voies qui ont une distance de
                # levenshtein potable
                # Pour des distances de levenshtein similaires on ne retient que l'ensemble des voies avec la
                # plus grande longueur

                possible_records = []

                if len(records) > 0:
                    least_leven_dist = min([r['leven_dist'] for r in records])
                    if least_leven_dist < len(ban_way_name) and least_leven_dist < leven_dist_max:
                        possible_records = [r for r in records if r['leven_dist'] == least_leven_dist]

                    final_records = []
                    if len(possible_records) == 1:
                        final_records = possible_records

                    elif len(possible_records) > 1:
                        final_records = []
                        max_length = max([r['length'] for r in possible_records])
                        final_records = [r for r in possible_records if r['length'] == max_length]

                    if len(final_records) > 0:
                        for r in final_records:
                            way_name = r[name_field]
                            leven_dist = r['leven_dist']
                            results[id_fantoir] = leven_dist

        if results:
            self.add_results_to_dict(result_dict, way_name, results)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('fantoir_file_path', type=click.Path(exists=True))
def load_fantoir(fantoir_file_path):
    """Chargement d'un fichier Fantoir dans la base de données

\b
Exemple : python update_ways_fantoir.py load_fantoir ../data/fantoir/nouvelle_aquitaine/330.txt"""
    click.echo(u"Chargement d'un fichier fantoir dans la base de données...")
    click.echo(u"Fichier Fantoir : {}".format(fantoir_file_path))
    # fantoir_file_path = r"../data/fantoir/nouvelle_aquitaine/330.txt"
    parser = fantoir.FantoirParser(fantoir_file_path)
    updater = FantoirUpdater()
    updater.load_fantoir_table(parser.get_data())


@cli.command()
@click.option('--ban/--no-ban', default=False, help=u"exploite la BAN pour compléter les codes Rivoli")
@click.option('--bano/--no-bano', default=False, help=u"exploite la BANO pour compléter les codes Rivoli")
@click.argument('insee', nargs=-1)
def update(insee, ban, bano):
    """Mise à jour des codes Rivoli du réseau routier à partir des données Fantoir.

Par défaut, cette commande compare les noms des voies avec les noms officiels présents dans la base Fantoir. Pour
exploiter les codes Rivoli présents dans la BAN et la BANO utilisez les options --ban et --bano.

\b
Exemples :
- Affichage de l'aide sur cette commande :
    python rivoli.py update --help
- Mise à jour des codes rivoli d'une commune :
    python rivoli.py update 33316
- Mise à jour des codes rivoli de 2 communes :
    python rivoli.py update 33316 33424
- Mise à jour des codes rivoli de toutes les communes :
    python rivoli.py update
- Mise à jour des codes rivoli d'une commune en utilisant en plus la BAN :
    python rivoli.py update --ban 33316
- Mise à jour des codes rivoli d'une commune en utilisant en plus la BANO :
    python rivoli.py update --bano 33316"""

    click.echo(u"Mise à jour des codes Rivoli du réseau routier à partir des données Fantoir...")

    # search fantoir codes for one city
    updater = FantoirUpdater()

    if len(insee) == 0:
        click.echo(u"Aucun code INSEE spécifié.")
        click.echo(u"L'ensemble des codes INSEE de la base seront traités. Le temps de traitement peut durer plusieurs heures.")
        if click.confirm(u"Voulez-vous continuer ?"):
            click.echo(u"Traitement lancé sur l'ensemble des codes INSEE de la base.")
            updater.update(use_ban=ban, use_bano=bano)
        else:
            click.echo(u"Traitement annulé.")
    else:
        for i in insee:
            click.echo(u"Traitement de la commune : {}".format(i))
            updater.update_for_one_city(i, use_ban=ban, use_bano=bano)


@cli.command()
@click.argument('insee', nargs=-1)
def clear(insee):
    """Suppression des codes Rivoli renseignés automatiquement.
\b
Exemples :
- Affichage de l'aide sur cette commande :
    python rivoli.py clear --help
- Suppression des codes Rivoli d'une commune :
    python rivoli.py clear 33316
- Suppression des codes Rivoli de 2 communes :
    python rivoli.py clear 33316 33424
- Suppression des codes Rivoli de toutes les communes :
    python rivoli.py clear"""

    click.echo(u"Supression des codes Rivoli du réseau routier...")

    updater = FantoirUpdater()

    if len(insee) == 0:
        click.echo(u"Aucun code INSEE spécifié.")
        click.echo(u"L'ensemble des codes INSEE de la base seront traités.")
        if click.confirm(u"Voulez-vous continuer ?"):
            click.echo(u"Traitement lancé sur l'ensemble des codes INSEE de la base.")
            updater.clear_rivoli_codes()
        else:
            click.echo(u"Traitement annulé.")
    else:
        for i in insee:
            click.echo(u"Traitement de la commune : {}".format(i))
            updater.clear_rivoli_codes_for_one_city(i)


if __name__ == '__main__':
    cli()
