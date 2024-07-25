import streamlit as st
import pandas as pd
import numpy as np

# Create a dictionary from the provided data
data = {
    'bahan': ['porsi', 'mie', 'telur', 'bakso', 'kerupuk'],
    'seblak mie': [20, 1, 1, 7, 8],
    'seblak telur': [30, 0, 1, 10, 10],
    'stok tersedia': [60, 200, 48, 450, 500]
}

# Convert the dictionary into a pandas DataFrame
df = pd.DataFrame(data)

# Display the DataFrame in Streamlit
st.title("Seblak Black")
st.table(df)

st.subheader("Variabel keputusan :")
st.write("x1 : seblak mie")
st.write("x2 : seblak telur")

st.subheader("Fungsi Tujuan :")
st.write("maks Z = 25x1 + 35x2 ")

st.subheader("Fungsi Pembatas :")
st.write("porsi     : 20x1 + 30x2 <=60")
st.write("mie       : x1 <=200")
st.write("telur     : x1 + x2 <= 48")
st.write("bakso     : 7x1 + 10x2 <= 450")
st.write("kerupuk   : 8x1 + 10x2 <=500")

st.subheader("Variabel Pembatas:")
st.write("x1, x2 >= 0")

simplex_data = {
    'Basic Var': ['Z', 's1', 's2', 's3', 's4', 's5'],
    'Z': [1, 0, 0, 0, 0, 0],
    'x1': [-25, 20, 1, 1, 7, 8],
    'x2': [-35, 30, 0, 1, 10, 10],
    's1': [0, 1, 0, 0, 0, 0],
    's2': [0, 0, 1, 0, 0, 0],
    's3': [0, 0, 0, 1, 0, 0],
    's4': [0, 0, 0, 0, 1, 0],
    's5': [0, 0, 0, 0, 0, 1],
    'RHS': [0, 60, 200, 48, 450, 500]
}

# Convert the dictionary into a pandas DataFrame
simplex_df = pd.DataFrame(simplex_data)

# Set the 'Basic Var' column as the index
simplex_df.set_index('Basic Var', inplace=True)

# Display the DataFrame in Streamlit
st.title("Tabel Standar Simpleks")
st.table(simplex_df)

# Initial Simplex Tableau
tableau = np.array([
    [1, -25, -35, 0, 0, 0, 0, 0, 0],  # Z row
    [0, 20, 30, 1, 0, 0, 0, 0, 60],   # s1
    [0, 1, 0, 0, 1, 0, 0, 0, 200],    # s2
    [0, 1, 1, 0, 0, 1, 0, 0, 48],     # s3
    [0, 7, 10, 0, 0, 0, 1, 0, 450],   # s4
    [0, 8, 10, 0, 0, 0, 0, 1, 500]    # s5
], dtype=float)

def simplex_iteration(tableau):
    pivot_col = np.argmin(tableau[0, 1:-1]) + 1
    ratios = tableau[1:, -1] / tableau[1:, pivot_col]
    ratios[tableau[1:, pivot_col] <= 0] = np.inf
    pivot_row = np.argmin(ratios) + 1
    pivot_element = tableau[pivot_row, pivot_col]
    tableau[pivot_row] /= pivot_element
    for r in range(tableau.shape[0]):
        if r != pivot_row:
            tableau[r] -= tableau[r, pivot_col] * tableau[pivot_row]
    return pivot_col, pivot_row

def solve_simplex(tableau):
    iterations = []
    iteration = 0
    while np.any(tableau[0, 1:-1] < 0):
        iterations.append(pd.DataFrame(tableau, columns=["Z", "x1", "x2", "s1", "s2", "s3", "s4", "s5", "RHS"]))
        pivot_col, pivot_row = simplex_iteration(tableau)
        iteration += 1
    iterations.append(pd.DataFrame(tableau, columns=["Z", "x1", "x2", "s1", "s2", "s3", "s4", "s5", "RHS"]))
    return iterations

# Streamlit app
st.title("Simplex Method with Streamlit")

# Display initial tableau
st.subheader("Initial Tableau")
initial_df = pd.DataFrame(tableau, columns=["Z", "x1", "x2", "s1", "s2", "s3", "s4", "s5", "RHS"])
st.write(initial_df)

# Perform Simplex Method
iterations = solve_simplex(tableau)

# Display iterations
for i, df in enumerate(iterations):
    st.subheader(f"Iteration {i+1}")
    st.write(df)

# Display optimal solution
optimal_solution = {
    "x1": 0,
    "x2": 0,
    "Maximum Z": -tableau[0, -1]
}

# Extract the solution values
basic_vars = np.where(np.sum(tableau[1:, 1:-1] == 1, axis=0) == 1)[0] + 1
solution = np.zeros(tableau.shape[1] - 2)

for i in basic_vars:
    if i < len(solution):
        solution[i - 1] = tableau[np.where(tableau[:, i] == 1)[0][0], -1]

optimal_solution["x1"] = solution[0]
optimal_solution["x2"] = solution[1]

st.subheader("Optimal Solution")
st.write(optimal_solution)
