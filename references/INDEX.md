# References Index

> 🤖 此文件由 development 框架维护，AI 在需要时可据此定位具体参考文档。
>
> **结构说明**：所有文档平铺在 `docs/` 目录下，分类由文档 frontmatter 中的 `tags` 字段声明。
> 标签注册表见 [TAGS.md](TAGS.md)，质量门规范见 [QUALITY_GATE.md](QUALITY_GATE.md)。
>
> 🗺️ **知识图谱入口**：每个领域有对应的 MoC（内容地图）文件，通过 `[[wiki links]]` 组织：
> - [[_moc_toolchain]] · [[_moc_ios]] · [[_moc_android]] · [[_moc_flutter]] · [[_moc_react-native]]
> - [[_moc_wechat]] · [[_moc_miniprogram]] · [[_moc_frontend]] · [[_moc_canvas]]
> - [[_moc_graphics]] · [[_moc_design-system]] · [[_moc_ml]] · [[_moc_network]]

---

## 工具链（tags: toolchain, coding-principles）

| 文件                                    | 内容                                             | Tags              | Keywords                                     |
| --------------------------------------- | ------------------------------------------------ | ----------------- | -------------------------------------------- |
| `docs/toolchain_ai-toolchain.md`        | AI 工具链配置与使用习惯                          | toolchain         | AI 工具链参考, ai toolchain, toolchain       |
| `docs/coding-principles_methodology.md` | 好项目方法论（可读性/设计模式/性能/安全/AI协作） | coding-principles | 好项目方法论, methodology, coding-principles |

→ MoC: [[_moc_toolchain]]

## 跨平台（tags: cross-platform）

| 文件                                           | 内容                        | Tags           | Keywords                                                     |
| ---------------------------------------------- | --------------------------- | -------------- | ------------------------------------------------------------ |
| `docs/cross-platform_vscode-vs-claude-code.md` | VS Code vs Claude Code 对比 | cross-platform | vscode-vs-claude-code, vscode vs claude code, cross-platform |
| `docs/cross-platform_bids-cognitive-stroop.md` | BIDS 数据标准化导出与 Stroop 认知指标计算规范 | cross-platform, flutter, architecture, coding-principles | BIDS sidecar, BIDS standard, Stroop Interference, Post-Error Slowing, Inverse Efficiency Score, Delta Score, Flutter Unit Testing |

## iOS / Swift / SwiftUI / UIKit（tags: ios）

| 文件                                    | 内容                                                | Tags | Keywords                                                  |
| --------------------------------------- | --------------------------------------------------- | ---- | --------------------------------------------------------- |
| `docs/ios_swift-coding-standards.md`    | Swift 编码规范                                      | ios  | swift-coding-standards, swift coding standards, ios       |
| `docs/ios_swiftui-design-guidelines.md` | SwiftUI 设计指南                                    | ios  | swiftui-design-guidelines, swiftui design guidelines, ios |
| `docs/ios_uikit-components.md`          | UIKit 组件参考                                      | ios  | uikit-components, uikit components, ios                   |
| `docs/ios_layout-system.md`             | 布局系统（SwiftUI Layout / Auto Layout）            | ios  | layout-system, layout system, ios                         |
| `docs/ios_navigation-patterns.md`       | 导航模式（NavigationStack / TabView / Coordinator） | ios  | navigation-patterns, navigation patterns, ios             |
| `docs/ios_graphics-animation.md`        | 图形与动画（Canvas / Lottie / PhaseAnimator）       | ios  | graphics-animation, graphics animation, ios               |
| `docs/ios_metal-shader.md`              | Metal Shader 参考                                   | ios  | metal-shader, metal shader, ios                           |
| `docs/ios_system-integration.md`        | 系统集成（HealthKit / WidgetKit / App Intents）     | ios  | system-integration, system integration, ios               |
| `docs/ios_accessibility.md`             | 无障碍（VoiceOver / Dynamic Type）                  | ios  | accessibility, ios                                        |
→ MoC: [[_moc_ios]]

