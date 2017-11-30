# sdis33_ban
Intégration des adresses de la BAN dans la base de données routière du SDIS 33

## Objectifs
L'objectif des outils fournis est le suivant :
* Mettre à jour les numéros d'adresse associés à chaque tronçon de la base de données 
routière maintenue par le SDIS 33.

En l'état actuel, les outils fournis couvrent les besoins suivants :
* Intégrer la base de données Fantoir dans la base de données PostgreSQL. Cette opération est réalisée à l'aide du 
script python suivant : source/update_ways_fantoir.sql ;
* Intégrer les bases de données BAN et BANO dans la base de données PostgreSQL/PostGIS. Cette opération est réalisée à 
l'aide des scripts SQL suivants : sql/import_ban_table.sql et sql/import_ban_table.sql ;
* Alimenter les tronçons de la base de données routière avec les codes Rivoli (à l'aide des bases Fantoir, BAN et BANO).
Cette opération est réalisée à l'aide du script python source/rivoli.py et de sa commande update.
* Alimenter les tronçons de la base de données routière avec les numéros d'adresse (à l'aide des bases BAN et BANO). 
Cette opération est réalisée à l'aide du script python source/adresses.py et de sa commande update.
* Extraire de la base de données des statistiques sur la qualité des traitements et alimenter des couches de données
vectorielles correspondant aux anomalies. Ces opérations sont réalisées à l'aide des scripts source/rivoli.py et 
source/adresses.py et de leur commande stats.
* Identifier les principales différences entre deux millésimes de la base de données Fantoir. Cette opération est 
réalisée à l'aide du script source/rivoli.py et de sa commande diff_fantoir.

## Installation et configuration

### Installation des scripts Python
Prérequis :
* Python
* Pip (gestionnaire de modules pour Python)

Procédure d'installation :
1. Copier le répertoires source à l'emplacement souhaité
2. Installer virtualenv si ce n'est pas déjà le cas : pip install virtualenv
3. Créer un environnement Python avec vitualenv : virtualenv venv
4. Activer cet environnement Python : source venv/bin/activate
4. Installer les modules nécessaires au fonctionnement des scripts :
pip install -r source/requirements.txt

En cas d'installation sous Windows, certains modules peuvent nécessiter une procédure particulière :
* pour shapely se référer à https://github.com/Toblerity/Shapely#built-distributions

### Configuration des scripts Python
Le paramétrage des scripts Python doit être réalisé à l'aide d'un fichier source/param.py.

1. Copier le fichier source/param_template.py pour créer un fichier param.py au même emplacement que le fichier 
param_template.py.
2. Modifier les valeurs des paramètres dans le fichier param.py pour correspondre à votre configuration. En particulier 
:
* DB_HOST : le nom du serveur PostgreSQL où est stockée la base à manipuler
* DB_PORT : le port réseau utilisé par PostgreSQL
* DB_NAME : le nom de la base de données
* DB_USER : un nom d'utilisateur déclaré dans la base PostgreSQL ayant les droits d'écriture sur les tables du réseau 
routier et sur les nouvelles 
tables créés (tables pour les données Fantoir, BAN et BANO)
* DB_PWD : mot de passe de l'utilisateur défini par DB_USER
* DB_SCHEMA : le nom du schéma qui contient les tables à manipuler
* DB_SDIS_ROAD_NAMES : la liste des champs des tables du réseau routier qui contiennent un nom à exploiter sous la 
forme d'une liste Pyhton. Par exemple : ["nom_origine", "nom_2", "nom_3", "nom_4"]. Plus cette liste est longue plus 
les traitements sont longs.

Les catégories de voies de la base Fantoir exploitées par les scripts sont définies dans le paramètre suivant :
* FANTOIR_USED_WAY_TYPES = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'X', 'Y', 'Z')

