import pandas as pd

df = pd.read_csv("data/processed/articles_emotions.csv")
ents = pd.read_csv("data/processed/entities_long.csv")

print("articles:", df.shape)
print("entities:", ents.shape)

print("\nTop 10 medios por volumen:")
print(df["Medio"].value_counts().head(10))

print("\nPromedio anger por medio (top 10 por volumen):")
top_medios = df["Medio"].value_counts().head(10).index
print(df[df["Medio"].isin(top_medios)].groupby("Medio")["anger"].mean().sort_values(ascending=False))

print("\nTop 20 entidades globales:")
print(ents["entity"].value_counts().head(20))
