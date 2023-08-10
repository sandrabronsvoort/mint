from mint_package.data_import import read_data
from mint_package.mathematical_model import solve_model

# File path for Excel data
file_path = 'C:/mint/mint2/MINT_Excel_Template.xlsx'

def main():
    supply_chain_data = read_data(file_path)
    results = solve_model(supply_chain_data)
    print (results)

if __name__ == "__main__":
    main()
