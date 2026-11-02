import csv,json
from app.modelo import entrenar,ROOT
with (ROOT/'data/train.csv').open(encoding='utf-8') as f:model=entrenar(list(csv.DictReader(f)))
(ROOT/'model/modelo.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Modelo entrenado con 36 textos sinteticos; prueba reservada: data/test.csv')