## Android / Kotlin / Jetpack Compose（tags: android）

| 文件                                      | 内容                                 | Tags    | Keywords                                                  |
| ----------------------------------------- | ------------------------------------ | ------- | --------------------------------------------------------- |
| `docs/android_design-style-guide.md`      | 设计风格指南                         | android | design-style-guide, design style guide, android           |
| `docs/android_visual-design.md`           | 视觉设计规范                         | android | visual-design, visual design, android                     |
| `docs/android_adaptive-screens.md`        | 自适应屏幕（折叠屏 / 平板 / 多窗口） | android | adaptive-screens, adaptive screens, android               |
| `docs/android_motion-system.md`           | 动效系统（SharedElement / Lottie）   | android | motion-system, motion system, android                     |
| `docs/android_functional-requirements.md` | 功能需求规范                         | android | functional-requirements, functional requirements, android |
| `docs/android_performance-stability.md`   | 性能与稳定性                         | android | performance-stability, performance stability, android     |
| `docs/android_privacy-security.md`        | 隐私与安全                           | android | privacy-security, privacy security, android               |
| `docs/android_accessibility.md`           | 无障碍指南                           | android | accessibility, android                                    |
| `docs/android_testing.md`                 | 测试                                 | android | testing, android                                          |
→ MoC: [[_moc_android]]

## Flutter / Dart（tags: flutter）

| 文件                                  | 内容                                          | Tags    | Keywords                     |
| ------------------------------------- | --------------------------------------------- | ------- | ---------------------------- |
| `docs/flutter_project-structure.md`   | 项目结构规范                                  | flutter | project structure, flutter   |
| `docs/flutter_widget-patterns.md`     | Widget 最佳实践（const 优化、响应式、Sliver） | flutter | widget patterns, flutter     |
| `docs/flutter_riverpod-state.md`      | Riverpod 2.0 状态管理                         | flutter | riverpod state, flutter      |
| `docs/flutter_bloc-state.md`          | Bloc/Cubit 状态管理模式                       | flutter | bloc state, flutter          |
| `docs/flutter_gorouter-navigation.md` | GoRouter 导航与路由                           | flutter | gorouter navigation, flutter |
| `docs/flutter_forms.md`               | 表单处理与验证                                | flutter | forms, flutter               |
| `docs/flutter_networking.md`          | 网络请求（Dio、错误处理、拦截器）             | flutter | networking, flutter          |
| `docs/flutter_localization.md`        | 国际化 / 多语言支持                           | flutter | localization, flutter        |
| `docs/flutter_animations.md`          | 动画与动效                                    | flutter | animations, flutter          |
| `docs/flutter_performance.md`         | 性能优化（渲染、内存、启动）                  | flutter | performance, flutter         |
| `docs/flutter_platform-specific.md`   | 平台集成（原生通道、权限）                    | flutter | platform specific, flutter   |
| `docs/flutter_testing.md`             | 测试策略（Unit / Widget / Integration）       | flutter | testing, flutter             |
→ MoC: [[_moc_flutter]]

## React Native / Expo（tags: react-native）

| 文件                                       | 内容                                          | Tags         | Keywords                                               |
| ------------------------------------------ | --------------------------------------------- | ------------ | ------------------------------------------------------ |
| `docs/react-native_components.md`          | 组件参考                                      | react-native | components, react-native                               |
| `docs/react-native_styling.md`             | 样式方案（StyleSheet / Tailwind / Unistyles） | react-native | styling, react-native                                  |
| `docs/react-native_navigation.md`          | 导航（React Navigation / Expo Router）        | react-native | navigation, react-native                               |
| `docs/react-native_state-management.md`    | 状态管理                                      | react-native | state-management, state management, react-native       |
| `docs/react-native_forms.md`               | 表单处理                                      | react-native | forms, react-native                                    |
| `docs/react-native_networking.md`          | 网络请求                                      | react-native | networking, react-native                               |
| `docs/react-native_animations.md`          | 动画（Animated / Reanimated / Lottie）        | react-native | animations, react-native                               |
| `docs/react-native_native-capabilities.md` | 原生能力（相机 / 推送 / 蓝牙）                | react-native | native-capabilities, native capabilities, react-native |
| `docs/react-native_performance.md`         | 性能优化                                      | react-native | performance, react-native                              |
| `docs/react-native_testing.md`             | 测试                                          | react-native | testing, react-native                                  |
| `docs/react-native_engineering.md`         | 工程化                                        | react-native | engineering, react-native                              |
→ MoC: [[_moc_react-native]]

