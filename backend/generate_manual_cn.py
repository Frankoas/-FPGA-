# -*- coding: utf-8 -*-
"""
Generate Chinese PDF user manual for FPGA Visual Programming Tool backend.
"""
import os
from fpdf import FPDF

FONT_PATH = r"C:\Windows\Fonts\simhei.ttf"


class ManualPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.add_font("CJK", "", FONT_PATH)
        self.add_font("CJK", "B", FONT_PATH)
        # Register monospace font (Courier doesn't support CJK, use CJK for code too)
        self.add_font("Code", "", FONT_PATH)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("CJK", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "FPGA可视化编程工具 - 后端测试使用手册", align="C")
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("CJK", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"第 {self.page_no()} 页 / 共 {{nb}} 页", align="C")

    def section_title(self, title: str):
        self.set_font("CJK", "B", 15)
        self.set_text_color(25, 60, 120)
        self.cell(0, 10, title)
        self.ln(8)
        self.set_line_width(0.8)
        self.set_draw_color(25, 60, 120)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)

    def sub_title(self, title: str):
        self.set_font("CJK", "B", 12)
        self.set_text_color(50, 90, 160)
        self.cell(0, 8, title)
        self.ln(7)

    def sub_sub_title(self, title: str):
        self.set_font("CJK", "B", 11)
        self.set_text_color(60, 60, 60)
        self.cell(0, 7, title)
        self.ln(6)

    def body(self, text: str):
        self.set_font("CJK", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, text)
        self.ln(1)

    def code_block(self, code: str):
        self.set_fill_color(248, 248, 250)
        self.set_line_width(0.3)
        self.set_draw_color(180, 180, 180)
        self.set_font("CJK", "", 8)
        self.set_text_color(40, 40, 40)
        lines = code.split("\n")
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

    def bullet(self, text: str):
        self.set_font("CJK", "", 10)
        self.set_text_color(40, 40, 40)
        x0 = self.get_x()
        self.cell(6, 6, ">")
        self.multi_cell(0, 6, text)
        self.ln(0.5)

    def numbered(self, num: str, text: str):
        self.set_font("CJK", "", 10)
        self.set_text_color(40, 40, 40)
        self.cell(10, 6, num)
        self.multi_cell(0, 6, text)
        self.ln(0.5)

    def note(self, text: str):
        self.set_fill_color(235, 245, 255)
        self.set_line_width(0.4)
        self.set_draw_color(50, 90, 160)
        self.set_font("CJK", "", 9)
        self.set_text_color(40, 60, 100)
        y0 = self.get_y()
        self.set_x(self.l_margin + 4)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 8, 5, text)
        h = self.get_y() - y0 + 2
        self.set_fill_color(235, 245, 255)
        self.rect(self.l_margin + 2, y0, self.w - self.l_margin - self.r_margin - 4, h, style="DF")
        # re-draw text on top
        self.set_xy(self.l_margin + 6, y0 + 1)
        self.set_font("CJK", "", 9)
        self.set_text_color(40, 60, 100)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 12, 5, text)
        self.ln(2)

    def warning(self, text: str):
        self.set_fill_color(255, 245, 230)
        self.set_line_width(0.4)
        self.set_draw_color(220, 150, 50)
        self.set_font("CJK", "", 9)
        self.set_text_color(140, 80, 20)
        y0 = self.get_y()
        self.set_x(self.l_margin + 4)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 8, 5, text)
        h = self.get_y() - y0 + 2
        self.rect(self.l_margin + 2, y0, self.w - self.l_margin - self.r_margin - 4, h, style="DF")
        self.set_xy(self.l_margin + 6, y0 + 1)
        self.set_font("CJK", "", 9)
        self.set_text_color(140, 80, 20)
        self.multi_cell(self.w - self.l_margin - self.r_margin - 12, 5, text)
        self.ln(2)

    def check_page_break(self, needed_mm: int = 40):
        if self.get_y() + needed_mm > self.h - 20:
            self.add_page()


