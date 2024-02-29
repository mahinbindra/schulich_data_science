from gurobipy import Model, GRB, quicksum
import pandas as pd

# Load the player data
players_df = pd.read_csv('/Users/mahinbindra/Downloads/BasketballPlayers.csv')

# Initialize the model
m = Model("team_selection")

# Decision variables: x[i] == 1 if player i is selected, 0 otherwise
x = m.addVars(len(players_df), vtype=GRB.BINARY, name="x")

# Position requirements based on predefined flags for guard and forward/center positions
guard_flags = [1 if pos in ['G', 'G/F'] else 0 for pos in players_df['Position']]
forward_center_flags = [1 if pos in ['F', 'C', 'F/C'] else 0 for pos in players_df['Position']]

# Apply position requirements
m.addConstr(quicksum(x[i] * guard_flags[i] for i in range(len(players_df))) >= 0.3 * 21, "min_guards")
m.addConstr(quicksum(x[i] * forward_center_flags[i] for i in range(len(players_df))) >= 0.4 * 21, "min_forwards_centers")

# Skill average requirement for each skill without division, optimized for clarity and efficiency
skills_columns = ['Ball Handling', 'Shooting', 'Rebounding', 'Defense', 'Athletic Ability', 'Toughness', 'Mental Acuity']
for skill in skills_columns:
    m.addConstr(quicksum(players_df[skill][i] * x[i] for i in range(len(players_df))) >= 2.05 * 21, f"skill_avg_{skill}")

# Specific invitations and exclusions, optimized for clarity
m.addConstr(quicksum(x[i] for i in range(19, 24)) + quicksum(x[i] for i in range(71, 78)) <= 1, "exclusion_rule_1")
m.addConstr(quicksum(x[i] for i in range(104, 114)) <= quicksum(x[i] for i in range(44, 49)) + quicksum(x[i] for i in range(64, 69)), "inclusion_rule_2")

# Diverse representation, ensuring at least one player from each specified group is selected
for k in range(0, 150, 10):  # Adjusted to cover the full range of players
    m.addConstr(quicksum(x[i] for i in range(k, min(k+10, len(players_df)))) >= 1, f"group_{k+1}-{k+10}")

# Total players constraint to ensure exactly 21 players are selected
m.addConstr(quicksum(x[i] for i in range(len(players_df))) == 21, "total_players")

# Objective function to maximize the total skill rating
m.setObjective(quicksum(quicksum(players_df[skill][i] * x[i] for i in range(len(players_df))) for skill in skills_columns), GRB.MAXIMIZE)

# Optimize model
m.optimize()

# # Print selected players
# if m.status == GRB.Status.OPTIMAL:
#     selected_players = [i for i in range(len(players_df)) if x[i].X > 0.5]
#     print("Selected players:", selected_players)
# else:
#     print("No feasible solution found.")

# Output results
if m.status == GRB.Status.OPTIMAL:
    selected_players = [i for i in range(len(players_df)) if x[i].X > 0.5]
    num_guards = sum(x[i].X * guard_flags[i] for i in range(len(players_df)))
    num_forwards_centers = sum(x[i].X * forward_center_flags[i] for i in range(len(players_df)))
    print("Selected players:", selected_players)
    print("Number of guards selected:", num_guards)
    print("Number of forwards/centers selected:", num_forwards_centers)
    print("Total value of the objective function:", m.objVal)
else:
    print("No feasible solution found.")


# Part H
from gurobipy import Model, GRB, quicksum
import pandas as pd

# Load the dataset
players_df = pd.read_csv('/Users/mahinbindra/Downloads/BasketballPlayers.csv')  # Update the path to your dataset

# Initialize variables for the model
skills_columns = ['Ball Handling', 'Shooting', 'Rebounding', 'Defense', 'Athletic Ability', 'Toughness', 'Mental Acuity']
guard_flags = [1 if pos in ['G', 'G/F'] else 0 for pos in players_df['Position']]
forward_center_flags = [1 if pos in ['F', 'C', 'F/C'] else 0 for pos in players_df['Position']]

# Iterate to find the smallest number of invitations
for total_invitations in range(21, 0, -1):
    m = Model("team_selection")

    # Decision variables for each player
    x = m.addVars(len(players_df), vtype=GRB.BINARY, name="Player")

    # Position requirements
    m.addConstr(quicksum(x[i] * guard_flags[i] for i in range(len(players_df))) >= 0.3 * total_invitations, "MinGuards")
    m.addConstr(quicksum(x[i] * forward_center_flags[i] for i in range(len(players_df))) >= 0.4 * total_invitations, "MinForwardsCenters")

    # Skill average requirements
    for skill in skills_columns:
        m.addConstr(quicksum(players_df.at[i, skill] * x[i] for i in range(len(players_df))) >= 2.05 * total_invitations, f"Avg{skill}")

    # Specific invitation and exclusion rules as defined in the problem statement
    # Adjust these constraints as needed based on your problem statement

    # Total invitations constraint
    m.addConstr(quicksum(x[i] for i in range(len(players_df))) == total_invitations, "TotalInvitations")

    # Dummy objective, since we're focusing on feasibility
    m.setObjective(quicksum(x[i] for i in range(len(players_df))), GRB.MAXIMIZE)

    # Optimize the model
    m.optimize()

    if m.status == GRB.INFEASIBLE:
        smallest_feasible_invitations = total_invitations + 1
        break

# Print the result
if 'smallest_feasible_invitations' in locals():
    print(f"The smallest number of training camp invitations before yielding an infeasible solution is: {smallest_feasible_invitations}")
else:
    print("The model was feasible with all tested numbers of invitations down to 1.")
