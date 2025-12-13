import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Fungsi Pembersihan Data 
def clean_price(price):
    if isinstance(price, str):
        price = price.replace('Rp', '').replace('.', '').replace(',', '').strip()
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

# Proksi Biaya Rangka (25% dari Dana Pembangunan Total)
# Konversi ke Jutaan Rupiah
df['Rangka_Proksi'] = (df['Dana_Pembangunan_Total'] * 0.25) / 1_000_000

# 3. Visualisasi 
plt.figure(figsize=(8, 6))
plt.hist(df['Rangka_Proksi'], bins=15, color='lightgreen', edgecolor='black')
plt.title('Distribusi Biaya Rangka (Proksi) di Madiun', fontsize=14)
plt.xlabel('Biaya Rangka (Juta Rupiah)')
plt.ylabel('Frekuensi')
plt.grid(axis='y', alpha=0.5)
plt.show()

# 4. Statistik untuk Penentuan Domain Fuzzy 
print("Statistik Proksi Variabel Rangka (Juta Rupiah):")
print(df['Rangka_Proksi'].describe())