# Modèle de données

## Modèle de données initial
### Tables du réseau routier
    Schema : gces
    Tables :
        "rerouprima_l" -> routes primaires
        "rerousecon_l" -> routes secondaires
        "rerouterti_l" -> routes tertiaires
        "rerouquate_l" -> routes quaternaires
        "rerouauacc_l" -> autres accès carrossables
        "rerouvonoc_l" -> voies non carrossables ?

### Code INSEE
    Champs codes insee :
        commune_insee
        inseecom_d character varying(255),
        inseecom_g character varying(255),
    Les 2 derniers champs ne sont jamais renseignés

### Noms des voies
    Champs contenant des noms de voies :
        nom character varying(255),
        nom_2 character varying(255),
        nom_3 character varying(255),
        nom_4 character varying(255),
        nom_iti character varying(255),
        nom_origine character varying(255),
    Champs exploités par défaut par le programme : ["nom_origine", "nom_2", "nom_3", "nom_4"]


## Modifications du modèle de données
### Champs ajoutés aux tables des tronçons :

* Code Rivoli :
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
  * src_rivoli : Mode de renseignement du code Rivoli :
    * NULL : non renseigné/inconnu (uniquement si les champs rivoli... n'ont pas été renseignés)
    * a : automatique (renseignement effectué par les outils développés par Neogeo)
    * m : manuel (renseignement réalisé sur la base d'informations recueillies de diverses manières et saisies
manuellement dans la base)

* nom_fantoir_autre : champ destiné à recevoir le nom d'un lieux-dit, d'un ensemble immobilier ou d'une pseudo-voie
telle que définie dans la base Fantoir

* Numéros en début et fin de tronçon. Les numéros sont renseignés uniquement lorsque le niveau de certitude à leur 
sujet est maximal. Quatre champs sont utilisés :
  * num_deb_gau : numéro au début et à gauche du tronçon.
  * num_deb_dro : numéro au début et à droite du tronçon.
  * num_fin_gau : numéro à la fin et à gauche du tronçon.
  * num_fin_dro : numéro à la fin et à droite du tronçon.
  * Valeurs possibles :
    * NULL : non reseigné/inconnu
    *  Nombre entiers avec éventuellement un autre signe distinctif (bis, ter...).

Les numéros en début et fin ne sont pas simplement les numéros les plus proches des extrémités du tronçon. On essaie 
autant que possible d'identifier l'ordre logique de numérotation pour éviter que des trous dans la numérotation ne se
forme. Si l'ordre observé des points adresse le long d'un tronçon est 2, 4, 10, 8 puis, 16, 14, 18, 20, 22 le long d'un 
autre tronçon on s'attache à renseigner les numéros aux extrémités de la manière suivante : 2-10 puis 14-22 afin 
d'éviter que les numéros 8 et 16 ne soient associés à aucun tronçon.

Cette opération est compliquée par le fait que les numéros peuvent avoir des extensions telles que BIS, TER qu'il faut 
ordonner. Ils sont ordonner dans l'ordre croissant suivant :
- dans l'ordre suivant pour les extensions classiques : BIS, TER, QUATER, QUIQUIES
- dans l'ordre alphabétique pour toutes les autres extensions : A, B, C...  ; 1, 2, 3...

Forcer l'ordre logique ne pourra être réalisé que si cette ordre est globalement respecté à gauche et à droite. Dans le 
cas contraire on se limite aux numéros présents au plus proche des extrémités du tronçon.

* src_num : Mode de renseignement des numéros en début et fin de tronçon. Un seul champ est utilisé pour caractériser 
le mode de renseignement des numéros. Dès qu'un des quatre numéros est
modifié, ce champ doit être mis à jour. Si les numéros de voies ont été renseignés manuellement ces numéros ne peuvent
pas être mis à jour automatiquement par l'outil. Valeurs possibles :
  * NULL : non renseigné/inconnu (uniquement si les champs num_... n'ont pas été renseignés)
  * a : automatique (renseignement effectué par les outils développés par Neogeo)
  * m : manuel (renseignement réalisé sur la base d'informations recueillies de diverses manières et saisies
manuellement dans la base)


* cote_impair : côté des numéros impairs. Valurs possibles :
** NULL : non renseigné/inconnu
** g : côté gauche du tronçon (lorsque l'on se place dans le sens de saisie du tronçon)
** d : côté droit
** m : lorsque les numéros pairs et impairs peuvent se trouver des 2 côtés du tronçon

### Tables utilisées pour les logs

####ban_log
Tables géométriques utilisées pour le suivi d'anomalies

    id : identifiant incrémental
    message_date : date de constat
    code_insee : code insee de la commune concernée
    message : nom de la voie issu de la BD SDIS
    code_erreur : cf. liste présentée ci-dessous
    geometrie : géométrie du tronçon concerné par le tronçon

Liste des codes d'erreur utilisés dans les tables de log :

    10 - code Rivoli de la base adresses non apparié à une voie
    20 - voie nommée sans adresse


## Problématique d'optimisation des requêtes et d'indexation
fuzzystrmatch n'est peut-être pas idéal pour avoir des requêtes performantes.
pg_trgm/similarity est peut-être plus adapté (capacité à définir des index adaptés)
cf. http://www.postgresonline.com/journal/categories/57-fuzzystrmatch

## Idées d'indicateurs

### Statistiques sans logs
Présence de points adresse strictement superposés -> difficile à réaliser
Présence de points adresse avec le même numéro pour un même code Rivoli
Présence de points adresse avec numéro = 0
Présence de points adresse avec numéro compris en 90 et 100
Présence de points adresse avec numéro > 1000
Présence de points adresse avec même code Rivoli mais noms de voies différentes

Proportion de voies avec code Rivoli renseigné
Proportion de voies avec numéros renseignés
Proportion de codes Rivoli localisés avec dist > 4


### Statistiques avec logs
Temps de traitement par commune
Changements des fichiers Fantoir par commune :
- suppresion d'un code insee
- nouveau code insee
- supression de codes rivoli
- nouveaux codes rivoli


# Données à télécharger

téléchargement des fichiers Fantoir par Région et par Département (un fichier zip par Région contenant un fichier txt
par Département) :
https://www.collectivites-locales.gouv.fr/mise-a-disposition-gratuite-fichier-des-voies-et-des-lieux-dits-fantoir


téléchargement du fichier national :
http://www.data.gouv.fr/fr/datasets/fichier-fantoir-des-voies-et-lieux-dits/
