# Print command-line args and optionally fail if a flag is present
args <- commandArgs(trailingOnly = TRUE)
cat("args:", paste(args, collapse = " "), "\n")
if ("--fail" %in% args) {
  stop("Failing because --fail was provided")
}
