# Lab 5 Submission

## Task 1: SAST Tool Effectiveness

**Vulnerabilities Detected by Semgrep:**
Semgrep detected code-level vulnerabilities by statically analyzing the source code. The main categories included:
- Hardcoded secrets, API keys, and JWT secrets in the repository text (e.g., `rs256.key`).
- Insecure cryptographic algorithms and hardcoded PRNG seeds.
- SQL injection patterns where string concatenation is used in database query builders.
- Cross-Site Scripting (XSS) patterns where raw user input is interpolated into HTML templates or unsafe DOM methods.
- Weak hashing algorithms used for user data.

**Coverage:**
Semgrep scanned the entire repository (frontend and backend code) covering approximately 1,130 files and identified over 45 security findings based on the `p/owasp-top-ten` and `p/security-audit` rulesets.

### Critical Vulnerability Analysis

1. **Hardcoded JWT Secret**
   - **Type:** Hardcoded Secret / Cryptographic Failure
   - **File:** `config/default.yml` (and `lib/insecurity.ts`)
   - **Severity:** High
2. **SQL Injection (Login Bypass)**
   - **Type:** SQL Injection (CWE-89)
   - **File:** `routes/login.js`
   - **Severity:** High
3. **Insecure Randomness / Weak Crypto**
   - **Type:** Cryptographic Failure (CWE-338)
   - **File:** `routes/profileImageUrlUpload.js` (and password resets)
   - **Severity:** Medium/High
4. **Reflected/DOM XSS**
   - **Type:** Cross-Site Scripting (XSS)
   - **File:** `frontend/src/app/search-result/search-result.component.ts`
   - **Severity:** Medium
5. **Path Traversal**
   - **Type:** Broken Access Control / File System
   - **File:** `routes/fileServer.js`
   - **Severity:** High

## Task 2: DAST Results Analysis

### Authenticated vs Unauthenticated Scanning

**URL Discovery Count:**
- Unauthenticated: ~112 URLs
- Authenticated: ~1,199 URLs

**Discovered Authenticated Endpoints:**
- `/rest/admin/application-configuration`
- `/rest/admin/application-version`
- User-specific profile routes (`/profile`)
- E-commerce cart and basket functions (`/rest/basket/*`)
- Payment and wallet endpoints (`/rest/wallet/*`)

**Why Authenticated Scanning Matters:**
Unauthenticated scanning only finds vulnerabilities on publicly accessible endpoints, missing the majority of the application's attack surface. Authenticated scanning (using the login credentials and ZAP's AJAX Spider) unlocks user-specific features, admin panels, and deeply nested operations, discovering >10x the endpoints and exposing critical context-dependent logic flaws.

### Tool Comparison Matrix

| Tool | Findings | Severity Breakdown | Best Use Case |
|---|---|---|---|
| ZAP | High volume of alerts (over 100) | Mostly Low/Medium, some High | Comprehensive scanning, crawling, authentication support. |
| Nuclei | Template matches (approx 10-15) | Low to High | Fast template-based vulnerability scanning (known CVEs, exposed panels). |
| Nikto | Around 10-20 alerts | Mostly Info/Low | Server misconfiguration scanning, checking for missing headers. |
| SQLmap | 2 database injection points | High | Deep SQL injection testing, data extraction, and payload confirmation. |

### Tool-Specific Strengths and Example Findings

- **ZAP:**
  - Strengths: Comprehensive crawling and passive/active scanning. Handles authentication and complex session states seamlessly with the Automation Framework.
  - Example Finding: Discovered XSS in the search parameter and Missing Anti-clickjacking Header (X-Frame-Options).
- **Nuclei:**
  - Strengths: Extreme speed, uses YAML templates to detect specific known vulnerabilities, exposed files, or common CVEs rapidly across many hosts.
  - Example Finding: Detected `package.json` exposure and missing security headers.
- **Nikto:**
  - Strengths: Quickly identifies server misconfigurations, outdated web server components, and directory listings.
  - Example Finding: `The X-XSS-Protection header is not defined` and `/ftp/` directory index exposed.
- **SQLmap:**
  - Strengths: Highly specialized for probing and exploiting SQL injections. Can extract entire backend database schemas and user data automatically.
  - Example Finding: Successfully exploited Boolean and Time-based blind SQL injection in `/rest/user/login` using the `email` JSON parameter, extracting user entries and hashed passwords.

## Task 3: SAST/DAST Correlation

**Total Findings:**
- SAST Count: 45+ findings
- Complete DAST Count: 100+ combined findings

**Vulnerabilities found ONLY by SAST:**
- Hardcoded sensitive data (e.g., test certificates, RSA keys).
- Weak RNG algorithms in functions that are hard to trigger externally.
- Detection of dangerous function calls (`eval()`, unsafe deserialization) before they are reachable.

**Vulnerabilities found ONLY by DAST:**
- Missing HTTP security headers (e.g., CORS, CSP, X-Frame-Options).
- Exposed server directories (like `/ftp/` without authentication).
- Misconfigured TLS/SSL protocols or cipher suites.

**Explanation:**
SAST operates on the source code (white-box) without executing the program, excelling at finding dangerous coding patterns, secrets, and logic flaws early in the SDLC. DAST tests the running application from the outside (black-box), focusing on environmental misconfigurations, deployment errors, and runtime responses that SAST cannot detect. Using BOTH provides comprehensive security coverage.
