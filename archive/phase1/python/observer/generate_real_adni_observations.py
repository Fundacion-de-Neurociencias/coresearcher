"""
Generate REAL ADNI observations from OpenAlex data.
No placeholders - actual evidence from ADNI publications.
"""
import json
import requests
from datetime import datetime

# Fetch real ADNI data from OpenAlex
r = requests.get(
    "https://api.openalex.org/works",
    params={"search": "ADNI Alzheimer", "per_page": 50},
    timeout=15
)
data = r.json()
results = data.get("results", [])

observations = []
observation_id = 1

# Generate real observations from actual publications
for work in results[:20]:
    doi = work.get("doi", "")
    title = work.get("title", "")
    year = work.get("publication_year", "")
    citations = work.get("cited_by_count", 0)
    concepts = [c.get("display_name", "") for c in work.get("concepts", [])[:5]]
    
    # REAL observations extracted from actual paper metadata
    obs = {
        "observation_id": f"obs_{observation_id:03d}",
        "asset": "ADNI",
        "observation_type": "publication",
        "signal": f"ADNI publication: {title[:60]}...",
        "evidence": f"cited_by_count: {citations}, concepts: {','.join(concepts[:3])}",
        "source_url": doi,
        "confidence": "high" if citations > 100 else "medium" if citations > 50 else "low",
        "observed_at": datetime.now().isoformat()
    }
    observations.append(obs)
    observation_id += 1

# Write real observations
with open("data/observatory/adni_observations.json", "w") as f:
    json.dump(observations, f, indent=2)

print(f"Generated {len(observations)} real ADNI observations")
for o in observations[:5]:
    print(f"\n{o['observation_id']}: {o['signal'][:50]}...")
    print(f"  Evidence: {o['evidence']}")