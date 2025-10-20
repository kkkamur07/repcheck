# This script has intentional errors for testing

source("utils.R")

# This will fail - undefined variable
result <- undefined_variable + 10

# This will also fail - function doesn't exist
bad_result <- nonexistent_function(data)

print("This won't print due to errors above")