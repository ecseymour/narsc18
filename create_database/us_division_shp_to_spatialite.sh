#!/bin/bash

ogr2ogr -f SQLite -update \
-t_srs http://spatialreference.org/ref/esri/102003/ \
/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite \
/home/eric/Documents/franklin/narsc2018/source_data/census/gz_2010_us_030_00_5m/gz_2010_us_030_00_5m.shp \
-nln census_divisions_10 \
-nlt PROMOTE_TO_MULTI

ogr2ogr -f SQLite -update \
-t_srs http://spatialreference.org/ref/esri/102003/ \
/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite \
/home/eric/Documents/franklin/narsc2018/source_data/census/gz_2010_us_020_00_5m/gz_2010_us_020_00_5m.shp \
-nln census_regions_10 \
-nlt PROMOTE_TO_MULTI

echo "DONE"