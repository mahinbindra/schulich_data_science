import pandas as pd
from gurobipy import Model, GRB, quicksum

# Read the datasets
food_categories_df = pd.read_csv('/Users/mahinbindra/Downloads/food_categories.csv')
food_preferences_df = pd.read_csv('/Users/mahinbindra/Downloads/food_preferences.csv')
nutrient_content_df = pd.read_csv('/Users/mahinbindra/Downloads/nutrient_content.csv')
nutrient_requirements_df = pd.read_csv('/Users/mahinbindra/Downloads/nutrient_requirements.csv')

# Create a new model
m = Model("OptiDiet")

# Decision Variables
foods = food_categories_df['Food_Item']
food_vars = m.addVars(foods, name="Food", lb=0)

# Objective Function: Minimize the total cost of the food items
m.setObjective(quicksum(food_vars[f] * food_categories_df.loc[food_categories_df.Food_Item == f, 'Cost_per_gram'].values[0] for f in foods), GRB.MINIMIZE)

# Nutritional Balance Constraints
nutrients = nutrient_requirements_df['Nutrient']
for nutrient in nutrients:
    min_intake = nutrient_requirements_df.loc[nutrient_requirements_df.Nutrient == nutrient, 'Min_Requirement'].values[0]
    max_intake = nutrient_requirements_df.loc[nutrient_requirements_df.Nutrient == nutrient, 'Max_Requirement'].values[0]
    
    m.addConstr(
        quicksum(food_vars[f] * nutrient_content_df.loc[nutrient_content_df['Unnamed: 0'] == f, nutrient].values[0] for f in foods) >= min_intake,
        f"min_{nutrient}"
    )
    
    m.addConstr(
        quicksum(food_vars[f] * nutrient_content_df.loc[nutrient_content_df['Unnamed: 0'] == f, nutrient].values[0] for f in foods) <= max_intake,
        f"max_{nutrient}"
    )

# Dietary Preferences Constraints
preferences = {
    'Vegetarian': 'Is_Vegetarian',
    'Vegan': 'Is_Vegan',
    'Kosher': 'Is_Kosher',
    'Halal': 'Is_Halal'
}

# Read the preference grams from the food_preferences_df DataFrame
preference_grams = food_preferences_df.iloc[0]

for pref, column in preferences.items():
    # Get the required grams for the current preference
    pref_grams = preference_grams[pref+'_grams']
    
    # Get the subset of food items that satisfy the current preference
    food_subset = food_categories_df[food_categories_df[column] == 1]['Food_Item']
    
    # Add the constraint for the current preference
    m.addConstr(quicksum(food_vars[food] for food in food_subset) <= pref_grams, f"DietPref_{pref}")

# Add the 'All' preference separately, which includes all foods
all_grams = preference_grams['All_grams']
m.addConstr(quicksum(food_vars[f] for f in foods) == all_grams, "DietPref_All")

# Variety Constraint
for f in foods:
    m.addConstr(food_vars[f] <= 0.03 * all_grams, f"Variety_{f}")

# Optimize the model
m.optimize()

# Infeasibility analysis
if m.status == GRB.Status.INFEASIBLE:
    # Compute the Irreducibly Inconsistent System (IIS)
    print('The model is infeasible; computing IIS')
    m.computeIIS()
    for c in m.getConstrs():
        if c.IISConstr:
            print(f'{c.constrName} is infeasible')

# Print the solution
if m.status == GRB.Status.OPTIMAL:
    solution = m.getAttr('x', food_vars)
    for f in foods:
        print(f"{f}: {solution[f]} grams")
else:
    print("No optimal solution found")
