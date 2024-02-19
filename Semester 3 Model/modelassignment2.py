import gurobipy as gp
from gurobipy import GRB

# Create a new model
model = gp.Model("SunnyshoreBay")

# Decision Variables
months = ["May", "June", "July", "August"]
borrow_m = model.addVars(months, vtype=GRB.CONTINUOUS, name="Borrow_1m", lb=0)
borrow_m2 = model.addVars(months, vtype=GRB.CONTINUOUS, name="Borrow_2m", lb=0)
borrow_m3 = model.addVars(months, vtype=GRB.CONTINUOUS, name="Borrow_3m", lb=0)
cash_balance = model.addVars(months, vtype=GRB.CONTINUOUS, name="Cash_balance", lb=0)

# Constants
initial_cash = 140000
revenues = {"May": 180000, "June": 260000, "July": 420000, "August": 580000}
expenses = {"May": 300000, "June": 400000, "July": 350000, "August": 200000}
min_balance = {"May": 25000, "June": 20000, "July": 35000, "August": 18000}
borrow_limits = {"May": 250000, "June": 150000, "July": 350000}
interest_rates = {"1m": 0.0175, "2m": 0.0225, "3m": 0.0275}

# Objective Function
model.setObjective(
    sum(borrow_m[m] * (1 + interest_rates["1m"]) for m in months[:3]) +
    sum(borrow_m2[m] * (1 + interest_rates["2m"]) for m in months[:2]) +
    borrow_m3["May"] * (1 + interest_rates["3m"]),
    GRB.MINIMIZE
)

# Constraints
# Cash balance constraints
for m in months:
    model.addConstr(cash_balance[m] >= min_balance[m], f"MinBalance_{m}")

# Borrowing limits
for m in months[:3]:
    model.addConstr(borrow_m[m] + borrow_m2[m] + borrow_m3[m] <= borrow_limits[m], f"BorrowLimit_{m}")

# July cash balance constraint
model.addConstr(cash_balance["July"] >= 0.65 * (cash_balance["May"] + cash_balance["June"]), "JulyBalanceConstraint")

# Cash flow constraints
model.addConstr(cash_balance["May"] == initial_cash + revenues["May"] - expenses["May"] + borrow_m["May"], "CashFlow_May")
model.addConstr(cash_balance["June"] == cash_balance["May"] + revenues["June"] - expenses["June"] + borrow_m["June"] - borrow_m["May"] * (1 + interest_rates["1m"]) - borrow_m2["May"] * (1 + interest_rates["2m"]), "CashFlow_June")
model.addConstr(cash_balance["July"] == cash_balance["June"] + revenues["July"] - expenses["July"] + borrow_m["July"] - borrow_m["June"] * (1 + interest_rates["1m"]) - borrow_m3["May"] * (1 + interest_rates["3m"]), "CashFlow_July")
model.addConstr(cash_balance["August"] == cash_balance["July"] + revenues["August"] - expenses["August"] - borrow_m["July"] * (1 + interest_rates["1m"]) - borrow_m2["June"] * (1 + interest_rates["2m"]), "CashFlow_August")

# Solve the model
model.optimize()

# Output the solution
if model.status == GRB.Status.OPTIMAL:
    print('Optimal solution found:')
    for v in model.getVars():
        print(f'{v.varName} = {v.x}')
else:
    print('No optimal solution found')
