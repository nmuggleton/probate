
rm(list = ls())

library(data.table)
library(tidyverse)
library(knitr)

# Functions ---------------------------------------------------------------

checker <- function(i) {
  year <- years_to_check[i]
  data <- fread(sprintf('resize/%d.csv', year))
  cat(paste0(year, ':\n'))
  print(names(which(colMeans(data[, -1]) == 0)))
}

# Set up ------------------------------------------------------------------

setwd('~/Documents/work/github/probate/src/params')

years <- 1909:1940

# Find shortlist of years -------------------------------------------------

years_to_check <- c()

for (i in 1:length(years)) {
  
  year <- years[i]
  data <- fread(sprintf('resize/%d.csv', year))

  if (T %in% (colMeans(data[, -1]) == 0)) {
    
    years_to_check <- c(years_to_check, year)
  
  }
  
}

# Check shortlist of years ------------------------------------------------

for (i in 1:length(years_to_check)) {
  
  checker(i)
  
}
