# Basic utility functions - no dependencies

clean_data <- function(data) {
  # Remove NA values
  cleaned <- data[complete.cases(data), ]
  return(cleaned)
}

calculate_summary <- function(data) {
  summary_stats <- list(
    mean = mean(data$value, na.rm = TRUE),
    median = median(data$value, na.rm = TRUE),
    sd = sd(data$value, na.rm = TRUE)
  )
  return(summary_stats)
}

print("Utils loaded successfully")