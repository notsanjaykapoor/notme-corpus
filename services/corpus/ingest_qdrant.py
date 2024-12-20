import os

import llama_index.embeddings
import more_itertools
import qdrant_client
import qdrant_client.models

import log
import models
import services.images
import services.qdrant

DOC_BATCH_SIZE_DEFAULT = 512
DOC_CLIP_MAX_SIZE = 77

logger = log.init("app")


def ingest_qdrant_multi(
    corpus: models.Corpus,
    nodes: list[models.NodeImage],
    embed_model: llama_index.embeddings,
) -> str:
    """
    Ingest multi modal images into qdrant.

    Each image node contains an image and some text.  Each node is stored as a single qdrant point with 2 vectors,
    1 for the image and 1 for text.
    """
    client = services.qdrant.client()
    collection_name = f"{corpus.name}_multi"

    client.delete_collection(collection_name)

    # generate image and text embeddings, create qdrant points, and upsert into qdrant collection

    chunked_i = 0
    vector_size = 0

    logger.info(
        f"corpus {corpus.id} ingest '{corpus.name}' epoch {corpus.epoch} clip model embed"
    )

    for chunked_nodes in more_itertools.chunked(nodes, DOC_BATCH_SIZE_DEFAULT):
        # truncate text to 77 characters for clip
        img_list = [
            services.images.download(
                uri=node.uri, dir=os.environ.get("APP_DOWNLOAD_PATH")
            )
            for node in chunked_nodes
        ]
        txt_list = [node.text_indexable[0:DOC_CLIP_MAX_SIZE] for node in chunked_nodes]

        img_embeddings = embed_model.get_image_embedding_batch(
            img_list,
            show_progress=True,
        )

        txt_embeddings = embed_model.get_text_embedding_batch(
            txt_list,
            show_progress=True,
        )

        qdrant_points: list[qdrant_client.models.PointStruct] = []

        for node, img_vector, txt_vector in zip(
            chunked_nodes, img_embeddings, txt_embeddings
        ):
            vector_size = len(img_vector)

            point = qdrant_client.models.PointStruct(
                id=node.id,
                payload=node.meta,
                vector={
                    "img": img_vector,
                    "txt": txt_vector,
                },
            )
            qdrant_points.append(point)

        if chunked_i == 0:
            # create collection, wait until first iteration to get embedding vector lengths
            client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "img": qdrant_client.models.VectorParams(
                        size=vector_size,
                        distance=qdrant_client.models.Distance.COSINE,
                    ),
                    "txt": qdrant_client.models.VectorParams(
                        size=vector_size,
                        distance=qdrant_client.models.Distance.COSINE,
                    ),
                },
            )

        # update collection

        client.upsert(
            collection_name=collection_name,
            points=qdrant_points,
        )

        chunked_i += 1

    return collection_name


def ingest_qdrant_text(
    corpus: models.Corpus,
    nodes: list[models.NodeText],
    embed_model: llama_index.embeddings,
) -> str:
    """
    Ingest text nodes into qdrant.
    """
    client = services.qdrant.client()
    collection_name = f"{corpus.name}_txt"

    client.delete_collection(collection_name)

    # generate text embeddings, create qdrant points, and upsert into qdrant collection

    chunked_i = 0

    for chunked_nodes in more_itertools.chunked(nodes, DOC_BATCH_SIZE_DEFAULT):
        nodes_list = [node for node in chunked_nodes]
        txt_list = [node.text_indexable for node in chunked_nodes]

        txt_embeddings = embed_model.get_text_embedding_batch(
            txt_list, show_progress=True
        )

        qdrant_points: list[qdrant_client.models.PointStruct] = []
        vector_size = 0

        for node, vector in zip(nodes_list, txt_embeddings):
            vector_size = len(vector)

            point = qdrant_client.models.PointStruct(
                id=node.id,
                payload=node.meta,
                vector={"txt": vector},
            )

            qdrant_points.append(point)

        if chunked_i == 0:
            # create collection
            client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "txt": qdrant_client.models.VectorParams(
                        size=vector_size,
                        distance=qdrant_client.models.Distance.COSINE,
                    ),
                },
            )

        # update collection

        client.upsert(
            collection_name=collection_name,
            points=qdrant_points,
        )

        chunked_i += 1

    return collection_name
