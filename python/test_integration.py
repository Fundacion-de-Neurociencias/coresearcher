"""Integration test for priority discovery system."""

import sys
sys.path.insert(0, '.')

from observer.priority_discovery import (
    generate_top_100_priority_list,
    discover_from_openalex,
    discover_from_zenodo,
    discover_from_ecosystems,
    priority_score,
)

print("=" * 70)
print("CORESEARCHER PRIORITY DISCOVERY - INTEGRATION TEST")
print("=" * 70)

# Test each discovery function
print("\n1. Testing discover_from_openalex()...")
openalex = discover_from_openalex()
print(f"   Found {len(openalex)} papers from OpenAlex")
if openalex:
    print(f"   Top: {openalex[0]['title'][:40]}... (score: {openalex[0]['score']:.2f})")

print("\n2. Testing discover_from_zenodo()...")
zenodo = discover_from_zenodo()
print(f"   Found {len(zenodo)} records from Zenodo")
if zenodo:
    print(f"   Top: {zenodo[0]['title'][:40]}... (score: {zenodo[0]['score']:.2f})")

print("\n3. Testing discover_from_ecosystems()...")
ecosystems = discover_from_ecosystems()
print(f"   Found {len(ecosystems)} ecosystem repos")
for eco in ecosystems[:3]:
    print(f"   - {eco['name']} ({eco['domain']}) - score: {eco['score']:.2f}")

print("\n4. Testing priority_score()...")
# Test the formula
test_score = priority_score(citations=5000, stars=3000, contributors=50, recent_activity=6)
print(f"   Score for (cit:5000, stars:3000, contrib:50, activity:6) = {test_score:.2f}")

# Expected: 0.4 * 0.5 + 0.3 * 0.3 + 0.2 * 0.5 + 0.1 * 0.5 = 0.2 + 0.09 + 0.1 + 0.05 = 0.44
# Normalized: min(citations/10000, 1.0) = 0.5
# min(stars/10000, 1.0) = 0.3
# min(contributors/100, 1.0) = 0.5
# min(activity/12, 1.0) = 0.5
# Score = 0.4*0.5 + 0.3*0.3 + 0.2*0.5 + 0.1*0.5 = 0.44

print("\n5. Testing generate_top_100_priority_list()...")
ledger = generate_top_100_priority_list()
print(f"   Strategy: {ledger['strategy']}")
print(f"   Total queued: {ledger['total_queued']}")
print(f"   Sources: {list(ledger['by_source'].keys())}")
for src, objs in ledger['by_source'].items():
    print(f"   - {src}: {len(objs)} objects")

print("\n" + "=" * 70)
print("INTEGRATION TEST COMPLETE")
print("=" * 70)