# FPGA 可视化编程工具 — 前端设计书

> 版本: 0.1.0 | 2026-05-02 | 对应后端版本 0.1.0
> 
> 本文档定义前端全部功能模块、组件架构、状态管理、API 对接和交互细节。设计前提：后端 9 个 API 端点已完工，IR JSON 是前后端唯一交换格式。

---

## 目录

1. [总体架构](#1-总体架构)
2. [技术栈](#2-技术栈)
3. [应用外壳与布局](#3-应用外壳与布局)
4. [组件树](#4-组件树)
5. [状态管理](#5-状态管理)
6. [画布与节点编辑器](#6-画布与节点编辑器)
7. [模块管理](#7-模块管理)
8. [连线系统](#8-连线系统)
9. [封装模块](#9-封装模块)
10. [代码生成面板](#10-代码生成面板)
11. [仿真联动](#11-仿真联动)
12. [波形可视化](#12-波形可视化)
13. [工程管理](#13-工程管理)
14. [板卡 IP 配置](#14-板卡ip配置)
15. [已有工程导入](#15-已有工程导入)
16. [画布自动布局](#16-画布自动布局)
17. [IR 构建与 API 对接](#17-ir-构建与api对接)
18. [快捷键设计](#18-快捷键设计)
19. [主题与样式](#19-主题与样式)
20. [开发环境搭建](#20-开发环境搭建)
21. [开发阶段划分](#21-开发阶段划分)

---

## 1. 总体架构

```
+---------------------------------------------------+
|                   Electron Shell                   |
|  +---------------------------------------------+  |
|  |              React App (Vite)               |  |
|  |  +--------+  +--------+  +--------------+   |  |
|  |  | 画布    |  | 面板区  |  | 工具栏/菜单  |   |  |
|  |  |(React  |  |(抽屉/  |  |(Toolbar/     |   |  |
|  |  | Flow)  |  | 侧栏)  |  | MenuBar)     |   |  |
|  |  +--------+  +--------+  +--------------+   |  |
|  |       |           |             |            |  |
|  |       +-----+-----+------+------+            |  |
|  |             |            |                   |  |
|  |        Zustand Store (状态管理)               |  |
|  |             |                                |  |
|  |        API Service Layer                     |  |
|  +---------------------------------------------+  |
|                      |                             |
|             HTTP localhost:8000                    |
|                      |                             |
|              +-------+--------+                    |
|              |  Python 后端   |                    |
|              |  (FastAPI)     |                    |
|              +----------------+                    |
+---------------------------------------------------+
```

**核心原则：**
- 单页面应用，画布为中心，面板在侧边/底部动态切换
- 所有复杂计算（代码生成、解析、仿真）交给后端，前端只做 UI 和状态管理
- IR JSON 在前端构建，通过 HTTP 发送给后端，响应展示给用户
- 工程文件 `.fpga.json` 自描述、自包含，支持离线保存/加载

---

## 2. 技术栈

| 层面 | 选型 | 版本 | 理由 |
|------|------|------|------|
| 桌面壳 | Electron | 30+ | 跨平台、可调本地进程（仿真） |
| 前端框架 | React | 18.3+ | 生态成熟、组件化 |
| 类型系统 | TypeScript | 5.5+ | 与后端 Pydantic 类型对齐 |
| 构建工具 | electron-vite | 2.x | Electron + Vite 一站集成 |
| 节点画布 | @xyflow/react (ReactFlow) | 12.x | 内置缩放/拖拽/小地图/边标签 |
| 状态管理 | Zustand | 5.x | 轻量、支持 persist/immer 中间件 |
| 数据校验 | Zod | 3.x | 运行时校验 IR，对应后端 Pydantic |
| 代码编辑器 | Monaco Editor | 0.50+ | Verilog 语法高亮、代码预览 |
| 波形渲染 | 自研 Canvas 组件 | — | 大数据量虚拟化渲染 |
| HTTP 客户端 | ky 或 fetch | — | 轻量，封装 API 调用 |
| 布局算法 | dagre 或 ELK.js | — | 画布自动布局 |
| 样式 | Tailwind CSS | 4.x | 快速构建 + 主题 CSS 变量 |
| 测试 | Playwright | — | Electron E2E 测试 |

---

## 3. 应用外壳与布局

### 3.1 主窗口布局

```
+-----------------------------------------------------------+
|  [MenuBar]  文件  编辑  视图  工程  仿真  帮助              |
+-----------------------------------------------------------+
|  [Toolbar]  |添加模块| |连线| |封装| |生成代码| |运行仿真| ... |
+--------+---------------------------------------+----------+
|        |                                       |          |
| 左侧   |           画布区域 (Canvas)            |  右侧    |
| 面板   |    - ReactFlow 节点/边渲染             |  属性    |
|        |    - 缩放: 滚轮 (0.1x ~ 3x)           |  面板    |
| (可    |    - 平移: 中键拖拽 / Space+拖拽      |          |
| 折叠)  |    - 框选: 左键拖拽空白区域            | (可     |
|        |    - 右键菜单: 上下文操作              |  折叠)  |
| 模块库 |                                       |  选中    |
| -------|                                       |  节点/边 |
| 搜索框 |                                       |  属性    |
|        |                                       |  编辑器  |
| 模块   |                                       |          |
| 列表   |  +---------------------+              |          |
| (可拖  |  | Minimap (小地图)     |              |          |
| 拽到   |  +---------------------+              |          |
| 画布)  |                                       |          |
|        |                                       |          |
+--------+---------------------------------------+----------+
|  [StatusBar]  模块数:5 | 连线数:8 | 缩放:100% | IR版本:0.1.0 |
+-----------------------------------------------------------+
```

### 3.2 面板切换逻辑

- **左侧面板**（宽度 240px，可拖拽调整，默认展开）：
  - Tab 1: 模块库（可用模块列表 + 搜索）
  - Tab 2: 仿真信号列表（标记的探针信号）
  - Tab 3: 工程文件树（导入的源文件结构）
- **右侧面板**（宽度 300px，可拖拽调整，按需展开）：
  - 无选中时：空白/工程概览
  - 选中节点时：节点属性编辑器
  - 选中边时：wire 属性编辑器
  - 多选时：批量操作面板
- **底部面板**（高度 250px，可折叠）：
  - Tab 1: 代码输出（生成的 Verilog / Testbench）
  - Tab 2: 仿真日志（编译/仿真实时输出）
  - Tab 3: 波形查看器（解析后的波形）

### 3.3 菜单结构

```
文件:
  - 新建工程          Ctrl+N
  - 打开工程...       Ctrl+O
  - 保存              Ctrl+S
  - 另存为...         Ctrl+Shift+S
  - 最近打开的文件    >
  - 导入 Verilog...   Ctrl+I
  - 导出 Top 文件...  Ctrl+E
  - 退出              Alt+F4

编辑:
  - 撤销              Ctrl+Z
  - 重做              Ctrl+Y
  - 剪切              Ctrl+X
  - 复制              Ctrl+C
  - 粘贴              Ctrl+V
  - 删除              Delete
  - 全选              Ctrl+A
  - 查找节点...       Ctrl+F

视图:
  - 放大              Ctrl+=
  - 缩小              Ctrl+-
  - 适配画布          Ctrl+0
  - 整理画布          Ctrl+L
  - 切换网格吸附      Ctrl+G
  - 切换小地图        Ctrl+M
  - 切换左侧面板      Ctrl+B
  - 切换右侧面板      Ctrl+Shift+B
  - 切换底部面板      Ctrl+J
  - 暗色/亮色主题     Ctrl+Shift+T

工程:
  - 封装选中模块      Ctrl+W
  - 展开封装模块      Ctrl+Shift+W
  - 生成 Top 模块     Ctrl+Shift+G
  - 生成 Testbench    Ctrl+Shift+T

仿真:
  - 编译源文件        F5
  - 运行仿真          F6
  - 停止仿真          Shift+F5
  - 添加探针          P
  - 清除所有探针      Shift+P
```

---

## 4. 组件树

```
<App>
  <ElectronShell>
    <MenuBar />                          // 菜单栏
    <Toolbar />                          // 快捷工具栏
    <MainLayout>                         // 主布局容器
      <LeftPanel>                        // 左侧面板（可折叠/调整宽度）
        <PanelTabs>
          <ModuleLibrary />              // 模块库 + 搜索
          <SimSignalList />              // 仿真信号列表
          <ProjectFileTree />            // 工程文件树
        </PanelTabs>
      </LeftPanel>

      <CanvasArea>                       // 画布区域
        <ReactFlowProvider>
          <Canvas>                       // ReactFlow 主画布
            <GridBackground />           // 网格/点阵背景
            <Minimap />                  // 小地图
            <Controls />                 // 缩放控制
            <NodeRenderer>              // 自定义节点渲染
              <BaseModuleNode />         // base 类型节点
              <WrappedModuleNode />      // wrapped 类型节点
              <BoardIPNode />            // board_ip 类型节点
              <AnnotationNode />         // 注释/批注节点
            </NodeRenderer>
            <EdgeRenderer>              // 自定义边渲染
              <SignalEdge />            // 信号线（可标记探针）
            </EdgeRenderer>
            <ConnectionLine />           // 拖拽中的临时连线
          </Canvas>
          <CanvasContextMenu />          // 画布空白区右键菜单
          <NodeContextMenu />            // 节点右键菜单
          <EdgeContextMenu />            // 边右键菜单
        </ReactFlowProvider>
      </CanvasArea>

      <RightPanel>                       // 右侧属性面板（按需展开）
        <EmptyState />                   // 无选中时
        <NodePropertyEditor />           // 节点属性编辑
        <EdgePropertyEditor />           // 边属性编辑
        <BatchOperationPanel />          // 多选批量操作
      </RightPanel>
    </MainLayout>

    <BottomPanel>                        // 底部面板（可折叠/调整高度）
      <PanelTabs>
        <CodeViewer />                   // 代码输出预览（Monaco Editor）
        <SimLogViewer />                 // 仿真日志输出
        <WaveformViewer />               // 波形可视化
      </PanelTabs>
    </BottomPanel>

    <StatusBar />                        // 底部状态栏
    <Dialogs>
      <NewProjectDialog />               // 新建工程
      <EncapsulateDialog />              // 封装模块配置
      <BoardConfigDialog />              // 板卡 IP 配置
      <SimConfigDialog />                // 仿真参数配置
      <ExportDialog />                   // 导出文件
      <ImportDialog />                   // 导入文件
      <AboutDialog />                    // 关于
    </Dialogs>
  </ElectronShell>
</App>
```

---

## 5. 状态管理

使用 Zustand，按功能域拆分为多个 store。

### 5.1 画布 Store (`useCanvasStore`)

```typescript
interface CanvasState {
  // 画布状态
  nodes: Node<ModuleData>[];          // ReactFlow 节点
  edges: Edge<ConnectionData>[];      // ReactFlow 边
  viewport: { x: number; y: number; zoom: number };

  // 操作
  addModule: (module: ModuleData) => void;
  removeModule: (id: string) => void;
  updateModulePosition: (id: string, pos: [number, number]) => void;
  addConnection: (conn: ConnectionData) => void;
  removeConnection: (id: string) => void;
  updateWireName: (id: string, name: string) => void;

  // 选择
  selectedNodeIds: string[];
  selectedEdgeIds: string[];
  selectNodes: (ids: string[]) => void;
  selectEdges: (ids: string[]) => void;
  clearSelection: () => void;

  // 历史（撤销/重做）
  undoStack: Snapshot[];
  redoStack: Snapshot[];
  undo: () => void;
  redo: () => void;
  takeSnapshot: () => void;
}
```

### 5.2 工程 Store (`useProjectStore`)

```typescript
interface ProjectState {
  // 工程元数据
  projectName: string;
  projectPath: string | null;
  isDirty: boolean;                   // 是否有未保存修改
  recentFiles: string[];

  // IR 顶层信息
  topModuleName: string;
  irVersion: string;

  // 封装模块
  wrappedModules: WrappedModuleData[];

  // 板卡配置
  boardConfig: BoardConfigData | null;

  // 仿真配置
  simulationConfig: SimulationConfigData;

  // 操作
  newProject: (name: string) => void;
  saveProject: (path?: string) => Promise<void>;
  loadProject: (path: string) => Promise<void>;
  setTopModuleName: (name: string) => void;
  addWrappedModule: (wm: WrappedModuleData) => void;
  removeWrappedModule: (name: string) => void;
  updateBoardConfig: (config: BoardConfigData) => void;
  updateSimConfig: (config: Partial<SimulationConfigData>) => void;

  // IR 导出
  buildIR: () => IR;                  // 从当前画布状态构建完整 IR
}
```

### 5.3 模块库 Store (`useModuleLibraryStore`)

```typescript
interface ModuleLibraryState {
  // 内置模块模板
  builtInModules: ModuleTemplate[];
  // 用户自定义模块模板（从封装/导入来的）
  userModules: ModuleTemplate[];
  // 搜索
  searchQuery: string;

  // 操作
  addCustomTemplate: (tmpl: ModuleTemplate) => void;
  removeCustomTemplate: (name: string) => void;
  searchModules: (query: string) => ModuleTemplate[];
}

interface ModuleTemplate {
  name: string;
  type: 'base' | 'board_ip' | 'user';
  category: string;                   // 分类: basic / io / clock / dsp / user
  ports: PortData[];
  defaultConfig: Record<string, any>;
  icon?: string;
}
```

### 5.4 仿真 Store (`useSimulationStore`)

```typescript
interface SimulationState {
  // 探针（标记的仿真信号）
  probedSignals: ProbedSignal[];
  // 仿真状态
  simStatus: 'idle' | 'compiling' | 'running' | 'done' | 'error';
  // 仿真日志（WebSocket 实时推送）
  logLines: LogLine[];
  // 波形数据（VCD 解析结果）
  waveform: WaveformData | null;
  // 光标/标记
  markers: TimeMarker[];

  // 操作
  addProbe: (moduleId: string, portName: string) => void;
  removeProbe: (moduleId: string, portName: string) => void;
  clearAllProbes: () => void;
  compile: () => Promise<void>;
  run: () => Promise<void>;
  stop: () => Promise<void>;
  loadWaveform: (vcdPath: string) => Promise<void>;
  addMarker: (timeNs: number, label: string) => void;
  removeMarker: (id: string) => void;
}

interface ProbedSignal {
  moduleId: string;
  moduleName: string;
  portName: string;
  width: number;
}
```

### 5.5 UI Store (`useUIStore`)

```typescript
interface UIState {
  // 面板可见性
  leftPanelOpen: boolean;
  rightPanelOpen: boolean;
  bottomPanelOpen: boolean;
  leftPanelTab: 'library' | 'signals' | 'files';
  bottomPanelTab: 'code' | 'log' | 'waveform';

  // 主题
  theme: 'light' | 'dark';

  // 网格
  gridSnap: boolean;
  gridSize: number;                   // 10 / 20 / 50

  // 对话框
  activeDialog: string | null;

  // 状态栏消息
  statusMessage: string;

  // 操作
  toggleLeftPanel: () => void;
  toggleRightPanel: () => void;
  toggleBottomPanel: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setGridSnap: (snap: boolean) => void;
  showDialog: (name: string) => void;
  hideDialog: () => void;
}
```

---

## 6. 画布与节点编辑器

### 6.1 画布基础配置

```typescript
const defaultViewport = { x: 0, y: 0, zoom: 1 };
const zoomRange: [number, number] = [0.1, 4];
const snapGrid: [number, number] = [20, 20];  // 可由用户调整
```

- 滚轮缩放，以鼠标位置为中心
- 中键拖拽平移，或按住 Space + 左键拖拽
- 右键拖拽空白区域平移画布
- 左键拖拽空白区域框选
- `onlyRenderVisibleElements` 在节点 > 100 时开启

### 6.2 自定义节点设计

每个节点分为三个区域：

```
+------------------------------+
|  [模块图标]  模块名    [折叠] |  <- Header (蓝色底)
|             实例名: u_xxx    |
+------------------------------+
|  input ports          output ports
|  (左侧 Handle)        (右侧 Handle)
|                              |
|  [clk] ----+         +---- [q[3:0]]
|  [rst_n] --+         +---- [led_out]
|  [data] ---+              [status]
|                              |
+------------------------------+
|  [配置: div_factor=4]        |  <- Footer (灰色, 可展开)
+------------------------------+
```

**节点类型与渲染差异：**

| 类型 | 颜色 | 图标 | 特殊行为 |
|------|------|------|----------|
| base | 蓝色 #214184 | 齿轮 | 标准节点 |
| wrapped | 紫色 #6B21A8 | 包裹图标 | 双击展开/折叠内部子图 |
| board_ip | 橙色 #C2410C | 芯片图标 | 双击打开 IP 配置面板 |
| annotation | 黄色 #FDE68A | 无 | 无端口，可书写多行文字 |

**端口 Handle 渲染规则：**
- 输入端口：左侧 Handle（type: 'target'），灰色圆点
- 输出端口：右侧 Handle（type: 'source'），蓝色圆点
- 双向端口：两侧均有 Handle，橙色圆点
- 拖拽连线时，兼容端口高亮为绿色，不兼容端口变红
- 端口标签：显示端口名 + 位宽（如 `q [3:0]`）

### 6.3 节点交互

- **拖拽移动**：左键拖拽 Header 区域，对齐网格（可选）
- **双击 Header**：编辑模块名 / 实例名（行内编辑）
- **右键 Header**：弹出节点上下文菜单
- **拖入新节点**：从左侧模块库拖拽到画布
- **右键端口圆点**：编辑端口属性（位宽、有无符号、删除/添加端口）
- **节点缩放**：暂不支持缩放（保持模块尺寸一致），但可通过配置展开 Footer 查看参数

### 6.4 节点右键菜单

```
[节点名]
──────────────
  编辑模块名...
  编辑实例名...
  编辑端口...
  ────────────
  封装为子模块      Ctrl+W
  添加注释节点
  ────────────
  复制             Ctrl+C
  删除             Delete
  ────────────
  标记全部端口仿真
  清除探针
```

---

## 7. 模块管理

### 7.1 模块库（左侧面板）

**内置模块模板：**

| 分类 | 模块名 | 端口示例 | 描述 |
|------|--------|----------|------|
| 基础 | blank | 无 | 空白模块，用户自定义端口 |
| 时钟 | clk_divider | clk_in, rst_n -> clk_out | 分频器 |
| 时钟 | pll | clk_in, rst_n -> clk_out, locked | PLL 锁相环 |
| IO | gpio_ctrl | clk, addr, wdata -> rdata | GPIO 控制器 |
| IO | uart_tx | clk, data[7:0], send -> tx, busy | UART 发送 |
| IO | uart_rx | clk, rx -> data[7:0], valid | UART 接收 |
| DSP | fir_filter | clk, din[15:0] -> dout[15:0] | FIR 滤波器 |
| 存储 | bram | clk, addr, wdata, we -> rdata | 块 RAM |
| 调试 | ila | clk, probe[*] -> (无输出) | ILA 逻辑分析仪 |

每个模板定义端口列表和默认参数，支持从 JSON 配置文件加载。

**搜索/过滤：**
- 输入关键词实时过滤模块名和端口名
- 分类标签过滤（点击分类名只显示该分类）

**拖入画布：**
- 从模块库拖拽 -> 进入画布区域 -> 释放 -> 创建新节点
- 新节点出现在释放位置
- 自动生成唯一 ID（uuid v4 前 12 位）

### 7.2 自定义模块模板

用户可以将封装后的模块添加到模块库，作为可复用模板：
- 封装完成后，对话框中有「添加到模块库」选项
- 模板存储在 `%APPDATA%/fpga-visual-tool/templates/` 下
- 支持导出/导入模板文件

---

## 8. 连线系统

### 8.1 连线规则

1. **方向约束**：只能从 output → input（或 inout ↔ inout）
2. **类型约束**：暂无（后续可加电气类型约束）
3. **环路检测**：连线时执行拓扑排序检查，有环路则禁止并提示
4. **多驱禁止**：一个 input 端口只能有一个来源（已有连线时禁止新连线）
5. **位宽匹配**：不匹配时给出 warning 图标（黄色三角），但不阻止连线

### 8.2 连线交互

- **拖拽连线**：从 output Handle 开始拖拽 -> 到 input Handle 释放
- **高亮反馈**：
  - 拖拽中：兼容端口绿色脉冲动画
  - 不兼容端口：红色 + 禁止光标
- **释放到空白区域**：弹出菜单 — 「取消」 / 「创建新节点并连接」
- **点击边**：选中边（高亮 + 贝塞尔曲线变粗）
- **双击边上的标签**：进入 wire_name 编辑模式
- **右键边**：弹出边上下文菜单

### 8.3 边样式

- 默认：贝塞尔曲线，2px 粗，颜色 #666
- 选中：3px 粗，颜色 #214184
- 有探针标记：虚线 + 黄色 #D97706
- 有 warning（位宽不匹配）：实线 + 黄色图标
- 高亮（hover）：颜色变浅 + 发光效果

### 8.4 边的标签

每条边可有一个 `wire_name` 标签：
- 位置：贝塞尔曲线中点
- 内容：用户命名的 wire 名，或自动生成的 `w_<src>_<dst>_<idx>`（灰色斜体）
- 编辑：双击标签进入行内编辑，回车确认，Esc 取消
- 在右键菜单中也可编辑

### 8.5 边右键菜单

```
连线: w_clk_divided
────────────────
  编辑 Wire 名...
  标记仿真探针    P
  ──────────────
  删除连线       Delete
```

### 8.6 仿真探针

- 在边上右键 -> 「标记仿真探针」，边变为黄色虚线
- 也可通过选中边后按 `P` 键
- 探针信号出现在左侧面板「仿真信号列表」中
- 探针列表项显示：信号名、所属模块、位宽
- 支持从探针列表移除 / 清空全部

---

## 9. 封装模块

### 9.1 封装流程

```
1. 用户在画布上框选多个节点 (或 Ctrl+点击多选)
2. 右键 -> "封装为模块" (Ctrl+W)
3. 弹出封装配置对话框
4. 用户:
   a. 输入封装模块名 (如 "hdmi_controller")
   b. 勾选要暴露的端口 (从内部端口列表中选择)
   c. 可选: 设置暴露端口的新名称 (如 data_out -> hdmi_data)
5. 点击"确认封装"
6. 内部节点 + 连线被折叠为一个 WrappedModule 节点
7. 选中的端口暴露为外部 Handle
8. 内部信息存入 WrappedModule 数据
```

### 9.2 封装配置对话框

```
┌─────────────────────────────────────────┐
│  封装为模块                         [×]  │
├─────────────────────────────────────────┤
│  模块名称: [hdmi_controller        ]    │
│                                         │
│  暴露端口 (共 6 个内部端口):            │
│  ┌─────────────────────────────────┐   │
│  │ ☑ clk_in      (input, 1bit)    │   │
│  │ ☑ rst_n       (input, 1bit)    │   │
│  │ ☐ tmds_clk    (output, 1bit)   │   │
│  │ ☑ tmds_d0     (output, 1bit)   │   │
│  │ ☑ tmds_d1     (output, 1bit)   │   │
│  │ ☑ tmds_d2     (output, 1bit)   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ☐ 添加到模块库 (可复用模板)            │
│                                         │
│         [取消]         [确认封装]       │
└─────────────────────────────────────────┘
```

### 9.3 展开/折叠

- **折叠状态**：画布上显示一个 WrappedModule 节点，外部可见暴露的端口
- **展开状态**（双击）：WrappedModule 节点展开，内部子图在画布上显示（带虚线边框标记封装范围）
- 展开时其他节点自动避让
- 再次双击 Header 或点击边框上的「折叠」按钮恢复折叠

---

## 10. 代码生成面板

### 10.1 生成 Top 模块

**触发方式：**
- 工具栏按钮「生成 Top」
- 快捷键 Ctrl+Shift+G
- 菜单: 工程 -> 生成 Top 模块

**前端流程：**
```
1. useProjectStore.buildIR() 收集画布上所有节点/边 -> 构建 IR JSON
2. POST /api/generate/top   { ir: IR }
3. 接收到响应: { success: true, verilog: "..." }
4. 底部面板自动切换到「代码输出」Tab
5. Monaco Editor 展示生成的 Verilog 代码（语法高亮）
6. 状态栏更新: "Top 模块生成完成"
```

**错误处理：**
- success=false 时：弹出错误提示，显示后端返回的 detail
- 网络错误时：底部面板显示红色错误信息

### 10.2 生成 Testbench

**触发方式：**
- 工具栏按钮「生成 TB」
- 快捷键 Ctrl+Shift+T

**前端流程：**
```
1. 检查是否有标记的仿真探针信号
2. 如果有探针信号，自动填入 SimConfig.monitored_signals
3. 构建 IR + SimulationConfig
4. POST /api/generate/testbench   { ir, simulation }
5. 底部面板展示生成的 Testbench
```

**仿真配置对话框（生成前可选配置）：**
```
┌─────────────────────────────────────────┐
│  仿真配置                           [×]  │
├─────────────────────────────────────────┤
│  仿真器:  [ModelSim  ▼]                │
│  时钟周期: [10.0    ] ns                 │
│  复位周期: [5       ]                   │
│  仿真时长: [100.0   ] us                 │
│                                         │
│  监控信号 (探针):                       │
│  ┌─────────────────────────────────┐   │
│  │ m1.clk          (1bit input)   │   │
│  │ m1.q            (4bit output)  │   │
│  └─────────────────────────────────┘   │
│                                         │
│         [取消]         [生成]           │
└─────────────────────────────────────────┘
```

### 10.3 代码预览器

- 使用 Monaco Editor（@monaco-editor/react）
- Verilog 语法高亮
- 支持复制到剪贴板
- 支持保存到文件（Electron dialog 选择路径）
- 支持手动编辑（编辑后重新生成时会有 "覆盖未保存的修改?" 提示）

---

## 11. 仿真联动

### 11.1 编译

**触发：工具栏「编译」按钮 或 F5**

```
1. 收集项目中所有 Verilog 源文件路径
2. POST /api/simulate/compile
   { sources: [...], work_dir: "./sim_work" }
3. 底部面板切换到「仿真日志」Tab
4. 实时显示编译输出 (stdout/stderr)
5. 编译成功 -> 状态栏 "编译成功"; 编译失败 -> 显示 errors[]
```

### 11.2 运行仿真

**触发：工具栏「运行仿真」按钮 或 F6**

```
1. POST /api/simulate/run
   { top_module, sim_time, work_dir, sources? }
2. 日志面板实时显示仿真进程
3. 仿真完成 -> 得到 vcd_path
4. 自动调用 POST /api/parse/vcd 解析波形
5. 底部面板切换到「波形」Tab
```

**注意：WebSocket 实时日志（第二阶段优化）：**
- 当前第一版可使用轮询（每秒查一次状态）或等待结果
- 第二版实现 WebSocket 端点 `/ws/simulate/log` 实时推送日志

### 11.3 停止仿真

- Shift+F5 或工具栏「停止」按钮
- 调用后端 kill 仿真进程（需要后端提供 `/api/simulate/stop`，暂未实现）

---

## 12. 波形可视化

### 12.1 波形渲染组件

使用自研 Canvas 组件，支持大量信号和高时间分辨率。

**组件结构：**
```
<WaveformViewer>
  <WaveformToolbar>              // 缩放、光标、导出工具
  <WaveformCanvas>               // Canvas 主渲染区
    <SignalLabels />             // 左侧信号名 + 位宽
    <WaveformArea />             // 右侧波形绘制
    <TimeAxis />                 // 顶部时间轴
    <Markers />                  // 可拖拽光标线
  </WaveformCanvas>
  <WaveformStatusBar />          // 光标时间、ΔT 显示
</WaveformViewer>
```

### 12.2 交互功能

| 功能 | 操作 | 描述 |
|------|------|------|
| 时间轴缩放 | Ctrl+滚轮 | 水平缩放时间轴 |
| 信号垂直缩放 | Alt+滚轮 | 调整信号行高度 |
| 平移时间轴 | 左键拖拽时间轴 | 水平滚动 |
| 滚动信号列表 | 滚轮 | 垂直滚动信号 |
| 添加光标 A | 在波形区按 A | 添加/移动绿色光标 |
| 添加光标 B | 在波形区按 B | 添加/移动蓝色光标 |
| 拖动光标 | 左键拖拽光标 | 移动光标到新位置 |
| 删除光标 | 右键光标 -> 删除 | |
| ΔT 测量 | 自动 | 显示 A-B 时间差 |
| 信号值 tooltip | hover 波形 | 显示当前时间点的值 |
| 信号分组 | 从信号列表拖拽 | 信号分组、折叠/展开 |

### 12.3 性能策略

- Canvas 虚拟化：只渲染可视时间窗口内的波形
- Web Worker 预处理：将 VCD JSON 转为渲染优化的数据格式
- 信号 > 50 时降低垂直间距
- 时间跨度 > 1ms 时自动降采样

---

## 13. 工程管理

### 13.1 工程文件格式 `.fpga.json`

```json
{
  "version": "0.1.0",
  "name": "my_design",
  "ir": { ... },           // 完整 IR（模块、连线、封装）
  "board": { ... } | null, // 板卡配置
  "simulation": { ... } | null, // 仿真配置
  "canvas_state": {
    "viewport": { "x": 0, "y": 0, "zoom": 1 },
    "leftPanelOpen": true,
    "rightPanelOpen": false
  }
}
```

### 13.2 保存 (Ctrl+S)

```
1. 构建完整 ProjectFile JSON
2. 如果已有 projectPath -> 直接 POST /api/project/save
3. 如果无 projectPath -> 弹出 Electron SaveDialog -> POST save
4. 保存成功后：isDirty = false，更新标题栏
```

### 13.3 加载 (Ctrl+O)

```
1. Electron OpenDialog 选择 .fpga.json 文件
2. POST /api/project/load { file_path }
3. 接收到 ProjectFile JSON
4. 恢复画布状态:
   a. 重建所有节点（modules）
   b. 重建所有边（connections）
   c. 恢复封装模块（wrapped_modules）
   d. 恢复视口位置
   e. 恢复面板状态
   f. 恢复板卡/仿真配置
5. 更新最近文件列表
```

### 13.4 自动保存

- 画布状态变化后 debounce 2 秒自动保存到临时文件
- 标题栏显示 ● 表示有未保存内容
- 应用退出时如果有未保存内容 -> 弹出确认对话框

### 13.5 最近文件

- 使用 Electron `app.addRecentDocument()` API
- 菜单「文件 -> 最近打开的文件」动态生成子菜单
- 最多显示 10 条

---

## 14. 板卡 IP 配置

### 14.1 板卡选择

- 从模块库中拖入 `board_ip` 类型模块（如 PLL、GPIO）到画布
- 或者在右侧面板中先选择板卡型号，然后 IP 列表自动更新

### 14.2 板卡配置对话框

```
┌──────────────────────────────────────────────┐
│  板卡配置                                [×]  │
├──────────────────────────────────────────────┤
│  板卡型号: [Xilinx Zynq-7000   ▼]           │
│  FPGA 型号: [xc7z020clg400-1   ]             │
│                                              │
│  时钟引脚配置:                                │
│  ┌──────────────────────────────────────┐   │
│  │ 时钟名      引脚    频率(MHz)         │   │
│  │ clk_50m     U18     50              │   │
│  │ [+添加]                              │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  GPIO 映射:                                  │
│  ┌──────────────────────────────────────┐   │
│  │ LED[0]   ->  M14                     │   │
│  │ LED[1]   ->  M15                     │   │
│  │ BTN[0]   ->  N17                     │   │
│  │ [+添加]                              │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  约束文件 (自动生成预览):                    │
│  ┌──────────────────────────────────────┐   │
│  │ set_property PACKAGE_PIN U18 ...     │   │
│  └──────────────────────────────────────┘   │
│                                              │
│          [取消]           [应用]             │
└──────────────────────────────────────────────┘
```

- 板卡型号从 JSON 配置文件加载（`boards/<board_name>.json`）
- 配置文件包含：默认时钟引脚、GPIO 映射、约束模板
- 用户修改后保存到工程文件中

---

## 15. 已有工程导入

### 15.1 导入流程

```
1. 菜单: 文件 -> 导入 Verilog... (Ctrl+I)
2. 选择文件或目录
3. POST /api/parse/verilog { file_path }
4. 接收到模块列表: [{name, ports[], instantiations[]}, ...]
5. 为每个解析出的模块创建节点:
   a. Module 名 = 解析出的模块名
   b. 自动生成 port list
   c. 初始位置由 dagre 自动布局算法计算
6. 根据 instantiations 信息自动创建连线
7. 导入的源文件路径记录在工程中（左侧文件树）
```

### 15.2 导入结果展示

- 导入完成后，弹出一个摘要提示：
  "已导入 5 个模块，创建 3 条连线"
- 左侧面板「工程文件」Tab 中展示导入的文件列表
- 双击文件可在底部面板的代码查看器中打开源文件

### 15.3 子模块封装

导入的模块可能有层次关系（例化关系），用户可以选择：
- 保持平铺（所有模块在同一画布）
- 按层次自动封装（顶层以下模块折叠为 WrappedModule）

在导入对话框中选择：
```
┌─────────────────────────────────────────┐
│  导入 Verilog 工程                  [×]  │
├─────────────────────────────────────────┤
│  源文件: [D:/projects/my_design/   ...] │
│                                         │
│  导入方式:                               │
│  ○ 平铺模式 (所有模块在同一层)           │
│  ● 层次模式 (按例化关系自动封装)         │
│                                         │
│         [取消]           [导入]         │
└─────────────────────────────────────────┘
```

---

## 16. 画布自动布局

### 16.1 布局算法

使用 dagre 实现分层布局（Sugiyama 算法）：

1. **拓扑分层**：根据连线方向将节点分配到不同的层（rank）
2. **层内排序**：最小化连线交叉
3. **坐标计算**：
   - 节点宽度 200px，节点间距水平 250px，垂直 150px
   - 每层节点居中排列

### 16.2 触发方式

- 快捷键 Ctrl+L
- 菜单: 视图 -> 整理画布
- 工具栏「整理」按钮

### 16.3 可选项

- 「仅整理选中节点」或「整理全部」
- 布局动画：节点平滑移动到新位置（CSS transition 300ms）
- 布局后自动适配画布缩放

### 16.4 端口对齐后处理

布局完成后，对直接相连的相邻层节点执行 Y 轴微调，使端口尽可能对齐减少交叉。

---

## 17. IR 构建与 API 对接

### 17.1 IR 构建函数

```typescript
// useProjectStore.buildIR()
function buildIR(): IR {
  const nodes = useCanvasStore.getState().nodes;
  const edges = useCanvasStore.getState().edges;

  return {
    version: "0.1.0",
    top_module_name: topModuleName,
    modules: nodes
      .filter(n => n.type !== 'annotation')
      .map(n => ({
        id: n.id,
        name: n.data.name,
        instance_name: n.data.instanceName || null,
        type: n.data.type,
        ports: n.data.ports,
        position: [n.position.x, n.position.y] as [number, number],
        config: n.data.config,
      })),
    connections: edges.map(e => ({
      id: e.id,
      src_module: e.source,
      src_port: e.data.sourcePort,
      dst_module: e.target,
      dst_port: e.data.targetPort,
      wire_name: e.data.wireName || null,
    })),
    wrapped_modules: wrappedModules,
  };
}
```

### 17.2 API Service Layer

```typescript
// services/api.ts
const BASE_URL = 'http://localhost:8000/api';

export const api = {
  health: () =>
    fetch(`${BASE_URL}/health`).then(r => r.json()),

  generateTop: (ir: IR) =>
    fetch(`${BASE_URL}/generate/top`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ir }),
    }).then(r => r.json()),

  generateTestbench: (ir: IR, simulation: SimulationConfig) =>
    fetch(`${BASE_URL}/generate/testbench`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ir, simulation }),
    }).then(r => r.json()),

  parseVerilog: (filePath: string) =>
    fetch(`${BASE_URL}/parse/verilog`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: filePath }),
    }).then(r => r.json()),

  parseVCD: (filePath: string) =>
    fetch(`${BASE_URL}/parse/vcd`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: filePath }),
    }).then(r => r.json()),

  saveProject: (project: ProjectFile, filePath: string) =>
    fetch(`${BASE_URL}/project/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project, file_path: filePath }),
    }).then(r => r.json()),

  loadProject: (filePath: string) =>
    fetch(`${BASE_URL}/project/load`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: filePath }),
    }).then(r => r.json()),

  compile: (sources: string[], workDir: string) =>
    fetch(`${BASE_URL}/simulate/compile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sources, work_dir: workDir }),
    }).then(r => r.json()),

  runSimulation: (topModule: string, simTime: string, workDir: string, sources?: string[]) =>
    fetch(`${BASE_URL}/simulate/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ top_module: topModule, sim_time: simTime, work_dir: workDir, sources }),
    }).then(r => r.json()),
};
```

### 17.3 Zod Schema 校验

与后端 Pydantic 模型对齐：

```typescript
import { z } from 'zod';

const PortSchema = z.object({
  name: z.string(),
  direction: z.enum(['input', 'output', 'inout']),
  width: z.number().int().min(1).default(1),
  signed: z.boolean().default(false),
});

const ModuleSchema = z.object({
  id: z.string(),
  name: z.string(),
  instance_name: z.string().nullable().optional(),
  type: z.enum(['base', 'wrapped', 'board_ip']).default('base'),
  ports: z.array(PortSchema),
  position: z.tuple([z.number(), z.number()]),
  config: z.record(z.any()).default({}),
});

const ConnectionSchema = z.object({
  id: z.string(),
  src_module: z.string(),
  src_port: z.string(),
  dst_module: z.string(),
  dst_port: z.string(),
  wire_name: z.string().nullable().optional(),
});

const IRSchema = z.object({
  version: z.string(),
  modules: z.array(ModuleSchema),
  connections: z.array(ConnectionSchema),
  wrapped_modules: z.array(z.any()),
  top_module_name: z.string(),
});
```

在 `buildIR()` 中调用 `IRSchema.parse(ir)` 进行运行时校验。

---

## 18. 快捷键设计

### 18.1 全局快捷键

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| Ctrl+N | 新建工程 | |
| Ctrl+O | 打开工程 | |
| Ctrl+S | 保存工程 | |
| Ctrl+Shift+S | 另存为 | |
| Ctrl+I | 导入 Verilog | |
| Ctrl+E | 导出 Top 文件 | |
| Ctrl+Z | 撤销 | |
| Ctrl+Y | 重做 | |
| Delete | 删除选中 | |
| Ctrl+A | 全选 | |
| Ctrl+C | 复制选中节点 | |
| Ctrl+V | 粘贴节点 | |
| Ctrl+F | 搜索节点 | |
| Ctrl+W | 封装选中 | |
| Ctrl+Shift+W | 展开封装 | |
| Ctrl+L | 整理画布 | |
| Ctrl+Shift+G | 生成 Top | |
| Ctrl+Shift+T | 生成 Testbench | |
| F5 | 编译 | |
| F6 | 运行仿真 | |
| Shift+F5 | 停止仿真 | |

### 18.2 画布快捷键

| 快捷键 | 功能 |
|--------|------|
| Space + 拖拽 | 平移画布 |
| 鼠标滚轮 | 缩放画布 |
| Ctrl+= | 放大 |
| Ctrl+- | 缩小 |
| Ctrl+0 | 适配画布 |
| G | 切换网格吸附 |
| P | 切换选中边的探针状态 |
| V | 切换到选择模式 |
| H | 切换到平移模式（手掌工具） |

---

## 19. 主题与样式

### 19.1 CSS 变量体系

```css
:root {
  /* 主色调 */
  --color-primary: #214184;
  --color-primary-light: #3B6AB5;
  --color-primary-dark: #162C5A;

  /* 语义色 */
  --color-success: #16A34A;
  --color-warning: #D97706;
  --color-error: #DC2626;
  --color-info: #2563EB;

  /* 画布 */
  --canvas-bg: #F8F9FA;           /* 亮色 */
  --canvas-grid: #E5E7EB;
  --canvas-grid-dot: #D1D5DB;

  /* 节点 */
  --node-bg: #FFFFFF;
  --node-border: #D1D5DB;
  --node-header-base: #214184;
  --node-header-wrapped: #6B21A8;
  --node-header-board-ip: #C2410C;
  --node-shadow: 0 1px 3px rgba(0,0,0,0.1);
  --node-shadow-selected: 0 0 0 2px #3B6AB5;

  /* 面板 */
  --panel-bg: #FFFFFF;
  --panel-border: #E5E7EB;
  --panel-width: 240px;

  /* 字体 */
  --font-mono: 'Consolas', 'Courier New', monospace;
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

  /* 间距 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 12px;
  --spacing-lg: 16px;
  --spacing-xl: 24px;
}
```

### 19.2 暗色主题

```css
[data-theme="dark"] {
  --canvas-bg: #1E1E2E;
  --canvas-grid: #2E2E3E;
  --node-bg: #2A2A3C;
  --node-border: #3E3E52;
  --panel-bg: #252536;
  --panel-border: #3E3E52;
  --color-primary: #5B8DEF;
  /* ... 更多暗色变量 */
}
```

### 19.3 响应式设计

- 最小窗口尺寸: 1024×768
- 推荐窗口尺寸: 1920×1080
- 面板宽度可拖拽调整（最小 180px，最大 400px）
- 底部面板高度可拖拽调整（最小 150px，最大 500px）

---

## 20. 开发环境搭建

### 20.1 项目初始化

```bash
# 1. 创建 Electron + React + Vite 项目
npm create electron-vite@latest fpga-visual-tool -- --template react-ts

# 2. 安装依赖
cd fpga-visual-tool
npm install

# 3. 安装核心库
npm install @xyflow/react zustand zod @monaco-editor/react dagre
npm install -D tailwindcss @tailwindcss/vite typescript

# 4. 安装开发工具
npm install -D eslint prettier playwright
```

### 20.2 目录结构（前端）

```
frontend/
  electron/
    main.ts              # Electron 主进程
    preload.ts           # 预加载脚本
    ipc.ts               # IPC 通信定义
  src/
    App.tsx              # 根组件
    main.tsx             # 入口

    components/
      canvas/
        Canvas.tsx        # 主画布
        nodes/
          BaseModuleNode.tsx
          WrappedModuleNode.tsx
          BoardIPNode.tsx
          AnnotationNode.tsx
        edges/
          SignalEdge.tsx
        CanvasContextMenu.tsx
        NodeContextMenu.tsx
        EdgeContextMenu.tsx

      panels/
        LeftPanel.tsx
        RightPanel.tsx
        BottomPanel.tsx
        ModuleLibrary.tsx
        SimSignalList.tsx
        ProjectFileTree.tsx
        CodeViewer.tsx
        SimLogViewer.tsx
        WaveformViewer/
          WaveformCanvas.tsx
          WaveformToolbar.tsx
          SignalLabels.tsx
          TimeAxis.tsx
          Markers.tsx

      dialogs/
        EncapsulateDialog.tsx
        BoardConfigDialog.tsx
        SimConfigDialog.tsx
        ExportDialog.tsx
        ImportDialog.tsx

      layout/
        MenuBar.tsx
        Toolbar.tsx
        StatusBar.tsx
        MainLayout.tsx

    stores/
      canvasStore.ts
      projectStore.ts
      moduleLibraryStore.ts
      simulationStore.ts
      uiStore.ts

    services/
      api.ts              # HTTP API 封装
      irBuilder.ts        # IR 构建逻辑

    schemas/
      ir.ts               # Zod Schema 定义
      project.ts

    types/
      index.ts            # TypeScript 类型定义

    hooks/
      useKeyboardShortcuts.ts
      useAutoSave.ts
      useCanvasHistory.ts
      useConnectionValidator.ts

    utils/
      layouts.ts          # 自动布局算法
      id.ts               # ID 生成

    styles/
      index.css           # 全局样式 + CSS 变量
      themes.css

  public/
    boards/               # 板卡配置文件
      xilinx_zynq7000.json
      altera_cyclonev.json

  resources/              # 图标等静态资源
    icon.png
```

### 20.3 启动开发

```bash
# 启动前端开发服务器
cd frontend
npm run dev

# 另开终端，启动后端
cd backend
python main.py

# 前端 Electron 窗口通过 electron-vite 启动
npm run dev:electron
```

---

## 21. 开发阶段划分

### 第一阶段：核心画布（第 1-4 周）

**目标**：可交互的节点式编辑器原型

- [ ] 1.1 项目脚手架搭建（Electron + React + Vite）
- [ ] 1.2 ReactFlow 画布集成（缩放、平移、拖拽、框选）
- [ ] 1.3 自定义 BaseModuleNode 组件（Header + 端口 Handle + Footer）
- [ ] 1.4 端口拖拽连线功能
- [ ] 1.5 连线规则校验（方向检查、环路检测）
- [ ] 1.6 边标签编辑（Wire Name）
- [ ] 1.7 左侧模块库面板（内置模板 + 搜索）
- [ ] 1.8 右侧属性面板（选中节点/边的属性编辑）
- [ ] 1.9 右键上下文菜单
- [ ] 1.10 画布状态管理（Zustand canvasStore）
- [ ] 1.11 撤销/重做（快照模式）

### 第二阶段：代码生成对接（第 5-6 周）

**目标**：画布 -> IR -> 后端 -> Verilog 完整链路

- [ ] 2.1 IR 构建逻辑（irBuilder.ts + Zod 校验）
- [ ] 2.2 API Service Layer 封装
- [ ] 2.3 底部代码预览面板（Monaco Editor）
- [ ] 2.4 生成 Top 模块功能（请求/展示/保存）
- [ ] 2.5 生成 Testbench 功能
- [ ] 2.6 仿真配置对话框
- [ ] 2.7 工程保存/加载（.fpga.json）
- [ ] 2.8 最近文件列表

### 第三阶段：封装与高级特性（第 7-8 周）

**目标**：模块封装、板卡配置、导入

- [ ] 3.1 封装模块（框选 -> 对话框 -> 折叠）
- [ ] 3.2 封装展开/折叠动画
- [ ] 3.3 WrappedModuleNode 组件
- [ ] 3.4 自定义模块模板（添加到模块库）
- [ ] 3.5 板卡 IP 配置对话框
- [ ] 3.6 BoardIPNode 组件
- [ ] 3.7 注释节点（AnnotationNode）
- [ ] 3.8 Verilog 文件导入（解析 + 自动创建节点）
- [ ] 3.9 导入层次处理（封装或平铺）

### 第四阶段：仿真联动（第 9-11 周）

**目标**：仿真编译/运行 + 波形可视化

- [ ] 4.1 仿真探针标记（边上标记 + 信号列表）
- [ ] 4.2 编译功能（F5）+ 日志面板
- [ ] 4.3 运行仿真（F6）+ 状态跟踪
- [ ] 4.4 VCD 解析对接
- [ ] 4.5 Canvas 波形渲染组件（基础版）
- [ ] 4.6 时间轴缩放/平移
- [ ] 4.7 光标标记与 ΔT 测量
- [ ] 4.8 信号值 tooltip

### 第五阶段：界面优化（第 12-13 周）

**目标**：布局、主题、交互优化

- [ ] 5.1 dagre 自动布局（Ctrl+L）
- [ ] 5.2 端口对齐后处理
- [ ] 5.3 暗色/亮色主题切换
- [ ] 5.4 网格吸附切换
- [ ] 5.5 面板拖拽调整大小
- [ ] 5.6 节点拖入画布 + 创建流程优化
- [ ] 5.7 加载/保存进度动画
- [ ] 5.8 状态栏信息完善

### 第六阶段：测试与发布（第 14-15 周）

**目标**：E2E 测试、打包、文档

- [ ] 6.1 Playwright E2E 测试（核心流程）
- [ ] 6.2 Electron 打包配置（electron-builder）
- [ ] 6.3 性能优化（画布虚拟化、波形 Web Worker）
- [ ] 6.4 用户手册（VitePress）
- [ ] 6.5 错误边界 + 全局异常处理
- [ ] 6.6 v0.1.0 发布

---

## 附录 A：前后端类型映射

| 前端 TypeScript / Zod | 后端 Python / Pydantic |
|------------------------|------------------------|
| `z.number().int().min(1).default(1)` | `int = Field(default=1, ge=1)` |
| `z.enum(['input','output','inout'])` | `PortDirection(str, Enum)` |
| `z.string().nullable().optional()` | `Optional[str] = None` |
| `z.record(z.any()).default({})` | `dict = Field(default_factory=dict)` |
| `z.tuple([z.number(), z.number()])` | `tuple[float, float]` |
| `z.array(PortSchema)` | `list[Port]` |

## 附录 B：前端依赖版本清单

```json
{
  "dependencies": {
    "@xyflow/react": "^12.4.0",
    "@monaco-editor/react": "^4.6.0",
    "zustand": "^5.0.0",
    "zod": "^3.23.0",
    "dagre": "^0.8.5",
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  },
  "devDependencies": {
    "@electron-vite": "^2.0.0",
    "@tailwindcss/vite": "^4.0.0",
    "electron": "^30.0.0",
    "electron-builder": "^24.0.0",
    "playwright": "^1.45.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0"
  }
}
```

---

> 本文档与后端 `FPGA可视化编程工具-实现路径与工具方案.md` 配合使用。
> 后端 API 文档参考 `FPGA_Backend_Manual_CN.pdf`。
> 后续开发过程中本设计书将持续更新，以反映实际实现细节。
