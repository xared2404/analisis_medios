import pandas as pd
import re

paths = [
 "data/bi/agenda_counts_stage3_monthly.csv",
 "data/bi/agenda_share_stage3_monthly.csv",
 "data/bi/scope_stage3_top500_monthly.csv",
 "data/bi/hhi_stage3_monthly.csv",
 "data/bi/bloc_distance_stage3_top500_monthly.csv",
 "data/bi/t_mec_share_stage3_top500_monthly.csv",
 "data/bi/t_mec_emotion_stage3_top500_monthly.csv",
 "data/bi/t_mec_distance_stage3_top500_monthly.csv",
]

pat = re.compile(r"^\d{4}-\d{2}$")

for p in paths:
    df = pd.read_csv(p)
    if "month" not in df.columns:
        continue
    bad = (~df["month"].astype(str).str.match(pat)).sum()
    print(p, "| bad months:", bad, "| unique:", df["month"].nunique())
