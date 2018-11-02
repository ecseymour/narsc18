library(sandwich)
library(stargazer)

# read data
data9000 <- read.csv('/home/eric/Documents/franklin/narsc2018/generated_data/regression_data_9000.csv',
  header = TRUE, sep = ",")

data0010 <- read.csv('/home/eric/Documents/franklin/narsc2018/generated_data/regression_data_0010.csv',
  header = TRUE, sep = ",")

# factor categorical vars
data9000$STATE <- factor(data9000$STATE)
data9000$region <- factor(data9000$region)
data9000$metro_dummy <- factor(data9000$metro_dummy)
data9000$loss_dummy <- factor(data9000$loss_dummy)

data0010$STATE <- factor(data0010$STATE)
data0010$region <- factor(data0010$region)
data0010$metro_dummy <- factor(data0010$metro_dummy)
data0010$loss_dummy <- factor(data0010$loss_dummy)


################################################################################################
# run specialization models
m9000.cont <- lm('specialization_diff ~ ppctchg + pwhite_start + log(pop_start) + metro_dummy + STATE', data = data9000)
m9000.dummy <- lm('specialization_diff ~ loss_dummy + pwhite_start + log(pop_start) + metro_dummy + STATE', data = data9000)
m0010.cont <- lm('specialization_diff ~ ppctchg + pwhite_start + log(pop_start) + metro_dummy + STATE', data = data0010)
m0010.dummy <- lm('specialization_diff ~ loss_dummy + pwhite_start + log(pop_start) + metro_dummy + STATE', data = data0010)

stargazer(m9000.cont, m9000.dummy, m0010.cont, m0010.dummy,
          type='latex', omit.stat = c('f', 'ser'), omit = c('STATE'),
          column.labels = c('90--00', '90--00', '00--10', '00--10'),
          model.numbers = FALSE,
          dep.var.labels = c('specialization difference'),
          omit.labels = 'state',
          covariate.labels = c('pop. pct. change', 'loss dummy', 'pct. white base yr', 'log(base pop.)', 'metro dummy'),
          table.placement = "p", title = "OLS regression for change in county specialization",
          out = '~/Documents/franklin/narsc2018/scripts/stargazer_output/specialization_tbl.tex'
          )
################################################################################################
# run diversity models
m9000.cont <- lm('diversity_diff ~ ppctchg + pwhite_start + log(pop_start) + metro_dummy + STATE', data = data9000)
m9000.dummy <- lm('diversity_diff ~ loss_dummy + pwhite_start + log(pop_start) + metro_dummy + STATE', data = data9000)
m0010.cont <- lm('diversity_diff ~ ppctchg + pwhite_start + log(pop_start) + metro_dummy + STATE', data = data0010)
m0010.dummy <- lm('diversity_diff ~ loss_dummy + pwhite_start + log(pop_start) + metro_dummy + STATE', data = data0010)

stargazer(m9000.cont, m9000.dummy, m0010.cont, m0010.dummy,
          type='latex', omit.stat = c('f', 'ser'), omit = c('STATE'),
          column.labels = c('90--00', '90--00', '00--10', '00--10'),
          model.numbers = FALSE,
          dep.var.labels = c('diversity difference'),
          covariate.labels = c('pop. pct. change', 'loss dummy', 'pct. white base yr', 'log(base pop.)', 'metro dummy'),
          omit.labels = 'state',
          table.placement = "p", title = "OLS regression for change in county diversity",
          out = '~/Documents/franklin/narsc2018/scripts/stargazer_output/diversity_tbl.tex'
          )
################################################################################################
# run gini models
m9000.cont <- lm('gini_diff ~ ppctchg + pwhite_start + log(pop_start) + metro_dummy + gini_start + STATE', data = data9000)
m9000.dummy <- lm('gini_diff ~ loss_dummy + pwhite_start + log(pop_start) + metro_dummy + gini_start + STATE', data = data9000)
m0010.cont <- lm('gini_diff ~ ppctchg + pwhite_start + log(pop_start) + metro_dummy + gini_start + STATE', data = data0010)
m0010.dummy <- lm('gini_diff ~ loss_dummy + pwhite_start + log(pop_start) + metro_dummy + gini_start + STATE', data = data0010)

stargazer(m9000.cont, m9000.dummy, m0010.cont, m0010.dummy,
          type='latex', omit.stat = c('f', 'ser'),
          column.labels = c('90--00', '90--00', '00--10', '00--10'),
          model.numbers = FALSE,
          dep.var.labels = c('gini difference'),
          omit.labels = 'state', omit = c('STATE'),
          covariate.labels = c('pop. pct. change', 'loss dummy', 'pct. white base yr', 'log(base pop.)', 'metro dummy', 'Gini base yr'),
          table.placement = "p", title = "OLS regression for change in county income inequality",
          out = '~/Documents/franklin/narsc2018/scripts/stargazer_output/gini_tables.tex'
          )
################################################################################################
m9000.cont <- lm('pwhite_diff ~ ppctchg + pwhite_start + log(pop_start) + metro_dummy  + STATE', data = data9000)
m9000.dummy <- lm('pwhite_diff ~ loss_dummy + pwhite_start + log(pop_start) + metro_dummy + STATE', data = data9000)
m0010.cont <- lm('pwhite_diff ~ ppctchg + pwhite_start + log(pop_start) + metro_dummy + STATE', data = data0010)
m0010.dummy <- lm('pwhite_diff ~ loss_dummy + pwhite_start + log(pop_start) + metro_dummy + STATE', data = data0010)

stargazer(m9000.cont, m9000.dummy, m0010.cont, m0010.dummy,
          type='latex', omit.stat = c('f', 'ser'),
          column.labels = c('90--00', '90--00', '00--10', '00--10'),
          model.numbers = FALSE,
          dep.var.labels = c('pct. white difference'),
          omit.labels = 'state', omit = c('STATE'),
          covariate.labels = c('pop. pct. change', 'loss dummy', 'pct. white base yr', 'log(base pop.)', 'metro dummy'),
          table.placement = "p", title = "OLS regression for change in county percent White",
          out = '~/Documents/franklin/narsc2018/scripts/stargazer_output/pwhite_tables.tex'
          )
################################################################################################
# run poverty models
m9000.cont <- lm('poverty_diff ~ ppctchg + pwhite_start + log(pop_start) + metro_dummy + poverty_start + STATE', data = data9000)
m9000.dummy <- lm('poverty_diff ~ loss_dummy + pwhite_start + log(pop_start) + metro_dummy + poverty_start + STATE', data = data9000)
m0010.cont <- lm('poverty_diff ~ ppctchg + pwhite_start + log(pop_start) + metro_dummy + poverty_start + STATE', data = data0010)
m0010.dummy <- lm('poverty_diff ~ loss_dummy + pwhite_start + log(pop_start) + metro_dummy + poverty_start + STATE', data = data0010)

stargazer(m9000.cont, m9000.dummy, m0010.cont, m0010.dummy,
          type='latex', omit.stat = c('f', 'ser'), omit = c('STATE'),
          column.labels = c('90--00', '90--00', '00--10', '00--10'),
          model.numbers = FALSE,
          dep.var.labels = c('poverty difference'),
          omit.labels = 'state',
          covariate.labels = c('pop. pct. change', 'loss dummy', 'pct. white base yr', 'log(base pop.)', 'metro dummy', 'poverty base yr'),
          table.placement = "p", title = "OLS regression for change in county poverty rate",
          out = '~/Documents/franklin/narsc2018/scripts/stargazer_output/poverty_tables.tex'
          )