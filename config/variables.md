# 变量约定

本技能所有路径与范围均通过变量表达，**禁止**写死个人家目录、桌面路径或某台机器上的绝对路径。

| 变量 | 含义 | 默认 / 示例 |
|------|------|-------------|
| `{target}` | 目标根域名或主资产标识 | `example.com` |
| `{output_dir}` | 本轮产物根目录 | `~/hunter/{target}` 或用户指定 |
| `{scope}` | 授权域名清单文件（每行一个域名） | `{output_dir}/scope.txt` |
| `{platform}` | 可选平台名；空=通用纪律 | `butian` / `leishen` / 空 |

## 产物子目录（相对 `{output_dir}`）

```
01_recon/    # 子域
02_probe/    # 探活与分诊
03_urls/     # URL / 参数候选
04_js/       # JS 与端点
05_scan/     # nuclei 等回归扫描
intel/       # 攻击面、假设、情报拼图
findings/    # 验证证据
report/      # 正式报告
07_manual/   # 会话、手测工单、签名脚本
08_app/      # App/小程序产物
```

## 平台规则文件

命名：`RULES_<平台>.md`，放在本技能根目录。用户指定平台且文件存在 → 开工必读；不存在 → 通用纪律。示例见根目录 `RULES_butian.md`。雷神等众测接入见 `optional/RULES_leishen.md`（可选插件，非主路必经）。

## 交付目录

若用户要求「桌面/指定目录放报告与截图」：复制 `{output_dir}/report/` 与证据到**用户指定的交付路径**。技能内不预设任何用户名下的 Desktop 路径。
