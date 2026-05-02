"""
Generate PDF user manual for FPGA Visual Programming Tool backend.
"""
import os
from fpdf import FPDF

class ManualPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, "FPGA Visual Programming Tool - Backend Manual", align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(33, 65, 132)
        self.cell(0, 10, self._safe(title))
        self.ln(8)
        # underline
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def sub_title(self, title: str):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(59, 105, 176)
        self.cell(0, 8, self._safe(title))
        self.ln(7)

    @staticmethod
    def _safe(text: str) -> str:
        """Replace Unicode chars with ASCII equivalents for latin-1 font."""
        replacements = {
            "—": "--",   # em dash
            "–": "-",    # en dash
            "‘": "'",    # left single quote
            "’": "'",    # right single quote
            "“": '"',    # left double quote
            "”": '"',    # right double quote
            "…": "...",  # ellipsis
            "•": "-",    # bullet
            "→": "->",   # right arrow
            "←": "<-",   # left arrow
            "†": "+",    # dagger
            "≤": "<=",   # less than or equal
            "≥": ">=",   # greater than or equal
            " ": " ",    # non-breaking space
        }
        for uni, ascii_val in replacements.items():
            text = text.replace(uni, ascii_val)
        # Remove any remaining non-latin-1 chars
        result = []
        for ch in text:
            try:
                ch.encode("latin-1")
                result.append(ch)
            except UnicodeEncodeError:
                result.append("?")
        return "".join(result)

    def body(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, self._safe(text))
        self.ln(1)

    def code_block(self, code: str):
        self.set_fill_color(245, 245, 247)
        self.set_line_width(0.3)
        self.set_font("Courier", "", 9)
        self.set_text_color(40, 40, 40)
        lines = code.split("\n")
        block_h = len(lines) * 5 + 6
        if self.get_y() + block_h > self.h - 20:
            self.add_page()
        y0 = self.get_y()
        self.rect(self.l_margin, y0, self.w - self.l_margin - self.r_margin, block_h, style="DF")
        self.set_xy(self.l_margin + 3, y0 + 2)
        for line in lines:
            self.cell(0, 5, self._safe(line))
            self.ln(5)
            self.set_x(self.l_margin + 3)
        self.ln(5)

    def bullet(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.cell(8, 5.5, "-")
        self.multi_cell(0, 5.5, self._safe(text))
        self.ln(0.5)

    def numbered(self, num: int, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.cell(10, 5.5, f"{num}.")
        self.multi_cell(0, 5.5, self._safe(text))
        self.ln(0.5)


def build_manual():
    pdf = ManualPDF("P", "mm", "A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(True, 18)
    pdf.set_left_margin(18)
    pdf.set_right_margin(18)

    # ─── Cover Page ───
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(33, 65, 132)
    pdf.multi_cell(0, 12, "FPGA Visual Programming Tool\nBackend User Manual", align="C")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Version 0.1.0  |  May 2026", align="C")
    pdf.ln(16)
    pdf.set_line_width(0.6)
    pdf.set_draw_color(33, 65, 132)
    mid_x = pdf.w / 2
    pdf.line(mid_x - 30, pdf.get_y(), mid_x + 30, pdf.get_y())
    pdf.ln(12)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, "Framework: FastAPI + Uvicorn", align="C")
    pdf.ln(7)
    pdf.cell(0, 8, "Language: Python 3.11+", align="C")
    pdf.ln(7)
    pdf.cell(0, 8, "Template Engine: Jinja2", align="C")
    pdf.ln(7)
    pdf.cell(0, 8, "Data Model: Pydantic v2", align="C")

    # ─── Table of Contents ───
    pdf.add_page()
    pdf.section_title("Table of Contents")
    toc = [
        "1. Project Overview",
        "2. Quick Start",
        "  2.1 Installation",
        "  2.2 Starting the Server",
        "3. Architecture Overview",
        "  3.1 Project Structure",
        "  3.2 Data Flow",
        "4. IR Data Model (Intermediate Representation)",
        "5. API Reference",
        "  5.1 Health Check",
        "  5.2 Code Generation - Top Module",
        "  5.3 Code Generation - Testbench",
        "  5.4 Parsing - Verilog",
        "  5.5 Parsing - VCD Waveform",
        "  5.6 Project Management - Save",
        "  5.7 Project Management - Load",
        "  5.8 Simulation - Compile",
        "  5.9 Simulation - Run",
        "6. Running Tests",
        "7. Demo: Quick Workflow",
        "8. Appendix: Dependencies",
    ]
    pdf.set_font("Helvetica", "", 10)
    for item in toc:
        indent = 4 if item.startswith("  ") else 0
        pdf.set_x(18 + indent)
        pdf.cell(0, 6, item.strip())
        pdf.ln(6)

    # ─── 1. Project Overview ───
    pdf.add_page()
    pdf.section_title("1. Project Overview")
    pdf.body(
        "The FPGA Visual Programming Tool backend provides a REST API service for "
        "the visual FPGA design workflow. It handles Verilog/VHDL code generation, "
        "hardware description parsing, simulation orchestration, and waveform analysis."
    )
    pdf.sub_title("Core Capabilities")
    pdf.bullet("IR-based Verilog Top module generation (auto port inference, wire declaration, instantiation)")
    pdf.bullet("Testbench scaffolding with clock generation, reset sequence, stimulus placeholders")
    pdf.bullet("Verilog file parsing for importing existing projects (regex-based, demo quality)")
    pdf.bullet("VCD waveform file parsing for simulation result visualization")
    pdf.bullet("ModelSim/Questa simulation integration (vlib/vlog/vsim via subprocess)")
    pdf.bullet("Project file save/load (.fpga.json format)")

    # ─── 2. Quick Start ───
    pdf.section_title("2. Quick Start")
    pdf.sub_title("2.1 Installation")
    pdf.body("Requirements: Python 3.11 or newer.")
    pdf.code_block(
        "cd backend\n"
        "pip install -r requirements.txt"
    )
    pdf.body("Dependencies include: FastAPI, Uvicorn, Pydantic v2, Jinja2, pytest, httpx.")

    pdf.sub_title("2.2 Starting the Server")
    pdf.body("Development mode (with hot reload):")
    pdf.code_block(
        "cd backend\n"
        "python main.py\n"
        "# or:\n"
        "uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    )
    pdf.body("The server starts at http://localhost:8000. Open http://localhost:8000/docs for the auto-generated Swagger API documentation, or http://localhost:8000/redoc for ReDoc.")

    # ─── 3. Architecture Overview ───
    pdf.section_title("3. Architecture Overview")
    pdf.sub_title("3.1 Project Structure")
    pdf.code_block(
        "backend/\n"
        "  main.py              # FastAPI app entry point\n"
        "  requirements.txt     # Python dependencies\n"
        "  pyproject.toml       # Pytest configuration\n"
        "  demo_input.json      # Sample IR input\n"
        "  app/\n"
        "    routes.py           # All API endpoint definitions\n"
        "    models/\n"
        "      ir.py             # IR data models (Pydantic)\n"
        "    generators/\n"
        "      top.py            # Top-module Verilog generator\n"
        "      testbench.py      # Testbench generator\n"
        "      templates/\n"
        "        top.v.j2        # Top module Jinja2 template\n"
        "        testbench.v.j2  # Testbench Jinja2 template\n"
        "    parser/\n"
        "      verilog_parser.py # Verilog parsing (regex)\n"
        "    simulator/\n"
        "      base.py           # Abstract simulator interface\n"
        "      modelsim.py       # ModelSim simulator backend\n"
        "    utils/\n"
        "      vcd_parser.py     # VCD waveform parser\n"
        "  tests/\n"
        "    test_ir.py          # IR model tests\n"
        "    test_generators.py  # Generator tests\n"
        "    test_vcd.py         # VCD parser tests\n"
        "    test_api.py         # API endpoint tests"
    )

    pdf.sub_title("3.2 Data Flow")
    pdf.body(
        "The frontend canvas produces an IR (Intermediate Representation) JSON object "
        "describing modules, ports, and connections. This IR is the single exchange format "
        "between the frontend and backend. The backend processes the IR and generates "
        "Verilog code, parses input files, or orchestrates simulation."
    )
    pdf.code_block(
        "Frontend Canvas\n"
        "    |\n"
        "    v\n"
        "IR (JSON) --POST--> /api/generate/top\n"
        "                        |\n"
        "    Jinja2 Template <---+--- Port inference\n"
        "                        |    Wire declaration\n"
        "                        |    Instantiation\n"
        "                        v\n"
        "                  Verilog (.v)"
    )

    # ─── 4. IR Data Model ───
    pdf.section_title("4. IR Data Model (Intermediate Representation)")
    pdf.body(
        "All Pydantic v2 models are defined in app/models/ir.py. The IR is versioned "
        "for forward/backward compatibility."
    )
    pdf.sub_title("Core Types")
    pdf.body("Port — defines a module port (name, direction, width, signed, array_size)")
    pdf.body("Module — a design node on the canvas (id, name, type, ports[], position, config{})")
    pdf.body("Connection — an edge between two ports (src_module, src_port, dst_module, dst_port, wire_name)")
    pdf.body("WrappedModule — a user-encapsulated sub-design (name, exposed_ports[], internal_modules[], internal_connections[])")
    pdf.body("IR — the top-level intermediate representation (version, modules[], connections[], wrapped_modules[], top_module_name)")
    pdf.body("ProjectFile — complete project save file (version, name, ir, board, simulation, canvas_state)")
    pdf.body("SimulationConfig — simulation parameters (simulator, clock_period_ns, reset_cycles, sim_time_us, monitored_signals[])")
    pdf.body("BoardConfig — board-specific IP configuration (board_name, fpga_part, clock_pins{}, gpio_map{}, constraints)")

    pdf.sub_title("Module Types")
    pdf.bullet("base: standard user-defined or imported module")
    pdf.bullet("wrapped: encapsulated sub-circuit (can expand/collapse)")
    pdf.bullet("board_ip: vendor-provided IP core (PLL, GPIO, UART, etc.)")

    # ─── 5. API Reference ───
    pdf.section_title("5. API Reference")
    pdf.body("Base URL: http://localhost:8000/api. All requests use JSON. Responses return {\"success\": bool, ...}.")

    pdf.sub_title("5.1 GET /api/health")
    pdf.body("Health check endpoint. Returns service status.")
    pdf.code_block(
        'GET /api/health\n'
        'Response: {"status": "ok", "service": "fpga-visual-tool-backend"}'
    )

    pdf.sub_title("5.2 POST /api/generate/top")
    pdf.body("Generate Verilog top-module code from an IR object.")
    pdf.code_block(
        "POST /api/generate/top\n"
        "Body: { \"ir\": { IR object } }\n"
        "Response: { \"success\": true, \"verilog\": \"...\" }"
    )
    pdf.body("The generator automatically: (a) infers top-level ports from unconnected module ports; (b) creates wire declarations for all connections; (c) instantiates all sub-modules with proper port mapping; and (d) leaves unused ports disconnected with comments.")

    pdf.sub_title("5.3 POST /api/generate/testbench")
    pdf.body("Generate a simulation testbench framework from an IR and simulation config.")
    pdf.code_block(
        "POST /api/generate/testbench\n"
        "Body: { \"ir\": { IR }, \"simulation\": { SimulationConfig } }\n"
        "Response: { \"success\": true, \"verilog\": \"...\" }"
    )
    pdf.body("The testbench includes: clock generation, configurable reset sequence, DUT instantiation, stimulus placeholder section, $dumpfile/$dumpvars for waveform export, and $finish at end of simulation.")

    pdf.sub_title("5.4 POST /api/parse/verilog")
    pdf.body("Parse a Verilog file or directory, extracting module definitions and instantiation relationships.")
    pdf.code_block(
        "POST /api/parse/verilog\n"
        'Body: { "file_path": "/path/to/file.v" }\n'
        "Response: { \"success\": true, \"modules\": [...] }"
    )
    pdf.body("Supports .v and .sv extensions. This is a regex-based parser (demo quality); for production use, integrate pyverilog or sv-parser for full SystemVerilog AST support.")

    pdf.sub_title("5.5 POST /api/parse/vcd")
    pdf.body("Parse a VCD waveform file into structured JSON for frontend visualization.")
    pdf.code_block(
        "POST /api/parse/vcd\n"
        'Body: { "file_path": "/path/to/waveform.vcd" }\n'
        "Response: { \"success\": true, \"waveform\": { \"signals\": [...], ... } }"
    )
    pdf.body("Each signal in the response contains a changes[] array with {time_ns, value} pairs, plus metadata (width, signed). Supports $var, $dumpvars, #time markers, multi-bit bus values.")

    pdf.sub_title("5.6 POST /api/project/save")
    pdf.body("Save a complete project to a .fpga.json file on disk.")
    pdf.code_block(
        "POST /api/project/save\n"
        "Body: { \"project\": { ProjectFile }, \"file_path\": \"...\" }\n"
        "Response: { \"success\": true, \"path\": \"...\" }"
    )

    pdf.sub_title("5.7 POST /api/project/load")
    pdf.body("Load a .fpga.json project file from disk.")
    pdf.code_block(
        "POST /api/project/load\n"
        'Body: { "file_path": "/path/to/project.fpga.json" }\n'
        "Response: { \"success\": true, \"project\": { ProjectFile } }"
    )

    pdf.sub_title("5.8 POST /api/simulate/compile")
    pdf.body("Compile HDL source files using ModelSim/Questa (requires local installation).")
    pdf.code_block(
        "POST /api/simulate/compile\n"
        'Body: { "sources": ["src1.v", "src2.v"], "work_dir": "./sim_work" }\n'
        "Response: { \"success\": true, \"stdout\": \"...\", \"errors\": [], \"warnings\": [] }"
    )
    pdf.body("Internally executes vlib work + vlog -work work <source> for each source file. Compilation errors and warnings are captured and returned.")

    pdf.sub_title("5.9 POST /api/simulate/run")
    pdf.body("Run simulation using ModelSim/Questa (requires local installation).")
    pdf.code_block(
        "POST /api/simulate/run\n"
        "Body: { \"top_module\": \"my_top\", \"sim_time\": \"1us\",\n"
        '        "work_dir": "./sim_work" }\n'
        "Response: { \"success\": true, \"vcd_path\": \"...\", \"stdout\": \"...\" }"
    )
    pdf.body("Optionally accepts a sources[] list to compile first, then run. Internally generates a TCL script with vcd add commands and executes vsim -c -do. The simulation output VCD file path is returned.")

    # ─── 6. Running Tests ───
    pdf.section_title("6. Running Tests")
    pdf.body("The project includes 23 tests across 4 test files. Test framework: pytest + pytest-asyncio + httpx.")
    pdf.sub_title("Run All Tests")
    pdf.code_block(
        "cd backend\n"
        "python -m pytest tests/ -v"
    )
    pdf.sub_title("Run Specific Test File")
    pdf.code_block(
        "python -m pytest tests/test_ir.py -v\n"
        "python -m pytest tests/test_generators.py -v\n"
        "python -m pytest tests/test_vcd.py -v\n"
        "python -m pytest tests/test_api.py -v"
    )
    pdf.sub_title("Test Summary")
    pdf.body("test_ir.py (9 tests): Validates Port, Module, Connection, IR, ProjectFile model creation, serialization, and deserialization.")
    pdf.body("test_generators.py (5 tests): Validates TopGenerator output (port inference, wire generation, instantiation) and TestbenchGenerator output (clock config, DUT, dump statements).")
    pdf.body("test_vcd.py (4 tests): Validates VCD parser against sample VCD content (single-bit signals, multi-bit buses, empty files).")
    pdf.body("test_api.py (5 tests): End-to-end HTTP tests against all API endpoints using httpx AsyncClient with ASGI transport (no server needed).")

    # ─── 7. Demo ───
    pdf.section_title("7. Demo: Quick Workflow")
    pdf.body("A complete end-to-end demo using the sample file demo_input.json.")
    pdf.sub_title("Step 1 - Start the server")
    pdf.code_block("cd backend\npython main.py")
    pdf.sub_title("Step 2 - Generate Top module")
    pdf.code_block(
        "curl -X POST http://localhost:8000/api/generate/top \\\n"
        "  -H \"Content-Type: application/json\" \\\n"
        '  -d @demo_input.json'
    )
    pdf.body(
        "This sends an IR with two modules (clk_divider, led_controller) and one connection. "
        "The backend returns a complete Verilog top module with inferred ports (clk_in, rst_n as inputs; "
        "led_out as output), a wire declaration for clk_divided, and two module instantiations."
    )
    pdf.sub_title("Step 3 - Generate Testbench")
    pdf.code_block(
        "curl -X POST http://localhost:8000/api/generate/testbench \\\n"
        "  -H \"Content-Type: application/json\" \\\n"
        "  -d '{\"ir\":{\"version\":\"0.1.0\",\"modules\":[],\"connections\":[],\"wrapped_modules\":[],\"top_module_name\":\"blinky\"},\"simulation\":{\"clock_period_ns\":10.0,\"reset_cycles\":5,\"sim_time_us\":100.0}}'"
    )
    pdf.sub_title("Step 4 - Browse API docs")
    pdf.body("Open http://localhost:8000/docs in a browser for interactive Swagger UI with all endpoints.")

    # ─── 8. Appendix ───
    pdf.add_page()
    pdf.section_title("8. Appendix: Dependencies")
    pdf.code_block(
        "fastapi       >= 0.111.0   Web framework\n"
        "uvicorn       >= 0.29.0    ASGI server\n"
        "pydantic      >= 2.7.0     Data validation\n"
        "jinja2        >= 3.1.4     Template engine\n"
        "vcdvcd        >= 2.0.0     VCD library (auxiliary)\n"
        "pytest        >= 8.2.0     Test framework\n"
        "pytest-asyncio>= 0.23.7    Async test support\n"
        "httpx         >= 0.27.0    HTTP test client"
    )
    pdf.ln(4)
    pdf.body(
        "For simulation features, ModelSim/Questa must be installed separately and "
        "available on the system PATH. The simulator module uses subprocess calls to "
        "vlib, vlog, vcom, and vsim executables."
    )
    pdf.ln(4)
    pdf.body(
        "The VCD parser (app/utils/vcd_parser.py) is a self-contained implementation "
        "that does not depend on the vcdvcd library. It handles $timescale, $var, "
        "$dumpvars, #time markers, and single/multi-bit value changes."
    )

    # ─── Save ───
    output_path = os.path.join(os.path.dirname(__file__), "FPGA_Backend_Manual.pdf")
    pdf.output(output_path)
    print(f"Manual saved to: {output_path}")
    print(f"Pages: {pdf.page_no()}")
    return output_path


if __name__ == "__main__":
    build_manual()
