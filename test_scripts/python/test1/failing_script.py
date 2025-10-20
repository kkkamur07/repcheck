"""Script with intentional error - depends on utils.py"""

import utils

# This will fail
result = undefined_variable + 10

print("This won't print due to error above")