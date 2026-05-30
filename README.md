# UNILIB: Agente Autónomo de Gestión de Biblioteca con RAG 

Este proyecto implementa un Agente Inteligente Autónomo basado en la arquitectura **ReAct (Reasoning and Action)** para automatizar la atención y gestión de la biblioteca institucional de **UNILIB**. El sistema integra un pipeline **RAG (Retrieval-Augmented Generation)** utilizando almacenamiento vectorial para resolver consultas normativas basándose estrictamente en el reglamento interno.

#Integrante: Angela Anhuaman Solon

##  Arquitectura del Sistema
El agente opera en un bucle reactivo continuo que evalúa las intenciones del estudiante y decide de manera autónoma qué herramienta invocar para resolver solicitudes complejas:

1. **`consultar_reglamento_y_catalogo`**: Pipeline RAG optimizado para la búsqueda semántica de normativas dentro del documento PDF del reglamento.
2. **`calcular_multa_atraso`**: Componente lógico que determina penalizaciones financieras ($1.000 CLP por día) y gestiona estados de suspensión automáticos al superar el límite de $10.000 CLP.
3. **`registrar_reserva_libro`**: Módulo transaccional que escribe los flujos de datos y confirmaciones de reserva en la persistencia del sistema.

---

##  Tecnologías y Librerías (`requirements.txt`)
El proyecto está construido sobre un stack moderno e inmune a conflictos de versiones comunes:
- **Orquestación:** `langchain==0.1.0` y `langchain-community`
- **Modelo de Lenguaje (LLM):** `langchain-openai` (conectado a GPT-4o vía GitHub Models API)
- **Embeddings locales:** `langchain-huggingface` y `sentence-transformers`
- **Base de Datos Vectorial:** `chromadb`
- **Procesamiento de Documentos:** `pypdf`

---

##  Instrucciones de Ejecución

### Opción 1: Ejecución Rápida en Google Colab 
Para probar el agente de forma inmediata en la nube sin configurar un entorno local:

1. Haga clic en el botón **Open In Colab** en la parte superior de este repositorio.
2. En la barra lateral izquierda de Colab, haga clic en el icono de la llave (**Secretos** 🔑).
3. Añada una nueva variable con el nombre `GITHUB_TOKEN` y pegue su credencial personal de GitHub Models. Active el interruptor de **"Acceso al cuaderno"** (Notebook access).
4. Asegúrese de subir el archivo `reglamento_unilib.pdf` a la sección de archivos de Colab (o deje que el script lo descargue si configuró la automatización).
5. Ejecute la celda principal. Si no configuró el paso de la llave, el código le solicitará el token amigablemente mediante una casilla de texto interactiva.

