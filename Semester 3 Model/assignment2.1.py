from gurobipy import Model, GRB
import gurobipy as gb
import pandas as pd

# Assume the dataset is loaded into a variable named 'data'
# Assuming 'data' is your DataFrame loaded with TechEssentials Inc.'s product data
data = pd.DataFrame({
    'Product': ['Line 1 Product 1', 'Line 1 Product 2', 'Line 1 Product 3',
                'Line 2 Product 1', 'Line 2 Product 2', 'Line 2 Product 3',
                'Line 3 Product 1', 'Line 3 Product 2', 'Line 3 Product 3'],
    'Intercept': [35234.545786, 37790.240832, 35675.333217, 37041.380378, 36846.140386,
                  34567.890123, 37890.123456, 38901.234567, 39012.345678],
    'Sensitivity': [-45.896450, -8.227794, -7.584436, -9.033166, -4.427869,
                    -6.789012, -5.678901, -4.567890, -3.456789],
    'Capacity': [80020.0, 89666.0, 80638.0, 86740.0, 84050.0,
                 82000.0, 91000.0, 90000.0, 89000.0]
})

# Cross-elasticity factor
cross_elasticity = 0.1

# Create a new model
model = Model("TechEssentials Pricing Optimization with Capacity")

# Decision variables: Price for each of the 9 products
prices = model.addVars(len(data), lb=0, vtype=GRB.CONTINUOUS, name="Price")

# Demand variables for each product, adjusted for cross-elasticity and data-driven
demands = model.addVars(len(data), lb=0, vtype=GRB.CONTINUOUS, name="Demand")

# Update demand calculations to include data-driven parameters and cross-elasticity
def demand(i, prices):
    base_demand = data.at[i, 'Intercept']
    price_sensitivity = data.at[i, 'Sensitivity']
    demand = base_demand + price_sensitivity * prices[i]
    # Simplified cross-elasticity effect using a dummy value
    dummy_cross_elasticity = 0.1  # This is a placeholder value
    for j in range(len(data)):
        if j != i:  # Assuming all products have some level of interaction
            demand += cross_elasticity * (prices[j] - prices[i])  # Dummy interaction
    return demand

# Capacity constraints
for i in range(len(data)):
    capacity = data.loc[i, 'Capacity']
    model.addConstr(demands[i] <= capacity, name=f"Capacity_{i}")

# Objective: Maximize total revenue
model.setObjective(gb.quicksum(prices[i] * demands[i] for i in range(len(data))), GRB.MAXIMIZE)

# Optimize the model
model.optimize()

# Display results (Pseudo-code; replace with actual Gurobi syntax if running in a compatible environment)
if model.status == GRB.OPTIMAL:
    print("Optimal Total Revenue: ${:.2f}".format(model.ObjVal))
    print("Optimal Prices and Expected Demands:")
    for i in range(len(data)):
        print(f"{data.loc[i, 'Product']}: Price = ${prices[i].X:.2f}, Demand = {demands[i].X:.0f}")
else:
    print("Optimal solution was not found.")