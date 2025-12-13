import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz

# --- 1. DEFINISI PARAMETER FUZZY ---
# Parameter Domain Himpunan Fuzzy (dalam JUTA Rupiah)
DOMAIN_L = {
    'Murah': [0, 0, 70],
    'Sedang': [60, 100, 140],
    'Mahal': [130, 200, 200]
}
DOMAIN_B = {
    'Murah': [0, 0, 80],
    'Sedang': [65, 120, 175],
    'Mahal': [160, 250, 250]
}
DOMAIN_R = {
    'Murah': [0, 0, 50],
    'Sedang': [40, 80, 120],
    'Mahal': [110, 160, 160]
}

# Konsekuen Z (Dana Pembangunan Total, dalam JUTA Rupiah)
Z_PARAMS = {
    'Murah': 180.0, 
    'Sedang': 280.0, 
    'Mahal': 450.0 
}


# --- 2. FUNGSI LOGIKA FUZZY (Ditingkatkan untuk Robustness) ---

def hitung_derajat_keanggotaan(x, domain):
    """
    Menghitung derajat keanggotaan (mu) untuk satu variabel input.
    Menggunakan fungsi segitiga (trimf) dan trapesium (trapmf) dari skfuzzy.
    """
    mu = {}
    
    # 1. Tentukan Universe Range secara dinamis
    max_domain_val = max(p[-1] for p in domain.values())
    
    # Buat universe dengan buffer yang cukup
    x_universe = np.arange(0, max_domain_val + 5, 1)
    
    # 2. Clamping input x ke dalam batas indeks universe
    # Ini PENTING untuk mencegah IndexError pada array skfuzzy
    x_clamped = min(max(int(x), 0), len(x_universe) - 1)
    
    for key, params in domain.items():
        if key == 'Murah' and params[1] == 0:
            # Fungsi trapesium untuk Murah
            mf = fuzz.trapmf(x_universe, [params[0], params[1], params[2], params[2] + 1])
        elif key == 'Mahal' and params[2] == domain[list(domain.keys())[-1]][2]:
            # Fungsi trapesium untuk Mahal
            mf = fuzz.trapmf(x_universe, [params[0], params[0] + 1, max_domain_val, max_domain_val])
        else:
            # Fungsi Segitiga untuk Sedang
            mf = fuzz.trimf(x_universe, params)
            
        # 3. Akses array mf pada index yang sudah di-clamped
        mu[key] = mf[x_clamped]
            
    return mu

def fuzzifikasi(X1, X2, X3):
    """
    Menghitung semua derajat keanggotaan untuk ketiga variabel.
    """
    mu_L = hitung_derajat_keanggotaan(X1, DOMAIN_L)
    mu_B = hitung_derajat_keanggotaan(X2, DOMAIN_B)
    mu_R = hitung_derajat_keanggotaan(X3, DOMAIN_R)
    
    return mu_L, mu_B, mu_R

def sugeno_inferensi(mu_L, mu_B, mu_R):
    """
    Menerapkan 27 aturan Sugeno Orde Nol (Implikasi & Konsekuen).
    """
    aturan_aktif = []

    for k_L, v_L in mu_L.items():
        for k_B, v_B in mu_B.items():
            for k_R, v_R in mu_R.items():
                # Implikasi (Operator AND menggunakan MIN)
                alpha_pred = min(v_L, v_B, v_R)
                
                if alpha_pred > 1e-4: # Batas toleransi (0.0001)

                    # Penentuan Konsekuen Z berdasarkan bobot kualitas
                    bobot = 0
                    if k_L == 'Mahal': bobot += 3
                    elif k_L == 'Sedang': bobot += 2
                    else: bobot += 1

                    if k_B == 'Mahal': bobot += 3
                    elif k_B == 'Sedang': bobot += 2
                    else: bobot += 1
                        
                    if k_R == 'Mahal': bobot += 3
                    elif k_R == 'Sedang': bobot += 2
                    else: bobot += 1
                    
                    avg_bobot = bobot / 3
                    
                    if avg_bobot >= 2.5: 
                        Z = Z_PARAMS['Mahal']
                    elif avg_bobot <= 1.5: 
                        Z = Z_PARAMS['Murah']
                    else: 
                        Z = Z_PARAMS['Sedang']
                    
                    aturan_aktif.append({
                        'kombinasi': f"{k_L}-{k_B}-{k_R}",
                        'alpha': alpha_pred,
                        'Z': Z
                    })
    return aturan_aktif

