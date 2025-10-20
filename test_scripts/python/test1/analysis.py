"""Analysis script - depends on data_prep.py"""

import data_prep

# Perform additional analysis
dataset = data_prep.clean_dataset
stats = data_prep.stats

# Group analysis
above_average = [x for x in dataset if x > stats["mean"]]
below_average = [x for x in dataset if x <= stats["mean"]]

print(f"Analysis completed")
print(f"Above average: {len(above_average)} values")
print(f"Below average: {len(below_average)} values")
print(f"Mean: {stats['mean']:.2f}")