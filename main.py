from mint_package.data_import import read_data
from mint_package.mathematical_model import solve_model

# File path for Excel data
file_path = 'MINT_Excel_Template.xlsx'

def main():
    # Print
    print("\n\n-----------------------\n[     STARTING MINT     ]\n-----------------------\n\n")

    supply_chain_data = read_data(file_path)
    result = solve_model(supply_chain_data)
    print (result)

if __name__ == "__main__":
    main()
