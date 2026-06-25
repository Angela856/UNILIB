import os
import json
import textwrap
import time
import logging
from datetime import datetime
from google.colab import userdata

# =====================================================================
# CONFIGURACIÓN DE OBSERVABILIDAD Y TRAZABILIDAD (IE1, IE2, IE3)
# =====================================================================
# Configuración del Logger de auditoría para guardar texto de trazabilidad técnico
logging.basicConfig(
    filename='unilib_execution.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def registrar_metricas(user_input, response, latencia, caracteres, estado, herramientas_usadas):
    """Guarda las métricas en un archivo JSON estructurado para el Dashboard de Streamlit"""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_input": user_input,
        "response": response,
        "latency_sec": round(latencia, 2),
        "resource_chars": caracteres,
        "status": estado,
        "tools_executed": tools_executed if tools_executed else ["Ninguna"]
    }
    
    # Escribir en el log de auditoría clásico
    logging.info(f"STATUS: {estado} | LATENCY: {round(latencia, 2)}s | TOOLS: {tools_executed} | INPUT: {user_input[:40]}...")
    
    # Escribir en el JSON acumulativo para analítica visual
    try:
        data = []
        if os.path.exists("metrics_history.json"):
            with open("metrics_history.json", "r", encoding="utf-8") as f:
                try: data = json.load(f)
                except: pass
        data.append(log_entry)
        with open("metrics_history.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Error escribiendo histórico de métricas: {str(e)}")


# 1.) CONFIGURACIÓN DEL ENTORNO (CON VALIDACIÓN INTELIGENTE)

try:
    # Intenta leer el token automáticamente desde los secretos de Colab
    token_github = userdata.get('GITHUB_TOKEN')
except Exception:
    token_github = None

# En caso de no encontrar el token, le saltará un error pidiendo que lo habilite
if not token_github:
    print("No se detectó 'GITHUB_TOKEN' en tus Secretos de Colab.")
    token_github = input("Por favor, pega tu token de GitHub Models aquí para continuar: ").strip()
    if not token_github:
        raise ValueError(" Error, se requiere un token válido para inicializar el modelo GPT-4o.")

os.environ["GITHUB_TOKEN"] = token_github

# Importaciones base estructurales de LangChain
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

# Inicialización del Modelo de Lenguaje (GPT-4o)
llm = ChatOpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
    model="gpt-4o",
    temperature=0.1
)


# 2.) PIPELINE RAG: BUSCADOR EN REGLAMENTO

ruta_pdf = "reglamento_unilib.pdf"

if not os.path.exists(ruta_pdf):
    if os.path.exists("/content/reglamento_unilib.pdf"):
        ruta_pdf = "/content/reglamento_unilib.pdf"
    else:
        raise FileNotFoundError("Error, por favor sube el archivo 'reglamento_unilib.pdf' a la barra lateral de Colab.")

print(f"Archivo detectado con éxito en: {ruta_pdf}")

loader = PyPDFLoader(ruta_pdf)
documentos = loader.load()

chunks = []
for doc in documentos:
    texto = doc.page_content
    for i in range(0, len(texto), 450):
        chunk_texto = texto[i:i+500]
        from langchain_core.documents import Document
        chunks.append(Document(page_content=chunk_texto, metadata=doc.metadata))

print(f"Se generaron {len(chunks)} fragmentos de texto con éxito.")

