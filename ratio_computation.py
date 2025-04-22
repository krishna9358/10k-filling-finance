from typing import Dict, Any, Optional, Union
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

@dataclass
class RatioResult:
    """Stores the result of a ratio calculation with metadata"""
    value: Optional[float]
    category: str
    description: str
    formula: str

class RatioCategory(Enum):
    """Categories for financial ratios"""
    LIQUIDITY = "Liquidity Ratios"
    PROFITABILITY = "Profitability Ratios"
    EFFICIENCY = "Efficiency Ratios"
    LEVERAGE = "Leverage Ratios"
    MARKET = "Market Value Ratios"

class FinancialRatios:
    """
    Calculates financial ratios from standardized financial data
    Designed to be extensible - add new ratio methods following the pattern
    """
    
    def __init__(self, data: Dict[str, Union[int, float, Decimal]]):
        self.data = {k: float(v) if v is not None else 0.0 for k, v in data.items()}
    
    def _safe_divide(self, numerator: float, denominator: float) -> Optional[float]:
        """Safely perform division handling zeros and None values"""
        try:
            if denominator == 0:
                return None
            return round(numerator / denominator, 4)
        except (TypeError, ValueError):
            return None
    
    def _get_value(self, key: str) -> float:
        """Safely get a value from the data dictionary"""
        return self.data.get(key, 0.0)

    # === Liquidity Ratios ===
    
    def current_ratio(self) -> RatioResult:
        """Current assets / Current liabilities"""
        value = self._safe_divide(
            self._get_value("current_assets"),
            self._get_value("current_liabilities")
        )
        return RatioResult(
            value=value,
            category=RatioCategory.LIQUIDITY.value,
            description="Measures company's ability to pay short-term obligations",
            formula="Current Assets / Current Liabilities"
        )

    def quick_ratio(self) -> RatioResult:
        """(Cash + Marketable Securities + Receivables) / Current Liabilities"""
        quick_assets = sum([
            self._get_value("cash_and_equivalents"),
            self._get_value("marketable_securities"),
            self._get_value("accounts_receivable")
        ])
        value = self._safe_divide(quick_assets, self._get_value("current_liabilities"))
        return RatioResult(
            value=value,
            category=RatioCategory.LIQUIDITY.value,
            description="Measures company's ability to meet short-term obligations with most liquid assets",
            formula="(Cash + Marketable Securities + Receivables) / Current Liabilities"
        )

    def cash_ratio(self) -> RatioResult:
        """Cash / Current Liabilities"""
        value = self._safe_divide(
            self._get_value("cash_and_equivalents"),
            self._get_value("current_liabilities")
        )
        return RatioResult(
            value=value,
            category=RatioCategory.LIQUIDITY.value,
            description="Measures ability to pay off short-term liabilities with cash",
            formula="Cash / Current Liabilities"
        )

    # === Profitability Ratios ===
    
    def gross_margin(self) -> RatioResult:
        """(Revenue - COGS) / Revenue"""
        revenue = self._get_value("revenue")
        cogs = self._get_value("cost_of_goods_sold")
        value = self._safe_divide(revenue - cogs, revenue)
        return RatioResult(
            value=value,
            category=RatioCategory.PROFITABILITY.value,
            description="Measures company's efficiency at managing cost of goods sold",
            formula="(Revenue - COGS) / Revenue"
        )

    def operating_margin(self) -> RatioResult:
        """Operating Income / Revenue"""
        value = self._safe_divide(
            self._get_value("operating_income"),
            self._get_value("revenue")
        )
        return RatioResult(
            value=value,
            category=RatioCategory.PROFITABILITY.value,
            description="Measures profitability from core business operations",
            formula="Operating Income / Revenue"
        )

    def net_profit_margin(self) -> RatioResult:
        """Net Income / Revenue"""
        value = self._safe_divide(
            self._get_value("net_income"),
            self._get_value("revenue")
        )
        return RatioResult(
            value=value,
            category=RatioCategory.PROFITABILITY.value,
            description="Measures overall profitability after all expenses",
            formula="Net Income / Revenue"
        )

    def return_on_assets(self) -> RatioResult:
        """Net Income / Total Assets"""
        value = self._safe_divide(
            self._get_value("net_income"),
            self._get_value("total_assets")
        )
        return RatioResult(
            value=value,
            category=RatioCategory.PROFITABILITY.value,
            description="Measures how efficiently company uses assets to generate profit",
            formula="Net Income / Total Assets"
        )

    def return_on_equity(self) -> RatioResult:
        """Net Income / Total Equity"""
        value = self._safe_divide(
            self._get_value("net_income"),
            self._get_value("total_equity")
        )
        return RatioResult(
            value=value,
            category=RatioCategory.PROFITABILITY.value,
            description="Measures return generated on shareholders' equity",
            formula="Net Income / Total Equity"
        )

    # === Efficiency Ratios ===
    
    def asset_turnover(self) -> RatioResult:
        """Revenue / Total Assets"""
        value = self._safe_divide(
            self._get_value("revenue"),
            self._get_value("total_assets")
        )
        return RatioResult(
            value=value,
            category=RatioCategory.EFFICIENCY.value,
            description="Measures how efficiently company uses assets to generate sales",
            formula="Revenue / Total Assets"
        )

    def inventory_turnover(self) -> RatioResult:
        """COGS / Average Inventory"""
        value = self._safe_divide(
            self._get_value("cost_of_goods_sold"),
            self._get_value("inventory")
        )
        return RatioResult(
            value=value,
            category=RatioCategory.EFFICIENCY.value,
            description="Measures how many times inventory is sold and replaced",
            formula="COGS / Average Inventory"
        )

    def receivables_turnover(self) -> RatioResult:
        """Net Credit Sales / Average Accounts Receivable"""
        value = self._safe_divide(
            self._get_value("revenue"),
            self._get_value("accounts_receivable")
        )
        return RatioResult(
            value=value,
            category=RatioCategory.EFFICIENCY.value,
            description="Measures how efficiently company collects debt",
            formula="Net Credit Sales / Average Accounts Receivable"
        )

    # === Leverage Ratios ===
    
    def debt_to_equity(self) -> RatioResult:
        """Total Liabilities / Total Equity"""
        value = self._safe_divide(
            self._get_value("total_liabilities"),
            self._get_value("total_equity")
        )
        return RatioResult(
            value=value,
            category=RatioCategory.LEVERAGE.value,
            description="Measures financial leverage and risk",
            formula="Total Liabilities / Total Equity"
        )

    def debt_ratio(self) -> RatioResult:
        """Total Liabilities / Total Assets"""
        value = self._safe_divide(
            self._get_value("total_liabilities"),
            self._get_value("total_assets")
        )
        return RatioResult(
            value=value,
            category=RatioCategory.LEVERAGE.value,
            description="Measures percentage of assets financed with debt",
            formula="Total Liabilities / Total Assets"
        )

    def interest_coverage(self) -> RatioResult:
        """EBIT / Interest Expense"""
        value = self._safe_divide(
            self._get_value("operating_income"),
            self._get_value("interest_expense")
        )
        return RatioResult(
            value=value,
            category=RatioCategory.LEVERAGE.value,
            description="Measures ability to pay interest on debt",
            formula="EBIT / Interest Expense"
        )

    def calculate_all_ratios(self) -> Dict[str, Dict[str, RatioResult]]:
        """
        Calculate all available ratios and return them grouped by category
        """
        # Get all methods that return RatioResult
        ratio_methods = [
            method for method in dir(self) 
            if callable(getattr(self, method)) 
            and not method.startswith('_')
            and method != 'calculate_all_ratios'
        ]
        
        # Calculate all ratios and group by category
        results: Dict[str, Dict[str, RatioResult]] = {}
        for method_name in ratio_methods:
            method = getattr(self, method_name)
            result = method()
            
            if result.category not in results:
                results[result.category] = {}
            
            results[result.category][method_name] = result
            
        return results

