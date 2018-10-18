ogr2ogr -f SQLite -update \
-t_srs http://spatialreference.org/ref/esri/102003/ \
/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite \
/home/eric/Documents/franklin/narsc2018/source_data/census/nhgis0058_shape/nhgis0058_shapefile_tl2000_us_msa_cmsa_1990/US_msacmsa_1990.shp \
-nln US_msacmsa_1990 \
-nlt PROMOTE_TO_MULTI

ogr2ogr -f SQLite -update \
-t_srs http://spatialreference.org/ref/esri/102003/ \
/home/eric/Documents/franklin/narsc2018/generated_data/narsc18.sqlite \
/home/eric/Documents/franklin/narsc2018/source_data/census/nhgis0058_shape/nhgis0058_shapefile_tl2000_us_msa_cmsa_2000/US_msacmsa_2000.shp \
-nln US_msacmsa_2000 \
-nlt PROMOTE_TO_MULTI

echo "DONE"