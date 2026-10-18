# Actividad 5 · Experimentos reproducibles con MLflow

Clasificación binaria de WDBC mediante regresión logística y Random Forest. Ejercicio académico; no es un sistema validado para uso clínico.

## Entregables
- [Reporte técnico en PDF](Reporte_tecnico_Actividad5.pdf)
- [Reporte técnico editable en Word](Reporte_tecnico_Actividad5.docx)
- [Cuaderno autónomo para Colab o Jupyter](fuentes/entrena.ipynb)
- [Comparación de resultados](resultados/comparacion.csv)
- [Evidencias de MLflow](evidencias/)

## Estructura
- `datos/datos_ini/wdbc_v1.csv`: copia obtenida con scikit-learn; etiqueta recodificada a malignant=1. No es el archivo original UCI byte por byte.
- `datos/datos_limp/wdbc_v1_clean.csv`: datos validados, sin duplicados.
- `datos/manifest.json`: versión y SHA-256 de datos.
- `datos/diccionario.csv`: definición de las 30 variables y etiqueta.
- `fuentes/datos_prep.py`: obtención y validación.
- `fuentes/train.py`: Grid Search, evaluación y MLflow.
- `fuentes/entrena.ipynb`: ejecución local o Colab.
- `resultados/`: búsquedas completas, predicciones, partición y análisis estadístico.
- `evidencias/`: capturas reales del experimento.
- `mlruns/`: registros y modelos generados al ejecutar el entrenamiento; excluidos del historial Git.
- `Reporte_tecnico_Actividad5.pdf`: análisis técnico.

## Reproducción
Python 3.12. Clonar el repositorio privado con una cuenta autorizada:
```bash
git clone https://github.com/carolynvargasgraniel-pixel/actividad-5-mlflow.git
cd actividad-5-mlflow
```
Desde la raíz del proyecto:
```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python fuentes/datos_prep.py
python fuentes/train.py
python -m mlflow ui --backend-store-uri ./mlruns --port 5000
```
Abrir http://127.0.0.1:5000. El entrenamiento crea dos ejecuciones nuevas con modelos, firma de entrada, métricas, parámetros, huellas de datos y código. No requiere GPU. Los tiempos dependen del hardware. Al mover una copia histórica de `mlruns`, sus URI absolutas de artefactos pueden requerir regenerar los experimentos: ejecutar `train.py` crea rutas locales válidas.

Semillas: 42; split estratificado 80/20; cinco folds estratificados compartidos; selección por F1; umbral 0.5 fijo. La prueba se reserva hasta la evaluación final. La media CV del mejor candidato tiene sesgo de selección: no se interpreta como rendimiento externo. El bootstrap pareado y McNemar usan el mismo holdout.

## Datos y licencia
Wolberg, W., Mangasarian, O., Street, N., & Street, W. (1993). Breast Cancer Wisconsin (Diagnostic). UCI. https://doi.org/10.24432/C5DW2B. Licencia CC BY 4.0. Se distribuye una copia de scikit-learn con nombres legibles y etiqueta recodificada. Los CSV no contienen identificadores personales. No se añaden errores artificiales para simular limpieza.

## Versionamiento y acceso
Repositorio privado: https://github.com/carolynvargasgraniel-pixel/actividad-5-mlflow. La persona que revise el trabajo debe tener acceso autorizado al repositorio.

Los datos pequeños se versionan directamente con Git. El manifest permite comprobar integridad; CHANGELOG documenta decisiones. Los modelos y el almacén MLflow se regeneran con el script para evitar rutas locales y binarios en Git. Los identificadores de commits locales citados en el reporte corresponden al historial de desarrollo previo a la publicación; los commits remotos documentan los archivos publicados.

El cuaderno es autónomo: crea los archivos de trabajo y puede ejecutarse sin clonar el proyecto. Para usar el repositorio privado directamente desde Colab, se requiere autenticación; alternativamente, descargar el cuaderno y abrirlo mediante la opción Subir de Colab.

## Referencias técnicas
- https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html
- https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html
- https://scikit-learn.org/stable/modules/compose.html
- https://mlflow.org/docs/3.5.0/ml/tracking/
- https://mlflow.org/docs/3.5.0/api_reference/python_api/mlflow.sklearn.html
