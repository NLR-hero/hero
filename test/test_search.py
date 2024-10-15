import pytest
import hero
import json

def test_keyword_search():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()
    hero_client.authenticate()

    search_index = "hero-data-repo-dev-chemcatbio-app"

    # Example data for NDJSON
    actions = [
        {},  # Metadata line (empty for default index)
        {"query": {"match": {"name": "test"}}}
    ]

    # Generate NDJSON string
    ndjson_query = "\n".join([json.dumps(action) for action in actions]) + "\n"

    search_service = hero_client.Search()
    search_results = search_service.msearch(search_index, ndjson_query)
    assert type(search_results) is dict
    assert search_results["hits"]["total"]["value"] > 0