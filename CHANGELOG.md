# Historial de cambios

## 1.0.0 · 2026-10-18
- Obtención de WDBC mediante scikit-learn, conservación de copia inicial y recodificación explícita del objetivo: maligno=1.
- Validación de tipos numéricos, etiqueta binaria, no negatividad y eliminación de duplicados exactos; auditoría de nulos. Sin exclusión automática de extremos.
- Partición estratificada y conservación de índices; transformaciones aprendidas dentro del pipeline, sin usar el test para ajustar.
- Grid Search de dos familias con cinco folds y criterio F1 predefinido.
- Registro de parámetros, métricas, modelos, firma y artefactos en MLflow; SHA-256 para datos y código.
- Evaluación en holdout, bootstrap pareado de diferencia de F1 y prueba exacta de McNemar.
- Reporte técnico con limitaciones y plan de MLOps.

## 1.0.1 · 2026-10-18
- Incorporación de introducción y revisión de la redacción académica en primera persona.
- Actualización del reporte técnico editable en Word y de su versión PDF, manteniendo métricas y evidencias de la ejecución 1.0.0.

## 1.0.2 · 2026-10-18
- Publicación del proyecto en el repositorio privado actividad-5-mlflow.
- Actualización del README con rutas de entregables y comandos de clonación.
- Incorporación del enlace del repositorio en el reporte técnico.