Des paramètres numériques sont utilisés par les algorithmes mis en place pour rechercher les codes Rivoli utilisés dans 
la BAN et la BANO :
* MAX_DIST : distance maximum en mètres (300 est une valeur fonctionnant plutôt bien) utilisée pour recherche les 
tronçons routiers de la base de données qui pourraient correspondre aux points adresse de la BAN et de la BANO.
* MAX_DIST_WITH_NO_NAME : distance maximum en mètres (10 est une valeur qui fonctionne assez bien) d'appariement d'un 
point adresse à une voie lorsque l'appariement par code Rivoli ou par le nom n'a pas donné de résultat. Cet 
appariement (purement géométrique) n'est réalisé que lorsqu'aucun autre appariement n'a donné aucun résultat. Il est 
donc important de donner à ce paramètre une valeur beaucoup plus faible que pour MAX_DIST.
* DROITE_GAUCHE_DIST : distance minimum en mètres (2 est une valeur fonctionnant plutôt bien) utilisée pour déterminer 
si un point adresse est situé à gauche ou à droite de la voie. Si le point adresse est situé à une distance inférieure à
ce seuil l'algorithme considère qu'il ne peut pas déterminer s'il est situé à droite ou à gauche de la voie. Sa 
localisation est donc indéterminée lorsque la distance à la voie est trop faible.

