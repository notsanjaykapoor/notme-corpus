

def schema() -> dict:
    return {
        "name": "places_explore",
        "description": "Search for places near a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city or the city and state or city and country, e.g. Chicago, IL or Tokyo"
                },
                "query": {
                    "type": "string",
                    "description": "The name or the category of the place, e.g. restaurant, pizza hut"
                }
            },
            "required": ["location", "query"]
        }
    }

def places_explore(query: str, location: str):
    """
    """

