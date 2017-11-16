ALTER TABLE gces.rerouprima_l
   ADD COLUMN rivoli character varying(255) DEFAULT(null),
   ADD COLUMN rivoli_dist integer DEFAULT(null),
   ADD COLUMN src_rivoli character DEFAULT(null),
   ADD COLUMN num_deb_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_deb_dro character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_dro character varying(32) DEFAULT(null),
   ADD COLUMN src_num character DEFAULT(null),
   ADD COLUMN cote_impair character DEFAULT(null);

ALTER TABLE gces.rerousecon_l
   ADD COLUMN rivoli character varying(255) DEFAULT(null),
   ADD COLUMN rivoli_dist integer DEFAULT(null),
   ADD COLUMN src_rivoli character DEFAULT(null),
   ADD COLUMN num_deb_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_deb_dro character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_dro character varying(32) DEFAULT(null),
   ADD COLUMN src_num character DEFAULT(null),
   ADD COLUMN cote_impair character DEFAULT(null);

ALTER TABLE gces.rerouterti_l
   ADD COLUMN rivoli character varying(255) DEFAULT(null),
   ADD COLUMN rivoli_dist integer DEFAULT(null),
   ADD COLUMN src_rivoli character DEFAULT(null),
   ADD COLUMN num_deb_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_deb_dro character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_dro character varying(32) DEFAULT(null),
   ADD COLUMN src_num character DEFAULT(null),
   ADD COLUMN cote_impair character DEFAULT(null);

ALTER TABLE gces.rerouquate_l
   ADD COLUMN rivoli character varying(255) DEFAULT(null),
   ADD COLUMN rivoli_dist integer DEFAULT(null),
   ADD COLUMN src_rivoli character DEFAULT(null),
   ADD COLUMN num_deb_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_deb_dro character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_dro character varying(32) DEFAULT(null),
   ADD COLUMN src_num character DEFAULT(null),
   ADD COLUMN cote_impair character DEFAULT(null);

ALTER TABLE gces.rerouauacc_l
   ADD COLUMN rivoli character varying(255) DEFAULT(null),
   ADD COLUMN rivoli_dist integer DEFAULT(null),
   ADD COLUMN src_rivoli character DEFAULT(null),
   ADD COLUMN num_deb_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_deb_dro character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_dro character varying(32) DEFAULT(null),
   ADD COLUMN src_num character DEFAULT(null),
   ADD COLUMN cote_impair character DEFAULT(null);

ALTER TABLE gces.rerouvonoc_l
   ADD COLUMN rivoli character varying(255) DEFAULT(null),
   ADD COLUMN rivoli_dist integer DEFAULT(null),
   ADD COLUMN src_rivoli character DEFAULT(null),
   ADD COLUMN num_deb_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_deb_dro character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_dro character varying(32) DEFAULT(null),
   ADD COLUMN src_num character DEFAULT(null),
   ADD COLUMN cote_impair character DEFAULT(null);
