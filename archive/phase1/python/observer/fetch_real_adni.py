"""
Fetch real ADNI observations from OpenAlex.
No placeholders - real data only.
"""
import json
from observer.openalex_connector import search_and_map

artifacts = search_and_map("ADNI Alzheimer", per_page=20)

print(f"Found {len(artifacts)} papers")

for a in artifacts[:10]:
    print(f"\nDOI: {a.doi}")
    print(f"Title: {a.title[:100]}...")
    print(f"Citations: {a.citations}")