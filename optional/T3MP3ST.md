> **可选插件**：未安装 T3MP3ST 时跳过；主流水线不依赖本引擎。将 `{T3MP3ST_HOME}` 换成本机安装路径。

# T3MP3ST 集成手册（T3MP3ST.md）

> T3MP3ST = 多智能体攻击框架（本地路径 `{T3MP3ST_HOME}`，Node/TS，已构建），设计给 AI 编码代理当武器库。XBEN 基准 90.1% pass@1。AGPL-3.0，仅限授权测试。
> **角色分工：ZCode（本技能）= 大脑（假设、范围、纪律、报告）；T3MP3ST = 执行引擎 + 证据库 + 可视化。** 它不替代主流水线——单 agent recon/exploit 已验证，8 操作员蜂群尚未基准化，用作辅助。

## 1. 启动方式

```bash
cd {T3MP3ST_HOME}
npm run server        # War Room API+UI → http://127.0.0.1:3333/ui/（任务监控/证据库/OPSEC 面板）
npm run doctor        # 环境自检（nmap/nuclei 已识别；缺 dig/whois/semgrep 为可选项）
node dist/cli.js      # 交互式 CLI（4 种预设：标准/测试/隐蔽/激进）
```
keyless：无需 API key——由已连接的本地 agent 驱动；走 API 模式时 ZCode 直接 REST 调用（见下）。

## 2. 与本技能的四个集成点

### 2.1 授权门（阶段8 开打前，强制）
T3MP3ST 自带授权审批流，与我们的授权三层护栏对齐：
```
POST /api/approvals/authorize-target   # 目标授权登记（对应 scope.txt 核对结果）
GET  /api/approvals                    # 审批状态
```
**规则：未经 authorize-target 登记的目标，T3MP3ST 操作员不得对其发请求**——把我们的 scope.txt 内容登记进去再开任务。

### 2.2 阶段6 Triage 独立复核（最高价值）
```bash
node scripts/verify-finding.mjs        # 对单个 finding 做独立复现验证
```
nuclei/假设验证给出的 verified 发现，交它**二次验证**（独立引擎复核）——两套引擎都过的发现才进报告正文，误报率进一步下降。

### 2.3 阶段8 蜂群执行（可选，按假设逐条投喂）
把 assumption.md 的假设转成 mission（描述目标+假设），用 **createStealthOperation 预设**（= 我们的噪声纪律：限速、静默、低可检测性）。产物：
- Evidence Vault（findings/凭据/截图/HTTP 证据）→ 归档到 {output_dir}/findings/
- War Room 实时杀链可视化 → **给用户盯进度的驾驶舱**
- 注意：蜂群未基准化，单假设验证结果必须经阶段6 流程三态标注后才可信

### 2.4 报告与披露（阶段8 报告增强）
```bash
node scripts/disclosure-gen.mjs        # 生成协调披露报告草稿
```
作为阶段8 报告的附录素材；雷神/补天提交文案仍以我们的平台规则文件为准。

## 3. MCP 接入（可选）

MCP server（stdio）现仅暴露 `security_recon`（nmap/DNS/HTTP/指纹，每个发现可溯源到工具输出）。ZCode 侧配置 stdio MCP server 指向 `{T3MP3ST_HOME}\npm run mcp`（或 dist 入口）即可在对话里直接调用其侦察引擎。其余 pliny_* 工具已退役，勿配置。

## 4. 红线映射（不可违反）

| T3MP3ST 概念 | 本技能约束 |
|---|---|
| createStealthOperation 预设 | 全局纪律噪声纪律（默认必用；createAggressiveOperation **禁止**用于 SRC 单） |
| authorize-target 授权门 | 全局纪律1 范围三层护栏 + 授权时效 |
| Evidence Vault findings | 阶段6 三态标注后才可写报告 |
| credential:harvested 事件 | 凭据收获**只记录不利用**，SRC 红线优先 |

## 5. 已知短板（诚实）

- 8 操作员蜂群端到端利用未基准化——别指望"一键打穿"，把它的 operator 当带工具的执行单元
- 依赖 swarm 的 exploit/exploit 链是真实工具驱动但稳定性一般——**关键验证仍以我们的 curl/scdiff 亲自复现为准**
- 需要 node ≥18（已满足）；Web War Room 占 3333 端口
