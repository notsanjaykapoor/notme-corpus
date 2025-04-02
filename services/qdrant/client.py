import qdrant_client

import services.qdrant

def client():
    return qdrant_client.QdrantClient(url=services.qdrant.qdrant_root_url())