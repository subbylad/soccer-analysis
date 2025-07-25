# Data Scripts

Utilities for downloading and cleaning soccer data.

## Scripts

### `data_loader.py`
Downloads raw soccer data from FBref API:
- Player statistics (standard, shooting, passing, defense)
- Team statistics
- Caches data locally

### `data_cleaner.py`
Cleans and standardizes the raw data:
- Fixes column naming issues
- Standardizes position names
- Converts data types
- Organizes data into clean/ directory

## Usage

```bash
# Download fresh data
python3 scripts/data_loader.py

# Clean the data
python3 scripts/data_cleaner.py
```

## Data Structure

- `data/raw/` - Original downloaded data
- `data/clean/` - Processed, analysis-ready data