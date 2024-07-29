import streamlit as st
import pandas as pd
import numpy as np
import pulp

st.subheader("Pembahasan")
st.write("""Bahan baku seblak dalam sehari maksimal bahan yang diperlukan 200 bungkus mie, 48 telur, 450 bakso, 500 kerupuk. 
         Dimana penjual memproduksi beberapa jenis seblak seperti seblak mie, dan seblak telur. 
         Setiap satu porsi seblak mie membutuhkan 1 bungkus mie, 1 telur, 7 bakso, dan 8 kerupuk. 
         Sedangkan satu porsi seblak telur membutuhkan 1 telur, 10 bakso, dan 10 kerupuk. 
         Dalam sehari penjual seblak dapat memproduksi 20 porsi seblak mie, 30 porsi seblak telur, dan maksimal memproduksi sebanyak 60 porsi. 
         Seblak mie, dan seblak telur bisa mendapatkan keuntungan sebanyak Rp.250.000 dan Rp.350.000 dalam sehari.""")

# Create a dictionary from the provided data
data = {
    'bahan': ['porsi', 'mie', 'telur', 'bakso', 'kerupuk'],
    'seblak mie': [20, 1, 1, 7, 8],
    'seblak telur': [30, 0, 1, 10, 10],
    'stok tersedia': [60, 200, 48, 450, 500]
}

# Convert the dictionary into a pandas DataFrame
df = pd.DataFrame(data)

# Tabs
tab1, tab2 = st.tabs(["Static", "Dynamic"])

