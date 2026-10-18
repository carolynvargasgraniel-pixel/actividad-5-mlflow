"""Obtención y validación determinista del conjunto Wisconsin Diagnostic."""
from pathlib import Path
import hashlib, json
import pandas as pd
from sklearn.datasets import load_breast_cancer
ROOT=Path(__file__).resolve().parents[1]
def prepare():
    raw=ROOT/'datos/datos_ini/wdbc_v1.csv'
    if not raw.exists():
        ds=load_breast_cancer(as_frame=True)
        df=ds.data.copy(); df['malignant']=(ds.target==0).astype(int)
        df.to_csv(raw,index=False)
    df=pd.read_csv(raw)
    missing=int(df.isna().sum().sum()); duplicates=int(df.duplicated().sum())
    clean=df.drop_duplicates().copy()
    for c in clean.columns: clean[c]=pd.to_numeric(clean[c],errors='raise')
    assert set(clean.malignant.unique())=={0,1}
    assert (clean.drop(columns='malignant')>=0).all().all()
    clean.to_csv(ROOT/'datos/datos_limp/wdbc_v1_clean.csv',index=False)
    manifest={'version':'1.0.0','rows_raw':len(df),'rows_clean':len(clean),'duplicates_removed':duplicates,'missing_cells':missing,'source':'sklearn.datasets.load_breast_cancer; UCI WDBC, DOI 10.24432/C5DW2B','positive_class':'malignant=1','files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [raw,ROOT/'datos/datos_limp/wdbc_v1_clean.csv']}}
    (ROOT/'datos/manifest.json').write_text(json.dumps(manifest,indent=2))
    return clean,manifest
if __name__=='__main__': prepare()
