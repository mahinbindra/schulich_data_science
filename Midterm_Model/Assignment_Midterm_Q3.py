import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Load the data
df = pd.read_csv('/Users/mahinbindra/Downloads/nurse_shift_costs.csv')

# Create lists for cost values
Category = df['Category'].tolist()
Cost_Weekday = df['Cost_Weekday'].tolist()
Cost_Weekend = df['Cost_Weekend'].tolist()
Cost_Overtime = df['Cost_Overtime'].tolist()

# Constants
N = 26  # Number of nurses
K = 3  # Number of nurse groups (SRN, RN, NIT)
HOURS_PER_SHIFT = 12
MAX_HOURS = 60
MIN_HOURS = 36
SHIFTS_PER_WEEK = 14

# Create a new model
model = gp.Model('Nursing')

# Decision variables
x = model.addVars(N, SHIFTS_PER_WEEK, vtype=GRB.BINARY, name="x")
a = model.addVars(N, vtype=GRB.INTEGER, name="o")
y = model.addVar(vtype=GRB.INTEGER, name="Overtime Shifts")

# Objective function
model.setObjective(
    gp.quicksum(Cost_Weekday[i] * x[i, j] for i in range(N) for j in range(SHIFTS_PER_WEEK) if j % 2 == 0) +
    gp.quicksum(Cost_Weekend[i] * x[i, j] for i in range(N) for j in range(SHIFTS_PER_WEEK) if j % 2 == 1) +
    gp.quicksum(Cost_Overtime[i] * a[i] for i in range(N)), GRB.MINIMIZE)

# Constraints
# Each shift must be staffed with at least 6 nurses
for j in range(SHIFTS_PER_WEEK):
    model.addConstr(gp.quicksum(x[i, j] for i in range(N)) >= 6, f"MinNurses_Shift{j}")

# Each nurse can work between 36 and 60 hours per week
for i in range(N):
    model.addConstr(HOURS_PER_SHIFT * gp.quicksum(x[i, j] for j in range(SHIFTS_PER_WEEK)) >= MIN_HOURS, f"MinHours_Nurse{i}")
    model.addConstr(HOURS_PER_SHIFT * gp.quicksum(x[i, j] for j in range(SHIFTS_PER_WEEK)) <= MAX_HOURS, f"MaxHours_Nurse{i}")

# Each shift must include at least one SRN
for j in range(SHIFTS_PER_WEEK):
    model.addConstr(gp.quicksum(x[i, j] for i in range(N) if Category[i] == 'SRN') >= 1, f"MinSRN_Shift{j}")

# Nurses cannot be scheduled for back-to-back shifts
for i in range(N):
    for j in range(SHIFTS_PER_WEEK - 1):
        model.addConstr(x[i, j] + x[i, j + 1] <= 1, f"NoBackToBack_Nurse{i}_Shift{j}")

# Overtime shifts calculation

for i in range(N):
    model.addConstr(o[i] >= gp.quicksum(x[i, j] for j in range(SHIFTS_PER_WEEK)) - MIN_HOURS / HOURS_PER_SHIFT, f"Overtime_Nurse{i}")
    model.addConstr(y == gp.quicksum(a[i] for i in range(N)), "TotalOvertime") # Updated constraint

# Optimize the model
model.optimize()

# Print the solution
if model.Status == GRB.OPTIMAL:
    print("Optimal solution found:")
    for i in range(N):
        for j in range(SHIFTS_PER_WEEK):
            if x[i, j].X > 0.5:
                if a[i].X > 0:
                    print(f"Nurse {i} (Category: {Category[i]}) works shift {j} (Overtime)")
                else:
                    print(f"Nurse {i} (Category: {Category[i]}) works shift {j} (Regular)")
else:
    print("No optimal solution found.")

print(f"Total cost: {model.ObjVal}")
print(f"Total overtime shifts: {y.X}")

print(f"Decision Variables: {sum(v.x for v in model.getVars())}")



