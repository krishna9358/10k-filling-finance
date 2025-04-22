#!/usr/bin/env python3

import os
import re
import json
import logging
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Financial statement sections
BALANCE_SHEET_ITEMS = [
    'CASH', 'SECURITIES', 'RECEIVABLES', 'ALLOWANCES', 'INVENTORY', 
    'CURRENT-ASSETS', 'PP&E', 'DEPRECIATION', 'TOTAL-ASSETS',
    'CURRENT-LIABILITIES', 'BONDS', 'PREFERRED-MANDATORY', 'PREFERRED',
    'COMMON', 'OTHER-SE', 'TOTAL-LIABILITY-AND-EQUITY'
]

INCOME_STATEMENT_ITEMS = [
    'SALES', 'TOTAL-REVENUES', 'CGS', 'TOTAL-COSTS', 'OTHER-EXPENSES',
    'LOSS-PROVISION', 'INTEREST-EXPENSE', 'INCOME-PRETAX', 'INCOME-TAX',
    'INCOME-CONTINUING', 'DISCONTINUED', 'EXTRAORDINARY', 'CHANGES',
    'NET-INCOME', 'EPS-BASIC', 'EPS-PRIMARY', 'EPS-DILUTED'
]

def extract_financial_data(file_path):
    """
    Extract financial data from a SEC filing.
    
    Args:
        file_path (str): Path to the SEC filing file
        
    Returns:
        dict: Extracted financial data organized by statement type
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            
        # Extract the ARTICLE section which contains financial data
        article_match = re.search(r'<ARTICLE>.*?</TABLE>', content, re.DOTALL)
        if not article_match:
            logger.warning(f"No ARTICLE section found in {file_path}")
            return None
            
        article_content = article_match.group(0)
        
        # Extract period information
        period_type_match = re.search(r'<PERIOD-TYPE>\s*(.*?)\s*\n', article_content)
        period_type = period_type_match.group(1).strip() if period_type_match else "Unknown"
        
        fiscal_year_end_match = re.search(r'<FISCAL-YEAR-END>\s*(.*?)\s*\n', article_content)
        fiscal_year_end = fiscal_year_end_match.group(1).strip() if fiscal_year_end_match else "Unknown"
        
        period_end_match = re.search(r'<PERIOD-END>\s*(.*?)\s*\n', article_content)
        period_end = period_end_match.group(1).strip() if period_end_match else "Unknown"
        
        # Create a data structure to hold the financial information
        financial_data = {
            "metadata": {
                "period_type": period_type,
                "fiscal_year_end": fiscal_year_end,
                "period_end": period_end,
                "source_file": os.path.basename(file_path),
                "extraction_date": datetime.now().strftime("%Y-%m-%d")
            },
            "balance_sheet": {},
            "income_statement": {},
            "other_financial_data": {}
        }
        
        # Extract all financial items using regex
        for item in BALANCE_SHEET_ITEMS:
            match = re.search(rf'<{item}>\s*(.*?)\s*\n', article_content)
            if match:
                try:
                    value = match.group(1).strip()
                    # Try to convert to number if possible
                    try:
                        if '.' in value:
                            financial_data["balance_sheet"][item.lower()] = float(value)
                        else:
                            financial_data["balance_sheet"][item.lower()] = int(value)
                    except ValueError:
                        financial_data["balance_sheet"][item.lower()] = value
                except Exception as e:
                    logger.error(f"Error processing {item}: {str(e)}")
        
        # Extract income statement items
        for item in INCOME_STATEMENT_ITEMS:
            match = re.search(rf'<{item}>\s*(.*?)\s*\n', article_content)
            if match:
                try:
                    value = match.group(1).strip()
                    # Try to convert to number if possible
                    try:
                        if '.' in value:
                            financial_data["income_statement"][item.lower()] = float(value)
                        else:
                            financial_data["income_statement"][item.lower()] = int(value)
                    except ValueError:
                        financial_data["income_statement"][item.lower()] = value
                except Exception as e:
                    logger.error(f"Error processing {item}: {str(e)}")
        
        # Extract any other financial data elements 
        soup = BeautifulSoup(article_content, 'html.parser')
        for tag in soup.find_all():
            if tag.name and tag.name not in BALANCE_SHEET_ITEMS and tag.name not in INCOME_STATEMENT_ITEMS and tag.name != 'ARTICLE':
                if tag.text.strip():
                    try:
                        key = tag.name.lower()
                        value = tag.text.strip()
                        
                        # Try to convert to number if possible
                        try:
                            if '.' in value:
                                financial_data["other_financial_data"][key] = float(value)
                            else:
                                financial_data["other_financial_data"][key] = int(value)
                        except ValueError:
                            financial_data["other_financial_data"][key] = value
                    except Exception as e:
                        logger.error(f"Error processing tag {tag.name}: {str(e)}")
        
        return financial_data
    
    except Exception as e:
        logger.error(f"Error extracting financial data from {file_path}: {str(e)}")
        return None

def process_sec_filings(base_directory):
    """
    Process all SEC filings in the given directory.
    
    Args:
        base_directory (str): Base directory containing SEC filings
        
    Returns:
        dict: Financial data organized by year
    """
    all_data = {}
    
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            if file.endswith('.txt') and "full-submission" in file:
                file_path = os.path.join(root, file)
                logger.info(f"Processing {file_path}")
                
                # Extract the filing year from the directory structure
                # Expected format: .../10-K/0000104169-YY-XXXXXX/full-submission.txt
                match = re.search(r'/(\d{4})-(\d{6})/full-submission\.txt$', file_path)
                if match:
                    year = match.group(1)
                else:
                    # Try alternative pattern
                    match = re.search(r'(\d{4})(?=.*?/full-submission\.txt$)', file_path)
                    if match:
                        year = match.group(1)
                    else:
                        # Extract year from directory name as a fallback
                        parent_dir = os.path.basename(os.path.dirname(file_path))
                        year_match = re.search(r'(\d{4})', parent_dir)
                        year = year_match.group(1) if year_match else "unknown"
                
                financial_data = extract_financial_data(file_path)
                
                if financial_data:
                    if year not in all_data:
                        all_data[year] = []
                    
                    all_data[year].append(financial_data)
    
    # Sort data by years
    sorted_data = {k: all_data[k] for k in sorted(all_data.keys())}
    
    return sorted_data

def create_financial_json(input_dir, output_file="financial_data.json"):
    """
    Create a JSON file containing financial data from SEC filings.
    
    Args:
        input_dir (str): Input directory containing SEC filings
        output_file (str): Output JSON file name
    """
    logger.info(f"Processing SEC filings in {input_dir}")
    financial_data = process_sec_filings(input_dir)
    
    if not financial_data:
        logger.warning("No financial data extracted")
        return False
    
    # Write data to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(financial_data, f, indent=2)
    
    logger.info(f"Financial data saved to {output_file}")
    
    # Print summary
    total_years = len(financial_data)
    total_filings = sum(len(filings) for filings in financial_data.values())
    
    logger.info(f"Extracted financial data from {total_filings} filings across {total_years} years")
    
    return True

def create_financial_summary_json(input_dir, output_file="financial_summary.json"):
    """
    Create a summary JSON file with key metrics by year.
    
    Args:
        input_dir (str): Input directory containing SEC filings
        output_file (str): Output JSON file name
    """
    logger.info(f"Processing SEC filings in {input_dir} for summary")
    financial_data = process_sec_filings(input_dir)
    
    if not financial_data:
        logger.warning("No financial data extracted for summary")
        return False
    
    # Create a summary with key metrics by year
    summary = {}
    
    for year, filings in financial_data.items():
        if not filings:
            continue
            
        # Use the latest filing for the year
        filing = filings[-1]
        
        summary[year] = {
            "period_end": filing["metadata"]["period_end"],
            "key_metrics": {
                "revenue": filing["income_statement"].get("total-revenues", 
                          filing["income_statement"].get("sales", "N/A")),
                "net_income": filing["income_statement"].get("net-income", "N/A"),
                "eps_basic": filing["income_statement"].get("eps-basic", 
                            filing["income_statement"].get("eps-primary", "N/A")),
                "total_assets": filing["balance_sheet"].get("total-assets", "N/A"),
                "total_liabilities_equity": filing["balance_sheet"].get("total-liability-and-equity", "N/A"),
                "cash": filing["balance_sheet"].get("cash", "N/A"),
                "inventory": filing["balance_sheet"].get("inventory", "N/A")
            }
        }
    
    # Write summary to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Financial summary saved to {output_file}")
    return True

def main():
    """Main function to demonstrate usage"""
    # Specify the folder path containing SEC filings
    sec_filings_path = "sec-edgar-filings/WMT/10-K/"
    
    try:
        # Create detailed financial data JSON
        create_financial_json(sec_filings_path)
        
        # Create summary financial data JSON
        create_financial_summary_json(sec_filings_path)
        
        logger.info("Financial data extraction completed successfully")
        
    except Exception as e:
        logger.error(f"Error during financial data extraction: {str(e)}")

if __name__ == "__main__":
    main()
