"""Grid Search, holdout, bootstrap pareado y registro MLflow. Ejecutar desde raíz."""
import os
os.environ['MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING']='false'
from pathlib import Path
import json, hashlib, subprocess, time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import binomtest
from sklearn.model_selection import train_test_split,StratifiedKFold,GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,ConfusionMatrixDisplay,RocCurveDisplay
import mlflow,mlflow.sklearn
from mlflow.models import infer_signature
from datos_prep import prepare,ROOT

def main():
    df,manifest=prepare(); out=ROOT/'resultados'; out.mkdir(exist_ok=True)
    X=df.drop(columns='malignant'); y=df.malignant
    tr,te=train_test_split(np.arange(len(df)),test_size=.2,stratify=y,random_state=42)
    pd.DataFrame({'row':np.r_[tr,te],'partition':['train']*len(tr)+['test']*len(te)}).to_csv(out/'split.csv',index=False)
    Xtr,Xte=X.iloc[tr],X.iloc[te]; ytr,yte=y.iloc[tr],y.iloc[te]
    cv=StratifiedKFold(5,shuffle=True,random_state=42)
    scoring={'accuracy':'accuracy','precision':'precision','recall':'recall','f1':'f1','roc_auc':'roc_auc'}
    configs={
    'LogisticRegression':(Pipeline([('imputer',SimpleImputer(strategy='median')),('scale',StandardScaler()),('model',LogisticRegression(max_iter=3000,solver='liblinear',random_state=42))]),{'model__C':[.01,.1,1,10,100],'model__class_weight':[None,'balanced']}),
    'RandomForest':(Pipeline([('imputer',SimpleImputer(strategy='median')),('model',RandomForestClassifier(random_state=42,n_jobs=1))]),{'model__n_estimators':[100,200],'model__max_depth':[None,5],'model__min_samples_leaf':[1,3],'model__class_weight':[None,'balanced']})}
    mlflow.set_tracking_uri((ROOT/'mlruns').as_uri()); mlflow.set_experiment('Actividad5_WDBC_v1')
    rows=[]; predictions={}; scores={}; folds={}; runids={}
    fig,axs=plt.subplots(1,2,figsize=(10,4))
    for name,(pipe,grid) in configs.items():
        with mlflow.start_run(run_name=name) as run:
            runids[name]=run.info.run_id
            search=GridSearchCV(pipe,grid,cv=cv,scoring=scoring,refit='f1',n_jobs=2,return_train_score=True)
            start=time.perf_counter(); search.fit(Xtr,ytr); elapsed=time.perf_counter()-start
            best=search.best_estimator_; pred=best.predict(Xte); prob=best.predict_proba(Xte)[:,1]
            predictions[name]=pred; scores[name]=prob
            folds[name]=[float(search.cv_results_[f'split{k}_test_f1'][search.best_index_]) for k in range(5)]
            metrics={'accuracy':accuracy_score(yte,pred),'precision':precision_score(yte,pred),'recall':recall_score(yte,pred),'f1':f1_score(yte,pred),'roc_auc':roc_auc_score(yte,prob),'cv_f1_mean':search.best_score_,'cv_f1_std':search.cv_results_['std_test_f1'][search.best_index_],'fit_seconds':elapsed}
            rows.append({'model':name,**metrics,'params':json.dumps(search.best_params_)})
            pd.DataFrame(search.cv_results_).to_csv(out/f'grid_{name}.csv',index=False)
            mlflow.log_params({**{k:str(v) for k,v in search.best_params_.items()},'seed':42,'cv_folds':5,'refit':'f1','train_rows':len(tr),'test_rows':len(te),'threshold':.5,'raw_sha256':manifest['files']['datos/datos_ini/wdbc_v1.csv'],'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
            mlflow.log_metrics({k:float(v) for k,v in metrics.items()})
            mlflow.set_tags({'dataset_version':'1.0.0','positive_class':'malignant','purpose':'academic'})
            mlflow.log_input(mlflow.data.from_pandas(df,source='datos/datos_ini/wdbc_v1.csv',name='WDBC_v1',targets='malignant'),context='dataset_before_split')
            mlflow.sklearn.log_model(best,name='model',signature=infer_signature(Xtr,best.predict(Xtr)),input_example=Xtr.head(3))
            ConfusionMatrixDisplay.from_predictions(yte,pred,ax=axs[len(rows)-1],colorbar=False); axs[len(rows)-1].set_title(name)
            mlflow.log_artifact(str(out/f'grid_{name}.csv'))
            mlflow.log_artifact(str(ROOT/'datos/manifest.json'))
            mlflow.log_artifact(str(out/'split.csv'))
            mlflow.log_artifact(str(Path(__file__)))
    fig.tight_layout(); fig.savefig(out/'confusion.png',dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4))
    for name in scores: RocCurveDisplay.from_predictions(yte,scores[name],name=name,ax=ax)
    fig.tight_layout();fig.savefig(out/'roc.png',dpi=160);plt.close(fig)
    pd.DataFrame(rows).to_csv(out/'comparacion.csv',index=False)
    names=list(predictions); rng=np.random.default_rng(42); deltas=[]
    for _ in range(2000):
        idx=rng.integers(0,len(te),len(te)); yt=yte.to_numpy()[idx]
        deltas.append(f1_score(yt,predictions[names[0]][idx],zero_division=0)-f1_score(yt,predictions[names[1]][idx],zero_division=0))
    a=predictions[names[0]]==yte.to_numpy(); b=predictions[names[1]]==yte.to_numpy(); b01=int((a&~b).sum()); b10=int((~a&b).sum())
    stats={'bootstrap_iterations':2000,'delta_f1_LR_minus_RF_95ci':np.quantile(deltas,[.025,.975]).tolist(),'discordant_LR_only_correct':b01,'discordant_RF_only_correct':b10,'mcnemar_exact_p':float(binomtest(b01,b01+b10).pvalue) if b01+b10 else 1.,'cv_fold_f1':folds,'run_ids':runids,'n_train':len(tr),'n_test':len(te),'train_positive':int(ytr.sum()),'test_positive':int(yte.sum()),'best_by_cv':max(rows,key=lambda r:r['cv_f1_mean'])['model']}
    (out/'estadistica.json').write_text(json.dumps(stats,indent=2))
    pd.DataFrame({'row':te,'actual':yte.to_numpy(),**{n:predictions[n] for n in names},**{n+'_prob':scores[n] for n in names}}).to_csv(out/'predicciones.csv',index=False)
    # EDA calculado exclusivamente sobre train para no inspeccionar el holdout.
    fig,axs=plt.subplots(1,2,figsize=(10,4)); ytr.value_counts().sort_index().plot.bar(ax=axs[0],color=['#1a8791','#d18c44']);axs[0].set(title='Clases en entrenamiento',xlabel='0 benigno / 1 maligno',ylabel='Casos')
    Xtr.boxplot(column=['mean radius','mean texture','mean smoothness'],ax=axs[1]);axs[1].set_title('Escalas diferentes (sin escalar)');fig.tight_layout();fig.savefig(out/'calidad.png',dpi=160);plt.close(fig)
    corr=Xtr.corr(); fig,ax=plt.subplots(figsize=(8,7));im=ax.imshow(corr,cmap='coolwarm',vmin=-1,vmax=1);ax.set_xticks(range(30),X.columns,rotation=90,fontsize=5);ax.set_yticks(range(30),X.columns,fontsize=5);fig.colorbar(im,ax=ax);fig.tight_layout();fig.savefig(out/'correlacion.png',dpi=160);plt.close(fig)
    q1=Xtr.quantile(.25);q3=Xtr.quantile(.75);iqr=q3-q1
    audit={'train_cells_outside_IQR_fences':int(((Xtr<q1-1.5*iqr)|(Xtr>q3+1.5*iqr)).sum().sum()),'corr_radius_perimeter':float(corr.loc['mean radius','mean perimeter']),'missing_cells':manifest['missing_cells'],'duplicates_removed':manifest['duplicates_removed']}
    (out/'calidad.json').write_text(json.dumps(audit,indent=2))
    for name,rid in runids.items():
        with mlflow.start_run(run_id=rid):
            mlflow.log_artifacts(str(out),artifact_path='resultados')
    print(pd.DataFrame(rows).to_string(index=False)); print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
