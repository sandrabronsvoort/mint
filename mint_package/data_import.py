import pandas as pd

class DataContainer:
    def __init__(self, suppliers, factories, products, customers, transport_modes, product_weight, demand_dict,
                 transport_costs, transport_emissions, distances_table, transport_lane_modes,
                 production_capacity, production_costs, production_emissions):
        self.suppliers = suppliers
        self.factories = factories
        self.products = products
        self.customers = customers
        self.transport_modes = transport_modes
        self.product_weight = product_weight
        self.demand_dict = demand_dict
        self.transport_costs = transport_costs
        self.transport_emissions = transport_emissions
        self.distances = distances_table
        self.transport_lane_modes = transport_lane_modes
        self.production_capacity = production_capacity
        self.production_costs = production_costs
        self.production_emissions = production_emissions

    def get_data(self):
        return {
            'suppliers': self.suppliers,
            'factories': self.factories,
            'products': self.products,
            'customers': self.customers,
            'transport_modes': self.transport_modes,
            'product_weight': self.product_weight,
            'demand_dict': self.demand_dict,
            'transport_costs': self.transport_costs,
            'transport_emissions': self.transport_emissions,
            'distances': self.distances,
            'transport_lane_modes': self.transport_lane_modes,
            'production_capacity': self.production_capacity,
            'production_costs': self.production_costs,
            'production_emissions': self.production_emissions
        }

def read_data(file_path):

    # Read Excel data
    data = pd.read_excel(file_path, sheet_name=None)

    # Define sets
    suppliers = set(data['Suppliers']['Supplier'].tolist())
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
                (demand_data['Customer'] == customer) & (
                    demand_data['Product'] == product),
                'Demand'
            ].values[0]
            for product in products
        }
        for customer in customers
    }

    transport_cost_data = data['TransportModes']['Cost (USD/tkm)'].tolist()
    transport_costs = dict(zip(transport_modes, transport_cost_data))

    transport_emissions_data = data['TransportModes']['CO2 emissions (g/tkm)'].tolist(
    )
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

    # Print data summary
    print("SUPPLY CHAIN SUMMARY:\n")
    print(f"- {len(suppliers)} suppliers")
    print(f"- {len(factories)} factories")
    print(f"- {len(products)} products")
    print(f"- {len(customers)} customers")
    print(f"- {len(transport_modes)} transport modes")
    print("\n\n")

    # Return data
    return DataContainer(suppliers, factories, products, customers, transport_modes, product_weight, demand_dict, transport_costs, transport_emissions, distance_table, transport_lane_modes, production_capacity, production_costs, production_emissions)
