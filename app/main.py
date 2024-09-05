from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client import models as qmodels
from qdrant_client.http.models import PointStruct, SearchRequest, Filter
import config_module.config as config
import openai
import json, os

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
    limit: int = 10

@app.post("/search")
async def search(query: SearchQuery):
    try:
        query_vector = get_embedding(query.query)

        response = qdrant_client.query_points(
            collection_name=config.QDRANT_COLLECTION_NAME,
            query=query_vector,
            limit=query.limit 
        )

        # Check the response and extract results
        if response:
            results = [
                {"id": result.id, "score": result.score, "payload": result.payload}
                for result in response.points
            ]
            return {"results": results}
        else:
            raise ValueError(f"Failed to query points")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/init")
async def search(query: SearchQuery):
    process_json("data/descriptor.json")
    restore_db()
    return {"message": "initiated"}


def get_embedding(text, model=config.OPENAI_MODEL):
    from langchain_openai import OpenAIEmbeddings

    response = OpenAIEmbeddings(model=model)
    embeeding = response.embed_query(text)
    return embeeding


def restore_db():
    if os.path.exists("data/descriptor.jsonb"):
        # Load the JSON file with embeddings
        with open("data/descriptor.jsonb", "r", encoding="utf-8") as f:
            data = json.load(f)

        # Insert vectors (embeddings) from the JSON file
        points = []
        for idx, entry in enumerate(data["institutionalParagraphs"]):
            points.append(
                qmodels.PointStruct(
                    id=idx,
                    payload={
                        "video": entry["video"],
                        "topic": entry["topic"]
                    },
                    vector=entry["content_embedding"],
                ),
            )
        if not qdrant_client.collection_exists(config.QDRANT_COLLECTION_NAME):
            qdrant_client.create_collection(
                collection_name=config.QDRANT_COLLECTION_NAME,
                vectors_config=qmodels.VectorParams(
                    size=1536, distance=qmodels.Distance.COSINE
                ),
            )
        qdrant_client.upsert(
            collection_name=config.QDRANT_COLLECTION_NAME, points=points
        )


def process_json(file_path):
    if os.path.exists("data/descriptor.jsonb"):
        return

    with open(file_path, "r", encoding="utf-8") as f:
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
        with open("data/descriptor.jsonb", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    return data


if __name__ == "__main__":
    import uvicorn
    process_json("data/descriptor.json")
    restore_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
