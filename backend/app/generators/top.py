"""
Top 模块代码生成器

根据 IR 生成完整的 Verilog 顶层模块文件，包括：
- 自动推断顶层端口
- 内部 wire 声明
- 子模块例化
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from app.models.ir import IR, Port, PortDirection, Module, Connection, WrappedModule


TEMPLATES_DIR = Path(__file__).parent / "templates"


class TopGenerator:
    """顶层模块 Verilog 生成器"""

    def __init__(self):
        self._env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            trim_blocks=False,
            lstrip_blocks=False,
        )
        self._template = self._env.get_template("top.v.j2")

    def generate(self, ir: IR) -> str:
        """从 IR 生成完整的 Top 模块 Verilog 代码"""
        all_modules = self._flatten_modules(ir)
        all_connections = self._flatten_connections(ir)

        top_ports = self._infer_top_ports(all_modules, all_connections)
        wires = self._build_wires(all_modules, all_connections)
        instantiations = self._build_instantiations(all_modules, all_connections)

        ctx = {
            "top_name": ir.top_module_name,
            "top_ports": top_ports,
            "parameters": [],  # 后续可从 board config 注入
            "wires": wires,
            "instantiations": instantiations,
        }
        return self._template.render(**ctx)

    # ─── helpers ─────────────────────────────────────────────────────────────

    @staticmethod
    def _flatten_modules(ir: IR) -> list[Module]:
        modules = list(ir.modules)
        for wm in ir.wrapped_modules:
            modules.extend(wm.internal_modules)
            for nested in wm.internal_wrapped:
                modules.extend(TopGenerator._flatten_wrapped(nested))
        return modules

    @staticmethod
    def _flatten_wrapped(wm: WrappedModule) -> list[Module]:
        modules = list(wm.internal_modules)
        for nested in wm.internal_wrapped:
            modules.extend(TopGenerator._flatten_wrapped(nested))
        return modules

    @staticmethod
    def _flatten_connections(ir: IR) -> list[Connection]:
        connections = list(ir.connections)
        for wm in ir.wrapped_modules:
            connections.extend(wm.internal_connections)
        return connections

    @staticmethod
    def _infer_top_ports(
        modules: list[Module], connections: list[Connection]
    ) -> list[Port]:
        """推断顶层端口：无外部连接的端口暴露为顶层 I/O，按名称去重"""
        connected_ports: set[tuple[str, str]] = set()
        for c in connections:
            connected_ports.add((c.src_module, c.src_port))
            connected_ports.add((c.dst_module, c.dst_port))

        # 收集未连接端口，按名称去重（取最大位宽）
        seen: dict[str, Port] = {}
        for m in modules:
            for p in m.ports:
                if (m.id, p.name) not in connected_ports:
                    if p.name in seen:
                        seen[p.name].width = max(seen[p.name].width, p.width)
                    else:
                        seen[p.name] = p.model_copy(deep=True)

        top_ports = list(seen.values())
        top_ports.sort(key=lambda p: (0 if p.direction == PortDirection.INPUT else 1, p.name))
        return top_ports

    @staticmethod
    def _build_wires(
        modules: list[Module], connections: list[Connection]
    ) -> list[dict]:
        """从连线生成 wire 声明列表"""
        # 构建模块端口位宽查找表
        port_widths: dict[tuple[str, str], tuple[int, bool]] = {}
        for m in modules:
            for p in m.ports:
                port_widths[(m.id, p.name)] = (p.width, p.signed)

        wires: dict[str, dict] = {}
        auto_idx = 0
        for c in connections:
            if c.wire_name:
                name = c.wire_name
            else:
                name = f"w_{c.src_port}_{c.dst_port}_{auto_idx}"
                auto_idx += 1

            # 取两端中较大位宽
            w_src = port_widths.get((c.src_module, c.src_port), (1, False))
            w_dst = port_widths.get((c.dst_module, c.dst_port), (1, False))
            width = max(w_src[0], w_dst[0])

            if name not in wires:
                wires[name] = {"name": name, "width": width, "signed": False}
            else:
                wires[name]["width"] = max(wires[name]["width"], width)

        return list(wires.values())

    @staticmethod
    def _build_instantiations(
        modules: list[Module], connections: list[Connection]
    ) -> list[dict]:
        """构建子模块例化信息"""
        # 按模块名分组连接
        conn_by_module: dict[str, list[dict]] = {}
        for c in connections:
            wire_name = c.wire_name or f"w_{c.src_port}_{c.dst_port}"
            conn_by_module.setdefault(c.src_module, []).append({
                "port_name": c.src_port,
                "wire_name": wire_name,
            })
            conn_by_module.setdefault(c.dst_module, []).append({
                "port_name": c.dst_port,
                "wire_name": wire_name,
            })

        insts = []
        for i, m in enumerate(modules):
            inst_name = m.instance_name or f"u_{m.name}_{i}"
            conns = conn_by_module.get(m.id, [])

            # 补充未连接的端口（悬空）
            connected_port_names = {x["port_name"] for x in conns}
            for p in m.ports:
                if p.name not in connected_port_names:
                    conns.append({"port_name": p.name, "wire_name": ""})

            insts.append({
                "module_name": m.name,
                "inst_name": inst_name,
                "params": [],  # 后续可从 config 注入
                "connections": conns,
            })

        return insts
