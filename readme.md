### Intro

This repo is a RAG example that includes:

- document/corpus ingestion
- corpus vector and rag queries
- image captions

### Setup

This repo uses [uv](https://docs.astral.sh/uv/) as its package manager:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create a virtual environment using a specific python version:

```
uv venv --python <path/to/python>
```

Install project dependencies:

```
uv sync
```

### Dev Environment

Start the dev environment server:

```
make dev
```

### Corpus Ingest

Ingest a corpus of documents using the command line:

```
./scripts/corpus-utils ingest --help
```

List all available corpora, with links to corpus files and corpus query:

![Corpus List Example](https://ik.imagekit.io/notme001/readme/corpus_list_example.png "corpus list example")


### RAG Example

Ingest documents, tokenize them and store them in a Qdrant database.  Run a query, find matches in Qdrant database, and then use these matches as context in a RAG query to an LLM.  The embed models are LLM's run locally to address security concerns.

![RAG Example](https://ik.imagekit.io/notme001/readme/rag_text_example.png "rag example")


### Image Caption Example

Run an image through a multi modal LLM asking it to describe the image.  The LLM is run locally to address security concerns.

![Image Caption Example](https://ik.imagekit.io/notme001/readme/rag_image_caption_example.png "image caption example")


### Long Context Example

LLM context windows are getting larger and unlocking new use cases and interaction methods.  For example, the recent Gemini models support ![1 million+ context window](https://ai.google.dev/gemini-api/docs/long-context "context window").  RAG queries can be simplified with these longer context windows by submitting a query with one or more documents and getting a single shot response.

The first step here is storing content with Gemini so it can easily referenced, and the second step is submitting a query with a document reference as context and getting the response.

![Step 1](https://ik.imagekit.io/notme001/readme/gemini_buckets_list.png)

![Step 2](https://ik.imagekit.io/notme001/readme/gemini_doc_query.png)