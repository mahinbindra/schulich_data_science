
from gurobipy import GRB
import gurobipy as gb
import pandas as pd
import numpy as np

# Create the model
model = gb.Model("OptiDiet")

# Load data
# Read the datasets
food_categories_df = pd.read_csv('/Users/mahinbindra/Downloads/food_categories.csv')
food_preferences_df = pd.read_csv('/Users/mahinbindra/Downloads/food_preferences.csv')
nutrient_content_df = pd.read_csv('/Users/mahinbindra/Downloads/nutrient_content.csv')
nutrient_requirements_df = pd.read_csv('/Users/mahinbindra/Downloads/nutrient_requirements.csv')

# Nutrient requirements
nutrient_names = nutrient_requirements_df['Nutrient'].tolist()
min_requirements = nutrient_requirements_df['Min_Requirement'].tolist()
max_requirements = nutrient_requirements_df['Max_Requirement'].tolist()

# Food items and categories
food_items = food_categories_df['Food_Item'].tolist()
cost_per_gram = food_categories_df['Cost_per_gram'].tolist()
dietary_preferences = ['All', 'Vegetarian', 'Vegan', 'Kosher', 'Halal']
dietary_totals = {
    'All': 577000,
    'Vegetarian': 46160,
    'Vegan': 11540,
    'Kosher': 17310,
    'Halal': 92320
}

# Decision variables
food_quantities = model.addVars(food_items, name="Food")

# Objective function: Minimize total cost
model.setObjective(gb.quicksum(cost_per_gram[i] * food_quantities[food] for i, food in enumerate(food_items)), GRB.MINIMIZE)

# Constraints
# Nutritional balance
for i, nutrient in enumerate(nutrient_names):
    model.addConstr(gb.quicksum(nutrient_content_df.loc[j, nutrient] * food_quantities[food] for j, food in enumerate(food_items)) >= min_requirements[i], f"Min_{nutrient}")
    model.addConstr(gb.quicksum(nutrient_content_df.loc[j, nutrient] * food_quantities[food] for j, food in enumerate(food_items)) <= max_requirements[i], f"Max_{nutrient}")

# Dietary preferences
for preference in dietary_preferences:
    model.addConstr(gb.quicksum(food_quantities[food] for food in food_categories_df[food_categories_df[preference] == 1]['Food_Item']) <= dietary_totals[preference], f"Total_{preference}")

# Variety: Proportion of each food item less than 3%
for food in food_items:
    model.addConstr(food_quantities[food] <= 0.03 * dietary_totals['All'], f"Variety_{food}")

# Optimize the model
model.optimize()

# Print the solution
if model.Status == GRB.OPTIMAL:
    print("Optimal solution found:")
    for food in food_items:
        quantity = food_quantities[food].X
        if quantity > 0:
            print(f"{food}: {quantity} grams")
else:
    print("No optimal solution found.")

#PART E
optimal_cost = model.ObjVal if model.Status == GRB.OPTIMAL else None

#PART F
halal_proportion = sum(food_quantities[food].X for food in food_items if 'Halal' in food) / sum(food_quantities[food].X for food in food_items)
kosher_proportion = sum(food_quantities[food].X for food in food_items if 'Kosher' in food) / sum(food_quantities[food].X for food in food_items)

#PART G and H
# Remove Variety constraints
model.remove(model.getConstrs()[-len(food_items):])
model.optimize()

# Calculate the new cost and compare
new_cost = model.ObjVal
cost_difference = new_cost - optimal_cost

#PART I
# Increase the dietary preference constraints
for preference in dietary_preferences:
    dietary_totals[preference] += 10000  # increase each by 10,000 grams
    model.getConstrByName(f"Total_{preference}").RHS = dietary_totals[preference]

model.optimize()
adjusted_cost = model.ObjVal

#PART J
# Assuming you have the reduced costs from the sensitivity analysis after optimization
reduced_cost_first_food = food_quantities[food_items[0]].RC

# The cost reduction needed for the first food to be included in the solution
cost_reduction_needed = cost_per_gram[0] - reduced_cost_first_food

