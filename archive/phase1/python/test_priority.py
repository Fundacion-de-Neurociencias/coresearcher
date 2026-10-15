import sys
sys.path.insert(0, '.')
from observer.priority_discovery import query_openalex_works

# Test query
works = query_openalex_works('Alzheimer disease', per_page=5)
print('Found works:', len(works))
for w in works[:5]:
    print(f'  - {w["title"][:60]}...')
    print(f'    Citations: {w["citations"]}, Year: {w["year"]}')