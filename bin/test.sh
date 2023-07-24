export HERO_PROJECT="test-project-2"
export HERO_QUEUE="test-queue"
export HERO_CLIENT_ID="70pj7rpoukmgnhl442jcmugl6i"
export HERO_CLIENT_SECRET="thae66jbq4e01nm96btcpahv0f2d45s079q4m0ufv9f1ft2sfli"
export HERO_QUEUE_VISIBILITY_TIMEOUT="60"
# pytest tests/test_queue.py
# pytest tests/test_dynamo.py
# pytest tests/test_config.py
pytest tests/api/test_queue.py
# pytest tests