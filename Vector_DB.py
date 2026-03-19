import dotenv
import os
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
dotenv.load_dotenv()
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

dotenv.load_dotenv()
# file path 
RESUME_PDF_PATH = "data/WORK.pdf"
CHROMA_PATH = "chroma_data"
JAILBREAK_PDG_PATH = "data/jailbreak.pdf"
INJECTION_PDG_PATH = "data/injection.pdf"
JAIBREAK_CHROMA_PATH = "chroma_jailbreak"
# resume file 
loader = PyPDFLoader(file_path=RESUME_PDF_PATH )

OS = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
documents = text_splitter.split_documents(OS)

# embed to vector form 
resume_vector_db = Chroma.from_documents(
    documents, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
)
# store into vector database 
resume_vector = Chroma(
     persist_directory=CHROMA_PATH,
     embedding_function=OpenAIEmbeddings(),
 )
# jailbreak file
loader_jailbreak = PyPDFLoader(file_path=JAILBREAK_PDG_PATH)
OS_jailbreak = loader_jailbreak.load()
text_splitter_jailbreak = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
documents_jailbreak = text_splitter_jailbreak.split_documents(OS_jailbreak)
# embed to vector form
jailbreak_vector_db = Chroma.from_documents(
    documents_jailbreak, OpenAIEmbeddings(), persist_directory=JAIBREAK_CHROMA_PATH
)
# store into vector database
jailbreak_vector = Chroma(
     persist_directory=JAIBREAK_CHROMA_PATH,
     embedding_function=OpenAIEmbeddings(),
 )  

# injection file
loader_injection = PyPDFLoader(file_path=INJECTION_PDG_PATH)
OS_injection = loader_injection.load()
text_splitter_injection = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
documents_injection = text_splitter_injection.split_documents(OS_injection)
# embed to vector form
injection_vector_db = Chroma.from_documents(
    documents_injection, OpenAIEmbeddings(), persist_directory=JAIBREAK_CHROMA_PATH
)
# store into vector database
injection_vector = Chroma(
     persist_directory=JAIBREAK_CHROMA_PATH,
     embedding_function=OpenAIEmbeddings(),
 )  



