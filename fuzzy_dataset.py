import pandas as pd
from fuzzy_core import fuzzy_predict

df = pd.read_csv("house_pricing_madiun.csv")

df["predicted_price"] = df.apply(
    lambda r: fuzzy_predict(r["land_size"], r["building_size"]), axis=1
)

df.to_csv("predicted_output.csv", index=False)
print("Hasil tersimpan di predicted_output.csv")
