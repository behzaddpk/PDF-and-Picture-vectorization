import logging
import pytesseract
from PIL import Image
import PyPDF2
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from langchain_community.document_loaders.image import UnstructuredImageLoader
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.schema import Document
from supabase.client import Client, create_client
import os
from dotenv import load_dotenv
import uuid

# Load environment variables from .env file
load_dotenv()
open_api_key = os.getenv('OPEN_API_KEY')
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

# Initialize OpenAI embeddings and Supabase client
embeddings = OpenAIEmbeddings(api_key=open_api_key)
supabase: Client = create_client(supabase_url, supabase_key)

def load_document(path: str, extension: str, metadata: dict):
    if extension in ['.png', '.jpg', '.jpeg']:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path based on your installation
        text = pytesseract.image_to_string(Image.open(path))
        documents = [Document(page_content=text, metadata=metadata)]
    elif extension == '.pdf':
        text = ''
        with open(path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
        documents = [Document(page_content=text, metadata=metadata)]
    else:
        raise ValueError("Unsupported file format")

    return documents

def vectorize_to_supabase(documents, file_path):
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=1536,
        chunk_overlap=0,
        length_function=len,
        is_separator_regex=False,
    )
    
    logging.info(f"Original documents: {documents}")  
    # Split the text in the document
    files = text_splitter.split_documents(documents)
    logging.info(f"files documents: {files}")  

    try:
        SupabaseVectorStore.from_documents(
            files,
            embedding=embeddings,
            client=supabase,
            table_name='documents',
            query_name='match_documents',
            chunk_size=500
        )
    except Exception as e:
        logging.error(f"Error during inserting into Supabase: {e}")
        raise ValueError("Error during inserting into Supabase")

def delete_vectors_of(specific_source: str):
    supabase.table("documents").delete().eq("metadata->>source", specific_source).execute()


def search_similar(query: str):
    vector_store = SupabaseVectorStore(
        embedding=embeddings,
        client=supabase,
        table_name="documents",
        query_name="match_documents",
    )
    matched_docs = vector_store.similarity_search(query)
    
    return "\n".join([matched_doc.page_content for matched_doc in matched_docs])