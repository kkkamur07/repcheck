"""Script with lint issues but works - depends on utils.py"""

import utils

# Long variable name (lint warning)
this_is_a_very_long_variable_name_that_exceeds_normal_conventions = 3

# Multiple statements on one line (lint warning)
x = 1; y = 2; z = 3

# Unused variable (lint warning)
unused_variable = "not used"

result = this_is_a_very_long_variable_name_that_exceeds_normal_conventions
print(result)