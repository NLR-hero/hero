import pytest
import hero

def test_keyword_search():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()
    hero_client.authenticate()

    search_index = "hero-data-repo-dev-chemcatbio-app"

    search_service = hero_client.Search()
    ndjson_query = '{"index": "hero-data-repo-dev-chemcatbio-app"}\n{"query": {"match": {"name": "test"}}}\n'
    search_results = search_service.msearch(search_index, ndjson_query)
    assert type(search_results) is dict
    assert search_results["hits"]["total"] > 0