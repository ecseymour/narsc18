cd "\\files.brown.edu\Home\eseymou1\Desktop"
insheet using diversity_regression_data.csv
encode(state), generate(state_dummy)
encode(region), generate(region_dummy)
generate lnpop00 = log(pop00)
regress specialization_diff_0010 ppctchg_0010 pwhite_00 lnpop00 i.metro_status00 i.state_dummy i.region_dummy