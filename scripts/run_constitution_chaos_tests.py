import json
from pathlib import Path
from validate_constitution import load_rules, validate_graph

def run_tests():
    rules_path = Path("schemas/constitution_rules.yaml")
    rules = load_rules(rules_path)
    
    print("Iniciando Chaos Engineering Constitucional...\n")
    
    tests = [
        {
            "name": "Caso 1: EvidenceGraph con ciclos",
            "expected_fail_rule": "ARQ-EG-003",
            "graph": {
                "nodes": [
                    {"id": "A", "type": "Claim"},
                    {"id": "B", "type": "Quote"}
                ],
                "edges": [
                    {"from": "A", "to": "B"},
                    {"from": "B", "to": "A"}
                ]
            }
        },
        {
            "name": "Caso 2: Claim sin evidencia (Orphan)",
            "expected_fail_rule": "ARQ-EG-002",
            "graph": {
                "nodes": [
                    {"id": "CLAIM-01", "type": "Claim"}
                ],
                "edges": []
            }
        },
        {
            "name": "Caso 3: Claim > 3 hops",
            "expected_fail_rule": "ARQ-EG-004",
            "graph": {
                "nodes": [
                    {"id": "C", "type": "Claim"},
                    {"id": "Q", "type": "Quote"},
                    {"id": "S1", "type": "Source"},
                    {"id": "S2", "type": "Source"},
                    {"id": "U", "type": "URL"}
                ],
                "edges": [
                    {"from": "C", "to": "Q", "hops": 1},
                    {"from": "Q", "to": "S1", "hops": 1},
                    {"from": "S1", "to": "S2", "hops": 1},
                    {"from": "S2", "to": "U", "hops": 1}
                ]
            }
        },
        {
            "name": "Caso 4: EditXT intenta emitir descubrimientos (Violación de Frontera)",
            "expected_fail_rule": "ARQ-BD-001",
            "graph": {
                "nodes": [
                    {"id": "C", "type": "Claim"},
                    {"id": "REV-01", "type": "ReviewFinding"}
                ],
                "edges": [{"from": "C", "to": "REV-01"}]
            }
        },
        {
            "name": "Caso 5: CoResearcher intenta generar hipótesis (Violación de Frontera)",
            "expected_fail_rule": "ARQ-BD-002",
            "graph": {
                "nodes": [
                    {"id": "HYP-01", "type": "Hypothesis"}
                ],
                "edges": []
            }
        },
        {
            "name": "Caso 6: EvidenceGraph contiene un Brief (Violación MissionGraph)",
            "expected_fail_rule": "ARQ-BD-003",
            "graph": {
                "nodes": [
                    {"id": "BRIEF-01", "type": "Brief"}
                ],
                "edges": []
            }
        },
        {
            "name": "Caso 7: EvidenceGraph contiene una Decisión (Violación DecisionGraph)",
            "expected_fail_rule": "ARQ-BD-004",
            "graph": {
                "nodes": [
                    {"id": "DECISION-01", "type": "Decision"}
                ],
                "edges": []
            }
        }
    ]
    
    passed_tests = 0
    
    for test in tests:
        print(f"Probando {test['name']}...")
        results = validate_graph(test["graph"], rules)
        
        # Check if the expected rule was REJECTED
        rule_result = next((r for r in results if r["adr"] == test["expected_fail_rule"]), None)
        
        if rule_result and rule_result["status"] == "REJECTED":
            print(f"[PASS] EXITO: Violación detectada correctamente por {test['expected_fail_rule']}")
            passed_tests += 1
        else:
            print(f"[FAIL] FALLO: El sistema no detectó la violación esperada de {test['expected_fail_rule']}")
            print(f"Resultados: {json.dumps(results, indent=2)}")
            
        print("-" * 40)
        
    print(f"\nResultados del Chaos Test: {passed_tests}/{len(tests)} pasados.")

if __name__ == "__main__":
    run_tests()
