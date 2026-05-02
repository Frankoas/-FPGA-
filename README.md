# FPGA可视化编程工具 — 实现路径与工具方案

> 对应文档：`# FPGA可视化编程工具任务计划书.md`
> 每个任务给出推荐实现路径（怎么做）与推荐工具/库（用什么）。

---

## 第一阶段：基础框架与节点编辑器

### 任务 1.1：技术选型与架构设计

**实现路径**
1. 确定整体架构：Electron 桌面壳 + React 前端 + Python 后端服务（独立进程通信）。
2. 前端负责画布交互与 UI；Python 后端负责解析、代码生成、仿真调度。
3. 前后端通过 HTTP (localhost) 或 stdin/stdout JSON-RPC 通信。
4. 定义数据流：节点图 → IR (JSON) → Python 代码生成 → Verilog/VHDL 文件。
5. 项目结构采用 monorepo：`frontend/` + `backend/` + `shared-types/`。

**推荐工具**
| 层面 | 工具 | 理由 |
|------|------|------|
| 桌面壳 | Electron 28+ | 跨平台、成熟生态、可调用本地进程 |
| 前端框架 | React 18 + TypeScript | 组件化、强类型、生态丰富 |
| 构建工具 | Vite (electron-vite) | 快速 HMR、Electron 集成好 |
| 后端语言 | Python 3.11+ | FPGA 工具链 (TCL/解析) 生态成熟 |
| 后端框架 | FastAPI | 异步支持、自动 OpenAPI、轻量 |
| IPC | HTTP localhost + WebSocket | 简单可靠、可单独调试后端 |

---

### 任务 1.2：画布渲染、缩放平移、节点拖拽

**实现路径**
1. 基于 ReactFlow 搭建画布，自定义 Node 组件。
2. 实现画布操作：鼠标滚轮缩放（0.1x–3x）、右键拖拽平移、键盘快捷键（Space+拖拽）。
3. 节点拖拽移动，连线随节点位置实时更新。
4. 添加 minimap 小地图与栅格背景。
5. 性能预留：节点数 > 200 时启用 `onlyRenderVisibleElements`。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **@xyflow/react (ReactFlow v12)** | 节点画布核心：节点/边管理、缩放、拖拽 |
| **@xyflow/react 内置 Minimap** | 小地图导航 |
| **@xyflow/react Background** | 栅格/点阵背景 |

---

### 任务 1.3：节点编辑器

#### 任务 1.3.1：节点数据模型

**实现路径**
1. 定义 TypeScript 接口：`NodeData { id, type, label, ports: {input: Port[], output: Port[]}, position, config }`。
2. `Port` 类型含：`name, direction, width, signed, arraySize` 等信号属性。
3. 使用 Zustand 管理全局节点/边状态，提供 `addNode / removeNode / updateNode / addEdge / removeEdge` action。
4. 节点类型枚举：`BaseModule / WrappedModule / BoardIP / TopModule / TestbenchStim`。
5. 定义共享类型包 `shared-types/` 供前后端共用（JSON Schema 校验）。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **Zustand** | 轻量状态管理，比 Redux 简洁 |
| **Zod** | 运行时类型校验 + TypeScript 类型推导 |
| **JSON Schema** | 工程文件格式校验 |

#### 任务 1.3.2：端口创建与连线

**实现路径**
1. 在自定义 ReactFlow Node 组件中，左右两侧渲染端口圆点（Handle 组件）。
2. 输入端口在左侧（target Handle），输出端口在右侧（source Handle）。
3. 连线规则校验：仅 output→input、同类型端口可连、禁止环路（拓扑排序检测）。
4. 连线时高亮兼容端口（绿色=可连，红色=禁止）。
5. 右键端口弹出菜单：添加/删除端口、编辑端口属性（位宽、有无符号）。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **@xyflow/react Handle** | 端口连接点渲染 |
| **@xyflow/react useConnection** | 连线校验 hook |
| **graphlib (或自研拓扑排序)** | 环路检测 |

#### 任务 1.3.3：信号线可编辑标注

**实现路径**
1. ReactFlow Edge 的 `label` 属性支持自定义 React 组件。
2. 双击边上的标注区域进入编辑模式，渲染 `<input>`。
3. 标注内容作为 `wireName` 存入边数据，代码生成时使用该名称声明 wire。
4. 回车或失焦确认，Esc 取消。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **@xyflow/react EdgeLabelRenderer** | 边上渲染自定义标签 |
| **React controlled input** | 行内编辑 |

