# FPGA 可视化编程工具 — 使用与测试手册

> **版本**：0.3.0  
> **更新日期**：2026-05-02  
> **适用对象**：开发者、测试人员、用户  
> **本次更新**：前端完全重写（参考设计 UI）、前后端字段命名对齐、全部 API 接通、修复 @xyflow/react v12 兼容性  

---

## 目录

1. [项目概述](#1-项目概述)  
2. [环境要求](#2-环境要求)  
3. [项目结构](#3-项目结构)  
4. [快速启动](#4-快速启动)  
5. [后端 API 参考](#5-后端-api-参考)  
   - 5.1 [健康检查](#51-健康检查-get-apihealth)  
   - 5.2 [生成 Top 模块](#52-生成-top-模块-post-apigeneratetop)  
   - 5.3 [生成 Testbench](#53-生成-testbench-post-apigeneratetestbench)  
   - 5.4 [解析 Verilog](#54-解析-verilog-post-apiparseverilog)  
   - 5.5 [解析 VCD 波形](#55-解析-vcd-波形-post-apiparsevcd)  
   - 5.6 [保存工程](#56-保存工程-post-apiprojectsave)  
   - 5.7 [加载工程](#57-加载工程-post-apiprojectload)  
   - 5.8 [编译](#58-编译-postapisimulatecompile)  
   - 5.9 [运行仿真](#59-运行仿真-postapisimulaterun)  
6. [前端使用指南](#6-前端使用指南)  
   - 6.1 [整体布局](#61-整体布局)  
   - 6.2 [菜单栏](#62-菜单栏)  
   - 6.3 [工具栏](#63-工具栏)  
   - 6.4 [模块库与左侧面板](#64-模块库与左侧面板)  
   - 6.5 [画布操作](#65-画布操作)  
   - 6.6 [连线系统](#66-连线系统)  
   - 6.7 [属性面板](#67-属性面板)  
   - 6.8 [代码预览与底部面板](#68-代码预览与底部面板)  
   - 6.9 [主题切换](#69-主题切换)  
   - 6.10 [键盘快捷键](#610-键盘快捷键)  
7. [完整工作流程](#7-完整工作流程)  
8. [测试指南](#8-测试指南)  
9. [常见问题](#9-常见问题)  
10. [附录](#10-附录)  

---

## 1. 项目概述

FPGA 可视化编程工具是一套基于 Web 的 FPGA 图形化开发环境。用户通过在画布上拖放模块、连接端口来构建数字电路，系统自动生成 Verilog 代码、Testbench，并可驱动仿真器完成验证。

### 核心架构

```
前端 (React + TypeScript)          后端 (FastAPI + Python)
┌─────────────────────────┐        ┌──────────────────────────┐
│  画布 (ReactFlow)        │  IR    │  代码生成器 (Jinja2)      │
│  模块库                   │ ────→ │  仿真调度器               │
│  属性编辑器               │  JSON  │  波形解析器 (VCD)         │
│  Monaco 代码预览          │ ←──── │  工程文件管理             │
│  主题切换 (明/暗)         │        │                         │
└─────────────────────────┘        └──────────────────────────┘

中间表示 (IR)：前端画布状态 ⇄ 后端生成的唯一 JSON 交换格式
```

### 关键特性

- 19 个内置模块（基本门电路、组合逻辑、时序逻辑、IO 接口）
- 拖放式模块放置，端口对齐连线
- 连线验证（方向检查、多驱动防止、自连接/重复连接检测）
- 一键生成 Verilog Top 模块和 Testbench
- Monaco Editor 语法高亮代码预览
- 明/暗双主题，CSS 变量驱动即时切换
- 前后端分离，Vite 代理 /api 到 FastAPI 后端
- .fpga.json 工程文件持久化

---

## 2. 环境要求

### 后端

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.11+ | 建议 3.12 |
| pip | 最新 | 随 Python 安装 |
| 虚拟环境 | venv | 隔离依赖 |

**Python 依赖（requirements.txt）：**

```
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
pydantic>=2.0.0
jinja2>=3.1.0
pytest>=8.0.0
pytest-asyncio>=0.25.0
httpx>=0.28.0
```

### 前端

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Node.js | 18+ | 建议 24 LTS |
| npm | 9+ | 随 Node 安装 |
| 浏览器 | Chrome / Edge / Firefox 最新 | 支持 ES2023 |

**前端依赖（package.json 核心）：**

```
react 19, react-dom 19
@xyflow/react 12 (ReactFlow)
zustand 5 (状态管理)
@monaco-editor/react (代码编辑器)
dagre (布局算法)
lucide-react (图标库)
motion (动画库, framer-motion)
tailwindcss 4, @tailwindcss/vite
vite 8
```

### 可选（仿真功能需要）

| 组件 | 说明 |
|------|------|
| ModelSim / Questa | 商业仿真器，用于编译和运行仿真 |
| Icarus Verilog (iverilog) | 开源 Verilog 仿真器 |

---

## 3. 项目结构

```
project/
├── backend/                        # 后端 (Python + FastAPI)
│   ├── main.py                     # 入口：FastAPI app 实例，CORS，路由挂载
│   ├── requirements.txt            # Python 依赖
│   ├── pytest.ini                  # pytest 配置
│   ├── app/
│   │   ├── routes.py               # 所有 9 个 API 端点定义
│   │   ├── models/
│   │   │   └── ir.py               # IR 数据模型 (Pydantic v2)
│   │   ├── generators/
│   │   │   ├── top.py              # Top 模块生成器 (Jinja2)
│   │   │   ├── testbench.py        # Testbench 生成器 (Jinja2)
│   │   │   └── templates/
│   │   │       ├── top.v.j2        # Top 模板
│   │   │       └── testbench.v.j2  # Testbench 模板
│   │   ├── parser/
│   │   │   └── verilog_parser.py   # Verilog 解析器
│   │   ├── simulator/
│   │   │   ├── base.py             # 仿真器抽象基类
│   │   │   └── modelsim.py         # ModelSim 实现
│   │   └── utils/
│   │       └── vcd_parser.py       # VCD 波形解析器
│   └── tests/
│       ├── test_api.py             # API 端点测试 (23 个用例)
│       └── test_ir.py              # IR 模型测试
│
├── frontend/                       # 前端 (React + TypeScript)
│   ├── vite.config.ts              # Vite 配置 (代理 /api、路径别名)
│   ├── tsconfig.app.json           # TypeScript 配置
│   ├── index.html                  # HTML 入口
│   └── src/
│       ├── main.tsx                # React 入口
│       ├── App.tsx                 # 主布局 (菜单+工具栏+面板+画布+状态栏)
│       ├── index.css               # 全局样式 + Tailwind + 主题变量
│       ├── types/
│       │   └── index.ts            # 全部 TypeScript 类型定义
│       ├── services/
│       │   └── api.ts              # HTTP API 服务层 (9 个端点)
│       ├── stores/
│       │   ├── uiStore.ts          # UI 状态 (主题/面板/状态栏)
│       │   ├── canvasStore.ts      # 画布状态 (节点/边/连线验证)
│       │   ├── projectStore.ts     # 工程状态 (保存/加载/脏标记)
│       │   ├── moduleLibraryStore.ts # 模块库 (19 个模板/搜索)
│       │   └── simulationStore.ts  # 仿真状态 (编译/运行/波形)
│       └── components/
│           ├── layout/
│           │   ├── Header.tsx      # 顶部工具栏
│           │   └── StatusBar.tsx   # 底部状态栏
│           ├── panels/
│           │   ├── ModuleLibrary.tsx   # 左侧模块库面板
│           │   ├── PropertiesPanel.tsx # 右侧属性编辑面板
│           │   └── BottomPanel.tsx     # 底部面板 (代码/日志/波形)
│           └── canvas/
│               ├── Canvas.tsx      # 画布主视图
│               └── nodes/
│                   └── BaseModuleNode.tsx # 自定义模块节点
│
└── FPGA_VISUAL_TOOL_MANUAL.md      # 本手册
```

---

## 4. 快速启动

### 4.1 启动后端

```bash
# 1. 进入后端目录
cd D:\claude\prj\backend

# 2. 创建并激活虚拟环境（首次）
python -m venv venv
.\venv\Scripts\activate

# 3. 安装依赖（首次）
pip install -r requirements.txt

# 4. 启动服务
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

启动成功标志：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 4.2 启动前端

```bash
# 1. 进入前端目录
cd D:\claude\prj\frontend

# 2. 安装依赖（首次）
npm install

# 3. 启动开发服务器
npm run dev
```

启动成功标志：

```
VITE v8.0.10  ready in 423 ms
➜  Local:   http://localhost:5173/
```

### 4.3 验证服务

**验证后端：**

```powershell
# PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing | Select-Object -ExpandProperty Content
```

期望输出：`{"status":"ok","service":"fpga-visual-tool-backend"}`

**验证前端：**

浏览器打开 `http://localhost:5173`，应看到 FPGA 可视化编程工具完整界面。

### 4.4 访问 API 文档

后端启动后访问：
- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

---

## 5. 后端 API 参考

### 通用说明

- **Base URL**：`http://localhost:8000/api`
- **Content-Type**：`application/json`
- **请求方式**：除 `/health` 为 GET 外，其余均为 POST
- **响应格式**：JSON，统一包含 `success` 字段
- **错误处理**：HTTP 4xx/5xx，响应体包含 `detail` 字段

---

### 5.1 健康检查 `GET /api/health`

检查后端服务是否正常运行。

**请求示例：**

```powershell
# PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get
```

```bash
# curl
curl http://localhost:8000/api/health
```

**响应：**

```json
{
  "status": "ok",
  "service": "fpga-visual-tool-backend"
}
```

**pytest 测试：**

```python
@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
```

---

### 5.2 生成 Top 模块 `POST /api/generate/top`

根据 IR（中间表示）生成顶层 Verilog 模块。

**请求体：**

```json
{
  "ir": {
    "version": "0.1.0",
    "modules": [
      {
        "id": "m1",
        "name": "counter",
        "type": "base",
        "instance_name": "counter_inst",
        "ports": [
          { "name": "clk", "direction": "input", "width": 1, "signed": false },
          { "name": "q", "direction": "output", "width": 4, "signed": false }
        ],
        "position": [0, 0],
        "config": {}
      }
    ],
    "connections": [],
    "wrapped_modules": [],
    "top_module_name": "demo_top"
  }
}
```

**响应：**

```json
{
  "success": true,
  "verilog": "module demo_top (\n  input wire clk,\n  output wire [3:0] q\n);\n\n  counter counter_inst (\n    .clk(clk),\n    .q(q)\n  );\n\nendmodule\n"
}
```

**PowerShell 测试：**

```powershell
$body = @{
  ir = @{
    version = "0.1.0"
    modules = @(
      @{
        id = "m1"
        name = "counter"
        type = "base"
        instance_name = "counter_inst"
        ports = @(
          @{ name = "clk"; direction = "input"; width = 1; signed = $false },
          @{ name = "q"; direction = "output"; width = 4; signed = $false }
        )
        position = @(0, 0)
        config = @{}
      }
    )
    connections = @()
    wrapped_modules = @()
    top_module_name = "demo_top"
  }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8000/api/generate/top" -Method Post -Body $body -ContentType "application/json"
```

**curl 测试：**

```bash
curl -X POST http://localhost:8000/api/generate/top \
  -H "Content-Type: application/json" \
  -d '{"ir":{"version":"0.1.0","modules":[{"id":"m1","name":"counter","type":"base","instance_name":"counter_inst","ports":[{"name":"clk","direction":"input","width":1,"signed":false},{"name":"q","direction":"output","width":4,"signed":false}],"position":[0,0],"config":{}}],"connections":[],"wrapped_modules":[],"top_module_name":"demo_top"}}'
```

**pytest 测试（3 个用例）：**

| 用例 | 说明 |
|------|------|
| `test_generate_top` | 单模块顶层生成 |
| `test_generate_top_empty` | 空模块列表 |
| `test_generate_top_multiple_modules` | 多模块互联 |

---

### 5.3 生成 Testbench `POST /api/generate/testbench`

根据 IR + 仿真配置生成 Verilog Testbench。

**请求体：**

```json
{
  "ir": {
    "version": "0.1.0",
    "modules": [
      {
        "id": "m1",
        "name": "counter",
        "type": "base",
        "ports": [
          { "name": "clk", "direction": "input", "width": 1, "signed": false },
          { "name": "rst_n", "direction": "input", "width": 1, "signed": false },
          { "name": "q", "direction": "output", "width": 4, "signed": false }
        ],
        "position": [0, 0],
        "config": {}
      }
    ],
    "connections": [],
    "wrapped_modules": [],
    "top_module_name": "counter_tb"
  },
  "simulation": {
    "simulator": "iverilog",
    "clock_period_ns": 10.0,
    "reset_cycles": 5,
    "sim_time_us": 100.0,
    "monitored_signals": ["clk", "rst_n", "q"]
  }
}
```

**响应：**

```json
{
  "success": true,
  "verilog": "`timescale 1ns / 1ps\n\nmodule counter_tb;\n  reg clk;\n  reg rst_n;\n  wire [3:0] q;\n\n  ...\n\nendmodule\n"
}
```

**curl 测试：**

```bash
curl -X POST http://localhost:8000/api/generate/testbench \
  -H "Content-Type: application/json" \
  -d '{"ir":{"version":"0.1.0","modules":[{"id":"m1","name":"counter","type":"base","ports":[{"name":"clk","direction":"input","width":1,"signed":false},{"name":"rst_n","direction":"input","width":1,"signed":false},{"name":"q","direction":"output","width":4,"signed":false}],"position":[0,0],"config":{}}],"connections":[],"wrapped_modules":[],"top_module_name":"counter_tb"},"simulation":{"simulator":"iverilog","clock_period_ns":10.0,"reset_cycles":5,"sim_time_us":100.0,"monitored_signals":[]}}'
```

---

### 5.4 解析 Verilog `POST /api/parse/verilog`

解析 Verilog 文件或目录，提取模块信息（模块名、端口、例化关系）。

**请求体：**

```json
{
  "file_path": "D:/projects/my_design/top.v"
}
```

**响应：**

```json
{
  "success": true,
  "modules": [
    {
      "name": "top",
      "ports": [
        { "name": "clk", "direction": "input", "width": 1 },
        { "name": "led", "direction": "output", "width": 4 }
      ],
      "instantiations": [
        { "module_name": "counter", "instance_name": "u_counter", "connections": {} }
      ]
    }
  ]
}
```

**curl 测试：**

```bash
curl -X POST http://localhost:8000/api/parse/verilog \
  -H "Content-Type: application/json" \
  -d '{"file_path": "D:/path/to/your/module.v"}'
```

**pytest 测试（3 个用例）：** `test_parse_verilog_file`、`test_parse_verilog_directory`、`test_parse_verilog_not_found`

---

### 5.5 解析 VCD 波形 `POST /api/parse/vcd`

解析 VCD（Value Change Dump）波形文件，返回信号变化数据。

**请求体：**

```json
{
  "file_path": "D:/sim_output/waveform.vcd"
}
```

**响应：**

```json
{
  "success": true,
  "waveform": {
    "signals": [
      {
        "name": "clk",
        "width": 1,
        "signed": false,
        "changes": [
          { "time_ns": 0, "value": "0" },
          { "time_ns": 5, "value": "1" },
          { "time_ns": 10, "value": "0" }
        ]
      }
    ],
    "total_time_ns": 1000.0,
    "timescale": "1ns"
  }
}
```

**curl 测试：**

```bash
curl -X POST http://localhost:8000/api/parse/vcd \
  -H "Content-Type: application/json" \
  -d '{"file_path": "D:/path/to/waveform.vcd"}'
```

**pytest 测试（2 个用例）：** `test_parse_vcd`、`test_parse_vcd_not_found`

---

### 5.6 保存工程 `POST /api/project/save`

将完整工程状态保存为 .fpga.json 文件。

**请求体：**

```json
{
  "project": {
    "version": "0.1.0",
    "name": "my_fpga_project",
    "ir": {
      "version": "0.1.0",
      "modules": [],
      "connections": [],
      "wrapped_modules": [],
      "top_module_name": "top"
    },
    "board": null,
    "simulation": null,
    "canvas_state": {}
  },
  "file_path": "D:/projects/my_fpga_project.fpga.json"
}
```

**响应：**

```json
{
  "success": true,
  "path": "D:\\projects\\my_fpga_project.fpga.json"
}
```

**curl 测试：**

```bash
curl -X POST http://localhost:8000/api/project/save \
  -H "Content-Type: application/json" \
  -d '{"project":{"version":"0.1.0","name":"test","ir":{"version":"0.1.0","modules":[],"connections":[],"wrapped_modules":[],"top_module_name":"top"},"board":null,"simulation":null,"canvas_state":{}},"file_path":"test_output.fpga.json"}'
```

---

### 5.7 加载工程 `POST /api/project/load`

加载 .fpga.json 工程文件。

**请求体：**

```json
{
  "file_path": "D:/projects/my_fpga_project.fpga.json"
}
```

**响应：**

```json
{
  "success": true,
  "project": {
    "version": "0.1.0",
    "name": "my_fpga_project",
    "ir": { "version": "0.1.0", "modules": [], "connections": [], "wrapped_modules": [], "top_module_name": "top" },
    "board": null,
    "simulation": null,
    "canvas_state": {}
  }
}
```

**curl 测试：**

```bash
curl -X POST http://localhost:8000/api/project/load \
  -H "Content-Type: application/json" \
  -d '{"file_path": "test_output.fpga.json"}'
```

---

### 5.8 编译 `POST /api/simulate/compile`

使用 ModelSim 编译 HDL 源文件。

> ⚠️ 需要安装 ModelSim/Questa 仿真器。

**请求体：**

```json
{
  "sources": ["D:/design/top.v", "D:/design/counter.v"],
  "work_dir": "D:/sim_work"
}
```

**响应：**

```json
{
  "success": true,
  "stdout": "ModelSim> vlib work\nModelSim> vlog top.v\n...",
  "stderr": "",
  "errors": [],
  "warnings": []
}
```

---

### 5.9 运行仿真 `POST /api/simulate/run`

运行仿真并生成 VCD 波形文件。

> ⚠️ 需要安装 ModelSim/Questa 仿真器。

**请求体：**

```json
{
  "top_module": "counter_tb",
  "sim_time": "100us",
  "work_dir": "D:/sim_work",
  "sources": ["D:/design/counter.v", "D:/design/counter_tb.v"]
}
```

**响应：**

```json
{
  "success": true,
  "vcd_path": "D:/sim_work/counter_tb.vcd",
  "stdout": "simulation finished...",
  "errors": [],
  "warnings": []
}
```

---

### API 端点速查表

| # | 方法 | 端点 | 功能 | 需要仿真器 |
|---|------|------|------|:---:|
| 1 | GET | `/api/health` | 健康检查 | |
| 2 | POST | `/api/generate/top` | 生成顶层模块 | |
| 3 | POST | `/api/generate/testbench` | 生成 Testbench | |
| 4 | POST | `/api/parse/verilog` | 解析 Verilog | |
| 5 | POST | `/api/parse/vcd` | 解析 VCD 波形 | |
| 6 | POST | `/api/project/save` | 保存工程 | |
| 7 | POST | `/api/project/load` | 加载工程 | |
| 8 | POST | `/api/simulate/compile` | 编译 | ✅ |
| 9 | POST | `/api/simulate/run` | 运行仿真 | ✅ |

---

## 6. 前端使用指南

### 6.1 整体布局

```
┌──────────────────────────────────────────────────────┐
│ Header (bg-primary 深蓝)                               │
│ 🖥 FPGA Visual Builder  File Edit Testbench │ 💾SAVE ✨LAYOUT 📝GENERATE ▶SIMULATE │
├────────────┬────────────────────────┬────────────────┤
│ ModuleLibrary │                    │ PropertiesPanel│
│ (w-64)       │   Canvas (flex-1)    │ (280px 可折叠)  │
│              │                      │                │
│ 🔍 搜索      │ ReactFlow 节点+连线  │ ⚙ 属性编辑器   │
│ ⊿ 门电路    │ 背景网格 · 控件 · 小地图│ 模块/连线详情  │
│ ∑ 组合逻辑  │                      │ 端口列表       │
│ ⏳ 时序逻辑  │ 节点可拖拽移动        │ 配置与删除     │
│ ⚡ IO接口    │ drop 精确定位         │               │
│              │ 连线方向/多驱/自连验证 │               │
├────────────┴────────────────────────┴────────────────┤
│ BottomPanel (motion 可折叠, h=200)  代码 │ 日志 │ 波形 │
│ ┌──────────────────────────────────────────────────┐ │
│ │ Monaco Editor — Verilog 语法高亮 · 暗/亮自适应    │ │
│ └──────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────┤
│ StatusBar (h-6)  ● 就绪 │ Nodes:3 | Edges:5 │ SNAP  LIGHT │
└──────────────────────────────────────────────────────┘
```

### 6.2 Header 工具栏（合并菜单栏 + 工具栏）

v0.3.0 将原 MenuBar 和 Toolbar 合并为单一 Header 组件（深蓝 bg-primary h-12）。

**左侧区域：**
- 🖥 FPGA Visual Builder 标题 + File / Edit / Testbench 导航按钮

**右侧按钮组：**

| 按钮 | 图标 | 功能 |
|------|------|------|
| SAVE | 💾 Save | 调用 buildIR + saveProject API，保存为 .fpga.json |
| LAYOUT | ✨ Wand2 | dagre 自动布局排布模块 |
| GENERATE | 📝 Code | 调用 /api/generate/top，结果显示在底部 CODE 面板 |
| SIMULATE | ▶ Play | 打开底部日志面板（完整仿真待后端 ModelSim） |

按钮位于 bg-white/10 半透明圆角容器内，使用 lucide-react 图标 + 大写标签，竖线分隔。

### 6.3 模块库与左侧面板

### 6.4 模块库与左侧面板

左侧面板包含 3 个标签页：

**标签页说明：**

| 标签 | 功能 |
|------|------|
| 模块库 | 浏览、搜索、拖放模块到画布 |
| 信号 | 查看仿真监测信号列表 |
| 文件 | 浏览项目文件结构 |

**模块库 19 个内置模块：**

| 分类 | 模块 | 端口数 |
|------|------|:---:|
| 基本门电路 | and_gate | 3 |
| | or_gate | 3 |
| | not_gate | 2 |
| | xor_gate | 3 |
| | nand_gate | 3 |
| | nor_gate | 3 |
| 组合逻辑 | mux_2to1 | 4 |
| | decoder_2to4 | 3 |
| | encoder_4to2 | 3 |
| | adder_n | 5 |
| 时序逻辑 | d_flipflop | 5 |
| | register_n | 5 |
| | counter_n | 5 |
| | shift_reg | 5 |
| IO 接口 | gpio_input | 2 |
| | gpio_output | 2 |
| | uart_tx | 6 |
| | uart_rx | 5 |

**添加模块的两种方式：**

1. **拖放**：从模块库拖动模块到画布，在目标位置释放鼠标。系统使用 `screenToFlowPosition()` 将屏幕坐标精确转换为画布坐标，模块准确定位在释放位置
2. **点击**：直接点击模块卡片，模块按阶梯式偏移自动排列（每次偏移 80px 纵向 / 250px 横向），避免堆叠重叠

**模块库 UI 改进：**
- 搜索框带放大镜图标，`focus` 时显示蓝色光晕
- 分类筛选使用彩色 `chip` 标签（全部/⊿ 门电路/∑ 组合逻辑/⏳ 时序逻辑/⚡ IO接口）
- 模块卡片带类型颜色圆点 + 发光效果，hover 时显示 `＋` 图标并高亮边框
- 分类可折叠，折叠状态旋转箭头指示器
- 每个分类标题右侧显示模块数量 badge

**搜索模块：**

在搜索框中输入关键字（如 "gate"、"uart"、"counter"），列表即时过滤。同时可通过分类 chip 按钮缩小范围。

### 6.5 画布操作

**ReactFlow 画布提供以下交互：**

| 操作 | 方式 |
|------|------|
| 平移画布 | 鼠标左键拖动空白区域 / 中键拖动 / 触控板双指滑动 |
| 缩放 | 滚轮 / 触控板捏合 |
| 选中模块 | 单击模块节点（显示蓝色外发光 + 阴影） |
| 选中连线 | 单击连线（高亮为强调色，线宽加粗） |
| 多选 | 按住 Shift 拖动框选 |
| 移动模块 | **拖动模块节点**（`nodesDraggable={true}`，所有模块可自由拖动） |
| 删除选中 | Delete 或 Backspace 键 |
| 取消选中 | 单击画布空白区域 |

**拖放定位修复 (v0.2.0)：**
- 旧版使用 `clientX - 260` 硬编码偏移，模块堆叠在同一位置
- 新版使用 `screenToFlowPosition()` 精确转换屏幕坐标为画布坐标
- 拖放模块准确定位在鼠标释放位置，支持画布缩放/平移后的精确放置

**模块节点外观（v0.2.0 新设计）：**

```
┌─────────────────────────┐
│  ◆ counter_inst    [IP] │  ← 头部（渐变背景 + 类型 badge）
├─────────────────────────┤
│  ● clk           q ●    │  ← 端口带发光圆点手柄
│  ● rst_n     [双向]●    │     绿=输入 红=输出 黄=双向
│  ● en                  │     输入在左侧，输出/双向在右侧
├─────────────────────────┤
│       COUNTER_N          │  ← 底部：原始模块名（小字大写）
└─────────────────────────┘
```
- 圆角 12px（rounded-xl），选中时带 3px 蓝色光环 + 大阴影
- 端口手柄 10px 直径，白色边框 2.5px，hover 时放大 1.3×
- 底部原始模块名以大写小字显示，背景透明
- 头部使用渐变背景（类型色透明→半透明）

### 6.6 连线系统

**连线规则（自动验证）：**

| 规则 | 说明 |
|------|------|
| 方向匹配 | output → input，或 inout ↔ inout。input → output 被拒绝 |
| 禁止多驱动 | 一个 input 端口只能被一根线驱动 |
| 禁止自连接 | 模块不能连接自身 |
| 禁止重复连线 | 同一对端口不能连两次 |

**连线步骤：**

1. 将鼠标悬停在输出端口（右侧绿点）上
2. 按住鼠标左键拖出连线
3. 将连线拖到目标模块的输入端口（左侧红点）上
4. 释放鼠标，连线生成

连线标签自动命名为 `{模块名}_{端口名}` 格式。

**连线外观：**

| 状态 | 样式 |
|------|------|
| 默认 | 灰色 smoothstep 曲线 |
| 选中 | 高亮强调色 |
| 探测信号 | 橙色 |

### 6.7 属性面板

点击画布上的模块或连线，右侧属性面板显示详情。

**模块属性：**

| 字段 | 说明 |
|------|------|
| 例化名 | 模块在顶层中的实例名称 |
| 类型 | base / wrapped / board_ip |
| 模块名 | 原始 Verilog 模块名 |
| 坐标 | 画布位置 (x, y) |
| 端口列表 | 所有端口：名称、方向、位宽 |
| 配置 | 模块参数（如波特率） |
| 删除模块 | 红色按钮，删除节点及相关连线 |

**连线属性：**

| 字段 | 说明 |
|------|------|
| 信号名 | wire 名称 |
| 源模块 | 驱动模块 ID |
| 目标模块 | 被驱动模块 ID |
| 源端口 | 输出端口名 |
| 目标端口 | 输入端口名 |
| 删除连线 | 红色按钮 |

### 6.8 代码预览与底部面板

底部面板包含 3 个标签页：

**代码标签（Code）：**

- 集成 Monaco Editor，支持 Verilog 语法高亮
- 点击工具栏 **Top** 或 **TB** 按钮后，后端生成的代码自动显示在此
- 支持直接编辑、复制（Ctrl+C）、缩进调整
- 代码字体：Cascadia Code / Fira Code / JetBrains Mono（连字支持）
- 明暗主题跟随全局设置自动切换

**日志标签（Log）：**

- 显示仿真运行状态（运行中/完成）
- 输出编译/仿真 stdout 和 stderr
- 警告和错误消息以颜色区分（黄色/红色）

**波形标签（Waveform）：**

- 加载 VCD 文件后显示信号列表
- 显示：信号名、位宽、变化次数
- 运行时：总时间、时标、信号总数

### 6.9 主题切换

**两种主题（v0.2.0 全新设计）：**

| 属性 | 暗色 (Dark) | 亮色 (Light) |
|------|------------|------------|
| 主背景 | GitHub Dark (#0d1117) | 纯白 (#ffffff) |
| 次背景 | (#161b22) | (#f6f8fa) |
| 画布 | 深蓝黑 (#0f1729) | 浅灰 (#f0f2f5) |
| 强调色 | 蓝 (#58a6ff) | 蓝 (#0969da) |
| 节点-基础 | 蓝 (#58a6ff) | 蓝 (#0969da) |
| 节点-封装 | 紫 (#bc8cff) | 紫 (#8250df) |
| 节点-板载IP | 橙 (#f0883e) | 橙 (#d84b00) |
| 端口-输入 | 绿 (#3fb950) | 绿 (#1a7f37) |
| 端口-输出 | 红 (#f85149) | 红 (#cf222e) |
| 端口-双向 | 黄 (#d29922) | 黄 (#9a6700) |

**设计风格：**
- 整体采用 GitHub 风格配色，专业 IDE 外观
- 暗色主题默认启用（适合 FPGA 开发环境）
- 面板和节点带圆角（8-12px）、柔和阴影
- 按钮有 hover/active 过渡动画，`active:scale-95` 点击反馈
- 强调按钮带发光阴影 (`shadow-glow`)
- 滚动条深色细条 (6px)，hover 时变亮

**切换方式：**

1. 点击状态栏右侧的 **☀ 亮色** / **🌙 暗色** 按钮
2. 主题状态持久化在 localStorage (`fpga-theme`) 中
3. 页面刷新后保留用户选择
4. Monaco Editor 自动跟随全局主题（vs-dark / vs）

### 6.10 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+N` | 新建项目 |
| `Ctrl+O` | 打开项目 |
| `Ctrl+S` | 保存 |
| `Ctrl+Shift+S` | 另存为 |
| `Ctrl+Z` | 撤销 |
| `Ctrl+Y` / `Ctrl+Shift+Z` | 重做 |
| `Ctrl+A` | 全选 |
| `Ctrl+B` | 切换左侧面板 |
| `Ctrl+J` | 切换底部面板 |
| `Ctrl+Shift+P` | 切换右侧面板 |
| `Ctrl+=` | 放大画布 |
| `Ctrl+-` | 缩小画布 |
| `Ctrl+0` | 适应画布 |
| `Delete` / `Backspace` | 删除选中 |
| `F5` | 生成 Top 模块 |
| `F6` | 生成 Testbench |
| `F7` | 编译 |
| `F8` | 仿真 |
| `Shift + 拖动` | 框选多个模块 |

---

## 7. 完整工作流程

### 示例：构建一个计数器 + 门控的数字电路

**步骤 1：启动服务**

```powershell
# 终端 1：启动后端
cd D:\claude\prj\backend
& "D:\claude\prj\backend\venv\Scripts\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 终端 2：启动前端
cd D:\claude\prj\frontend
npm run dev
```

**步骤 2：添加模块到画布**

1. 浏览器打开 `http://localhost:5173`
2. 左侧面板 "模块库" 标签
3. 在 "时序逻辑" 分组中，点击 **counter_n** → 模块出现在画布
4. 在 "基本门电路" 分组中，点击 **and_gate** → 模块出现在画布
5. 在 "IO 接口" 分组中，点击 **gpio_output** → 模块出现在画布

**步骤 3：排列模块**

- 拖动三个模块到合适位置（counter 左侧，and_gate 中间，gpio_output 右侧）

**步骤 4：连接端口**

- 从 counter_n 的 `count`（右侧红点）拖一条线到 and_gate 的 `a`（左侧绿点）
- 从 counter_n 的 `overflow` 拖一条线到 and_gate 的 `b`
- 从 and_gate 的 `y` 拖一条线到 gpio_output 的 `data_out`

**步骤 5：生成代码**

1. 点击工具栏 **Top** 按钮（或按 F5）
2. 底部面板自动切换到 "代码" 标签，显示生成的 Verilog 代码
3. Monaco Editor 中显示带语法高亮的顶层模块代码

**步骤 6：生成 Testbench**

1. 点击工具栏 **TB** 按钮（或按 F6）
2. 底部面板显示生成的 Testbench 代码（含时钟生成、复位序列、DUT 例化等）

**步骤 7：保存工程**

- 点击工具栏 💾 保存按钮，或按 Ctrl+S
- 工程保存为 .fpga.json 文件

**步骤 8：主题切换**

- 点击状态栏右侧 **☀ 亮色** 按钮切换到暗色主题
- 再次点击可切回亮色

---

## 8. 测试指南

### 8.1 运行后端测试

```powershell
cd D:\claude\prj\backend

# 激活虚拟环境
.\venv\Scripts\activate

# 运行全部测试
pytest

# 运行指定测试文件
pytest tests/test_api.py -v

# 运行指定测试用例
pytest tests/test_api.py::test_generate_top -v

# 查看覆盖率（需安装 pytest-cov）
pytest --cov=app --cov-report=term-missing
```

### 8.2 测试清单（23 个用例）

**test_api.py — API 端点测试：**

| # | 测试用例 | 验证内容 |
|:---:|------|------|
| 1 | `test_health` | 健康检查返回 200 + status=ok |
| 2 | `test_generate_top` | 单模块 Top 生成，含 module/endmodule |
| 3 | `test_generate_top_empty` | 空 IR 仍正确生成 shell |
| 4 | `test_generate_top_multiple_modules` | 多模块实例化代码 |
| 5 | `test_generate_top_with_connections` | 端口连线声明 |
| 6 | `test_generate_top_wrapped_module` | 封装模块展平 |
| 7 | `test_generate_testbench` | TB 含时钟、复位、DUT |
| 8 | `test_generate_testbench_with_signals` | 监控信号列表 |
| 9 | `test_parse_verilog_file` | 单文件解析模块 |
| 10 | `test_parse_verilog_directory` | 目录批量解析 |
| 11 | `test_parse_verilog_not_found` | 文件不存在 404 |
| 12 | `test_parse_vcd` | VCD 解析信号+变化 |
| 13 | `test_parse_vcd_not_found` | VCD 不存在 404 |
| 14 | `test_save_project` | 保存 JSON，验证磁盘文件 |
| 15 | `test_save_project_creates_dir` | 自动创建父目录 |
| 16 | `test_load_project` | 加载已保存的工程 |
| 17 | `test_load_project_not_found` | 加载不存在的文件 404 |
| 18 | `test_load_project_invalid_json` | 损坏的 JSON 400 |
| 19 | `test_health_response_format` | 响应格式完整性 |
| 20 | `test_generate_top_module_name` | 顶层模块名正确 |
| 21 | `test_parse_verilog_port_types` | 端口方向识别 |
| 22 | `test_parse_vcd_signal_count` | 信号数量完整 |
| 23 | `test_project_roundtrip` | 保存→加载往返数据一致 |

**test_ir.py — IR 模型测试：**

| # | 测试用例 | 验证内容 |
|:---:|------|------|
| 1 | `test_port_creation` | Port 默认值和必填字段 |
| 2 | `test_module_creation` | Module 创建和端口关联 |
| 3 | `test_connection_creation` | Connection 连线定义 |
| 4 | `test_ir_creation` | IR 顶层结构 |
| 5 | `test_project_file_creation` | 工程文件整体 |
| 6 | `test_simulation_config_defaults` | 仿真配置默认值 |
| 7 | `test_port_direction_enum` | 方向枚举 input/output/inout |

### 8.3 前端 TypeScript 类型检查

```powershell
cd D:\claude\prj\frontend

# TypeScript 类型检查（无 emit）
npx tsc --noEmit

# 生产构建
npx vite build
```

### 8.4 手动探索性测试建议

| 场景 | 操作 | 预期结果 |
|------|------|---------|
| 模块放置 | 从库中拖放 5 个模块 | 全部出现在画布不同位置 |
| 连线方向错误 | 尝试 input→input 连线 | 连线不会被创建 |
| 多驱动 | 两个 output 连同一 input | 第二次连接被拒绝 |
| 自连接 | output 连回自身 input | 连线不会被创建 |
| 复制连线 | 同一对端口连两次 | 第二次连接被拒绝 |
| 删除模块 | 删除有连线的模块 | 模块和关联连线均消失 |
| 主题切换 | 切暗→亮→暗 | 界面颜色即时切换 |
| 代码生成 | 放 2 模块 + 连线，点 Top | 代码面板显示 Verilog |
| 面板切换 | Ctrl+B, Ctrl+J | 左右底部面板显示/隐藏 |

---

## 9. 常见问题

### Q1：前端页面打开后空白？

**A**：检查以下几点：
1. `npm install` 是否成功完成
2. 浏览器控制台（F12）是否有报错
3. Vite 代理是否正确指向后端 `http://localhost:8000`
4. 确认 `vite.config.ts` 中 proxy 配置存在

### Q2：点击 Top/TB 按钮后没反应？

**A**：检查后端是否在 8000 端口运行：
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/health" -UseBasicParsing
```
如果连接被拒，启动后端服务。

### Q3：模块拖放没反应？

**A**：v0.2.0 已修复拖放定位问题：
1. 左侧面板处于 "模块库" 标签（非 "信号" 或 "文件"）
2. 拖放现在使用 `screenToFlowPosition()` 精确转换坐标，模块出现在鼠标释放位置
3. 也可直接点击模块名添加（自动阶梯式排列，每次偏移 80px，不会堆叠）
4. 确认浏览器支持 HTML5 Drag and Drop API
5. 模块放置后可**自由拖动**（`nodesDraggable={true}`），拖动时带吸附网格（可关闭）

### Q4：连线拖出后无法连接到目标端口？

**A**：连线有方向验证：
- 输出端口（右侧红点）只能连到输入端口（左侧绿点）
- 输入端口不能被多个输出驱动
- 检查端口颜色：绿=输入、红=输出、黄=双向

### Q5：如何切换到暗色模式？

**A**：三种方式：
1. 点击状态栏最右侧的 "☀ 亮色" 按钮
2. 浏览器开发者工具中执行：`localStorage.setItem('fpga-theme', 'dark')`
3. 主题偏好会自动保存，下次打开页面自动恢复

### Q6：后端显示 "Error loading ASGI app. Could not import module"？

**A**：检查启动命令是否从正确的目录执行：
```powershell
# 正确：在 backend 目录下
cd D:\claude\prj\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
不要写成 `app.main:app`，因为 `main.py` 在 `backend/` 根目录。

### Q7：仿真功能不可用？

**A**：编译和仿真端点（`/api/simulate/compile`、`/api/simulate/run`）需要安装 ModelSim 或 Questa 仿真器。如果未安装，这些端点会返回 500 错误。代码生成功能不依赖仿真器。

---

## 10. 附录

### A. IR JSON 完整结构

```json
{
  "version": "0.1.0",
  "modules": [
    {
      "id": "m1",
      "name": "counter",
      "instance_name": "my_counter",
      "type": "base",
      "ports": [
        {
          "id": "p1",
          "name": "clk",
          "direction": "input",
          "width": 1,
          "signed": false,
          "array_size": null,
          "description": "系统时钟"
        }
      ],
      "position": [120.0, 250.0],
      "config": {}
    }
  ],
  "connections": [
    {
      "id": "c1",
      "src_module": "m1",
      "src_port": "count",
      "dst_module": "m2",
      "dst_port": "a",
      "wire_name": "counter_count"
    }
  ],
  "wrapped_modules": [],
  "top_module_name": "my_top_design"
}
```

### B. 工程文件 (.fpga.json) 结构

```json
{
  "version": "0.1.0",
  "name": "my_project",
  "ir": { /* 上述 IR 结构 */ },
  "board": {
    "board_name": "xilinx_zynq7000",
    "fpga_part": "xc7z020clg400-1",
    "clock_pins": { "clk": "W5" },
    "gpio_map": { "led[0]": "R14" },
    "constraints": ""
  },
  "simulation": {
    "simulator": "iverilog",
    "clock_period_ns": 10.0,
    "reset_cycles": 5,
    "sim_time_us": 100.0,
    "monitored_signals": ["clk", "rst_n", "count"]
  },
  "canvas_state": {
    "viewport": { "x": 0, "y": 0, "zoom": 1.0 }
  }
}
```

### C. 前端状态管理架构

```
┌─────────────────────────────────────────────────┐
│                    Zustand Stores                │
├──────────────┬──────────────┬───────────────────┤
│  uiStore     │  canvasStore  │  projectStore     │
│  主题         │  节点/边      │  工程名/路径       │
│  面板显示     │  选中状态     │  IR/板卡/仿真     │
│  状态消息     │  连线验证     │  脏标记           │
│  生成代码     │  IR 构建     │  保存/加载        │
├──────────────┼──────────────┼───────────────────┤
│ moduleLibraryStore │ simulationStore │           │
│  19 个模板         │  仿真配置      │           │
│  搜索/过滤         │  编译/运行     │           │
│  分类管理          │  波形数据      │           │
│                    │  探测信号      │           │
└────────────────────┴────────────────┴───────────┘
```

### D. 浏览器兼容性

| 浏览器 | 版本 | 状态 |
|--------|------|:---:|
| Google Chrome | 90+ | ✅ 完全支持 |
| Microsoft Edge | 90+ | ✅ 完全支持 |
| Mozilla Firefox | 90+ | ✅ 完全支持 |
| Safari | 15+ | ⚠️ 未充分测试 |

### E. 技术栈版本

| 组件 | 版本 | 许可证 |
|------|------|------|
| React | 19.x | MIT |
| @xyflow/react | 12.x | MIT |
| Zustand | 5.x | MIT |
| Monaco Editor | 0.x | MIT |
| lucide-react | 1.x | ISC |
| motion (framer) | 12.x | MIT |
| Tailwind CSS | 4.x | MIT |
| Vite | 8.x | MIT |
| FastAPI | 0.115+ | MIT |
| Pydantic | 2.x | MIT |
| Jinja2 | 3.1+ | BSD |
| Python | 3.11+ | PSF |

---

> **文档版本**：0.3.0 | **生成日期**：2026-05-02 | **作者**：FPGA Visual Tool Team
> 
> ### 版本历史
> 
> | 版本 | 日期 | 变更 |
> |------|------|------|
> | 0.3.0 | 2026-05-02 | **前端完全重写**：采用专业 FPGA IDE 参考设计 UI。新布局 Header + ModuleLibrary(w-64) + Canvas + PropertiesPanel(280px可折叠) + BottomPanel(200px可折叠) + StatusBar(h-6)。lucide-react 图标 + motion 动画。**修复 @xyflow/react v12 兼容性**：type/value 导入分离。**修复前后端字段命名对齐**：camelCase → snake_case（src_module, wire_name, instance_name）匹配 Pydantic 模型。**修复保存流程**：SAVE 按钮调用 buildIR 确保 IR 不为空。TS 6.0 兼容 + dagre 类型声明。构建通过 tsc + vite build。v0.3.0 发布至 GitHub |
> | 0.2.0 | 2026-05-02 | 修复拖放定位（screenToFlowPosition）、修复模块拖动、全新 UI 设计（GitHub 风格配色、渐变节点头部、发光端口手柄、圆角卡片、分类 chip 筛选）、工具栏按钮样式分级、状态栏状态指示灯、Monaco Editor 暗/亮自动切换 |
> | 0.1.0 | 2026-05-02 | 初始版本：后端 9 API + 23 测试，前端 18 文件 + 19 模块库 + ReactFlow 画布 + Monaco 编辑器 |
