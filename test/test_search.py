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

    search_service = hero_client.Search()
    search_results = search_service.msearch(search_index, actions)
    assert type(search_results) is dict
    assert search_results["responses"][0]["hits"]["total"]["value"] > 0

def test_list_resources():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()
    hero_client.authenticate()

    search_index = "hero-data-repo-dev-chemcatbio-app"

    # Example data for NDJSON
    actions = [
        {},  # Metadata line (empty for default index)
        {"query": {"match_all": {}}, "size": 10}
    ]

    search_service = hero_client.Search()
    search_results = search_service.msearch(search_index, actions)
    assert type(search_results) is dict
    assert search_results["responses"][0]["hits"]["total"]["value"] > 0

def test_list_resources_by_type():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()
    hero_client.authenticate()

    search_index = "hero-data-repo-dev-chemcatbio-app"

    # Example data for NDJSON
    actions = [
        {},  # Metadata line (empty for default index)
         {"query": {"match": {"metatype": "Project"}}}
    ]

    search_service = hero_client.Search()
    search_results = search_service.msearch(search_index, actions)
    assert type(search_results) is dict
    assert search_results["responses"][0]["hits"]["total"]["value"] > 0

def test_list_resources_by_metadata():
    hero_client = hero.HeroClient()
    auth = hero_client.Auth()
    hero_client.authenticate()

    search_index = "hero-data-repo-dev-chemcatbio-app"

    # Example data for NDJSON
    actions = [
        {},  # Metadata line (empty for default index)
        {"query": {"match": {"metadata.format": "CSV"}}}
    ]

    search_service = hero_client.Search()
    search_results = search_service.msearch(search_index, actions)
    assert type(search_results) is dict
    assert search_results["responses"][0]["hits"]["total"]["value"] > 0
