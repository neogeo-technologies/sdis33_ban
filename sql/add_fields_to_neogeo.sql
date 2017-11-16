ALTER TABLE neogeo.rerouprima_l
   ADD COLUMN rivoli character varying(255) DEFAULT(null),
   ADD COLUMN rivoli_dist integer DEFAULT(null),
   ADD COLUMN src_rivoli character DEFAULT(null),
   ADD COLUMN num_deb_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_deb_dro character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_dro character varying(32) DEFAULT(null),
   ADD COLUMN src_num character DEFAULT(null),
   ADD COLUMN cote_impair character DEFAULT(null);

ALTER TABLE neogeo.rerousecon_l
   ADD COLUMN rivoli character varying(255) DEFAULT(null),
   ADD COLUMN rivoli_dist integer DEFAULT(null),
   ADD COLUMN src_rivoli character DEFAULT(null),
   ADD COLUMN num_deb_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_deb_dro character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_dro character varying(32) DEFAULT(null),
   ADD COLUMN src_num character DEFAULT(null),
   ADD COLUMN cote_impair character DEFAULT(null);

ALTER TABLE neogeo.rerouterti_l
   ADD COLUMN rivoli character varying(255) DEFAULT(null),
   ADD COLUMN rivoli_dist integer DEFAULT(null),
   ADD COLUMN src_rivoli character DEFAULT(null),
   ADD COLUMN num_deb_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_deb_dro character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_dro character varying(32) DEFAULT(null),
   ADD COLUMN src_num character DEFAULT(null),
   ADD COLUMN cote_impair character DEFAULT(null);

ALTER TABLE neogeo.rerouquate_l
   ADD COLUMN rivoli character varying(255) DEFAULT(null),
   ADD COLUMN rivoli_dist integer DEFAULT(null),
   ADD COLUMN src_rivoli character DEFAULT(null),
   ADD COLUMN num_deb_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_deb_dro character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_dro character varying(32) DEFAULT(null),
   ADD COLUMN src_num character DEFAULT(null),
   ADD COLUMN cote_impair character DEFAULT(null);

ALTER TABLE neogeo.rerouauacc_l
   ADD COLUMN rivoli character varying(255) DEFAULT(null),
   ADD COLUMN rivoli_dist integer DEFAULT(null),
   ADD COLUMN src_rivoli character DEFAULT(null),
   ADD COLUMN num_deb_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_deb_dro character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_dro character varying(32) DEFAULT(null),
   ADD COLUMN src_num character DEFAULT(null),
   ADD COLUMN cote_impair character DEFAULT(null);

ALTER TABLE neogeo.rerouvonoc_l
   ADD COLUMN rivoli character varying(255) DEFAULT(null),
   ADD COLUMN rivoli_dist integer DEFAULT(null),
   ADD COLUMN src_rivoli character DEFAULT(null),
   ADD COLUMN num_deb_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_deb_dro character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_gau character varying(32) DEFAULT(null),
   ADD COLUMN num_fin_dro character varying(32) DEFAULT(null),
   ADD COLUMN src_num character DEFAULT(null),
   ADD COLUMN cote_impair character DEFAULT(null);
