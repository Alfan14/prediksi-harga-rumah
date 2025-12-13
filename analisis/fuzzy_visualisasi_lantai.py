import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Fungsi Pembersihan Data
def clean_price(price):
    if isinstance(price, str):
        # Menghapus simbol non-numerik
        price = price.replace('Rp', '').replace('.', '').replace(',', '').strip()
        # Mengambil rata-rata jika ada range harga
        if '-' in price:
            parts = [float(p) for p in price.split('-')]
            return sum(parts) / len(parts)
        try:
            return float(price)
        except ValueError:
            return np.nan
    return price

# 2. Pemrosesan Data 
file_path = 'house_pricing_madiun.csv'
df = pd.read_csv(file_path)

df['price_cleaned'] = df['price'].apply(clean_price)
df = df.dropna(subset=['price_cleaned'])

# Asumsi: Dana Pembangunan Total = 70% dari Harga Jual
df['Dana_Pembangunan_Total'] = df['price_cleaned'] * 0.70

# Proksi Biaya Lantai (35% dari Dana Pembangunan Total)
df['Lantai_Proksi'] = (df['Dana_Pembangunan_Total'] * 0.35) / 1_000_000

# 3. Visualisasi
plt.figure(figsize=(8, 6))
plt.hist(df['Lantai_Proksi'], bins=15, color='skyblue', edgecolor='black')
plt.title('Distribusi Biaya Lantai (Proksi) di Madiun', fontsize=14)
plt.xlabel('Biaya Lantai (Juta Rupiah)')
plt.ylabel('Frekuensi')
plt.grid(axis='y', alpha=0.5)
plt.show()

# 4. Statistik untuk Penentuan Domain Fuzzy 
print("Statistik Proksi Variabel Lantai (Juta Rupiah):")
print(df['Lantai_Proksi'].describe())