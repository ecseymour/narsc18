cd "\\files.brown.edu\Home\eseymou1\Desktop\gini"
net set ado "\\files.brown.edu\Home\eseymou1\Desktop\gini"
ssc install egen_inequal
ssc install rpme

insheet using us_bins_1990.csv
destring bin_max, replace ignore("NA")
encode(fips), generate(fips_new)
rpme pop bin_min bin_max, by(fips_new) saving(us_ests_1990)
clear
use us_ests_1990
outsheet using us_ests_1990.csv , comma
clear

insheet using us_bins_2000.csv
destring bin_max, replace ignore("NA")
encode(fips), generate(fips_new)
rpme pop bin_min bin_max, by(fips_new) saving(us_ests_2000)
clear
use us_ests_2000
outsheet using us_ests_2000.csv , comma
clear

insheet using us_bins_125.csv
destring bin_max, replace ignore("NA")
encode(fips), generate(fips_new)
rpme pop bin_min bin_max, by(fips_new) saving(us_ests_125)
clear
use us_ests_125
outsheet using us_ests_125.csv , comma
clear