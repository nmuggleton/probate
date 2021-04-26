
rm(list = ls())

library(data.table)
library(stringr)
library(tidyverse)
library(scales)

data <- fread('../output_1858_1981.csv')

data[, year := str_extract(filename, '\\d{4}(?=\\.)') %>% as.numeric()]

ggplot(data[size == 100], aes(x = year, y = accuracy)) + 
  geom_point() +
  scale_y_continuous(labels = percent_format(accuracy = 1), limits = c(0, 1)) +
  geom_smooth(method = lm)

ggplot(data, aes(x = size, y = accuracy)) +
  geom_point() +
  scale_y_continuous(labels = percent_format(accuracy = 1), limits = c(0, 1)) +
  facet_wrap(~ year)

data[, max := max(accuracy), by = year]

ggplot(data[size == 100], aes(x = year)) +
  geom_point(aes(y = accuracy, colour = 'Before resizing'), alpha = .7) +
  geom_point(aes(y = max, colour = 'After resizing'), alpha = .7) +
  scale_y_continuous(labels = percent_format(accuracy = 1), limits = c(0, 1))

