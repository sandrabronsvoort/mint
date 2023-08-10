import pulp
import pandas as pd

def solve_model(supply_chain_data):

    # Get data
    data = supply_chain_data.get_data()
    suppliers = data['suppliers']
    factories = data['factories']
    products = data['products']
    customers = data['customers']
    transport_modes = data['transport_modes']
    product_weight = data['product_weight']
    demand_dict = data['demand_dict']
    transport_costs = data['transport_costs']
    transport_emissions = data['transport_emissions']
    distance_table = data['distances']
    transport_mode = data['transport_lane_modes']
    production_capacity = data['production_capacity']
    production_costs = data['production_costs']
    production_emissions = data['production_emissions']

    # Define the problem
    problem = pulp.LpProblem("Emissions_minimization", pulp.LpMinimize)

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
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    print("OPTIMIZATION RESULTS:\n")

    # Calculate and print total costs per product
    print(f"- Total emissions:", round(pulp.value(problem.objective)), "tonnes")

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
        print(f"- Total cost for Product {product}: {round(cost)} USD")

    # Print production quantities for each factory and product combination
    print("- Production quantities:")
    
    for factory in factories:
        for product in products:
            production_value = production[factory][product].varValue
            print(f"    - Production quantity for product {product} at factory {factory}: {round(production_value)} units")

    success_message = "\n\n-------------------------\n[     RUN SUCCESSFUL     ]\n-------------------------\n\n"
    return success_message