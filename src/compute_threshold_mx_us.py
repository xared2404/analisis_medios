import pandas as pd

INP = "data/bi/bloc_distance_stage3_top500_monthly.csv"

df = pd.read_csv(INP)

col = "mx_us_mean"

mean = df[col].mean()
std = df[col].std()
p75 = df[col].quantile(0.75)
p90 = df[col].quantile(0.90)

print("\n=== UMBRALES INTERPRETATIVOS MX–US ===\n")
print(f"Media: {mean:.6f}")
print(f"Desviación estándar: {std:.6f}")
print(f"Media + 1 SD: {(mean + std):.6f}")
print(f"Media + 2 SD: {(mean + 2*std):.6f}")
print(f"Percentil 75: {p75:.6f}")
print(f"Percentil 90: {p90:.6f}")
print("\n--------------------------------------\n")
