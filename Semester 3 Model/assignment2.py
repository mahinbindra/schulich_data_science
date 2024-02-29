from gurobipy import Model, GRB
import pandas as pd

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

# Initialize the model
m = Model('TechEssentialsPricing')

# Add price decision variables for each product
prices = m.addVars(len(data), name="p", lb=0)

# Define a simplified demand function considering a dummy cross-elasticity effect
def demand(i, prices):
    base_demand = data.at[i, 'Intercept']
    price_sensitivity = data.at[i, 'Sensitivity']
    demand = base_demand + price_sensitivity * prices[i]
    # Simplified cross-elasticity effect using a dummy value
    dummy_cross_elasticity = 0.1  # This is a placeholder value
    for j in range(len(data)):
        if j != i:  # Assuming all products have some level of interaction
            demand += dummy_cross_elasticity * (prices[j] - prices[i])  # Dummy interaction
    return demand

# Set the objective: Maximize total revenue
m.setObjective(sum(prices[i] * demand(i, prices) for i in range(len(data))), GRB.MAXIMIZE)

# Add production capacity constraints
for i in range(len(data)):
    m.addConstr(demand(i, prices) <= data.at[i, 'Capacity'], name=f"capacity_{i}")

# Optimize the model
m.optimize()

# Print the optimal prices
if m.status == GRB.OPTIMAL:
    optimal_prices = m.getAttr('X', prices)
    for i in range(len(data)):
        print(f"Optimal price for {data.at[i, 'Product']}: {optimal_prices[i]:.2f}")
else:
    print("Optimization was not successful.")
