from gurobipy import Model, GRB, quicksum
import pandas as pd

# Load the dataset
costs_df = pd.read_csv('/Users/mahinbindra/Downloads/nurse_shift_costs.csv')

# Constants from the problem statement
num_nurses = 26
num_shifts = 14
min_hours = 36
max_hours = 60
min_nurses_per_shift = 6
shift_length = 12

# Create a new model
m = Model('nurse_scheduling')

# Decision variables
x = m.addVars(num_nurses, num_shifts, vtype=GRB.BINARY, name='x')
y = m.addVars(num_nurses, num_shifts, vtype=GRB.BINARY, name='y')
z = m.addVars(num_nurses, num_shifts, vtype=GRB.BINARY, name='z')

# Objective: Minimize total cost
obj = quicksum(costs_df.at[i, 'Cost_Weekday'] * (x[i, j] + y[i, j] + z[i, j]) for i in range(num_nurses) for j in range(5)) + \
      quicksum(costs_df.at[i, 'Cost_Weekend'] * (x[i, j] + y[i, j] + z[i, j]) for i in range(num_nurses) for j in range(5, num_shifts)) + \
      quicksum(costs_df.at[i, 'Cost_Overtime'] * (quicksum((x[i, j] + y[i, j] + z[i, j]) * shift_length for j in range(num_shifts)) - min_hours) for i in range(num_nurses))
m.setObjective(obj, GRB.MINIMIZE)

# Constraints
# Each shift must have at least 6 nurses
for j in range(num_shifts):
    m.addConstr(quicksum(x[i, j] + y[i, j] + z[i, j] for i in range(num_nurses)) >= min_nurses_per_shift)

# Each nurse works between 36 and 60 hours
for i in range(num_nurses):
    m.addConstr(quicksum((x[i, j] + y[i, j] + z[i, j]) * shift_length for j in range(num_shifts)) >= min_hours)
    m.addConstr(quicksum((x[i, j] + y[i, j] + z[i, j]) * shift_length for j in range(num_shifts)) <= max_hours)

# Each shift must have at least one SRN
for j in range(num_shifts):
    m.addConstr(quicksum(x[i, j] for i in range(num_nurses)) >= 1)

# Nurses cannot work consecutive shifts
for i in range(num_nurses):
    for j in range(num_shifts - 1):
        m.addConstr(x[i, j] + x[i, j+1] <= 1)
        m.addConstr(y[i, j] + y[i, j+1] <= 1)
        m.addConstr(z[i, j] + z[i, j+1] <= 1)
    # Ensure wrap-around constraint for the last shift of the week
    m.addConstr(x[i, 0] + x[i, num_shifts-1] <= 1)
    m.addConstr(y[i, 0] + y[i, num_shifts-1] <= 1)
    m.addConstr(z[i, 0] + z[i, num_shifts-1] <= 1)

# Solve the model
m.optimize()

# Output the solution
for v in m.getVars():
    if v.x > 0:
        print(f"{v.varName}, {v.x}")

# Number of decision variables = num_nurses * num_shifts * 3 (for SRN, RN, NIT)
total_decision_variables = num_nurses * num_shifts * 3
total_decision_variables

# This would retrieve the optimal value after optimization, which cannot be done here
optimal_value = m.objVal
optimal_value