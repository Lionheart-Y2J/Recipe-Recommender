import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tkinter as tk
from tkinter import messagebox, ttk

# Charger les données
df_recipes = pd.read_csv('RAW_recipes.csv', encoding='utf-8')

# Nettoyage des données
df_recipes = df_recipes[['name', 'ingredients', 'steps', 'minutes', 'n_steps', 'n_ingredients']]
df_recipes = df_recipes.dropna()
df_recipes['ingredients'] = df_recipes['ingredients'].str.replace('[^a-zA-Z, ]', '', regex=True)
df_recipes['ingredients'] = df_recipes['ingredients'].str.lower()

# Fonction pour recommander des recettes
def recommend_recipes(user_ingredients, n=20):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df_recipes['ingredients'])
    
    user_input = [' '.join(user_ingredients)]
    user_vector = vectorizer.transform(user_input)
    
    similarities = cosine_similarity(user_vector, tfidf_matrix)
    
    recipe_indices = similarities[0].argsort()[-n:][::-1]
    recommendations = df_recipes.iloc[recipe_indices]
    return recommendations

# Afficher les détails d'une recette sous forme de liste d'étapes avec défilement
def show_recipe_details(recipe):
    details_window = tk.Toplevel(root)
    details_window.title(recipe['name'])
    details_window.geometry("600x400")

    tk.Label(details_window, text=f"{recipe['name']}", font=("Arial", 18, "bold")).pack(pady=10)
    tk.Label(details_window, text=f"Ingredients: {recipe['ingredients']}", font=("Arial", 12), wraplength=550, justify="left").pack(pady=10)

    # Créer une frame scrollable pour les étapes
    steps_frame = tk.Frame(details_window)
    steps_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(steps_frame)
    scrollbar = ttk.Scrollbar(steps_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    steps = recipe['steps'].strip("[]").replace("'", "").split(', ')
    for i, step in enumerate(steps, 1):
        tk.Label(scrollable_frame, text=f"Étape {i}: {step}", font=("Arial", 12), wraplength=550, justify="left").pack(anchor="w", pady=2)

# Fenêtre de résultats
def show_results(results):
    global result_window
    if 'result_window' in globals() and result_window.winfo_exists():
        result_window.destroy()
    
    result_window = tk.Toplevel(root)
    result_window.title("Recipe Results")
    result_window.geometry("800x600")

    frame = tk.Frame(result_window)
    frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    if results.empty:
        tk.Label(scrollable_frame, text="No recipes found.", font=("Arial", 12)).pack(pady=10)
    else:
        for _, row in results.iterrows():
            recipe_button = tk.Button(scrollable_frame, text=row['name'], font=("Arial", 14, "bold"), anchor="w", command=lambda r=row: show_recipe_details(r))
            recipe_button.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(scrollable_frame, text=f"Ingredients: {row['ingredients']}", font=("Arial", 11), wraplength=750, justify="left").pack(pady=5)
            ttk.Separator(scrollable_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)

# Interface utilisateur
def on_submit():
    user_input = entry.get()
    user_ingredients = [x.strip() for x in user_input.split(',')]
    if not user_ingredients or user_ingredients == ['']:
        messagebox.showerror("Error", "Please enter at least one ingredient.")
        return

    results = recommend_recipes(user_ingredients)
    show_results(results)

# Configurer la fenêtre principale
root = tk.Tk()
root.title("Recipe Recommender")

label = tk.Label(root, text="Enter ingredients (comma separated):")
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

submit_button = tk.Button(root, text="Find Recipes", command=on_submit)
submit_button.pack(pady=10)

root.mainloop()
