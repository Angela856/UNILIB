import os
import time
from google.colab import userdata 
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory

# 1. CONFIGURACIÓN DE SEGURIDAD Y MODELO
os.environ["GITHUB_TOKEN"] = userdata.get('GITHUB_TOKEN') 

llm = ChatOpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
    model="gpt-4o",
    temperature=0.1, # Conservador para evitar alucinaciones en reglamentos
    streaming=True
)

# 2. PIPELINE RAG (Lectura del PDF en la carpeta data)
def preparar_asistente():
    ruta_pdf = "data/reglamento_unilib.pdf" 
    
    loader = PyPDFLoader(ruta_pdf)
    documentos = loader.load()
    
    # Dividimos el texto para no exceder los tokens 
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documentos)
    
    # Creamos la base de datos vectorial
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=OpenAIEmbeddings()
    )
    
    # 3. CONFIGURACIÓN DE MEMORIA 
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        output_key="answer",
        return_messages=True,
        k=5 # Recuerda las últimas 5 preguntas
    )
    
    # Creamos la cadena de conversación con RAG
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

# 4. EJECUCIÓN CON STREAMING (Notebook 3)
agente = preparar_asistente()

print("--- ASISTENTE UNILIB ACTIVO ---")
while True:
    pregunta = input("\nUsuario: ")
    if pregunta.lower() in ["salir", "exit"]: break
    
    print("Agente: ", end="", flush=True)
    # El método stream permite ver la respuesta palabra por palabra
    for chunk in agente.stream({"question": pregunta}):
        if 'answer' in chunk:
            print(chunk['answer'], end="", flush=True)
