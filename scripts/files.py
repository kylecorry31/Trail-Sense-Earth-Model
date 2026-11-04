def monthly_files(start_year, end_year, name):
    """The climate normal image of each month (January to December) of a variable."""
    return [f"images/{start_year}-{end_year}-{month}-{name}.tif" for month in range(1, 13)]
