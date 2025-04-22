1. data_extraction.py -> to get the 10-k filling data of company stores in sec-edgar-filling folder
2. financial_data_mapper.py -> to parse the data into json -> financial_data.json
3. standarize_mapping.py -> convert into standarize account mapping (normalizing for better reading) -> standard_finance_output.txt
4. validation.py -> to check raw data with mapped data correctness -> creates validation_report_xyz.txt
5. ratio_computation.py -> get the ratio gross margin and creates a file -> ratio_result.txt
6. main.py -> main file wchi runs to do all above automatically and gives final output. 