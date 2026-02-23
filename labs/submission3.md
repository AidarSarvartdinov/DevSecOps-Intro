# Lab 3 — Secure Git

## Task 1 — SSH Commit Signature Verification

### 1.1 Benefits of Signing Commits

Commit signing provides cryptographic proof of **authorship** and **integrity** for every change in a repository. The core benefits are:

| Benefit | Description |
|---------|-------------|
| **Authenticity** | Proves the commit was created by the claimed author, preventing impersonation via `git config user.email` spoofing |
| **Integrity** | Any post-signing modification (content, message, metadata) invalidates the signature |
| **Non-repudiation** | Authors cannot deny having made a signed commit |
| **Supply-chain trust** | GitHub displays a "Verified" badge, enabling reviewers to trust that merged code comes from authorized contributors |
| **Compliance** | Satisfies audit requirements in regulated environments (SOC 2, ISO 27001) where provenance tracking is mandatory |

SSH signing (vs. GPG) offers a simpler key management model — developers already have SSH keys for repository access, so reusing them for signing reduces operational overhead.

### 1.2 SSH Key Setup and Configuration

**Key Generation:**

```
$ ssh-keygen -t ed25519 -C "a.sarvartdinov@innopolis.university"

Generating public/private ed25519 key pair.
Enter file in which to save the key (C:\Users\aidar/.ssh/id_ed25519):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in C:\Users\aidar/.ssh/id_ed25519
Your public key has been saved in C:\Users\aidar/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:4tmBCfpTJ3U6QEZKPo5NrU8uK4V/Wd29m5gn6fz/z20 a.sarvartdinov@innopolis.university
```

**Git Configuration for SSH Signing:**

```
$ git config --global gpg.format ssh
$ git config --global user.signingkey C:\Users\aidar\.ssh\id_ed25519.pub
$ git config --global commit.gpgSign true
```

**Verification of configuration:**

```
$ git config --global --list | grep -E "gpg|signing|sign"
user.signingkey=C:\Users\aidar\.ssh\id_ed25519.pub
gpg.format=ssh
commit.gpgsign=true
```

**Public key added to GitHub** as a Signing Key at Settings → SSH and GPG keys → New SSH key (Type: Signing Key):

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKFua7OrFJCV7XPPagTsWm/Mh4XTbbtwaKVpqg2N2QtC a.sarvartdinov@innopolis.university
```

### 1.3 Signed Commit

```
$ git commit -S -m "docs: add lab3 submission"
```

After pushing, the commit displays a **"Verified"** badge on GitHub, confirming the signature was validated against the uploaded signing key.

### 1.4 Analysis: Why Is Commit Signing Critical in DevSecOps Workflows?

In DevSecOps, every artifact flowing through the CI/CD pipeline must be **traceable and tamper-evident**. Commit signing addresses several critical concerns:

1. **Preventing supply-chain attacks.** Without signing, an attacker who gains write access to a repository can push malicious commits under any author identity. Signed commits make such impersonation detectable — CI pipelines can enforce a policy that only verified commits are deployable.

2. **Enforcing branch protection.** GitHub supports requiring signed commits on protected branches. Combined with CODEOWNERS and required reviews, this creates a multi-layered defense: code must be authored by a verified identity, reviewed by an authorized team member, and pass automated checks before merging.

3. **Audit trail integrity.** In incident response, investigators rely on git history to reconstruct what happened. If commits are unsigned, the entire history is untrustworthy — anyone could have rewritten it. Signing provides a cryptographic audit trail.

4. **Compliance automation.** Standards like SLSA (Supply-chain Levels for Software Artifacts) require provenance metadata. Signed commits are the foundation of provenance — they answer "who authored this change and has it been modified since?"

5. **Zero-trust development.** DevSecOps adopts a zero-trust mindset: trust nothing, verify everything. Commit signing extends this principle to source code — every commit is verified, not just assumed legitimate.

---

## Task 2 — Pre-commit Secret Scanning

#### Test 1: Blocked Commit (Secret Detected)

A test file `test-secret.txt` was created with a fake AWS access key:

```
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

```
$ git add test-secret.txt
$ git commit -m "test: add file with secret"

[pre-commit] scanning staged files for secrets…
[pre-commit] Files to scan: test-secret.txt
[pre-commit] TruffleHog scan on non-lectures files…
[pre-commit] ✖ TruffleHog detected potential secrets in non-lectures files
[pre-commit] Gitleaks scan on staged files…
✖ Secrets found in non-excluded file: test-secret.txt
✖ COMMIT BLOCKED: Secrets detected in non-excluded files.
Fix or unstage the offending files and try again.
```

**Result:** ✖ Commit was blocked — both TruffleHog and Gitleaks detected the fake AWS credentials.

#### Test 2: Successful Commit (No Secrets)

After removing the test file and staging a clean file:

```
$ git rm test-secret.txt
$ git add labs/submission3.md
$ git commit -m "docs: add lab3 submission"

[pre-commit] scanning staged files for secrets…
[pre-commit] Files to scan: labs/submission3.md
[pre-commit] TruffleHog scan on non-lectures files…
[pre-commit] ✓ TruffleHog found no secrets in non-lectures files
[pre-commit] Gitleaks scan on staged files…
[pre-commit] No secrets found in labs/submission3.md
✓ No secrets detected in non-excluded files; proceeding with commit.
```

**Result:** Commit proceeded successfully — no secrets detected.

### Analysis: How Automated Secret Scanning Prevents Security Incidents

Secrets accidentally committed to version control are one of the most common causes of security breaches. Once a secret is pushed, it becomes part of the permanent history (even if "deleted" in a subsequent commit) and may be exposed to anyone with repository access.

**How pre-commit scanning mitigates this risk:**

| Layer | Without Scanning | With Pre-commit Scanning |
|-------|-----------------|--------------------------|
| **Prevention** | Secrets reach the repository | Secrets are caught before commit |
| **Detection speed** | Discovered hours/days later via audit | Detected instantly at commit time |
| **Blast radius** | Secret in git history forever (requires history rewrite) | Secret never enters history |
| **Developer friction** | Manual review only | Automated, consistent check |
| **Coverage** | Depends on human vigilance | Pattern-based detection (regex for API keys, tokens, passwords) |

**Defense-in-depth with two scanners:**

- **TruffleHog** specializes in high-confidence detections using entropy analysis and verified credential checks (it actually tests if credentials are valid).
- **Gitleaks** uses regex-based patterns from a comprehensive rule set, catching a broader range of secret formats.

Using both tools in parallel provides complementary coverage — TruffleHog catches secrets Gitleaks might miss (and vice versa), reducing the false-negative rate.

**Integration into DevSecOps workflows:**

1. **Shift-left security** — catching secrets at the earliest possible stage (before commit) is far cheaper than remediating after deployment.
2. **Automated enforcement** — the hook runs automatically on every commit, removing the dependency on developer awareness.
3. **Lectures directory exception** — the hook intelligently allows educational content in `lectures/` while blocking secrets in application code, balancing security with usability.
