cat("fail_runtime_type.R: producing a type error\n")
x <- "not-a-number"
y <- log(x)  # will error: non-numeric argument to mathematical function
cat("This should never print, y =", y, "\n")
