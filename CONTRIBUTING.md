# Contributing to hunter-skill

欢迎为 **hunter-skill** 贡献新的子技能（`skills/`）、平台规则（`RULES_<平台>.md`）或攻击面假设速查条目！

## 新增子技能规范

1. 在 `skills/<skill-name>/` 下创建目录并编写 `SKILL.md`（推荐包含 YAML frontmatter 与清晰的触发信号、验证步骤及质量门禁）。
2. 提交前运行本地校验脚本：
   ```bash
   python3 scripts/validate_skills.py
   ```
3. 严禁提交任何真实目标的未脱敏敏感信息、Cookie、Token 或私有 API Key。
