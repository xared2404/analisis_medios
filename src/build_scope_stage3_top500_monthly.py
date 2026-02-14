import pandas as pd

INP = "data/bi/agenda_share_stage3_monthly.csv"
OUT = "data/bi/scope_stage3_top500_monthly.csv"

df = pd.read_csv(INP, dtype={
    "month":"string",
    "Medio":"string",
    "entity_canon":"string",
    "share_within_medio_month":"float64"
})

# --- Diccionarios básicos ---

mex_states = {
    "nuevo leon","jalisco","veracruz","chiapas","sinaloa","puebla",
    "oaxaca","guerrero","michoacan","colima","sonora","yucatan",
    "tabasco","coahuila","durango","zacatecas","hidalgo","queretaro",
    "tlaxcala","nayarit","campeche","baja california","quintana roo",
    "estado de mexico","cdmx","ciudad de mexico"
}

mex_keywords = {
    "mexico","morena","pan","pri","ine",
    "andres manuel lopez obrador","claudia sheinbaum",
    "lopez obrador","sheinbaum","amlo",
    "palacio nacional","congreso","senado",
    "poder judicial","fiscalia general de la republica"
}

def classify_scope(e):
    e = str(e).lower()
    
    if any(k in e for k in mex_keywords):
        return "national"
    
    if any(s in e for s in mex_states):
        return "national"
    
    if "mexico" in e:
        return "national"
    
    return "international"

df["scope"] = df["entity_canon"].map(classify_scope)

agg = (
    df.groupby(["month","Medio","scope"], as_index=False)
      .agg(
          total_share=("share_within_medio_month","sum")
      )
)

pivot = (
    agg.pivot(index=["month","Medio"],
              columns="scope",
              values="total_share")
       .reset_index()
)

pivot = pivot.fillna(0)

pivot.rename(columns={
    "national":"share_national",
    "international":"share_international"
}, inplace=True)

pivot.to_csv(OUT, index=False)

print("[OK] wrote:", OUT)
print("Rows:", len(pivot))
print(pivot.head(10))
