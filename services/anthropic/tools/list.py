import services.anthropic.tools.tool_places_explore
import services.anthropic.tools.tool_places_search

def list() -> list[dict]:
    """
    Get list of claude tools.
    """
    return [
        services.anthropic.tools.tool_places_explore.schema(),
        services.anthropic.tools.tool_places_search.schema(),
    ]
    