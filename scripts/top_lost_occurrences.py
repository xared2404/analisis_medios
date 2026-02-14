import pandas as pd

base = pd.read_csv("data/processed/entities_long.csv",
                   usecols=["entity","entity_type"], dtype=str, low_memory=False)

clean = pd.read_csv("data/processed/entities_long_clean.csv",
                    usecols=["entity","entity_type"], dtype=str, low_memory=False)

b = base.groupby(["entity_type","entity"]).size().reset_index(name="base_n")
c = clean.groupby(["entity_type","entity"]).size().reset_index(name="clean_n")

m = b.merge(c, on=["entity_type","entity"], how="left")
m["clean_n"] = m["clean_n"].fillna(0).astype(int)
m["lost_n"] = m["base_n"] - m["clean_n"]

for t in ["ORG","PER","LOC","MISC"]:
    sub = m[m["entity_type"]==t].sort_values("lost_n", ascending=False).head(25)
    print(f"\n=== TOP lost OCCURRENCES {t} ===")
    print(sub[["entity","base_n","clean_n","lost_n"]].to_string(index=False))
