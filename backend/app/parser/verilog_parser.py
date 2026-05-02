"""
简易 Verilog 解析器

提取模块声明（端口、参数）和内部例化关系。
用于"导入已有工程"功能（第四阶段）。

注意：生产环境应使用 pyverilog 或 sv-parser 做完整 AST 解析，
此模块仅作 demo 用途，处理常见可综合代码风格。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from app.models.ir import Port, PortDirection, Module, Connection


@dataclass
class ParsedModule:
    """从 Verilog 文件解析出的模块信息"""
    name: str
    ports: list[Port] = field(default_factory=list)
    parameters: list[dict] = field(default_factory=list)
    instantiations: list[dict] = field(default_factory=list)  # [{module, inst_name, connections}]
    raw_text: str = ""


class VerilogParser:
    """Verilog 模块解析器 (regex-based, demo quality)"""

    # 匹配 module 声明: module foo #(params) (ports);
    _MODULE_RE = re.compile(
        r"module\s+(?P<name>\w+)\s*"
        r"(?:#\s*\((?P<params>[\s\S]*?)\)\s*)?"
        r"\(\s*(?P<ports>[\s\S]*?)\s*\)\s*;",
        re.IGNORECASE,
    )

    # 匹配端口: input/output/inout [signed] [W-1:0] name
    _PORT_RE = re.compile(
        r"(?P<direction>input|output|inout)\s+"
        r"(?:(?P<signed>signed)\s+)?"
        r"(?:reg\s+|wire\s+)?"
        r"(?:\[(?P<msb>\d+)\s*:\s*(?P<lsb>\d+)\]\s+)?"
        r"(?P<name>\w+)",
        re.IGNORECASE,
    )

    # 匹配例化: module_name #(params) inst_name (.port(wire), ...);
    _INST_RE = re.compile(
        r"(?P<module>\w+)\s*"
        r"(?:#\s*\([\s\S]*?\)\s*)?"
        r"(?P<inst>\w+)\s*"
        r"\(\s*(?P<conns>[\s\S]*?)\s*\)\s*;",
    )

    # 匹配端口连接: .port_name(wire_name)
    _CONN_RE = re.compile(r"\.(?P<port>\w+)\s*\(\s*(?P<wire>\w*)\s*\)")

    def parse_file(self, filepath: str) -> list[ParsedModule]:
        """解析单个 Verilog 文件，返回所有模块"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        if path.suffix.lower() == ".vhd" or path.suffix.lower() == ".vhdl":
            return self._parse_vhdl(path)
        return self._parse_verilog(path)

    def parse_directory(self, dirpath: str) -> list[ParsedModule]:
        """解析目录下所有 Verilog/VHDL 文件"""
        modules: list[ParsedModule] = []
        for pattern in ("**/*.v", "**/*.sv", "**/*.vhd", "**/*.vhdl"):
            for p in Path(dirpath).glob(pattern):
                try:
                    modules.extend(self.parse_file(str(p)))
                except Exception:
                    continue
        return modules

    def to_ir(self, modules: list[ParsedModule]) -> "tuple[list[Module], list[Connection]]":
        """将解析结果转换为 IR 的 Module 和 Connection"""
        ir_modules: list[Module] = []
        ir_connections: list[Connection] = []

        for pm in modules:
            m = Module(
                name=pm.name,
                type="base",
                ports=[Port(
                    name=p.name,
                    direction=p.direction,
                    width=p.width,
                    signed=p.signed,
                ) for p in pm.ports],
            )
            ir_modules.append(m)

            for inst in pm.instantiations:
                for conn in inst.get("connections", []):
                    c = Connection(
                        src_module=m.id,
                        src_port=conn.get("port", ""),
                        dst_module="",  # 需要后续匹配
                        dst_port=conn.get("port", ""),
                        wire_name=conn.get("wire", ""),
                    )
                    ir_connections.append(c)

        return ir_modules, ir_connections

    # ─── private ─────────────────────────────────────────────────────────────

    def _parse_verilog(self, filepath: Path) -> list[ParsedModule]:
        text = filepath.read_text(encoding="utf-8", errors="replace")
        # 去除注释
        text = re.sub(r"//.*", "", text)
        text = re.sub(r"/\*[\s\S]*?\*/", "", text)

        modules: list[ParsedModule] = []

        for m_match in self._MODULE_RE.finditer(text):
            pm = ParsedModule(name=m_match.group("name"), raw_text=m_match.group(0))
            ports_str = m_match.group("ports") or ""

            for p_match in self._PORT_RE.finditer(ports_str):
                direction = PortDirection(p_match.group("direction").lower())
                signed = p_match.group("signed") is not None
                msb = int(p_match.group("msb")) if p_match.group("msb") else 0
                lsb = int(p_match.group("lsb")) if p_match.group("lsb") else 0
                width = abs(msb - lsb) + 1
                pm.ports.append(Port(
                    name=p_match.group("name"),
                    direction=direction,
                    width=width,
                    signed=signed,
                ))

            # 查找该模块内部的例化
            self._extract_instantiations(text, m_match.end(), pm)

            modules.append(pm)

        return modules

    def _extract_instantiations(self, text: str, start: int, pm: ParsedModule) -> None:
        """在 module 体内查找子模块例化"""
        # 找 endmodule
        end_match = re.search(r"endmodule", text[start:], re.IGNORECASE)
        if not end_match:
            return
        body = text[start:start + end_match.start()]

        for inst_match in self._INST_RE.finditer(body):
            inst_info = {
                "module": inst_match.group("module"),
                "inst_name": inst_match.group("inst"),
                "connections": [],
            }
            conns_str = inst_match.group("conns") or ""
            for c_match in self._CONN_RE.finditer(conns_str):
                inst_info["connections"].append({
                    "port": c_match.group("port"),
                    "wire": c_match.group("wire") or f"w_{c_match.group('port')}",
                })
            pm.instantiations.append(inst_info)

    def _parse_vhdl(self, filepath: Path) -> list[ParsedModule]:
        """VHDL 解析占位 — 生产环境应使用 pyVHDLParser"""
        # Demo: 返回空，提示用户使用 Verilog
        return []
