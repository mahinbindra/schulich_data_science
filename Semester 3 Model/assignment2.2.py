import pandas as pd
from gurobipy import Model, GRB, quicksum
data = pd.read_csv("/Users/mahinbindra/Downloads/price_response.csv")

from gurobipy import Model, GRB
import gurobipy as gb

# Assume the dataset is loaded into a variable named 'data'
# Cross-elasticity factor
cross_elasticity = 0.1

# Create a new model
model = Model("TechEssentials Pricing Optimization with Capacity")

# Decision variables: Price for each of the 9 products
prices = model.addVars(len(data), lb=0, vtype=GRB.CONTINUOUS, name="Price")

# Demand variables for each product, adjusted for cross-elasticity and data-driven
demands = model.addVars(len(data), lb=0, vtype=GRB.CONTINUOUS, name="Demand")

# Update demand calculations to include data-driven parameters and cross-elasticity
for i in range(len(data)):
    intercept, sensitivity = data.loc[i, ['Intercept', 'Sensitivity']]
    # Base demand from price, adjusted for intercept and sensitivity from the dataset
    demand_expr = intercept + sensitivity * prices[i]
    
    # Add cross-elasticity effects from other products within the same line
    for j in range((i // 3) * 3, (i // 3) * 3 + 3):
        if i != j:
            demand_expr += cross_elasticity * (prices[j] - prices[i])
    
    model.addConstr(demands[i] == demand_expr, name=f"DemandCalc_{i}")
    

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

df = data[(data["Product"] == "Line 1 Product 1") | (data["Product"] == "Line 2 Product 1")]
df.reset_index(drop=True, inplace=True)

#(A)
m=Model("abc")


p1 = m.addVar(lb=0,vtype=GRB.CONTINUOUS,name="basic")
p2 = m.addVar(lb=0,vtype=GRB.CONTINUOUS,name="Adv")

d1 = m.addVar(lb=0, ub=80020,vtype=GRB.INTEGER,name="demand for basic")
d2 = m.addVar(lb=0, ub=86740,vtype=GRB.INTEGER,name="adv demand")

# Objective: Maximize total revenue
m.setObjective((p1*d1+p2*d2), GRB.MAXIMIZE)

a1,b1,a2,b2=35234.545786, -45.896450, 37041.380378, -9.033166

m.addConstr(d1 == a1 - b1*p1, "Demand Definition")
m.addConstr(d2 == a2 - b2*p2, "Demand Definition 2")
m.addConstr(p2>=p1,"price ordering")

# Optimize the model
m.optimize()


if m.status == GRB.OPTIMAL:
    print("Optimal Basic Price:", p1.x)
    print("Optimal Advanced Price:", p2.x)
else:
    print("Optimal solution was not found.")
    

# (B)
import numpy as np
from gurobipy import Model, GRB

# Initialization
p = np.array([0.0, 0.0])  # Initial prices for Basic (p1) and Advanced (p2)
alpha = 0.001  # Step size
tolerance = 1e-6  # Stopping criterion for convergence
max_iterations = 10000  # To prevent infinite loops

# Coefficients for the revenue function
a = np.array([35234.545786, 37041.380378])
b = np.array([45.896450, 9.033166])

# Gradient Descent Loop
for iteration in range(max_iterations):
    # Calculate gradients
    gradients = a - 2 * np.multiply(b, p)
    
    # Update prices using gradient
    p_updated = p + alpha * gradients
    
    # Projection step using Gurobi
    m = Model()
    m.setParam('OutputFlag', 0)  # Turn off Gurobi output
    p_proj = m.addVars(2, lb=0, name="p")
    
    # Objective for projection: minimize the distance to the updated prices
    m.setObjective(sum((p_proj[i] - p_updated[i]) * (p_proj[i] - p_updated[i]) for i in range(2)), GRB.MINIMIZE)
    
    # Add constraint for price ordering
    m.addConstr(p_proj[1] >= p_proj[0], "price_ordering")
    
    # Optimize the model for projection
    m.optimize()
    
    # Update prices based on the projection
    p_new = np.array([p_proj[i].X for i in range(2)])
    
    # Check for convergence
    if np.linalg.norm(p_new - p, ord=2) < tolerance:
        print(f"Converged in {iteration+1} iterations.")
        break
    
    p = p_new

# Print optimal prices
print(f"Optimal Basic Price: {p[0]}")
print(f"Optimal Advanced Price: {p[1]}")


#(C) But is this quadratic????
from gurobipy import Model, GRB, QuadExpr
import gurobipy as gb

# Assuming 'data' is pre-loaded with price response functions, capacities, etc.

# Initialize the model
model = Model("TechEssentials Quadratic Pricing Optimization")

# Decision variables: Prices for each of the 9 products, with lower bounds to ensure non-negative prices
prices = model.addVars(len(data), lb=0, vtype=GRB.CONTINUOUS, name="Price")

# Demand variables: Adjusted for cross-elasticity and data-driven parameters
demands = model.addVars(len(data), lb=0, vtype=GRB.CONTINUOUS, name="Demand")

# Update demand calculations including data parameters and cross-elasticity
for i in range(len(data)):
    intercept, sensitivity = data.loc[i, ['Intercept', 'Sensitivity']]
    demand_expr = intercept + sensitivity * prices[i]

    # Adjust demand for cross-elasticity within the same product line
    for j in range((i // 3) * 3, (i // 3) * 3 + 3):
        if i != j:
            demand_expr += cross_elasticity * (prices[j] - prices[i])

    model.addConstr(demands[i] == demand_expr, name=f"DemandCalc_{i}")

# Capacity constraints for each product
for i in range(len(data)):
    capacity = data.loc[i, 'Capacity']
    model.addConstr(demands[i] <= capacity, name=f"Capacity_{i}")

# Price order constraints within each product line to ensure Basic < Advanced < Premium
for line_start in range(0, len(data), 3):
    model.addConstr(prices[line_start] <= prices[line_start + 1], name=f"PriceOrder_{line_start}_to_{line_start + 1}")
    model.addConstr(prices[line_start + 1] <= prices[line_start + 2], name=f"PriceOrder_{line_start + 1}_to_{line_start + 2}")

# Objective: Maximize total revenue, which is a quadratic function due to the price order constraints
objective = QuadExpr()
for i in range(len(data)):
    objective += prices[i] * demands[i]
model.setObjective(objective, GRB.MAXIMIZE)

# Optimize the model
model.optimize()

# Display results
if model.status == GRB.OPTIMAL:
    print("Optimal Total Revenue: ${:.2f}".format(model.ObjVal))
    print("Optimal Prices and Expected Demands:")
    for i in range(len(data)):
        print(f"{data.loc[i, 'Product']}: Price = ${prices[i].X:.2f}, Demand = {demands[i].X:.0f}")
else:
    print("Optimal solution was not found.")

#(D)
from gurobipy import Model, GRB, QuadExpr
import gurobipy as gb

# Initialize the model
model = Model("TechEssentials Quadratic Pricing Optimization")

# Assuming 'data' contains all the necessary information
# Decision variables: Prices for each of the 9 products, with lower bounds to ensure non-negative prices
prices = model.addVars(len(data), lb=0, vtype=GRB.CONTINUOUS, name="Price")

# Demand variables: Adjusted for cross-elasticity and data-driven parameters
demands = model.addVars(len(data), lb=0, vtype=GRB.CONTINUOUS, name="Demand")

# Update demand calculations including data parameters and cross-elasticity
cross_elasticity = 0.1  # Assuming a given cross-elasticity value
for i in range(len(data)):
    intercept, sensitivity = data.loc[i, ['Intercept', 'Sensitivity']]
    demand_expr = intercept + sensitivity * prices[i]

    # Adjust demand for cross-elasticity within the same product line
    for j in range((i // 3) * 3, (i // 3) * 3 + 3):
        if i != j:
            demand_expr += cross_elasticity * (prices[j] - prices[i])

    model.addConstr(demands[i] == demand_expr, name=f"DemandCalc_{i}")

# Capacity constraints for each product
for i in range(len(data)):
    capacity = data.loc[i, 'Capacity']
    model.addConstr(demands[i] <= capacity, name=f"Capacity_{i}")

# Price order constraints within each product line to ensure Basic < Advanced < Premium
for line_start in range(0, len(data), 3):
    model.addConstr(prices[line_start] <= prices[line_start + 1], name=f"PriceOrder_{line_start}_to_{line_start + 1}")
    model.addConstr(prices[line_start + 1] <= prices[line_start + 2], name=f"PriceOrder_{line_start + 1}_to_{line_start + 2}")

# New constraints for price hierarchy across product lines for the same version
for version_index in range(3):  # For each version within the product lines
    model.addConstr(prices[version_index] <= prices[version_index + 3], name=f"VersionOrder_{version_index}_to_{version_index + 3}")
    model.addConstr(prices[version_index + 3] <= prices[version_index + 6], name=f"VersionOrder_{version_index + 3}_to_{version_index + 6}")

# Objective: Maximize total revenue
objective = QuadExpr()
for i in range(len(data)):
    objective += prices[i] * demands[i]
model.setObjective(objective, GRB.MAXIMIZE)

# Optimize the model
model.optimize()

# Display results
if model.status == GRB.OPTIMAL:
    print("Optimal Total Revenue: ${:.2f}".format(model.ObjVal))
    for i in range(len(data)):
        print(f"{data.loc[i, 'Product']}: Price = ${prices[i].X:.2f}, Demand = {demands[i].X:.0f}")
else:
    print("Optimal solution was not found.")

