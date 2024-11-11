import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import Client, create_client

load_dotenv()

open_api_key = os.getenv('OPEN_API_KEY')
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

embeddings = OpenAIEmbeddings(api_key=open_api_key)
supabase: Client = create_client(supabase_url, supabase_key)


def get_embeddings(text: str):
    return embeddings.aembed_documents([text])[0]

def search_similar(query_embedding):
    vector_store = SupabaseVectorStore(
        embedding=embeddings,
        client=supabase,
        table_name="documents",
        query_name="match_documents"
    )
    matched_data = vector_store.similarity_search(query_embedding)
    return [{"content": matched_doc.page_content} for matched_doc in matched_data]
