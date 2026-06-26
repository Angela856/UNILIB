# UNILIB: Agente Autónomo de Gestión de Biblioteca con RAG y Observabilidad

Este proyecto implementa un Agente Inteligente Autónomo basado en la arquitectura **ReAct (Reasoning and Action)** para automatizar la atención y gestión de la biblioteca institucional de **UNILIB**. El sistema integra un pipeline **RAG (Retrieval-Augmented Generation)** utilizando almacenamiento vectorial para resolver consultas normativas basándose estrictamente en el reglamento interno, además de incorporar un stack completo de auditoría y observabilidad en tiempo real.

**Integrante:** Angela Anhuaman Solon

---

## Arquitectura del Sistema
El agente opera en un bucle reactivo continuo que evalúa las intenciones del estudiante y decide de manera autónoma qué herramienta invocar para resolver solicitudes complejas:

1. **`consultar_reglamento_y_catalogo`**: Pipeline RAG optimizado para la búsqueda semántica de normativas dentro del documento PDF del reglamento institucional mediante embeddings locales.
2. **`calcular_multa_atraso`**: Componente lógico determinista que calcula penalizaciones financieras ($1.000 CLP por día de atraso) y gestiona estados de suspensión automáticos al superar el límite de $10.000 CLP.
3. **`registrar_reserva_libro`**: Módulo transaccional que valida la disponibilidad del material y escribe las confirmaciones de reserva en la persistencia del sistema.

---

## Stack de Observabilidad y Trazabilidad
Para garantizar el monitoreo del sistema en entornos de producción, el proyecto incluye un panel analítico desarrollado en **Streamlit** que consume un histórico de eventos estructurado en JSON (`metrics_history.json`). Este panel evalúa:

- **Métricas de Rendimiento:** Latencia por consulta (segundos) e identificación de cuellos de botella en el pipeline RAG.
- **Métricas de Negocio y Consistencia:** Tasa de éxito operacional de las transacciones (KPI de estabilidad del agente).
- **Métricas de Infraestructura:** Consumo acumulado de recursos (volumen de caracteres procesados como métrica proxy de tokens).
- **Auditoría del Agente:** Desglose del uso de módulos lógicos frente a respuestas conversacionales puras.

---

## Tecnologías y Librerías (`requirements.txt`)
El proyecto está construido sobre un stack moderno e inmune a conflictos de versiones:
- **Orquestación de Agentes:** `langchain==0.1.0` y `langchain-community`
- **Modelo de Lenguaje (LLM):** `langchain-openai` (conectado a GPT-4o vía GitHub Models API)
- **Embeddings locales:** `langchain-huggingface` y `sentence-transformers`
- **Base de Datos Vectorial:** `chromadb`
- **Procesamiento de Documentos:** `pypdf`
- **Interfaz y Analítica Visual:** `streamlit`, `pandas` y `plotly`

---

## Estructura del Repositorio
El repositorio mantiene una distribución limpia en su raíz para facilitar el despliegue automático:

```text
├── data/                  # Directorio de persistencia de datos vectoriales
├── README.md              # Documentación técnica del proyecto
├── .gitignore             # Exclusiones de Git (caché, entornos virtuales y logs locales)
├── main.py                # Código fuente principal del Agente UNILIB V3
├── dashboard.py           # Panel de control analítico y auditoría en Streamlit
├── requirements.txt       # Dependencias estrictas del proyecto
└── metrics_history.json   # Historial estructurado de logs y métricas de ejecución