def format_ratio_results(results: Dict[str, Dict[str, RatioResult]]) -> str:
    """Format ratio results into a readable string"""
    output = []
    
    for category, ratios in results.items():
        output.append(f"\n=== {category} ===\n")
        
        for name, result in ratios.items():
            ratio_name = name.replace('_', ' ').title()
            value = f"{result.value:.4f}" if result.value is not None else "N/A"
            
            output.append(f"{ratio_name}:")
            output.append(f"  Value: {value}")
            output.append(f"  Formula: {result.formula}")
            output.append(f"  Description: {result.description}")
            output.append("")
    
    return "\n".join(output)

def load_financial_data(filepath="financial_data.json"):
    """
    Load financial data from the JSON file
    
    Args:
        filepath (str): Path to the financial data JSON file
        
    Returns:
        dict: Standardized financial data for ratio computation
    """
    import json
    
    # Load the data
    try:
        with open(filepath, 'r') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Unable to decode JSON from {filepath}.")
        return None
    
    # For simplicity, use the most recent data from the first company ("0000")
    if "0000" not in raw_data or not raw_data["0000"]:
        print("Error: No data found for company '0000'.")
        return None
    
    # Get the most recent filing (last in the list)
    latest_filing = raw_data["0000"][-1]
    
    # Extract and standardize the data
    balance_sheet = latest_filing.get("balance_sheet", {})
    income_statement = latest_filing.get("income_statement", {})
    
    # Combine and standardize the data
    standardized_data = {}
    
    # Process numeric values (remove commas and convert to float)
    def process_value(value):
        if isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            # Remove commas and try to convert to float
            cleaned = value.replace(',', '')
            try:
                return float(cleaned)
            except ValueError:
                # Handle parentheses for negative values
                if cleaned.startswith('(') and cleaned.endswith(')'):
                    try:
                        return -float(cleaned[1:-1].replace(',', ''))
                    except ValueError:
                        return 0.0
                return 0.0
        return 0.0
    
    # Map the financial data to standardized keys
    mapping = {
        # Balance sheet
        "cash": "cash_and_equivalents",
        "securities": "marketable_securities",
        "receivables": "accounts_receivable",
        "inventory": "inventory",
        "current-assets": "current_assets",
        "total-assets": "total_assets",
        "current-liabilities": "current_liabilities",
        "total-liability-and-equity": "total_liabilities_and_equity",
        "bonds": "long_term_debt",
        "common": "common_stock",
        "other-se": "retained_earnings",
        
        # Income statement
        "sales": "revenue",
        "total-revenues": "total_revenue",
        "cgs": "cost_of_goods_sold",
        "interest-expense": "interest_expense",
        "income-pretax": "income_before_tax",
        "income-tax": "income_tax",
        "net-income": "net_income",
        "other-expenses": "operating_expenses",
        "income-continuing": "operating_income"
    }
    
    # Map and standardize values from balance sheet
    for src_key, std_key in mapping.items():
        if src_key in balance_sheet:
            standardized_data[std_key] = process_value(balance_sheet[src_key])
        elif src_key in income_statement:
            standardized_data[std_key] = process_value(income_statement[src_key])
    
    # Calculate total equity if not directly available
    if "total_equity" not in standardized_data:
        # Simplified: total equity = total assets - total liabilities
        total_assets = standardized_data.get("total_assets", 0)
        total_liabilities = standardized_data.get("total_liabilities", 0)
        
        # If total_liabilities is not available, try to calculate from total_liabilities_and_equity
        if total_liabilities == 0 and "total_liabilities_and_equity" in standardized_data:
            # In a balanced statement: assets = liabilities + equity
            # So: equity = assets - liabilities
            # If we don't have liabilities directly, we can use this relationship
            standardized_data["total_equity"] = standardized_data.get("common_stock", 0) + standardized_data.get("retained_earnings", 0)
    
    # Add multiplier if available to scale the values appropriately
    multiplier = 1.0
    if "other_financial_data" in latest_filing and "multiplier" in latest_filing["other_financial_data"]:
        multiplier_str = latest_filing["other_financial_data"]["multiplier"]
        if multiplier_str == "1,000":
            multiplier = 1000
        elif multiplier_str == "1,000,000":
            multiplier = 1000000
    
    # Apply multiplier to all numeric values
    for key, value in standardized_data.items():
        if isinstance(value, (int, float)):
            standardized_data[key] = value * multiplier
    
    return standardized_data

