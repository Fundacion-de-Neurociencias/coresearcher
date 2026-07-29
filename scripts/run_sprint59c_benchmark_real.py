#!/usr/bin/env python3
import csv, json, re, statistics, time, urllib.request
from datetime import datetime, timezone

REPOS_BY_CATEGORY = {
    "A_frameworks_ia": ["langchain-ai/langgraph","langchain-ai/langchain","run-llama/LlamaIndex","deepset-ai/haystack"],
    "B_proyectos_cientificos": ["scikit-learn/scikit-learn","pytorch/pytorch","jax-ml/jax","nilearn/nilearn"],
    "C_bibliotecas_pequenas": ["pallets/flask","psf/requests","pallets/click","marshmallow-code/marshmallow"],
    "D_archivados": ["google/guetzli","esimov/caire","request/request","bitly/segment"],
    "E_baja_actividad": ["tj/commander.js","substack/gray-matter","pallets/itsdangerous","jashkenas/underscore"],
}
GITHUB_HEADERS = {"Accept":"application/vnd.github+json","User-Agent":"coresearcher-benchmark","X-GitHub-Api-Version":"2022-11-28"}

def _sleep_if_rate_limited(response):
    remaining = response.getheader("X-RateLimit-Remaining")
    reset = response.getheader("X-RateLimit-Reset")
    if remaining == "0" and reset:
        wait = max(int(reset) - int(time.time()), 0) + 5
        print(f"  Rate limit alcanzado. Esperando {wait}s...")
        time.sleep(wait)

def fetch_json(url):
    req = urllib.request.Request(url, headers=GITHUB_HEADERS)
    with urllib.request.urlopen(req) as resp:
        _sleep_if_rate_limited(resp)
        return json.loads(resp.read().decode())

def fetch_paginated(url, max_pages=3):
    results = []
    for page in range(1, max_pages + 1):
        url_with_page = url + (f"&page={page}" if "?" in url else f"?page={page}")
        try:
            data = fetch_json(url_with_page)
            if isinstance(data, list) and len(data) > 0:
                results.extend(data)
            else:
                break
        except Exception as e:
            print(f"    Paginación interrumpida: {e}")
            break
    return results

def classify_claim(claim_text, source_url, quote):
    if quote and source_url:
        return "observable" if claim_text.lower() in quote.lower() else "derivable"
    elif source_url:
        return "derivable"
    return "inferred"

def extract_claims(repo):
    base_url = f"https://api.github.com/repos/{repo}"
    claims = []
    failure_modes = []
    try:
        repo_info = fetch_json(base_url)
    except Exception as e:
        return claims, [f"REPOSITORY_IDENTIFIER_ERROR: {e}"], {}, 0, 0
    try:
        issues = fetch_paginated(f"{base_url}/issues?state=closed&per_page=100&sort=updated&direction=desc")
        prs = fetch_paginated(f"{base_url}/pulls?state=closed&per_page=100&sort=updated&direction=desc")
        open_issues = fetch_paginated(f"{base_url}/issues?state=open&per_page=50")
        releases = fetch_paginated(f"{base_url}/releases?per_page=10")
    except Exception as e:
        return claims, [f"DATA_FETCH_ERROR: {e}"], repo_info, 0, 0
    if not issues and not prs: failure_modes.append("NO_ISSUES_NO_PRS")
    if not issues: failure_modes.append("NO_ISSUES")
    if not prs: failure_modes.append("NO_PULL_REQUESTS")
    if not releases: failure_modes.append("NO_RELEASES")
    if not open_issues: failure_modes.append("NO_OPEN_ISSUES")
    decision_keywords = ["we decided to","chose","opted for","replaced","switched to","decided to","went with","picked","selected"]
    alt_keywords = ["we could","we considered","instead of","rather than","alternative"]
    criteria_keywords = ["for performance","for simplicity","for compatibility","because","since","due to"]
    evidence_keywords = ["benchmark","test","performance","latency","memory","paper","data","metric"]
    def _process(items, ctype):
        out = []
        kws = {"decision":decision_keywords,"alternative":alt_keywords,"criterion":criteria_keywords,"evidence":evidence_keywords}.get(ctype, [])
        for item in items:
            body = (item.get("body") or "") + " " + (item.get("title") or "")
            body_lower = body.lower()
            for kw in kws:
                if kw in body_lower:
                    sentences = re.split(r'[.!?]+', body)
                    for sentence in sentences:
                        if kw in sentence.lower():
                            quote_text = item.get("title","") + ": " + (item.get("body") or "")[:500]
                            out.append({
                                "claim": sentence.strip()[:200],
                                "type": ctype,
                                "source_url": item.get("html_url",""),
                                "quote": quote_text[:500],
                                "classification": classify_claim(sentence.strip()[:200], item.get("html_url",""), quote_text),
                            })
                            break
                    break
        return out
    claims.extend(_process(issues,"decision"))
    claims.extend(_process(prs,"decision"))
    claims.extend(_process(issues,"alternative"))
    claims.extend(_process(issues,"criterion"))
    claims.extend(_process(issues,"evidence"))
    for issue in open_issues:
        quote = issue.get("title","") + ": " + (issue.get("body") or "")[:500]
        claims.append({"claim":issue.get("title","")[:200],"type":"gap","source_url":issue.get("html_url",""),"quote":quote[:500],"classification":"unknown"})
    return claims, failure_modes, repo_info, len(issues), len(prs)

