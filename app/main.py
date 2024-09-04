from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, SearchRequest, Filter
import config_module.config as config
import openai
import json,os

app = FastAPI()

# Initialize Qdrant client with settings from config.py
qdrant_client = QdrantClient(location=":memory:")

# Set up OpenAI API key from config.py
openai.api_key = config.OPENAI_API_KEY
 
# Define the request body model for adding an entry
class AddEntryRequest(BaseModel):
    id: int
    text: str
 
# Define the request body model for removing an entry
class RemoveEntryRequest(BaseModel):
    id: int
 
# Define the request body model for search
class SearchQuery(BaseModel):
    query: str
 
@app.post("/search")
async def search(query: SearchQuery):
    try:
        # Perform a hybrid search on Qdrant
        search_request = SearchRequest(
            query_vector=None,  # Hybrid search can use `query_vector` + `filter`
            filter=Filter(
                must=[{"key": "text", "match": {"text": query.query}}]  # Example filter for the text field
            ),
            limit=10  # Number of results to return
        )
 
        search_results = qdrant_client.search(
            collection_name=config.QDRANT_COLLECTION_NAME,
            request=search_request
        )
 
        # Process and return the results
        results = [
            {"id": result.id, "score": result.score, "payload": result.payload}
            for result in search_results
        ]
 
        return {"results": results}
 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
   
def get_embedding(text, model="text-embedding-3-small"):
    from langchain_openai import OpenAIEmbeddings
    response = OpenAIEmbeddings(
      model=model
    )
    embeeding = response.embed_query(text)
    return embeeding

def process_json(file_path):
    if os.path.exists('data/descriptor.jsonb'):
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for entry in data["institutionalParagraphs"]:
        topic = entry["topic"]
        content = entry["content"]
        
        topic_embedding = get_embedding(topic)
        content_embedding = get_embedding(content)
        
        # Optionally, you can store these embeddings in the entry or use them as needed
        entry["topic_embedding"] = topic_embedding
        entry["content_embedding"] = content_embedding
        
        print(f"Processed: {topic}")

    # Optionally save the data with embeddings back to a file
    with open('data/descriptor.jsonb', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
 
    return data

if __name__ == "__main__":
    import uvicorn
    process_json('data/descriptor.json')
    uvicorn.run(app, host="0.0.0.0", port=8000)