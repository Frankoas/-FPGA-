# -*- coding: utf-8 -*-
"""Generate Chinese PDF manual for FPGA Visual Programming Tool backend."""

import json, os
from fpdf import FPDF

FONT_PATH = r"C:\Windows\Fonts\simhei.ttf"

with open(os.path.join(os.path.dirname(__file__), "manual_cn_content.json"), "r", encoding="utf-8") as f:
    C = json.load(f)


class CNPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.add_font("CJK", "", FONT_PATH)
        self.add_font("CJK", "B", FONT_PATH)

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font("CJK", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, C["header"], align="C")
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("CJK", "", 8)
        self.set_text_color(128, 128, 128)
        pn = self.page_no()
        self.cell(0, 10, f"第 {pn} 页 / 共 {{nb}} 页", align="C")

    def sect(self, title):
        self.set_font("CJK", "B", 15)
        self.set_text_color(25, 60, 120)
        self.cell(0, 10, title)
        self.ln(8)
        self.set_line_width(0.8)
        self.set_draw_color(25, 60, 120)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)

    def subsect(self, title):
        self.set_font("CJK", "B", 12)
        self.set_text_color(50, 90, 160)
        self.cell(0, 8, title)
        self.ln(7)

    def text(self, s):
        self.set_font("CJK", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, s)
        self.ln(1)

    def code(self, s):
        self.set_fill_color(248, 248, 250)
        self.set_line_width(0.3)
        self.set_draw_color(180, 180, 180)
        self.set_font("CJK", "", 8)
        self.set_text_color(40, 40, 40)
        lines = s.split("\n")
        block_h = len(lines) * 4.5 + 5
        if self.get_y() + block_h > self.h - 20:
            self.add_page()
        y0 = self.get_y()
        self.rect(self.l_margin + 2, y0, self.w - self.l_margin - self.r_margin - 4, block_h, style="DF")
        self.set_xy(self.l_margin + 5, y0 + 2)
        for line in lines:
            self.cell(0, 4.5, line)
            self.ln(4.5)
            self.set_x(self.l_margin + 5)
        self.ln(4)

    def item(self, s):
        self.set_font("CJK", "", 10)
        self.set_text_color(40, 40, 40)
        self.cell(6, 6, ">")
        self.multi_cell(0, 6, s)
        self.ln(0.5)

    def num(self, n, s):
        self.set_font("CJK", "", 10)
        self.set_text_color(40, 40, 40)
        self.cell(12, 6, n)
        self.multi_cell(0, 6, s)
        self.ln(0.5)

    def check_break(self, mm=40):
        if self.get_y() + mm > self.h - 20:
            self.add_page()

    def warn(self, s):
        self.set_fill_color(255, 245, 230)
        self.set_line_width(0.4)
        self.set_draw_color(220, 150, 50)
        self.set_font("CJK", "", 9)
        self.set_text_color(140, 80, 20)
        y0 = self.get_y()
        self.set_x(self.l_margin + 4)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 8, 5, s)
        h = self.get_y() - y0 + 2
        self.rect(self.l_margin + 2, y0 + 0.5, self.w - self.l_margin - self.r_margin - 4, h + 1, style="DF")
        self.set_xy(self.l_margin + 6, y0 + 2)
        self.set_font("CJK", "", 9)
        self.set_text_color(140, 80, 20)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 12, 5, s)
        self.ln(3)


