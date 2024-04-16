import gurobipy as gp
from gurobipy import GRB

# Data from the snippet
probabilities = [0.09, 0.12, 0.10, 0.05, 0.16, 0.14, 0.03, 0.08, 0.05, 0.05, 0.04, 0.03, 0.02, 0.01, 0.02, 0.01]
demands = [90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165]
supplier_costs = [120, 105, 110]  # Costs for Phil & Sebastian, Rosso, and Monogram respectively
advance_order_cost = 95
min_order_quantities = [0, 70, 40]  # Minimum order quantities for Phil & Sebastian, Rosso, and Monogram

# Model setup
m = gp.Model("Coffee_Supply")

# Decision variables
x = m.addVar(name="x", vtype=GRB.CONTINUOUS)  # Advanced order
y = m.addVars(3, 16, vtype=GRB.CONTINUOUS, name="y")  # Emergency orders

# Objective: Minimize the expected cost
m.setObjective(advance_order_cost * x + gp.quicksum(probabilities[n] * gp.quicksum(supplier_costs[i] * y[i, n] for i in range(3)) for n in range(16)), GRB.MINIMIZE)

# Constraints
# Demand satisfaction in each scenario
for n in range(16):
    m.addConstr(x + gp.quicksum(y[i, n] for i in range(3)) >= demands[n], name=f"demand_satisfaction_{n}")

# Minimum order constraints for Rosso (index 1) and Monogram (index 2)
for i in [1, 2]:  # We do not need a minimum constraint for Phil & Sebastian (index 0)
    for n in range(16):
        is_ordered = m.addVar(vtype=GRB.BINARY, name=f"is_ordered_{i}_{n}")
        m.addConstr(y[i, n] >= min_order_quantities[i] * is_ordered, name=f"min_order_{i}_{n}")
        m.addConstr(y[i, n] <= demands[n] * is_ordered, name=f"max_order_{i}_{n}")


# Solve the model
m.optimize()

# Output solution
if m.status == GRB.OPTIMAL:
    print(f"Optimal amount of coffee to order in advance: {x.X} gallons at a cost of ${advance_order_cost * x.X}.")
    for n in range(16):
        for i in range(3):
            if y[i, n].X > 0:
                print(f"Order {y[i, n].X} gallons from supplier {i+1} in scenario {n+1} at a cost of ${supplier_costs[i] * y[i, n].X}.")
else:
    print("No optimal solution found.")

print("######################## PART F ######################")
# Assuming `m` is the Gurobi model after optimization has been performed
print(f"Optimal amount of coffee to order in advance: {x.X} gallons.")
print(f"Optimal objective function value (total expected cost): ${m.ObjVal:.2f}.")

print("######################## PART G ######################")
# Constants
emergency_costs = [120, 105, 110]  # Phil & Sebastian, Rosso, Monogram

# Cheapest reliable emergency option without minimum exceeding common additional demands
cheapest_reliable_emergency_cost = min(emergency_costs)  # Assuming no constraints for simplicity

# Print the break-even pre-order price
print(f"The break-even pre-order price: ${cheapest_reliable_emergency_cost:.2f} per gallon")

print("######################## PART H ######################")
# Determine the price per gallon to order the maximum amount in advance
# This is based on the scenario with the highest demand and its emergency order cost

# Find the highest demand scenario
max_demand_scenario = max(demands)
max_demand_cost = max_demand_scenario * supplier_costs[2]  # Assuming supplier 3 has the cheapest emergency cost

# Now we find the price per gallon where this is equivalent to the cost of ordering for the max demand scenario
price_per_gallon_max_advance = max_demand_cost / max_demand_scenario
print(f"Price per gallon to order the maximum amount in advance: ${round(price_per_gallon_max_advance, 2)}")


print("######################## PART I ######################")
import gurobipy as gp
from gurobipy import GRB

# Data from the snippet
probabilities = [0.09, 0.12, 0.10, 0.05, 0.16, 0.14, 0.03, 0.08, 0.05, 0.05, 0.04, 0.03, 0.02, 0.01, 0.02, 0.01]
demands = [90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165]
supplier_costs = [120, 105, 110]  # Costs for Phil & Sebastian, Rosso, and Monogram respectively
min_order_quantities = [0, 70, 40]  # Minimum order quantities for Rosso and Monogram

