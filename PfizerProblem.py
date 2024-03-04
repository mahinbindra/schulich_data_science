from gurobipy import Model, GRB

# Create a new model
m = Model("vaccine_distribution")

# Data
airports = ['Billy_Bishop', 'Toronto_Pearson']

# Costs for transportation from each airport to each vaccination site
costs = {
    ('Billy_Bishop', 1): 0.05, ('Billy_Bishop', 2): 0.06, ('Billy_Bishop', 3): 0.07,
    ('Billy_Bishop', 4): 0.08, ('Billy_Bishop', 5): 0.09, ('Billy_Bishop', 6): 0.10,
    ('Toronto_Pearson', 1): 0.08, ('Toronto_Pearson', 2): 0.05, ('Toronto_Pearson', 3): 0.09,
    ('Toronto_Pearson', 4): 0.10, ('Toronto_Pearson', 5): 0.07, ('Toronto_Pearson', 6): 0.06
}
# Extend the cost dictionary to cover all sites from 1 to 29
costs.update({(k[0], i+5*k[1]): v for k, v in costs.items() for i in range(5)})

# Total supply at each airport
supply = {'Billy_Bishop': 100000, 'Toronto_Pearson': 250000}

# Demand at each vaccination site (total number needed for a week)
demand = {i: 50000*7 for i in range(1, 30)}

# Decision variables for the number of vaccines sent from airport i to site j
x = m.addVars(airports, demand.keys(), name="x", vtype=GRB.INTEGER)

# Set the objective function
m.setObjective(sum(costs[i, j] * x[i, j] for i in airports for j in demand.keys()), GRB.MINIMIZE)

# Supply constraints for each airport
for i in airports:
    m.addConstr(sum(x[i, j] for j in demand.keys()) <= supply[i], name=f"supply_constraint_{i}")

# Demand constraints for each vaccination site
for j in demand.keys():
    m.addConstr(sum(x[i, j] for i in airports) == demand[j], name=f"demand_constraint_{j}")

# Additional constraints
# Constraint 1: Difference in the number of doses sent to sites 1-5 from each airport must be within 4800 units
m.addConstrs((x['Billy_Bishop', j] - x['Toronto_Pearson', j] <= 4800 for j in range(1, 6)), name="constraint1_upper")
m.addConstrs((x['Toronto_Pearson', j] - x['Billy_Bishop', j] <= 4800 for j in range(1, 6)), name="constraint1_lower")

# Constraint 2: Doses sent from Pearson to sites 21-25 must be less than or equal to eight times the doses sent from Billy Bishop to sites 11-15
m.addConstr(sum(x['Toronto_Pearson', j] for j in range(21, 26)) <= 
            8 * sum(x['Billy_Bishop', j] for j in range(11, 16)), name="constraint2")

# Constraint 3: Doses sent from Billy Bishop to sites 26-29 must be greater than or equal to 80% of the doses sent from Pearson to sites 16-20
m.addConstr(sum(x['Billy_Bishop', j] for j in range(26, 30)) >= 
            0.8 * sum(x['Toronto_Pearson', j] for j in range(16, 21)), name="constraint3")

# Solve model
m.optimize()

# Print solution
if m.status == GRB.OPTIMAL:
    solution = m.getAttr('x', x)
    for i in airports:
        for j in demand.keys():
            if solution[i, j] > 0:
                print(f"Vaccines from {i} to site {j}: {solution[i, j]}")
