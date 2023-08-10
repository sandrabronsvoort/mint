import pulp
import pandas as pd

# READ IN DATA

# File path for Excel data
FILE_PATH = 'C:/mint/mint2/MINT_Excel_Template.xlsx'

# Read Excel data
data = pd.read_excel(FILE_PATH, sheet_name=None)

# Define sets
factories = set(data['Factories']['Factory'].tolist())
products = set(data['Products']['Product'].tolist())
customers = set(data['Customers']['Customer'].tolist())
transport_modes = set(data['TransportModes']['Mode'].tolist())

# Extract data
product_weight_data = data['Products']['Weight (kg)'].tolist()
product_weight = dict(zip(products, product_weight_data))

demand_data = data['ProductDemand']

demand_dict = {
    customer: {
        product: demand_data.loc[
            (demand_data['Customer'] == customer) & (demand_data['Product'] == product),
            'Demand'
        ].values[0]
        for product in products
    }
    for customer in customers
}

transport_cost_data = data['TransportModes']['Cost (USD/tkm)'].tolist()
transport_costs = dict(zip(transport_modes, transport_cost_data))

transport_emissions_data = data['TransportModes']['CO2 emissions (g/tkm)'].tolist()
transport_emissions = dict(zip(transport_modes, transport_emissions_data))

from_locations = data['TransportLanes']['From'].tolist()
to_locations = data['TransportLanes']['To'].tolist()
distances = data['TransportLanes']['Distance (km)'].tolist()
distance_table = {}
for from_loc, to_loc, distance in zip(from_locations, to_locations, distances):
    if from_loc not in distance_table:
        distance_table[from_loc] = {}
    distance_table[from_loc][to_loc] = distance

transport_lane_data = data['TransportLanes']['Mode'].tolist()
transport_lane_modes = {(from_loc, to_loc): mode for from_loc, to_loc, mode in zip(
    from_locations, to_locations, transport_lane_data)}

production_data = data['ProductionData']
production_capacity = {(factory, product): capacity for factory, product, capacity in zip(
    production_data['Factory'], production_data['Product'], production_data['Capacity'])}
production_costs = {(factory, product): cost for factory, product, cost in zip(
    production_data['Factory'], production_data['Product'], production_data['Cost (USD)'])}
production_emissions = {(factory, product): emissions for factory, product, emissions in zip(
    production_data['Factory'], production_data['Product'], production_data['CO2 emissions (kg/unit)'])}


# MATHEMATICAL MODEL

# Define the problem
problem = pulp.LpProblem("Emissions minimization", pulp.LpMinimize)

# Define decision variables
production = pulp.LpVariable.dicts("Production", (factories, products),
                                   lowBound=0, cat="Continuous")
transport = pulp.LpVariable.dicts("Transport", (factories, customers, transport_modes, products),
                                  lowBound=0, cat="Continuous")

# Define objective function
total_production_emissions = pulp.lpSum(production_emissions[factory,product] *
                                        production[factory][product]
                                        for factory in factories
                                        for product in products
                                        )

total_transport_emissions = pulp.lpSum(transport_emissions[transport_mode]
                                       * distance_table[factory][customer]
                                       * transport[factory][customer][transport_mode][product]
                                for factory in factories
                                for customer in customers
                                for transport_mode in transport_modes
                                for product in products)

problem += total_production_emissions + total_transport_emissions

# Define constraints
           
# Production should cover product demand
for product in products:
    production_sum = pulp.lpSum(production[factory][product] for factory in factories)
    problem += production_sum >= sum(demand_dict[customer][product] for customer in customers)

# Production should respect capacity constraints
for factory in factories:
    for product in products:
        problem += production[factory][product] <= production_capacity[factory,product]

# Product demand should be met
for customer in customers:
    for product in products:
        demand = demand_dict.get(customer, {}).get(product,0)

        transport_sum = pulp.lpSum(transport[factory][customer][transport_mode][product]
                              for factory in factories
                              for transport_mode in transport_modes)
        
        problem += transport_sum >= demand

# Solve the problem
problem.solve()

# Calculate and print total costs per product
print("Total emissions:", pulp.value(problem.objective))

total_costs_per_product = {}

for product in products:
    total_production_cost = pulp.lpSum(
        production_costs[factory, product] * production[factory][product] for factory in factories)
    total_transport_cost = pulp.lpSum(
        transport_costs[transport_mode] * distance_table[factory][customer] *
        transport[factory][customer][transport_mode][product]
        for factory in factories
        for customer in customers
        for transport_mode in transport_modes
    ) * product_weight[product] / 1000

    total_cost = total_production_cost + total_transport_cost
    total_production_quantity = pulp.lpSum(production[factory][product] for factory in factories)
    
    if total_production_quantity.value() != 0:
        unit_cost = total_cost.value() / total_production_quantity.value()
        total_costs_per_product[product] = unit_cost
    else:
        total_costs_per_product[product] = float('inf')  # Handle division by zero

# Print total costs per product
for product, cost in total_costs_per_product.items():
    print(f"Total cost for Product {product}: {cost}")

# Print production quantities for each factory and product combination
for factory in factories:
    for product in products:
        production_value = production[factory][product].varValue
        print(f"Factory: {factory}, Product: {product}, Production Quantity: {production_value}")