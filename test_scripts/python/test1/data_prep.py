"""Data preparation script - depends on utils.py"""

import utils

# Create sample data
raw_data = [10, 20, 30, None, 40, 50, None, 60, 70, 80]

# Clean the data using utility function
clean_dataset = utils.clean_data(raw_data)

# Calculate statistics
stats = utils.calculate_stats(clean_dataset)

print(f"Data prepared: {len(clean_dataset)} clean records")
print(f"Statistics: {stats}")