import gurobipy as gb
from gurobipy import GRB
import pandas as pd

# # Read the details associated with each center
df_center = pd.read_csv("homecare_centers.csv", index_col=0)

# # Read the details associated with each demand
df_demand = pd.read_csv("homecare_demands.csv")

# Read the distance between each center and region
df_dist = pd.read_csv("homecare_distances.csv")

# Parameters derived from the CSV file and sets for the constraints
centers = list(df_center.index)
regions = list(df_demand["Region"].unique())
periods = list(df_demand["Year"].unique())
workers = {i: int(df_center.loc[i]["Workers"]) for i in centers}
center_capacities = {i : int(df_center.loc[i]["Maximum Capacity"]) for i in centers}
opening_cost = {i : float(df_center.loc[i]["Opening Costs"]) for i in centers}
operating_cost = {i : float(df_center.loc[i]["Operating Costs"]) for i in centers}
demands = {(i,t) : df_demand[(df_demand["Year"] == t) & (df_demand["Region"] == i)]["Demand"].iloc[0] for t in periods for i in regions}             

# Assume that it costs $5000 to hire one worker (advertising, interviews, training) 
hiring_cost = 5000

# Because this is shift work, the maximum number of appointments each worker can work per 
# year is 250 (260 working days - 2 weeks of vacation). Assume no overtime.
max_appointments_per_year = 2000

# Assume that the revenue starts at $42.00 per appointment and this increases 2.5% per year (inflation)
revenue = {t: 42.00*1.025**(t-2024) for t in periods}

# Assume that the wage cost starts at $37.00 per appointment and this increases 3.4% per year (> inflation)
service_cost = {t: 37.00*1.034**(t-2024) for t in periods}

# Travel cost is reimbursed at $0.50 per kilometer; approximate distance cost by analyzing the number of visits to each region
travel_cost = {(i,j) : 0.50*df_dist[(df_dist["Center"] == i) & (df_dist["Region"] == j)]["Distance"].iloc[0] for i in centers for j in regions}

# The profit per appointment to the company is the revenue - wage cost - travel cost
profit_per_appointment = {(i,j,t) : revenue[t] - service_cost[t] - travel_cost[i,j] for i in centers for j in regions for t in periods}
            
# Create the Gurobi model
model = gb.Model("Facility Location Model")

# Add Decision Variables

# Decision variables: if a center is opened/allocated
y = model.addVars(centers, vtype=GRB.BINARY, name="y")

# Decision variables: amount of demand from each region allocated to center, per period
x = model.addVars(centers, regions, periods, lb=0.0, vtype=GRB.INTEGER, name="x")

# Decision variables: number of home care workers per center, per period
hcw = model.addVars(centers, periods, lb=0, vtype=GRB.INTEGER, name="w")

# Decision variables: number of home care workers to hire per center, per period
hire = model.addVars(centers, periods, lb=0, vtype=GRB.INTEGER, name="h")

# Add Constraints

# Constraint: All demand must be fully satisfied in every period
model.addConstrs(gb.quicksum(x[i, j, t] for i in centers) == demands[j, t] for j in regions for t in periods)

# Constraint: Centers A-D are opened while it remains to be seen whether centers E and F should be opened
model.addConstrs(y[c] == 1 for c in ["Center A", "Center B", "Center C", "Center D"])

# Constraint: Center capacities must be observed in all scenarios
model.addConstrs(gb.quicksum(x[i, j, t] for j in regions) <= center_capacities[i] * y[i] for i in centers for t in periods)

# Constraint: Flow of workers per period
model.addConstrs(hcw[i, t] == (workers[i] if t == 2024 else hcw[i, t - 1]) + hire[i, t] for i in centers for t in periods)

# Constraint: Maximum number of hires per year
model.addConstrs(hire[c, t] <= 300 for c in centers for t in periods)

# Constraint: The number of appointments per year are limited by the number of workers at a center
model.addConstrs(gb.quicksum(x[i, j, t] for j in regions) <= hcw[i, t] * max_appointments_per_year for i in centers for t in periods)

# Objective function
obj = gb.quicksum(profit_per_appointment[i, j, t] * x[i, j, t] for i in centers for j in regions for t in periods)
obj -= gb.quicksum(opening_cost[i] * y[i] for i in ["Center E", "Center F"])
obj -= gb.quicksum(operating_cost[i] * y[i] * len(periods) for i in centers)
obj -= gb.quicksum(hiring_cost * hire[i, t] for i in centers for t in periods)

# Set the objective sense to maximize
model.setObjective(obj, GRB.MAXIMIZE)

# Optimize the model
model.optimize()

# Print solution 
for i in centers:
    if y[i].X > 0.5:
        print(i + " is open:")
        print("\tNumber of hires: ")
        for t in periods:
            if hire[(i,t)].X > 0.0:
                print("\t\tt=" + str(t) + ": " + str(hire[(i,t)].X))
        print("\tNumber of workers: ")
        for t in periods:
            print("\t\tt=" + str(t) + ": " + str(hcw[(i,t)].X))

# Number of decision variables in the model
print("Number of Decision Variables: ", model.numVars)

# Number of constraints in the model
print("Number of Constraints: ", model.numConstrs)