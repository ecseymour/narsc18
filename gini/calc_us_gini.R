library(binequality)
library(glue)

files <- c("/home/eric/Documents/franklin/narsc2018/generated_data/binned_income/us_bins_1990.csv",
           "/home/eric/Documents/franklin/narsc2018/generated_data/binned_income/us_bins_2000.csv",
           "/home/eric/Documents/franklin/narsc2018/generated_data/binned_income/us_bins_125.csv"
           )

for(i in 1:length(files)){
  print(files[i])
  
  survey <- gsub(".*bins_|\\.csv", "", files[i]) # extract survey string
  outfile <- glue("/home/eric/Documents/franklin/narsc2018/generated_data/binned_income/us_gini_{survey}.csv") # add to end of output file
  print(outfile)
  
  us_bins <- read.csv(files[i], colClasses = c("FIPS"="character")) # write fips as string to preserve leading zeros
  ID = us_bins$FIPS
  hb = us_bins$pop
  bmin = us_bins$bin_min
  bmax = us_bins$bin_max
  omu = rep(NA, length(us_bins))

  results <- fitFunc(ID = ID, hb = hb, bin_min = bmin, bin_max = bmax, obs_mean = omu, ID_name = 'FIPS')
  print(results)
  write.csv(results$datOut, outfile)
}