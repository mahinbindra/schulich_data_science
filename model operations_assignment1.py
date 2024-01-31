#Assignment Question 1: Can2Oil LP Problem
#Solved by Group members: Rupali Wadhawan, Aimal Dastagirzada, Mahin Bindra

import pandas as pd

# Loading the files
df_direct_prod_capacity = pd.read_csv('/Users/mahinbindra/Downloads/Capacity_for_Direct_Production_Facilities.csv')
df_transship_dist_capacity = pd.read_csv('/Users/mahinbindra/Downloads/Capacity_for_Transship_Distribution_Centers.csv')
df_transship_prod_capacity = pd.read_csv('/Users/mahinbindra/Downloads/Capacity_for_Transship_Production_Facilities.csv')
df_cost_prod_to_refinement = pd.read_csv('/Users/mahinbindra/Downloads/Cost_Production_to_Refinement.csv')
df_cost_prod_to_transship = pd.read_csv('/Users/mahinbindra/Downloads/Cost_Production_to_Transshipment.csv')
df_cost_transship_to_refinement = pd.read_csv('/Users/mahinbindra/Downloads/Cost_Transshipment_to_Refinement.csv')
df_refinement_demand = pd.read_csv('/Users/mahinbindra/Downloads/Refinement_Demand.csv')


# Displaying the first few rows of each dataframe for inspection
dfs = {
    "Direct Production Capacity": df_direct_prod_capacity,
    "Transship Distribution Capacity": df_transship_dist_capacity,
    "Transship Production Capacity": df_transship_prod_capacity,
    "Cost Production to Refinement": df_cost_prod_to_refinement,
    "Cost Production to Transshipment": df_cost_prod_to_transship,
    "Cost Transshipment to Refinement": df_cost_transship_to_refinement,
    "Demand at each refinement center": df_refinement_demand
}

# Convert numpy.int64 to standard Python int
num_prod_facilities = int(max(df_direct_prod_capacity['ProductionFacility'].max(), df_transship_prod_capacity['ProductionFacility'].max()))
num_refinement_centers = int(df_refinement_demand['RefinementCenter'].nunique())
num_transship_hubs = int(df_transship_dist_capacity['TransshipmentHub'].nunique())

# Capacity and demand data
capacity_direct_prod = df_direct_prod_capacity.set_index('ProductionFacility')['Capacity']
capacity_transship_prod = df_transship_prod_capacity.set_index('ProductionFacility')['Capacity']
capacity_transship_dist = df_transship_dist_capacity.set_index('TransshipmentHub')['Capacity']
demand_refinement = df_refinement_demand.set_index('RefinementCenter')['Demand']

# Cost data
cost_prod_to_ref = df_cost_prod_to_refinement.pivot(index='ProductionFacility', columns='RefinementCenter', values='Cost').fillna(0)
cost_prod_to_trans = df_cost_prod_to_transship.pivot(index='ProductionFacility', columns='TransshipmentHub', values='Cost').fillna(0)
cost_trans_to_ref = df_cost_transship_to_refinement.pivot(index='TransshipmentHub', columns='RefinementCenter', values='Cost').fillna(0)

import gurobipy as gp
from gurobipy import GRB

# Create a new model
m = gp.Model("can2oil_optimization")

# Decision Variables
# x[i, j] for direct production to refinement center
# y[i, k] for production to transshipment hub
# z[k, j] for transshipment hub to refinement center
x = m.addVars(num_prod_facilities, num_refinement_centers, name="x", lb=0)
y = m.addVars(15, num_transship_hubs, name="y", lb=0)  # 15 transship-needed facilities
z = m.addVars(num_transship_hubs, num_refinement_centers, name="z", lb=0)

# Objective: Minimize total transportation cost
m.setObjective(
    gp.quicksum(x[i, j] * cost_prod_to_ref.iloc[i, j] for i in range(num_prod_facilities) for j in range(num_refinement_centers)) +
    gp.quicksum(y[i, k] * cost_prod_to_trans.iloc[i, k] for i in range(15) for k in range(num_transship_hubs)) +
    gp.quicksum(z[k, j] * cost_trans_to_ref.iloc[k, j] for k in range(num_transship_hubs) for j in range(num_refinement_centers)),
    GRB.MINIMIZE
)

