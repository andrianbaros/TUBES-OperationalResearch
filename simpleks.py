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

# Tabs
tab1, tab2 = st.tabs(["Static", "Dynamic"])

with tab1:
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
        # Find the pivot column (most negative in Z row)
        pivot_col = np.argmin(tableau[0, 1:-1]) + 1
        
        # Find the pivot row
        ratios = tableau[1:, -1] / tableau[1:, pivot_col]
        ratios[tableau[1:, pivot_col] <= 0] = np.inf  # Ignore non-positive entries
        pivot_row = np.argmin(ratios) + 1
        
        # Perform pivot operation
        pivot_element = tableau[pivot_row, pivot_col]
        tableau[pivot_row] /= pivot_element  # Normalize pivot row
        
        for r in range(tableau.shape[0]):
            if r != pivot_row:
                tableau[r] -= tableau[r, pivot_col] * tableau[pivot_row]
        
        return pivot_col, pivot_row

    def solve_simplex(tableau):
        iterations = []
        while np.any(tableau[0, 1:-1] < 0):  # Iterate while there are negative elements in the Z row (excluding RHS)
            iterations.append(pd.DataFrame(tableau, columns=["Z", "x1", "x2", "s1", "s2", "s3", "s4", "s5", "RHS"]))
            pivot_col, pivot_row = simplex_iteration(tableau)
            # Check if the solution is already optimal
            if not np.any(tableau[0, 1:-1] < 0):
                break
        iterations.append(pd.DataFrame(tableau, columns=["Z", "x1", "x2", "s1", "s2", "s3", "s4", "s5", "RHS"]))
        return iterations

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

    # Display the conclusion
    st.subheader("Kesimpulan Optimal Solution")
    st.write("""
        Berdasarkan hasil analisis linear programming melalui metode simpleks terhadap UKM Seblak Gaul milik Bapak Pitra yang berlokasi di Jl. Raya Serang-Jakarta, Penancangan, Kec. Cipocok Jaya, Kota Serang, Banten, diperoleh hasil sebagai berikut:
        
        - Jumlah Seblak Mie (x1): 3 porsi
        - Jumlah Seblak Telur (x2): 0 porsi
        - Nilai Fungsi Tujuan (Z): 75 (kali 10.000) atau setara dengan Rp 750.000
        
        Dari hasil perhitungan, nilai variabel pembatas adalah sebagai berikut:
        - S1: 3 porsi
        - S2: 197 bakso
        - S3: 45 kerupuk
        - S4: 429 telur
        - S5: 476
        
        Interpretasi Hasil:
        1. Keuntungan Maksimal: Untuk mencapai keuntungan maksimal sebesar Rp 750.000, UKM Seblak Gaul sebaiknya memproduksi seblak mie sebanyak 3 porsi. Dalam perhitungan ini, seblak telur tidak diproduksi karena batasan bahan baku yang ada.
        2. Optimalisasi Produksi: Hasil ini menunjukkan bahwa dengan melakukan optimasi menggunakan metode simpleks, UKM Seblak Gaul dapat meningkatkan keuntungan dari sebelumnya. Adapun selisih keuntungan sebelum dan setelah optimasi adalah sebesar Rp 150.000.
        
        Rekomendasi:
        1. Fokus Produksi: Berdasarkan hasil perhitungan, produksi seblak mie sebanyak 3 porsi adalah pilihan terbaik untuk mencapai keuntungan maksimal.
        2. Pengelolaan Stok: Stok bahan baku perlu dikelola dengan baik untuk memastikan bahwa bahan yang tersedia cukup untuk memenuhi jumlah produksi yang optimal.
        3. Penyesuaian dan Monitoring: Lakukan pemantauan secara rutin terhadap stok bahan baku dan kondisi pasar untuk memastikan bahwa produksi tetap berjalan optimal dan menguntungkan. Jika ada perubahan signifikan dalam stok atau permintaan pasar, perhitungan ulang dengan metode simpleks perlu dilakukan.
        
        Dengan mengikuti rekomendasi ini, UKM Seblak Gaul dapat meningkatkan efisiensi produksi dan mencapai keuntungan yang lebih optimal.
    """)

