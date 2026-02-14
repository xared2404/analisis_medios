import pandas as pd

FILES = [
  ("data/bi/agenda_share_stage3_monthly.csv", ["month","Medio","entity_canon"]),
  ("data/bi/agenda_counts_stage3_monthly.csv", ["month","Medio","entity_canon"]),
  ("data/bi/scope_stage3_top500_monthly.csv", ["month","Medio"]),
  ("data/bi/hhi_stage3_monthly.csv", ["month","Medio"]),
  ("data/bi/distance_stage3_top500_monthly.csv", ["month","Medio_A","Medio_B"]),
  ("data/bi/bloc_distance_stage3_top500_monthly.csv", ["month"]),
  ("data/bi/t_mec_share_stage3_top500_monthly.csv", ["month","Medio"]),
  ("data/bi/t_mec_emotion_stage3_top500_monthly.csv", ["month","Medio"]),
  ("data/bi/t_mec_distance_stage3_top500_monthly.csv", ["month"]),
  ("data/bi/media_metadata.csv", ["Medio"]),
]

def check(path, keys):
    df = pd.read_csv(path)
    print(f"\n=== {path} ===")
    print("rows:", len(df), "| cols:", len(df.columns))
    for k in keys:
        if k not in df.columns:
            print("!! missing key col:", k)
            return
    # nulls in keys
    nk = df[keys].isna().sum().sum()
    if nk:
        print("!! NULLS in key columns:", nk)
    else:
        print("[OK] no nulls in keys")

    # duplicates in keys
    dup = df.duplicated(keys).sum()
    if dup:
        print("!! DUPLICATE KEYS:", dup)
        # show a sample
        print(df[df.duplicated(keys, keep=False)].head(5).to_string(index=False))
    else:
        print("[OK] unique keys")

for p, k in FILES:
    check(p, k)

print("\n[DONE] BI sanity check")
