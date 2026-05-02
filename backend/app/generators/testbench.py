"""
Testbench 代码生成器

根据 IR + SimulationConfig 生成仿真 Testbench 框架。
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from app.models.ir import IR, PortDirection, SimulationConfig


TEMPLATES_DIR = Path(__file__).parent / "templates"


class TestbenchGenerator:
    """Testbench 生成器"""

    def __init__(self):
        self._env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._template = self._env.get_template("testbench.v.j2")

    def generate(self, ir: IR, sim_cfg: SimulationConfig) -> str:
        """生成 Testbench Verilog 代码"""
        # 构建模块端口查找表
        port_map: dict[str, tuple] = {}  # (module_id, port_name) -> (direction, width, signed)
        all_modules = list(ir.modules)
        for wm in ir.wrapped_modules:
            all_modules.extend(wm.internal_modules)

        for m in all_modules:
            for p in m.ports:
                port_map[(m.id, p.name)] = (p.direction, p.width, p.signed)

        # 从 monitored_signals 提取信号信息
        stimuli: list[dict] = []
        monitored: list[dict] = []

        for sig_ref in sim_cfg.monitored_signals:
            # sig_ref 格式: "module_id.port_name"
            parts = sig_ref.split(".")
            if len(parts) == 2:
                mid, pname = parts
                info = port_map.get((mid, pname))
                if info:
                    direction, width, signed = info
                    entry = {"name": pname, "width": width, "signed": signed}
                    if direction == PortDirection.INPUT:
                        stimuli.append(entry)
                    else:
                        monitored.append(entry)

        # 如果未指定信号，暴露所有端口
        if not stimuli and not monitored:
            for m in all_modules:
                for p in m.ports:
                    entry = {"name": f"{m.name}_{p.name}", "width": p.width, "signed": p.signed}
                    if p.direction == PortDirection.INPUT:
                        stimuli.append(entry)
                    else:
                        monitored.append(entry)

        sim_time_ns = int(sim_cfg.sim_time_us * 1000)

        ctx = {
            "tb_name": f"tb_{ir.top_module_name}",
            "dut_name": ir.top_module_name,
            "clock_period_ns": sim_cfg.clock_period_ns,
            "reset_cycles": sim_cfg.reset_cycles,
            "sim_time_ns": sim_time_ns,
            "dump_filename": f"{ir.top_module_name}.vcd",
            "stimuli_signals": stimuli,
            "monitored_signals": monitored,
        }
        return self._template.render(**ctx)