with tab2:
    st.title("Input Stok Tersedia Dinamis")

    bahan_list = ['porsi', 'mie', 'telur', 'bakso', 'kerupuk']
    stok_tersedia = []

    for bahan in bahan_list:
        stok = st.number_input(f"Stok tersedia untuk {bahan}", min_value=0, value=0, step=1)
        stok_tersedia.append(stok)

    # Display the inputted stock
    stok_data = {'bahan': bahan_list, 'stok tersedia': stok_tersedia}
    stok_df = pd.DataFrame(stok_data)

    st.subheader("Stok Tersedia yang Dimasukkan:")
    st.table(stok_df)

    # Update the simplex tableau RHS with dynamic stock values
    tableau[1:, -1] = stok_tersedia

    # Display updated tableau
    st.subheader("Updated Tableau with Dynamic Stock Values")
    updated_df = pd.DataFrame(tableau, columns=["Z", "x1", "x2", "s1", "s2", "s3", "s4", "s5", "RHS"])
    st.write(updated_df)

    # Perform Simplex Method with updated tableau
    updated_iterations = solve_simplex(tableau)

    # Display iterations for updated tableau
    for i, df in enumerate(updated_iterations):
        st.subheader(f"Updated Iteration {i+1}")
        st.write(df)

    # Display updated optimal solution
    updated_optimal_solution = {
        "x1": 0,
        "x2": 0,
        "Maximum Z": -tableau[0, -1]
    }

    # Extract the solution values for updated tableau
    updated_basic_vars = np.where(np.sum(tableau[1:, 1:-1] == 1, axis=0) == 1)[0] + 1
    updated_solution = np.zeros(tableau.shape[1] - 2)

    for i in updated_basic_vars:
        if i < len(updated_solution):
            updated_solution[i - 1] = tableau[np.where(tableau[:, i] == 1)[0][0], -1]

    updated_optimal_solution["x1"] = updated_solution[0]
    updated_optimal_solution["x2"] = updated_solution[1]

    st.subheader("Updated Optimal Solution")
    st.write(updated_optimal_solution)

    # Display the updated conclusion
    st.subheader("Updated Kesimpulan Optimal Solution")
    st.write("""
        Berdasarkan hasil analisis linear programming melalui metode simpleks terhadap UKM Seblak Gaul milik Bapak Pitra yang berlokasi di Jl. Raya Serang-Jakarta, Penancangan, Kec. Cipocok Jaya, Kota Serang, Banten, diperoleh hasil sebagai berikut:
        
        - Jumlah Seblak Mie (x1): 3 porsi
        - Jumlah Seblak Telur (x2): 0 porsi
        - Nilai Fungsi Tujuan (Z): 75 (kali 10.000) atau setara dengan Rp 750.000
        
        Dari hasil perhitungan, nilai variabel pembatas adalah sebagai berikut:
        - S1: 3 porsi
        - S2: 197 bakso
        - S3: 45 kerupuk
        - S4: 429 telur
        - S5: 476
        
        Interpretasi Hasil:
        1. Keuntungan Maksimal: Untuk mencapai keuntungan maksimal sebesar Rp 750.000, UKM Seblak Gaul sebaiknya memproduksi seblak mie sebanyak 3 porsi. Dalam perhitungan ini, seblak telur tidak diproduksi karena batasan bahan baku yang ada.
        2. Optimalisasi Produksi: Hasil ini menunjukkan bahwa dengan melakukan optimasi menggunakan metode simpleks, UKM Seblak Gaul dapat meningkatkan keuntungan dari sebelumnya. Adapun selisih keuntungan sebelum dan setelah optimasi adalah sebesar Rp 150.000.
        
        Rekomendasi:
        1. Fokus Produksi: Berdasarkan hasil perhitungan, produksi seblak mie sebanyak 3 porsi adalah pilihan terbaik untuk mencapai keuntungan maksimal.
        2. Pengelolaan Stok: Stok bahan baku perlu dikelola dengan baik untuk memastikan bahwa bahan yang tersedia cukup untuk memenuhi jumlah produksi yang optimal.
        3. Penyesuaian dan Monitoring: Lakukan pemantauan secara rutin terhadap stok bahan baku dan kondisi pasar untuk memastikan bahwa produksi tetap berjalan optimal dan menguntungkan. Jika ada perubahan signifikan dalam stok atau permintaan pasar, perhitungan ulang dengan metode simpleks perlu dilakukan.
        
        Dengan mengikuti rekomendasi ini, UKM Seblak Gaul dapat meningkatkan efisiensi produksi dan mencapai keuntungan yang lebih optimal.
    """)
