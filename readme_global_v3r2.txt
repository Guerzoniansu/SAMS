Oct-03-2017
*****************************************************
Differences to spam2005V3r1 files:
Allocation for the 6 following countries was performed again due to the omission of level1 statistics for some crops:
Yemen, New Zealand, Czech Republic, Italy, Poland and Sweden.
Allocation for New Delhi and Madrid was repeated (previously infeasible) 
*****************************************************


*****************************************************
Files in this directory and naming conventions
*****************************************************

Zip files
*********
spam2005V3r2_global_harv_area.zip		SPAM area harvested, global pixels, files in 2 formats x 6 technologies, strucuture A, record type H
spam2005V3r2_global_phys_area.zip		SPAM physical area, global pixels, files in 2 formats x 6 technologies, strucuture A, record type A
spam2005V3r2_global_prod.zip		SPAM production, global pixels, files in 2 formats x 6 technologies, strucuture A, record type P
spam2005V3r2_global_yield.zip		SPAM yield, global pixels, files in 2 formats x 6 technologies, strucuture A, record type Y
spam2005V3r2_global_val_prod_agg.zip	SPAM value of production and area harvested, global pixels, files in 2 formats x 6 technologies, strucuture B, record type V

File names
*************
All files have standard names, which allow direct identification of variable and technology:
SPAM2005V3r2_global_v_t.fff
where
v = variable 
t = technology
fff = format

v: Variables
**************
*_A_*		physical area
*_H_*		harvested area
*_P_*		production
*_Y_*		yield
*_V_agg_*	value of production, aggregated to all crops, food and non-food (see below)

t: Technologies
******************
*_TA	all technologies together, ie complete crop
*_TI	irrigated portion of crop
*_TH	rainfed high inputs portion of crop
*_TL	rainfed low inputs portion of crop
*_TS	rainfed subsistence portion of crop
*_TR	rainfed portion of crop (= TA - TI, or TH + TL + TS)

fff: File formats
******************
*.dbf	FoxPlus, directly readable by ArcGis
*.csv	comma separated values

Structure A
**************
each pixel has
7 fields to identify pixel:
   ISO3, prod_level (=fips2), alloc_key (SPAM pixel id), cell5m (cell5m id), rec_type (same in each zip file), tech_type (see technologies above), unit (same in each zip file, for all values)
42 fields for 42 crops: 
     similar to spam  notation: crop_T, where T = A, I, H, L, S or R
7 fields for annotations: 
   creation data of data, year_data (years of statistics used), source (source for scaling, always FAO avg2004-06), name_cntr, name_adm1, name_adm2 (all derived from prod_level field)

Structure B
**************
each pixel has
7 fields to identify pixel:
   ISO3, prod_level (=fips2), alloc_key (SPAM pixel id), cell5m (cell5m id), rec_type (same in each zip file), tech_type (see technologies above), unit (same in each zip file, shows I$ .. international $, but only applies to VoP fields; unit of area harvested fields = ha)
9 fields for file with individual technologies: 
   vp_crop_T ( value of production of all 42 crops), VP_food_T (value of production of food crops), VP_nonf_T (value of produciton of non-food crops), area_cr_T (harvested area of all crops), area_fo_T (harvested area of food crops), area_nf_T (harvested area of non-food crops), vp_cr_ar_T (VoP per ha of all crops), vp_fo_ar_T (VoP per ha of food crops), vp_nf_ar_T (VoP per ha of non-food crops)
where T = A, I, H, L, S or R
7 fields for annotations: 
   creation data of data, year_data (years of statistics used), source (source for scaling, always FAO avg2004-06), name_cntr, name_adm1, name_adm2 (all derived from prod_level field)

Food crops:
**************
crop #	name		SPAM name
1	wheat		whea
2	rice		rice
3	maize		maiz
4	barley		barl
5	pearl millet	pmil
6	small millet	smil
7	sorghum		sorg
8	other cereals	ocer
9	potato		pota
10	sweet potato	swpo
11	yams		yams
12	cassava		cass
13	other roots	orts
14	bean		bean
15	chickpea		chic
16	cowpea		cowp
17	pigeonpea	pige
18	lentil		lent
19	other pulses	opul
20	soybean		soyb
21	groundnut	grou
22	coconut		cnut
37	banana		bana
38	plantain		plnt
39	tropical fruit	trof
40	temperate fruit	temf
41	vegetables	vege

Non-food crops:
*******************
crop #	name		SPAM name
23	oilpalm		oilp
24	sunflower	sunf
25	rapeseed		rape
26	sesameseed	sesa
27	other oil crops	ooil
28	sugarcane	sugc
29	sugarbeet	sugb
30	cotton		cott
31	other fibre crops	ofib
32	arabica coffee	acof
33	robusta coffee	rcof
34	cocoa		coco
35	tea		teas
36	tobacco		toba
42	rest of crops	rest

