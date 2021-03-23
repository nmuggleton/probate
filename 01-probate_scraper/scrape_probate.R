## ------------------------------------------------------------------------
## Script name: scrape_probate.R
## Purpose of script: To scrape the probate records from gov.uk
## Dependencies: None
## Author: Naomi Muggleton
## Date created: 15/01/2021
## Date last modified: 17/02/2021
## ------------------------------------------------------------------------

rm(list = ls())

library(data.table)
library(tidyverse)
library(rvest)
library(httr)
library(aws.s3)

# Import ------------------------------------------------------------------

reset_config()

## List of name popularity (source: britishsurnames.co.uk)
names <- get_object(
  '/inputs/name_frequency.csv', 
  bucket = 'probate-calendar',
  as = 'text'
) %>% 
  fread()

## List of user agents
ip <- get_object(
  '/inputs/ips.csv', 
  bucket = 'probate-calendar',
  as = 'text'
) %>% 
  fread()

## Import sync function
s3source(
  '/inputs/ones3sync.R', 
  bucket = 'probate-calendar'
)

## Get R environment parameters
save_object(
  '/inputs/.Renviron', 
  bucket = 'probate-calendar'
)

# Set parameters ----------------------------------------------------------

## Key urls
base_url <- 'https://probatesearch.service.gov.uk'
probate_url <- paste(base_url, 'Calendar%s#calendar', sep = '/')

## Parameter inputs
names <- names[page_count > 0]$name
years <- 1858:1995
lag <- 10
time <- as.numeric(Sys.time()) - 10

## Proxies for rotation
ips <- ip %>% 
  .[[1]] %>% 
  as.list()

ports <- ip %>% 
  .[[2]] %>% 
  as.list()

user_agents <- ip %>% 
  .[[3]] %>% 
  as.list()

# Set up ------------------------------------------------------------------

## Create probate directory
dir.create('probate', showWarnings = F)

## Tidy up
rm(ip)

# Scrape ------------------------------------------------------------------

for (i in 1:length(years)) {
  
  ## Year that I want to use as my search term
  year_i <- years[i]
  
  dir.create(paste('probate', year_i, sep = '/'))
  
  for (j in 1:length(names)) {
    
    ## Name that I want to use as my search term
    name_j <- names[j]  
    
    ## Find results for a given year and name prefix
    search_suffix <- sprintf('?surname=%s&yearOfDeath=%d', name_j, year_i)
    search <- sprintf(probate_url, search_suffix)
    
    ## Read probate html (only once ten seconds have elapsed)
    while (as.numeric(Sys.time()) - time < lag) {}
    
    ## If server times out, retry up to five times
    probate_html <- read_html(search)
    
    time <- as.numeric(Sys.time())
    
    ## Count number of pages in search results
    page_count <- probate_html %>% 
      html_nodes(xpath = '//h2[contains(text(), "page")]/text()[1]') %>% 
      html_text() %>% 
      str_split(' page') %>% 
      .[[1]] %>% 
      .[1] %>% 
      as.numeric()
    
    ## url with place holder for page number
    page_suffix <- paste0(search_suffix, '&page=%d')
    url_page <- sprintf(probate_url, page_suffix)
    
    for (k in 1:page_count) {
      
      ## Select a random number for rotation
      rand_n <- sample(1:20, 1)
      
      rand_agent <- user_agents[rand_n][[1]]
      rand_ip    <- ips[rand_n][[1]]
      rand_port  <- ports[rand_n][[1]]
      
      ## Add header
      set_config(
        add_headers(
          `User-Agent` = rand_agent
        )
      )
      
      set_config(
        use_proxy(
          rand_ip,
          port = rand_port
        ),
        override = F
      )
      
      ## Page url
      url <- sprintf(url_page, k)
      
      ## Get html for page
      while (as.numeric(Sys.time()) - time < lag) {}
      
      ## To look more human, do an unexpected search 10% of the time
      if (sample(1:10, 1) == 1) {
        
        read_html('https://probatesearch.service.gov.uk/#calendar')
        Sys.sleep(10 + rnorm(1))
        
      }
      
      page <- read_html(url)
      
      time <- as.numeric(Sys.time())
      
      ## Find location of the image
      image_string <- page %>% 
        html_nodes(xpath = '//*[@id = "imgCalendar"]') %>% 
        html_attr('src')
      
      image_url <- paste0(base_url, image_string)
      
      image_stub <- str_split(image_url, 'filePath=')[[1]][2] %>% 
        str_remove_all('%2F[0-9]+%2F[A-Z]%2F') %>% 
        str_to_lower() %>% 
        str_remove_all('%20') %>% 
        str_remove_all('%')
      
      ## Download image
      download.file(
        image_url, 
        paste('probate', year_i, image_stub, sep = '/'),
        quiet = T
      )
      
      ## Feedback
      cat( 
        paste0(
          'Complete: year ', year_i, 
          ', name ', name_j, 
          ', page ', k, ' of ', page_count,
          '\n'
        )
      )
      
    }
  }
  
  reset_config()
  
  ones3sync(
    path = paste('~', 'probate', year_i, sep = '/'),
    bucket = 'probate-calendar',
    prefix = paste0(year_i, '/'),
    region = 'eu-west-2',
    direction = 'upload',
    verbose = T,
    year = year_i
  )
  
  nfiles_bucket <- length(
    get_bucket(
      'probate-calendar', 
      prefix = paste0(year_i, '/'),
      max = Inf
    )
  )
  
  nfiles_local <- length(
    list.files(
      paste('probate', year_i, sep = '/')
    )
  )
  
  if (nfiles_bucket == nfiles_local) {
    
    file.remove(
      paste('probate', 
            year_i, 
            list.files(
              paste('probate', year_i, sep = '/')
            ), 
            sep = '/')
    )
    
  } 
  
  rm(nfiles_local, nfiles_bucket)
  
}