def main():
    # Load real financial data from the JSON file
    financial_data = load_financial_data()
    
    if not financial_data:
        print("Using sample data as fallback...")
        # Use sample data as fallback if real data couldn't be loaded
        financial_data = {
            "cash_and_equivalents": 1000000,
            "marketable_securities": 500000,
            "accounts_receivable": 750000,
            "inventory": 1500000,
            "current_assets": 4000000,
            "total_assets": 10000000,
            "current_liabilities": 2000000,
            "total_liabilities": 6000000,
            "total_equity": 4000000,
            "revenue": 12000000,
            "cost_of_goods_sold": 8000000,
            "operating_income": 2500000,
            "interest_expense": 400000,
            "net_income": 1800000
        }
    else:
        print("Using real financial data from financial_data.json")

    # Calculate ratios
    calculator = FinancialRatios(financial_data)
    results = calculator.calculate_all_ratios()
    
    # Format and display results
    formatted_results = format_ratio_results(results)
    print(formatted_results)
    
    # Save the results to a file
    with open("ratio_results.txt", "w") as f:
        f.write("Financial Ratios Calculation Results\n")
        f.write("==================================\n\n")
        f.write(formatted_results)
    
    print("\nResults have been saved to ratio_results.txt")

if __name__ == "__main__":
    main()
