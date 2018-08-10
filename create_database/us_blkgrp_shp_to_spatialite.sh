#!/bin/bash

ogr2ogr -f SQLite -update \
-t_srs http://spatialreference.org/ref/esri/102003/ \
/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite \
/home/eric/Documents/franklin/narsc2018/source_data/census/nhgis0041_shape/nhgis0041_shapefile_tl2010_us_blck_grp_2010/US_blck_grp_2010.shp \
-nlt PROMOTE_TO_MULTI

echo "DONE"