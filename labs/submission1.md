# Triage Report — OWASP Juice Shop

## Scope & Asset
- Asset: OWASP Juice Shop (local lab instance)
- Image: bkimminich/juice-shop:v19.0.0
- Release link/date: <https://hub.docker.com/layers/bkimminich/juice-shop/v19.0.0/images/sha256-547bd3fef4a6d7e25e131da68f454e6dc4a59d281f8793df6853e6796c9bbf58> — <2025-09-04T05:38:11Z>
- Image digest (optional): <sha256:2765a26de7647609099a338d5b7f61085d95903c8703bb70f03fcc4b12f0818d>

## Environment
- Host OS: Windows 10 22H2
- Docker: 29.1.5

## Deployment Details
- Run command used: `docker run -d --name juice-shop -p 127.0.0.1:3000:3000 bkimminich/juice-shop:v19.0.0`
- Access URL: http://127.0.0.1:3000
- Network exposure: 127.0.0.1 only [ * ] Yes  [ ] No  (explain if No)

## Health Check
- Page load:
![alt text](image1.png)
- API check: first 5–10 lines from `curl -s http://127.0.0.1:3000/rest/products | head`
```
<html>
  <head>
    <meta charset='utf-8'>
    <title>Error: Unexpected path: /rest/products</title>
    <style>* {
  margin: 0;
  padding: 0;
  outline: 0;
}

```

## Surface Snapshot (Triage)
- Login/Registration visible: [ * ] Yes  [ ] No — notes: The login and registration forms are standard. They contain numerous intentional vulnerabilities (e.g., SQL injection).
- Product listing/search present: [ * ] Yes  [ ] No — notes: It contains multiple vulnerability types, including XSS and injection attacks.
- Admin or account area discoverable: [ * ] Yes  [ ] No — notes: It is hidden. There is no direct link to the admin panel in the user interface.
- Client-side errors in console: [ * ] Yes  [ ] No — notes: When going to the product information page (/#/search) the app can output complete data objects (including hidden fields, such as id or createdAt) to the console
- Security headers (quick look — optional): `curl -I http://127.0.0.1:3000` → CSP/HSTS present? No.

HTTP/1.1 200 OK\
Access-Control-Allow-Origin: *\
X-Content-Type-Options: nosniff\
X-Frame-Options: SAMEORIGIN\
Feature-Policy: payment 'self'\
X-Recruiting: /#/jobs\
Accept-Ranges: bytes\
Cache-Control: public, max-age=0\
Last-Modified: Mon, 09 Feb 2026 09:21:20 GMT\
ETag: W/"124fa-19c41b498dc"\
Content-Type: text/html; charset=UTF-8\
Content-Length: 75002\
Vary: Accept-Encoding\
Date: Mon, 09 Feb 2026 13:19:48 GMT\
Connection: keep-alive\
Keep-Alive: timeout=5

## Risks Observed (Top 3)
1) Injection. SQL injectoin allows to log in as admin
2) JWT in the local storage. The token can be stolen during an XSS attack.
3) DOM XSS. A malicious script can be inserted into the search form.

