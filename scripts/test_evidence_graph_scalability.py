import json
import time
from validate_constitution import load_rules, validate_graph
import uuid

def generate_synthetic_graph(num_claims):
    print(f"Generando grafo sintético de {num_claims} claims...")
    nodes = []
    edges = []
    
    # Cada claim tendra 1 quote y 1 source para mantener max hops = 2
    for i in range(num_claims):
        cid = f"CLAIM-{i:06d}"
        qid = f"QUOTE-{i:06d}"
        sid = f"SOURCE-{i:06d}"
        
        nodes.append({"id": cid, "type": "Claim", "text": "Synthentic claim data."})
        nodes.append({"id": qid, "type": "Quote", "text": "Synthetic quote."})
        nodes.append({"id": sid, "type": "Source", "text": "Synthetic source."})
        
        edges.append({"from": cid, "to": qid, "type": "supported_by", "hops": 1})
        edges.append({"from": qid, "to": sid, "type": "sourced_from", "hops": 1})
        
    return {"graph_id": f"DG-TEST-{uuid.uuid4().hex[:6]}", "nodes": nodes, "edges": edges}

def run_scalability_tests():
    rules = load_rules("schemas/constitution_rules.yaml")
    
    scales = [1000, 10000, 100000]
    
    print("--- INICIANDO BENCHMARK DE ESCALABILIDAD ARQ-002B ---")
    
    for scale in scales:
        graph = generate_synthetic_graph(scale)
        num_nodes = len(graph["nodes"])
        num_edges = len(graph["edges"])
        
        print(f"\nTesteando Escala: {scale} Claims ({num_nodes} nodos, {num_edges} aristas)")
        
        start_time = time.time()
        results = validate_graph(graph, rules)
        end_time = time.time()
        
        elapsed_ms = (end_time - start_time) * 1000
        
        passed = all(r["status"] == "PASS" for r in results)
        status_text = "[PASS]" if passed else "[FAIL]"
        
        print(f"{status_text} Validación completada en {elapsed_ms:.2f} ms")
        if elapsed_ms > 5000:
            print("[WARNING] ADVERTENCIA: La latencia de validación superó los 5 segundos. Riesgo de cuello de botella estructural.")

if __name__ == "__main__":
    run_scalability_tests()
