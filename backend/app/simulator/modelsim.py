"""
ModelSim / Questa 仿真器实现

通过 subprocess 调用 vsim / vlib / vlog / vcom 命令行工具。
通过 TCL 脚本批处理模式执行仿真，并导出 VCD 波形。
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

from app.simulator.base import Simulator, SimulationResult


class ModelSimSimulator(Simulator):
    """ModelSim / Questa 仿真器

    Args:
        executable_path: ModelSim 安装路径 (如 C:/modeltech64_10.7/win64)
        gui_mode: True 打开 GUI，False 为命令行批处理模式
    """

    def __init__(self, executable_path: str = "", gui_mode: bool = False):
        self._bin_dir = Path(executable_path) if executable_path else Path("")
        self._gui = gui_mode

    def _exe(self, name: str) -> str:
        """获取可执行文件完整路径"""
        if self._bin_dir and self._bin_dir.exists():
            return str(self._bin_dir / name)
        return name  # 依赖 PATH

    async def compile(self, sources: list[str], work_dir: str) -> SimulationResult:
        """编译源文件：vlib work + vlog source.v"""
        errors: list[str] = []
        warnings: list[str] = []

        work_path = Path(work_dir)
        work_path.mkdir(parents=True, exist_ok=True)

        # 1. 创建 work 库
        proc = await asyncio.create_subprocess_exec(
            self._exe("vlib"),
            "work",
            cwd=str(work_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        stdout_str = stdout.decode(errors="replace")
        stderr_str = stderr.decode(errors="replace")

        if proc.returncode != 0:
            return SimulationResult(
                success=False,
                stdout=stdout_str,
                stderr=stderr_str,
                errors=[stderr_str],
            )

        # 2. 编译源文件
        for src in sources:
            proc = await asyncio.create_subprocess_exec(
                self._exe("vlog"),
                "-work", "work",
                src,
                cwd=str(work_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            stdout_str += stdout.decode(errors="replace")
            stderr_str += stderr.decode(errors="replace")

            if proc.returncode != 0:
                errors.append(f"Compilation failed for {src}: {stderr.decode(errors='replace')}")

            # 检查 warning
            for line in stderr.decode(errors="replace").splitlines():
                if "warning" in line.lower() or "** warning" in line.lower():
                    warnings.append(line.strip())

        return SimulationResult(
            success=len(errors) == 0,
            stdout=stdout_str,
            stderr=stderr_str,
            errors=errors,
            warnings=warnings,
        )

    async def run(
        self,
        top_module: str,
        sim_time: str = "1us",
        work_dir: str = ".",
    ) -> SimulationResult:
        """运行仿真：vsim -c -do tcl_script"""
        work_path = Path(work_dir)
        vcd_path = str(work_path / f"{top_module}.vcd")

        # 生成 TCL 脚本
        tcl_script = self._build_tcl_script(top_module, sim_time, vcd_path)
        tcl_file = work_path / f"sim_{top_module}.do"

        with open(tcl_file, "w", encoding="utf-8") as f:
            f.write(tcl_script)

        # 执行 vsim
        args = [
            self._exe("vsim"),
            "-c",  # 命令行模式
            "-do", f"do {tcl_file.name}; quit",
            f"work.{top_module}",
        ]

        if self._gui:
            args.remove("-c")

        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=str(work_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.subprocess.communicate()
        stdout_str = stdout.decode(errors="replace")
        stderr_str = stderr.decode(errors="replace")

        # 检查 VCD 是否生成
        vcd_exists = os.path.exists(vcd_path)

        return SimulationResult(
            success=proc.returncode == 0 and vcd_exists,
            stdout=stdout_str,
            stderr=stderr_str,
            vcd_path=vcd_path if vcd_exists else "",
        )

    async def compile_and_run(
        self,
        sources: list[str],
        top_module: str,
        sim_time: str = "1us",
        work_dir: str = ".",
    ) -> SimulationResult:
        """编译并运行"""
        compile_result = await self.compile(sources, work_dir)
        if not compile_result.success:
            return compile_result

        run_result = await self.run(top_module, sim_time, work_dir)
        run_result.warnings = compile_result.warnings + run_result.warnings
        return run_result

    # ─── private ─────────────────────────────────────────────────────────────

    def _build_tcl_script(self, top_module: str, sim_time: str, vcd_path: str) -> str:
        """构建 ModelSim TCL 批处理脚本"""
        vcd_path_escaped = vcd_path.replace("\\", "/")
        return f"""
# Auto-generated simulation script
vcd file {vcd_path_escaped}
vcd add -r /*

# Run simulation
run {sim_time}

# Cleanup
vcd flush
quit
"""
