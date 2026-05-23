# Probability and Statistics

Repositorio de apoyo para estudio, resolución de ejercicios y simulación de conceptos de probabilidad y estadística. El contenido combina material teórico en Markdown y PDF, una aplicación interactiva en Python para experimentos con dados y scripts auxiliares para diagramas de Venn.

## Contenido del repositorio

- `dice/`: aplicación principal de simulación con interfaz gráfica en Tkinter.
- `scripts/`: scripts independientes para generar diagramas de Venn.
- `chapter-2-exercises/`: espacio para resolver ejercicios del capítulo 2.
- `exercising/`: guía de trabajo y formato para ejercicios pendientes.
- `assets/`: imágenes y recursos visuales usados en material de estudio.
- Archivos `study-*.md` y `study-*.pdf`: resúmenes y material temático.
- `infography-study.html`: recurso HTML estático para consulta visual.
- `.github/workflows/static.yml`: despliegue estático del repositorio completo en GitHub Pages.

## Requisitos

### Python

Se recomienda Python 3.11 o superior. La app de dados usa solo librerías estándar, pero los scripts de Venn requieren dependencias externas.

Dependencias observadas en el repositorio:

- Estándar: `json`, `os`, `random`, `tkinter`, `collections`, `itertools`, `pathlib`, `concurrent.futures`.
- Externas para scripts: `matplotlib`, `matplotlib-venn`, `numpy`.

### Tkinter

En Linux, si Tkinter no está disponible, normalmente se instala con el paquete del sistema. Por ejemplo, en distribuciones basadas en Debian o Ubuntu:

```bash
sudo apt install python3-tk
```

