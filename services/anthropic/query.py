import os

import anthropic
import anthropic.types.message

MAX_TOKENS_DEFAULT = 1024
MODEL_DEFAULT = "claude-sonnet-4-20250514"

def query_doc(file_id: str, query: str) -> anthropic.types.message.Message:
    """
    Query model with a referenced document.

    The referenced document is file_id of a document that has already been uploaded to anthropic file storage.

    docs: https://docs.anthropic.com/en/docs/build-with-claude/files
    """
    client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        default_headers={
            "anthropic-beta": "files-api-2025-04-14",  # required header for file api
        }
    )

    response = client.messages.create(
        model=MODEL_DEFAULT,
        max_tokens=MAX_TOKENS_DEFAULT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Answer the following question using the referenced document: {query}"
                    },
                    {
                        "type": "document",
                        "source": {
                            "type": "file",
                            "file_id": file_id,
                        }
                    }
                ]
            }
        ]
    )

    return response


def query_tools(query: str, tools: list[dict]) -> anthropic.types.message.Message:
    """
    Query model with a set of tools that can be used.

    docs: https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview
    """
    client = anthropic.Anthropic(
        api_key=os.environ["ANTHROPIC_API_KEY"],
        default_headers={},
    )

    response = client.messages.create(
        model=MODEL_DEFAULT,
        max_tokens=MAX_TOKENS_DEFAULT,
        messages=[
            {
                "content": query,
                "role": "user",
            }
        ],
        tools=tools,
    )

    print("response", response) #

    return response
