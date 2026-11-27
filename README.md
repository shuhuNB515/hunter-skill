# hunter — 通用授权挖洞技能

让 AI 编码代理（Claude Code / Cursor / Codex / ZCode 等）以**渗透测试专家**而非扫描器的方式做授权测试（SRC / 众测 / Bug Bounty）。

## 味道

```
测绘采弹药（阶段 0–6）
    → 攻击面建模 + 假设清单（阶段 7）
    → hack 信号路由选类型 playbook（阶段 8）
    → pentest-quality-gate 出门
```

扫描器等洞出现；攻击者让洞现形。子技能弹药在 `skills/`，主流程在根 `SKILL.md`。

## 目录

| 路径 | 作用 |
|------|------|
| `SKILL.md` | 主入口：变量、纪律、阶段、路由/闸挂钩 |
| `HACKER_MINDSET.md` | 假设驱动心法 |
| `THREAT_KNOWLEDGE.md` | 红蓝白假设速查 |
| `PLAYBOOK.md` | 侦察 / JS 签名 / triage 实战手册 |
| `APP_PLAYBOOK.md` | App / 小程序，产物回灌主流水线 |
| `RULES_butian.md` | 平台规则可插拔示例 |
| `VULN_DB.md` | 组件 / CVE 笔记模板 |
| `config/variables.md` | 变量与产物约定 |
| `optional/` | WORKERS / T3MP3ST / 雷神等可选插件 |
| `skills/` | 类型 playbook + 旁线（CTF/AD/kernel/mobile…） |

## 安装

将本目录放入代理的技能目录，例如：

- Claude Code：`~/.claude/skills/hunter/`（或项目 `.claude/skills/hunter/`）
- 其它代理：按其 skill / prompt 目录约定放置，保持本目录结构完整

需要的常见 CLI（缺失时流程内提示安装）：`subfinder`、`httpx`、`katana`、`gau`、`nuclei`、`ffuf`、`gf`、`anew`；攻击阶段可选 `sqlmap`、`dalfox`、`interactsh-client`、`naabu`。

## 触发

对**已授权**目标说例如：

- 「对 example.com 做授权挖洞 / 资产收集 / 漏洞扫描」
- 「按 hunter 流水线测这个 SRC 范围」
- 「这是 CTF / 域控 / App 专项」→ 走旁线路由，不默认全量测绘

## 融合口令

```
阶段编排 → 听 SKILL.md
深入打点 → 听 skills/hack → 类型 playbook
出门交洞 → 必过 skills/pentest-quality-gate
平台红线 → RULES_<平台>.md（无则通用纪律）
旁线     → 默认不加载；点名或强信号才加载
```

## 与旧包关系

`bug-bounty-hunter-skill-master/hunter-skill` 为整合前对照源，本目录为独立通用包，互不覆盖。

## 授权声明

仅用于合法授权的安全测试。范围外零请求；只验证漏洞存在性，不做破坏性利用。使用者对自身行为负责。
