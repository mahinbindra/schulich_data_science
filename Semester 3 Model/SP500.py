import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Load the dataset
file_path = '/Users/mahinbindra/Downloads/sp500_data.csv'
sp500_data = pd.read_csv(file_path)

# Preprocessing to identify sectors and locations
sectors = sp500_data['GICS Sector'].unique()
companies = sp500_data['Ticker symbol'].tolist()
returns = sp500_data.set_index('Ticker symbol')['PercentReturn'].to_dict()
sector_companies = {sector: sp500_data['Ticker symbol'][sp500_data['GICS Sector'] == sector].tolist() for sector in sectors}
ny_companies = sp500_data['Ticker symbol'][sp500_data['Location of Headquarters'].str.contains('New York')].tolist()

# Initialize the model
m = gp.Model("investment_portfolio")

# Decision Variables
invest = m.addVars(companies, name="invest")

# Objective Function
m.setObjective(gp.quicksum(invest[c] * returns[c] for c in companies), GRB.MAXIMIZE)

# Constraints
# Total investment of $10 million
m.addConstr(gp.quicksum(invest[c] for c in companies) == 10e6, "total_investment")

# At most $600,000 can be invested in any individual stock
m.addConstrs((invest[c] <= 600000 for c in companies), "max_invest_individual")

# No more than $500,000 can be invested in the Telecommunications sector
telecom_sector = "Telecommunications Services"
m.addConstr(gp.quicksum(invest[c] for c in sector_companies[telecom_sector]) <= 500000, "max_invest_telecom")

# At least 75% in IT compared to Telecommunications
it_sector = "Information Technology"
m.addConstr(gp.quicksum(invest[c] for c in sector_companies[it_sector]) >= 0.75 * gp.quicksum(invest[c] for c in sector_companies[telecom_sector]), "min_invest_it")

# Difference between Consumer Discretionary and Consumer Staples
consumer_discretionary = "Consumer Discretionary"
consumer_staples = "Consumer Staples"
m.addConstr(gp.quicksum(invest[c] for c in sector_companies[consumer_discretionary]) - gp.quicksum(invest[c] for c in sector_companies[consumer_staples]) <= 200000, "consumer_difference_pos")
m.addConstr(gp.quicksum(invest[c] for c in sector_companies[consumer_staples]) - gp.quicksum(invest[c] for c in sector_companies[consumer_discretionary]) <= 200000, "consumer_difference_neg")

# At least $1 million must be invested in the Energy sector
energy_sector = "Energy"
m.addConstr(gp.quicksum(invest[c] for c in sector_companies[energy_sector]) >= 1e6, "min_invest_energy")

# At least $300,000 must be invested in companies headquartered in New York, New York
m.addConstr(gp.quicksum(invest[c] for c in ny_companies) >= 300000, "min_invest_ny")

# Solve the model
m.optimize()

# Display the solution
if m.status == GRB.OPTIMAL:
    solution = m.getAttr('x', invest)
    for c in companies:
        if solution[c] > 0:
            print(f"Invest ${solution[c]:,.2f} in {c} ({sp500_data.loc[sp500_data['Ticker symbol'] == c, 'Company'].iloc[0]})")
