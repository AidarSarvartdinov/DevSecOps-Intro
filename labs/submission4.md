# Lab 4 Submission — SBOM Generation & Software Composition Analysis

## Task 1 — SBOM Generation with Syft and Trivy

### Package Type Distribution
A comparison of the package type distributions found by Syft and Trivy:

**Syft Findings:**
- **npm:** 1128 packages
- **deb:** 10 packages
- **binary:** 1 package
- **Total:** 1139 packages

**Trivy Findings:**
- **Node.js:** 1125 packages
- **OS Packages (debian 12.11):** 10 packages
- **Total:** 1135 packages

### Dependency Discovery Analysis
Syft slightly outperformed Trivy in raw package detection (1139 vs 1135), finding a `binary` type package and 3 additional npm packages. Both tools were highly effective at identifying the Node.js application dependencies and the underlying Debian 12.11 OS packages. Syft's JSON format natively separated components by type and provided a slightly deeper detection of edge cases.

### License Discovery Analysis
License extraction revealed some tool differences in scanning and categorization:
- **Syft** found **32** unique license types. The most common were MIT (890), ISC (143), LGPL-3.0 (19), and BSD-3-Clause (16).
- **Trivy** found **28** unique license types. It separately categorized OS package licenses (GPL-2.0-only, Artistic-2.0) and language package licenses (MIT 878, ISC 143).
- **Conclusion:** Syft discovered slightly more license varieties and parsed complex/dual-licenses effectively `(MIT OR Apache-2.0)`, whereas Trivy offered clean categorization but missed a few niche license attachments found by Syft.

---

## Task 2 — Software Composition Analysis with Grype and Trivy

### SCA Tool Comparison
Both Grype and Trivy successfully analyzed the application for vulnerabilities. 

**Vulnerability Severities (Grype):**
- **High:** 88
- **Medium:** 32
- **Negligible:** 12
- **Critical:** 11
- **Low:** 3
- *Total:* 146

**Vulnerability Severities (Trivy):**
- **High:** 81
- **Medium:** 34
- **Low:** 18
- **Critical:** 10
- *Total:* 143

### Critical Vulnerabilities Analysis
Top critical vulnerabilities discovered and remediation advice:
1. **CVE-2022-25883 / GHSA-4wqj-x9cw-3fv8 (semver)**: A ReDoS vulnerability in parsing. *Remediation: Upgrade `semver` to a patched version.*
2. **GHSA-p6mc-m468-83gw (engine.io)**: Uncaught exception vulnerability in engine.io. *Remediation: Upgrade `engine.io` to version >= 6.2.1.*
3. **CVE-2023-26136 (tough-cookie)**: Prototype pollution vulnerability. *Remediation: Upgrade `tough-cookie` to 4.1.3+.*
4. **CVE-2022-25844 (qs)**: Denial of Service parsing arrays. *Remediation: Upgrade `qs` object parser in the dependency chain.* 
5. **libsqlite3-0 OS Vulns**: Outdated SQLite library in the base Debian image. *Remediation: Rebuild the Docker image using a newer Debian base.*

### License Compliance Assessment
The license scan highlighted several potentially restrictive licenses depending on how the application is distributed:
- **GPL-2.0 / GPL-3.0**: Detected in several dependencies. If the Juice Shop application is distributed, these copyleft licenses could enforce open-sourcing of the proprietary codebase.
- **Recommendations**: For internal or SaaS usage, this is generally acceptable, but redistribution must be carefully audited by legal to verify the GPL boundaries.

### Additional Security Features
**Secrets Scanning:** Trivy's secret scanning completed with no hardcoded credentials found in the application configuration files or `package.json` manifests, demonstrating safe handling of secrets in the base configuration.

---

## Task 3 — Toolchain Comparison: Syft+Grype vs Trivy All-in-One

### Accuracy Analysis
- **Packages detected by both tools:** 988
- **Packages only detected by Syft:** 13
- **Packages only detected by Trivy:** 9
- **CVEs found by Grype:** 95
- **CVEs found by Trivy:** 91
- **Common CVEs:** 26

*Note: The low Common CVE overlap (26) is due to differing vulnerability naming conventions. Trivy uses GHSA IDs frequently alongside CVEs, whereas Grype may favor traditional CVE IDs, making strict textual correlation appear lower than actual functional overlap.*

### Tool Strengths and Weaknesses
**Syft + Grype**
- **Strengths:** Excellent, highly-detailed SBOM generation. Syft is arguably the industry standard for SBOMs, extracting very granular license and metadata details. Grype integrates seamlessly with Syft's output.
- **Weaknesses:** Requires managing two separate tools and moving output files between them, slightly increasing CI/CD complexity.

**Trivy (All-in-One)**
- **Strengths:** Single binary that handles SBOMs, vulnerabilities, licenses, and secrets. Extremely fast, very developer-friendly, and offers consolidated JSON outputs covering the entire spectrum.
- **Weaknesses:** SBOM generation is slightly less "deep" than Syft (e.g., missed 4 packages and 4 license types in this run), though difference is immaterial for most use cases.

### Use Case Recommendations
- **Choose Syft + Grype if:** You need strict compliance SBOMs (CycloneDX/SPDX), have a dedicated compliance team that audits SBOMs independently from vulnerabilities, or require the absolute deepest dependency parsing. 
- **Choose Trivy if:** You are building DevSecOps pipelines from scratch and want maximum coverage (secrets, IaC, Vulns, License) with minimal tool maintenance and the lowest friction in CI/CD.

### Integration Considerations
For CI/CD automation, **Trivy** is generally easier to drop into a GitHub Action or GitLab CI pipeline due to its single-binary architecture. The **Syft + Grype** combination requires chaining the artifacts (SBOM generation -> artifact storage -> SCA scanning), but provides a clean separation of concerns for enterprise environments where the SecOps team might scan the SBOM independently of the build pipeline.
