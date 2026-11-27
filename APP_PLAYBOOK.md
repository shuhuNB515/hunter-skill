# App/小程序 攻击面 Playbook（APP_PLAYBOOK.md）

> 金融/银行/车企/ IoT 的主战场在 App 和小程序，Web 只是冰山一角。目标提供 App 或小程序时，本 playbook 与 SKILL.md 主流水线并行执行，产物落 {output_dir}/08_app/。
> 红线继承 SKILL.md 全局纪律：只验证存在性、不做破坏性利用、越权测试用双自有账号 ≤5 组。

## 阶段 A：样本获取

1. **APK 下载**：优先官网/应用商店直链；花瓣/豌豆荚等聚合源备用。落 {output_dir}/08_app/sample.apk，记录版本号与下载时间（后续 diff 用）。
2. **小程序包获取**：
   - 微信：Android `data/com.tencent.mm/MicroMsg/{用户id}/appbrand/pkg/` 下 `__APP__.wxapkg`（需 root 或已备份）；PC 端微信小程序缓存在 `%APPDATA%\Tencent\WeChat\WXApplet`（版本相关）
   - 解包工具：`unveilr` / `wxappUnpacker`（node 版），解出 app-service.js 与各页面 js
3. **版本 diff 意识**：同一目标的新版本 APK 下来后先 `jadx` 对比新旧资源，新增接口/新增密钥优先看。

## 阶段 B：静态侦察（jadx）

```bash
# 反编译（缺失先装：jadx release 解压即用，需 JDK）
jadx -d {output_dir}/08_app/jadx_out sample.apk --no-res -j 4
# 资源/manifest 单独出（看权限、exported 组件、deep links）
jadx -d {output_dir}/08_app/jadx_res sample.apk --no-src
```

四条 grep 主线（命中即候选，逐条人工复核）：
0. **apkleaks 自动密钥提取（先跑）**：`apkleaks -f sample.apk -o {output_dir}/08_app/apkleaks.txt`（内置正则覆盖 AWS/GCP/Firebase/云 AK 等；结果按 PLAYBOOK 第7节"SDK 凭据可提交性判定线"过滤——能独立调用出敏感接口的才立假设）
1. **API 端点**：`grep -rE "https?://[a-zA-Z0-9./_-]+" jadx_out/sources` → 汇总 api_endpoints_app.txt；域名可回灌 SKILL.md 阶段1 做子域补充
2. **硬编码密钥**：`grep -rE "(api[_-]?key|app[_-]?secret|access[_-]?token|-----BEGIN)" ` + 高熵字符串扫描；金融 App 硬编码密钥/内置证书是稳定出洞点（同上先过判定线）
3. **加密逻辑定位**：`grep -rE "javax.crypto|Cipher.getInstance|HmacSHA|AES/CBC" ` → 签名/加密函数定位后转阶段 C 动态 hook；同时把加密相关类名记入 signature_notes.md
4. **暴露组件**：从 AndroidManifest 看 `exported=true` 的 activity/service/receiver、`deeplink` scheme——可被外部拉起的组件逐个测（intent 重定向、越权拉起）

小程序静态侦察同理：解包后的 `app-service.js` 里 grep 域名、key、`wx.request` 封装（签名逻辑常在这里）。

## 阶段 C：动态 hook（frida）

前置：设备 root/越权 或 用 frida-gadget 重打包（`objection patchapk` 一条命令）。

```bash
# 缺失先装：pip install frida-tools；设备端 frida-server 版本必须与 PC 端一致
frida-ps -U                      # 确认设备连接
frida -U -f <包名> -l hook.js --no-pause
objection -g <包名> explore      # 交互式，免写脚本快速排障
```

hook 脚本模板直接复用 PLAYBOOK.md 2c 节（Cipher/Mac 通用 hook、HMAC 网格搜索）。App 场景额外加：
- **SSL Pinning 绕过**：`objection -g 包名 android sslpinning-disable` 首选；失败再上 Frida CodeShare 的 universal pinning 脚本。之后 Burp/mitmproxy 挂 127.0.0.1:8080 看明文流量
- **根检测/加固绕过**：仅以"能跑起来"为限，不做脱壳深挖（投入产出比低，Web+API 面通常已够）

## 阶段 D：回灌主流水线（关键衔接）

App 挖出的所有 API 端点、域名、密钥**必须回灌**：
- 端点 → 合入 {output_dir}/03_urls/all_urls.txt 与 04_js/api_endpoints.txt（gf 分诊、nuclei 扫描照常）
- 域名 → 回灌 01_recon 补 subfinder/httpx
- 抓到的签名算法 → 按 PLAYBOOK 2c 产物规范落 sign_gen.py，之后的 API 测试（越权/参数篡改）用伪造签名打
- 测试重心：App API 的**服务端校验缺失**（客户端校验可绕 = App 特有洞：本地校验支付状态、客户端加密当安全边界、越权拉起组件）

## 工具自检（阶段 A 前执行）

`jadx`、`frida-tools`（pip）、`objection`（pip）、unveilr（小程序解包）。缺失时的安装见各节说明；jadx 从 GitHub release 下载，若环境需 HTTP 代理则使用用户本机已有代理。
