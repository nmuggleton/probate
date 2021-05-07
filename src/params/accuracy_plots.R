
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


# Improvement plots -------------------------------------------------------

rm(list = ls())

library(data.table)
library(tidyverse)
library(knitr)

setwd('/Volumes/T7/work/github/probate/src/params')

output <- data.table(size = numeric(), accuracy = numeric(), year = numeric())

years <- 1858:1907

for (i in 1:length(years)) {
  
  year <- years[i]
  data <- fread(sprintf('resize/%d.csv', year))
  data[, accuracy := rowMeans(data[, -1])]
  
  data <- data[size == 100 | accuracy == max(accuracy)][, .(size, accuracy)][, year := year]
  
  output <- rbind(output, data)
  
}

# ggplot(output, aes(x = year, y = accuracy, colour = (size == 100))) +
#   geom_point() +
#   scale_y_continuous(limits = c(0, 1), labels = scales::percent_format(accuracy = 1))


original <- output[size == 100]
setnames(original, 'accuracy', 'original')

best <- output[, .(best_size = median(size), best = max(accuracy)), by = year]

data <- merge(original, best, by = 'year')

ggplot(data) +
  geom_segment(
    aes(x = year, xend = year, y = original, yend = best), 
    colour = 'grey'
    ) +
  geom_point(
    aes(x = year, y = original), 
    colour = 'red', 
    size = 3
    ) +
  geom_point( aes(x = year, y = best), color = 'green', size = 3) +
  scale_y_continuous(
    name = 'accuracy', 
    limits = c(0, 1), 
    labels = percent_format(accuracy = 1)
    ) +
  theme(
    legend.position = "none",
  )

mean(data$best)
mean(data$original)
mean(data$best_size)

caption <- paste(
  'Optimal size = size that gives the highest accuracy, as a percentage of',
  'original size'
)
data[, .(year, best_size = round(best_size), original, best)] %>% 
  kable(
    digits = 2, 
    col.names = c('Year', 'Optimal size (%)', 'Original (%)', 'Improved (%)'),
    caption = 'Optimal size = size that gives the highest accuracy, as a percentage of original size',
    )

