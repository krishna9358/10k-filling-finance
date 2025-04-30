# SEC Financial Data Analysis

This project extracts and analyzes financial data from SEC filings. The workflow includes:

1. `financial_data_mapper.py` - Parses the data into structured JSON format
2. `standarize_mapping.py` - Normalizes financial data with standardized account mapping 
3. `validation.py` - Validates standardized data against raw data
4. `ratio_computation.py` - Calculates financial ratios from standardized data
5. `main.py` - Main entry point that orchestrates all the above steps

## Installtion of requirements
` uv sync `

## Usage

The `main.py` script serves as a single point of contact, orchestrating the entire workflow:

```bash
# Run with a specific ticker symbol and your email
uv run main.py --ticker AAPL --email your.email@example.com

# Skip downloading new filings if they already exist
uv run main.py --ticker AAPL --email your.email@example.com --skip-download

# Use sample data instead of downloading real data
uv run main.py --ticker AAPL --email your.email@example.com --use-sample-data
```

### Command Line Arguments

- `--ticker`: Required. The stock ticker symbol (e.g., AAPL, MSFT, GOOG)
- `--email`: Required. Your email address for SEC EDGAR access
- `--skip-download`: Optional. Skip downloading new filings if they already exist
- `--use-sample-data`: Optional. Use built-in sample data without attempting to download

### Workflow Steps

When you run main.py, it executes these steps in sequence:

1. Downloads SEC filings for the specified ticker
2. Processes the filings and extracts financial data
3. Standardizes the data using the mapping definitions
4. Validates the standardized data against raw data
5. Computes financial ratios (final output)

### Fallback Handling

The script includes robust error handling:
- If downloading fails, it will create the necessary directory structure
- If financial data extraction fails, it will use sample data as a fallback
- If loading financial data fails, it will automatically use sample data

This ensures that the entire workflow can run successfully even if certain steps encounter issues.

### Output Files

The script generates:
- `financial_data.json` - Raw financial data extracted from SEC filings
- `financial_summary.json` - Processed financial summary
- `standard_finance_output.txt` - Standardized financial data
- `validation_report_{year}.txt` - Validation reports for each year
- `ratio_result.txt` - Financial ratio results (FINAL ANSWER)
- Console output with key financial metrics and ratios

## Requirements

This project requires the following Python packages (specified in pyproject.toml):
- beautifulsoup4
- lxml
- python-accounting
- requests
- sec-edgar-downloader
- urllib3 
