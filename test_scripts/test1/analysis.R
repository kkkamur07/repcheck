# Analysis script - depends on data_prep.R

source("data_prep.R")

# Perform analysis
summary_stats <- calculate_summary(clean_dataset)

# Group analysis
group_stats <- aggregate(value ~ category, clean_dataset, mean)

# Create a simple plot
if (require(graphics)) {
  png("analysis_plot.png")
  hist(clean_dataset$value, main = "Distribution of Values", xlab = "Value")
  dev.off()
}

print("Analysis completed")
print(summary_stats)