from pprint import pprint
import json

# Define mapping from XBRL/raw tags to standardized financial concepts
MAPPING = {
    # Balance Sheet mappings
    "us-gaap:CashAndCashEquivalentsAtCarryingValue": "cash_and_equivalents",
    "us-gaap:Assets": "total_assets",
    "us-gaap:LiabilitiesCurrent": "current_liabilities",
    "us-gaap:StockholdersEquity": "total_equity",
    "cash": "cash_and_equivalents",
    "securities": "marketable_securities",
    "receivables": "accounts_receivable",
    "inventory": "inventory",
    "current-assets": "current_assets",
    "pp&e": "property_plant_equipment",
    "depreciation": "accumulated_depreciation",
    "total-assets": "total_assets",
    "current-liabilities": "current_liabilities",
    "common": "common_stock",
    "other-se": "additional_paid_in_capital",
    "total-liability-and-equity": "total_liabilities_and_equity",
    
    # Income Statement mappings
    "sales": "revenue",
    "total-revenues": "total_revenue",
    "cgs": "cost_of_goods_sold",
    "total-costs": "total_expenses",
    "interest-expense": "interest_expense",
    "income-pretax": "income_before_tax",
    "income-tax": "income_tax_expense",
    "net-income": "net_income",
    "eps-basic": "earnings_per_share_basic",
    "eps-diluted": "earnings_per_share_diluted"
}

class FinancialDataParser:
    """Parser for financial data from various sources to a standardized format"""
    
    def __init__(self, mapping=None):
        """Initialize with optional custom mapping"""
        self.mapping = mapping or MAPPING
    
    def parse(self, data):
        """
        Parse financial data into standardized format
        
        Args:
            data (dict): Raw financial data
            
        Returns:
            dict: Standardized financial data
        """
        standardized = {}
        
        # Process each item in the data
        for key, value in data.items():
            # Convert string values to numeric when possible
            if isinstance(value, str) and value.replace(',', '').replace('.', '').isdigit():
                # Handle numbers with commas
                cleaned_value = value.replace(',', '')
                if '.' in cleaned_value:
                    value = float(cleaned_value)
                else:
                    value = int(cleaned_value)
                    
            # Map to standardized key if available
            std_key = self.mapping.get(key.lower())
            if std_key:
                standardized[std_key] = value
                
        return standardized

def load_financial_data(file_path):
    """Load financial data from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_yearly_data(financial_data):
    """Extract yearly data from the financial data structure"""
    yearly_data = {}
    
    # Process data for each year
    for year_key, filings in financial_data.items():
        if not filings:
            continue
            
        # Use the latest filing for each year
        latest_filing = filings[-1]
        
        # Combine balance sheet and income statement data
        combined_data = {}
        combined_data.update(latest_filing.get('balance_sheet', {}))
        combined_data.update(latest_filing.get('income_statement', {}))
        
        # Add metadata
        period_end = latest_filing.get('metadata', {}).get('period_end', '')
        
        yearly_data[year_key] = {
            'period_end': period_end,
            'raw_data': combined_data
        }
    
    return yearly_data

def main():
    """Main function to demonstrate the financial data standardization"""    
    # Create parser and standardize the data
    parser = FinancialDataParser()
    
    try:
        # Load and process data from financial_data.json
        financial_data = load_financial_data('financial_data.json')
        yearly_data = extract_yearly_data(financial_data)
        
        # Open file for writing the standardized data
        with open('standard_finance_output.txt', 'w') as f:
            f.write("Standardized data from financial_data.json:\n")
            for year, data in yearly_data.items():
                standardized = parser.parse(data['raw_data'])
                f.write(f"\nYear: {year} (Period ending: {data['period_end']})\n")
                # Use pformat for pretty formatting the dictionary
                from pprint import pformat
                f.write(pformat(standardized))
                f.write('\n')
                
                # Validate the standardized data against raw data
                from validation import validate_mapping, generate_validation_report
                validation_results = validate_mapping(standardized, data['raw_data'], MAPPING)
                generate_validation_report(validation_results, f'validation_report_{year}.txt')
                
    except Exception as e:
        print(f"Error processing financial_data.json: {str(e)}")

if __name__ == "__main__":
    main()