---

### 任务 1.4：自定义封装工程

**实现路径**
1. 用户框选一组节点 → 右键 "封装为模块" → 弹出配置窗口。
2. 配置窗口：命名新模块、勾选暴露的端口（内部向外透传的信号）。
3. 确认后：内部节点/边折叠为一个 WrappedModule 节点，选中端口暴露为外部 Handle。
4. 封装信息存入节点元数据（内部子图引用 ID），支持 "展开/折叠" 切换。
5. 导出为可复用节点模板（存模板库 localStorage 或文件）。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **@xyflow/react useNodesInitialized** | 监听选择/框选 |
| **React Portal 或 Dialog** | 封装配置弹窗 |
| **localStorage / IndexedDB** | 模板持久化 |

---

## 第二阶段：硬件描述与代码生成

### 任务 2.1：设计中间表示 (IR)

**实现路径**
1. 定义 IR 结构（Python dataclass / Pydantic model）：
   ```
   IR {
     modules: [{ name, type, ports[], config }]
     connections: [{ src: {module, port}, dst: {module, port}, wireName }]
     wrapped_modules: [{ name, internal_ir }]
   }
   ```
2. 前端导出 IR-JSON → 后端 FastAPI 接收 → 解析为 Python 对象。
3. IR 是前端图形与后端代码生成的唯一交换格式，保证前后端解耦。
4. 版本化 IR（version 字段），便于后续兼容。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **Pydantic v2** | Python 侧 IR 模型定义与校验 |
| **dataclasses-json** | 备选（更轻量） |

---

### 任务 2.2：顶层拓扑生成器

#### 任务 2.2.1：生成 module 例化语句

**实现路径**
1. 拓扑排序确定模块例化顺序（无依赖的在前）。
2. 遍历 IR 中每个模块，生成 Verilog 例化模板：
   ```verilog
   module_name u_inst_name (
       .port_a (wire_name),
       .port_b (wire_name)
   );
   ```
3. 实例名自动生成规范：`u_<模块名>_<序号>`。
4. 支持用户自定义例化名（通过节点属性覆盖）。

#### 任务 2.2.2：自动生成 wire 声明与连接

**实现路径**
1. 分析所有连线：两端端口位宽匹配检查，不匹配时给出 warning 并自动截断/补零。
2. 为每条无标注连线自动生成 wire 名：`w_<src>_<dst>_<port>`。
3. 有标注的连线使用用户指定名。
4. 生成 `wire [WIDTH-1:0] name;` 声明集合。
5. 模块端口位宽参数化（支持 parameter 传递）。

**推荐工具（2.2.1 & 2.2.2 共用）**
| 工具 | 用途 |
|------|------|
| **Jinja2** | Verilog 代码模板渲染 |
| **graphlib (Python)** | 拓扑排序 |
| **自定义 CodeWriter 类** | 缩进管理、代码拼接 |

---

### 任务 2.3：板卡 IP 封装支持

#### 任务 2.3.1：IP 配置界面

**实现路径**
1. 前端实现 IP 配置面板（右侧抽屉），用户选择板卡类型。
2. 板卡信息从 JSON 配置文件加载：包含时钟引脚、GPIO 映射、外设 IP 列表。
3. 用户从 IP 库拖入所需 IP 模块到画布，双击打开参数面板。
4. 参数包括：输入时钟频率、复位极性、接口协议选择（SPI/I2C/UART）。

#### 任务 2.3.2：样板工程与半自动代码生成

**实现路径**
1. 每种支持板卡预置一个 YAML/JSON 样板工程：`boards/xilinx_zynq7000/template.json`。
2. 样板含：顶层端口模板、PLL 配置、常用外设 IP（GPIO/UART/I2C）。
3. 用户配置后，Jinja2 渲染生成约束文件 (.xdc) 和例化代码。
4. 半自动：自动生成框架 + 用户补充业务逻辑区域（标记为 `// USER CODE BEGIN`）。

#### 任务 2.3.3：IDE 导出接口

**实现路径**
1. 定义导出适配器接口：`Exporter.export(ir, target_ide) -> {files}`。
2. 实现 Vivado 适配器：生成 `.tcl` 工程创建脚本 + `.xdc` 约束 + Verilog 源文件列表。
3. 预留 Quartus 适配器扩展点（同接口不同实现）。
4. 导出为 ZIP 包，或直接写入用户指定目录。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **YAML / JSON config files** | 板卡定义与样板 |
| **Jinja2** | 约束文件、TCL 脚本模板渲染 |
| **Python zipfile** | 打包导出 |
| **策略模式 (class Exporter)** | IDE 适配器可扩展架构 |

