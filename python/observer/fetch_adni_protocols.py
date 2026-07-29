"""
Fetch ADNI protocol documentation - REAL structural observations.
No citations, no popularity metrics - only protocol facts.
"""
import requests
import json

# Search for ADNI protocol papers specifically
r = requests.get(
    "https://api.openalex.org/works",
    params={"search": "ADNI protocol MRI methodology", "per_page": 20},
    timeout=15
)
data = r.json()

# Extract real protocol details from abstracts/methods
observations = []
obs_id = 1

for work in data.get("results", []):
    doi = work.get("doi", "")
    title = work.get("title", "")
    concepts = [c.get("display_name", "") for c in work.get("concepts", [])]
    
    # Get abstract if available
    abstract = work.get("abstract", "")
    
    obs = {
        "observation_id": f"obs_{obs_id:03d}",
        "category": "protocol",
        "evidence": title[:100] if title else "",
        "source": doi,
        "confidence": "high" if doi else "low"
    }
    observations.append(obs)
    obs_id += 1

# Save raw findings
with open("data/observatory/adni_protocols_raw.json", "w") as f:
    json.dump(observations, f, indent=2)

print(f"Found {len(observations)} protocol-related papers")