def defuzzifikasi(aturan_aktif):
    """
    Menghitung hasil prediksi akhir menggunakan Rata-Rata Terbobot.
    """
    if not aturan_aktif:
        return 0.0

    pembilang = sum(r['alpha'] * r['Z'] for r in aturan_aktif)
    penyebut = sum(r['alpha'] for r in aturan_aktif)
    
    if penyebut == 0:
        return 0.0
        
    Z_akhir = pembilang / penyebut
    return Z_akhir

# --- 3. FUNGSI UTILITY & VISUALISASI ---

def plot_membership(domain, title, ax, input_val, mu_dict):
    """Membuat plot Derajat Keanggotaan"""
    
    max_domain_val = max(p[-1] for p in domain.values())
    x_universe = np.arange(0, max_domain_val + 5, 1)

    for key, params in domain.items():
        if key == 'Murah' and params[1] == 0:
             # Fungsi trapesium untuk Murah
            mf = fuzz.trapmf(x_universe, [params[0], params[1], params[2], params[2]+1])
        elif key == 'Mahal' and params[2] == domain[list(domain.keys())[-1]][2]:
            # Fungsi trapesium untuk Mahal
            mf = fuzz.trapmf(x_universe, [params[0], params[0]+1, max_domain_val, max_domain_val])
        else:
            # Fungsi Segitiga untuk Sedang
            mf = fuzz.trimf(x_universe, params)
            
        ax.plot(x_universe, mf, label=key)

    ax.set_title(title)
    ax.set_xlabel('Biaya (Juta Rupiah)')
    ax.set_ylabel('Derajat Keanggotaan ($\mu$)')
    ax.legend()
    
    # Tandai posisi input dan derajat keanggotaan tertinggi
    plot_input_val = min(max(input_val, 0), max_domain_val) 
    
    mu_values = [v for v in mu_dict.values() if v > 1e-4]
    if mu_values:
        max_mu = max(mu_values)
        ax.axvline(plot_input_val, color='gray', linestyle='--', alpha=0.7)
        ax.scatter(plot_input_val, max_mu, color='red', zorder=5, label='Input $\\mu_{max}$')
        ax.legend()


# --- 4. STREAMLIT APP ---