def calculate_metrics(repo, category, claims, failure_modes, repo_info, n_issues, n_prs):
    total = len(claims)
    observable = sum(1 for c in claims if c["classification"] == "observable")
    derivable = sum(1 for c in claims if c["classification"] == "derivable")
    inferred = sum(1 for c in claims if c["classification"] == "inferred")
    unknown = sum(1 for c in claims if c["classification"] == "unknown")
    has_url = sum(1 for c in claims if c["source_url"])
    has_quote = sum(1 for c in claims if c["quote"])
    observable_ratio = round(observable/total,4) if total>0 else 0.0
    evidence_coverage = round((total-inferred-unknown)/total,4) if total>0 else 0.0
    auditability_score = round((has_url+has_quote)/(2*total),4) if total>0 else 0.0
    unknown_ratio = round(unknown/total,4) if total>0 else 0.0
    failure_types = []
    if total==0: failure_types.append("NO_CLAIMS")
    if auditability_score<0.90: failure_types.append("LOW_AUDITABILITY")
    if evidence_coverage<0.50: failure_types.append("LOW_COVERAGE")
    if any("ERROR" in str(fm) for fm in failure_modes): failure_types.append("FETCH_ERROR")
    if category=="D_archivados" and not repo_info.get("archived",False): failure_types.append("MISCLASSIFIED_NOT_ARCHIVED")
    if category=="E_baja_actividad":
        pushed = repo_info.get("pushed_at","")
        if pushed:
            pushed_dt = datetime.fromisoformat(pushed.replace("Z","+00:00"))
            threshold = datetime(2022,1,1,tzinfo=timezone.utc)
            if pushed_dt > threshold: failure_types.append("MISCLASSIFIED_NOT_LOW_ACTIVITY")
    failure_type = ";".join(failure_types) if failure_types else "OK"
    return {
        "repo":repo,"category":category,"stars":repo_info.get("stargazers_count",0),"issues":n_issues,"prs":n_prs,"claims":total,
        "observable_ratio":observable_ratio,"evidence_coverage":evidence_coverage,"auditability_score":auditability_score,"unknown_ratio":unknown_ratio,
        "failure_type":failure_type,"failure_modes":failure_modes,
    }