# Constraints

# Production capacity constraints
for i in range(num_prod_facilities):
    m.addConstr(gp.quicksum(x[i, j] for j in range(num_refinement_centers)) <= capacity_direct_prod.iloc[i])

# Transshipment production capacity constraints
for i in range(15):
    m.addConstr(gp.quicksum(y[i, k] for k in range(num_transship_hubs)) <= capacity_transship_prod.iloc[i])

# Transshipment hub capacity constraints
for k in range(num_transship_hubs):
    m.addConstr(gp.quicksum(y[i, k] for i in range(15)) <= capacity_transship_dist.iloc[k])

# Demand constraints at each refinement center
for j in range(num_refinement_centers):
    m.addConstr(gp.quicksum(x[i, j] for i in range(num_prod_facilities)) + gp.quicksum(z[k, j] for k in range(num_transship_hubs)) == demand_refinement.iloc[j])

# Solve the model
m.optimize()

# Print solution
if m.status == GRB.Status.OPTIMAL:
    print('Optimal solution found with total cost:', m.objVal)
    for v in m.getVars():
        if v.x > 0:
            print(f'{v.varName} = {v.x}')
else:
    print('No optimal solution found')
    
### (C) Modifying the Objective Function to Limit Transshipment

# Define a penalty for transshipment
transshipment_penalty = 1.0  # This is an example value; you can adjust it based on your requirements

# Modify the objective function
m.setObjective(
    gp.quicksum(x[i, j] * cost_prod_to_ref.iloc[i, j] for i in range(num_prod_facilities) for j in range(num_refinement_centers)) +
    gp.quicksum(y[i, k] * cost_prod_to_trans.iloc[i, k] for i in range(15) for k in range(num_transship_hubs)) +
    gp.quicksum(z[k, j] * (cost_trans_to_ref.iloc[k, j] + transshipment_penalty) for k in range(num_transship_hubs) for j in range(num_refinement_centers)),
    GRB.MINIMIZE
)

# Solve the model with the modified objective
m.optimize()

if m.status == GRB.Status.OPTIMAL:
    print('Optimal solution found with total cost:', m.objVal)
    for v in m.getVars():
        if v.x > 0:
            print(f'{v.varName} = {v.x}')
else:
    print('No optimal solution found')
    
### (D) Modifying the Constraint Set to Reduce Transshipment

# Define a limit for total transshipment
transshipment_limit = 5000  # This is an example value; adjust it as needed

# Add the constraint to limit total transshipment
m.addConstr(gp.quicksum(y[i, k] for i in range(15) for k in range(num_transship_hubs)) <= transshipment_limit)

# Solve the model with the new constraint
m.optimize()

if m.status == GRB.Status.OPTIMAL:
    print('Optimal solution found with total cost:', m.objVal)
    for v in m.getVars():
        if v.x > 0:
            print(f'{v.varName} = {v.x}')
else:
    print('No optimal solution found')

### (F) Altering the model for re-shoring

# Define a factor to reduce transportation costs for North American facilities
cost_reduction_factor = 0.8  # Example value, adjust as needed

# Apply the cost reduction to North American facilities
for i in range(15):  # Assuming the first 15 facilities are in North America
    for j in range(num_refinement_centers):
        cost_prod_to_ref.iloc[i, j] *= cost_reduction_factor

# Update the objective function with the adjusted costs
m.setObjective(
    gp.quicksum(x[i, j] * cost_prod_to_ref.iloc[i, j] for i in range(num_prod_facilities) for j in range(num_refinement_centers)) +
    gp.quicksum(y[i, k] * cost_prod_to_trans.iloc[i, k] for i in range(15) for k in range(num_transship_hubs)) +
    gp.quicksum(z[k, j] * cost_trans_to_ref.iloc[k, j] for k in range(num_transship_hubs) for j in range(num_refinement_centers)),
    GRB.MINIMIZE
)

# Solve the model with the adjusted costs
m.optimize()

if m.status == GRB.Status.OPTIMAL:
    print('Optimal solution found with total cost:', m.objVal)
    for v in m.getVars():
        if v.x > 0:
            print(f'{v.varName} = {v.x}')
else:
    print('No optimal solution found')


