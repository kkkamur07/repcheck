# A simple R script that fails with a non-zero exit
cat("About to fail\n")
stop("Intentional failure in fail.R")
# Alternatively, to be explicit:
# quit(status = 1)