def build():
    pdf = CNPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(True, 18)
    pdf.set_left_margin(18)
    pdf.set_right_margin(18)

    # ===== COVER =====
    pdf.add_page()
    pdf.ln(35)
    pdf.set_font("CJK", "B", 30)
    pdf.set_text_color(25, 60, 120)
    pdf.multi_cell(0, 14, C["cover_title"], align="C")
    pdf.ln(6)
    pdf.set_font("CJK", "", 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, C["cover_version"], align="C")
    pdf.ln(14)
    pdf.set_line_width(0.6)
    pdf.set_draw_color(25, 60, 120)
    mid_x = pdf.w / 2
    pdf.line(mid_x - 35, pdf.get_y(), mid_x + 35, pdf.get_y())
    pdf.ln(14)
    pdf.set_font("CJK", "", 12)
    pdf.set_text_color(70, 70, 70)
    for key in ["cover_stack1", "cover_stack2", "cover_stack3", "cover_stack4", "cover_stack5"]:
        pdf.cell(0, 9, C[key], align="C")
        pdf.ln(8)
    pdf.ln(6)
    pdf.set_font("CJK", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, C["cover_desc"], align="C")
    pdf.ln(14)

    # ===== TOC =====
    pdf.add_page()
    pdf.sect(C["toc_title"])
    pdf.set_font("CJK", "", 10)
    pdf.set_text_color(40, 40, 40)
    for num, title in C["toc"]:
        indent = 6 if num.startswith("  ") or "." in num[1:] else 0
        pdf.set_x(18 + indent)
        pdf.cell(0, 7, f"{num}  {title}")
        pdf.ln(7)

    # ============================================================
    # ALL SECTIONS - content defined below via helper functions
    # ============================================================
    print("PDF builder initialized, starting section content...")

    # ================================================================
    # 1. PROJECT OVERVIEW
    # ================================================================
    pdf.add_page()
    pdf.sect("1. 项目概述")
    pdf.subsect("1.1 项目背景与目标")
    pdf.text(
        "FPGA 可视化编程工具旨在为 FPGA 开发者提供一套类似于 ComfyUI 的节点式编程环境。"
        "用户可以通过拖拽模块节点、连接端口的方式完成 FPGA 设计，无需手写繁琐的顶层例化代码。"
        "工具最终可一键生成可综合的 Verilog/VHDL 顶层设计文件，并支持仿真联动与时序调试。"
    )
    pdf.text(
        "后端服务是整个工具的「引擎」，负责：\n"
        "(1) 接收前端画布生成的 IR (中间表示) JSON 数据\n"
        "(2) 根据 IR 生成 Verilog 顶层模块代码\n"
        "(3) 根据 IR 和仿真配置生成 Testbench 测试框架\n"
        "(4) 解析已有的 Verilog 文件，提取模块信息（用于工程导入）\n"
        "(5) 解析仿真产生的 VCD 波形文件（用于波形可视化）\n"
        "(6) 管理工程文件的保存与加载\n"
        "(7) 通过 subprocess 调用 ModelSim/Questa 进行仿真"
    )

    pdf.subsect("1.2 后端核心能力")
    pdf.item("IR 驱动的 Verilog 顶层模块自动生成：自动推断顶层端口、创建 wire 声明、生成模块例化代码")
    pdf.item("Testbench 框架自动生成：时钟生成、复位序列、DUT 例化、激励占位区域、波形导出语句")
    pdf.item("Verilog 文件解析：基于正则表达式的解析器，支持 .v / .sv 文件，提取模块声明和例化关系")
    pdf.item("VCD 波形文件解析：自研解析器，支持 $timescale、$var、$dumpvars、#time 标记和多 bit 总线值")
    pdf.item("ModelSim/Questa 仿真集成：通过 subprocess 异步调用 vlib/vlog/vsim，支持 TCL 脚本批处理")
    pdf.item("工程文件管理：.fpga.json 格式的保存和加载，包含版本化管理")
    pdf.item("完整的测试套件：23 个测试覆盖数据模型、代码生成、VCD 解析、API 端点")

    pdf.subsect("1.3 技术栈总览")
    pdf.text("后端使用的技术栈：")
    pdf.item("Web 框架: FastAPI — 基于 Starlette/Pydantic，异步支持，自动生成 OpenAPI 文档")
    pdf.item("ASGI 服务器: Uvicorn — 支持热重载，高性能异步处理")
    pdf.item("数据校验: Pydantic v2 — 类型安全，自动 JSON Schema 生成")
    pdf.item("模板引擎: Jinja2 — Verilog 代码模板渲染")
    pdf.item("测试框架: pytest + pytest-asyncio + httpx — 异步 HTTP 测试")
    pdf.item("仿真接口: subprocess + TCL 脚本 — 调用 ModelSim/Questa 命令行")
    pdf.item("波形解析: 自研 VCD 解析器 — 无外部依赖，支持基本 VCD 语法")

    # ================================================================
    # 2. ENVIRONMENT SETUP
    # ================================================================
    pdf.add_page()
    pdf.sect("2. 环境准备")

    pdf.subsect("2.1 Python 环境安装")
    pdf.text("后端服务需要 Python 3.11 或更高版本。请按以下步骤操作：")
    pdf.num("第1步", "检查是否已安装 Python：")
    pdf.code("python --version\n# 预期输出: Python 3.11.x 或更高版本")
    pdf.text("如果未安装 Python，请前往 https://www.python.org/downloads/ 下载安装。安装时务必勾选「Add Python to PATH」选项。")
    pdf.num("第2步", "检查 pip（Python 包管理器）是否可用：")
    pdf.code("pip --version\n# 预期输出: pip 24.x 或类似版本信息")
    pdf.num("第3步", "建议使用虚拟环境（可选但推荐）：")
    pdf.code(
        "cd backend\n"
        "python -m venv venv\n\n"
        "# Windows 激活虚拟环境:\n"
        "venv\\Scripts\\activate\n\n"
        "# 激活成功后，命令行前面会显示 (venv) 前缀"
    )
    pdf.num("第4步", "确认 Python 版本满足要求（>= 3.11）：")
    pdf.code(
        "python -c \"import sys; assert sys.version_info >= (3, 11), 'Need Python 3.11+'; print('OK')\"\n"
        "# 预期输出: OK"
    )

    pdf.subsect("2.2 项目依赖安装")
    pdf.text("进入 backend 目录，使用 pip 安装所有依赖：")
    pdf.code("cd backend\npip install -r requirements.txt")
    pdf.text(
        "此命令将安装以下核心依赖：\n"
        "  fastapi >= 0.111.0     — Web 框架\n"
        "  uvicorn >= 0.29.0      — ASGI 服务器\n"
        "  pydantic >= 2.7.0      — 数据校验\n"
        "  jinja2 >= 3.1.4        — 模板引擎\n"
        "  pytest >= 8.2.0        — 测试框架\n"
        "  pytest-asyncio >= 0.23.7 — 异步测试支持\n"
        "  httpx >= 0.27.0        — HTTP 客户端（测试用）\n"
        "  fpdf >= 1.7.0          — PDF 生成（手册生成用）"
    )
    pdf.text("安装过程通常在 1-2 分钟内完成。如果下载速度较慢，可以使用国内镜像：")
    pdf.code("pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple")

    pdf.subsect("2.3 验证安装")
    pdf.text("安装完成后，执行以下命令验证所有依赖是否正确安装：")
    pdf.code(
        "cd backend\n"
        "python -c \"import fastapi; import uvicorn; import pydantic; import jinja2; print('All OK')\"\n\n"
        "# 预期输出: All OK"
    )
    pdf.text("如果没有任何错误输出，说明环境已准备就绪。")
    pdf.text("还可以通过运行测试套件来全面验证：")
    pdf.code("cd backend\npython -m pytest tests/ -v\n# 预期输出: 23 passed")

    # ================================================================
    # 3. START SERVER
    # ================================================================
    pdf.add_page()
    pdf.sect("3. 启动服务")

    pdf.subsect("3.1 开发模式启动（推荐）")
    pdf.text("使用项目自带的 main.py 启动服务（已内置 uvicorn 配置）：")
    pdf.code(
        "cd backend\n"
        "python main.py"
    )
    pdf.text(
        "此命令将以开发模式启动服务，默认监听 http://localhost:8000。\n"
        "服务启动后，你将在终端看到类似以下的输出："
    )
    pdf.code(
        "INFO:     Will watch for changes in these directories: ['D:\\\\...\\\\backend']\n"
        "INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)\n"
        "INFO:     Started reloader process\n"
        "INFO:     Started server process\n"
        "INFO:     Application startup complete."
    )
    pdf.text("看到「Application startup complete.」表示服务已成功启动。")

    pdf.subsect("3.2 命令行启动")
    pdf.text("也可以直接使用 uvicorn 命令启动，支持更多自定义参数：")
    pdf.code("cd backend\nuvicorn main:app --reload --host 0.0.0.0 --port 8000")
    pdf.text("常用参数说明：")
    pdf.item("--reload: 开启热重载，代码修改后自动重启（开发必备）")
    pdf.item("--host 0.0.0.0: 监听所有网络接口（如需局域网内其他设备访问）")
    pdf.item("--port 8000: 指定端口号，可改为任意未占用端口")
    pdf.item("--workers 4: 指定工作进程数（生产环境，不与 --reload 同时使用）")
    pdf.warn("注意：如果端口 8000 被占用，可以换用其他端口如 --port 8001。不要同时启动多个实例监听同一端口。")

    pdf.subsect("3.3 验证服务运行")
    pdf.text("服务启动后，可以通过以下三种方式验证：")
    pdf.num("方式1", "浏览器访问 http://localhost:8000/api/health，应看到 JSON 响应：")
    pdf.code('{"status": "ok", "service": "fpga-visual-tool-backend"}')
    pdf.num("方式2", "使用 curl 命令测试：")
    pdf.code("curl http://localhost:8000/api/health")
    pdf.num("方式3", "打开 Swagger UI 交互式文档（推荐用于手动测试和探索 API）：")
    pdf.code("# 浏览器打开:\nhttp://localhost:8000/docs")
    pdf.text(
        "Swagger UI 页面列出了所有可用的 API 端点。你可以直接在页面上填写参数、\n"
        "发送请求并查看响应结果。这是最方便的手动测试方式。\n"
        "另外，访问 http://localhost:8000/redoc 可以查看 ReDoc 风格的文档。"
    )

    # ================================================================
    # 4. ARCHITECTURE
    # ================================================================
    pdf.add_page()
    pdf.sect("4. 项目架构详解")

    pdf.subsect("4.1 目录结构")
    pdf.text("以下是 backend 目录的完整结构及各文件职责说明：")
    pdf.code(
        "backend/\n"
        "  main.py                  # FastAPI 应用入口，创建 app 实例\n"
        "  requirements.txt         # Python 依赖清单\n"
        "  pyproject.toml           # pytest 测试配置\n"
        "  demo_input.json          # 示例 IR 输入文件（用于快速测试）\n"
        "  generate_manual.py       # PDF 手册生成脚本（英文版）\n"
        "  generate_manual_cn.py    # PDF 手册生成脚本（中文版）\n"
        "  app/\n"
        "    __init__.py             # 包初始化\n"
        "    routes.py               # 所有 API 路由定义（9个端点）\n"
        "    models/\n"
        "      __init__.py\n"
        "      ir.py                 # IR 数据模型定义（Pydantic v2）\n"
        "    generators/\n"
        "      __init__.py\n"
        "      top.py                # 顶层模块 Verilog 代码生成器\n"
        "      testbench.py          # Testbench 代码生成器\n"
        "      templates/\n"
        "        top.v.j2            # 顶层模块 Jinja2 模板\n"
        "        testbench.v.j2      # Testbench Jinja2 模板\n"
        "    parser/\n"
        "      __init__.py\n"
        "      verilog_parser.py     # Verilog 解析器（正则匹配）\n"
        "    simulator/\n"
        "      __init__.py\n"
        "      base.py               # 仿真器抽象基类（接口定义）\n"
        "      modelsim.py           # ModelSim/Questa 仿真器实现\n"
        "    utils/\n"
        "      __init__.py\n"
        "      vcd_parser.py         # VCD 波形解析器（自研）\n"
        "  tests/\n"
        "    __init__.py\n"
        "    test_ir.py              # IR 数据模型测试 (9个)\n"
        "    test_generators.py      # 代码生成器测试 (5个)\n"
        "    test_vcd.py             # VCD 解析器测试 (4个)\n"
        "    test_api.py             # API 端点集成测试 (5个)"
    )

    pdf.subsect("4.2 数据流架构")
    pdf.text(
        "整个后端的数据流是单向的：前端画布 -> IR (JSON) -> 后端处理 -> 生成代码/解析结果。\n"
        "IR (Intermediate Representation) 是前后端之间的唯一交换格式，保证前后端解耦。"
    )
    pdf.code(
        "  +-------------------+\n"
        "  |  前端画布 (React)  |\n"
        "  +--------+----------+\n"
        "           | IR (JSON)\n"
        "           v\n"
        "  +--------+----------+\n"
        "  |  FastAPI 后端服务  |\n"
        "  +--------+----------+\n"
        "           |\n"
        "     +-----+------+-------------+\n"
        "     |            |             |\n"
        "     v            v             v\n"
        "  Top生成器   TB生成器    Verilog/VCD解析器\n"
        "     |            |             |\n"
        "     v            v             v\n"
        "  Jinja2模板   Jinja2模板    Python解析器\n"
        "     |            |             |\n"
        "     v            v             v\n"
        "  Verilog代码  Verilog代码   结构化JSON"
    )

    pdf.subsect("4.3 模块职责说明")
    pdf.text("routes.py (app/routes.py) — API 路由层：")
    pdf.item("定义 9 个 API 端点的请求/响应模型（Pydantic）")
    pdf.item("使用单例模式管理生成器和解析器实例，避免重复初始化")
    pdf.item("统一的异常处理：业务异常返回 HTTP 4xx，系统异常返回 HTTP 5xx")

    pdf.text("models/ir.py (app/models/ir.py) — 数据模型层：")
    pdf.item("定义 8 个核心 Pydantic 模型")
    pdf.item("自动生成唯一 ID（uuid4 前12位十六进制）")
    pdf.item("IR 版本化（version 字段），支持向前/向后兼容")

    pdf.text("generators/ — 代码生成层：")
    pdf.item("top.py: 扁平化模块和连线 -> 推断顶层端口 -> 构建 wire 声明 -> 生成例化语句 -> Jinja2 渲染")
    pdf.item("testbench.py: 提取仿真信号 -> 构建时钟/复位逻辑 -> 生成 DUT 例化 -> 添加 dump 语句 -> Jinja2 渲染")
    pdf.item("Jinja2 模板位于 templates/ 目录，模板与逻辑分离，方便维护")

    pdf.text("parser/verilog_parser.py — 解析层：")
    pdf.item("正则匹配 module 声明、端口定义、例化语句")
    pdf.item("自动去除注释（单行 // 和块注释 /* */）")
    pdf.item("支持 .v / .sv 单文件解析和目录递归解析")
    pdf.item("VHDL 解析为占位实现，生产环境需使用 pyVHDLParser 或 GHDL")

    pdf.text("simulator/ — 仿真层：")
    pdf.item("base.py: 定义 Simulator 抽象基类，声明 compile/run/compile_and_run 统一接口")
    pdf.item("modelsim.py: 通过 asyncio.create_subprocess_exec 异步调用 ModelSim")
    pdf.item("自动生成 TCL 批处理脚本，包含 vcd add -r /* 和 run 命令")
    pdf.item("预留 Icarus Verilog / Verilator 实现扩展点")

    pdf.text("utils/vcd_parser.py — 工具层：")
    pdf.item("自研 VCD 解析器，零外部依赖")
    pdf.item("支持 $timescale（时间单位）、$var（信号定义）、$dumpvars（初始值）、#time（时间标记）")
    pdf.item("正确处理单 bit 值（0/1/x/z）和多 bit 总线值（b1010 格式）")
    pdf.item("解析结果通过 to_dict() 方法输出为前端可直接消费的 JSON 结构")

    # ================================================================
    # 5. IR DATA MODEL
    # ================================================================
    pdf.add_page()
    pdf.sect("5. IR 中间表示数据模型")
    pdf.text(
        "IR (Intermediate Representation) 是前端图形画布与后端代码生成之间的唯一数据交换格式。"
        "所有模型使用 Pydantic v2 定义，位于 app/models/ir.py。"
        "IR 包含版本号字段（version），用于保证向前/向后兼容性。"
    )

    pdf.subsect("5.1 Port — 端口模型")
    pdf.text("描述模块的一个输入/输出/双向端口。")
    pdf.code(
        "class PortDirection(str, Enum):\n"
        "    INPUT  = \"input\"      # 输入端口\n"
        "    OUTPUT = \"output\"     # 输出端口\n"
        "    INOUT  = \"inout\"      # 双向端口\n\n"
        "class Port(BaseModel):\n"
        "    id: str            # 自动生成唯一ID (12位十六进制)\n"
        "    name: str          # 端口名称，如 clk, rst_n, data_in\n"
        "    direction: PortDirection  # 端口方向\n"
        "    width: int = 1     # 位宽，默认1\n"
        "    signed: bool = False  # 有无符号\n"
        "    array_size: int | None  # 数组维度\n"
        "    description: str = ''  # 端口注释/说明"
    )
    pdf.text("JSON 示例：")
    pdf.code('{\n  "name": "clk",\n  "direction": "input",\n  "width": 1,\n  "signed": false\n}')

    pdf.subsect("5.2 Module — 模块模型")
    pdf.text("描述画布上的一个模块节点。")
    pdf.code(
        "class Module(BaseModel):\n"
        "    id: str            # 自动生成唯一ID\n"
        "    name: str          # 模块名（对应 Verilog module 名）\n"
        "    instance_name: str | None  # 用户自定义例化名\n"
        "    type: str = \"base\" # 模块类型: base/wrapped/board_ip\n"
        "    ports: list[Port]  # 端口列表\n"
        "    position: tuple[float,float]  # 画布坐标 (x, y)\n"
        "    config: dict = {}  # 模块参数配置，如 {div_factor: 4}"
    )
    pdf.text("模块类型说明：")
    pdf.item("base — 标准用户定义或从已有工程导入的模块")
    pdf.item("wrapped — 封装后的子电路模块，可在画布上展开/折叠")
    pdf.item("board_ip — 板卡厂商提供的 IP 核（如 PLL、GPIO、UART 等）")

    pdf.subsect("5.3 Connection — 连线模型")
    pdf.text("描述两个端口之间的连线关系，每条连线对应一根 wire。")
    pdf.code(
        "class Connection(BaseModel):\n"
        "    id: str            # 自动生成唯一ID\n"
        "    src_module: str    # 源模块 ID\n"
        "    src_port: str      # 源端口名称\n"
        "    dst_module: str    # 目标模块 ID\n"
        "    dst_port: str      # 目标端口名称\n"
        "    wire_name: str | None  # 用户标注的wire名，为空则自动生成"
    )

    pdf.subsect("5.4 WrappedModule — 封装模块")
    pdf.text("将一组内部模块打包为可复用的封装节点，支持嵌套封装。")
    pdf.code(
        "class WrappedModule(BaseModel):\n"
        "    name: str              # 封装后的模块名\n"
        "    exposed_ports: list[Port]  # 暴露到外部的端口\n"
        "    internal_modules: list[Module]  # 内部子模块\n"
        "    internal_connections: list[Connection]  # 内部连线\n"
        "    internal_wrapped: list[WrappedModule]  # 嵌套封装（递归）"
    )

    pdf.subsect("5.5 IR — 顶层中间表示")
    pdf.text("画布完整状态的抽象，是前后端交换的核心对象。")
    pdf.code(
        "class IR(BaseModel):\n"
        "    version: str = \"0.1.0\"  # IR 版本号\n"
        "    modules: list[Module]    # 顶层模块列表\n"
        "    connections: list[Connection]  # 连线列表\n"
        "    wrapped_modules: list[WrappedModule]  # 封装模块\n"
        "    top_module_name: str = \"top\"  # 顶层模块名"
    )

    pdf.subsect("5.6 ProjectFile — 工程文件")
    pdf.text("完整的工程存档格式（.fpga.json），包含 IR 及所有配置信息。")
    pdf.code(
        "class ProjectFile(BaseModel):\n"
        "    version: str = \"0.1.0\"\n"
        "    name: str = \"untitled\"\n"
        "    ir: IR              # IR 数据\n"
        "    board: BoardConfig | None  # 板卡配置（可选）\n"
        "    simulation: SimulationConfig | None  # 仿真配置（可选）\n"
        "    canvas_state: dict  # UI状态（视口位置、缩放等）"
    )

    pdf.subsect("5.7 SimulationConfig — 仿真配置")
    pdf.code(
        "class SimulationConfig(BaseModel):\n"
        "    simulator: str = \"modelsim\"  # 仿真器: modelsim/questa/icarus\n"
        "    clock_period_ns: float = 10.0  # 时钟周期 (ns)\n"
        "    reset_cycles: int = 10  # 复位持续周期数\n"
        "    sim_time_us: float = 100.0  # 仿真总时长 (us)\n"
        "    monitored_signals: list[str]  # 待抓取信号列表\n"
        "        # 格式: \"module_id.port_name\"，如 \"m1.clk\""
    )

    pdf.subsect("5.8 BoardConfig — 板卡配置")
    pdf.code(
        "class BoardConfig(BaseModel):\n"
        "    board_name: str         # 板卡名称，如 xilinx_zynq7000\n"
        "    fpga_part: str          # FPGA 型号\n"
        "    clock_pins: dict[str,str]  # 时钟引脚映射\n"
        "    gpio_map: dict[str,str]    # GPIO 映射\n"
        "    constraints: str        # 约束文件内容 (.xdc / .qsf)"
    )

    # ================================================================
    # 6. API REFERENCE
    # ================================================================
    pdf.add_page()
    pdf.sect("6. API 接口详细参考")
    pdf.text(
        "所有 API 的基础 URL 为 http://localhost:8000/api。\n"
        "请求和响应均使用 JSON 格式。\n"
        "响应统一包含 \"success\" 字段（布尔值）表示操作是否成功。\n\n"
        "测试 API 有三种方式：\n"
        "(1) 浏览器打开 http://localhost:8000/docs 使用 Swagger UI 交互式测试\n"
        "(2) 使用 curl 命令行测试（Windows PowerShell 亦可）\n"
        "(3) 使用 pytest 自动测试（推荐用于回归测试）\n\n"
        "以下每个接口都提供了功能说明、请求/响应格式、curl 测试命令、PowerShell 测试命令和 pytest 测试命令。"
    )

    # ---------- 6.1 Health ----------
    pdf.check_break(60)
    pdf.subsect("6.1 GET /api/health — 健康检查")
    pdf.text("功能说明：检查后端服务是否正常运行。通常在服务启动后首先调用此接口确认服务可用。")
    pdf.text("请求格式：GET 请求，无需请求体。")

    pdf.text("响应格式：")
    pdf.code(
        'HTTP 200 OK\n'
        'Content-Type: application/json\n\n'
        '{\n'
        '  "status": "ok",\n'
        '  "service": "fpga-visual-tool-backend"\n'
        '}'
    )

    pdf.text("curl 测试命令：")
    pdf.code("curl http://localhost:8000/api/health")

    pdf.text("PowerShell 测试命令：")
    pdf.code("Invoke-RestMethod -Uri http://localhost:8000/api/health | ConvertTo-Json")

    pdf.text("预期结果：返回 HTTP 200，响应体包含 status=\"ok\"。")

    pdf.text("pytest 测试命令：")
    pdf.code("python -m pytest tests/test_api.py::test_health -v")

    pdf.text("测试代码片段（来自 tests/test_api.py）：")
    pdf.code(
        "@pytest.mark.asyncio\n"
        "async def test_health(client: AsyncClient):\n"
        "    resp = await client.get(\"/api/health\")\n"
        "    assert resp.status_code == 200\n"
        "    data = resp.json()\n"
        '    assert data["status"] == "ok"'
    )

    # ---------- 6.2 Generate Top ----------
    pdf.add_page()
    pdf.subsect("6.2 POST /api/generate/top — 生成顶层模块")

    pdf.text("功能说明：")
    pdf.text(
        "这是最核心的 API。接收一个 IR 对象，自动生成完整的 Verilog 顶层模块代码。\n"
        "生成器会自动完成以下工作：\n"
        "(1) 遍历所有模块和封装子模块，扁平化处理\n"
        "(2) 推断顶层端口：未与其他模块连接的端口自动暴露为顶层 I/O，按名称去重\n"
        "(3) 为所有连线生成 wire 声明（使用用户标注的 wire 名或自动生成 w_xxx 格式的名称）\n"
        "(4) 位宽自动匹配：取连线两端中较大的位宽\n"
        "(5) 为所有子模块生成例化语句，未连接的端口悬空处理\n"
        "(6) 通过 Jinja2 模板渲染输出最终的 Verilog 代码"
    )

    pdf.text("请求格式：")
    pdf.code(
        "POST /api/generate/top\n"
        "Content-Type: application/json\n\n"
        "{\n"
        '  "ir": {\n'
        '    "version": "0.1.0",\n'
        '    "modules": [ ... ],\n'
        '    "connections": [ ... ],\n'
        '    "wrapped_modules": [],\n'
        '    "top_module_name": "my_design"\n'
        "  }\n"
        "}"
    )

    pdf.text("响应格式：")
    pdf.code(
        '{\n'
        '  "success": true,\n'
        '  "verilog": "module my_design(...)\\n  ...\\nendmodule\\n"\n'
        '}'
    )

    pdf.text("curl 测试命令（使用项目自带的 demo_input.json）：")
    pdf.code(
        "curl -X POST http://localhost:8000/api/generate/top ^\n"
        "  -H \"Content-Type: application/json\" ^\n"
        "  -d @demo_input.json"
    )

    pdf.text("PowerShell 测试命令：")
    pdf.code(
        "$body = Get-Content demo_input.json -Raw\n"
        "$resp = Invoke-RestMethod -Uri http://localhost:8000/api/generate/top -Method Post -Body $body -ContentType \"application/json\"\n"
        "$resp.success\n"
        "Write-Output $resp.verilog"
    )

    pdf.text("预期结果：返回一段完整的 Verilog 代码，包含 module blinky_demo 声明、input/output 端口声明、wire clk_divided 声明、clk_divider 和 led_controller 的例化。")

    pdf.text("pytest 测试命令：")
    pdf.code("python -m pytest tests/test_api.py::test_generate_top -v")

    # ---------- 6.3 Generate Testbench ----------
    pdf.add_page()
    pdf.subsect("6.3 POST /api/generate/testbench — 生成 Testbench")

    pdf.text("功能说明：")
    pdf.text(
        "根据 IR 和仿真配置自动生成 Testbench 框架代码。\n"
        "生成的 Testbench 包含：\n"
        "(1) 时钟生成逻辑（周期通过 clock_period_ns 可配置）\n"
        "(2) 可配置的复位序列（持续 reset_cycles 个周期后释放）\n"
        "(3) DUT（待测模块）例化\n"
        "(4) 激励信号声明和占位区域（标记 // STIMULUS: 供用户添加测试激励）\n"
        "(5) $dumpfile / $dumpvars 波形导出语句\n"
        "(6) 仿真超时后自动调用 $finish 结束仿真"
    )

    pdf.text("请求格式：")
    pdf.code(
        "POST /api/generate/testbench\n"
        "Content-Type: application/json\n\n"
        "{\n"
        '  "ir": { IR对象 },\n'
        '  "simulation": {\n'
        '    "clock_period_ns": 10.0,\n'
        '    "reset_cycles": 5,\n'
        '    "sim_time_us": 100.0\n'
        "  }\n"
        "}"
    )

    pdf.text("响应格式：")
    pdf.code('{\n  "success": true,\n  "verilog": "module tb_xxx...\\nendmodule\\n"\n}')

    pdf.text("curl 测试命令：")
    pdf.code(
        "curl -X POST http://localhost:8000/api/generate/testbench ^\n"
        "  -H \"Content-Type: application/json\" ^\n"
        "  -d \"{\\\"ir\\\":{\\\"version\\\":\\\"0.1.0\\\",\\\"modules\\\":[],\\\"connections\\\":[],\\\"wrapped_modules\\\":[],\\\"top_module_name\\\":\\\"blinky\\\"},\\\"simulation\\\":{\\\"clock_period_ns\\\":10.0,\\\"reset_cycles\\\":5,\\\"sim_time_us\\\":100.0}}\""
    )

    pdf.text("预期结果：返回 Testbench 代码，包含 tb_blinky 模块声明、clk 生成逻辑（forever #5.0）、rst_n 复位序列（repeat(5)）、$dumpfile / $dumpvars 语句和 $finish 语句。")

    pdf.text("pytest 测试命令：")
    pdf.code("python -m pytest tests/test_api.py::test_generate_testbench -v")

    # ---------- 6.4 Parse Verilog ----------
    pdf.check_break(60)
    pdf.subsect("6.4 POST /api/parse/verilog — 解析 Verilog 文件")

    pdf.text("功能说明：")
    pdf.text(
        "解析指定的 Verilog 文件（或目录），提取其中定义的模块信息。\n"
        "用于「导入已有工程」功能。支持 .v 和 .sv 扩展名。\n"
        "解析结果包括：模块名称、端口列表（方向/位宽/有无符号）、内部子模块例化关系。\n\n"
        "注意：当前为基于正则表达式的解析器（demo 质量），对于复杂的 SystemVerilog 语法\n"
        "（如 generate、interface、parameterized module）可能解析不完整。"
    )

    pdf.text("请求格式：")
    pdf.code(
        "POST /api/parse/verilog\n"
        "Content-Type: application/json\n\n"
        "{\n"
        '  "file_path": "D:/projects/my_module.v"\n'
        "}"
    )

    pdf.text("响应格式：")
    pdf.code(
        '{\n'
        '  "success": true,\n'
        '  "modules": [\n'
        '    {\n'
        '      "name": "counter",\n'
        '      "ports": [\n'
        '        {"name": "clk", "direction": "input", "width": 1},\n'
        '        {"name": "q", "direction": "output", "width": 4}\n'
        '      ],\n'
        '      "instantiations": [...]\n'
        '    }\n'
        '  ]\n'
        '}'
    )

    pdf.text("PowerShell 测试命令：")
    pdf.code(
        "# 1. 创建测试用 Verilog 文件\n"
        'Set-Content -Path test_sample.v -Value @"\n'
        "module counter(input clk, input rst_n, output reg [3:0] q);\n"
        "  always @(posedge clk) q <= q + 1;\n"
        "endmodule\n"
        '"@\n\n'
        "# 2. 调用解析 API\n"
        '$body = ''{"file_path": "test_sample.v"}''\n'
        "$resp = Invoke-RestMethod -Uri http://localhost:8000/api/parse/verilog -Method Post -Body $body -ContentType \"application/json\"\n"
        "$resp.success\n"
        "$resp.modules | ConvertTo-Json"
    )

    pdf.text("预期结果：返回 modules 数组，包含 counter 模块及其 2 个端口（clk 和 q）的信息。")
    pdf.warn("如果文件不存在，返回 HTTP 404 错误。解析器对 generate、interface 等复杂语法支持有限。")

    # ---------- 6.5 Parse VCD ----------
    pdf.check_break(60)
    pdf.subsect("6.5 POST /api/parse/vcd — 解析 VCD 波形文件")

    pdf.text("功能说明：")
    pdf.text(
        "解析仿真产生的 VCD (Value Change Dump) 波形文件，返回结构化的波形数据供前端渲染波形图。\n"
        "解析器支持：\n"
        "  $timescale — 时间单位定义\n"
        "  $var — 信号定义（名称、位宽、ID 代码）\n"
        "  $dumpvars — 初始值\n"
        "  #time — 时间标记\n"
        "  单 bit 值（0/1/x/z）和多 bit 总线值（b1010 格式）"
    )

    pdf.text("请求格式：")
    pdf.code(
        "POST /api/parse/vcd\n"
        "Content-Type: application/json\n\n"
        "{\n"
        '  "file_path": "D:/sim_output/waveform.vcd"\n'
        "}"
    )

    pdf.text("响应格式：")
    pdf.code(
        '{\n'
        '  "success": true,\n'
        '  "waveform": {\n'
        '    "signals": [\n'
        '      {\n'
        '        "name": "clk",\n'
        '        "width": 1,\n'
        '        "signed": false,\n'
        '        "changes": [\n'
        '          {"time_ns": 0, "value": "0"},\n'
        '          {"time_ns": 10, "value": "1"},\n'
        '          {"time_ns": 20, "value": "0"}\n'
        '        ]\n'
        '      }\n'
        '    ],\n'
        '    "total_time_ns": 20,\n'
        '    "timescale": "1ns"\n'
        '  }\n'
        '}'
    )

    pdf.text("每个信号包含一个 changes 数组，记录了每次值变化的时间点和值。total_time_ns 为整个波形的最大时间戳。")

    pdf.text("PowerShell 测试命令：")
    pdf.code(
        "# 1. 创建测试 VCD 文件\n"
        'Set-Content -Path test_wave.vcd -Value @"\n'
        '$timescale 1ns $end\n'
        '$var wire 1 ! clk $end\n'
        '$dumpvars\n'
        '0!\n'
        '$end\n'
        '#10\n'
        '1!\n'
        '"@\n\n'
        "# 2. 调用解析 API\n"
        '$body = ''{"file_path": "test_wave.vcd"}''\n'
        "$resp = Invoke-RestMethod -Uri http://localhost:8000/api/parse/vcd -Method Post -Body $body -ContentType \"application/json\"\n"
        "$resp.success\n"
        "$resp.waveform.signals | ConvertTo-Json -Depth 5"
    )

    pdf.text("预期结果：返回 clk 信号，包含 2 次值变化（0ns 时值为 0，10ns 时值为 1）。")

    pdf.text("pytest 测试命令：")
    pdf.code("python -m pytest tests/test_vcd.py -v")

    # ---------- 6.6 Save Project ----------
    pdf.add_page()
    pdf.subsect("6.6 POST /api/project/save — 保存工程")

    pdf.text("功能说明：")
    pdf.text(
        "将完整的工程数据（包括 IR、板卡配置、仿真配置、画布 UI 状态）保存为 .fpga.json 文件。\n"
        "文件以 UTF-8 编码写入，JSON 格式化输出（indent=2），便于版本控制。\n"
        "目标目录不存在时会自动创建。"
    )

    pdf.text("请求格式：")
    pdf.code(
        "POST /api/project/save\n"
        "Content-Type: application/json\n\n"
        "{\n"
        '  "project": { ProjectFile 对象 },\n'
        '  "file_path": "D:/projects/my_design.fpga.json"\n'
        "}"
    )

    pdf.text("响应格式：")
    pdf.code('{\n  "success": true,\n  "path": "D:/projects/my_design.fpga.json"\n}')

    pdf.text("PowerShell 测试命令：")
    pdf.code(
        "$proj = @{\n"
        '    version = "0.1.0"\n'
        '    name = "my_test_project"\n'
        "    ir = @{\n"
        '        version = "0.1.0"\n'
        "        modules = @()\n"
        "        connections = @()\n"
        "        wrapped_modules = @()\n"
        '        top_module_name = "top"\n'
        "    }\n"
        "}\n"
        "$body = @{ project = $proj; file_path = \"test_project.fpga.json\" } | ConvertTo-Json -Depth 6\n"
        "Invoke-RestMethod -Uri http://localhost:8000/api/project/save -Method Post -Body $body -ContentType \"application/json\""
    )

    pdf.text("预期结果：在当前目录生成 test_project.fpga.json 文件，包含完整的工程数据结构。")

    # ---------- 6.7 Load Project ----------
    pdf.check_break(60)
    pdf.subsect("6.7 POST /api/project/load — 加载工程")

    pdf.text("功能说明：")
    pdf.text(
        "从磁盘加载一个 .fpga.json 工程文件，返回完整的 ProjectFile 对象。\n"
        "文件不存在时返回 HTTP 404 错误。\n"
        "JSON 格式无效时返回 HTTP 400 错误。\n"
        "加载时使用 Pydantic 的 model_validate 对数据进行完整校验。"
    )

    pdf.text("请求格式：")
    pdf.code(
        "POST /api/project/load\n"
        "Content-Type: application/json\n\n"
        "{\n"
        '  "file_path": "test_project.fpga.json"\n'
        "}"
    )

    pdf.text("响应格式：")
    pdf.code(
        '{\n'
        '  "success": true,\n'
        '  "project": {\n'
        '    "version": "0.1.0",\n'
        '    "name": "my_test_project",\n'
        '    "ir": { ... }\n'
        '  }\n'
        '}'
    )

    pdf.text("PowerShell 测试命令（先保存再加载）：")
    pdf.code(
        '$body = ''{"file_path": "test_project.fpga.json"}''\n'
        "$resp = Invoke-RestMethod -Uri http://localhost:8000/api/project/load -Method Post -Body $body -ContentType \"application/json\"\n"
        "$resp.success\n"
        "$resp.project.name"
    )

    pdf.text("预期结果：返回 success=true，project.name 为保存时设置的名称 my_test_project。")

    pdf.text("pytest 集成测试（保存+加载）：")
    pdf.code("python -m pytest tests/test_api.py::test_save_and_load_project -v")

    # ---------- 6.8 Simulate Compile ----------
    pdf.add_page()
    pdf.subsect("6.8 POST /api/simulate/compile — 编译 HDL 源文件")

    pdf.text("功能说明：")
    pdf.text(
        "使用 ModelSim/Questa 的 vlib 和 vlog 命令编译 Verilog 源文件。\n"
        "执行流程：(1) vlib work 创建 work 仿真库；(2) 对每个源文件执行 vlog -work work <file>。\n"
        "编译过程中产生的错误（errors）和警告（warnings）会被捕获并返回给调用者。\n"
        "work_dir 目录不存在时会自动创建。"
    )
    pdf.warn("此接口需要本地安装 ModelSim/Questa，且 vlib/vlog 命令必须在系统 PATH 中，或通过 ModelSimSimulator 的 executable_path 参数指定安装路径。")

    pdf.text("请求格式：")
    pdf.code(
        "POST /api/simulate/compile\n"
        "Content-Type: application/json\n\n"
        "{\n"
        '  "sources": ["src/counter.v", "src/top.v"],\n'
        '  "work_dir": "./sim_work"\n'
        "}"
    )

    pdf.text("响应格式：")
    pdf.code(
        '{\n'
        '  "success": true,\n'
        '  "stdout": "编译输出日志...",\n'
        '  "stderr": "",\n'
        '  "errors": [],\n'
        '  "warnings": []\n'
        '}'
    )

    pdf.text("如果编译失败（success=false），检查 errors 数组获取详细错误信息。stdout/stderr 返回最后 2000 个字符。")

    # ---------- 6.9 Simulate Run ----------
    pdf.check_break(60)
    pdf.subsect("6.9 POST /api/simulate/run — 运行仿真")

    pdf.text("功能说明：")
    pdf.text(
        "使用 ModelSim/Questa 的 vsim 命令运行仿真。\n"
        "执行流程：(1) 生成 TCL 批处理脚本（vcd file / vcd add -r /* / run <time> / vcd flush / quit）\n"
        "(2) 执行 vsim -c -do <tcl_script> work.<top_module>\n"
        "(3) 检查 VCD 文件是否生成，返回 VCD 文件路径\n"
        "支持两种模式：直接运行（已有编译好的 work 库）或编译+运行（提供 sources 参数）。"
    )
    pdf.warn("此接口需要本地安装 ModelSim/Questa。确保 vsim 命令在系统 PATH 中可用。")

    pdf.text("请求格式：")
    pdf.code(
        "POST /api/simulate/run\n"
        "Content-Type: application/json\n\n"
        "{\n"
        '  "top_module": "my_top",\n'
        '  "sim_time": "1us",\n'
        '  "work_dir": "./sim_work",\n'
        '  "sources": ["src/counter.v", "src/top.v"]\n'
        '  // sources 为可选参数，提供后将先编译再运行\n'
        "}"
    )

    pdf.text("响应格式：")
    pdf.code(
        '{\n'
        '  "success": true,\n'
        '  "vcd_path": "./sim_work/my_top.vcd",\n'
        '  "stdout": "仿真输出日志...",\n'
        '  "errors": [],\n'
        '  "warnings": []\n'
        '}'
    )

    # ================================================================
    # 7. TESTING GUIDE
    # ================================================================
    pdf.add_page()
    pdf.sect("7. 测试指南")

    pdf.subsect("7.1 测试框架概述")
    pdf.text(
        "项目包含 23 个测试用例，分布在 4 个测试文件中，全部通过。\n\n"
        "测试框架: pytest + pytest-asyncio（异步测试）+ httpx（HTTP 客户端）\n"
        "测试配置: pyproject.toml 中 asyncio_mode = auto，自动管理事件循环\n"
        "API 测试特色: 使用 httpx AsyncClient + ASGI transport，直接在内存中测试 app 实例，无需启动真实服务器，测试执行速度快。"
    )

    pdf.subsect("7.2 运行全部测试")
    pdf.text("在 backend 目录下执行以下命令：")
    pdf.code("cd backend\npython -m pytest tests/ -v")
    pdf.text("预期输出：23 passed in ~0.5s，全部绿色通过。")

    pdf.text("常用测试选项：")
    pdf.item("查看详细输出（含 print 语句）：python -m pytest tests/ -v -s")
    pdf.item("仅运行失败的测试：python -m pytest tests/ --lf")
    pdf.item("先运行失败的再运行其他的：python -m pytest tests/ --ff")
    pdf.item("生成覆盖率报告（需安装 pytest-cov）：pip install pytest-cov && python -m pytest tests/ --cov=app --cov-report=html")
    pdf.item("指定单个测试文件：python -m pytest tests/test_ir.py -v")

    pdf.subsect("7.3 test_ir.py — 数据模型测试 (9个)")
    pdf.text("测试内容：验证所有 Pydantic 数据模型的创建、属性默认值、序列化和反序列化。")
    pdf.code("python -m pytest tests/test_ir.py -v")
    pdf.text("包含 5 个测试类：")
    pdf.item("TestPort (3个): test_create_simple_port — 验证默认参数（width=1, signed=False）; test_create_bus_port — 验证多位宽有符号端口; test_auto_id — 验证自动生成的 ID 长度为 12 且唯一")
    pdf.item("TestModule (2个): test_create_module — 验证空模块创建（type=base, ports=[]）; test_module_with_ports — 验证带 2 个端口的模块")
    pdf.item("TestConnection (1个): test_connection — 验证连线创建，含自定义 wire_name")
    pdf.item("TestIR (2个): test_empty_ir — 验证默认 IR（version=0.1.0, name=top, 空列表）; test_ir_with_data — 验证完整 IR 创建")
    pdf.item("TestProjectFile (2个): test_default_project — 验证默认工程; test_serialize_deserialize — 验证 model_dump() 和 model_validate() 的往返正确性")

    pdf.subsect("7.4 test_generators.py — 代码生成器测试 (5个)")
    pdf.text("测试内容：验证 TopGenerator 和 TestbenchGenerator 生成的 Verilog 代码的正确性。")
    pdf.code("python -m pytest tests/test_generators.py -v")
    pdf.text("包含 2 个测试类：")
    pdf.item("TestTopGenerator (3个): test_generate_simple_top — 2模块1连线生成包含 module/endmodule/wire/例化; test_infer_top_ports — 未连接端口暴露为顶层 I/O; test_multiple_connections — 多连线场景 wire 名正确性")
    pdf.item("TestTestbenchGenerator (2个): test_generate_tb — 验证 TB 包含时钟/复位/DUT/$dumpfile/$finish; test_tb_includes_clock_period — 验证时钟周期值出现在输出中")

    pdf.subsect("7.5 test_vcd.py — VCD 解析器测试 (4个)")
    pdf.text("测试内容：验证自研 VCD 解析器对 VCD 文件内容的正确解析。")
    pdf.code("python -m pytest tests/test_vcd.py -v")
    pdf.text("包含 2 个测试类：")
    pdf.item("TestVCDParser (3个): test_parse_simple_vcd — 1bit+4bit 信号的完整 VCD; test_empty_vcd — 空 VCD 返回空信号列表")
    pdf.item("TestWaveformData (1个): test_to_dict — 验证 to_dict() 输出的 JSON 结构正确")

    pdf.subsect("7.6 test_api.py — API 端点集成测试 (5个)")
    pdf.text("测试内容：端到端 HTTP 测试，验证所有主要 API 端点。使用 ASGI transport 直接在内存中测试，无需启动服务器。")
    pdf.code("python -m pytest tests/test_api.py -v")
    pdf.item("test_health — GET /api/health -> 200 + status=ok")
    pdf.item("test_generate_top — POST /api/generate/top -> 验证生成的 Verilog 包含 module/endmodule")
    pdf.item("test_generate_testbench — POST /api/generate/testbench -> 验证 TB 包含模块名")
    pdf.item("test_save_and_load_project — 保存+加载往返测试 -> 验证加载的工程名一致")
    pdf.item("test_parse_vcd_not_found — 解析不存在的 VCD 文件 -> 验证返回 404")

    pdf.subsect("7.7 如何编写新测试")
    pdf.text("编写数据模型测试（参考 test_ir.py 的模式）：")
    pdf.code(
        "# 在 tests/ 下创建 test_xxx.py\n"
        "import pytest\n"
        "from app.models.ir import Port, PortDirection\n\n"
        "class TestYourFeature:\n"
        "    def test_something(self):\n"
        '        p = Port(name="test", direction=PortDirection.INPUT)\n'
        '        assert p.name == "test"\n'
        '        assert p.width == 1'
    )

    pdf.text("编写 API 测试（参考 test_api.py 的模式）：")
    pdf.code(
        "import pytest\n"
        "from httpx import AsyncClient, ASGITransport\n"
        "from main import app\n\n"
        "@pytest.fixture\n"
        "async def client():\n"
        '    transport = ASGITransport(app=app)\n'
        '    async with AsyncClient(transport=transport, base_url="http://test") as ac:\n'
        "        yield ac\n\n"
        "@pytest.mark.asyncio\n"
        "async def test_my_endpoint(client: AsyncClient):\n"
        '    resp = await client.post("/api/my/endpoint", json={"key": "value"})\n'
        "    assert resp.status_code == 200\n"
        "    assert resp.json()[\"success\"]"
    )

    # ================================================================
    # 8. DEMO WORKFLOW
    # ================================================================
    pdf.add_page()
    pdf.sect("8. 完整工作流演示")
    pdf.text(
        "本章演示一个完整的端到端工作流：从启动服务到生成顶层模块、生成 Testbench、"
        "解析文件、保存/加载工程。使用项目自带的 demo_input.json 示例文件。"
    )

    pdf.subsect("8.1 准备工作")
    pdf.num("第1步", "打开终端，进入 backend 目录并启动服务：")
    pdf.code("cd D:\\claude\\prj\\backend\npython main.py")
    pdf.text("看到「Application startup complete.」说明服务已就绪。")

    pdf.num("第2步", "打开另一个终端窗口（保留服务运行），验证服务：")
    pdf.code("curl http://localhost:8000/api/health")
    pdf.text("预期返回: {\"status\":\"ok\",\"service\":\"fpga-visual-tool-backend\"}")

    pdf.num("第3步", "打开 Swagger UI（可选，方便可视化测试）：")
    pdf.code("# 浏览器打开: http://localhost:8000/docs")

    pdf.subsect("8.2 生成顶层模块 — 详细步骤")
    pdf.num("第1步", "查看 demo_input.json 的内容。该文件包含 2 个模块（clk_divider, led_controller）和 1 根连线（clk_out -> clk），顶层名为 blinky_demo。")
    pdf.num("第2步", "发送生成请求：")
    pdf.code(
        "curl -X POST http://localhost:8000/api/generate/top ^\n"
        "  -H \"Content-Type: application/json\" ^\n"
        "  -d @demo_input.json"
    )

    pdf.num("第3步", "预期的生成结果（关键内容）：")
    pdf.code(
        "module blinky_demo (\n"
        "    input  clk_in,\n"
        "    input  rst_n,\n"
        "    output [3:0] led_out\n"
        ");\n\n"
        "wire clk_divided;\n\n"
        "clk_divider u_div (\n"
        "    .clk_in (clk_in),\n"
        "    .rst_n  (rst_n),\n"
        "    .clk_out(clk_divided)\n"
        ");\n\n"
        "led_controller u_led (\n"
        "    .clk    (clk_divided),\n"
        "    .rst_n  (rst_n),\n"
        "    .led_out(led_out)\n"
        ");\n\n"
        "endmodule"
    )

    pdf.text("验证要点：")
    pdf.item("clk_in/rst_n 被推断为顶层 input（这些端口虽然被连接但未被其他模块的输出驱动）")
    pdf.item("led_out 被推断为顶层 output（未被任何模块的 input 连接）")
    pdf.item("clk_divided 被声明为内部 wire（连接 m1.clk_out 和 m2.clk）")
    pdf.item("两个模块的例化端口映射正确")

    pdf.subsect("8.3 生成 Testbench — 详细步骤")
    pdf.text("使用与上一步相同的 IR 结构，加上仿真配置参数：")
    pdf.code(
        "curl -X POST http://localhost:8000/api/generate/testbench ^\n"
        "  -H \"Content-Type: application/json\" ^\n"
        "  -d \"{\\\"ir\\\":{\\\"version\\\":\\\"0.1.0\\\",\\\"modules\\\":[],\\\"connections\\\":[],\\\"wrapped_modules\\\":[],\\\"top_module_name\\\":\\\"blinky\\\"},\\\"simulation\\\":{\\\"clock_period_ns\\\":10.0,\\\"reset_cycles\\\":5,\\\"sim_time_us\\\":100.0}}\""
    )
    pdf.text("预期输出包含以下关键内容：")
    pdf.item("module tb_blinky — Testbench 模块声明")
    pdf.item("forever #5.0 clk = ~clk — 10ns 周期的时钟生成")
    pdf.item("repeat(5) @(posedge clk) — 5 个周期的复位序列")
    pdf.item("blinky u_dut(...) — DUT 例化")
    pdf.item("$dumpfile / $dumpvars — 波形导出配置")
    pdf.item("#100000; $finish — 100us 后自动结束仿真")

    pdf.subsect("8.4 解析 Verilog 文件")
    pdf.num("第1步", "创建测试用 Verilog 文件：")
    pdf.code(
        "Set-Content -Path test_sample.v -Value @\"\n"
        "module counter(input clk, input rst_n, output reg [3:0] q);\n"
        "  always @(posedge clk) q <= q + 1;\n"
        "endmodule\n"
        '"@'
    )
    pdf.num("第2步", "调用解析 API：")
    pdf.code(
        '$body = ''{"file_path": "test_sample.v"}''\n'
        "Invoke-RestMethod -Uri http://localhost:8000/api/parse/verilog -Method Post -Body $body -ContentType \"application/json\" | ConvertTo-Json"
    )
    pdf.text("预期返回 counter 模块的端口信息：clk(input,1bit), rst_n(input,1bit), q(output,4bit)。")

    pdf.subsect("8.5 解析 VCD 波形")
    pdf.num("第1步", "创建测试 VCD 文件：")
    pdf.code(
        'Set-Content -Path test_wave.vcd -Value @"\n'
        '$timescale 1ns $end\n'
        '$var wire 1 ! clk $end\n'
        '$dumpvars\n'
        '0!\n'
        '$end\n'
        '#10\n'
        '1!\n'
        '"@'
    )
    pdf.num("第2步", "调用解析 API：")
    pdf.code(
        '$body = ''{"file_path": "test_wave.vcd"}''\n'
        "Invoke-RestMethod -Uri http://localhost:8000/api/parse/vcd -Method Post -Body $body -ContentType \"application/json\" | ConvertTo-Json -Depth 5"
    )
    pdf.text("预期返回 clk 信号的波形数据，包含 2 次值变化（0ns 时值为 0，10ns 时值为 1）。")

    pdf.subsect("8.6 保存和加载工程")
    pdf.num("第1步", "保存工程：")
    pdf.code(
        '$proj = @{version="0.1.0"; name="demo"; ir=@{version="0.1.0"; modules=@(); connections=@(); wrapped_modules=@(); top_module_name="top"}}\n'
        '$body = @{project=$proj; file_path="demo_project.fpga.json"} | ConvertTo-Json -Depth 6\n'
        "Invoke-RestMethod -Uri http://localhost:8000/api/project/save -Method Post -Body $body -ContentType \"application/json\""
    )
    pdf.num("第2步", "加载工程：")
    pdf.code(
        '$body = ''{"file_path": "demo_project.fpga.json"}''\n'
        "$resp = Invoke-RestMethod -Uri http://localhost:8000/api/project/load -Method Post -Body $body -ContentType \"application/json\"\n"
        "$resp.project.name"
    )
    pdf.text("预期加载的工程 name 为 demo，与保存时一致。")

    # ================================================================
    # 9. FAQ
    # ================================================================
    pdf.add_page()
    pdf.sect("9. 常见问题与故障排除")

    pdf.subsect("Q1: 启动服务时提示端口被占用")
    pdf.text("错误信息: Address already in use")
    pdf.text("解决方法 A：更换端口号启动。")
    pdf.code("uvicorn main:app --reload --host 0.0.0.0 --port 8001")
    pdf.text("解决方法 B：查找并终止占用端口的进程。")
    pdf.code(
        "# PowerShell 查找占用 8000 端口的进程:\n"
        "netstat -ano | findstr :8000\n"
        "# 记下最后一列的 PID，然后终止:\n"
        "taskkill /PID <PID> /F"
    )

    pdf.subsect("Q2: 导入模块时报 ModuleNotFoundError")
    pdf.text("错误信息: ModuleNotFoundError: No module named \'app\'")
    pdf.text("解决方法：确保在 backend 目录下执行命令，pyproject.toml 中已配置 pythonpath = [\".\"]。")
    pdf.code(
        "cd D:\\claude\\prj\\backend\n"
        "python -m pytest tests/ -v\n\n"
        "# 或手动设置 PYTHONPATH:\n"
        '$env:PYTHONPATH = "D:\\claude\\prj\\backend"\n'
        "python -m pytest tests/"
    )

    pdf.subsect("Q3: pytest 找不到测试文件")
    pdf.text("确认 pyproject.toml 中已配置 testpaths 和 pythonpath：")
    pdf.code(
        "[tool.pytest.ini_options]\n"
        'testpaths = ["tests"]\n'
        'pythonpath = ["."]'
    )
    pdf.text("同时确认测试文件命名符合 pytest 默认规则（test_*.py 或 *_test.py）。")

    pdf.subsect("Q4: 代码生成结果中端口丢失或 wire 名不对")
    pdf.text("可能原因：")
    pdf.item("IR 中 module.id 和 Connection 中的 src_module/dst_module 不匹配 — 检查 ID 引用")
    pdf.item("端口名称大小写不一致 — 确认 IR 中的 port name 与实际 Verilog module 的端口名一致")
    pdf.item("封装模块的内部连线未正确扁平化 — 检查 WrappedModule 的 internal_connections 是否正确传入")
    pdf.text("排查方法：打印 IR JSON 内容，逐字段与预期值比对。")

    pdf.subsect("Q5: 仿真接口报错 vlib/vlog/vsim not found")
    pdf.text("原因：ModelSim/Questa 未安装或不在系统 PATH 环境变量中。")
    pdf.text("解决方法：")
    pdf.item("安装 ModelSim/Questa 到本地（如 C:\\modeltech64_10.7）")
    pdf.item("将安装路径（如 C:\\modeltech64_10.7\\win64）添加到系统 PATH 环境变量")
    pdf.item("或在代码中创建 ModelSimSimulator 时传入 executable_path 参数指定安装目录")

    pdf.subsect("Q6: VCD 解析结果为空或不完整")
    pdf.text("可能原因：")
    pdf.item("VCD 文件格式不规范 — 某些 EDA 工具生成的 VCD 有变体语法")
    pdf.item("$var 定义使用了多行格式 — 解析器已支持多行，但极特殊情况可能遗漏")
    pdf.item("信号 ID 代码使用了非标准字符 — 解析器对 ID 代码有字符限制")
    pdf.text("排查方法：先手动查看 VCD 文件内容，确认格式。然后用简单测试 VCD 验证解析器是否正常。")

    pdf.subsect("Q7: curl 命令在 PowerShell 中执行失败")
    pdf.text("Windows PowerShell 中的 curl 可能指向 Invoke-WebRequest 的别名。")
    pdf.text("解决方法：使用 curl.exe 明确调用，或直接使用 PowerShell 的 Invoke-RestMethod。")
    pdf.code(
        "# 方法1: 使用 curl.exe\n"
        "curl.exe http://localhost:8000/api/health\n\n"
        "# 方法2: 使用 Invoke-RestMethod\n"
        "Invoke-RestMethod -Uri http://localhost:8000/api/health"
    )

    # ================================================================
    # 10. APPENDIX
    # ================================================================
    pdf.add_page()
    pdf.sect("10. 附录")

    pdf.subsect("10.1 依赖列表")
    pdf.text("requirements.txt 完整内容：")
    pdf.code(
        "fastapi        >= 0.111.0     # Web 框架\n"
        "uvicorn        >= 0.29.0      # ASGI 服务器\n"
        "pydantic       >= 2.7.0       # 数据校验\n"
        "jinja2         >= 3.1.4       # 模板引擎\n"
        "vcdvcd         >= 2.0.0       # VCD 库（辅助，非核心依赖）\n"
        "pytest         >= 8.2.0       # 测试框架\n"
        "pytest-asyncio >= 0.23.7      # 异步测试支持\n"
        "httpx          >= 0.27.0      # HTTP 测试客户端\n"
        "fpdf           >= 1.7.0       # PDF 生成（手册生成用）"
    )

    pdf.subsect("10.2 demo_input.json 示例文件")
    pdf.text("项目根目录下的 demo_input.json 包含了一个完整的 IR 示例，可作为测试数据直接使用：")
    pdf.code(
        "{\n"
        '  "ir": {\n'
        '    "version": "0.1.0",\n'
        '    "modules": [\n'
        '      {"id":"m1","name":"clk_divider","instance_name":"u_div","type":"base",\n'
        '       "ports":[{"name":"clk_in","direction":"input","width":1},\n'
        '               {"name":"rst_n","direction":"input","width":1},\n'
        '               {"name":"clk_out","direction":"output","width":1}],\n'
        '       "position":[0,0],"config":{"div_factor":4}},\n'
        '      {"id":"m2","name":"led_controller","instance_name":"u_led","type":"base",\n'
        '       "ports":[{"name":"clk","direction":"input","width":1},\n'
        '               {"name":"rst_n","direction":"input","width":1},\n'
        '               {"name":"led_out","direction":"output","width":4}],\n'
        '       "position":[300,0],"config":{}}\n'
        "    ],\n"
        '    "connections": [\n'
        '      {"id":"c1","src_module":"m1","src_port":"clk_out",\n'
        '       "dst_module":"m2","dst_port":"clk","wire_name":"clk_divided"}\n'
        "    ],\n"
        '    "wrapped_modules": [],\n'
        '    "top_module_name": "blinky_demo"\n'
        "  }\n"
        "}"
    )
    pdf.text(
        "此示例描述了一个简单的设计：clk_divider 模块产生分频时钟 clk_divided，\n"
        "输出给 led_controller 模块驱动 LED。该文件可直接用于测试 /api/generate/top 接口。"
    )

    pdf.subsect("10.3 ModelSim 环境要求")
    pdf.text("仿真功能（/api/simulate/compile 和 /api/simulate/run）需要本地安装 ModelSim 或 Questa Sim。")
    pdf.text("安装后，以下命令需要在终端中可直接调用：")
    pdf.item("vlib — 创建仿真库（vlib work）")
    pdf.item("vlog — 编译 Verilog 源文件（vlog -work work <source>）")
    pdf.item("vcom — 编译 VHDL 源文件（如果使用 VHDL）")
    pdf.item("vsim — 运行仿真（vsim -c -do <tcl_script>）")
    pdf.text(
        "如果未安装 ModelSim，仿真相关的 API 将返回错误（success=false），但其他所有 API 功能不受影响。\n"
        "对于 CI/CD 环境或没有 ModelSim 许可证的情况，可以考虑以下替代方案：\n"
        "(1) 使用免费的 Icarus Verilog (iverilog) 进行仿真验证\n"
        "(2) 使用 Verilator 进行 C++/SystemC 协同仿真\n"
        "(3) 实现对应的 Simulator 子类来集成其他仿真器"
    )

    pdf.ln(4)
    pdf.set_font("CJK", "B", 12)
    pdf.set_text_color(25, 60, 120)
    pdf.cell(0, 10, "-- 手册结束 --", align="C")

    # ===== SAVE =====
    output_path = os.path.join(os.path.dirname(__file__), "FPGA_Backend_Manual_CN.pdf")
    pdf.output(output_path)
    print(f"Manual saved to: {output_path}")
    print(f"Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build()
