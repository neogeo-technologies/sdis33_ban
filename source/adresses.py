# -*- coding: utf-8 -*-

import utils

import psycopg2
import psycopg2.extras

import time
import click
import pprint

import shapely.ops

import param


# retourne le signe du nombre
def sign(x):
    return x and (1, -1)[x < 0]


class NumbersUpdater(object):
    def __init__(self):

        # Table des points adresse
        addr_table_name = param.DB_BAN_TABLE

        # db connection
        db_conn_str = utils.build_db_connect_string()
        self.db_connection = psycopg2.connect(db_conn_str)
        self.db_connection.set_client_encoding('UTF8')

    def clear_adresses(self):
        for table_name in param.DB_ROAD_TABLES:
            sql = """
                UPDATE {0}.{1}
                SET {2} = NULL, {3} = NULL, {4} = NULL, {5} = NULL, {6} = NULL
                WHERE ({6} = '{7}' OR {6} IS NULL);
            """.format(param.DB_SCHEMA,
                       table_name,
                       param.DB_SDIS_ROAD_NUM_DEB_GAU,
                       param.DB_SDIS_ROAD_NUM_FIN_GAU,
                       param.DB_SDIS_ROAD_NUM_DEB_DRO,
                       param.DB_SDIS_ROAD_NUM_FIN_DRO,
                       param.DB_SDIS_ROAD_SRC_NUM,
                       param.DB_SDIS_ROAD_SRC_NUM_NEOGEO_VALUE)
            with self.db_connection.cursor() as cur:
                cur.execute(sql)

        self.db_connection.commit()

    def clear_adresses_for_one_city(self, insee):
        # Suppression des informations sur les adresses pour la commune en question
        for table_name in param.DB_ROAD_TABLES:
            sql = """
                UPDATE {0}.{1}
                SET {2} = NULL, {3} = NULL, {4} = NULL, {5} = NULL, {6} = NULL
                WHERE ({6} = '{7}' OR {6} IS NULL) AND {8} = '{9}';
            """.format(param.DB_SCHEMA,
                       table_name,
                       param.DB_SDIS_ROAD_NUM_DEB_GAU,
                       param.DB_SDIS_ROAD_NUM_FIN_GAU,
                       param.DB_SDIS_ROAD_NUM_DEB_DRO,
                       param.DB_SDIS_ROAD_NUM_FIN_DRO,
                       param.DB_SDIS_ROAD_SRC_NUM,
                       param.DB_SDIS_ROAD_SRC_NUM_NEOGEO_VALUE,
                       param.DB_SDIS_ROAD_INSEE,
                       insee)
            with self.db_connection.cursor() as cur:
                cur.execute(sql)

        self.db_connection.commit()

    # Fonction déterminant de quel côté du tronçon sont situés les différents points adresse
    # 2 cas de figure :
    #   - on sait a priori si les numéros pairs et impairs sont bien séparés de chaque côté de la voie et de quel côté
    #     Dans ce cas, on regarde juste si l'adresse est paire ou impaire pour déterminer de quel côté elle est censée
    #     se trouver
    #   - on ne sait pas, dans ce cas on détermine de manière géométrique la position du point adresse à droite ou à
    #     à gauche. Si le point est à une distance inférieure d'un seuil du tronçon, on considère qu'on ne peut pas
    #     déterminer son côté. Pour les autres cas, on trace une ligne parallèle à droite. Si le point adresse est plus
    #     proche de la ligne de droite que de la ligne originelle on considère que le point est à droite. Sinon il est
    #     à gauche
    def identify_side_for_adps(self, road_segment):

        # Géométrie du tronçon
        longer_geom_part_index = -1
        length_of_longer_geom_part = -1
        nb_parts = len(road_segment["shapely_geom"].geoms)
        for part_index in range(nb_parts):
            part_length = road_segment["shapely_geom"].geoms[part_index].length
            if part_length > length_of_longer_geom_part:
                longer_geom_part_index = part_index
                length_of_longer_geom_part = part_length

        if longer_geom_part_index < 0 and length_of_longer_geom_part <= 0.:
            #TODO: Insérer l'évènement dans les logs
            for adp in road_segment["adps"]:
                adp["side"] = "m"
                return

        segment_geometry = road_segment["shapely_geom"].geoms[longer_geom_part_index]

        # Est-ce qu'on sait si les numéros pairs et impairs sont d'un côté particulier ?
        # Si l'on connait le côté des numéros pairs et celui des numéros impairs on regarde juste si le numéro est pair
        # ou impair pour lui affecter un côté
        # Sinon on cherche de quel côté il est en exploitant les géométries du tronçon et du point adresse

        # D'abord le côté droit
        if road_segment[param.DB_SDIS_ROAD_COTE_IMPAIR] == "d":
            # Boucle sur les points adresse associés au tronçon
            for adp in road_segment["adps"]:
                impair = adp[param.DB_BAN_NUM] % 2
                if impair:
                    adp["side"] = "d"
                else:
                    adp["side"] = "g"

        # Puis le côté gauche
        elif road_segment[param.DB_SDIS_ROAD_COTE_IMPAIR] == "g":
            # Boucle sur les points adresse associés au tronçon
            for adp in road_segment["adps"]:
                impair = adp[param.DB_BAN_NUM] % 2
                if impair:
                    adp["side"] = "g"
                else:
                    adp["side"] = "d"

        # Sinon
        else:
            # seuil de distance
            dist_max = param.DROITE_GAUCHE_DIST

            # Calcul d'une ligne décalée à droite  et d'une autre à gauche du tronçon
            right_shifted_segment_geometry = segment_geometry.parallel_offset(distance=dist_max, side='right', resolution=2)
            # left_shifted_segment_geometry = segment_geometry.parallel_offset(distance=dist_max, side='left', resolution=2)

            # Boucle sur les points adresse associés au tronçon
            for adp in road_segment["adps"]:
                adp_geometry = adp["shapely_geom"]

                # Calcul de la distance par rapport à la géométrie d'origine
                dist = adp_geometry.distance(segment_geometry)

                # Si la distance est inférieure au seuil on est dans un cas indéterminé
                if dist > dist_max:
                    # Calcul de la distance par rapport à la géométrie de droite
                    # Calcul de la distance par rapport à la géométrie de gauche
                    dist_right = adp_geometry.distance(right_shifted_segment_geometry)

                    if dist_right < dist:
                        adp["side"] = "d"
                    else:
                        adp["side"] = "g"
                else:
                    adp["side"] = "m"

    # Fonction déterminant la position de chaque point adresse par rapport à son début et sa fin
    # (référencement linéaire)
    def compute_linear_reference_for_adps(self, road_segment):

        # Géométrie du tronçon
        segment_geometry = road_segment["shapely_geom"].geoms[0]

        # Boucle sur les points adresse associés au tronçon
        for adp in road_segment["adps"]:
            adp_geometry = adp["shapely_geom"]

            linear_proj = segment_geometry.project(adp_geometry, normalized=True)
            adp["proj"] = linear_proj

    # Fonction déterminant les numéros de début et fin à gauche et à droite du tronçon
    def identify_numbers_at_ends(self, road_segment):
        # Tentative de détermination de l'ordre croissant
        # -1 : décroissance des numéros
        # 0 : on ne sait pas
        # +1 : croissance des numéros
        order = 0

        # Points côté gauche et côté droit dans leur ordre de présence le long du tronçon
        adp_g = [adp for adp in sorted(road_segment["adps"], key=lambda k: k["proj"]) if adp["side"] == "g"]
        adp_d = [adp for adp in sorted(road_segment["adps"], key=lambda k: k["proj"]) if adp["side"] == "d"]

        # Division de chaque tronçon en n zones consécutives
        # Sur chaque zone on effectue une moyenne des numéros présents
        # On compare la moyenne de chaque zone à la moyenne de la zone suivante
        # Si l'ordre de ces moyennes correspond à une croissance ou une décroissance des deux côtés, alors on recherche
        # les numéros les petits et les plus grands à associer au tronçons
        # Sinon, on garde les numéros les plus proches des extrémités
        nb_zones = 4
        mean_num_zone_g = []
        mean_num_zone_d = []
        for n in range(nb_zones):
            proj_min = n*(1./float(nb_zones))
            proj_max = (n+1)*(1./float(nb_zones))

            adp_num_zone_g = [adp[param.DB_BAN_NUM] for adp in adp_g if proj_min <= adp["proj"] <= proj_max]
            adp_num_zone_d = [adp[param.DB_BAN_NUM] for adp in adp_d if proj_min <= adp["proj"] <= proj_max]
            if len(adp_num_zone_g) > 0:
                mean_value = float(sum(adp_num_zone_g)) / max(len(adp_num_zone_g), 1)
                mean_num_zone_g.append(mean_value)

            if len(adp_num_zone_d) > 0:
                mean_value = float(sum(adp_num_zone_d)) / max(len(adp_num_zone_d), 1)
                mean_num_zone_d.append(mean_value)

        order_zones = []
        if len(mean_num_zone_g) > 0:
            order_zones += [sign(mean_num_zone_g[n+1] - mean_num_zone_g[n]) for n in range(len(mean_num_zone_g)-1)]

        if len(mean_num_zone_d) > 0:
            order_zones += [sign(mean_num_zone_d[n+1] - mean_num_zone_d[n]) for n in range(len(mean_num_zone_d)-1)]

        nb_plus_sign = len([v for v in order_zones if v > 0])
        nb_minus_sign = len([v for v in order_zones if v < 0])

        if nb_plus_sign*5 <= nb_minus_sign:
            order = -1
        if nb_minus_sign*5 <= nb_plus_sign:
            order = +1

        road_segment[param.DB_SDIS_ROAD_NUM_DEB_GAU] = None
        road_segment[param.DB_SDIS_ROAD_NUM_FIN_GAU] = None
        road_segment[param.DB_SDIS_ROAD_NUM_DEB_DRO] = None
        road_segment[param.DB_SDIS_ROAD_NUM_FIN_DRO] = None

        if order == 0:
            sorted_adp_g = sorted(adp_g, key=lambda k: k["proj"])
            sorted_adp_d = sorted(adp_d, key=lambda k: k["proj"])
            if len(sorted_adp_g) > 0:
                road_segment[param.DB_SDIS_ROAD_NUM_DEB_GAU] = sorted_adp_g[0]["num_rep"]
                road_segment[param.DB_SDIS_ROAD_NUM_FIN_GAU] = sorted_adp_g[-1]["num_rep"]
            if len(sorted_adp_d) > 0:
                road_segment[param.DB_SDIS_ROAD_NUM_DEB_DRO] = sorted_adp_d[0]["num_rep"]
                road_segment[param.DB_SDIS_ROAD_NUM_FIN_DRO] = sorted_adp_d[-1]["num_rep"]
        else:
            sorted_adp_g = sorted(adp_g, key=lambda k: k["num_rep_sort"])
            sorted_adp_d = sorted(adp_d, key=lambda k: k["num_rep_sort"])
            if len(sorted_adp_g) > 0:
                min_g = sorted_adp_g[0]["num_rep"]
                max_g = sorted_adp_g[-1]["num_rep"]
                if order > 0:
                    road_segment[param.DB_SDIS_ROAD_NUM_DEB_GAU] = min_g
                    road_segment[param.DB_SDIS_ROAD_NUM_FIN_GAU] = max_g
                else:
                    road_segment[param.DB_SDIS_ROAD_NUM_DEB_GAU] = max_g
                    road_segment[param.DB_SDIS_ROAD_NUM_FIN_GAU] = min_g

            if len(sorted_adp_d) > 0:
                min_d = sorted_adp_d[0]["num_rep"]
                max_d = sorted_adp_d[-1]["num_rep"]
                if order > 0:
                    road_segment[param.DB_SDIS_ROAD_NUM_DEB_DRO] = min_d
                    road_segment[param.DB_SDIS_ROAD_NUM_FIN_DRO] = max_d
                else:
                    road_segment[param.DB_SDIS_ROAD_NUM_DEB_DRO] = max_d
                    road_segment[param.DB_SDIS_ROAD_NUM_FIN_DRO] = min_d

    def find_closest_segments_for_addr_point(self, adp, road_segments):
        distances = []
        closest_segments = []
        adp_geom = adp["shapely_geom"]

        for seg in road_segments.values():
            seg_geom = seg["shapely_geom"]
            distance = adp_geom.distance(seg_geom)
            distances.append({"segment": seg, "distance": distance})

        closest_segments = []
        if len(distances) > 0:
            distances = sorted(distances,  key=lambda k: k["distance"])
            min_distance = distances[0]["distance"]
            max_distance = min_distance + 15

            closest_segments = [item for item in distances if item["distance"] < max_distance]
            # print(u"distance minimale : {} - nombre de tronçons : {}".format(min_distance, len(closest_segments)))

        return closest_segments

    def update_road_segments_with_adps(self, road_segments, addr_points):
        # Boucle sur chacun des points adresse pour identifier les tronçons les plus proches
        for adp in addr_points:
            closest_segments = self.find_closest_segments_for_addr_point(adp, road_segments)
            if len(closest_segments) > 0:
                closest_segment = closest_segments[0]["segment"]
                road_segments[closest_segment[param.DB_SDIS_ROAD_ID]]["adps"].append(adp)

            # segments_related_to_address_points[adp[ban_attr_id]] = closest_segments
            # address_points_data[adp[ban_attr_id]] = adp

        for r in road_segments.values():
            # Détection des points situés à gauche et à droite
            self.identify_side_for_adps(r)

            # Calcul de la distance des points adresse par rapport au début du tronçon
            self.compute_linear_reference_for_adps(r)

            # Identificaton des numéros en début et fin de chaque côté
            self.identify_numbers_at_ends(r)

            # print(u"id : {} - nb de points adresse : {}".format(r[param.DB_SDIS_ROAD_ID], len(r["adps"])))
            # print(u"id : {} - points adresse à gauche : {}".format(r[param.DB_SDIS_ROAD_ID], ", ".join([adp["num_rep"] for adp in sorted(r["adps"], key=lambda k: k["num_rep_sort"]) if adp["side"] == "g"])))
            # print(u"id : {} - points adresse à droite : {}".format(r[param.DB_SDIS_ROAD_ID], ", ".join([adp["num_rep"] for adp in sorted(r["adps"], key=lambda k: k["num_rep_sort"]) if adp["side"] == "d"])))
            # print(u"id : {} - points adresse ailleurs : {}".format(r[param.DB_SDIS_ROAD_ID], ", ".join([adp["num_rep"] for adp in sorted(r["adps"], key=lambda k: k["num_rep_sort"]) if adp["side"] == "m"])))
            # print(u"id : {} - projection : {}".format(r[param.DB_SDIS_ROAD_ID], ", ".join([str(adp["proj"]) for adp in sorted(r["adps"], key=lambda k: k["num_rep_sort"])])))

            # print("{} {} {} {}".format(
            #     r.get(param.DB_SDIS_ROAD_NUM_DEB_GAU), r.get(param.DB_SDIS_ROAD_NUM_FIN_GAU),
            #     r.get(param.DB_SDIS_ROAD_NUM_DEB_DRO), r.get(param.DB_SDIS_ROAD_NUM_FIN_DRO)))

            # Mise à jour des points adresse et des tronçons avec les informations collectées
            # uniquement si les informations n'ont pas pour origine une autre source
            if r[param.DB_SDIS_ROAD_SRC_NUM] in (param.DB_SDIS_ROAD_SRC_NUM_NEOGEO_VALUE, None):
                sql = """
                    UPDATE {0}.{1}
                    SET {2} = {3}, {4} = {5}, {6} = {7}, {8} = {9}, {10} = '{11}'
                    WHERE {12} = {13};
                """.format(
                    param.DB_SCHEMA,
                    r['table_name'],
                    param.DB_SDIS_ROAD_NUM_DEB_GAU,
                    "'{}'".format(r[param.DB_SDIS_ROAD_NUM_DEB_GAU]) if r[param.DB_SDIS_ROAD_NUM_DEB_GAU] is not None else 'DEFAULT',
                    param.DB_SDIS_ROAD_NUM_FIN_GAU,
                    "'{}'".format(r[param.DB_SDIS_ROAD_NUM_FIN_GAU]) if r[param.DB_SDIS_ROAD_NUM_FIN_GAU] is not None else "DEFAULT",
                    param.DB_SDIS_ROAD_NUM_DEB_DRO,
                    "'{}'".format(r[param.DB_SDIS_ROAD_NUM_DEB_DRO]) if r[param.DB_SDIS_ROAD_NUM_DEB_DRO] is not None else "DEFAULT",
                    param.DB_SDIS_ROAD_NUM_FIN_DRO,
                    "'{}'".format(r[param.DB_SDIS_ROAD_NUM_FIN_DRO]) if r[param.DB_SDIS_ROAD_NUM_FIN_DRO] is not None else "DEFAULT",
                    param.DB_SDIS_ROAD_SRC_NUM,
                    param.DB_SDIS_ROAD_SRC_NUM_NEOGEO_VALUE,
                    param.DB_SDIS_ROAD_ID,
                    r[param.DB_SDIS_ROAD_ID])

                # print(r[param.DB_SDIS_ROAD_NUM_DEB_GAU])
                # print(sql)

                with self.db_connection.cursor() as cur:
                    cur.execute(sql)

        self.db_connection.commit()

    def update_one_way_with_rivoli(self, insee, ban_table_name, rivoli):
        # On récupère les tronçons et les points correspondants
        # On associe chaque point adresse à un tronçon unique

        # Structures de données temporaire pour gérer les relations entre tronçons
        # et points adresse
        segments_related_to_address_points = {}
        address_points_data = {}

        # Récupération de tous les points adresses associés et création d'une géométrie multipoint
        # pour l'ensemble de ces points
        addr_points = utils.get_all_adp_for_way(self.db_connection, insee, ban_table_name, rivoli)
        # print(addr_points)
        # print(u"Nombre de points adresse : {0} - {1} - {2}".format(insee, rivoli, len(addr_points)))
        if len(addr_points) == 0:
            # TODO : à mettre dans les logs
            #             print(u"Erreur : aucun point récupéré pour la commune et le code Rivoli")
            #             print(u"Commune : {0} - Code fantoir : {1} - Schema : {2} - Table : {3}".format(
            #                 insee, rivoli, param.DB_SCHEMA, ban_table_name))
            return

        # Récupération de tous les tronçons de voies correspondant à ce code rivoli
        road_segments = utils.get_all_segments_for_way_with_rivoli(self.db_connection, insee, rivoli)
        # print(u"Nombre de tronçons de voies : {0} - {1} - {2}".format(insee, rivoli, len(road_segments)))

        if len(road_segments) > 0:
            self.update_road_segments_with_adps(road_segments=road_segments, addr_points=addr_points)
        else:
            # TODO: insérer cet évènement dans les logs
            pass

    # Cette fonction se base sur la géométrie des points adresse et le nom de la voie pour essayer d'associer les bons
    # tronçons.
    # Cette fonction retourne un booléen indiquant si l'association entre les points adresse et les tronçon a pu être
    # fait. Ainsi si l'association n'a pas pu être faite il sera possible de la faire sans se baser sur le nom de voie.
    def update_one_way_with_name_and_no_rivoli(self, insee, ban_table_name, rivoli, way_name):

        # Valeur False indique que la fonction n'a pas mis à jour de tronçons
        # True indique que des tronçons ont été mis à jour
        result = False

        # Structures de données temporaire pour gérer les relations entre tronçons et points adresse
        road_segments = {}
        adps = {}

        # Recherche des points BAN associés au code Rivoli
        # et création d'une géométrie multipoint
        # pour l'ensemble de ces points
        adps = utils.get_all_adp_for_way(
            db_connection=self.db_connection, insee=insee, ban_table_name=ban_table_name, rivoli=rivoli)
        if len(adps) == 0:
            # TODO : à mettre dans les logs
            print(u"  Erreur : aucun point récupéré pour la commune et le code rivoli")
            print(u"  Commune : {0} - Code fantoir : {1}".format(insee, rivoli))
            return

        # Création d'une géométrie multipoints pour l'ensemble des points adresse
        adps_geoms = [adp["shapely_geom"] for adp in adps]
        adps_geom = shapely.ops.unary_union(adps_geoms)
        wkt_geom = adps_geom.wkt
        # print(adps_geom)

        # Recherche des tronçons possibles
        result_names = set()

        max_dist = param.MAX_DIST_WITH_NAME
        leven_dist_max = max(5, int(len(way_name)/5))

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
                """.format(name_field, 'count', 'length', way_name.upper().replace("'", "''"), 'leven_dist')

            individual_sql_selects = []
            for table_name in param.DB_ROAD_TABLES:
                individual_select = """
                    (SELECT {0}, {1}, ST_Length({2}) as length
                        FROM {3}.{4}
                        WHERE {1} IS NOT NULL
                            AND ST_Distance({2}, ST_GeomFromText('{5}', 27572)) < {6})
                    """.format(param.DB_SDIS_ROAD_INSEE, name_field, param.DB_SDIS_ROAD_GEOM,
                           param.DB_SCHEMA, table_name, wkt_geom, max_dist)
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
                final_records = []

                if len(records) > 0:
                    least_leven_dist = min([r['leven_dist'] for r in records])
                    if least_leven_dist < len(way_name) and least_leven_dist < leven_dist_max:
                        possible_records = [r for r in records if r['leven_dist'] == least_leven_dist]

                    if len(possible_records) == 1:
                        final_records = possible_records

                    elif len(possible_records) > 1:
                        max_length = max([r['length'] for r in possible_records])
                        final_records = [r for r in possible_records if r['length'] == max_length]

                    if len(final_records) > 0:
                        for r in final_records:
                            result_names.add(r[0].decode("utf-8"))

        for sdis_way_name in result_names:
            result = True
            road_segments = utils.get_all_segments_for_way_with_name(
                db_connection=self.db_connection, insee=insee, way_name=sdis_way_name, )
            # print(len(road_segments))
            # print(len(adps))

            # Affectation des points adresse aux tronçons
            self.update_road_segments_with_adps(road_segments=road_segments, addr_points=adps)

        return result

    def find_and_update_closest_segments(self, insee, ban_table_name, rivoli):

        # Structures de données temporaire pour gérer les relations entre tronçons et points adresse
        road_segments = {}
        adps = {}

        # Recherche des points BAN associés au code Rivoli
        # et création d'une géométrie multipoint
        # pour l'ensemble de ces points
        adps = utils.get_all_adp_for_way(
            db_connection=self.db_connection, insee=insee, ban_table_name=ban_table_name, rivoli=rivoli)
        if len(adps) == 0:
            # TODO : à mettre dans les logs
            print(u"  Erreur : aucun point récupéré pour la commune et le code rivoli")
            print(u"  Commune : {0} - Code fantoir : {1}".format(insee, rivoli))
            return

        # Création d'une géométrie multipoints pour l'ensemble des points adresse
        adps_geoms = [adp["shapely_geom"] for adp in adps]
        adps_geom = shapely.ops.unary_union(adps_geoms)
        wkt_geom = adps_geom.wkt

        # Récupération des tronçons situés à proximité de la géométrie
        # Pour assurer une certaine continuité seuls les tronçons portant un nom sont récupérés
        # Les résultats sont groupés par nom de voie
        # Les plus grands ensembles de voies portant le même nom sont recherchés
        # Si des ensembles de voies de longueurs similaires sont détectés la proximité orthographique est étudiée

        max_dist = param.MAX_DIST_WITH_NO_NAME

        individual_sql_selects = []
        for table_name in param.DB_ROAD_TABLES:
            individual_select = """
                (SELECT {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, ST_AsText({9}) AS geom, '{10}' AS table_name
                    FROM {12}.{10}
                    WHERE {1} = '{11}'
                        AND {7} IS NULL
                        AND ST_Distance({9}, ST_GeomFromText('{13}', 27572)) < {14})
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
                           table_name,
                           insee,
                           param.DB_SCHEMA,
                           wkt_geom,
                           max_dist)
            individual_sql_selects.append(individual_select)

        sql = u"\nUNION\n".join(individual_sql_selects)

        with self.db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(sql)
            records = cur.fetchall()

            col_names = [desc[0] for desc in cur.description]

            for r in records:
                segment = {col_name: r[col_name] for col_name in col_names}
                segment["shapely_geom"] = shapely.wkt.loads(segment["geom"])
                # Liste des points adresse associés au tronçon de voie (liste vide à son initialisation ici)
                segment["adps"] = []
                road_segments[segment[param.DB_SDIS_ROAD_ID]] = segment

        # Affectation des points adresse aux tronçons
        if len(road_segments) > 0:
            self.update_road_segments_with_adps(road_segments=road_segments, addr_points=adps)

    def update_one_city(self, insee, ban_or_bano="ban"):

        time1 = time.time()

        if ban_or_bano == "ban":
            ban_table_name = param.DB_BAN_TABLE
        elif ban_or_bano == "bano":
            ban_table_name = param.DB_BANO_TABLE

        # On récupère l'ensemble des noms de voie du réseau SDIS et des codes fantoir associés
        # On constitue 2 listes :
        # - une liste des voies avec code fantoir unique
        # - une liste des autres voies
        # A chaque fois qu'un de ces noms de voie est traité on le retire de la liste à traiter

        # Liste des codes fantoir identifié sur les tronçons de la commune
        known_rivoli_codes = utils.get_known_rivoli_codes_for_city(self.db_connection, insee)
        # print(known_rivoli_codes)
        # print(u"Codes fantoir identifiés sur les tronçons des voies de la base SDIS de la commune {0} : {1}".format(
        #     insee, ", ".join(known_rivoli_codes)))

        # Récupération d'un dictionaire des noms de voies issues de la BAN / BANO pour la commune
        #   clef : code Fantoir
        #   valeur : nom de la voie
        ban_way_dict_for_city = utils.get_ban_way_dict_for_city(
            db_connection=self.db_connection, insee=insee, ban_table_name=ban_table_name, max_nb_roads=None)
        # print(u"Nombre de voies de la BAN/BANO pour la commune {0} : {1}".format(insee, len(ban_way_dict_for_city)))

        # Dictionnaire des voies issues de la BAN/BANO sur cette commune et dont les codes fantoir ne correspondent pas
        # aux codes fantoir trouvés sur les tronçons de la commune
        ban_way_dict_for_city_with_no_fantoir = {}
        for key, value in ban_way_dict_for_city.iteritems():
            if key not in known_rivoli_codes:
                ban_way_dict_for_city_with_no_fantoir[key] = value
        # TODO : mettre ce dictionnaire dans les logs

        # print(ban_way_dict_for_city_with_no_fantoir)

        # On traite d'abord les voies avec code fantoir unique
        print(u"  Traitements des voies dont le code Rivoli est renseigné dans la base...")
        # Pour chaque voie...
        for rivoli in known_rivoli_codes:
            # ... on cherche les bons numéros de voie
            print(u"    Code Rivoli: {}".format(rivoli))
            self.update_one_way_with_rivoli(insee=insee, ban_table_name=ban_table_name, rivoli=rivoli)

        # On traite ensuite les points adresses de la commune qui n'ont pas été traités dans l'étape précédente
        # On récupère tous les codes Rivoli des points adresses de la commune qui ne sont pas dans la liste des codes
        # Rivoli précédemment traités
        all_rivoli_codes = utils.get_rivoli_codes_for_city_from_ban(
            db_connection=self.db_connection, insee=insee, ban_table_name=ban_table_name)

        remaining_rivoli_codes = list(set(all_rivoli_codes)-set(known_rivoli_codes))
        remaining_rivoli_codes_2 = list()

        # Pour chaque code Rivoli non déjà traité...
        print(u"  Traitements des voies dont le code Rivoli n'est pas renseigné dans la base...")
        for rivoli in remaining_rivoli_codes:

            # Récupération du nom de la voie correspondant au code Rivoli
            # On ne peut pas se baser sur le nom Afnor car il n'est pas disponible pour la BANO
            # Utilisation du nom de voie avec accents et minuscules par conséquent
            way_names = utils.get_way_names_from_rivoli_code_from_ban(
                db_connection=self.db_connection,
                ban_table_name=ban_table_name,
                insee=insee,
                rivoli=rivoli)

            # On traite différemment les cas suivants :
            # - un nom est présent
            # - plus d'un nom est présent
            # - aucun nom n'est présent
            # Si plus d'un nom est présent alors on fait comme si aucun nom n'est présent
            # On se base alors uniquement sur les géométries pour identifier les bons tronçons à associer aux
            # points adresse.

            # TODO : si plusieurs noms de voie sont associés à un même code Rivoli on émet une alerte dans la
            # table des logs

            if len(way_names) == 0:
                remaining_rivoli_codes_2.append(rivoli)
            elif len(way_names) > 1:
                remaining_rivoli_codes_2.append(rivoli)
            else:
                way_name = way_names[0].decode("utf-8")
                print(u"    Code Rivoli: {} - Nom de voie : {}".format(rivoli, way_name))

                # ... on cherche les bons segments de voies correspondant aux points adresse
                segments_updated = self.update_one_way_with_name_and_no_rivoli(
                    insee=insee, ban_table_name=ban_table_name, rivoli=rivoli, way_name=way_name)

                if not segments_updated:
                    remaining_rivoli_codes_2.append(rivoli)

        # Traitement des codes Rivoli non encore traités par simple recherche géographique locale
        for rivoli in remaining_rivoli_codes_2:
            self.find_and_update_closest_segments(insee=insee, ban_table_name=ban_table_name, rivoli=rivoli)

        result_dict = {}

        time9 = time.time()
        # print(u"update : {}".format(time6-time5))

        click.echo(u"  temps de traitement pour {} : {} s".format(insee, time9 - time1))

    def update(self, ban_or_bano="ban"):
        insee_codes = utils.get_all_city_insee(self.db_connection)

        click.echo(u"Nombre de communes à traiter : {}".format(len(insee_codes)))
        for insee in insee_codes:
            click.echo(u"Traitement de la commune : {}".format(insee))
            self.update_one_city(insee, ban_or_bano=ban_or_bano)

    def get_stats_for_one_city(self, insee, verbose=False):

        # Suppression des logs sur les adresses pour cette commune
        utils.clear_records_in_log(
            db_connection=self.db_connection,
            table=param.DB_BAN_LOG_L_TABLE,
            insee=insee,
            error_codes=(20,))

        # Identification des voies sans numéros par type de voies
        for table in param.DB_ROAD_TABLES:
            stats = utils.get_stats_for_named_ways(db_connection=self.db_connection, insee=insee, table_name=table)

            nb_all_ways = stats["nb_of_named_ways"]
            nb_ways_with_no_numbers = stats["nb_of_named_ways_with_no_numbers"]
            ways_with_no_numbers = stats["ways_with_no_numbers"]
            wkt_geometries = stats["wkt_geometries"]

            if nb_all_ways > 0:
                nb_ways_with_no_address_percentage = float(nb_ways_with_no_numbers)/float(nb_all_ways)
                print(u"  Nombre de voies nommées de la table {} sans adresse : {} ({:.1%})".format(
                    table, nb_ways_with_no_numbers, nb_ways_with_no_address_percentage))
                if verbose  and len(ways_with_no_numbers) > 0:
                    print(u"  Voies nommées sans adresses de la table {} :".format(table))
                    for way in ways_with_no_numbers:
                        print(u"    {}".format(way))

                # Insertion de logs dans la table des linéaires
                if len(ways_with_no_numbers) > 0:
                    utils.insert_records_in_log(
                        db_connection=self.db_connection,
                        table=param.DB_BAN_LOG_L_TABLE,
                        insee=insee,
                        message=u"voie nommée sans adresse",
                        error_code=20,
                        geometries=wkt_geometries
                    )


    def get_stats(self, verbose=False):
        insee_codes = utils.get_all_city_insee(self.db_connection)

        click.echo(u"Nombre de communes à traiter : {}".format(len(insee_codes)))
        for insee in insee_codes:
            click.echo(u"Traitement de la commune : {}".format(insee))
            self.get_stats_for_one_city(insee, verbose=verbose)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('insee', nargs=-1)
