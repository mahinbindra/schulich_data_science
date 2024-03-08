import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Load the data
df = pd.read_csv('/Users/mahinbindra/Downloads/non_profits.csv')


alpha = df['alpha_i'].tolist()
beta = df['beta_i'].tolist()

budget = 50000000

# Create a new model
m = gp.Model('Funding')

# Number of nonprofits
N = len(df)

# Decision variables
a = m.addVars(N, lb=0, vtype=GRB.CONTINUOUS, name="a")
x = m.addVars(N, lb=0, vtype=GRB.CONTINUOUS, name="x") 

# Objective function
m.setObjective(gp.quicksum(2 * x[i] for i in range(N)), GRB.MAXIMIZE)

# Constraints
# Budget Constraint
m.addConstr(gp.quicksum(a[i] for i in range(N)) <= budget, "Budget")

# Power constraint using addGenConstrPow()
for i in range(N):
    m.addGenConstrPow(a[i], x[i], 2.0/3.0, f"PowConstraint_{i}")

# Optimize the model
m.optimize()

# Check the optimization status
if m.Status == GRB.OPTIMAL:
    print("Optimal solution found.")
    # Print the decision variables
    for v in m.getVars():
        print(f"{v.varName} = {v.x}")
    print(f"Objective Value: {m.ObjVal}")
elif m.Status == GRB.INFEASIBLE:
    print("Model is infeasible.")
    # Compute and print the IIS (Irreducible Inconsistent Subsystem)
    m.computeIIS()
    m.write("model.ilp")
    print("IIS written to file 'model.ilp'")
elif m.Status == GRB.UNBOUNDED:
    print("Model is unbounded.")
else:
    print(f"Optimization was stopped with status {m.Status}")


print(f"Number of constraints: {m.NumConstrs}") 
print(f"Number of decision variables: {m.NumVars}")

# Sum of decision variables in the optimal solution
sum_decision_variables = sum(v.x for v in m.getVars())
print(f"Sum of decision variables: {sum_decision_variables}")

#PART E
# Number of nonprofits
N = len(df)

# Decision variables for allocation 'a' and auxiliary variable 'x'
a = m.addVars(N, lb=0, vtype=GRB.CONTINUOUS, name="a")
x = m.addVars(N, lb=0, vtype=GRB.CONTINUOUS, name="x")  # Variable for fractional exponent

# Constraints
# Budget Constraint
m.addConstr(gp.quicksum(a[i] for i in range(N)) <= budget, "Budget")

# Power constraints
for i in range(N):
    m.addGenConstrPow(a[i], x[i], 2.0/3.0, f"PowConstraint_{i}")

# Number of decision variables (2 for each nonprofit, a and x)
num_decision_variables = m.NumVars

# Number of constraints (1 budget constraint + N power constraints)
num_constraints = m.NumConstrs

print(f"Number of decision variables: {num_decision_variables}")
print(f"Number of constraints: {num_constraints}")


#PART F
# Assuming model has been optimized and x_i are the decision variables for the output
output_value = sum(2 * x[i].x for i in range(N))

#PART H
# Assuming a is the decision variable representing the allocation for each nonprofit
num_unfunded_nonprofits = sum(1 for i in range(N) if a[i].x == 0)
