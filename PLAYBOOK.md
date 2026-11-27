# 挖掘手册（PLAYBOOK）v1.1

> 本文件由主对话维护，是子对话（bounty-recon / bounty-deepdive / bounty-scanner）的"挖掘方式"。
> 子对话开工前必读最新版；主对话每轮挖洞后把 worker 的经验反馈合并进来。
> 每节末尾注明更新日期；重复与过时条目会被主对话删除，保持精炼。

## 0. 铁律
- 范围外零请求；拿不准的资产先查 scope，宁可漏、不可越。
- **授权必须可指认（2026-09-26）**：scope 只来自平台项目资产清单/雷神 testRange/用户书面确认——"它像目标"不构成授权，推断授权=未授权；新发现子域默认范围外，核对平台清单或经用户确认后才可请求；CDN/共享 IP 不扫端口不直连（用域名 Host 访问）。
- 只验证漏洞存在性，不做利用升级；PoC 停在最小请求。
- **假设驱动 + 噪声纪律（2026-09-25）**：先写攻击假设再发请求；被动先行、认证/支付端点限速 ≤10、禁任何爆破；深测开工必读同目录 HACKER_MINDSET.md。
- 出现 429 / 封禁迹象立即把 -rl 降到 50 并记录 errors.log。
- 项目暂停/停止收洞时，同步暂停对该目标的主动测试（授权状态可能随项目状态变化），已发现归档待恢复后提交。
- **Token 成本排序（2026-09-14）**：CLI 批量命令（~0.5k/轮）＜ JS 静态分析（~1k/轮）＜ 浏览器 GUI 自动化（~5k/轮，a11y树+截图+焦点重试）。能用 curl/subfinder/grep 解决的绝不进浏览器；进浏览器前先写好完整脚本一次粘贴执行，禁止逐步交互；页面输出用 console.log+截图读，不用 copy/剪贴板往返。

## 1. 侦察技巧（2026-09-11）
- `subfinder -d 目标 -all -active`；API key 配在本机 subfinder `provider-config.yaml`（常见于用户配置目录下的 `subfinder/`；Shodan / Censys / VirusTotal / GitHub token，配完子域量通常翻倍）
- httpx 探活必带 `-td -title -sc -ip -cdn -fr`；CDN 命中但 IP 不在范围的资产降权
- 高价值关键词：login、sso、admin、api、graphql、swagger、console、jenkins、git-、vpn、internal
- 弱防护词单独加权（常年出洞）：staging、dev、uat、test、demo、pre、beta
- 存活资产 > 300 时，主动爬取只打 TOP300，其余靠 gau 被动

## 2. URL 与 JS 深挖（2026-09-11）
- gau（被动，量大先跑）∥ katana `-d 3 -jc -kf all`（-kf all 需要深度≥3，勿改 -d 3）
- JS 正文端点提取：绝对 URL `https?://[^"'[:space:]<>]+`；相对路径 `"(/[a-zA-Z0-9_\-\.]{2,}(/[a-zA-Z0-9_\-\.]+)+)"`，过滤 .css/.png/.jpg/.woff 等静态后缀
- 秘密关键词：`apikey|api_key|secret|token|password|bearer|AKIA[0-9A-Z]{16}|xox[baprs]-|ghp_[A-Za-z0-9]{36}|AIza[0-9A-Za-z_-]{35}`
- gf 命中只是参数候选（interesting_params.txt），供人工构造 payload，不自动攻击
- Git Bash 正则坑：模式含 `\.` 会被参数改写吞掉导致静默失配，URL 类模式一律用 `[.]` 代替；清单文件读入前先 `tr -d '\r'`（CRLF 会污染 URL）