## Web Canvas 系列（tags: web, canvas）

| 文件                                    | 内容                                                   | Tags                                         | Keywords                                                                                                                                                           |
| --------------------------------------- | ------------------------------------------------------ | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `docs/web_canvas-2d-drawing.md`         | Canvas 2D 绘图核心技术：形状/样式/变换/合成/文本/图像/像素/动画/OffscreenCanvas/性能优化 | web, canvas, graphics, performance, animation | Canvas API, HTML Canvas, 2D绘图, Canvas 2D context, 坐标变换, OffscreenCanvas, Path2D, requestAnimationFrame, canvas performance |
| `docs/web_canvas-advanced-architecture.md` | 生产级 Canvas 应用架构：场景图/脏标记/图层缓存/Build-Layout-Paint-Composite 管线/差分更新/帧调度 | web, canvas, architecture, rendering-pipeline, scene-graph | Canvas 架构, 场景图 Scene Graph, 差分渲染 diff rendering, dirty rect, 渲染管线, Canvas布局引擎, 保留模式 retained mode, Flutter rendering pipeline |
| `docs/web_canvas-interaction.md`         | Canvas 交互系统：坐标转换/事件代理/离屏HitCanvas/拖拽/文本输入(隐藏DOM+IME)/光标管理/键盘导航 | web, canvas, interaction, event-system, hit-testing | Canvas 交互, hit testing, Canvas 事件系统, Canvas 点击检测, Canvas 拖拽, Canvas 文本输入, Konva 事件, Fabric.js 交互 |
| `docs/web_canvas-ui-frameworks.md`       | Canvas 全渲染 UI 框架：egui/Dear ImGui 即时模式/Flutter CanvasKit 保留模式/Vello GPU渲染/WASM方案对比 | web, canvas, ui-framework, imgui, wasm | Canvas UI, 全Canvas渲染, 无DOM界面, immediate mode GUI, Dear ImGui, egui, Flutter CanvasKit, Vello, WASM UI |
| `docs/web_html-in-canvas.md`             | HTML-in-Canvas 技术体系：html2canvas/CSS Painting API (Houdini)/SVG foreignObject/跨域安全策略 | web, canvas, html2canvas, css-houdini, svg | HTML-in-Canvas, html2canvas, DOM to Canvas, CSS Painting API, CSS Houdini, SVG foreignObject, Canvas 渲染HTML, cross-origin canvas |
→ MoC: [[_moc_canvas]]

## 微信小程序（tags: miniprogram, wechat）

