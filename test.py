import json
from agent.pubmed_tools import search_pubmed

result = search_pubmed("sepsis treatment elderly patients", max_results=3)
print(json.dumps(result, indent=2))
