from gurobipy import Model, GRB

# Create a new model
m = Model("road_salt_storage")

# Parameters
n_locations = 15
n_wards = 44
max_capacity = 4500
min_salt_per_ward = 500
fixed_cost = 500000

# Function to calculate transportation cost
def calc_cni(n, i):
    return (n**2 * (11 - (i / 4))) / 10

# Decision variables
x = m.addVars(n_locations, vtype=GRB.BINARY, name="x")
y = m.addVars(n_locations, n_wards, vtype=GRB.CONTINUOUS, name="y", lb=0)

# Objective function
m.setObjective(sum(fixed_cost * x[n] for n in range(n_locations)) +
               sum(calc_cni(n+1, i+1) * y[n,i] for n in range(n_locations) for i in range(n_wards)),
               GRB.MINIMIZE)

# Constraints

# Constraint a: Capacity limit at each site
m.addConstrs((sum(y[n, i] for i in range(n_wards)) <= max_capacity * x[n] for n in range(n_locations)), "capacity")

# Constraint b: Demand at each ward
m.addConstrs((sum(y[n, i] for n in range(n_locations)) >= min_salt_per_ward for i in range(n_wards)), "demand")

# Constraint c: At least 8 storage sites must be opened
m.addConstr(sum(x[n] for n in range(n_locations)) >= 8, "min_sites")

# Constraint d: Limitation on specific sites
specific_sites = [1, 3, 5, 7, 9, 11]
m.addConstr(sum(x[n] for n in specific_sites) <= 3, "specific_limit")

# Constraint e: Linked opening of sites 7 and 13
m.addConstr(x[6] <= x[12], "link_7_13")

# Constraint f: Exact two sites among 1, 5, 14
m.addConstr(x[0] + x[4] + x[13] == 2, "exact_two")

# Constraint g: Exclusive sites 2 and 12
m.addConstr(x[1] + x[11] <= 1, "exclusive_2_12")

# Constraint h: Conditional openings
m.addConstr(x[2] <= x[1], "cond_3_2")
m.addConstr(x[2] <= x[8], "cond_3_9")
m.addConstr(x[2] <= x[10], "cond_3_11")

# Optimize model
m.optimize()

# Print solution
if m.status == GRB.OPTIMAL:
    print('Optimal solution found:\n')
    for v in m.getVars():
        if v.x > 0:
            print(f"{v.varName} = {v.x}")

else:
    print('No optimal solution found.')