---

### 任务 2.4：一键生成 Top 文件

**实现路径**
1. 收集画布上所有顶级模块（非封装子模块）及其连线。
2. 通过 IR 传给后端 `/api/generate/top` 端点。
3. 后端：
   a. 自动推断顶层端口（无连接的输入→顶层 input，无连接的输出→顶层 output）。
   b. 生成 module 头（端口声明、parameter）。
   c. 生成内部 wire 声明 + 所有子模块例化。
4. 返回生成的 Verilog/VHDL 文本，前端在代码预览窗口中展示并支持下载。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **FastAPI** | REST 端点 `/api/generate/top` |
| **Jinja2** | Top 模板渲染 |
| **Monaco Editor (@monaco-editor/react)** | 前端代码预览（语法高亮） |

---

## 第三阶段：仿真联动与信号捕捉

### 任务 3.1：信号线选择与抓取界面

**实现路径**
1. 在节点连线上添加 "探针" 按钮（点击或右键菜单 "标记仿真"）。
2. 标记信号高亮显示（如变为黄色虚线），加入仿真信号列表面板。
3. 面板内展示：信号名、所属模块、位宽、预计波形初值。
4. 支持从面板移除 / 清空信号。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **@xyflow/react 自定义 Edge** | 探针式信号标记 |
| **Zustand 仿真信号 store** | 状态管理 |

---

### 任务 3.2：构建 API 服务层调用 ModelSim

**实现路径**
1. Python 后端封装 `Simulator` 抽象类，定义 `compile / run / get_waves` 接口。
2. `ModelSimSimulator` 实现类：
   a. 调用 `vsim` 命令行启动 ModelSim（TCL 批处理模式）。
   b. 生成 TCL 脚本：编译源文件、启动仿真、运行指定时间、导出波形。
   c. 使用 `subprocess` 异步执行，实时回传日志进度（WebSocket）。
3. 超时与异常处理：仿真超时自动 kill，错误信息回传前端。
4. 预留 QuestaSim / Icarus Verilog / Verilator 实现扩展点。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **Python subprocess + asyncio** | 异步进程管理 |
| **FastAPI WebSocket** | 实时日志推送 |
| **策略/工厂模式** | 仿真器多后端架构 |

---

### 任务 3.3：自动生成 Testbench 框架

**实现路径**
1. 根据用户标记的仿真信号，构建 Testbench 上下文。
2. Jinja2 模板生成：
   a. `include "top_module.v"` 宏。
   b. 时钟生成逻辑（周期可配置）。
   c. 复位序列（前 N 个周期复位）。
   d. 激励占位标记 `// STIMULUS: signal_name`。
3. 自动例化 DUT（顶层模块）。
4. 生成 `initial begin ... $finish; end` 框架。
5. 前端可预览和手动编辑，再提交执行。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **Jinja2** | Testbench 模板 |
| **Monaco Editor** | 前端 TB 编辑/预览 |

---

### 任务 3.4：解析仿真波形数据并可视化

**实现路径**
1. 仿真执行后导出 VCD 或 WLF→VCD 文件。
2. 后端用 `vcdvcd` 或自研解析器解析 VCD 为 JSON：
   ```
   { signals: [{ name, values: [{time, value}] }] }
   ```
3. 前端接收 JSON，用自研 Canvas 波形组件或 WaveDrom 渲染。
4. 波形组件功能：多信号展开、缩放时间轴、信号分组、颜色区分。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **vcdvcd (Python)** | VCD 文件解析库 |
| **自研 Canvas 组件 (React + OffscreenCanvas)** | 波形渲染（大数据量时 Web Worker 预处理） |
| **WaveDrom** | 备选：简单场景波形渲染 |

---

### 任务 3.5：可视化调试（光标与时序测量）

**实现路径**
1. 波形图上叠加可拖拽的垂直光标线（Marker）。
2. 用户点击添加光标 A 和 B，自动计算 ΔT 并显示。
3. 支持键盘微调光标（← → 移动 1 个时间单位）。
4. 信号值跟随光标位置实时显示（tooltip）。
5. 光标状态通过 Zustand 管理，支持保存/恢复。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **自研 Canvas 交互层** | 光标拖拽与渲染 |
| **Zustand** | 光标状态管理 |
| **快捷键 bindings (react-hotkeys-hook)** | 键盘微调 |