def write_csv(results, path):
    fieldnames = ["repo","stars","issues","prs","claims","observable_ratio","evidence_coverage","auditability_score","unknown_ratio","failure_type"]
    with open(path,"w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({k:r.get(k,"") for k in fieldnames})

    return claims, failure_modes, repo_info, len(issues), len(prs)


def compute_stats(results):
    keys = ["observable_ratio","evidence_coverage","auditability_score","unknown_ratio","claims"]
    stats = {}
    for key in keys:
        values = [r[key] for r in results]
        if values:
            stats[key] = {"mean":round(statistics.mean(values),4),"median":round(statistics.median(values),4),"std":round(statistics.stdev(values),4) if len(values)>1 else 0.0,"min":round(min(values),4),"max":round(max(values),4)}
        else:
            stats[key] = {"mean":0.0,"median":0.0,"std":0.0,"min":0.0,"max":0.0}
    return stats

def write_failure_taxonomy(failed_results, path):
    lines = ["# Sprint 59C --- Failure Taxonomy (Real Data)","","Repositorios excluidos o en riesgo por:","- `auditability_score < 0.90`","- `claims == 0`","- `evidence_coverage < 0.50`","","---",""]
    if not failed_results:
        lines.append("No se identificaron repositorios que cumplan los criterios de fallo.")
    else:
        for r in failed_results:
            lines.append(f"## {r['repo']}")
            lines.append("")
            lines.append(f"- **categoría**: {r['category']}")
            lines.append(f"- **stars**: {r['stars']}")
            lines.append(f"- **issues**: {r['issues']}")
            lines.append(f"- **prs**: {r['prs']}")
            lines.append(f"- **claims**: {r['claims']}")
            lines.append(f"- **observable_ratio**: {r['observable_ratio']}")
            lines.append(f"- **evidence_coverage**: {r['evidence_coverage']}")
            lines.append(f"- **auditability_score**: {r['auditability_score']}")
            lines.append(f"- **unknown_ratio**: {r['unknown_ratio']}")
            lines.append(f"- **failure_type**: {r['failure_type']}")
            if r.get("failure_modes"):
                lines.append(f"- **failure_modes (raw)**: {', '.join(r['failure_modes'])}")
            lines.append("")
            lines.append("---")
            lines.append("")
    with open(path,"w",encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    print("=== Sprint 59C --- BENCHMARK REAL ===")
    all_results = []
    for category, repos in REPOS_BY_CATEGORY.items():
        print(f"--- Categoría: {category} ---")
        for repo in repos:
            print(f"  Procesando: {repo}")
            try:
                claims, failure_modes, repo_info, n_issues, n_prs = extract_claims(repo)
                metrics = calculate_metrics(repo, category, claims, failure_modes, repo_info, n_issues, n_prs)
                all_results.append(metrics)
                print(f"    stars={metrics['stars']}, issues={metrics['issues']}, prs={metrics['prs']}, claims={metrics['claims']}")
                print(f"    observable_ratio={metrics['observable_ratio']}, evidence_coverage={metrics['evidence_coverage']}, auditability_score={metrics['auditability_score']}, unknown_ratio={metrics['unknown_ratio']}")
                print(f"    failure_type={metrics['failure_type']}")
                if failure_modes: print(f"    failure_modes={failure_modes}")
            except Exception as e:
                print(f"    ERROR: {e}")
                all_results.append({
                    "repo":repo,"category":category,"stars":0,"issues":0,"prs":0,"claims":0,
                    "observable_ratio":0.0,"evidence_coverage":0.0,"auditability_score":0.0,"unknown_ratio":0.0,
                    "failure_type":"FETCH_ERROR","failure_modes":[str(e)],
                })
            print()
    write_csv(all_results, "artifacts/cross_repo_20_benchmark.csv")
    print("CSV generado: artifacts/cross_repo_20_benchmark.csv")
    stats = compute_stats(all_results)
    with open("artifacts/stability_metrics_20repos.json","w",encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print("Stats generadas: artifacts/stability_metrics_20repos.json")
    print("\n=== Estadísticas agregadas ===")
    for k, v in stats.items():
        print(f"  {k}: mean={v['mean']}, median={v['median']}, std={v['std']}, min={v['min']}, max={v['max']}")
    failed = [r for r in all_results if r["auditability_score"]<0.90 or r["claims"]==0 or r["evidence_coverage"]<0.50]
    write_failure_taxonomy(failed, "artifacts/failure_taxonomy_real.md")
    print(f"\nTaxonomía generada: artifacts/failure_taxonomy_real.md")
    print(f"Repos en fallo: {len(failed)} / {len(all_results)}")
    print("\n=== Resumen ===")
    print(f"Repositorios procesados: {len(all_results)}")
    print(f"Repositorios en fallo: {len(failed)}")
    for r in all_results:
        flag = " [FALLO]" if r in failed else ""
        print(f"  {r['repo']}: claims={r['claims']}, audit={r['auditability_score']}, coverage={r['evidence_coverage']}{flag}")
    print("\nSPRINT 59C --- BENCHMARK REAL completado.")

if __name__ == "__main__":
    main()


    with open(path,"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
