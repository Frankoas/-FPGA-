"""
仿真器抽象基类

定义统一的仿真接口，支持 ModelSim / Questa / Icarus 等多种后端。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SimulationResult:
    """仿真执行结果"""
    success: bool
    stdout: str = ""
    stderr: str = ""
    vcd_path: str = ""  # 生成的 VCD 文件路径
    elapsed_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class Simulator(ABC):
    """仿真器抽象基类

    所有仿真器后端必须实现以下接口：
    - compile: 编译源文件
    - run: 执行仿真
    - get_waves: 获取波形数据
    """

    @abstractmethod
    async def compile(self, sources: list[str], work_dir: str) -> SimulationResult:
        """编译 HDL 源文件"""
        ...

    @abstractmethod
    async def run(
        self,
        top_module: str,
        sim_time: str = "1us",
        work_dir: str = ".",
    ) -> SimulationResult:
        """运行仿真并生成 VCD"""
        ...

    @abstractmethod
    async def compile_and_run(
        self,
        sources: list[str],
        top_module: str,
        sim_time: str = "1us",
        work_dir: str = ".",
    ) -> SimulationResult:
        """编译并运行仿真（便捷方法）"""
        ...
