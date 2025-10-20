# Independent script with no dependencies

# Simple standalone script
message("Starting independent analysis")

# Generate some data
x <- 1:10
y <- x^2 + rnorm(10)

# Simple analysis
correlation <- cor(x, y)
print(paste("Correlation:", round(correlation, 3)))

# Save result
write.csv(data.frame(x = x, y = y), "independent_data.csv")

message("Independent script completed successfully")