@click.option('-v', '--verbose', is_flag=True, default=False)
def stats(insee, verbose):
    """Calcul de statistiques sur les adresses.

Cette commande analyse les numéros adresse asscoiés aux voies de la base de données.

\b
Exemples :
- Affichage de l'aide sur cette commande :
    python adresses.py stats --help
- Calcul de statistiques sur les adresses d'une commune (en mode non verbeux par défaut) :
    python adresses.py stats 33316
- Calcul de statistiques sur les adresses d'une commune en mode verbeux :
    python adresses.py stats --verbose 33316
    python adresses.py stats -v 33316
- Calcul de statistiques sur les adresses de 2 communes :
    python adresses.py stats 33316 33424
- Calcul de statistiques sur les adresses de toutes les communes :
    python adresses.py stats"""

    click.echo(u"Calcul de statistiques sur les numéros adresse...")

    # search fantoir codes for one city
    updater = NumbersUpdater()

    if len(insee) == 0:
        click.echo(u"Aucun code INSEE spécifié. Si vous continuez, toutes les communes du département seront traitées.")
        if click.confirm(u"Voulez-vous continuer ?"):
            click.echo(u"Traitement lancé sur l'ensemble des codes INSEE de la base.")
            updater.get_stats(verbose=verbose)
        else:
            click.echo(u"Traitement annulé.")
    else:
        for i in insee:
            click.echo(u"Traitement de la commune : {}".format(i))
            updater.get_stats_for_one_city(i, verbose=verbose)


