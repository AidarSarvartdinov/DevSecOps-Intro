import json
import collections

with open("labs/lab4/syft/grype-vuln-results.json", "r", encoding="utf-8") as f:
    grype_data = json.load(f)

with open("labs/lab4/trivy/juice-shop-trivy-detailed.json", "r", encoding="utf-8") as f:
    trivy_vuln = json.load(f)

with open("labs/lab4/syft/juice-shop-syft-native.json", "r", encoding="utf-8") as f:
    syft_sbom = json.load(f)

with open("labs/lab4/trivy/juice-shop-trivy-detailed.json", "r", encoding="utf-8") as f:
    trivy_sbom = json.load(f)

try:
    with open("labs/lab4/trivy/trivy-licenses.json", "r", encoding="utf-8") as f:
        trivy_licenses = json.load(f)
except:
    trivy_licenses = None

# 1. Vulnerability Analysis
grype_severity = collections.Counter()
for match in grype_data.get("matches", []):
    sev = match.get("vulnerability", {}).get("severity", "Unknown")
    grype_severity[sev] += 1

trivy_severity = collections.Counter()
if trivy_vuln.get("Results"):
    for result in trivy_vuln.get("Results", []):
        for vuln in result.get("Vulnerabilities", []):
            sev = vuln.get("Severity", "Unknown")
            trivy_severity[sev] += 1

syft_licenses_count = len(set(
    l.get("value") for artifact in syft_sbom.get("artifacts", []) 
    for l in artifact.get("licenses", [])
))

trivy_licenses_count = 0
if trivy_licenses and trivy_licenses.get("Results"):
    trivy_licenses_count = len(set(
        l.get("Name")
        for r in trivy_licenses.get("Results", [])
        if r.get("Licenses")
        for l in r.get("Licenses", []) if l.get("Name")
    ))

with open("labs/lab4/analysis/vulnerability-analysis.txt", "w", encoding="utf-8") as f:
    f.write("=== Vulnerability Analysis ===\n\n")
    f.write("Grype Vulnerabilities by Severity:\n")
    for sev, count in grype_severity.most_common():
        f.write(f" {count} {sev}\n")
        
    f.write("\nTrivy Vulnerabilities by Severity:\n")
    for sev, count in trivy_severity.most_common():
        f.write(f" {count} {sev}\n")
        
    f.write("\n=== License Analysis Summary ===\n")
    f.write("Tool Comparison:\n")
    f.write(f"- Syft found {syft_licenses_count} unique license types\n")
    f.write(f"- Trivy found {trivy_licenses_count} unique license types\n")

# 2. Package & Accuracy Comparison
syft_pkgs = set()
for a in syft_sbom.get("artifacts", []):
    syft_pkgs.add(f"{a.get('name')}@{a.get('version')}")

trivy_pkgs = set()
if trivy_sbom.get("Results"):
    for r in trivy_sbom.get("Results", []):
        for p in r.get("Packages", []):
            trivy_pkgs.add(f"{p.get('Name')}@{p.get('Version')}")

common_pkgs = syft_pkgs.intersection(trivy_pkgs)
syft_only = syft_pkgs - trivy_pkgs
trivy_only = trivy_pkgs - syft_pkgs

with open("labs/lab4/comparison/syft-packages.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(syft_pkgs)))
with open("labs/lab4/comparison/trivy-packages.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(trivy_pkgs)))
with open("labs/lab4/comparison/common-packages.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(common_pkgs)))
with open("labs/lab4/comparison/syft-only.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(syft_only)))
with open("labs/lab4/comparison/trivy-only.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(trivy_only)))

grype_cves = set()
for m in grype_data.get("matches", []):
    grype_cves.add(m.get("vulnerability", {}).get("id"))

trivy_cves = set()
if trivy_vuln.get("Results"):
    for r in trivy_vuln.get("Results", []):
        for v in r.get("Vulnerabilities", []):
            trivy_cves.add(v.get("VulnerabilityID"))

common_cves = grype_cves.intersection(trivy_cves)

with open("labs/lab4/comparison/grype-cves.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(grype_cves)))
with open("labs/lab4/comparison/trivy-cves.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(trivy_cves)))

with open("labs/lab4/comparison/accuracy-analysis.txt", "w", encoding="utf-8") as f:
    f.write("=== Package Detection Comparison ===\n")
    f.write(f"Packages detected by both tools: {len(common_pkgs)}\n")
    f.write(f"Packages only detected by Syft: {len(syft_only)}\n")
    f.write(f"Packages only detected by Trivy: {len(trivy_only)}\n\n")
    f.write("=== Vulnerability Detection Overlap ===\n")
    f.write(f"CVEs found by Grype: {len(grype_cves)}\n")
    f.write(f"CVEs found by Trivy: {len(trivy_cves)}\n")
    f.write(f"Common CVEs: {len(common_cves)}\n")

print("Analysis 2 & 3 complete.")
