# Fase II Asistente para aclaraciones de pagos

Prototipo académico que continúa el business case de Fase I. Clasifica textos simulados en no_acreditado, duplicado o devolucion; recupera una regla académica y prepara un borrador fijo para revisión humana. No consulta sistemas bancarios ni ejecuta pagos. El clasificador es Naive Bayes multinomial entrenado con 36 textos sintéticos. No es un modelo generativo: esta fase implementa el componente de clasificación y la integración; no implementa extracción de PDF ni consulta transaccional de la solución completa planteada en Fase I.

## Arquitectura e integración
Navegador (app/index.html) → POST /predict → clasificador (model/modelo.json) → regla asociada → JSON → navegador. La interfaz y la API usan el mismo origen y puerto; no requieren CORS. GET /health verifica disponibilidad y versión del modelo. No hay dependencias de pip ni claves de servicios.

## Ejecución con Python
Python 3.12 o posterior. Desde la raíz del proyecto:
```
python -m app.api
```
Abrir http://localhost:8000. Para repetir entrenamiento: `python entrenar.py`. Para validar sin Docker: `python tests/validar.py`. Esta prueba inicia y detiene su propia API en el puerto 8765.

## Contenedor Docker
Con Docker Engine o Docker Desktop activo:
```
docker build -t aclaraciones-ia:fase2 .
docker run --rm --name aclaraciones-fase2 -p 127.0.0.1:8000:8000 aclaraciones-ia:fase2
```
Abrir http://localhost:8000. Alternativa: `docker compose up --build`.
En una segunda terminal:
```
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"texto":"La transferencia no aparece en destino"}'
```
En PowerShell, usar `curl.exe`. Para ejecutar construcción y pruebas automatizadas en Bash: `bash validar_docker.sh`. Genera evidencias/docker.log y evidencias/resultados.json. El script requiere Docker, curl y Python 3.12. La imagen usa Python 3.12-slim, un usuario sin privilegios y un healthcheck. PORT es configurable (predeterminado 8000); si se cambia, actualizar también el healthcheck y los puertos publicados.

## Contrato de API
POST /predict acepta exclusivamente `{"texto":"descripción"}` con application/json y texto de 5 a 2000 caracteres sin espacios extremos. Devuelve categoria, confianza, requiere_revision, evidencia, borrador y modelo. La confianza es una puntuación posterior de Naive Bayes, no una probabilidad calibrada de acierto. Se abstiene por debajo de 0.65 o con menos de dos palabras distintas reconocidas. Evidencia significa regla académica asociada; no prueba que un pago exista ni que se haya acreditado.

Errores: 400 JSON inválido o cuerpo vacío; 413 más de 16384 bytes; 415 tipo de contenido incorrecto; 422 estructura o texto inválido; 404 ruta inexistente. Siempre se exige revisión humana. Las reglas R01, R02 y R03 son simuladas y están en app/api.py.

## Pruebas y datos
`data/train.csv`: 36 textos de entrenamiento. `data/test.csv`: 18 textos reservados (6 por clase), redactados por separado y sin duplicados exactos. Son ejemplos sintéticos, no expedientes reales ni evidencia de generalización. `evidencias/resultados.json` contiene las entradas, predicciones, matriz de confusión y pruebas HTTP efectivamente ejecutadas en Python. Métricas iniciales: accuracy 16/18, macro F1 0.9333 y 2 abstenciones. Las pruebas funcionales validan el contrato; las métricas se reportan por separado y no se convierten en aciertos artificiales.

La imagen se construyó y ejecutó correctamente en GitHub Actions, en el host Ubuntu 24.04.5 del runner con Docker 28.0.4. Las 35 pruebas contra localhost:8000 pasaron. Ejecución: https://github.com/carolynvargasgraniel-pixel/actividad-5-mlflow/actions/runs/41365176978 . Commit probado: 3daec6251d066f309453288e0d44117dcd6fddfa. Registro: evidencias/docker_github.log; identificación: evidencias/ejecucion.json. Esto comprueba ejecución local en el runner; no equivale a ejecución en el equipo personal ni a despliegue en Azure. El código de aplicación y el Dockerfile de la entrega coinciden con ese commit.

## Despliegue en nube
Consultar el manual Word y el documento de validación entregados por separado y en el ZIP de la actividad. Estrategia: contenedor en Azure Container Apps, puerto 8000 e interfaz y API en una misma aplicación. Solo para demostración con textos sintéticos. No se efectuó despliegue a una cuenta de Azure.

## Uso de asistencia de IA para documentación
Utilicé ChatGPT para estructurar el manual, describir el contrato de API y proponer casos extremos. Consulta empleada: «Redacta un manual replicable para desplegar este prototipo Python en Docker y Azure Container Apps; distingue pasos propuestos de pruebas ejecutadas». La documentación se contrastó con el código y los resultados de pruebas. No atribuyo este trabajo a Copilot.