| 文件                                          | 内容                                 | Tags                   | Keywords                                                                                          |
| --------------------------------------------- | ------------------------------------ | ---------------------- | ------------------------------------------------------------------------------------------------- |
| `docs/miniprogram_wechat-native-dev.md`       | 小程序原生开发入门：双线程架构、WXML/WXSS/JS、生命周期、API体系 | miniprogram, wechat, frontend | 微信小程序, 小程序原生开发, WeChat Mini Program, WXML, WXSS, miniprogram native, rpx, 双线程模型 |
| `docs/miniprogram_wepy-framework-analysis.md` | WePY 框架技术分析：已归档状态、核心特性、workspace 使用情况、迁移路径 | miniprogram, wechat, frontend, wepy | WePY, 微信小程序框架, wepy框架, 小程序组件化, wepy vs uni-app, WeChat Mini Program Framework |
| `docs/wechat_getting_started.md`              | 入门指南                             | wechat                 | getting_started, wechat                                                                           |
| `docs/wechat_framework.md`                    | 小程序框架（WXML / WXSS / WXS）      | wechat                 | framework, wechat                                                                                 |
| `docs/wechat_components.md`                   | 组件参考                             | wechat                 | components, wechat                                                                                |
| `docs/wechat_api.md`                          | API 参考                             | wechat                 | api, wechat                                                                                       |
| `docs/wechat_cloud.md`                        | 云开发                               | wechat                 | cloud, wechat                                                                                     |
| `docs/wechat_reference.md`                    | 参考文档汇总                         | wechat                 | reference, wechat                                                                                 |
| `docs/wechat_other.md`                        | 其他主题                             | wechat                 | other, wechat                                                                                     |
| `docs/wechat_index.md`                        | 文档索引入口                         | wechat                 | index, wechat                                                                                     |
→ MoC: [[_moc_wechat]]

## uni-app / 支付宝小程序（tags: miniprogram, uni-app, alipay, vue, cross-platform）

| 文件                                          | 内容                                                     | Tags                              | Keywords                                                                                          |
| --------------------------------------------- | -------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------- |
| `docs/miniprogram_uni-app-development.md`     | uni-app 跨平台框架：编译器+运行时架构、工程结构、pages.json、条件编译、小程序自定义组件、uni.request API | miniprogram, uni-app, cross-platform, vue, frontend | uni-app, 小程序开发, 跨平台, 微信小程序, Vue, pages.json, 条件编译, uni.request, HBuilderX |
| `docs/miniprogram_uni-app-engineering.md`     | uni-app 3.0 工程化实践：pages.json 官方验证、easycom、unplugin-auto-import、Pinia、UnoCSS 适配、分包策略 | miniprogram, uni-app, frontend, vue | uni-app, uni-app 3.0, Vue3, Vite, pages.json, easycom, Pinia, unplugin-auto-import, 条件编译, subpackage |
| `docs/miniprogram_alipay-development.md`      | 支付宝小程序：自研vs第三方开发模式、AXML/ACSS/JS框架架构、文件结构、逻辑层视图层、数据绑定 | miniprogram, alipay, frontend       | 支付宝小程序, Alipay Mini Program, AXML, ACSS, 自研开发, 第三方开发, 商家授权, 蚂蚁集团 |
| `docs/miniprogram_batch-express-delivery.md`   | 批量寄件（ComponentCreationMultiple）架构分析：支付枚举(6种)/同步批量下单/异步改造/双副本差异 | miniprogram, wechat, vue, uni-app | 批量寄件, batch express, ComponentCreationMultiple, 支付方式, batchCreate, FooterCard, 信用支付 |
→ MoC: [[_moc_miniprogram]]

## 抖音小程序（tags: miniprogram, douyin, frontend）

| 文件                                          | 内容                                                     | Tags                              | Keywords                                                                                          |
| --------------------------------------------- | -------------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------- |
| `docs/miniprogram_douyin-development.md`      | 抖音小程序开发入门：平台概述、四层双线程架构、TTML/TTSS、生命周期与setData、JS API体系、组件系统、Web差异 | miniprogram, douyin, frontend      | 抖音小程序, Douyin mini program, TTML, TTSS, setData, rpx, 字节小程序, 开放平台 |

## Web 前端 / React / Ant Design（tags: frontend, react, antd）