@cli.command()
@click.option('--ban-or-bano', default='ban', type=click.Choice(['ban', 'bano']))
@click.argument('insee', nargs=-1)
def update(insee, ban_or_bano):
    """Mise à jour des numéros d'adresse des tronçons de voie de la base de données routière à partir des points adresse
    présents dans la BAN ou la BANO. Par défaut, l'opération utilise les données de la BAN.

\b
Exemples :
- Affichage de l'aide sur cette commande :
    python adresses.py update --help
- Mise à jour des numéros de rue d'une commune :
    python adresses.py update 33316
- Mise à jour des numéros de rue de 2 communes :
    python adresses.py update 33316 33424
- Mise à jour des numéros de rue de toutes les communes :
    python adresses.py update
- Mise à jour des des numéros de rue d'une commune en utilisant à partie de la BANO :
    python adresses.py update --ban-or-bano bano 33316"""

    click.echo(u"Mise à jour des numéros de rue du réseau routier à partir des données BAN ou BANO...")

    updater = NumbersUpdater()

    if len(insee) == 0:
        click.echo(u"Aucun code INSEE spécifié.")
        click.echo(u"L'ensemble des codes INSEE de la base seront traités. Le temps de traitement peut durer plusieurs heures.")
        if click.confirm(u"Voulez-vous continuer ?"):
            click.echo(u"Traitement lancé sur l'ensemble des codes INSEE de la base.")
            updater.update(ban_or_bano=ban_or_bano)
        else:
            click.echo(u"Traitement annulé.")
    else:
        for i in insee:
            click.echo(u"Traitement de la commune : {}".format(i))
            updater.clear_adresses_for_one_city(i)
            updater.update_one_city(i, ban_or_bano=ban_or_bano)


@cli.command()
@click.argument('insee', nargs=-1)
def clear(insee):
    """Suppression des numéros d'adresse renseignés automatiquement.

\b
Exemples :
- Affichage de l'aide sur cette commande :
    python adresses.py clear --help
- Suppression des adresses d'une commune :
    python adresses.py clear 33316
- Suppression des adresses de 2 communes :
    python adresses.py clear 33316 33424
- Suppression des adresses de toutes les communes :
    python adresses.py clear"""

    click.echo(u"Supression des adresses du réseau routier...")

    updater = NumbersUpdater()

    if len(insee) == 0:
        click.echo(u"Aucun code INSEE spécifié.")
        click.echo(u"L'ensemble des codes INSEE de la base seront traités.")
        if click.confirm(u"Voulez-vous continuer ?"):
            click.echo(u"Traitement lancé sur l'ensemble des codes INSEE de la base.")
            updater.clear_adresses()
        else:
            click.echo(u"Traitement annulé.")
    else:
        for i in insee:
            click.echo(u"Traitement de la commune : {}".format(i))
            updater.clear_adresses_for_one_city(i)

if __name__ == '__main__':
    cli()