with tab1:
    st.title("Seblak Black")
    st.table(df)

    st.subheader("Variabel keputusan :")
    st.write("x1 : seblak mie")
    st.write("x2 : seblak telur")

    st.subheader("Fungsi Tujuan :")
    st.write("maks Z = 25x1 + 35x2")

    st.subheader("Fungsi Pembatas :")
    st.write("porsi     : 20x1 + 30x2 <=60")
    st.write("mie       : x1 <=200")
    st.write("telur     : x1 + x2 <= 48")
    st.write("bakso     : 7x1 + 10x2 <= 450")
    st.write("kerupuk   : 8x1 + 10x2 <=500")

    st.subheader("Variabel Pembatas:")
    st.write("x1, x2 >= 0")

    # Initialize the problem
    prob = pulp.LpProblem("Seblak_Optimization", pulp.LpMaximize)

    # Decision Variables
    x1 = pulp.LpVariable('x1', lowBound=0, cat='Integer')
    x2 = pulp.LpVariable('x2', lowBound=0, cat='Integer')

    # Objective Function
    prob += 25 * x1 + 35 * x2, "Total Profit"

    # Constraints
    prob += 20 * x1 + 30 * x2 <= 60, "Total Portions"
    prob += x1 <= 200, "Mie Constraint"
    prob += x1 + x2 <= 48, "Telur Constraint"
    prob += 7 * x1 + 10 * x2 <= 450, "Bakso Constraint"
    prob += 8 * x1 + 10 * x2 <= 500, "Kerupuk Constraint"

    # Initial Tablea
    initial_tableau = np.array([
        [1, -25, -35, 0, 0, 0, 0, 0, 0],  # Z row
        [0, 20, 30, 1, 0, 0, 0, 0, 60],           # Total Portions
        [0, 1, 0, 0, 1, 0, 0, 0, 200],            # Mie Constraint
        [0, 1, 1, 0, 0, 1, 0, 0, 48],             # Telur Constraint
        [0, 7, 10, 0, 0, 0, 1, 0, 450],           # Bakso Constraint
        [0, 8, 10, 0, 0, 0, 0, 1, 500]            # Kerupuk Constraint
    ], dtype=float)

    def simplex_iteration(tableau):
        pivot_col = np.argmin(tableau[0, 1:-1]) + 1  # Find the pivot column (most negative in Z row)
        ratios = tableau[1:, -1] / tableau[1:, pivot_col]  # Calculate ratios
        ratios[tableau[1:, pivot_col] <= 0] = np.inf  # Ignore non-positive entries
        pivot_row = np.argmin(ratios) + 1  # Find the pivot row
        pivot_element = tableau[pivot_row, pivot_col]  # Find the pivot element

        if pivot_element == 0:
            st.write("Pivot element is zero, cannot proceed with iteration.")
            return tableau

        tableau[pivot_row] /= pivot_element  # Normalize pivot row
        for r in range(tableau.shape[0]):
            if r != pivot_row:
                tableau[r] -= tableau[r, pivot_col] * tableau[pivot_row]  # Perform row operations
        return tableau,pivot_col, pivot_row

    def solve_simplex(tableau):
        iterations = []
        while np.any(tableau[0, 1:-1] < 0):  # Iterate while there are negative elements in the Z row (excluding RHS)
            iterations.append(pd.DataFrame(tableau, columns=["Z", "x1", "x2", "s1", "s2", "s3", "s4", "s5", "RHS"]))                
            tableau, pivot_col, pivot_row = simplex_iteration(tableau)
            st.write(f"Pivot Column: {pivot_col}, Pivot Row: {pivot_row}")
            st.write(pd.DataFrame(tableau, columns=["Z", "x1", "x2", "s1", "s2", "s3", "s4", "s5", "RHS"]))
            if not np.any(tableau[0, 1:-1] < 0):
                    break
        iterations.append(pd.DataFrame(tableau, columns=["Z", "x1", "x2", "s1", "s2", "s3", "s4", "s5", "RHS"]))
        return iterations
    
    # Solve and get the iteration results
    iterations = solve_simplex(initial_tableau.copy())
    
    # Display initial tableau
    st.title("Tabel Standar Simpleks")
    st.table(pd.DataFrame(initial_tableau, columns=["Z", "x1", "x2", "s1", "s2", "s3", "s4", "s5", "RHS"]).astype(int))

    # Display each iteration
    for i, df in enumerate(iterations):
        
        st.subheader(f"Iteration {i+1}")
        st.write(df)

    # Solving the problem using PuLP after displaying manual iterations
    prob.solve()

    # Extracting optimal solution
    optimal_solution = {
        "x1": pulp.value(x1),
        "x2": pulp.value(x2),
        "Maximum Z": pulp.value(prob.objective)
    }

    st.subheader("Optimal Solution")
    st.write(optimal_solution)

    st.subheader("Kesimpulan Optimal Solution")
    st.write(f"""
        Berdasarkan hasil analisis linear programming melalui metode simpleks terhadap UKM Seblak Gaul milik Bapak Pitra yang berlokasi di Jl. Raya Serang-Jakarta, Penancangan, Kec. Cipocok Jaya, Kota Serang, Banten, diperoleh hasil sebagai berikut:
        
        - Jumlah Seblak Mie (x1): {optimal_solution['x1']} porsi
        - Jumlah Seblak Telur (x2): {optimal_solution['x2']} porsi
        - Nilai Fungsi Tujuan (Z): {optimal_solution['Maximum Z']}
        
        Dari hasil perhitungan, nilai variabel pembatas adalah sebagai berikut:
        - S1: 3 porsi
        - S2: 197 bakso
        - S3: 45 kerupuk
        - S4: 429 telur
        - S5: 476
        
        Interpretasi Hasil:
        1. Keuntungan Maksimal: Untuk mencapai keuntungan maksimal sebesar Rp {optimal_solution['Maximum Z']}, UKM Seblak Gaul sebaiknya memproduksi seblak mie sebanyak {optimal_solution['x1']} porsi dan seblak telur sebanyak {optimal_solution['x2']} porsi.
        2. Optimalisasi Produksi: Hasil ini menunjukkan bahwa dengan melakukan optimasi menggunakan metode PuLP, UKM Seblak Gaul dapat meningkatkan keuntungan dari sebelumnya.
        
        Rekomendasi:
        1. Fokus Produksi: Berdasarkan hasil perhitungan, produksi seblak mie sebanyak {optimal_solution['x1']} porsi dan seblak telur sebanyak {optimal_solution['x2']} porsi akan memberikan keuntungan maksimal. Disarankan untuk mengarahkan upaya produksi sesuai dengan hasil optimasi ini.
        2. Pemantauan dan Evaluasi: Lakukan pemantauan berkala terhadap proses produksi dan evaluasi hasil penjualan untuk memastikan bahwa produksi berjalan sesuai dengan rencana optimasi.
    """)

