import pandas as pd
from gurobipy import Model, GRB

# Load data
supply_data = pd.read_csv('/Users/mahinbindra/Downloads/ecogreen_energy_supply.csv')
demand_data = pd.read_csv('/Users/mahinbindra/Downloads/ecogreen_energy_demand.csv')

# Initialize the model
model = Model("EcoGreen Energy Expansion")

# Number of sites and provinces
num_sites = supply_data.shape[0]
num_provinces = demand_data.shape[0]

# Decision Variables
x = model.addVars(num_sites, vtype=GRB.BINARY, name="Open")
y = model.addVars(num_sites, num_provinces, vtype=GRB.CONTINUOUS, name="Energy_Transferred")

# Objective Function: Minimize total costs
model.setObjective(
    sum(supply_data.loc[i, 'Fixed'] * x[i] for i in range(num_sites)) +
    sum(supply_data.loc[i, f'Province {j+1}'] * y[i, j] for i in range(num_sites) for j in range(num_provinces)),
    GRB.MINIMIZE
)

# Constraints
# Capacity constraints
model.addConstrs((sum(y[i, j] for j in range(num_provinces)) <= supply_data.loc[i, 'Capacity'] * x[i]
                  for i in range(num_sites)), "Capacity")

# Demand constraints
model.addConstrs((sum(y[i, j] for i in range(num_sites)) >= demand_data.loc[j, 'Demand']
                  for j in range(num_provinces)), "Demand")

# Mutual Exclusivity and Dependency
model.addConstr(x[9] <= 1 - x[14], "Mutual_Exclusivity_10_15")
model.addConstr(x[19] <= 1 - x[14], "Mutual_Exclusivity_20_15")
model.addConstr(x[14] <= 1 - x[19], "Mutual_Exclusivity_15_20")
model.addConstr(2 * x[2] <= x[3] + x[4], "Dependency_3_4_5")
model.addConstr(x[4] <= x[7] + x[8], "Dependency_5_on_8_9")

# Regional Plant Limits
model.addConstr(sum(x[i] for i in range(10)) <= 2 * sum(x[i] for i in range(10, 20)), "Regional_Limits")

# Energy Output Mix
total_energy = sum(y[i, j] for i in range(5) for j in range(num_provinces))
total_all_energy = sum(y[i, j] for i in range(num_sites) for j in range(num_provinces))
model.addConstr(total_energy >= 0.3 * total_all_energy, "Minimum_Output")

# Provincial Energy Caps
model.addConstrs((y[i, j] <= 0.5 * demand_data.loc[j, 'Demand'] for i in range(num_sites) for j in range(num_provinces)),
                 "Max_Energy_Per_Province")

# Optimize the model
model.optimize()

# Display results
if model.status == GRB.OPTIMAL:
    print("Optimal solution found:")
    for v in model.getVars():
        print(f"{v.varName} = {v.x}")
else:
    print("No optimal solution found.")


print("######################## PART A ######################")

# Calculate the number of distinct provinces each plant can supply
distinct_provinces_per_plant = {i: sum(1 for j in range(num_provinces) if y[i, j].X > 0) for i in range(num_sites)}

# Print the results for each plant
for i in range(num_sites):
    print(f"Plant {i+1} can supply {distinct_provinces_per_plant[i]} distinct provinces.")


print("######################## PART B ######################")

num_variables = num_sites + (num_sites * num_provinces)
print(f"Total number of decision variables: {num_variables}")


print("######################## PART F ######################")

optimal_cost = model.ObjVal
print(f"Optimal Cost: {optimal_cost}")


print("######################## PART G ######################")

num_plants_opened = sum(1 for i in range(num_sites) if x[i].X > 0.5)
print(f"Number of power plants established: {num_plants_opened}")


print("######################## PART H ######################")

plants_per_province = [sum(1 for i in range(num_sites) if y[i, j].X > 0) for j in range(num_provinces)]
highest = max(plants_per_province)
lowest = min(plants_per_province)
print(f"Highest number of plants per province: {highest}")
print(f"Lowest number of plants per province: {lowest}")


print("######################## PART J ######################")

model.setParam('PoolSearchMode', 2)  # Find n best solutions
model.setParam('PoolGap', 0.01)      # Within 1% of the optimal
model.optimize()

number_of_solutions = model.SolCount
print(f"Number of feasible solutions within 1% of the optimal: {number_of_solutions}")


print("######################## PART K ######################")

# Remove the constraint related to the 50% energy supply cap
for i in range(num_sites):
    for j in range(num_provinces):
        constraint_name = f"Max_Energy_Per_Province_{i}_{j}"
        if model.getConstrByName(constraint_name):  # Check if the constraint exists
            model.remove(model.getConstrByName(constraint_name))

# Update the model to apply the changes
model.update()

# Optimize the model after removing the constraint
model.optimize()

# Display results and count the number of power plants established
if model.status == GRB.OPTIMAL:
    print("Optimal solution found after removing 50% cap constraint:")
    num_plants_opened = sum(1 for i in range(num_sites) if x[i].X > 0.5)
    print(f"Number of power plants established: {num_plants_opened}")
else:
    print("No optimal solution found.")