| 文件                                     | 内容                                   | Tags               | Keywords                                               |
| ---------------------------------------- | -------------------------------------- | ------------------ | ------------------------------------------------------ |
| `docs/frontend_motion-recipes.md`        | 动效配方（CSS / Framer Motion / GSAP） | frontend           | motion-recipes, motion recipes, frontend               |
| `docs/frontend_asset-prompt-guide.md`    | AI 资产生成 Prompt 工程指南            | frontend           | asset-prompt-guide, asset prompt guide, frontend       |
| `docs/frontend_env-setup.md`             | 环境配置入门                           | frontend           | env-setup, env setup, frontend                         |
| `docs/frontend_minimax-cli-reference.md` | MiniMax CLI 参考                       | frontend           | minimax-cli-reference, minimax cli reference, frontend |
| `docs/frontend_minimax-image-guide.md`   | MiniMax 图片生成指南                   | frontend           | minimax-image-guide, minimax image guide, frontend     |
| `docs/frontend_minimax-music-guide.md`   | MiniMax 音乐生成指南                   | frontend           | minimax-music-guide, minimax music guide, frontend     |
| `docs/frontend_minimax-tts-guide.md`     | MiniMax TTS 语音合成指南               | frontend           | minimax-tts-guide, minimax tts guide, frontend         |
| `docs/frontend_minimax-video-guide.md`   | MiniMax 视频生成指南                   | frontend           | minimax-video-guide, minimax video guide, frontend     |
| `docs/frontend_minimax-voice-catalog.md` | MiniMax 音色目录                       | frontend           | minimax-voice-catalog, minimax voice catalog, frontend |
| `docs/frontend_troubleshooting.md`       | 疑难排查                               | frontend           | troubleshooting, frontend                              |
| `docs/frontend_security.md`              | XSS / CSRF / CSP / 安全标头综合指南    | frontend, security | 前端安全, frontend security, XSS, CSRF, CSP, OWASP     |
| `docs/frontend_antd-ecosystem-workspace.md` | Ant Design 生态系统实践：v4→v5→v6 版本演进、workspace 使用情况、升级路径 | frontend, react, antd, design-system | Ant Design, antd, React UI组件库, CSS-in-JS, Ant Design Pro, ProComponents, AntV |
→ MoC: [[_moc_frontend]]

## 架构与系统设计（tags: architecture, filesystem, event-driven, macos, nodejs, automation, shell）

| 文件                                              | 内容                                                                                                            | Tags                                           | Keywords                                                                                                            |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `docs/architecture_filesystem-event-pipeline.md`  | 文件系统事件监听与触发管道设计：FSEvents/chokidar/事件总线/shell hook/launchd/cron | architecture, filesystem, event-driven, macos, nodejs, automation, shell | FSEvents, chokidar, 文件系统监听, 事件驱动架构, event bus, 事件总线, launchd, shell hook, trigger pipeline, 触发管道 |

## 品牌设计系统（tags: design-system）

| 文件                                                   | 内容                  | Tags          | Keywords                                           |
| ------------------------------------------------------ | --------------------- | ------------- | -------------------------------------------------- |
| `docs/design-system_figma.md`                          | Figma 品牌设计系统    | design-system | figma 品牌设计系统, figma, design-system           |
| `docs/design-system_apple.md`                          | Apple 品牌设计系统    | design-system | apple 品牌设计系统, apple, design-system           |
| `docs/design-system_stripe.md`                         | Stripe 品牌设计系统   | design-system | stripe 品牌设计系统, stripe, design-system         |
| `docs/design-system_vercel.md`                         | Vercel 品牌设计系统   | design-system | vercel 品牌设计系统, vercel, design-system         |
| `docs/design-system_linear.app.md`                     | Linear 品牌设计系统   | design-system | linear.app 品牌设计系统, linear.app, design-system |
| `docs/design-system_notion.md`                         | Notion 品牌设计系统   | design-system | notion 品牌设计系统, notion, design-system         |
| `docs/design-system_airbnb.md`                         | Airbnb 品牌设计系统   | design-system | airbnb 品牌设计系统, airbnb, design-system         |
| `docs/design-system_supabase.md`                       | Supabase 品牌设计系统 | design-system | supabase 品牌设计系统, supabase, design-system     |
| （共 54 个品牌，完整列表见 `docs/design-system_*.md`） | —                     |
→ MoC: [[_moc_design-system]]

## TDesign 组件库（tags: tdesign）

> tdesign 保留嵌套目录结构（组件数量多，层级深）。完整列表见 `docs/tdesign/` 目录。