## 2b. 前端签名体系破解方法论（2026-09-14，某IoT厂商+某医疗站双实证）
- **挖密钥**：下载站点全部 `_nuxt/*.js` chunk，grep `appSignKey|SecretKey|getHeaderInfo|interceptors.request`——密钥和算法几乎总在前端 bundle 里
- **验证签名层**：A/B 对比法——同接口先无签名头发一次、再带伪造签名头发一次，**对比错误码**：不同错误码 = 签名层被绕过（如 400→11006），相同 = 签名算法还没对
- **动态 import 大法（最优雅）**：`import("/web/_nuxt/xxx.js").then(m=>window.__mod=m)` 拿到模块导出后**直接调用页面自己的签名函数**（如 t.getHeaderInfo(url,method,data,cookie)）——比断点抓包快十倍，且生成的是 100% 正确的签名
- **错误码阶梯 = 鉴权分层地图**：400(无签名)→11006(签名过)→11012/11013(时间窗/会话层)→404(网关伪装)——每突破一层记录对应码，下一层的目标就明确
- **Copy as cURL 拿原始全貌**：DevTools Network 对目标请求右键 → 复制为 cURL(bash)——cookie/头/body 一次拿全，比逐个头看好用
- **nonce 格式陷阱**：同一站点可能有多套签名封装（62字符集32位 vs 时间戳前缀+hex 48位）——按接口逐一确认，不要假设全局统一
- **判定后必须测越权**：签名绕过本身常不算洞（服务端还有会话层），真正价值是用伪造签名+他人资源ID测归属校验（双自有账号互测，≤5组）

## 2c. 签名/加密逆向固化模板（2026-09-25，某IoT厂商/某医疗站沉淀——遇到签名站直接套，不再 ad-hoc）

**识别签名体系（开工先做，10分钟内出结论）**：
- 抓 3 个同接口不同参数的请求，对比 headers：出现 sign/signature/timestamp/nonce/X-Sign 类字段 = 签名层存在
- 双签名体系识别：headers 里同时有两组 sign 字段（或 cookie 签名 + header 签名并存）= 网关层 + 业务层各一套，必须逐层突破，错误码阶梯分别记录
- 加密 body 识别：请求 body 为 base64/hex 长串且每次变化 = 加密传输，先找密钥再谈重放

**webpack 动态 import 套路（首选，最优雅）**：
```js
// 1. 从 chunk 里定位签名模块：grep "appSignKey|getHeaderInfo|interceptors.request" *.js
// 2. DevTools console 动态 import 拿模块导出，直接调页面自己的签名函数：
import("/web/_nuxt/[chunk名].js").then(m => window.__sig = m);
// 3. 之后任意请求：window.__sig.getHeaderInfo(url, method, data, cookie) 生成 100% 正确签名
```
- 模块不是 ESM 时改用 `webpackChunk` 注入法：伪造一个 chunk push 进 `self.webpackChunkxxx` 数组，拿 `__webpack_require__` 后按模块 ID 取签名函数
- Vue/React SPA 的签名函数常挂在 axios 拦截器上：`window.__axios = axios实例` 后读 `interceptors.request.handlers[0].fulfilled.toString()`

**Frida hook 模板（App/加固场景，Web 拿不到时用）**：
```js
// Java 层通用 hook：打印所有 Cipher/Mac 的 init 与 doFinal，抓密钥和明文
Java.perform(function() {
  var Cipher = Java.use('javax.crypto.Cipher');
  Cipher.init.overload('int','java.security.Key').implementation = function(m, k) {
    console.log("[Cipher.init] mode=" + m + " algo=" + this.getAlgorithm() + " key=" + k.getEncoded());
    return this.init(m, k);
  };
  var Mac = Java.use('javax.crypto.Mac');
  Mac.doFinal.overload('[B').implementation = function(input) {
    var out = this.doFinal(input);
    console.log("[HMAC] in=" + bytesToHex(input) + " out=" + bytesToHex(out));
    return out;
  };
});
```
- HMAC plain 网格搜索法：hook 到密钥后，用明文候选（path、body、timestamp、nonce 的排列组合：`path+ts+nonce+body`、`method+path+body+ts` 等常见顺序）本地批量算 HMAC 对比密文，命中即为签名拼接顺序——某IoT厂商 plain 网格实测 ≤20 组合必命中
- Native 层（so 加固）：frida-trace 跟 `JNI_OnLoad` 与 `Java_*_native*`，配合 IDA/Ghidra 静态看；仅证明存在性，不深陷

**产物规范**：每个破解的签名站必须在 {output_dir}/07_manual/ 落 `sign_gen.py`（可复用签名生成器）+ `signature_notes.md`（算法、密钥来源、拼接顺序、双体系分层图），下次复测直接复用