### Module fuzzystrmatch de PostgreSQL
Les scripts utilisent la mesure de distance de Levenshtein pour comparer des chaînes de caractères. Cette mesure est 
fournie par la fonction Levenshtein du module fuzzystrmatch 
(cf. https://www.postgresql.org/docs/current/static/fuzzystrmatch.html).

Il convient donc d'activer ce module dans la base de données avant toute utilisation des scripts :

CREATE EXTENSION fuzzystrmatch
  SCHEMA public
  VERSION "1.0";

### Schéma de la base de données
Afin de pouvoir réaliser des tests en toute sécurité, il est préférable de travailler sur un nouveau schéma de la base 
de données dans lequel une copie de la base de données routière est réalisée.

Une partie scripts SQL livrés dans le répertoire sql utilisent un schéma "neogeo" a cet effet.

Pour la mise en place d'une copie des données routières dans le schéma neogeo (scripts à utiliser dans cet ordre) :
1. Création des tables du réseau routier dans le schéma neogeo : neogeo.rerou*.sql
2. Ajout de nouvelles colonnes dans ces tables : add_fields_to_neogeo.sql
3. Copie des données routières du schema gces vers le schéma neogeo : copy_data_to_neogeo_full.sql (pour l'ensemble des 
communes) et copy_data_to_neogeo_partial.sql (pour quelques communes)

Pour la création des nouvelles tables contenant les données Fantoir, de la BAN et de la BANO :
1. create_fantoir_table.sql
2. create_ban_table.sql
3. create_bano_table.sql

Pour l'alimentation des données BAN et BANO (les chemins des fichiers CSV à importer doivent être mis à jour de sorte à 
correspondre à l'emplacement de ces fichiers sur votre ordinateur/serveur) :
1. import_ban_data.sql
2. import_bano_data.sql

Pour la création des tables géographiques de log :
1. create_ban_log_p_table.sql
2. create_abn_log_l_table.sql 
La première table ne contient que des objets ponctuels (localisation de points adresse problématiques) 
alors que la seconde ne contient que des objets linéaires (voies problématiques).

Le champ code_erreur supporte pour les valeurs suivantes :
-    10 - code Rivoli de la base adresses non apparié à une voie
-    20 - voie nommée sans adresse

## Données externes

### Fantoir
Les données Fantoir sont mises à disposition de manière régulière par Région et par Département à l'emplacement suivant
 :
https://www.collectivites-locales.gouv.fr/mise-a-disposition-gratuite-fichier-des-voies-et-des-lieux-dits-fantoir

Chaque région fait l'objet d'un fichier zip contenant un fichier txt par Département.

Un fichier complet pour l'ensemble du territoire national est disponible également à l'adresse suivante avec une 
fréquence mensuelle : http://www.data.gouv.fr/fr/datasets/fichier-fantoir-des-voies-et-lieux-dits/

Ces 2 sources de données sont parfaitement exploitables.
Les scripts lisant ces fichiers ne retiennent que les lignes commençant par "330" (informations asscoiées à la Gironde).

### BAN
Les données de la BAN sont mises à jour quotidiennement sur le site de data.gouv.fr :
https://adresse.data.gouv.fr/data/

Chaque département y est disponible sous la forme d'une archive zip. Pour la Gironde :
https://adresse.data.gouv.fr/data/BAN_licence_gratuite_repartage_33.zip

Elle contient un fichier CSV avec les coordonnées de chaque point adresse. Le script sql/import_ban_data.sql importe 
ces données dans la base PostgreSQL/PostGIS et construit leurs géométries à partir de ces coordonnées.

### BANO
Les données de la BANO sont mises à jour quotidiennement sur le site d'OpenStreetMap France :
http://bano.openstreetmap.fr/BAN_odbl/

Vous devez utiliser l'archive de votre département au format CSV :
http://bano.openstreetmap.fr/BAN_odbl/BAN_odbl_33-csv.bz2

Le script sql/import_bano_data.sql importe ces données dans la base PostgreSQL/PostGIS et construit leurs géométries à 
partir de ces coordonnées.

## Usage

### Chargement des données de la BAN
* Script : sql/import_ban_data.sql

Remarques :
- ce script supprime les anciennes données de la table de la BAN
- il insère les nouvelles données dans cette table
- il calcule les géométrie de chaque point à partir des champs x et y présents dans le fichier CSV
- ce script n'a aucun impact sur les autres tables

### Chargement des données de la BANO
* Script : sql/import_bano_data.sql

Remarques :
- ce script supprime les anciennes données de la table de la BANO
- il insère les nouvelles données dans cette table
- il calcule les géométrie de chaque point à partir des champs x et y présents dans le fichier CSV
- ce script n'a aucun impact sur les autres tables

### Mise à jour de la table Fantoir dans la base
* Script : rivoli.py
* Commande : load_fantoir
* Paramètre : chemin du fichier Fantoir à charger
* Options : aucune

Exemple : python rivoli.py load_fantoir ../data/fantoir/nouvelle_aquitaine/330.txt

Remarques :
* Ce script vide complètement la table fantoir avant de la remplir.
* Ce script n'a aucun impact sur les autres tables.

### Comparaison de 2 fichiers Fantoir
* Script : rivoli.py
* Commande : diff_fantoir
* Paramètres : chemin des 2 fichiers Fantoir à comparer
* Options : aucune

Exemple : python rivoli.py diff_fantoir ../data/fantoir/FANTOIR0717 ../data/fantoir/FANTOIR1017

Remarques :
* Ce script n'a aucun effet sur la base de données.
* Il affiche les résultat de manière textuelle dans la console d'exécution.

### Mise à jour des codes Rivoli du réseau routier en base
* Script : rivoli.py
* Commande : update
* Paramètre : codes INSEE des communes à traiter (codes séparés par des espaces)
* Options :
  * --ban : recherche également les codes rivoli utilisés dans la BAN
  * --bano : recherche également les codes rivoli utilisés dans la BANO

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
    python rivoli.py update --bano 33316

Les deux options --ban et --bano augmentent considérablement le temps de traitement sans réelle plus-value aujourd'hui 
car l'algorithme d'association des codes Rivoli utilisé pour la BAN et la BANO semble moins performant que celui que 
nous utilisons. Mais le renseignement des codes Rivoli dans les bases BAN et BANO pourrait s'améliorer à l'avenir.

Nous recommandons donc d'utiliser ces options lorsque la BAN et la BANO seront améliorées pour un utisage ponctuel sur 
un nombre de communes limité lorsque l'utilisation du script donne des résultats médiocres sur celles-ci.

Ce script peut être extrèmement long à exécuter sur l'ensemble du département. Il est donc recommandé de l'exécuter
pour un sous-ensemble de communes.

Ce script ne modifie que les tables du réseau routier.

Ce script insère dans les tables du réseau routier les nouvelles informations suivantes :
* rivoli : liste des codes Rivoli de la commune qui correspondent le mieux au nom de la voie. Plusieurs valeurs peuvent 
être présentes dans le cas où une correspondance exacte des noms n'a pas pu être établie. Les valeurs sont alors 
séparées par des virgules.
* rivoli_dist : indicateur de la proximité orthographique entre le nom de la voie de la base routière et le nom de la 
voie dans la base Fantoir. La proximité orthographique est établie grâce à une mesure de la distance de Levenshtein. Une 
valeur de 0 représente une correspondance parfaite. Le remplacement d'un caractère par un autre induit par exemple une 
distance valant 2 (1 pour la suppression d'un caractère + 1 pour l'insertion d'un autre caractère). Plus la valeur est 
grande, moins la correspondance est bonne.  Contrairement au champ rivoli, le champ rivoli_dist n'est alimenté qu'avec 
une seule valeur car seuls sont retenus les codes Rivoli dont la distance orhtographique est la plus faible. Les codes 
Rivoli proposés ont donc la même distance de Levenshtein.
* src_rivoli : indique si le code Rivoli a été renseigné par le script (valeur "a" dans ce cas) ou non.

Les codes Rivoli renseignés automatiquement par le script sont marqués par la valeur "a" (pour "automatique") dans le 
champ src_rivoli. Les scripts ne peuvent pas modifier les valeurs des codes Rivoli si le champ﻿src_rivoli est renseigné 
avec une autre valeur que "a".


### Réinitialisation des codes Rivoli du réseau routier en base
* Script : rivoli.py
* Commande : clear
* Paramètre : codes INSEE des communes à traiter (codes séparés par des espaces)

Exemples :
  - Affichage de l'aide sur cette commande :
      python rivoli.py clear --help
  - Suppression des codes Rivoli d'une commune :
      python rivoli.py clear 33316
  - Suppression des codes Rivoli de 2 communes :
      python rivoli.py clear 33316 33424
  - Suppression des codes Rivoli de toutes les communes :
      python rivoli.py clear

Seuls les codes Rivoli renseignés par les scripts sont modifiés. Les codes Rivoli renseignés automatiquement par le script sont marqués par la valeur "a" (pour "automatique") dans le 
champ src_rivoli. Les scripts ne peuvent pas modifier les valeurs des codes Rivoli si le champ﻿src_rivoli est renseigné 
avec une autre valeur que "a".

### Test de la qualité de l'intégration des codes Rivoli dans le réseau routier en base
* Script : rivoli.py
* Commande : stats
* Paramètre : codes INSEE des communes à traiter (codes séparés par des espaces)
* Options :
  * --ban-or-bano : indique si les tests doivent être réalisés en utilisant la BAN ou la BANO (BAN par défaut)
  * --verbose ou -v : exécution du script en mode verbeux (affichage des codes Rivoli et des noms de voies de la base
  adresses qui n'ont pas pu être associés à des tronçons routiers)

Exemples :
- Affichage de l'aide sur cette commande :
  python rivoli.py stats --help
- Calcul de statistiques sur les codes rivoli d'une commune (en mode non verbeux par défaut) :
  python rivoli.py stats 33316
- Calcul de statistiques sur les codes rivoli d'une commune en mode verbeux :
  python rivoli.py stats --verbose 33316
  python rivoli.py stats -v 33316
- Calcul de statistiques sur les codes rivoli de 2 communes :
  python rivoli.py stats 33316 33424
- Calcul de statistiques sur les codes rivoli de toutes les communes :
  python rivoli.py stats
- Calcul de statistiques sur les codes rivoli d'une commune en utilisant en plus la BAN :
  python rivoli.py stats --ban 33316
- Calcul de statistiques sur les codes rivoli d'une commune en utilisant en plus la BANO :
  python rivoli.py stats --bano 33316

Ce script peut être extrèmement long à exécuter sur l'ensemble du département. Il est donc recommandé de l'exécuter
pour un sous-ensemble de communes.

Les deux options --ban et --bano permettent d'indiquer à la quelle base adresse les codes Rivoli présents dans la base
de données routières doivent être comparés. Par défaut, cette comparaison est réalisée par rapport à la BAN.

Ce script ne modifie que les tables de log : un objet ponctuel est créé dans ces logs pour tous les points adresse dont
le code Rivoli n'a pas été associé à des tronçons du réseau routier.

Lorsque ce script est exécuté les précédents enregistrements dans les tables des logs pour cette commune et pour ce type
de tests sont effacés. Pour une commune donnée, il ne peut donc pas y avoir de cohabitation en base de résultats de
tests réalisés à des dates différentes.

### Mise à jour des numéros d'adresse du réseau routier en base
* Script : adresses.py
* Commande : update
* Paramètre : codes INSEE des communes à traiter (codes séparés par des espaces)
* Options :
  * --ban-or-bano : indique quelle base adresses utiliser (par défaut l'outil utilise la BAN)

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
      python adresses.py update --ban-or-bano bano 33316

Ce script peut être extrèmement long à exécuter sur l'ensemble du département. Il est donc recommandé de l'exécuter
pour un sous-ensemble de communes : 6 min pour Pellegrue et 1h30 pour Bordeaux par exemple

Ce script ne modifie que les tables du réseau routier.

Ce script insère dans les tables du réseau routier les informations suivantes :
* ﻿num_deb_gau : numéro au début du tronçon à gauche. Une chaîne de caractères contenant éventuellement une information
complémentaire telle que "BIS", "TER", "T"...
* num_deb_dro : idem pour le début et le côté droit du tronçon.
* num_fin_gau : idem pour la fin et le côté gauche du tronçon.
* num_fin_dro : idem pour la fin et le côté droit du tronçon.
* src_num : indique comment les numéro ont été renseignés. Les scripts utilisent la valeur "a" (pour "automatique").

Le champ cote_impair n'est pas renseigné par les scripts mais peut l'être par l'administrateur de la base de données
pour aider le script à affecter les numéros d'adresse aux bons côtés des tronçons. La valeur "g" spécifie que les 
numéros impairs sont tous localisés su côté gauche du tronçon. La valeur "d" indique que les numéros impairs de ce
tronçon sont tous localisés à droite. Le renseignement de ce champ peut améliorer l'identification de localisation
des numéros d'adresse pour les tronçons qui ont les caractéristiques suivantes :
- les numéros d'adresse pairs et impairs sont répartis de part et d'autre du tronçon
- les précisions de localisation des points adresse et de l'axe de la voie ne sont pas suffisantes pour déterminer de
manière automatique de quel côté les points adresse sont localisés.

Les numéros d'adresse renseignés automatiquement par le script sont marqués par la valeur "a" (pour "automatique") dans le 
champ src_num. Les scripts ne peuvent pas modifier les valeurs des numéros adresse si le src_num est renseigné 
avec une autre valeur que "a".

Un numéro d'adresse ne peut pas être présent sur plus d'un tronçon. Lorsqu'un numéro est localisé à proximité de 2
tronçons d'une même voie, il est affecté au tronçon le plus proche.

Pour déterminer les numéros de début et de fin d'un tronçon, deux procédures différentes sont utilisées en fonction
des configurations :
- si les numéros se succèdent le long du tronçon de manière globalement croissante ou décroissant, sont affectés aux 
extrémités du tronçon les plus petits et les plus grands numéros
- si l'algorithme précédent n'arrive pas à identifier un ordre croissant ou décroissant, ce sont les numéros localisés 
au plus près (en utilisant leurs abscisses curvilignes par rapport au tronçon et non leur distance cartésienne) des 
extrémités qui sont retenus.

### Réinitialisation des numéros d'adresse du réseau routier en base
* Script : adresses.py
* Commande : clear
* Paramètre : codes INSEE des communes à traiter (codes séparés par des espaces)

Exemples :
- Affichage de l'aide sur cette commande :
  python adresses.py clear --help
- Suppression des adresses d'une commune :
  python adresses.py clear 33316
- Suppression des adresses de 2 communes :
  python adresses.py clear 33316 33424
- Suppression des adresses de toutes les communes :
  python adresses.py clear

Seuls les numéros d'adresse renseignés par les scripts sont modifiés. Les numéros d'adresse renseignés automatiquement 
par le script sont marqués par la valeur "a" (pour "automatique") dans le champ src_num. Les scripts ne peuvent pas 
modifier les valeurs des numéros d'adresse si le src_num est renseigné avec une autre valeur que "a".

### Test de la qualité de l'intégration des numéros d'adresse dans le réseau routier en base
* Script : adresses.py
* Commande : stats
* Paramètre : codes INSEE des communes à traiter (codes séparés par des espaces)
* Options :
  * --verbose ou -v : exécution du script en mode verbeux (affichage des voies nommées ne portant pas de numéros
  d'adresse)

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
  python adresses.py stats


Ce script peut être extrèmement long à exécuter sur l'ensemble du département. Il est donc recommandé de l'exécuter
pour un sous-ensemble de communes.

Les deux options --ban et --bano permettent d'indiquer à la quelle base adresse les codes Rivoli présents dans la base
de données routières doivent être comparés. Par défaut, cette comparaison est réalisée par rapport à la BAN.

Ce script ne modifie que les tables de log : un objet linéaire est créé dans ces logs pour toutes les voies nommées ne
portant pas de numéros d'adresse.

Lorsque ce script est exécuté les précédents enregistrements dans les tables des logs pour cette commune et pour ce type
de tests sont effacés. Pour une commune donnée, il ne peut donc pas y avoir de cohabitation en base de résultats de
tests réalisés à des dates différentes.