| 路径                             | 内容                               | Tags                      | Keywords |
| -------------------------------- | ---------------------------------- | ------------------------- | -------- |
| `docs/tdesign/miniprogram/`      | 小程序组件文档（5 概览 + 58 组件） | tdesign, miniprogram      | —        |
| `docs/tdesign/miniprogram-chat/` | Chat 组件文档（2 概览 + 9 组件）   | tdesign, miniprogram-chat | —        |

---

## API 集成与后端架构（tags: api, backend, data-validation, resilience, payment, middleware）

| 文件                                                   | 内容                   | Tags                                                                         | Keywords                                                                                                                                                                 |
| ------------------------------------------------------ | ---------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `docs/api_third-party-data-validation-strategies.md`   | 第三方数据校验策略体系 | api, backend, data-validation, resilience, security, payment, middleware     | 第三方数据校验, third-party data validation, API集成, 幂等性, 熔断, 重试, 对账, Schema校验, 安全, 支付回调, webhook签名验证, 中间层平台 |

---

## 索引统计

| Tag               | 文件数 | Keywords |
| ----------------- | ------ | -------- |
| toolchain         | 1      | —        |
| coding-principles | 1      | —        |
| cross-platform    | 2      | —        |
| ios               | 9      | —        |
| android           | 9      | —        |
| flutter           | 12     | —        |
| react-native      | 11     | —        |
| miniprogram       | 3      | —        |
| douyin            | 1      | —        |
| wechat            | 10     | —        |
| frontend          | 14     | —        |
| design-system     | 55     | —        |
| tdesign           | 74     | —        |
| graphics          | 9      | —        |
| rendering         | 9      | —        |
| ray-tracing       | 2      | —        |
| machine-learning  | 2      | —        |
| algorithm         | 3      | —        |
| network           | 2      | —        |
| security          | 2      | —        |
| lighting          | 2      | —        |
| gpu               | 3      | —        |
| learning-path     | 1      | —        |
| architecture      | 1      | —        |
| filesystem        | 1      | —        |
| event-driven      | 1      | —        |
| macos             | 1      | —        |
| nodejs            | 1      | —        |
| automation        | 1      | —        |
| shell             | 1      | —        |
| uni-app           | 1      | —        |
| vue               | 1      | —        |
| alipay            | 1      | —        |
| react             | 1      | —        |
| antd              | 1      | —        |
| wepy              | 1      | —        |
| web               | 5      | —        |
| canvas            | 5      | —        |
| performance       | 0      | —        |
| animation         | 0      | —        |
| rendering-pipeline | 1     | —        |
| scene-graph       | 1      | —        |
| interaction       | 1      | —        |
| event-system      | 1      | —        |
| hit-testing       | 1      | —        |
| ui-framework      | 1      | —        |
| imgui             | 1      | —        |
| wasm              | 1      | —        |
| html2canvas       | 1      | —        |
| css-houdini       | 1      | —        |
| svg               | 1      | —        |
| api               | 1      | —        |
| backend           | 1      | —        |
| data-validation   | 1      | —        |
| resilience        | 1      | —        |
| payment           | 1      | —        |
| middleware         | 1      | —        |
| **总计**          | **223** | —        |

## 领域知识 / 计算机图形学（tags: graphics, rendering, ray-tracing, lighting, gpu）

