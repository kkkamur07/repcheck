"""Utility functions for data processing."""

def clean_data(data):
    """Remove None values from list."""
    return [x for x in data if x is not None]

def calculate_mean(data):
    """Calculate mean of numeric data."""
    if not data:
        return 0
    return sum(data) / len(data)

def calculate_stats(data):
    """Calculate basic statistics."""
    clean = clean_data(data)
    if not clean:
        return {"mean": 0, "min": 0, "max": 0, "count": 0}
    
    return {
        "mean": calculate_mean(clean),
        "min": min(clean),
        "max": max(clean),
        "count": len(clean)
    }

print("Utils loaded successfully")