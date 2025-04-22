#!/usr/bin/env python3

from typing import Dict, Any, List, Tuple
import re
import os
import json

def normalize_number(value: Any) -> float:
    """Normalize a value to a float for comparison"""
    if isinstance(value, (int, float)):
        return float(value)
    elif isinstance(value, str):
        # Remove commas, spaces, currency symbols, and try to convert
        clean_str = re.sub(r'[,$\s]', '', value)
        try:
            return float(clean_str)
        except ValueError:
            pass
    return None

def values_match(value1: Any, value2: Any, tolerance: float = 0.01) -> bool:
    """Check if two values match within a tolerance"""
    num1 = normalize_number(value1)
    num2 = normalize_number(value2)
    
    # If both are numbers, check if they're close
    if num1 is not None and num2 is not None:
        # If either value is zero
        if abs(num1) < 1e-10 and abs(num2) < 1e-10:
            return True
        
        # Calculate relative difference
        max_val = max(abs(num1), abs(num2))
        if max_val > 0:
            rel_diff = abs(num1 - num2) / max_val
            return rel_diff <= tolerance
    
    # If they're not numbers, check string equality
    return str(value1).strip().lower() == str(value2).strip().lower()

def validate_mapping(standardized_data: Dict[str, Any], 
                    raw_data: Dict[str, Any],
                    mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Validate that standardized values match the raw data
    
    Args:
        standardized_data: Standardized financial data
        raw_data: Raw financial data
        mapping: Mapping from raw keys to standardized keys
        
    Returns:
        List of validation results
    """
    results = []
    
    # Invert the mapping to get standardized_key -> raw_key
    inverted_mapping = {}
    for raw_key, std_key in mapping.items():
        if std_key in inverted_mapping:
            if not isinstance(inverted_mapping[std_key], list):
                inverted_mapping[std_key] = [inverted_mapping[std_key]]
            inverted_mapping[std_key].append(raw_key)
        else:
            inverted_mapping[std_key] = raw_key
    
    # Check each standardized field
    for std_key, std_value in standardized_data.items():
        # Skip fields not in the mapping
        if std_key not in inverted_mapping:
            results.append({
                "standardized_key": std_key,
                "raw_key": None,
                "standardized_value": std_value,
                "raw_value": None,
                "is_valid": False,
                "reason": "Standardized key not in mapping"
            })
            continue
            
        raw_keys = inverted_mapping[std_key]
        if not isinstance(raw_keys, list):
            raw_keys = [raw_keys]
            
        # Try each possible raw key
        found_match = False
        for raw_key in raw_keys:
            if raw_key.lower() in raw_data:
                raw_value = raw_data[raw_key.lower()]
                if values_match(std_value, raw_value):
                    results.append({
                        "standardized_key": std_key,
                        "raw_key": raw_key,
                        "standardized_value": std_value,
                        "raw_value": raw_value,
                        "is_valid": True,
                        "reason": "Values match"
                    })
                    found_match = True
                    break
                else:
                    results.append({
                        "standardized_key": std_key,
                        "raw_key": raw_key,
                        "standardized_value": std_value,
                        "raw_value": raw_value,
                        "is_valid": False,
                        "reason": "Values don't match"
                    })
                    found_match = True
                    break
        
        if not found_match:
            results.append({
                "standardized_key": std_key,
                "raw_key": raw_keys,
                "standardized_value": std_value,
                "raw_value": None,
                "is_valid": False,
                "reason": "Raw key not found in data"
            })
                
    return results

def generate_validation_report(validation_results: List[Dict[str, Any]], output_file: str) -> None:
    """
    Generate a validation report file
    
    Args:
        validation_results: Results from validate_mapping
        output_file: Path to the output file
    """
    # Create directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_file, 'w') as f:
        f.write("Validation Report\n")
        f.write("================\n\n")
        
        # Count valid/invalid mappings
        valid_count = sum(1 for r in validation_results if r["is_valid"])
        total_count = len(validation_results)
        
        f.write(f"Total mappings: {total_count}\n")
        f.write(f"Valid mappings: {valid_count}\n")
        f.write(f"Invalid mappings: {total_count - valid_count}\n\n")
        
        # Group by validity
        f.write("Invalid Mappings:\n")
        f.write("-----------------\n")
        for result in validation_results:
            if not result["is_valid"]:
                f.write(f"- {result['standardized_key']}: {result['reason']}\n")
                if result['raw_key']:
                    if isinstance(result['raw_key'], list):
                        f.write(f"  Raw keys: {', '.join(result['raw_key'])}\n")
                    else:
                        f.write(f"  Raw key: {result['raw_key']}\n")
                f.write(f"  Standardized value: {result['standardized_value']}\n")
                if result['raw_value'] is not None:
                    f.write(f"  Raw value: {result['raw_value']}\n")
                f.write("\n")
        
        # Detailed results
        f.write("\nDetailed Results:\n")
        f.write("----------------\n")
        for i, result in enumerate(validation_results, 1):
            status = "✓" if result["is_valid"] else "✗"
            f.write(f"{i}. [{status}] {result['standardized_key']}\n")
            f.write(f"   Reason: {result['reason']}\n")
            if result['raw_key']:
                if isinstance(result['raw_key'], list):
                    f.write(f"   Raw keys: {', '.join(result['raw_key'])}\n")
                else:
                    f.write(f"   Raw key: {result['raw_key']}\n")
            f.write(f"   Standardized value: {result['standardized_value']}\n")
            if result['raw_value'] is not None:
                f.write(f"   Raw value: {result['raw_value']}\n")
            f.write("\n")

def main() -> bool:
    """Main function for standalone validation using existing codebase files"""
    
    # Paths to existing files from the codebase
    financial_data_file = "financial_data.json"
    financial_summary_file = "financial_summary.json"
    mapping_file = "standarize_mapping.py"
    output_dir = "."
    
    try:
        # Load financial data
        print(f"Loading financial data from: {financial_data_file}")
        with open(financial_data_file, 'r') as f:
            financial_data = json.load(f)
        
        # Load financial summary (standardized data)
        print(f"Loading standardized financial data from: {financial_summary_file}")
        with open(financial_summary_file, 'r') as f:
            financial_summary = json.load(f)
        
        # Extract mapping from standarize_mapping.py
        print(f"Extracting mapping from: {mapping_file}")
        mapping = {}
        with open(mapping_file, 'r') as f:
            for line in f:
                if ':' in line and '=' not in line and 'class' not in line and 'def' not in line:
                    # Extract key-value pairs from the MAPPING dictionary in the file
                    parts = line.strip().strip(',').split(':')
                    if len(parts) == 2:
                        key = parts[0].strip().strip('"\'')
                        value = parts[1].strip().strip('"\'')
                        if key and value:
                            mapping[key] = value
        
        # Process each company's data
        for company_id, company_summary in financial_summary.items():
            print(f"\nValidating data for company ID: {company_id}")
            
            # Get the raw data for this company
            
            if company_id in financial_data:
                # Find the latest filing that matches the period_end date
                target_period = company_summary.get("period_end")
                raw_data = {}
                
                for filing in financial_data[company_id]:
                    if filing.get("metadata", {}).get("period_end") == target_period:
                        # Combine balance sheet and income statement
                        raw_data.update(filing.get("balance_sheet", {}))
                        raw_data.update(filing.get("income_statement", {}))
                        break
                
                if raw_data:
                    # Convert keys to lowercase for case-insensitive matching
                    raw_data = {k.lower(): v for k, v in raw_data.items()}
                    
                    # Get standardized data (key metrics)
                    standardized_data = company_summary.get("key_metrics", {})
                    
                    # Validate the data
                    output_file = os.path.join(output_dir, f"validation_report_{company_id}.txt")
                    results = validate_mapping(standardized_data, raw_data, mapping)
                    generate_validation_report(results, output_file)
                    
                    valid_count = sum(1 for r in results if r["is_valid"])
                    total_count = len(results)
                    print(f"Validation complete: {valid_count}/{total_count} valid mappings")
                    print(f"Report saved to: {output_file}")
                else:
                    print(f"No matching filing found for period {target_period}")
            else:
                print(f"No financial data found for company ID: {company_id}")
        
        # Also create a validation log
        with open("validation.log", "w") as log:
            log.write(f"Validation run: {os.path.basename(__file__)}\n")
            log.write(f"Financial data file: {financial_data_file}\n")
            log.write(f"Financial summary file: {financial_summary_file}\n")
            log.write(f"Mapping file: {mapping_file}\n")
        
        return True
        
    except Exception as e:
        print(f"Error during validation: {str(e)}")
        return False

if __name__ == "__main__":
    main() 