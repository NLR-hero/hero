pdoc --html hero --force --template-dir ./pdoc/templates --output-dir ./docs

# Creates index.html at the root, and places a redirect inside to the nested index.html
# - for Github Pages to be able to find the entry point
html_content='<meta http-equiv="refresh" content="0; url=./hero/index.html" />'
echo "$html_content" > "./docs/index.html"