---

## 第四阶段：工程导入与模块提取

### 任务 4.1：Verilog/VHDL 解析器

**实现路径**
1. **Verilog**：集成 `sv-parser` (Rust/Node binding) 或 `pyverilog` (Python) 做 AST 解析。
2. 提取信息：模块名、端口列表（方向+位宽）、内部例化语句（子模块名+实例名+连接）。
3. **VHDL**：集成 `pyVHDLParser` 或 `GHDL` 生成 AST。
4. 构建统一中间格式 `ParsedModule`（与 IR module 结构对齐）。
5. 容错处理：解析失败时标记文件+行号，给出友好提示。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **pyverilog / sv-parser** | Verilog/SystemVerilog 解析 |
| **pyVHDLParser / GHDL** | VHDL 解析 |
| **自定义 AST→IR 转换器** | 统一中间格式 |

---

### 任务 4.2：导入工程自动创建模块节点

**实现路径**
1. 用户选择工程目录或文件列表。
2. 解析所有 `.v/.sv/.vhd` 文件，提取模块定义。
3. 为每个模块创建节点，初始布局由层次关系 + 简单拓扑分层算法决定。
4. 自动连线：根据例化语句中的端口连接关系生成边。
5. 保留层次分组信息（折叠子模块到父模块附近）。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **dagre (或 dagrejs)** | 自动布局算法 |
| **自定义布局引擎** | 层次感知节点放置 |

---

### 任务 4.3：子模块拖入封装

**实现路径**
1. 已导入模块节点右键 → "拖入封装为子模块"。
2. 弹出封装编辑器：选择新封装名、暴露端口。
3. 与任务 1.4 共用的封装引擎生成 WrappedModule。
4. 封装节点可拖入其他画布复用。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **与 1.4 共用封装引擎** | 复用逻辑 |
| **React DnD (或 @xyflow/react 原生拖放)** | 跨画布拖拽 |

---

## 第五阶段：界面优化与自动化

### 任务 5.1：一键整理画布（自动布局）

**实现路径**
1. 实现分层布局算法（Sugiyama）：
   a. 拓扑分层（每层无依赖的节点在同一行）。
   b. 层内排序减少交叉。
   c. 节点坐标分配（水平间距 250px，垂直间距 150px）。
2. 或使用力导向布局（Dagre / ELK.js）处理复杂拓扑。
3. 前端展示布局动画（平滑移动到新位置）。
4. 支持 "仅整理选中节点" 或 "整理全部"。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **dagre + dagrejs** | 分层/力导向布局算法 |
| **ELK.js (Eclipse Layout Kernel)** | 备选：更强布局引擎 |
| **CSS transition** | 节点移动动画 |

---

### 任务 5.2：端口智能对齐

**实现路径**
1. 在自动布局后执行端口对齐优化：
   a. 检测垂直相邻节点间的直接连线，微调 Y 坐标对齐端口。
   b. 同层节点端口高度一致化处理。
2. 实现为布局引擎的后处理步骤，独立可调用。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **自研对齐算法** | 基于边连接信息重新计算 Y 偏移 |
| **dagre 边约束** | 利用 dagre 的 rank 调整减少交叉 |

---

### 任务 5.3：主题定制、网格吸附、批注

**实现路径**
1. **主题定制**：CSS 变量体系 + 主题配置对象，支持暗/亮模式、自定义色板。
2. **网格吸附**：节点拖拽时对齐到最近网格点（gridSize 可配置 10/20/50 px），松开时自动吸附。
3. **批注功能**：独立于模块节点的 "注释框" 节点，可调整大小、书写多行文字、设置背景色。连线也可添加浮动注释。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **CSS Variables + Tailwind CSS** | 主题系统 |
| **@xyflow/react snapToGrid** | 网格吸附 |
| **ReactFlow Node 自定义组件** | 注释节点渲染 |

---

### 任务 5.4：保存/加载工程文件

**实现路径**
1. 定义工程文件格式 `.fpga.json`（自描述格式，含版本号、IR、画布状态、仿真配置）。
2. 保存：导出全量节点/边状态 + 封装子图 + 板卡配置 + 仿真信号列表。
3. 加载：解析 JSON → 校验 Schema → 重建画布状态 → 恢复封装展开状态。
4. 支持最近打开文件列表（Electron `app.getRecentDocuments`）。
5. 自动保存（debounce 2s）+ 脏状态标记（标题栏 `•`）。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **Zod Schema** | 文件格式校验 |
| **Electron dialog API** | 保存/打开文件对话框 |
| **Electron app.addRecentDocument** | 最近文件 |
| **Zustand persist middleware** | 自动保存到文件 |

