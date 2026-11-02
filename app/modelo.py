import json, math, re, unicodedata
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
STOP=set('el la los las de del un una en al y se por para a mi me que fue es con lo'.split())
def tokens(text):
    t=''.join(c for c in unicodedata.normalize('NFD',text.lower()) if unicodedata.category(c)!='Mn')
    return [w for w in re.findall(r'[a-z]+',t) if w not in STOP]
def entrenar(rows):
    classes=sorted({r['categoria'] for r in rows}); counts={c:Counter() for c in classes}; docs=Counter()
    for r in rows:
        counts[r['categoria']].update(tokens(r['texto']));docs[r['categoria']]+=1
    vocab=sorted({w for cnt in counts.values() for w in cnt})
    return {'version':'nb-aclaraciones-1','vocabulario':vocab,'documentos':dict(docs),'conteos':{c:dict(v) for c,v in counts.items()}}
class Modelo:
    def __init__(self):
        self.m=json.loads((ROOT/'model/modelo.json').read_text());self.v=set(self.m['vocabulario'])
    def predict(self,text):
        ts=[w for w in tokens(text) if w in self.v]
        if len(set(ts))<2:return None,0.0
        scores={}
        for c,cnt in self.m['conteos'].items():
            denominator=sum(cnt.values())+len(self.v)
            scores[c]=math.log(self.m['documentos'][c]/sum(self.m['documentos'].values()))+sum(math.log((cnt.get(t,0)+1)/denominator) for t in ts)
        best=max(scores,key=scores.get); mx=scores[best]; z=sum(math.exp(s-mx) for s in scores.values())
        confidence=1/z
        return (best if confidence>=0.65 else None),round(confidence,6)
