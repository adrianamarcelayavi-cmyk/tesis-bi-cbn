# Fase 1. Diagnóstico inicial de los datos

## 1. Objetivo

Evaluar la calidad, integridad y disponibilidad de los registros históricos de productos vencidos y pinchados en siete sucursales, identificando inconsistencias que deben resolverse antes de la limpieza, integración y aplicación de modelos de aprendizaje automático.

## 2. Datos utilizados

El diagnóstico se realizó sobre una base histórica de 501 registros y 12 columnas originales. Para el análisis se conservaron 9 variables relevantes.

También se dispone de un catálogo maestro de 70 registros, que será utilizado para la posterior estandarización de productos.

Los archivos publicados son versiones seudonimizadas de las bases de trabajo.

## 3. Análisis realizados

- Cambio al tipo de variable correspondiente
- Estadísticas descriptivas de los registros históricos
- Evaluación de la completitud de variables obligatorias.
- Cumplimiento de condiciones según el motivo del registro.
- Cobertura semanal de registros por sucursal.
- Identificación de posibles registros duplicados.
- Identificación y cuantificación de valores faltantes.

## 4. Resultados principales

| Indicador | Resultado |
|---|---|
| Registros históricos | 501 |
| Sucursales identificadas | 7 |
| Nombres estándar diferentes | 56 |
| Registros incompletos | 39 (7,78 %) |
| Registros que incumplen condiciones según motivo | 18 (3,59 %) |
| Duplicados exactos adicionales | 18 (3,59 %) |
| Cobertura semanal promedio de registros | 38,89 % |

## 5. Reproducibilidad

El cuaderno `01_diagnostico.ipynb` permite ejecutar el diagnóstico desde Google Colab.

Los datos se descargan automáticamente desde la rama `main` del repositorio, utilizando los archivos ubicados en `data/sample/`:

- `datos_diagnostico_pseudonimizados.csv`
- `catalogo_pseudonimizado.csv`

**Instrucciones:**

1. Abrir el archivo `01_diagnostico.ipynb` desde GitHub en Google Colab.
2. Seleccionar `Entorno de ejecución`.
3. Seleccionar `Reiniciar sesión y ejecutar todas las celdas`.
4. Esperar a que se generen las tablas, indicadores y gráficos.

No se requiere acceso al Google Drive del autor ni cargar manualmente los archivos CSV.

## 6. Consideraciones metodológicas

La Fase 1 se desarrolló conservando los registros iniciales, incluidos los valores faltantes y los posibles duplicados, para evitar alterar los resultados del diagnóstico.

Los datos publicados han sido seudonimizados. Esta medida sustituye identificadores comerciales, pero no garantiza por sí sola anonimato completo.


## 7. Continuidad del proyecto

Los resultados de esta fase servirán como referencia para:

- Fase 2: Limpieza, validación y estandarización de datos.
- Fase 3: Integración de registros históricos y nuevos con productos próximos a vencer.
- Fase 4: Análisis exploratorio y desarrollo de modelos K-Means y DBSCAN.
- Fase 5: Interpretación de resultados y formulación de recomendaciones
La base del diagnóstico se conservará como referencia de la situación inicial, sin reemplazarla por los datos posteriormente depurados.
