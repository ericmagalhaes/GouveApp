from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, SearchRequest, Filter
import config_module.config as config
import openai

app = FastAPI()

# Initialize Qdrant client with settings from config.py
qdrant_client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)

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
 
 
@app.post("/add-entry")
async def add_entry(entry: AddEntryRequest):
    try:
        # Generate the vector using OpenAI's text embedding model
        response = openai.Embedding.create(
            input=entry.text,
            model=config.OPENAI_MODEL
        )
 
        vector = response['data'][0]['embedding']
 
        point = PointStruct(
            id=entry.id,
            vector=vector,
            payload={"text": entry.text}
        )
 
        qdrant_client.upsert(
            collection_name=config.QDRANT_COLLECTION_NAME,
            points=[point]
        )
 
        return {"message": "Entry added successfully"}
 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@app.post("/remove-entry")
async def remove_entry(entry: RemoveEntryRequest):
    try:
        qdrant_client.delete(
            collection_name=config.QDRANT_COLLECTION_NAME,
            points_selector={"ids": [entry.id]}
        )
 
        return {"message": "Entry removed successfully"}
 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)