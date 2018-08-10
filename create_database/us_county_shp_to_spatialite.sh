#!/bin/bash

ogr2ogr -f SQLite -dsco SPATIALITE=YES \
-t_srs http://spatialreference.org/ref/esri/102003/ \
/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite \
/home/eric/Documents/franklin/narsc2018/source_data/census/nhgis0040_shape/nhgis0040_shapefile_tl2010_us_county_2010/US_county_2010.shp \
-nlt PROMOTE_TO_MULTI

echo "DONE"