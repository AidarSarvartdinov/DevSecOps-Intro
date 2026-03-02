import json
import collections
from collections import Counter

def format_counter(counter):
    return "\n".join(f" {count} {val}" for val, count in counter.most_common())

with open("labs/lab4/syft/juice-shop-syft-native.json", "r", encoding="utf-8") as f:
    syft_data = json.load(f)

with open("labs/lab4/trivy/juice-shop-trivy-detailed.json", "r", encoding="utf-8") as f:
    trivy_data = json.load(f)

# Syft Package Counts
syft_obj_types = Counter()
syft_licenses_extract = []
syft_licenses_counter = Counter()

for artifact in syft_data.get("artifacts", []):
    syft_obj_types[artifact.get("type")] += 1
    licenses = artifact.get("licenses", [])
    if licenses:
        license_values = [l.get("value") for l in licenses]
        syft_licenses_extract.append(f"{artifact.get('name')} | {artifact.get('version')} | {', '.join(license_values)}")
        for l in license_values:
            syft_licenses_counter[l] += 1

# Trivy Package Counts
trivy_obj_types = Counter()
trivy_os_licenses = Counter()
trivy_lang_licenses = Counter()

for result in trivy_data.get("Results", []):
    target = result.get("Target", "Unknown")
    rclass = result.get("Class", "")
    for pkg in result.get("Packages", []):
        ptype = pkg.get("Type", "unknown")
        trivy_obj_types[f"{target} - {ptype}"] += 1
        
        licenses = pkg.get("Licenses", [])
        for l in licenses:
            if "os-pkgs" in rclass:
                trivy_os_licenses[l] += 1
            if "lang-pkgs" in rclass:
                trivy_lang_licenses[l] += 1

with open("labs/lab4/analysis/sbom-analysis.txt", "w", encoding="utf-8") as f:
    f.write("=== SBOM Component Analysis ===\n\n")
    f.write("Syft Package Counts:\n")
    f.write(format_counter(syft_obj_types) + "\n\n")
    
    f.write("Trivy Package Counts:\n")
    f.write(format_counter(trivy_obj_types) + "\n\n")
    
    f.write("=== License Analysis ===\n\n")
    f.write("Syft Licenses:\n")
    f.write(format_counter(syft_licenses_counter) + "\n\n")
    
    f.write("Trivy Licenses (OS Packages):\n")
    f.write(format_counter(trivy_os_licenses) + "\n\n")
    
    f.write("Trivy Licenses (Node.js):\n")
    f.write(format_counter(trivy_lang_licenses) + "\n\n")

with open("labs/lab4/syft/juice-shop-licenses.txt", "w", encoding="utf-8") as f:
    f.write("Extracting licenses from Syft SBOM...\n")
    f.write("\n".join(syft_licenses_extract) + "\n")

print("Analysis extraction complete.")
