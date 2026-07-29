import json
import sys
import yaml
from pathlib import Path
from collections import defaultdict, deque

def load_rules(yaml_path):
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f).get('rules', [])

def has_cycle(nodes, edges):
    # Detectar ciclos en grafo dirigido
    adj = defaultdict(list)
    for e in edges:
        adj[e['from']].append(e['to'])
        
    visited = set()
    rec_stack = set()
    
    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in adj[node]:
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
                
        rec_stack.remove(node)
        return False
        
    for n in nodes:
        node_id = n['id']
        if node_id not in visited:
            if dfs(node_id):
                return True
    return False

def max_path_length_from_claims(nodes, edges):
    # Calcula la profundidad maxima desde un Claim a un Source
    adj = defaultdict(list)
    for e in edges:
        adj[e['from']].append(e)
        
    claim_ids = [n['id'] for n in nodes if n.get('type', '').lower() == 'claim']
    
    max_hops = 0
    
    def get_max_depth(node_id, current_depth, visited_path):
        nonlocal max_hops
        if node_id in visited_path:
            return # Avoid infinite recursion on cycles
            
        visited_path.add(node_id)
        
        neighbors = adj[node_id]
        if not neighbors:
            if current_depth > max_hops:
                max_hops = current_depth
        else:
            for e in neighbors:
                get_max_depth(e['to'], current_depth + e.get('hops', 1), visited_path)
                
        visited_path.remove(node_id)
            
    for cid in claim_ids:
        get_max_depth(cid, 0, set())
        
    return max_hops

def validate_graph(graph_data, rules):
    nodes = graph_data.get('nodes', [])
    edges = graph_data.get('edges', [])
    
    results = []
    
    for rule in rules:
        rule_id = rule['id']
        condition = rule['condition']
        passed = True
        reason = ""
        
        if rule_id == "ARQ-EG-001":
            # Claim -> Claim not allowed
            for e in edges:
                u = next((n for n in nodes if n['id'] == e['from']), None)
                v = next((n for n in nodes if n['id'] == e['to']), None)
                if u and v and u.get('type') == 'Claim' and v.get('type') == 'Claim':
                    passed = False
                    reason = f"Edge {u['id']} -> {v['id']} violates isolation"
                    break
                    
        elif rule_id == "ARQ-EG-002":
            # Orphan Claim prevention
            claim_ids = [n['id'] for n in nodes if n.get('type', '').lower() == 'claim']
            for cid in claim_ids:
                has_out = any(e['from'] == cid for e in edges)
                if not has_out:
                    passed = False
                    reason = f"Claim {cid} is an orphan"
                    break
                    
        elif rule_id == "ARQ-EG-003":
            # Acyclic
            if has_cycle(nodes, edges):
                passed = False
                reason = "Ciclo detectado en el grafo"
                
        elif rule_id == "ARQ-BD-001":
            # No EditXT eval nodes
            forbidden = {'ReviewFinding', 'ReviewSeverity', 'Recommendation'}
            for n in nodes:
                if n.get('type') in forbidden:
                    passed = False
                    reason = f"Nodo evaluativo prohibido: {n['id']} ({n.get('type')})"
                    break
                    
        elif rule_id == "ARQ-BD-002":
            # No AI Scientist generation nodes
            forbidden = {'Hypothesis', 'Experiment', 'Discovery'}
            for n in nodes:
                if n.get('type') in forbidden:
                    passed = False
                    reason = f"Nodo generativo prohibido: {n['id']} ({n.get('type')})"
                    break
                    
        elif rule_id == "ARQ-BD-003":
            # Evidence Never Contains Intent (Mission Boundary)
            forbidden = {'Mission', 'Brief', 'Execution'}
            for n in nodes:
                if n.get('type') in forbidden:
                    passed = False
                    reason = f"Nodo de intención prohibido en EvidenceGraph: {n['id']} ({n.get('type')})"
                    break

        elif rule_id == "ARQ-BD-004":
            # Governance Boundary (Decision Isolation)
            if any(n.get('type') == 'Decision' for n in nodes):
                passed = False
                reason = "Nodo Decision prohibido en EvidenceGraph"
                    
        elif rule_id == "ARQ-EG-004":
            # Max Hops <= 3
            hops = max_path_length_from_claims(nodes, edges)
            if hops > 3:
                passed = False
                reason = f"Max hops excedido ({hops} > 3)"
                
        results.append({
            "adr": rule_id,
            "name": rule["name"],
            "status": "PASS" if passed else "REJECTED",
            "reason": reason
        })
        
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_constitution.py <graph_json>")
        sys.exit(1)
        
    graph_path = Path(sys.argv[1])
    rules_path = Path("schemas/constitution_rules.yaml")
    
    if not graph_path.exists() or not rules_path.exists():
        print("Archivos no encontrados.")
        sys.exit(1)
        
    rules = load_rules(rules_path)
    
    with open(graph_path, 'r', encoding='utf-8') as f:
        graph_data = json.load(f)
        
    results = validate_graph(graph_data, rules)
    print(json.dumps(results, indent=2))
    
    if any(r['status'] == 'REJECTED' for r in results):
        sys.exit(1)

if __name__ == "__main__":
    main()