| 文件                                                 | 内容                                                                                                  | Tags                               | Keywords                                                                                    |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------- |
| `docs/graphics_ray-tracing.md`                       | 光线追踪算法：Ray Casting → Whitted → Path Tracing → BDPT → MLT，含加速结构与降噪                     | graphics, rendering, ray-tracing   | 光线追踪算法概述, ray tracing, graphics, rendering, ray-tracing                             |
| `docs/graphics_raytracing-practice.md`               | 光线追踪实践：TinyRayTracer 256行实现、PBRT v4 新增内容、渲染方程、Möller-Trumbore 求交               | graphics, rendering, ray-tracing   | 光线追踪实践, TinyRayTracer, PBRT, 路径追踪, BVH, ray tracing                               |
| `docs/graphics_lighting.md`                          | 实时渲染光照：阴影映射/环境光遮蔽/全局光照近似（Lightmap/Light Probe/SSGI/Radiosity）/Unreal 4 帧流程 | graphics, rendering, lighting      | 实时渲染光照, 全局光照, global illumination, lighting, shadow mapping, SSAO, lightmap       |
| `docs/graphics_pbr-materials.md`                     | PBR 着色与材质：Cook-Torrance 微面元 BRDF、GGX、Fresnel、金属度工作流、Disney BSDF、次表面散射        | graphics, rendering, lighting      | PBR, BRDF, 微面元理论, microfacet, GGX, Fresnel, metallic-roughness, Disney BSDF            |
| `docs/graphics_pipeline.md`                          | 图形渲染管线：GPU 架构/命令处理器/D3D11 管线/顶点管线/光栅化（Pineda 算法）/Early-Z Hi-Z 优化         | graphics, rendering, gpu           | 图形渲染管线, graphics pipeline, GPU 架构, rasterization, vertex shader, gpu                |
| `docs/graphics_visibility-rasterization-practice.md` | 渲染管线补充：可见性问题两种范式对比、离散化困境、TinyRenderer 实践路线图、Z-Buffer/重心坐标          | graphics, rendering, gpu           | 可见性问题, visibility, TinyRenderer, Z-buffer, rasterization, 光栅化                       |
| `docs/graphics_mathematics.md`                       | CG 数学基础：点积/叉积、齐次坐标、MVP 变换链、透视投影矩阵、四元数与 SLERP、重心坐标                  | graphics, rendering                | 线性代数, linear algebra, 矩阵变换, 透视投影, 四元数, quaternion, 重心坐标                  |
| `docs/graphics_api-intro.md`                         | 现代图形 API 入门：WebGL2 Hello World、GLSL 速览、纹理、学习路径、常见陷阱                            | graphics, rendering, gpu           | WebGL2, OpenGL, GLSL, shader, 图形 API, graphics API, Vulkan, Metal                         |
| `docs/graphics_learning-path.md`                     | CG 学习路径与书单推荐：六阶段路线图、核心书单速查、KB 文档交叉引用、资源难度/免费标注                 | graphics, rendering, learning-path | 计算机图形学学习路径, CG learning path, 书单推荐, book recommendations, 学习路线图, roadmap |
→ MoC: [[_moc_graphics]]

## 机器学习（tags: machine-learning, algorithm）

| 文件                                         | 内容                                                                                                       | Tags                        | Keywords                                                                                                                                                                                              |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/general_naive-bayes.md`                | 朴素贝叶斯算法详解：贝叶斯定理、条件独立性、三种变体、拉普拉斯平滑                                         | machine-learning, algorithm | naive bayes, machine-learning, algorithm                                                                                                                                                              |
| `docs/general_residuals-gradient-descent.md` | 残差、平均残差与梯度下降：残差定义与诊断、平均残差的零与非零场景、梯度下降更新规则与三种变体、三者串联图景 | machine-learning, algorithm | 残差, residual, 平均残差, mean residual, 梯度下降, gradient descent, SGD, BGD, mini-batch, 损失函数, loss function, MSE, 回归分析, regression analysis, 优化算法, optimization, 学习率, learning rate |
| `docs/algorithm_shortest-path.md`            | 最短路径算法：Dijkstra / Bellman-Ford / Floyd-Warshall / A\\* 优劣对比与选型决策                            | algorithm                   | 最短路径, shortest path, Dijkstra, Bellman-Ford, Floyd-Warshall, A\\*算法, 图论, graph theory, 路径规划, pathfinding, 启发式搜索, heuristic search, 负权边, negative weight edge                       |
→ MoC: [[_moc_ml]]

## 网络协议与安全（tags: network）

| 文件                                   | 内容                                                                     | Tags    | Keywords                                                                                                                                                    |
| -------------------------------------- | ------------------------------------------------------------------------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docs/network_arp-security.md`         | ARP 协议原理与 ARP 欺骗防护（DAI/静态ARP/加密/TLS/IPv6 SEND）            | network | ARP, 地址解析协议, ARP spoofing, ARP 欺骗, DAI, 动态 ARP 检测, static ARP, 中间人攻击, MITM, DHCP snooping, 端口安全, ARP cache poisoning, network security |
| `docs/network_fingerprinting-proxy.md` | 网络指纹双向校验（JA3/JA4/SSL Pinning）+ 抖音/字节系代理转发失败原因分析 | network | 网络指纹, JA3, JA4, TLS fingerprint, SSL Pinning, 证书固定, 代理转发, proxy bypass, mitmproxy, Charles, 抓包失败, cronet, 抖音, 中间人检测, anti-proxy      |
→ MoC: [[_moc_network]]