## 3. nuclei 调优（2026-09-11）
- 模板集（单次运行挂全）：http/vulnerabilities + exposures + misconfiguration + takeovers + exposed-panels + default-logins
- 产物用 `-jle` JSONL（默认含 -irr 请求/响应证据）；加 `-es info -duc`
- 默认 `-rl 150 -c 25 -bs 25`；资产 > 500 或 WAF 严格：`-rl 50 -c 10`
- cves/ 类模板误报率高：复现前先核对模板声明的受影响版本
- 盲打类（SSRF/盲XSS）依赖 interactsh 回连，默认开启，勿加 -ni
- 外层 timeout 强杀 nuclei 会丢 -jle 产物（SIGTERM 时不落盘）：长扫描拆批跑，或事后从 stdout 日志按 `^\[模板ID\]` 行恢复结果（先 strip ANSI 色码）

## 4. Triage 纪律（2026-09-11）
- verified 判据：响应内容与模板匹配条件一致 + 二次复现成功
- unverified 不进报告正文，进附录并写明原因
- 修复建议按漏洞类别给通用方案，不臆测业务细节
- 报告中范围外资产只计数量、不列域名
- **发现必升级（2026-09-14）**：每个 verified 发现自问四连——能否越权影响他人？能否读改更敏感数据？能否组合成攻击链？业务危害一句话能否说清（"可遍历全站用户手机号"级别）？四连全否才算终点，否则继续深挖（深测模式）

## 5. 人工协同测试（2026-09-11）
- 手测输入来源：interesting_params.txt（gf 六模式命中）、api_endpoints.txt、unverified 发现、需登录态的功能面
- 默认 CLI 模拟 Burp：curl = Repeater、ffuf = Intruder（限速 ≤50 req/s）、browser-use 过登录态；产物落 07_manual/
- Burp **由用户负责启动**；主对话只协作已打开的 GUI（Repeater/Intruder/插件），不参与启动器与激活
- 人机共用代理：curl/ffuf 可加 `-x http://127.0.0.1:<Burp端口>`（常见 8080），请求进 Burp History，用户可随时接手
- 需要用户凭据/验证码/业务判断时：生成 07_manual/burp_tickets.md 工单交给用户，结果回填报告
- **登录态判定先行**：先分清子系统各自的技术栈与认证方式（JSP+httpOnly Cookie ≠ Vue+token 头），前端 JS 分析出的认证逻辑必须核对资源实际归属域，否则会提取一个不存在的凭证
- 浏览器 console 测试三板斧：①`copy()` 在 Promise 异步回调里不可用——结果存 window 变量再同步 copy；②焦点停在日志链接上时 Enter 会打开链接——用 a11y 元素定位「控制台提示」输入框；③httpOnly Cookie 拿不到也不要紧——登录标签内同源 `fetch()` 自动携带会话，可直接做同源接口测试
- Java 栈 API 常用 HTTP 200 包业务错误码：测鉴权必须看响应体 code 字段，只看状态码会把拦截误判成放行
- IDOR/越权类：先申请两个测试账号横向对比，不对真实他人数据操作；单账号时改 1-2 个相邻 ID 证明缺陷即停

## 5b. 平台提交经验（2026-09-14，某站被拒实证）
- **归属证明截图是硬门槛**：证据截图必须出现厂商名/备案主体（官网页脚、ICP备案、厂商 logo 与漏洞 URL 同框）——仅有域名=无法证明归属=直接拒收。正确做法：漏洞复现截图 + 官网首页（含厂商名）截图一起交
- **危害门槛**：单纯版本号/堆栈泄露类低危，补天不予收录——提交前先过"发现必升级四连问"，说不出业务危害就不交，避免留拒绝记录
- 被拒后平台明示"无需再次提交"的，记录 progress.md 防 AI 重复劳动