---

## 第六阶段：集成测试与文档

### 任务 6.1：端到端测试

**实现路径**
1. 编写测试场景脚本：
   a. 新建工程 → 拖入 3 个模块 → 连线 → 封装为子模块 → 生成 Top → 与预期 Verilog 比对。
   b. 标记信号 → 生成 TB → 调用仿真（Mock ModelSim 或 Icarus）→ 验证波形输出。
2. 前端用 Playwright 做 UI 自动化测试。
3. 后端用 pytest 做 API 与代码生成逻辑测试。
4. CI 中集成：GitHub Actions 自动运行测试套件。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **Playwright** | 前端 E2E 测试 (Electron 支持) |
| **pytest + pytest-asyncio** | 后端测试 |
| **Icarus Verilog (iverilog)** | CI 中免费仿真验证 |
| **GitHub Actions** | CI/CD 流水线 |

---

### 任务 6.2：不同板卡 IP 兼容性测试

**实现路径**
1. 为每种支持的板卡编写一份测试用例。
2. 测试内容：IP 配置 → 代码生成 → 样板工程完整性校验。
3. 差异测试：切换板卡后重新生成，确认约束文件和引脚映射变化正确。
4. 用 snapshot 测试对比生成代码输出。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **pytest-snapshot** | 代码生成输出快照对比 |
| **YAML 数据驱动测试** | 多板卡参数化测试 |

---

### 任务 6.3：用户手册与开发者文档

**实现路径**
1. 用户手册：Markdown → VitePress 构建静态站点。
2. 内容结构：快速入门 → 节点编辑器 → 封装 → 仿真 → 板卡配置 → 常见问题。
3. 开发者文档：前后端 README、API 文档（FastAPI 自动生成 Swagger）、架构图。
4. 内嵌 GIF/截屏（Electron 内录工具或 OBS）。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **VitePress** | 文档站点 |
| **FastAPI Swagger UI** | API 文档自动生成 |
| **Draw.io / Excalidraw** | 架构图 |

---

### 任务 6.4：性能优化与 Bug 修复

**实现路径**
1. **画布虚拟化**：ReactFlow `onlyRenderVisibleElements` + 视口外节点不渲染 DOM。
2. **大数据波形**：Canvas 渲染 + Web Worker 解码 VCD，主线程仅画可视时间窗口。
3. **大型工程**：增量布局（仅移动变化的节点），防抖批量更新。
4. **内存**：及时释放未使用的封装子图数据。
5. Bug 跟踪用 GitHub Issues，回归测试套件覆盖每个修复合入。

**推荐工具**
| 工具 | 用途 |
|------|------|
| **React DevTools Profiler** | 渲染性能分析 |
| **OffscreenCanvas + Web Worker** | 波形大数据处理 |
| **Lighthouse / Electron DevTools** | 整体性能审计 |
| **pytest regression suite** | 回归测试 |

---

## 附录：总体技术栈一览

| 层面 | 核心技术 | 辅助/备选 |
|------|----------|-----------|
| 桌面框架 | Electron 28+ | Tauri (未来迁移备选) |
| 前端 UI | React 18 + TypeScript | — |
| 节点画布 | @xyflow/react (ReactFlow v12) | 自研 Canvas (如有极端性能需求) |
| 状态管理 | Zustand | Jotai (原子化备选) |
| 构建 | electron-vite | Webpack (下降趋势) |
| 后端 | Python 3.11 + FastAPI | Node.js + Express (统一栈备选) |
| 模板引擎 | Jinja2 | — |
| 仿真接口 | ModelSim TCL + subprocess | Icarus Verilog (免费 CI 备选) |
| 硬件解析 | pyverilog + pyVHDLParser | sv-parser + GHDL |
| 波形解析 | vcdvcd | 自研 VCD parser |
| 波形渲染 | 自研 Canvas 组件 | WaveDrom |
| 自动布局 | dagre + dagrejs | ELK.js |
| 代码编辑 | Monaco Editor | CodeMirror 6 |
| 测试 | Playwright + pytest | Vitest (单元测试) |
| 文档 | VitePress | Docusaurus |
| CI/CD | GitHub Actions | — |
| 打包分发 | electron-builder | — |