## 品牌设计系统（参考）

| `design-systems/figma.md` | Figma | — |
| `design-systems/notion.md` | Notion | — |
| `design-systems/github.md` | GitHub | — |
| `design-systems/supabase.md` | Supabase | — |
| `design-systems/airbnb.md` | Airbnb | — |
| `design-systems/uber.md` | Uber | — |
| `design-systems/spotify.md` | Spotify | — |
| `design-systems/coinbase.md` | Coinbase | — |
| `design-systems/nvidia.md` | Nvidia | — |
| `design-systems/ibm.md` | IBM | — |
| `design-systems/pinterest.md` | Pinterest | — |
| `design-systems/spacex.md` | SpaceX | — |
| `design-systems/revolut.md` | Revolut | — |
| `design-systems/sentry.md` | Sentry | — |
| `design-systems/hashicorp.md` | HashiCorp | — |
| `design-systems/mintlify.md` | Mintlify | — |
| `design-systems/resend.md` | Resend | — |
| `design-systems/raycast.md` | Raycast | — |
| `design-systems/zapier.md` | Zapier | — |
| `design-systems/webflow.md` | Webflow | — |
| `design-systems/warp.md` | Warp | — |
| `design-systems/sanity.md` | Sanity | — |
| `design-systems/clickhouse.md` | ClickHouse | — |
| `design-systems/framer.md` | Framer | — |
| `design-systems/miro.md` | Miro | — |
| `design-systems/intercom.md` | Intercom | — |
| `design-systems/lovable.md` | Lovable | — |
| `design-systems/cursor.md` | Cursor | — |
| `design-systems/claude.md` | Claude (Anthropic) | — |
| `design-systems/replicate.md` | Replicate | — |
| `design-systems/runwayml.md` | RunwayML | — |
| `design-systems/elevenlabs.md` | ElevenLabs | — |
| `design-systems/mistral.ai.md` | Mistral AI | — |
| `design-systems/cohere.md` | Cohere | — |
| `design-systems/together.ai.md` | Together AI | — |
| `design-systems/x.ai.md` | xAI | — |
| `design-systems/minimax.md` | MiniMax | — |
| `design-systems/ollama.md` | Ollama | — |
| `design-systems/opencode.ai.md` | OpenCode AI | — |
| `design-systems/voltagent.md` | VoltAgent | — |
| `design-systems/mongodb.md` | MongoDB | — |
| `design-systems/posthog.md` | PostHog | — |
| `design-systems/expo.md` | Expo | — |
| `design-systems/superhuman.md` | Superhuman | — |
| `design-systems/wise.md` | Wise | — |
| `design-systems/kraken.md` | Kraken | — |
| `design-systems/airtable.md` | Airtable | — |
| `design-systems/clay.md` | Clay | — |
| `design-systems/cal.md` | Cal | — |
| `design-systems/bmw.md` | BMW | — |
| `design-systems/composio.md` | Composio | — |

> 📌 完整品牌列表见 `development.instructions.md` 末尾「品牌设计系统」章节。