# Script with linting issues but working code

source("utils.R")

# Bad style - long line and spacing issues
very_long_variable_name_that_exceeds_normal_limits<-function(x,y,z){return(x+y+z)}

# Trailing whitespace and inconsistent spacing
data<-c(1,2,3,4,5)   
result =   mean( data )  

# This works but has style issues
print(result)