print("Cargando modelo de embeddings local...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore = Chroma.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
print("Base de datos vectorial Chroma inicializada correctamente.")

@tool
def consultar_reglamento_y_catalogo(query: str) -> str:
    """Útil para responder preguntas sobre normativas de la biblioteca UNILIB, 
    políticas de préstamos, costos de multas y estados administrativos."""
    docs = retriever.invoke(query)
    
    fragmentos_limpios = []
    for doc in docs:
        texto_unificado = " ".join(doc.page_content.split())
        fragmentos_limpios.append(texto_unificado)
        
    return "\n\n".join(fragmentos_limpios)


# 3.) HERRAMIENTAS DE RAZONAMIENTO Y ESCRITURA

@tool
def calcular_multa_atraso(dias_atraso: int) -> str:
    """Útil para calcular el costo financiero de una multa por devolución tardía de libros.
    Recibe los días como entero y aplica las reglas del reglamento."""
    if dias_atraso <= 0:
        return "No registra días de atraso. No aplica multa."
    total = dias_atraso * 1000
    resultado = f"Monto de multa calculado: ${total} CLP por {dias_atraso} días de retraso."
    if total > 10000:
        resultado += " ALERTA: El usuario supera el límite de $10.000 CLP. Cuenta suspendida temporalmente."
    return resultado

@tool
def registrar_reserva_libro(nombre_estudiante: str, titulo_libro: str) -> str:
    """Útil para realizar la reserva automática de un libro en el sistema de UNILIB.
    Escribe el flujo de datos directamente en el registro transaccional."""
    registro_path = "registro_reservas.json"
    nueva_reserva = {"estudiante": nombre_estudiante, "libro": titulo_libro, "estado": "Confirmada"}
    
    datos = []
    if os.path.exists(registro_path):
        with open(registro_path, "r", encoding="utf-8") as f:
            try: datos = json.load(f)
            except: pass
            
    datos.append(nueva_reserva)
    with open(registro_path, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)
        
    return f"Éxito: Reserva del libro '{titulo_libro}' registrada para el estudiante {nombre_estudiante}."

tools_map = {
    "consultar_reglamento_y_catalogo": consultar_reglamento_y_catalogo,
    "calcular_multa_atraso": calcular_multa_atraso,
    "registrar_reserva_libro": registrar_reserva_libro
}
llm_with_tools = llm.bind_tools(list(tools_map.values()))


# 4.) ORQUESTACIÓN / PROMPT DE SISTEMA

prompt_sistema = (
    "Eres el Agente Autónomo de Gestión de la Biblioteca UNILIB.\n"
    "Tu objetivo es resolver solicitudes complejas de estudiantes de forma eficiente.\n"
    "Cuentas con herramientas específicas para consultar el reglamento, calcular multas y reservar libros.\n"
    "Analiza la petición. Si necesitas usar una herramienta, úsala de inmediato.\n"
    "REGLA DE FORMATO CRÍTICA: Responde SIEMPRE en texto plano y corrido. "
    "NO utilices viñetas, listas estructuradas ni Markdown in tu respuesta final."
)


# 5.) BUCLE REACT INTERACTIVO CON MEMORIA OPTIMIZADA Y PROTOCOLOS

print("\n===  AGENTE AUTÓNOMO UNILIB V3 OPERATIVO ===")
print("Escribe tus consultas. Para terminar, escribe 'salir'.")

historial_conversacion = [
    SystemMessage(content=prompt_sistema)
]

while True:
    usuario_input = input("\nEstudiante: ")
    if usuario_input.lower() in ["salir", "exit"]:
        print("Cerrando sesión del Agente UNILIB. ¡Adiós!")
        break
    if not usuario_input.strip():
        continue
        
    # -----------------------------------------------------------------
    # PROTOCOLO DE SEGURIDAD Y FILTRO ÉTICO DE ENTRADA (IE6)
    # -----------------------------------------------------------------
    terminos_maliciosos = ["ignora", "ignore", "override", "hack", "bypass", "instrucción anterior"]
    if any(term in usuario_input.lower() for term in terminos_maliciosos):
        print("\n[Guardrail de Seguridad]: Consulta bloqueada por contener patrones de inyección o vulnerar el uso responsable.")
        logging.warning(f"SECURITY_BLOCK | Intento de inyección de prompt detectado: '{usuario_input}'")
        continue

    # Iniciar conteo de latencia para el turno
    inicio_tiempo = time.time()
    tools_executed = []
    
    historial_conversacion.append(HumanMessage(content=usuario_input))
    
    # -----------------------------------------------------------------
    # SOSTENIBILIDAD: VENTANA DESLIZANTE DE MEMORIA (IE7)
    # -----------------------------------------------------------------
    # Mantenemos el mensaje de sistema inicial fijo, pero limitamos los últimos 6 mensajes 
    # de interacción activa para que la ventana de contexto no crezca infinitamente.
    if len(historial_conversacion) > 7:
        historial_conversacion = [historial_conversacion[0]] + historial_conversacion[-6:]
    
    try:
        print("[Agente Pensando...]")
        respuesta_llm = llm_with_tools.invoke(historial_conversacion)
        
        while respuesta_llm.tool_calls:
            historial_conversacion.append(respuesta_llm)
            
            for tool_call in respuesta_llm.tool_calls:
                nombre_herramienta = tool_call["name"]
                argumentos = tool_call["args"]
                id_llamada = tool_call["id"]
                
                # Registrar herramienta en la trazabilidad interna
                tools_executed.append(nombre_herramienta)
                
                print(f"[Acción]: Ejecutando herramienta '{nombre_herramienta}' con argumentos: {argumentos}")
                
                funcion_herramienta = tools_map[nombre_herramienta]
                resultado_observacion = funcion_herramienta.invoke(argumentos)
                
                observacion_ajustada = textwrap.fill(str(resultado_observacion), width=110)
                print(f"[Observación]:\n{observacion_ajustada}")
                
                historial_conversacion.append(ToolMessage(content=str(resultado_observacion), tool_call_id=id_llamada))
            
            respuesta_llm = llm_with_tools.invoke(historial_conversacion)
            
        historial_conversacion.append(respuesta_llm)
        
        respuesta_final_ajustada = textwrap.fill(respuesta_llm.content.strip(), width=110)
        print(f"\nAgente UNILIB:\n{respuesta_final_ajustada}")
        
        # Guardar métricas de éxito (SUCCESS)
        latencia_final = time.time() - inicio_tiempo
        uso_recursos_chars = len(usuario_input) + len(respuesta_llm.content)
        registrar_metricas(usuario_input, respuesta_llm.content, latencia_final, uso_recursos_chars, "SUCCESS", tools_executed)
        
    except Exception as e:
        # Guardar métricas de error (ERROR) para detectar cuellos de botella
        latencia_final = time.time() - inicio_tiempo
        print(f"\n Error ha ocurrido un inconveniente: {str(e)}")
        registrar_metricas(usuario_input, f"Error: {str(e)}", latencia_final, len(usuario_input), "ERROR", tools_executed)