def build_manual():
    pdf = ManualPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(True, 18)
    pdf.set_left_margin(18)
    pdf.set_right_margin(18)

    # =========================================================================
    # 封面
    # =========================================================================
    pdf.add_page()
    pdf.ln(35)
    pdf.set_font("CJK", "B", 30)
    pdf.set_text_color(25, 60, 120)
    pdf.multi_cell(0, 14, "FPGA 可视化编程工具\n后端测试使用手册", align="C")
    pdf.ln(6)
    pdf.set_font("CJK", "", 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "版本 0.1.0  |  2026年5月", align="C")
    pdf.ln(14)
    pdf.set_line_width(0.6)
    pdf.set_draw_color(25, 60, 120)
    mid_x = pdf.w / 2
    pdf.line(mid_x - 35, pdf.get_y(), mid_x + 35, pdf.get_y())
    pdf.ln(14)
    pdf.set_font("CJK", "", 12)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(0, 9, "后端框架: FastAPI + Uvicorn", align="C")
    pdf.ln(8)
    pdf.cell(0, 9, "开发语言: Python 3.11+", align="C")
    pdf.ln(8)
    pdf.cell(0, 9, "模板引擎: Jinja2", align="C")
    pdf.ln(8)
    pdf.cell(0, 9, "数据模型: Pydantic v2", align="C")
    pdf.ln(8)
    pdf.cell(0, 9, "测试框架: pytest + httpx", align="C")
    pdf.ln(14)
    pdf.set_font("CJK", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, "本文档面向后端开发者和测试人员", align="C")
    pdf.ln(7)
    pdf.cell(0, 8, "详细说明每个API的功能、使用方法、测试步骤及预期结果", align="C")

    # =========================================================================
    # 目录
    # =========================================================================
    pdf.add_page()
    pdf.section_title("目录")
    toc = [
        ("1.", "项目概述", ""),
        ("  1.1", "项目背景与目标", ""),
        ("  1.2", "后端核心能力", ""),
        ("  1.3", "技术栈总览", ""),
        ("2.", "环境准备", ""),
        ("  2.1", "Python 环境安装", ""),
        ("  2.2", "项目依赖安装", ""),
        ("  2.3", "验证安装", ""),
        ("3.", "启动服务", ""),
        ("  3.1", "开发模式启动", ""),
        ("  3.2", "命令行启动", ""),
        ("  3.3", "验证服务运行", ""),
        ("4.", "项目架构详解", ""),
        ("  4.1", "目录结构", ""),
        ("  4.2", "数据流架构", ""),
        ("  4.3", "模块职责说明", ""),
        ("5.", "IR 中间表示数据模型", ""),
        ("  5.1", "Port - 端口模型", ""),
        ("  5.2", "Module - 模块模型", ""),
        ("  5.3", "Connection - 连线模型", ""),
        ("  5.4", "WrappedModule - 封装模块", ""),
        ("  5.5", "IR - 顶层中间表示", ""),
        ("  5.6", "ProjectFile - 工程文件", ""),
        ("  5.7", "SimulationConfig - 仿真配置", ""),
        ("  5.8", "BoardConfig - 板卡配置", ""),
        ("6.", "API 接口详细参考", ""),
        ("  6.1", "GET /api/health - 健康检查", ""),
        ("  6.2", "POST /api/generate/top - 生成顶层模块", ""),
        ("  6.3", "POST /api/generate/testbench - 生成Testbench", ""),
        ("  6.4", "POST /api/parse/verilog - 解析Verilog文件", ""),
        ("  6.5", "POST /api/parse/vcd - 解析VCD波形", ""),
        ("  6.6", "POST /api/project/save - 保存工程", ""),
        ("  6.7", "POST /api/project/load - 加载工程", ""),
        ("  6.8", "POST /api/simulate/compile - 编译HDL源文件", ""),
        ("  6.9", "POST /api/simulate/run - 运行仿真", ""),
        ("7.", "测试指南", ""),
        ("  7.1", "测试框架概述", ""),
        ("  7.2", "运行全部测试", ""),
        ("  7.3", "test_ir.py - 数据模型测试 (9个)", ""),
        ("  7.4", "test_generators.py - 代码生成测试 (5个)", ""),
        ("  7.5", "test_vcd.py - VCD解析测试 (4个)", ""),
        ("  7.6", "test_api.py - API端点测试 (5个)", ""),
        ("  7.7", "如何编写新测试", ""),
        ("8.", "完整工作流演示", ""),
        ("  8.1", "准备工作", ""),
        ("  8.2", "生成顶层模块", ""),
        ("  8.3", "生成Testbench", ""),
        ("  8.4", "解析Verilog文件", ""),
        ("  8.5", "解析VCD波形", ""),
        ("  8.6", "保存和加载工程", ""),
        ("9.", "常见问题与故障排除", ""),
        ("10.", "附录", ""),
        ("  10.1", "依赖列表", ""),
        ("  10.2", "demo_input.json 示例文件", ""),
        ("  10.3", "ModelSim 环境要求", ""),
    ]
    pdf.set_font("CJK", "", 10)
    pdf.set_text_color(40, 40, 40)
    for num, title, _ in toc:
        indent = 4 if num.startswith("  ") else 0
        pdf.set_x(18 + indent)
        pdf.cell(0, 6.5, f"{num.strip()}  {title}")
        pdf.ln(6.5)

    # =========================================================================
    # 1. 项目概述
    # =========================================================================
    pdf.add_page()
    pdf.section_title("1. 项目概述")

    pdf.sub_title("1.1 项目背景与目标")
    pdf.body(
        "FPGA 可视化编程工具旨在为 FPGA 开发者提供一套类似于 ComfyUI 的节点式编程环境。"
        "用户可以通过拖拽模块节点、连接端口的方式完成 FPGA 设计，无需手写繁琐的顶层例化代码。"
        "工具最终可一键生成可综合的 Verilog/VHDL 顶层设计文件，并支持仿真联动与时序调试。"
    )
    pdf.body(
        "后端服务是整个工具的\"引擎\"，负责：\n"
        "(1) 接收前端画布生成的 IR (中间表示) JSON 数据\n"
        "(2) 根据 IR 生成 Verilog 顶层模块代码\n"
        "(3) 根据 IR 和仿真配置生成 Testbench 测试框架\n"
        "(4) 解析已有的 Verilog 文件，提取模块信息（用于工程导入）\n"
        "(5) 解析仿真产生的 VCD 波形文件（用于波形可视化）\n"
        "(6) 管理工程文件的保存与加载\n"
        "(7) 通过 subprocess 调用 ModelSim/Questa 进行仿真"
    )

    pdf.sub_title("1.2 后端核心能力")
    pdf.bullet("IR 驱动的 Verilog 顶层模块自动生成：自动推断顶层端口、创建 wire 声明、生成模块例化代码")
    pdf.bullet("Testbench 框架自动生成：时钟生成、复位序列、DUT 例化、激励占位区域、波形导出语句")
    pdf.bullet("Verilog 文件解析：基于正则表达式的解析器，支持 .v / .sv 文件，提取模块声明和例化关系")
    pdf.bullet("VCD 波形文件解析：自研解析器，支持 $timescale、$var、$dumpvars、#time 标记和多 bit 总线值")
    pdf.bullet("ModelSim/Questa 仿真集成：通过 subprocess 异步调用 vlib/vlog/vsim，支持 TCL 脚本批处理")
    pdf.bullet("工程文件管理：.fpga.json 格式的保存和加载，包含版本化管理")
    pdf.bullet("完整的测试套件：23 个测试覆盖数据模型、代码生成、VCD 解析、API 端点")

    pdf.sub_title("1.3 技术栈总览")
    pdf.body("后端技术栈：")
    pdf.bullet("Web 框架: FastAPI (基于 Starlette/Pydantic，异步支持，自动生成 OpenAPI 文档)")
    pdf.bullet("ASGI 服务器: Uvicorn (支持热重载，高性能异步)")
    pdf.bullet("数据校验: Pydantic v2 (类型安全，自动 JSON Schema 生成)")
    pdf.bullet("模板引擎: Jinja2 (Verilog 代码模板渲染)")
    pdf.bullet("测试框架: pytest + pytest-asyncio + httpx (异步 HTTP 测试)")
    pdf.bullet("仿真接口: subprocess + TCL 脚本 (调用 ModelSim/Questa 命令行)")
    pdf.bullet("波形解析: 自研 VCD 解析器 (无外部依赖，支持基本 VCD 语法)")

    # =========================================================================
    # 2. 环境准备
    # =========================================================================
    pdf.add_page()
    pdf.section_title("2. 环境准备")

    pdf.sub_title("2.1 Python 环境安装")
    pdf.body("后端服务需要 Python 3.11 或更高版本。请按以下步骤操作：")
    pdf.numbered("第1步", "检查是否已安装 Python：")
    pdf.code_block("python --version\n# 预期输出: Python 3.11.x 或更高版本")
    pdf.body("如果未安装 Python，请前往 https://www.python.org/downloads/ 下载安装。安装时务必勾选 \"Add Python to PATH\" 选项。")
    pdf.numbered("第2步", "检查 pip（Python 包管理器）是否可用：")
    pdf.code_block("pip --version\n# 预期输出: pip 24.x 或类似版本信息")
    pdf.numbered("第3步", "建议使用虚拟环境（可选但推荐）：")
    pdf.code_block(
        "cd backend\n"
        "python -m venv venv\n\n"
        "# Windows 激活虚拟环境:\n"
        "venv\\Scripts\\activate\n\n"
        "# 激活成功后，命令行前面会显示 (venv) 前缀"
    )

    pdf.sub_title("2.2 项目依赖安装")
    pdf.body("进入 backend 目录，使用 pip 安装所有依赖：")
    pdf.code_block(
        "cd backend\n"
        "pip install -r requirements.txt"
    )
    pdf.body(
        "此命令将安装以下核心依赖：\n"
        "fastapi >= 0.111.0 -- Web 框架\n"
        "uvicorn >= 0.29.0 -- ASGI 服务器\n"
        "pydantic >= 2.7.0 -- 数据校验\n"
        "jinja2 >= 3.1.4 -- 模板引擎\n"
        "pytest >= 8.2.0 -- 测试框架\n"
        "pytest-asyncio >= 0.23.7 -- 异步测试支持\n"
        "httpx >= 0.27.0 -- HTTP 客户端（测试用）"
    )

    pdf.sub_title("2.3 验证安装")
    pdf.body("安装完成后，执行以下命令验证依赖是否正确安装：")
    pdf.code_block(
        "cd backend\n"
        "python -c \"import fastapi; import uvicorn; import pydantic; import jinja2; print('All OK')\"\n\n"
        "# 预期输出: All OK"
    )
    pdf.body("如果没有任何错误输出，说明环境已准备就绪。")

    # =========================================================================
    # 3. 启动服务
    # =========================================================================
    pdf.add_page()
    pdf.section_title("3. 启动服务")

    pdf.sub_title("3.1 开发模式启动（推荐）")
    pdf.body("使用 main.py 启动（自带 uvicorn 配置）：")
    pdf.code_block(
        "cd backend\n"
        "python main.py"
    )
    pdf.body(
        "此命令将以开发模式启动服务，默认监听 http://localhost:8000。\n"
        "服务启动后，你将在终端看到类似以下的输出："
    )
    pdf.code_block(
        "INFO:     Will watch for changes...\n"
        "INFO:     Uvicorn running on http://0.0.0.0:8000\n"
        "INFO:     Application startup complete."
    )

    pdf.sub_title("3.2 命令行启动")
    pdf.body("也可以直接使用 uvicorn 命令启动，支持更多自定义参数：")
    pdf.code_block(
        "cd backend\n"
        "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    )
    pdf.body("参数说明：")
    pdf.bullet("--reload: 开启热重载，代码修改后自动重启（开发必备）")
    pdf.bullet("--host 0.0.0.0: 监听所有网络接口（如需局域网内其他设备访问）")
    pdf.bullet("--port 8000: 指定端口号，可改为任意未占用端口")

    pdf.sub_title("3.3 验证服务运行")
    pdf.body("服务启动后，使用以下方式验证：")
    pdf.numbered("方式1", "浏览器访问 http://localhost:8000/api/health，应看到 JSON 响应：")
    pdf.code_block('{"status": "ok", "service": "fpga-visual-tool-backend"}')
    pdf.numbered("方式2", "使用 curl 命令测试：")
    pdf.code_block("curl http://localhost:8000/api/health")
    pdf.numbered("方式3", "打开 Swagger UI 交互式文档：")
    pdf.code_block("# 浏览器访问:\nhttp://localhost:8000/docs")
    pdf.body("Swagger UI 页面列出了所有可用的 API 端点，你可以直接在页面上填写参数并发送请求进行测试。")

    # =========================================================================
    # 4. 项目架构详解
    # =========================================================================
    pdf.add_page()
    pdf.section_title("4. 项目架构详解")

    pdf.sub_title("4.1 目录结构")
    pdf.body("以下是 backend 目录的完整结构及各文件职责说明：")
    pdf.code_block(
        "backend/\n"
        "  main.py                  # FastAPI 应用入口，创建 app 实例\n"
        "  requirements.txt         # Python 依赖清单\n"
        "  pyproject.toml           # pytest 测试配置\n"
        "  demo_input.json          # 示例 IR 输入文件（用于快速测试）\n"
        "  generate_manual.py       # PDF 手册生成脚本\n"
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

    pdf.sub_title("4.2 数据流架构")
    pdf.body(
        "整个后端的数据流是单向的：前端画布 -> IR (JSON) -> 后端处理 -> 生成代码/解析结果。\n"
        "IR (Intermediate Representation) 是前后端之间的唯一交换格式。"
    )
    pdf.code_block(
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
        "  Jinja2模板   Jinja2模板    Python正则/解析器\n"
        "     |            |             |\n"
        "     v            v             v\n"
        "  Verilog代码  Verilog代码   结构化JSON"
    )

    pdf.sub_title("4.3 模块职责说明")
    pdf.body("routes.py (app/routes.py) - API 路由层：")
    pdf.bullet("定义 9 个 API 端点的请求/响应模型（Pydantic）")
    pdf.bullet("使用单例模式管理生成器和解析器实例，避免重复初始化")
    pdf.bullet("统一的异常处理：捕获异常并返回 HTTP 4xx/5xx 错误")

    pdf.body("models/ir.py (app/models/ir.py) - 数据模型层：")
    pdf.bullet("定义 8 个核心 Pydantic 模型：Port, Module, Connection, WrappedModule, IR, BoardConfig, SimulationConfig, ProjectFile")
    pdf.bullet("自动生成唯一 ID（uuid4 前12位）")
    pdf.bullet("版本化 IR（version 字段），支持前后兼容")

    pdf.body("generators/ - 代码生成层：")
    pdf.bullet("top.py: 扁平化模块和连线 -> 推断顶层端口 -> 构建 wire 声明 -> 生成例化语句 -> Jinja2 渲染")
    pdf.bullet("testbench.py: 提取仿真信号 -> 构建时钟/复位逻辑 -> 生成 DUT 例化 -> 添加 dump 语句 -> Jinja2 渲染")

    pdf.body("parser/verilog_parser.py - 解析层：")
    pdf.bullet("正则匹配 module 声明、端口定义、例化语句")
    pdf.bullet("支持 .v/.sv 文件和目录递归解析")
    pdf.bullet("VHDL 解析为占位实现，生产环境需使用 pyVHDLParser")

    pdf.body("simulator/ - 仿真层：")
    pdf.bullet("base.py: 定义 Simulator 抽象基类（compile/run/compile_and_run）")
    pdf.bullet("modelsim.py: 通过 asyncio subprocess 异步调用 ModelSim 命令行工具")

    pdf.body("utils/vcd_parser.py - 工具层：")
    pdf.bullet("自研 VCD 解析器，无外部依赖")
    pdf.bullet("支持 $timescale, $var, $dumpvars, #time 标记")
    pdf.bullet("解析单 bit 和多 bit 总线值变化")

    # =========================================================================
    # 5. IR 中间表示数据模型
    # =========================================================================
    pdf.add_page()
    pdf.section_title("5. IR 中间表示数据模型")

    pdf.body(
        "IR (Intermediate Representation) 是前端图形画布与后端代码生成之间的唯一数据交换格式。"
        "所有模型使用 Pydantic v2 定义，位于 app/models/ir.py。"
        "IR 包含版本号字段，用于保证前后向兼容性。"
    )

    pdf.sub_title("5.1 Port - 端口模型")
    pdf.body("描述模块的一个输入/输出/双向端口。")
    pdf.code_block(
        "class PortDirection(str, Enum):\n"
        '    INPUT  = "input"      # 输入端口\n'
        '    OUTPUT = "output"     # 输出端口\n'
        '    INOUT  = "inout"      # 双向端口\n\n'
        "class Port(BaseModel):\n"
        "    id: str            # 自动生成的唯一ID (12位十六进制)\n"
        "    name: str          # 端口名称，如 clk, rst_n, data_in\n"
        "    direction: PortDirection  # 端口方向\n"
        "    width: int = 1     # 位宽，默认1\n"
        "    signed: bool = False  # 有无符号\n"
        "    array_size: int | None = None  # 数组维度\n"
        "    description: str = ''  # 端口注释"
    )
    pdf.body("JSON 示例：")
    pdf.code_block(
        '{\n'
        '  "name": "clk",\n'
        '  "direction": "input",\n'
        '  "width": 1,\n'
        '  "signed": false\n'
        '}'
    )

    pdf.sub_title("5.2 Module - 模块模型")
    pdf.body("描述画布上的一个模块节点。")
    pdf.code_block(
        "class Module(BaseModel):\n"
        "    id: str            # 自动生成的唯一ID\n"
        "    name: str          # 模块名（对应 Verilog module 名）\n"
        "    instance_name: str | None  # 用户自定义例化名\n"
        '    type: str = "base" # 模块类型: base/wrapped/board_ip\n'
        "    ports: list[Port]  # 端口列表\n"
        "    position: tuple[float,float]  # 画布坐标 (x, y)\n"
        "    config: dict       # 模块参数配置"
    )
    pdf.body("模块类型说明：")
    pdf.bullet("base -- 标准用户定义或导入的模块")
    pdf.bullet("wrapped -- 封装后的子电路模块（可展开/折叠）")
    pdf.bullet("board_ip -- 板卡厂商提供的 IP 核（PLL, GPIO, UART 等）")

    pdf.sub_title("5.3 Connection - 连线模型")
    pdf.body("描述两个端口之间的连线关系。")
    pdf.code_block(
        "class Connection(BaseModel):\n"
        "    id: str            # 自动生成的唯一ID\n"
        "    src_module: str    # 源模块 ID\n"
        "    src_port: str      # 源端口名称\n"
        "    dst_module: str    # 目标模块 ID\n"
        "    dst_port: str      # 目标端口名称\n"
        "    wire_name: str | None  # 用户标注的wire名，为空则自动生成"
    )

    pdf.sub_title("5.4 WrappedModule - 封装模块")
    pdf.body("将一组内部模块打包为可复用的封装节点。")
    pdf.code_block(
        "class WrappedModule(BaseModel):\n"
        "    name: str           # 封装后的模块名\n"
        "    exposed_ports: list[Port]  # 暴露到外部的端口\n"
        "    internal_modules: list[Module]  # 内部子模块\n"
        "    internal_connections: list[Connection]  # 内部连线\n"
        "    internal_wrapped: list[WrappedModule]  # 嵌套封装"
    )

    pdf.sub_title("5.5 IR - 顶层中间表示")
    pdf.body("画布完整状态的抽象，是前后端交换的核心对象。")
    pdf.code_block(
        "class IR(BaseModel):\n"
        '    version: str = "0.1.0"  # IR 版本号\n'
        "    modules: list[Module]   # 顶层模块列表\n"
        "    connections: list[Connection]  # 连线列表\n"
        "    wrapped_modules: list[WrappedModule]  # 封装模块\n"
        '    top_module_name: str = "top"  # 顶层模块名'
    )

    pdf.sub_title("5.6 ProjectFile - 工程文件")
    pdf.body("完整的工程存档文件格式（.fpga.json）。")
    pdf.code_block(
        "class ProjectFile(BaseModel):\n"
        '    version: str = "0.1.0"\n'
        '    name: str = "untitled"\n'
        "    ir: IR              # IR 数据\n"
        "    board: BoardConfig | None  # 板卡配置\n"
        "    simulation: SimulationConfig | None  # 仿真配置\n"
        "    canvas_state: dict  # UI状态（视口位置、缩放等）"
    )

    pdf.sub_title("5.7 SimulationConfig - 仿真配置")
    pdf.code_block(
        "class SimulationConfig(BaseModel):\n"
        '    simulator: str = "modelsim"  # 仿真器类型\n'
        "    clock_period_ns: float = 10.0  # 时钟周期 (ns)\n"
        "    reset_cycles: int = 10  # 复位持续周期数\n"
        "    sim_time_us: float = 100.0  # 仿真总时长 (us)\n"
        "    monitored_signals: list[str]  # 待抓取信号列表\n"
        '        # 格式: "module_id.port_name"'
    )

    pdf.sub_title("5.8 BoardConfig - 板卡配置")
    pdf.code_block(
        "class BoardConfig(BaseModel):\n"
        "    board_name: str         # 板卡名称\n"
        "    fpga_part: str          # FPGA 型号\n"
        "    clock_pins: dict[str,str]  # 时钟引脚映射\n"
        "    gpio_map: dict[str,str]    # GPIO 映射\n"
        "    constraints: str        # 约束文件内容"
    )

    # =========================================================================
    # 6. API 接口详细参考
    # =========================================================================
    pdf.add_page()
    pdf.section_title("6. API 接口详细参考")

    pdf.body(
        "所有 API 的基础 URL 为 http://localhost:8000/api。\n"
        "请求和响应均使用 JSON 格式。响应统一包含 \"success\" 字段表示操作是否成功。"
    )
    pdf.body(
        "测试 API 有两种方式：\n"
        "(1) 浏览器打开 http://localhost:8000/docs 使用 Swagger UI 交互式测试\n"
        "(2) 使用 curl 或 PowerShell 命令行测试\n"
        "以下每个接口都提供了 curl 和 PowerShell 两种测试命令。"
    )

    # -----------------------------------------------------------------
    pdf.check_page_break(60)
    pdf.sub_title("6.1 GET /api/health - 健康检查")

    pdf.body("功能说明：")
    pdf.body("检查后端服务是否正常运行。通常在服务启动后首先调用此接口确认服务可用。")

    pdf.body("请求格式：GET 请求，无需请求体。")

    pdf.body("响应格式：")
    pdf.code_block(
        '{\n'
        '  "status": "ok",\n'
        '  "service": "fpga-visual-tool-backend"\n'
        '}'
    )

    pdf.body("curl 测试命令：")
    pdf.code_block("curl http://localhost:8000/api/health")

    pdf.body("PowerShell 测试命令：")
    pdf.code_block("Invoke-RestMethod -Uri http://localhost:8000/api/health | ConvertTo-Json")

    pdf.body("预期结果：返回 HTTP 200，响应体包含 status=ok。")

    pdf.sub_sub_title("使用 pytest 测试")
    pdf.body("对应的自动化测试位于 tests/test_api.py 的 test_health 函数：")
    pdf.code_block(
        "@pytest.mark.asyncio\n"
        "async def test_health(client: AsyncClient):\n"
        '    resp = await client.get("/api/health")\n'
        "    assert resp.status_code == 200\n"
        "    data = resp.json()\n"
        '    assert data["status"] == "ok"'
    )
    pdf.body("运行此测试：")
    pdf.code_block("python -m pytest tests/test_api.py::test_health -v")

    # -----------------------------------------------------------------
    pdf.add_page()
    pdf.sub_title("6.2 POST /api/generate/top - 生成顶层模块")

    pdf.body("功能说明：")
    pdf.body(
        "这是最核心的 API。接收一个 IR 对象，自动生成完整的 Verilog 顶层模块代码。\n"
        "生成器会自动完成以下工作：\n"
        "(1) 遍历所有模块和封装子模块，扁平化处理\n"
        "(2) 推断顶层端口：未与其他模块连接的端口自动暴露为顶层 I/O，按名称去重\n"
        "(3) 为所有连线生成 wire 声明（使用用户标注的 wire 名或自动生成）\n"
        "(4) 位宽自动匹配，取两端中较大值\n"
        "(5) 为所有子模块生成例化语句，未连接端口悬空处理\n"
        "(6) 通过 Jinja2 模板渲染输出最终 Verilog 代码"
    )

    pdf.body("请求格式：")
    pdf.code_block(
        "POST /api/generate/top\n"
        'Content-Type: application/json\n\n'
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

    pdf.body("响应格式：")
    pdf.code_block(
        '{\n'
        '  "success": true,\n'
        '  "verilog": "module my_design(...)\\n  ...\\nendmodule\\n"\n'
        '}'
    )

    pdf.body("curl 测试命令（使用项目自带的 demo_input.json）：")
    pdf.code_block(
        "curl -X POST http://localhost:8000/api/generate/top ^\n"
        "  -H \"Content-Type: application/json\" ^\n"
        "  -d @demo_input.json"
    )

    pdf.body("PowerShell 测试命令：")
    pdf.code_block(
        "$body = Get-Content demo_input.json -Raw | ConvertFrom-Json\n"
        "$resp = Invoke-RestMethod -Uri http://localhost:8000/api/generate/top -Method Post -Body ($body | ConvertTo-Json -Depth 10) -ContentType \"application/json\"\n"
        "$resp.success\n"
        "$resp.verilog"
    )

    pdf.body("预期结果：返回一段完整的 Verilog 代码，包含 module blinky_demo 声明、input/output 端口、wire clk_divided 声明、clk_divider 和 led_controller 的例化。")

    pdf.sub_sub_title("使用 pytest 测试")
    pdf.code_block("python -m pytest tests/test_api.py::test_generate_top -v")

    # -----------------------------------------------------------------
    pdf.add_page()
    pdf.sub_title("6.3 POST /api/generate/testbench - 生成 Testbench")

    pdf.body("功能说明：")
    pdf.body(
        "根据 IR 和仿真配置自动生成 Testbench 框架代码。\n"
        "生成的 Testbench 包含：\n"
        "(1) 时钟生成逻辑（周期可配置）\n"
        "(2) 可配置的复位序列（持续 N 个周期后释放）\n"
        "(3) DUT（待测模块）例化\n"
        "(4) 激励占位区域（标记 // STIMULUS: 供用户添加测试激励）\n"
        "(5) $dumpfile/$dumpvars 波形导出语句\n"
        "(6) 仿真超时后自动 $finish"
    )

    pdf.body("请求格式：")
    pdf.code_block(
        "POST /api/generate/testbench\nContent-Type: application/json\n\n"
        "{\n"
        '  "ir": { IR对象 },\n'
        '  "simulation": {\n'
        '    "clock_period_ns": 10.0,\n'
        '    "reset_cycles": 5,\n'
        '    "sim_time_us": 100.0\n'
        "  }\n"
        "}"
    )

    pdf.body("响应格式：")
    pdf.code_block(
        '{\n'
        '  "success": true,\n'
        '  "verilog": "module tb_xxx...\\nendmodule\\n"\n'
        '}'
    )

    pdf.body("curl 测试命令：")
    pdf.code_block(
        "curl -X POST http://localhost:8000/api/generate/testbench ^\n"
        "  -H \"Content-Type: application/json\" ^\n"
        "  -d \"{\\\"ir\\\":{\\\"version\\\":\\\"0.1.0\\\",\\\"modules\\\":[],\\\"connections\\\":[],\\\"wrapped_modules\\\":[],\\\"top_module_name\\\":\\\"blinky\\\"},\\\"simulation\\\":{\\\"clock_period_ns\\\":10.0,\\\"reset_cycles\\\":5,\\\"sim_time_us\\\":100.0}}\""
    )

    pdf.body("预期结果：返回 Testbench 代码，包含 tb_blinky 模块、clk 生成逻辑、rst_n 复位序列、$dumpfile 语句和 $finish 语句。")

    pdf.sub_sub_title("使用 pytest 测试")
    pdf.code_block("python -m pytest tests/test_api.py::test_generate_testbench -v")

    # -----------------------------------------------------------------
    pdf.sub_title("6.4 POST /api/parse/verilog - 解析 Verilog 文件")

    pdf.body("功能说明：")
    pdf.body(
        "解析指定的 Verilog 文件（或目录），提取其中定义的模块信息。\n"
        "用于"导入已有工程"功能。支持 .v 和 .sv 扩展名。\n"
        "解析结果包括：模块名称、端口列表（方向/位宽）、内部子模块例化关系。\n"
        "注意：当前为基于正则表达式的解析器（demo 质量），对于复杂的 SystemVerilog 语法可能解析不完整。"
    )

    pdf.body("请求格式：")
    pdf.code_block(
        "POST /api/parse/verilog\nContent-Type: application/json\n\n"
        "{\n"
        '  "file_path": "D:/projects/my_module.v"\n'
        "}"
    )

    pdf.body("响应格式：")
    pdf.code_block(
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

    pdf.body("PowerShell 测试命令：")
    pdf.code_block(
        "# 首先创建一个测试用的 Verilog 文件\n"
        "Set-Content -Path test_sample.v -Value @\"\n"
        "module counter(input clk, input rst_n, output reg [3:0] q);\n"
        "always @(posedge clk) q <= q + 1;\n"
        "endmodule\n"
        '\"@\n\n'
        "# 调用解析 API\n"
        "$body = '{\"file_path\": \"test_sample.v\"}'\n"
        "Invoke-RestMethod -Uri http://localhost:8000/api/parse/verilog -Method Post -Body $body -ContentType \"application/json\" | ConvertTo-Json"
    )

    pdf.body("预期结果：返回 modules 数组，包含 counter 模块及其端口信息。")

    pdf.warning("如果文件不存在，返回 HTTP 404 错误。解析器对复杂语法（如 generate、interface、parameterized module）支持有限。")

    # -----------------------------------------------------------------
    pdf.sub_title("6.5 POST /api/parse/vcd - 解析 VCD 波形文件")

    pdf.body("功能说明：")
    pdf.body(
        "解析仿真产生的 VCD (Value Change Dump) 波形文件，返回结构化的波形数据。\n"
        "前端可使用这些数据渲染波形图。\n"
        "解析器支持：$timescale 时间单位、$var 信号定义、$dumpvars 初始值、#time 时间标记、单 bit 和多 bit 值变化。"
    )

    pdf.body("请求格式：")
    pdf.code_block(
        "POST /api/parse/vcd\nContent-Type: application/json\n\n"
        "{\n"
        '  "file_path": "D:/sim_output/waveform.vcd"\n'
        "}"
    )

    pdf.body("响应格式：")
    pdf.code_block(
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
        '    "total_time_ns": 30,\n'
        '    "timescale": "1ns"\n'
        '  }\n'
        '}'
    )

    pdf.body("每个信号包含一个 changes 数组，记录了每次值变化的时间点和值。total_time_ns 为整个波形的最大时间戳。")

    pdf.body("PowerShell 测试命令：")
    pdf.code_block(
        "# 创建测试 VCD 文件\n"
        "Set-Content -Path test_wave.vcd -Value @\"\n"
        "\$timescale 1ns \$end\n"
        "\$var wire 1 ! clk \$end\n"
        "\$dumpvars\n"
        "0!\n"
        "\$end\n"
        "#10\n"
        "1!\n"
        "#20\n"
        "0!\n"
        '\"@\n\n'
        "# 调用解析 API\n"
        "$body = '{\"file_path\": \"test_wave.vcd\"}'\n"
        "Invoke-RestMethod -Uri http://localhost:8000/api/parse/vcd -Method Post -Body $body -ContentType \"application/json\" | ConvertTo-Json -Depth 5"
    )

    pdf.body("预期结果：返回 waveform 对象，包含 clk 信号及其 3 次值变化记录。")

    pdf.sub_sub_title("使用 pytest 测试")
    pdf.code_block("python -m pytest tests/test_vcd.py -v")

    # -----------------------------------------------------------------
    pdf.add_page()
    pdf.sub_title("6.6 POST /api/project/save - 保存工程")

    pdf.body("功能说明：")
    pdf.body(
        "将完整的工程数据（包括 IR、板卡配置、仿真配置、画布状态）保存为 .fpga.json 文件。\n"
        "文件以 UTF-8 编码、格式化的 JSON 写入。目标目录不存在时会自动创建。"
    )

    pdf.body("请求格式：")
    pdf.code_block(
        "POST /api/project/save\nContent-Type: application/json\n\n"
        "{\n"
        '  "project": { ProjectFile 对象 },\n'
        '  "file_path": "D:/projects/my_design.fpga.json"\n'
        "}"
    )

    pdf.body("响应格式：")
    pdf.code_block(
        '{\n'
        '  "success": true,\n'
        '  "path": "D:/projects/my_design.fpga.json"\n'
        '}'
    )

    pdf.body("PowerShell 测试命令：")
    pdf.code_block(
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
        "$body = @{ project = $proj; file_path = \"test_project.fpga.json\" } | ConvertTo-Json -Depth 5\n"
        "Invoke-RestMethod -Uri http://localhost:8000/api/project/save -Method Post -Body $body -ContentType \"application/json\""
    )

    pdf.body("预期结果：在当前目录生成一个 test_project.fpga.json 文件，包含完整的工程数据。")

    # -----------------------------------------------------------------
    pdf.sub_title("6.7 POST /api/project/load - 加载工程")

    pdf.body("功能说明：")
    pdf.body(
        "从磁盘加载一个 .fpga.json 工程文件，返回完整的 ProjectFile 对象。\n"
        "文件不存在时返回 404 错误，JSON 格式无效时返回 400 错误。"
    )

    pdf.body("请求格式：")
    pdf.code_block(
        "POST /api/project/load\nContent-Type: application/json\n\n"
        "{\n"
        '  "file_path": "test_project.fpga.json"\n'
        "}"
    )

    pdf.body("响应格式：")
    pdf.code_block(
        '{\n'
        '  "success": true,\n'
        '  "project": {\n'
        '    "version": "0.1.0",\n'
        '    "name": "my_test_project",\n'
        '    "ir": { ... }\n'
        '  }\n'
        '}'
    )

    pdf.body("PowerShell 测试命令（先保存再加载）：")
    pdf.code_block(
        "$body = '{\"file_path\": \"test_project.fpga.json\"}'\n"
        "$resp = Invoke-RestMethod -Uri http://localhost:8000/api/project/load -Method Post -Body $body -ContentType \"application/json\"\n"
        "$resp.success\n"
        "$resp.project.name"
    )

    pdf.body("预期结果：返回 success=true，project.name 为保存时设置的名称 my_test_project。")

    pdf.sub_sub_title("保存+加载集成测试")
    pdf.code_block("python -m pytest tests/test_api.py::test_save_and_load_project -v")

    # -----------------------------------------------------------------
    pdf.add_page()
    pdf.sub_title("6.8 POST /api/simulate/compile - 编译 HDL 源文件")

    pdf.body("功能说明：")
    pdf.body(
        "使用 ModelSim/Questa 的 vlib 和 vlog 命令编译 Verilog 源文件。\n"
        "流程：(1) vlib work 创建 work 库；(2) 对每个源文件执行 vlog -work work <file>。\n"
        "编译错误和警告会被捕获并返回。"
    )

    pdf.warning("此接口需要本地安装 ModelSim/Questa，且 vlib/vlog 命令必须在系统 PATH 中或通过 executable_path 指定安装路径。")

    pdf.body("请求格式：")
    pdf.code_block(
        "POST /api/simulate/compile\nContent-Type: application/json\n\n"
        "{\n"
        '  "sources": ["src/counter.v", "src/top.v"],\n'
        '  "work_dir": "./sim_work"\n'
        "}"
    )

    pdf.body("响应格式：")
    pdf.code_block(
        '{\n'
        '  "success": true,\n'
        '  "stdout": "编译输出...",\n'
        '  "errors": [],\n'
        '  "warnings": []\n'
        '}'
    )

    # -----------------------------------------------------------------
    pdf.sub_title("6.9 POST /api/simulate/run - 运行仿真")

    pdf.body("功能说明：")
    pdf.body(
        "使用 ModelSim/Questa 的 vsim 命令运行仿真。\n"
        "流程：(1) 生成 TCL 批处理脚本（包含 vcd add 命令）；(2) 执行 vsim -c -do <tcl_script>。\n"
        "可选择同时编译源文件再运行（提供 sources 参数）。\n"
        "仿真结束后返回 VCD 波形文件路径。"
    )

    pdf.warning("此接口需要本地安装 ModelSim/Questa。确保 vsim 命令在系统 PATH 中。")

    pdf.body("请求格式：")
    pdf.code_block(
        "POST /api/simulate/run\nContent-Type: application/json\n\n"
        "{\n"
        '  "top_module": "my_top",\n'
        '  "sim_time": "1us",\n'
        '  "work_dir": "./sim_work",\n'
        '  "sources": ["src/counter.v", "src/top.v"]\n'
        "}"
    )

    pdf.body("响应格式：")
    pdf.code_block(
        '{\n'
        '  "success": true,\n'
        '  "vcd_path": "./sim_work/my_top.vcd",\n'
        '  "stdout": "仿真输出...",\n'
        '  "errors": [],\n'
        '  "warnings": []\n'
        '}'
    )

    # =========================================================================
    # 7. 测试指南
    # =========================================================================
    pdf.add_page()
    pdf.section_title("7. 测试指南")

    pdf.sub_title("7.1 测试框架概述")
    pdf.body(
        "项目包含 23 个测试用例，分布在 4 个测试文件中。\n"
        "测试框架: pytest + pytest-asyncio (异步测试) + httpx (HTTP 客户端)\n"
        "测试配置: pyproject.toml 中 asyncio_mode = auto\n"
        "API 测试使用 httpx AsyncClient + ASGI transport，无需启动真实服务器即可测。"
    )

    pdf.sub_title("7.2 运行全部测试")
    pdf.body("在 backend 目录下执行：")
    pdf.code_block("cd backend\npython -m pytest tests/ -v")
    pdf.body("预期输出：23 passed，全部绿色通过。")

    pdf.body("查看更详细的输出（含 print 语句）：")
    pdf.code_block("python -m pytest tests/ -v -s")

    pdf.body("生成测试覆盖率报告（需安装 pytest-cov）：")
    pdf.code_block("pip install pytest-cov\npython -m pytest tests/ --cov=app --cov-report=html")

    # -----------------------------------------------------------------
    pdf.sub_title("7.3 test_ir.py - 数据模型测试 (9个)")

    pdf.body("测试内容：验证所有 Pydantic 数据模型的创建、序列化和反序列化。")
    pdf.code_block("python -m pytest tests/test_ir.py -v")

    pdf.body("包含以下测试类：")
    pdf.bullet("TestPort (3个测试): test_create_simple_port (默认参数), test_create_bus_port (多位宽有符号), test_auto_id (自动ID唯一性)")
    pdf.bullet("TestModule (2个测试): test_create_module (空模块创建), test_module_with_ports (带端口模块)")
    pdf.bullet("TestConnection (1个测试): test_connection (连线创建与wire_name)")
    pdf.bullet("TestIR (2个测试): test_empty_ir (默认IR), test_ir_with_data (完整IR)")
    pdf.bullet("TestProjectFile (2个测试): test_default_project (默认工程), test_serialize_deserialize (序列化往返校验)")

    pdf.body("每个测试验证什么：")
    pdf.bullet("TestPort: 验证端口名称、方向、位宽默认值(1)、有无符号默认值(false)、auto_id 长度为12")
    pdf.bullet("TestModule: 验证模块名、类型、端口列表、config 字典")
    pdf.bullet("TestConnection: 验证源/目标模块和端口、wire_name 标注")
    pdf.bullet("TestIR: 验证版本号(0.1.0)、默认顶层名(top)、modules/connections 列表")
    pdf.bullet("TestProjectFile: 验证 model_dump 和 model_validate 的往返正确性")

    # -----------------------------------------------------------------
    pdf.sub_title("7.4 test_generators.py - 代码生成器测试 (5个)")

    pdf.body("测试内容：验证 TopGenerator 和 TestbenchGenerator 的输出正确性。")
    pdf.code_block("python -m pytest tests/test_generators.py -v")

    pdf.body("TestTopGenerator (3个测试):")
    pdf.bullet("test_generate_simple_top: 两个模块直连 -> 验证生成的 Verilog 包含 module/endmodule/wire/例化")
    pdf.bullet("test_infer_top_ports: 未连接端口的模块 -> 验证端口被暴露为顶层 input/output")
    pdf.bullet("test_multiple_connections: 多模块多连线 -> 验证所有自定义 wire 名出现在输出中")

    pdf.body("TestTestbenchGenerator (2个测试):")
    pdf.bullet("test_generate_tb: 带仿真配置的 IR -> 验证 TB 包含模块名、clk/rst_n、$dumpfile、$finish、DUT 例化")
    pdf.bullet("test_tb_includes_clock_period: 指定时钟周期 -> 验证周期值出现在生成的 TB 中")

    # -----------------------------------------------------------------
    pdf.sub_title("7.5 test_vcd.py - VCD 解析器测试 (4个)")

    pdf.body("测试内容：验证自研 VCD 解析器对 VCD 文件内容的正确解析。")
    pdf.code_block("python -m pytest tests/test_vcd.py -v")

    pdf.body("TestVCDParser (3个测试):")
    pdf.bullet("test_parse_simple_vcd: 包含 clk(1bit) 和 data(4bit) 两个信号的完整 VCD -> 验证信号数量、位宽、值变化")
    pdf.bullet("test_empty_vcd: 仅含 timescale 的 VCD -> 验证 signals 为空，total_time_ns 为 0")

    pdf.body("TestWaveformData (1个测试):")
    pdf.bullet("test_to_dict: 构建 SignalTrace 并调用 to_dict() -> 验证字典结构正确、包含 name/width/changes/total_time_ns")

    # -----------------------------------------------------------------
    pdf.sub_title("7.6 test_api.py - API 端点集成测试 (5个)")

    pdf.body("测试内容：端到端 HTTP 测试，验证所有主要 API 端点。")
    pdf.body("注意：API 测试使用 ASGI transport，直接在内存中测试 app 实例，无需启动服务器。")
    pdf.code_block("python -m pytest tests/test_api.py -v")

    pdf.body("包含的测试：")
    pdf.bullet("test_health: GET /api/health -> 验证 status_code==200, status==ok")
    pdf.bullet("test_generate_top: POST /api/generate/top 发送含1模块0连线的IR -> 验证 Verilog 包含 module/endmodule")
    pdf.bullet("test_generate_testbench: POST /api/generate/testbench 发送空IR+仿真配置 -> 验证 TB 包含模块名")
    pdf.bullet("test_save_and_load_project: 先 POST save 再 POST load -> 验证加载的工程名与保存的一致")
    pdf.bullet("test_parse_vcd_not_found: POST /api/parse/vcd 用不存在文件 -> 验证返回 404")

    # -----------------------------------------------------------------
    pdf.sub_title("7.7 如何编写新测试")

    pdf.body("编写数据模型测试（参考 test_ir.py）：")
    pdf.code_block(
        "# 在 tests/ 下创建 test_xxx.py\n"
        "import pytest\n"
        "from app.models.ir import Port, PortDirection\n\n"
        "class TestYourFeature:\n"
        "    def test_something(self):\n"
        '        p = Port(name="test", direction=PortDirection.INPUT)\n'
        '        assert p.name == "test"'
    )

    pdf.body("编写 API 测试（参考 test_api.py）：")
    pdf.code_block(
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
        "    assert resp.json()['success']"
    )

    # =========================================================================
    # 8. 完整工作流演示
    # =========================================================================
    pdf.add_page()
    pdf.section_title("8. 完整工作流演示")

    pdf.body(
        "本章演示一个完整的端到端工作流：从启动服务到生成顶层模块、生成 Testbench、"
        "解析文件、保存/加载工程。使用项目自带的 demo_input.json 示例文件。"
    )

    pdf.sub_title("8.1 准备工作")
    pdf.numbered("第1步", "打开终端，进入 backend 目录并启动服务：")
    pdf.code_block("cd D:\\claude\\prj\\backend\npython main.py")
    pdf.body("看到 \"Application startup complete.\" 说明服务已就绪。")

    pdf.numbered("第2步", "打开另一个终端窗口（保留服务运行），验证服务：")
    pdf.code_block("curl http://localhost:8000/api/health")
    pdf.body('预期返回: {"status":"ok","service":"fpga-visual-tool-backend"}')

    pdf.numbered("第3步", "打开 Swagger UI 浏览器窗口（可选，方便可视化测试）：")
    pdf.code_block("# 浏览器打开: http://localhost:8000/docs")

    pdf.sub_title("8.2 生成顶层模块 - 详细步骤")
    pdf.numbered("第1步", "查看 demo_input.json 的内容。该文件包含 2 个模块（clk_divider, led_controller）和 1 根连线（clk_out -> clk），顶层名为 blinky_demo。")
    pdf.numbered("第2步", "发送生成请求：")
    pdf.code_block(
        "curl -X POST http://localhost:8000/api/generate/top ^\n"
        "  -H \"Content-Type: application/json\" ^\n"
        "  -d @demo_input.json"
    )

    pdf.numbered("第3步", "预期的生成结果（关键内容）：")
    pdf.code_block(
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

    pdf.body("验证要点：")
    pdf.bullet("顶层端口 clk_in/rst_n 被推断为 input（因为它们连接的模块端口都是 input）")
    pdf.bullet("led_out 被推断为 output（连接的模块端口是 output）")
    pdf.bullet("clk_divided 被声明为 wire（两个模块之间的连线）")
    pdf.bullet("两个模块都被正确例化，端口映射正确")

    pdf.sub_title("8.3 生成 Testbench - 详细步骤")
    pdf.body("使用与上一步相同的 IR 结构，加上仿真配置参数：")
    pdf.code_block(
        "curl -X POST http://localhost:8000/api/generate/testbench ^\n"
        "  -H \"Content-Type: application/json\" ^\n"
        "  -d \"{\\\"ir\\\":{\\\"version\\\":\\\"0.1.0\\\",\\\"modules\\\":[],\\\"connections\\\":[],\\\"wrapped_modules\\\":[],\\\"top_module_name\\\":\\\"blinky\\\"},\\\"simulation\\\":{\\\"clock_period_ns\\\":10.0,\\\"reset_cycles\\\":5,\\\"sim_time_us\\\":100.0}}\""
    )
    pdf.body("预期输出包含：")
    pdf.bullet("module tb_blinky 声明")
    pdf.bullet("forever #5.0 clk = ~clk（10ns 周期的时钟生成）")
    pdf.bullet("repeat(5) @(posedge clk)（5 个周期的复位）")
    pdf.bullet("blinky u_dut(...)（DUT 例化）")
    pdf.bullet("$dumpfile 和 $dumpvars（波形导出配置）")
    pdf.bullet("#100000; $finish（100us 后结束仿真）")

    pdf.sub_title("8.4 解析 Verilog 文件")
    pdf.numbered("第1步", "先创建一个测试用的 Verilog 文件：")
    pdf.code_block(
        "echo module counter(input clk, input rst_n, output reg [3:0] q); > test_sample.v\n"
        "echo always @(posedge clk) q ^<= q + 1; >> test_sample.v\n"
        "echo endmodule >> test_sample.v"
    )
    pdf.numbered("第2步", "调用解析 API：")
    pdf.code_block(
        "curl -X POST http://localhost:8000/api/parse/verilog ^\n"
        "  -H \"Content-Type: application/json\" ^\n"
        "  -d \"{\\\"file_path\\\": \\\"test_sample.v\\\"}\""
    )
    pdf.body("预期返回 counter 模块的端口信息：clk(input,1bit), rst_n(input,1bit), q(output,4bit)。")

    pdf.sub_title("8.5 解析 VCD 波形")
    pdf.numbered("第1步", "创建测试 VCD 文件：")
    pdf.code_block(
        "echo $timescale 1ns $end > test_wave.vcd\n"
        "echo $var wire 1 ! clk $end >> test_wave.vcd\n"
        "echo $dumpvars >> test_wave.vcd\n"
        "echo 0! >> test_wave.vcd\n"
        "echo $end >> test_wave.vcd\n"
        "echo #10 >> test_wave.vcd\n"
        "echo 1! >> test_wave.vcd"
    )
    pdf.numbered("第2步", "调用解析 API：")
    pdf.code_block(
        "curl -X POST http://localhost:8000/api/parse/vcd ^\n"
        "  -H \"Content-Type: application/json\" ^\n"
        "  -d \"{\\\"file_path\\\": \\\"test_wave.vcd\\\"}\""
    )
    pdf.body("预期返回 clk 信号的波形数据，包含 2 次值变化（0ns 时值为 0，10ns 时值为 1）。")

    pdf.sub_title("8.6 保存和加载工程")
    pdf.numbered("第1步", "保存工程：")
    pdf.code_block(
        "curl -X POST http://localhost:8000/api/project/save ^\n"
        "  -H \"Content-Type: application/json\" ^\n"
        "  -d \"{\\\"project\\\":{\\\"version\\\":\\\"0.1.0\\\",\\\"name\\\":\\\"demo\\\",\\\"ir\\\":{\\\"version\\\":\\\"0.1.0\\\",\\\"modules\\\":[],\\\"connections\\\":[],\\\"wrapped_modules\\\":[],\\\"top_module_name\\\":\\\"top\\\"}},\\\"file_path\\\":\\\"demo_project.fpga.json\\\"}\""
    )
    pdf.numbered("第2步", "加载工程：")
    pdf.code_block(
        "curl -X POST http://localhost:8000/api/project/load ^\n"
        "  -H \"Content-Type: application/json\" ^\n"
        "  -d \"{\\\"file_path\\\": \\\"demo_project.fpga.json\\\"}\""
    )
    pdf.body("预期加载的工程 name 为 demo，与保存时一致。")

    # =========================================================================
    # 9. 常见问题与故障排除
    # =========================================================================
    pdf.add_page()
    pdf.section_title("9. 常见问题与故障排除")

    pdf.sub_title("Q1: 启动服务时提示端口被占用")
    pdf.body("错误信息: \"Address already in use\"")
    pdf.body("解决方法：更换端口号启动")
    pdf.code_block("uvicorn main:app --reload --host 0.0.0.0 --port 8001")
    pdf.body("或查找并关闭占用 8000 端口的进程：")
    pdf.code_block(
        "# 查找占用 8000 端口的进程\n"
        "netstat -ano | findstr :8000\n"
        "# 记下 PID，然后终止该进程\n"
        "taskkill /PID <PID> /F"
    )

    pdf.sub_title("Q2: 导入模块时报 ModuleNotFoundError")
    pdf.body("错误信息: \"ModuleNotFoundError: No module named 'app'\"")
    pdf.body("解决方法：确保在 backend 目录下执行命令，或将 backend 加入 PYTHONPATH")
    pdf.code_block(
        "cd D:\\claude\\prj\\backend\n"
        "python -m pytest tests/ -v"
    )

    pdf.sub_title("Q3: pytest 找不到测试文件")
    pdf.body("解决方法：确认 pyproject.toml 配置正确，测试文件以 test_ 开头")
    pdf.code_block(
        "# pyproject.toml 中的配置\n"
        "[tool.pytest.ini_options]\n"
        'testpaths = ["tests"]\n'
        'pythonpath = ["."]'
    )

    pdf.sub_title("Q4: 代码生成结果中的端口丢失或 wire 名不对")
    pdf.body("可能原因：")
    pdf.bullet("IR 中 module.id 和 Connection 中 src_module/dst_module 不匹配")
    pdf.bullet("端口名称大小写不一致")
    pdf.bullet("封装模块的内部连线未正确扁平化")
    pdf.body("排查方法：检查 demo_input.json 的格式，确保 module.id 与 connection 中的 module 引用一致")

    pdf.sub_title("Q5: 仿真接口报错 'vlib/vlog/vsim not found'")
    pdf.body("原因：ModelSim/Questa 未安装或不在 PATH 中。")
    pdf.body("解决方法：")
    pdf.bullet("安装 ModelSim/Questa 到本地")
    pdf.bullet("将安装路径添加到系统 PATH 环境变量")
    pdf.bullet("或在创建 ModelSimSimulator 时传入 executable_path 参数指定安装目录")

    pdf.sub_title("Q6: VCD 解析结果为空")
    pdf.body("可能原因：")
    pdf.bullet("VCD 文件格式不规范（某些仿真器生成的 VCD 有变体语法）")
    pdf.bullet("$var 定义使用了多行格式，解析器未正确处理")
    pdf.bullet("信号 ID 代码使用了非标准字符")
    pdf.body("排查方法：先用简单的测试 VCD 文件验证解析器是否正常，然后逐步增加复杂度。")

    # =========================================================================
    # 10. 附录
    # =========================================================================
    pdf.add_page()
    pdf.section_title("10. 附录")

    pdf.sub_title("10.1 依赖列表")
    pdf.body("requirements.txt 完整内容：")
    pdf.code_block(
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

    pdf.sub_title("10.2 demo_input.json 示例文件")
    pdf.body("项目根目录下的 demo_input.json 包含了一个完整的 IR 示例：")
    pdf.code_block(
        "{\n"
        '  "ir": {\n'
        '    "version": "0.1.0",\n'
        '    "modules": [\n'
        "      {\n"
        '        "id": "m1",\n'
        '        "name": "clk_divider",\n'
        '        "instance_name": "u_div",\n'
        '        "type": "base",\n'
        '        "ports": [\n'
        '          {"name": "clk_in",  "direction": "input",  "width": 1},\n'
        '          {"name": "rst_n",   "direction": "input",  "width": 1},\n'
        '          {"name": "clk_out", "direction": "output", "width": 1}\n'
        "        ],\n"
        '        "position": [0, 0],\n'
        '        "config": {"div_factor": 4}\n'
        "      },\n"
        "      {\n"
        '        "id": "m2",\n'
        '        "name": "led_controller",\n'
        '        "instance_name": "u_led",\n'
        '        "type": "base",\n'
        '        "ports": [\n'
        '          {"name": "clk",     "direction": "input",  "width": 1},\n'
        '          {"name": "rst_n",   "direction": "input",  "width": 1},\n'
        '          {"name": "led_out", "direction": "output", "width": 4}\n'
        "        ],\n"
        '        "position": [300, 0],\n'
        '        "config": {}\n'
        "      }\n"
        "    ],\n"
        '    "connections": [\n'
        "      {\n"
        '        "id": "c1",\n'
        '        "src_module": "m1",\n'
        '        "src_port": "clk_out",\n'
        '        "dst_module": "m2",\n'
        '        "dst_port": "clk",\n'
        '        "wire_name": "clk_divided"\n'
        "      }\n"
        "    ],\n"
        '    "wrapped_modules": [],\n'
        '    "top_module_name": "blinky_demo"\n'
        "  }\n"
        "}"
    )

    pdf.sub_title("10.3 ModelSim 环境要求")
    pdf.body("仿真功能需要本地安装 ModelSim 或 Questa Sim。")
    pdf.body("安装后，以下命令需要在终端中可直接调用：")
    pdf.bullet("vlib -- 创建仿真库")
    pdf.bullet("vlog -- 编译 Verilog 源文件")
    pdf.bullet("vcom -- 编译 VHDL 源文件（如果使用 VHDL）")
    pdf.bullet("vsim -- 运行仿真")
    pdf.body("如果未安装 ModelSim，模拟仿真相关的 API（/api/simulate/compile 和 /api/simulate/run）将无法使用，但其他所有 API 功能不受影响。")
    pdf.body("对于 CI/CD 环境，可以使用免费的 Icarus Verilog (iverilog) 作为替代方案（需实现对应的 Simulator 子类）。")

    pdf.ln(4)
    pdf.set_font("CJK", "B", 12)
    pdf.set_text_color(25, 60, 120)
    pdf.cell(0, 10, "-- 手册结束 --", align="C")

    # =========================================================================
    # Save
    # =========================================================================
    output_path = os.path.join(os.path.dirname(__file__), "FPGA_Backend_Manual_CN.pdf")
    pdf.output(output_path)
    print(f"Manual saved to: {output_path}")
    print(f"Pages: {pdf.page_no()}")
    return output_path


if __name__ == "__main__":
    build_manual()