with tab2:
    st.title("Input Stok Tersedia Dinamis")
    bahan_list = ['porsi', 'mie', 'telur', 'bakso', 'kerupuk']
    stok_tersedia = []

    for bahan in bahan_list:
        stok = st.number_input(f"Stok tersedia untuk {bahan}", min_value=0, value=0, step=1)
        stok_tersedia.append(stok)

    stok_data = {'bahan': bahan_list, 'stok tersedia': stok_tersedia}
    stok_df = pd.DataFrame(stok_data)

    st.subheader("Stok Tersedia yang Dimasukkan:")
    st.table(stok_df)

    # Dynamic problem setup
    prob = pulp.LpProblem("Seblak_Optimization_Dynamic", pulp.LpMaximize)

    x1 = pulp.LpVariable('x1', lowBound=0, cat='Integer')
    x2 = pulp.LpVariable('x2', lowBound=0, cat='Integer')

    prob += 250000 * x1 + 350000 * x2, "Total Profit"

    prob += 20 * x1 + 30 * x2 <= stok_tersedia[0], "Total Portions"
    prob += x1 <= stok_tersedia[1], "Mie Constraint"
    prob += x1 + x2 <= stok_tersedia[2], "Telur Constraint"
    prob += 7 * x1 + 10 * x2 <= stok_tersedia[3], "Bakso Constraint"
    prob += 8 * x1 + 10 * x2 <= stok_tersedia[4], "Kerupuk Constraint"

    prob.solve()

    updated_optimal_solution = {
        "x1": pulp.value(x1),
        "x2": pulp.value(x2),
        "Maximum Z": pulp.value(prob.objective)
    }

    st.subheader("Updated Optimal Solution")
    st.write(updated_optimal_solution)

    st.subheader("Updated Kesimpulan Optimal Solution")
    st.write(f"""
        Berdasarkan hasil analisis linear programming melalui metode simpleks terhadap UKM Seblak Gaul milik Bapak Pitra yang berlokasi di Jl. Raya Serang-Jakarta, Penancangan, Kec. Cipocok Jaya, Kota Serang, Banten, diperoleh hasil sebagai berikut:
        
        - Jumlah Seblak Mie (x1): {updated_optimal_solution['x1']} porsi
        - Jumlah Seblak Telur (x2): {updated_optimal_solution['x2']} porsi
        - Nilai Fungsi Tujuan (Z): {updated_optimal_solution['Maximum Z']}
        
        Dari hasil perhitungan, nilai variabel pembatas adalah sebagai berikut:
        - S1: 3 porsi
        - S2: 197 bakso
        - S3: 45 kerupuk
        - S4: 429 telur
        - S5: 476
        
        Interpretasi Hasil:
        1. Keuntungan Maksimal: Untuk mencapai keuntungan maksimal sebesar Rp {updated_optimal_solution['Maximum Z']}, UKM Seblak Gaul sebaiknya memproduksi seblak mie sebanyak {updated_optimal_solution['x1']} porsi dan seblak telur sebanyak {updated_optimal_solution['x2']} porsi.
        2. Optimalisasi Produksi: Hasil ini menunjukkan bahwa dengan melakukan optimasi menggunakan metode PuLP, UKM Seblak Gaul dapat meningkatkan keuntungan dari sebelumnya.
        
        Rekomendasi:
        1. Fokus Produksi: Berdasarkan hasil perhitungan, produksi seblak mie sebanyak {updated_optimal_solution['x1']} porsi dan seblak telur sebanyak {updated_optimal_solution['x2']} porsi akan memberikan keuntungan maksimal. Disarankan untuk mengarahkan upaya produksi sesuai dengan hasil optimasi ini.
        2. Pemantauan dan Evaluasi: Lakukan pemantauan berkala terhadap proses produksi dan evaluasi hasil penjualan untuk memastikan bahwa produksi berjalan sesuai dengan rencana optimasi.
    """)