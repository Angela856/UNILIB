# UNILIB
Implementación de Agente (IA) con RAG para un sistema bibliotecario UNILIB

Este proyecto presenta una solución para la modernización de la biblioteca central de la Universidad "UNILIB", abordando problemas de procesos manuales, extravíos de material y búsquedas poco intuitivas mediante el uso de Inteligencia Artificial.

Integrante:
- Angela Anhuaman

# La Solución
Implementamos un **Agente Experto** basado en la arquitectura **RAG (Retrieval-Augmented Generation)**. Este sistema permite a los estudiantes consultar el reglamento institucional y la ubicación de libros en lenguaje natural, garantizando respuestas veraces y reduciendo la carga administrativa en el mesón de atención.

# Tecnologías Utilizadas
*   **Modelo de Lenguaje:** GPT-4o (vía GitHub Models).
*   **Orquestador:** LangChain.
*   **Base de Datos Vectorial:** ChromaDB.
*   **Gestión de Memoria:** (ConversationBufferWindowMemory) para coherencia en el diálogo.
*   **Interfaz:** Streaming de respuestas en tiempo real.

# Estructura del Repositorio
*   `/Código`: Contiene el script principal (main.py) con la lógica del agente.
*   `/data`: Carpeta con el (reglamento_unilib.pdf), base de conocimiento del sistema.
*   `requirements.txt`: Librerías necesarias para el entorno de ejecución.
* 
# Requisitos e Instalación
1. Clonar el repositorio.
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
