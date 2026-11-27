---
name: ctf-solve-mode
description: Use for CTF, challenge, flag hunting, web/pwn/reverse/crypto/misc/forensics tasks. Prioritizes solving and extracting the flag over SRC-style reporting.
---

# CTF Solve Mode

## Goal

Find the flag quickly and reproducibly.

Do **not** default to:
- SRC vulnerability report format
- Risk rating
- Business impact analysis
- Remediation advice
- pentest-quality-gate

unless the user explicitly asks for a report.

## Default Output Format

```
题型：
关键线索：
测试过程：
成功 payload / 命令：
flag：
简短复盘：
```

## Tool Priority

For simple Web CTF (HTTP params, PHP, LFI, SSRF, SQLi, template injection, file read, upload):
1. curl
2. Python requests
3. grep / sed / awk or PowerShell text processing
4. dirsearch / ffuf when path discovery is needed
5. nmap when service discovery is needed
6. Chrome MCP only when browser state or JS interaction matters

Use Chrome MCP when:
- Login state matters
- JavaScript rendering matters
- XSS popup needs confirmation
- WebSocket / SSE page interaction matters
- Frontend route / state needs inspection

Do **not** use Chrome MCP as the default for simple HTTP parameter testing.

## Request Testing Discipline

When testing multiple payloads, always label results:
- Payload name
- Full URL or parameter
- HTTP status code
- Response length
- Key markers: `flag{`, `root:x`, error messages, blocked/forbidden indicators

Avoid unlabeled parallel curl requests — result attribution becomes confusing.

## Workflow

1. Open target with curl first.
2. Identify stack, title, hints, comments, links, forms, parameters.
3. Classify challenge type.
4. Use shortest likely payloads first.
5. If blocked, load the matching checklist skill.
6. Stop once flag is found and verified.
7. Provide concise recap.

## Escape Hatches

- If a direction fails after 3-5 attempts, switch approaches quickly.
- Do not get stuck in report-style analysis.
- For LFI challenges, load `web-ctf-lfi`.
- For SQLi challenges, load `sqli-sql-injection`.
- For SSRF challenges, load `ssrf-server-side-request-forgery`.
- For template injection, load `ssti-server-side-template-injection`.
- For upload challenges, load `upload-insecure-files`.
- For XSS challenges, load `xss-cross-site-scripting`.
