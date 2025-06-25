

def schema() -> dict:
    return {
        "name": "places_search",
        "description": "Search for places tagged with specified value near a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city or the city and state, e.g. Chicago, IL or Tokyo"
                },
                "tag": {
                    "type": "string",
                    "description": "The tag of the place, e.g. fashion, food, hotel"
                }
            },
            "required": ["location", "query"]
        }
    }

def places_search(query: str, location: str):
    """
    """

