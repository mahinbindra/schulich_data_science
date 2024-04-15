# Modules required for this class
from gurobipy import GRB
import gurobipy as gb
import pandas as pd
import random

# Read data
df = pd.read_csv("/Users/mahinbindra/Downloads/vaccine_sales.csv")

# Descriptive statistics
df.describe()

# Model parameters
r = 5.14
v = 1.47

# The model to run: profit using SAA (0), exact (!=0)
model_type = 1

# Initialize model 
model = gb.Model("Vaccine Procruement")
 
# The SAA algorithm
if model_type == 0:

    # The sum of all objectives and decision variables
    objectives = 0
    capacities = 0
    
    # The number of trials to perform
    trials = 250
    
    # The number of scenarios per trial
    samples = 50
    
    for trial in range(trials):
    
        # The scenarios in this trial
        scenarios = random.sample(range(df.shape[0]),samples)

        # Add the capacity decision variable (common to all problems)
        x = model.addVar(lb=0, vtype=GRB.INTEGER, name="Capacity")
    
        # Deviational variables in the average model 
        d_plus = model.addVars(samples, lb=0, vtype=GRB.INTEGER, name="Above")
        d_minus = model.addVars(samples, lb=0, vtype=GRB.INTEGER, name="Below")    
        
        # Deterministic objective function 
        underage_cost = 1.0/samples * gb.quicksum((r - df.cost[scenarios[n]])*d_minus[n] for n in range(samples))
        overage_cost = 1.0/samples * gb.quicksum((r - df.cost[scenarios[n]] + v)*d_plus[n] for n in range(samples))
        revenue = 1.0/samples * gb.quicksum((r - df.cost[scenarios[n]])*x for n in range(samples))
        model.setObjective(revenue - underage_cost - overage_cost, GRB.MAXIMIZE)
        
        # Demand constraint
        for n in range(samples):
            model.addConstr(x + d_minus[n] == df.doses[scenarios[n]] + d_plus[n])

        # Optimally solve the problem
        model.optimize()
        
        # The running total
        objectives += model.objVal
        capacities += x.x
        
        # Reset the model
        model.reset(0)
        
    print("Objective: ", objectives/trials)
    print("Optimal Capacity: ", capacities/trials)

# The full model    
else:
    
    # The number of scenarios
    scenarios = df.shape[0]
    
    # Add the capacity decision variable (common to all problems)
    x = model.addVar(lb=0, vtype=GRB.INTEGER, name="Capacity")

    # Deviational variables in the average model 
    d_plus = model.addVars(scenarios, lb=0, vtype=GRB.INTEGER, name="Above")
    d_minus = model.addVars(scenarios, lb=0, vtype=GRB.INTEGER, name="Below")    
    
    # Deterministic objective function 
    underage_cost = 1.0/scenarios * gb.quicksum((r - df.cost[n])*d_minus[n] for n in range(scenarios))
    overage_cost = 1.0/scenarios * gb.quicksum((r - df.cost[n] + v)*d_plus[n] for n in range(scenarios))
    revenue = 1.0/scenarios * gb.quicksum((r - df.cost[n])*x for n in range(scenarios))
    model.setObjective(revenue - underage_cost - overage_cost, GRB.MAXIMIZE)
    
    # Demand constraint
    for n in range(scenarios):
        model.addConstr(x + d_minus[n] == df.doses[n] + d_plus[n])

    # Optimally solve the problem
    model.optimize()

    # Number of decision variables in the model
    print("Number of Decision Variables: ", model.numVars)

    # Number of constraints in the model
    print("Number of Constraints: ", model.numConstrs)
    
    # The objective and capacity level
    print("Objective: ", model.objVal)
    print("Optimal Capacity: ", x.x)