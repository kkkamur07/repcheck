# Data preparation - depends on utils.R

source("utils.R")

# Create sample data
set.seed(123)
raw_data <- data.frame(
  id = 1:100,
  value = c(rnorm(80, 50, 10), rep(NA, 20)),  # 20% missing values
  category = sample(c("A", "B", "C"), 100, replace = TRUE)
)

# Clean the data using utility function
clean_dataset <- clean_data(raw_data)

print(paste("Data prepared:", nrow(clean_dataset), "clean records"))