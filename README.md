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
* Exploiter les base de données Fantoir, BAN et BANO pour alimenter les tronçons de la base de données routière avec 
les codes Rivoli. Cette opération est réalisée à l'aide du script python suivant : source/update_ways_fantoir.sql.

D'autres outils viendront les compléter pour atteindre l'objectif final identifier plus haut.

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
4. Installer les modules nécessaire au fonctionnement des scripts :
pip install -r source/requirements.txt

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

Un paramètre numérique est utilisé par l'algorithme mis en place pour rechercher les codes Rivoli utilisés dans la BAN 
et la BANO :
* MAX_DIST : distance maximum en mètres (300 est une valeur fonctionnant plutôt bien) utilisée pour recherche les 
tronçons routiers de la base de données qui pourraient correspondre aux points adresse de la BAN et de la BANO.

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

## Données externes

### Fantoir
Les données Fantoir sont mises à disposition de manière régulière par Région et par Département à l'emplacement suivant
 :
https://www.collectivites-locales.gouv.fr/mise-a-disposition-gratuite-fichier-des-voies-et-des-lieux-dits-fantoir

Chaque région fait l'objet d'un fichier zip contenant un fichier txt par Département.

Un fichier complet pour l'ensemble du territoire national est disponible également ici mais il faudrait le subdiviser 
pour n'en exploiter que les données du département de la Gironde. Nous ne vous recommandons donc pas de l'exploiter en 
l'état.

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
* Script : update_ways_fantoir.py
* Commande : load_fantoir
* Paramètre : chemin du fichier Fantoir à charger
* Options : aucune

Exemple : python update_ways_fantoir.py load_fantoir ../data/fantoir/nouvelle_aquitaine/330.txt

Remarques :
* Ce script vide complètement la table fantoir avant de la remplir.
* Ce script n'a aucun impact sur les autres tables.

### Mise à jour des codes Rivoli du réseau routier en base
* Script : update_ways_fantoir.py
* Commande : update_rivoli
* Paramètre : codes INSEE des communes à traiter (codes séparés par des virgules)
* Options :
  * --ban : recherche également les codes rivoli utilisés dans la BAN
  * --bano : recherche également les codes rivoli utilisés dans la BANO

Exemples :
- Affichage de l'aide sur cette commande :
    python update_ways_fantoir.py update_rivoli --help
- Mise à jour des codes rivoli d'une commune :
    python update_ways_fantoir.py update_rivoli 33316
- Mise à jour des codes rivoli de 2 communes :
    python update_ways_fantoir.py update_rivoli 33316 33424
- Mise à jour des codes rivoli de toutes les communes :
    python update_ways_fantoir.py update_rivoli
- Mise à jour des codes rivoli d'une commune en utilisant en plus la BAN :
    python update_ways_fantoir.py update_rivoli --ban 33316
- Mise à jour des codes rivoli d'une commune en utilisant en plus la BANO :
    python update_ways_fantoir.py update_rivoli --bano 33316

Les deux options --ban et --bano augmentent considérablement le temps de traitement sans réelle plus-value aujourd'hui 
car l'algorithme d'association des codes Rivoli utilisé pour la BAN et la BANO semble moins performant que celui que 
nous utilisons. Mais le renseignement des codes Rivoli dans les bases BAN et bANO pourrait s'améliorer à l'avenir.

Nous recommandons donc d'utiliser ces options lorsque la BAN et la BANO seront améliorées pour un utisage ponctuel sur 
un nombre de communes limité lorsque l'utilisation du script donne des résultats médiocres sur celles-ci.

Ce script ne modifie que les tables du réseau routier.

Ce script insère dans les tables du réseau routier deux nouvelles informations :
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
