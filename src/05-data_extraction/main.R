
rm(list = ls())

library(data.table)
library(stringr)
library(tokenizers)

# Functions ---------------------------------------------------------------



# Parameters --------------------------------------------------------------

i <- 'text'
year <- 1858
l <- 20

# Step 1: import files ----------------------------------------------------

path <- paste('/Volumes/T7/probate_files', i, year, sep = '/')

files <- list.files(path)  # List all files
files <- files[str_which(files, '.txt')]  # Remove non-.txt files
files <- files[str_which(files, '^\\d{6}')]  # Remove hidden files
files <- paste(path, files, sep = '/')

files <- sort(files)

file <- paste(read_lines(files[1]), collapse = '\n')

pages <- lapply(
  files[1:l], 
  function(x) {
    paste(read_lines(x), collapse = '\n') %>% 
      str_replace_all('-\n', '')
  }
)

pages <- tokenize_regex(pages, '\\s(?=[A-Z]+\\h[A-Z]\\w+)')

page <- list()
people <- list()

for (p in 1:l) {
  
  # Get first line for page
  first_line <- pages[[p]][1]
  
  # If contains page break, it is a carry-over from previous page
  if (str_detect(first_line, '\\n')) {
    hangover <- str_remove(first_line, '^.*\\n')
    
    # Tag this to previous page
    prev_page_len <- length(pages[[p - 1]])
    prev_page_txt <- pages[[p - 1]][prev_page_len]
    pages[[p - 1]][prev_page_len] <- paste(prev_page_txt, hangover, sep = '\n')
    
    # Remove this from current page
    pages[[p]][1] <- str_extract(first_line, '.*(?=\\n)')
    
  }
  
  pages[[p]][1] <- str_split(pages[[p]][1], ' ')
  
  page[[p]] <- pages[[p]][[1]]
  pages[[p]] <- pages[[p]][-1]
  
}

for (page in pages) {
  
  people <- page[1:length(page)]
  
  for (person in people) {

    name <- str_extract(person, '^[A-Z]+\\s[A-Z]\\w+.*\\d')
    name <- str_remove_all(name, '[:punct:]')
    name <- str_remove_all(name, '\\d+')
    name <- str_trim(name)
    
    proved <- str_extract(person, '\\d+\\s\\w.*\\.')
    proved <- str_remove_all(proved, '[:punct:]')
    
    effects <- str_extract(person, '[A-Z].*£\\d+.*\\d\\.')
    effects <- str_remove_all(effects, '\\.')
    effects <- str_trim(effects)
    print(effects)

  }
  
}
