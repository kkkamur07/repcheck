cat("fail_missing_pkg.R: checking for a non-installed package\n")
if (!requireNamespace("definitelynotapkg123", quietly = TRUE)) {
  stop("Package 'definitelynotapkg123' is not installed")
}
cat("This should never print\n")