### Entorno virtual sugerido

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install matplotlib matplotlib-venn numpy
```

## Ejecución rápida

### App de dados

```bash
python dice/main.py
```

### Scripts de Venn

```bash
python scripts/venn.py
python scripts/venn_tuplas.py
```

## Aplicación de simulación de dados

La app en `dice/main.py` es el componente más completo del repositorio. Permite trabajar con uno o varios dados, registrar experimentos, explorar el espacio muestral y visualizar resultados.

### Capacidades principales

- Lanzamiento individual con animación.
- Lanzamiento masivo de `N` experimentos.
- Selección de número de dados por experimento.
- Filtro por caras seleccionadas.
- Cálculo de media, moda, frecuencia absoluta y frecuencia relativa.
- Estadísticas globales y por dado.
- Visualización del espacio muestral.
- Histograma del espacio muestral con opción de ordenar por frecuencia.
- Histograma por cara y por dado.
- Gráfica de evolución de resultados filtrados.
- Guardado y carga de sesiones en `dice/sessions/`.

### Flujo de uso básico

1. Elegir la cantidad de dados por experimento.
2. Lanzar una vez o indicar `N` para generar muchos experimentos.
3. Ajustar las caras seleccionadas desde el checklist.
4. Revisar estadísticas, historial y espacio muestral.
5. Abrir histogramas o gráficas según el análisis deseado.
6. Guardar la sesión si se quiere continuar después.

### Persistencia de sesiones

Las sesiones se almacenan como JSON en `dice/sessions/`. Cada sesión guarda:

- muestra reciente del historial;
- selección activa de caras;
- cantidad de dados;
- resúmenes estadísticos por dimensión;
- indicador de si el historial visible fue recortado para ahorrar memoria.

Esto permite reabrir sesiones grandes sin depender de conservar todas las tiradas en RAM.

## Rendimiento y generación masiva

La app fue optimizada para escenarios con muchos experimentos.

### Qué hace la optimización

- Mantiene resúmenes incrementales por cantidad de dados en vez de recalcular desde cero después de cada lote.
- Conserva solo una muestra reciente del historial visible en memoria.
- Usa procesos paralelos para generación masiva cuando el volumen lo justifica.
- Las estadísticas y el histograma del espacio muestral se apoyan en conteos agregados exactos.

### Parámetros importantes

- `MAXIMO_HISTORIAL_MUESTRA = 3000`: límite de muestra visible guardada en memoria.
- `UMBRAL_PARALELISMO = 50000`: a partir de este volumen se habilita el camino paralelo, si hay más de un proceso.

### Campo Procesos paralelos

En la interfaz aparece el campo `Procesos paralelos`.

- Si se escribe `auto`, vacío o `0`, la app usa `os.cpu_count()`.
- Si se escribe un entero positivo, usa exactamente esa cantidad de procesos.
- Si `N` es menor al umbral, la generación sigue por el camino simple para evitar sobrecoste innecesario.

### Consideraciones prácticas

- Más procesos no siempre implican mejor respuesta visual.
- Tkinter sigue dibujando en el proceso principal.
- La generación paralela acelera la producción de resultados, pero la interfaz no delega el renderizado a varios procesos.
- Para análisis enormes, el historial textual visible es solo una muestra, mientras que los resúmenes siguen siendo exactos.

## Visualizaciones disponibles

### Histograma de resultados

Muestra frecuencias por cara y por dado. Es útil para comparar el comportamiento de cada dado cuando se simulan varios a la vez.

### Gráfica de resultados

Representa la evolución temporal de los resultados filtrados. Es más adecuada para inspección visual rápida que para análisis masivo exhaustivo.

### Lista e histograma del espacio muestral

Estas vistas permiten inspeccionar cada evento completo del experimento actual, junto con su frecuencia absoluta y relativa.

## Scripts auxiliares

### `scripts/venn.py`

Genera un diagrama de Venn de tres conjuntos con `matplotlib-venn`. Reemplaza las etiquetas numéricas por los elementos reales de cada región.

Uso principal:

- ejemplos conceptuales con conjuntos pequeños de nombres.

### `scripts/venn_tuplas.py`

Genera un diagrama de Venn personalizado para conjuntos de tuplas usando `matplotlib` y `numpy`, sin depender del renderizado estándar de subconjuntos de `venn3`.

Uso principal:

- ejercicios donde los elementos del espacio muestral son pares ordenados;
- representación visual de intersecciones entre eventos definidos sobre resultados de dados.

## Material de estudio

El repositorio incluye varios archivos de apoyo académico:

- `study-binomial-multinomial.md` y su PDF asociado.
- `study-geometrical-poisson.md` y su PDF asociado.
- `study-hiyergeometrical-negative.binomial.md` y su PDF asociado.
- `notes.md`, `examen-teams-30-01-2026.md` y otros apuntes sueltos.
- `infography-study.html` como recurso visual estático.
- PDF de referencia general de probabilidad y estadística.

Estos archivos no forman una aplicación única; funcionan como material de consulta y trabajo.

## Ejercicios

### `exercising/chapter-2-problem-instructions.md`

Define la convención de trabajo para resolver ejercicios en Markdown con notación LaTeX, incluyendo etiquetas para pendientes y verificaciones.

### `chapter-2-exercises/solving.md`

Actualmente existe como archivo de trabajo para soluciones del capítulo 2. En este momento está vacío.

## Publicación estática

El workflow de GitHub Actions en `.github/workflows/static.yml` publica el repositorio completo como contenido estático en GitHub Pages cuando hay pushes a la rama `master` o cuando se ejecuta manualmente.

Esto es útil para archivos HTML, Markdown renderizado por Pages y materiales de consulta que no requieren backend.

## Estructura resumida

```text
.
├── .github/
├── assets/
├── chapter-2-exercises/
├── dice/
│   ├── main.py
│   └── sessions/
├── exercising/
├── scripts/
├── infography-study.html
├── notes.md
└── study-*.md / study-*.pdf
```

## Posibles mejoras futuras

- agregar un `requirements.txt` o `pyproject.toml`;
- separar el motor estadístico de la interfaz gráfica;
- persistir historiales grandes en SQLite;
- añadir pruebas automáticas para la lógica de simulación;
- documentar cada conjunto de apuntes con índice temático.