def main():
    st.set_page_config(layout="wide")
    st.title("🏡 Prediksi Dana Pembangunan (Fuzzy Sugeno) - Madiun")
    st.markdown("Aplikasi ini menggunakan Inferensi Fuzzy Sugeno untuk memprediksi total dana pembangunan rumah berdasarkan estimasi biaya material di Madiun. (Satuan dalam Juta Rupiah).")

    # --- INPUT SIDEBAR ---
    st.sidebar.header("Input Estimasi Biaya (Juta Rupiah)")
    st.sidebar.markdown("**Input ini adalah estimasi total biaya material (bukan per m²)**")

    # Input Sliders (Batas slider disesuaikan dengan DOMAIN)
    X1 = st.sidebar.slider("1. Biaya Material Lantai (X₁)", 0, 200, 100)
    X2 = st.sidebar.slider("2. Biaya Bahan Pokok (X₂)", 0, 250, 120)
    X3 = st.sidebar.slider("3. Biaya Material Rangka (X₃)", 0, 160, 80)
    
    # --- PROSES FUZZY ---
    
    mu_L, mu_B, mu_R = fuzzifikasi(X1, X2, X3)
    aturan_aktif = sugeno_inferensi(mu_L, mu_B, mu_R)
    prediksi_Z = defuzzifikasi(aturan_aktif)
    
    # --- OUTPUT UTAMA ---
    st.header("Hasil Prediksi Dana Pembangunan Total")
    
    if prediksi_Z > 0:
        st.success(f"## 💰 Dana Pembangunan Diprediksi: Rp {prediksi_Z:,.0f} Juta")
        st.markdown(f"*(Setara dengan **Rp {prediksi_Z * 1_000_000:,.0f}**)*")
        st.info("Prediksi ini adalah estimasi Biaya Borongan Total (Material + Upah) untuk rumah dengan kualitas yang sesuai dengan kombinasi input.")
    else:
        st.warning("Tidak ada aturan fuzzy yang aktif. Coba sesuaikan rentang input.")
    
    # --- VISUALISASI DERIVATIF ---
    st.header("Detail Proses Inferensi")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("1. Fuzzifikasi Lantai (X₁)")
        for k, v in mu_L.items():
            st.text(f"  μ({k}) = {v:.3f}")
        fig, ax = plt.subplots(figsize=(6, 4))
        plot_membership(DOMAIN_L, 'Lantai', ax, X1, mu_L)
        st.pyplot(fig)

    with col2:
        st.subheader("2. Fuzzifikasi Bahan (X₂)")
        for k, v in mu_B.items():
            st.text(f"  μ({k}) = {v:.3f}")
        fig, ax = plt.subplots(figsize=(6, 4))
        plot_membership(DOMAIN_B, 'Bahan Pokok', ax, X2, mu_B)
        st.pyplot(fig)

    with col3:
        st.subheader("3. Fuzzifikasi Rangka (X₃)")
        for k, v in mu_R.items():
            st.text(f"  μ({k}) = {v:.3f}")
        fig, ax = plt.subplots(figsize=(6, 4))
        plot_membership(DOMAIN_R, 'Rangka Atap', ax, X3, mu_R)
        st.pyplot(fig)

    # --- TABEL ATURAN AKTIF & DEFUZZIFIKASI ---
    st.subheader("4. Aturan Fuzzy Aktif (Implikasi)")
    
    df_rules = pd.DataFrame(aturan_aktif)
    if not df_rules.empty:
        # Penamaan kolom yang konsisten (Fix KeyError lama)
        df_rules = df_rules.rename(columns={'kombinasi': 'Kombinasi Input', 
                                            'alpha': 'alpha_pred (MIN)', 
                                            'Z': 'Z (Konsekuen Madiun)'})
        df_rules['alpha_pred * Z'] = df_rules['alpha_pred (MIN)'] * df_rules['Z (Konsekuen Madiun)']
        
        st.dataframe(df_rules)
        
        # Menggunakan nama kolom yang konsisten di markdown
        st.markdown(f"""
        <div style="background-color: #e6f7ff; padding: 10px; border-radius: 5px;">
        **Defuzzifikasi (Weighted Average):**
        $$\\text{{Total Pembilang }} (\\sum \\alpha_i \\cdot Z_i) = \\text{{Rp }} {df_rules['alpha_pred * Z'].sum():,.3f} \\text{{ Juta}}$$
        $$\\text{{Total Penyebut }} (\\sum \\alpha_i) = {df_rules['alpha_pred (MIN)'].sum():,.3f}$$
        $$\\text{{Prediksi Z Akhir}} = \\frac{{ {df_rules['alpha_pred * Z'].sum():,.3f} }}{{ {df_rules['alpha_pred (MIN)'].sum():,.3f} }} = \\mathbf{{\\text{{Rp }} {prediksi_Z:,.3f} \\text{{ Juta}}}}$$
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada kombinasi aturan yang memiliki derajat keanggotaan aktif.")

if __name__ == "__main__":
    main()