# Perfect foresight models for each scenario
perfect_foresight_costs = []
for n, demand in enumerate(demands):
    m_pf = gp.Model("Coffee_Supply_Perfect_Foresight_" + str(n))
    
    # Decision variables
    y = m_pf.addVars(3, vtype=GRB.INTEGER, name=f"y_{n}")  # Emergency orders from each supplier
    use = m_pf.addVars(2, vtype=GRB.BINARY, name=f"use_{n}")  # Binary variables for Rosso and Monogram

    # Objective function to minimize cost for this scenario
    total_cost_expr = gp.quicksum(supplier_costs[i] * y[i] for i in range(3))
    m_pf.setObjective(total_cost_expr, GRB.MINIMIZE)

    # Constraints
    m_pf.addConstr(gp.quicksum(y[i] for i in range(3)) >= demand, name=f"Demand_{n}")

    # Rosso Coffee minimum order constraints
    m_pf.addConstr(y[1] >= 70 * use[0], name=f"MinOrder_Rosso_{n}")
    m_pf.addGenConstrIndicator(use[0], True, y[1] >= 70, name=f"Activate_Rosso_{n}")
    m_pf.addGenConstrIndicator(use[0], False, y[1] == 0, name=f"Deactivate_Rosso_{n}")

    # Monogram Coffee minimum order constraints
    m_pf.addConstr(y[2] >= 40 * use[1], name=f"MinOrder_Monogram_{n}")
    m_pf.addGenConstrIndicator(use[1], True, y[2] >= 40, name=f"Activate_Monogram_{n}")
    m_pf.addGenConstrIndicator(use[1], False, y[2] == 0, name=f"Deactivate_Monogram_{n}")

    # Solve the model
    m_pf.optimize()

    # Store costs for each scenario, weighted by scenario probability
    if m_pf.status == GRB.OPTIMAL:
        perfect_foresight_costs.append(m_pf.objVal * probabilities[n])

# Calculate WS (Wait-and-See)
WS = sum(perfect_foresight_costs)

# Stochastic Programming Solution (SP) from your original calculation
SP = 11343.5  # Replace with m.objVal if available

# Calculate EVPI
EVPI = SP - WS

print("SP (Stochastic Programming Solution):", SP)
print("WS (Wait-and-See Solution):", WS)
print("EVPI (Expected Value of Perfect Information):", EVPI)

print("######################## PART J ######################")
import gurobipy as gp
from gurobipy import GRB

# Given data setup
probabilities = [0.09, 0.12, 0.10, 0.05, 0.16, 0.14, 0.03, 0.08, 0.05, 0.05, 0.04, 0.03, 0.02, 0.01, 0.02, 0.01]
demands = [90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165]
supplier_costs = [120, 105, 110]  # Costs for Phil & Sebastian, Rosso, and Monogram respectively
advance_order_cost = 95

# Calculate mean demand
mean_demand = sum(p * d for p, d in zip(probabilities, demands))

# Model setup for the deterministic mean value problem
m_mean = gp.Model("Deterministic_Mean_Value_Problem")

# Decision variables
x_mean = m_mean.addVar(name="x_mean", vtype=GRB.CONTINUOUS)  # Base order

# Objective function to minimize cost
m_mean.setObjective(advance_order_cost * x_mean, GRB.MINIMIZE)

# Constraint to ensure demand is met using average demand
m_mean.addConstr(x_mean >= mean_demand, "AverageDemand")

# Solve the model
m_mean.optimize()

print("Objective for the Average:", m_mean.objVal)

# Step 2: stochastic solution holding first-stage variables fixed
# Create a new optimization model
m_stochastic = gp.Model("Stochastic_Model")

# Use first-stage decisions from the mean value problem
fs_x = x_mean.X

# Scenario-specific decision variables
y = m_stochastic.addVars(3, 16, vtype=GRB.CONTINUOUS, name="y")  # Emergency orders

# Objective function to minimize total expected cost
objective = gp.quicksum(probabilities[n] * (advance_order_cost * fs_x + sum(supplier_costs[i] * y[i, n] for i in range(3))) for n in range(16))
m_stochastic.setObjective(objective, GRB.MINIMIZE)

# Constraints for each scenario
for n in range(16):
    m_stochastic.addConstr(fs_x + gp.quicksum(y[i, n] for i in range(3)) >= demands[n], name=f"Demand_{n}")

# Solve our model
m_stochastic.optimize()

print("Objective for the Stochastic Solution:", m_stochastic.objVal)

# EEV from the mean value problem
EEV = m_mean.objVal

# SP from the stochastic model
SP = m_stochastic.objVal

# Calculate VSS
VSS = abs(EEV - SP)

print("EEV (Expected Ex-Post Value):", EEV)
print("SP (Expected Value of Stochastic Solution):", SP)
print("VSS (Value of Stochastic Solution):", VSS)