## 6. 经验回写区
（主对话每轮把 worker 的「经验反馈」合并到这里，格式：[日期][worker] 内容；每轮最多新增 3 条，重复与过时的删除）
- [2026-09-11][main] gf 是调用系统 grep 执行的，模式必须 POSIX ERE 语法（(?:...)、+? 会静默失配）；管道输入时 flags 用 -aoE 避免行号前缀污染。
- [2026-09-11][recon] httpx v1.10.0 的 -o / -j / -oa 文件输出全部静默失败（exit=0、无文件）：用 -silent 捕 stdout 落盘或 -json 后 grep 提取；探活加 -method GET 防 HEAD-500 站误杀（本轮 9/9 零误杀）。
- [2026-09-11][scanner] nuclei 长扫中目标 DNS 瞬时失败会把资产静默标记 unresponsive 并跳过——收工前必须核对 stdout 的 skipped 记录并补扫，9 资产的小目标也会发生（首轮即漏了 user/s 两个）。
- [2026-09-11][deepdive] katana -d 3 -jc -kf all 能从 JS 提取 subfinder 漏掉的子域与端点（首轮即发现 api.某公益SRC站 + 51 个 REST 端点）：阶段3 合并后必须把 URL 中的新子域回灌探活与扫描。

## 7. 第三方 SDK 凭据的可提交性判定（2026-09-26，某厂商案例 被忽略的教训）
- **SDK 初始化凭据（appKey/appSecret 仅用于 SDK init）默认不报**：业内普遍视为标准集成方式，审核方几乎必判忽略——哪怕配了 Base64 藏匿/实名场景/平台条目字面覆盖
- 报与不报的判定线：**该凭据能否独立调用出敏感接口/数据**（如高德 key 可直接调付费 API=可报；核身 SDK 的 init 配置，调用需完整业务流程+用户数据=不可报）
- 我方无第三方供应商授权时无法在线验证凭据有效性 → 危害无法闭环 → 天然卡死。不要赌"审核员会内部核实"
- LTAI 前缀类"疑似云凭据"的疑点不能单独撑起提交——内部核实不等于收录
- APK 四条 grep 主线照跑（端点/暴露组件仍有效），但"硬编码密钥"主线的命中物要先过上面判定线再定性
- **用户定案标准（2026-09-26）：编码/配置/凭据藏匿类默认不通过，必须有实际风险、可攻击的利用路径才提交**。"凭据泄露但未验证可利用"=不算漏洞
- **优先打"可实测攻击"的面**：暴露组件（exported 可实测拉起）、未授权 API（可实测响应）、IDOR（双账号可实测）——这类能在授权范围内完成危害闭环；检测时优先选能"当场证明"的方向

## 8. 攻击面分类模板（2026-09-25，配合 SKILL 阶段7 / HACKER_MINDSET 使用）
对每类入口，列出：具体端点/页面、所属子系统、**它信任什么输入**、应然的鉴权要求——"信任客户端"的每一处都是假设来源：
- **认证类**：登录/注册/找回/SSO/OAuth回调/验证码。标准怀疑：错误码差异=用户枚举；找回流程状态可跳步；回调 state 校验缺失
- **文件类**：上传/导入/导出/头像/附件预览。标准怀疑：类型校验在哪层、文件名入库、存储可否被解析、下载链接可否预测
- **富文本与模板**：评论/公告/邮件模板。标准怀疑：存储型二阶（谁还会渲染它）
- **资金与订单流**：下单/支付/退款/优惠券/余额。标准怀疑：状态机跳步/倒退、金额/数量边界值、竞态（红线内）
- **管理面**：admin/console/后台API。标准怀疑：JS 里有路由但入口 404（找真实路径）、弱口令默认口令、只藏不鉴权
- **内部与遗留接口**：JS 调用但前端未用、v1 旧版、App 专用。标准怀疑：新接口做了校验，老接口没有——同功能多版本逐个打
- **回调与集成**：webhook/支付回调/开放API。标准怀疑：签名是否可重放、来源 IP 是否真校验、金额是否信任回调体
- **新上线功能**：changelog/新版 App diff 出的新接口。标准怀疑：新=赶工期=校验不全，最高优先级
- **目标筛选新增"企业经营状态"检查（2026-09-27，哪吒汽车教训）**：破产/重整/停摆企业直接排除——无授权主体、无修复能力、无奖励，测试纯属法律风险。选目标前 30 秒搜一下"XX 2026 现状/销量/经营"，冷门≠僵尸
