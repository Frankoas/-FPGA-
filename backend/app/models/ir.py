"""
FPGA 可视化编程工具 — 中间表示 (IR) 数据模型

IR 是前端图形界面与后端代码生成之间的唯一交换格式。
所有模型使用 Pydantic v2 定义，支持 JSON Schema 自动生成与校验。
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


def _uid() -> str:
    return uuid.uuid4().hex[:12]


# ─── 端口 ────────────────────────────────────────────────────────────────────

class PortDirection(str, Enum):
    INPUT = "input"
    OUTPUT = "output"
    INOUT = "inout"


class Port(BaseModel):
    """模块端口定义"""
    id: str = Field(default_factory=_uid)
    name: str = Field(..., description="端口名称，如 clk, rst_n, data_in")
    direction: PortDirection
    width: int = Field(default=1, ge=1, description="位宽")
    signed: bool = Field(default=False, description="有无符号")
    array_size: Optional[int] = Field(default=None, description="数组维度，如 [7:0] 中为 8")
    description: str = Field(default="", description="端口注释/说明")


# ─── 模块 ────────────────────────────────────────────────────────────────────

class Module(BaseModel):
    """画布上的基础模块节点"""
    id: str = Field(default_factory=_uid)
    name: str = Field(..., description="模块名，对应 Verilog module 名")
    instance_name: Optional[str] = Field(default=None, description="用户自定义例化名")
    type: str = Field(default="base", description="模块类型: base / wrapped / board_ip")
    ports: list[Port] = Field(default_factory=list)
    position: tuple[float, float] = Field(default=(0, 0), description="画布坐标 (x, y)")
    config: dict = Field(default_factory=dict, description="模块参数配置，如 PLL 倍频系数等")


# ─── 连线 ────────────────────────────────────────────────────────────────────

class Connection(BaseModel):
    """两端口之间的连线"""
    id: str = Field(default_factory=_uid)
    src_module: str = Field(..., description="源模块 ID")
    src_port: str = Field(..., description="源端口名")
    dst_module: str = Field(..., description="目标模块 ID")
    dst_port: str = Field(..., description="目标端口名")
    wire_name: Optional[str] = Field(default=None, description="用户标注的 wire 名，为空则自动生成")


# ─── 封装模块 ────────────────────────────────────────────────────────────────

class WrappedModule(BaseModel):
    """自定义封装模块：将一组内部模块打包为可复用节点"""
    name: str = Field(..., description="封装后的模块名")
    exposed_ports: list[Port] = Field(default_factory=list, description="暴露到外部的端口")
    internal_modules: list[Module] = Field(default_factory=list)
    internal_connections: list[Connection] = Field(default_factory=list)
    internal_wrapped: list["WrappedModule"] = Field(default_factory=list)


# ─── 顶层 IR ─────────────────────────────────────────────────────────────────

class IR(BaseModel):
    """中间表示：画布完整状态的抽象"""
    version: str = Field(default="0.1.0", description="IR 版本号，用于前后兼容")
    modules: list[Module] = Field(default_factory=list)
    connections: list[Connection] = Field(default_factory=list)
    wrapped_modules: list[WrappedModule] = Field(default_factory=list)
    top_module_name: str = Field(default="top", description="顶层模块名")


# ─── 板卡配置 ────────────────────────────────────────────────────────────────

class BoardConfig(BaseModel):
    """板卡 IP 配置"""
    board_name: str = Field(..., description="板卡名称，如 xilinx_zynq7000")
    fpga_part: str = Field(default="", description="FPGA 型号")
    clock_pins: dict[str, str] = Field(default_factory=dict, description="时钟引脚映射")
    gpio_map: dict[str, str] = Field(default_factory=dict, description="GPIO 映射")
    constraints: str = Field(default="", description="约束文件内容 (.xdc / .qsf)")


# ─── 仿真配置 ────────────────────────────────────────────────────────────────

class SimulationConfig(BaseModel):
    """仿真配置"""
    simulator: str = Field(default="modelsim", description="仿真器: modelsim / questa / icarus")
    clock_period_ns: float = Field(default=10.0, description="时钟周期 (ns)")
    reset_cycles: int = Field(default=10, description="复位持续周期数")
    sim_time_us: float = Field(default=100.0, description="仿真总时长 (us)")
    monitored_signals: list[str] = Field(default_factory=list, description="待抓取信号列表")


# ─── 工程文件 ────────────────────────────────────────────────────────────────

class ProjectFile(BaseModel):
    """完整工程文件 (.fpga.json)"""
    version: str = Field(default="0.1.0")
    name: str = Field(default="untitled")
    ir: IR = Field(default_factory=IR)
    board: Optional[BoardConfig] = Field(default=None)
    simulation: Optional[SimulationConfig] = Field(default=None)
    canvas_state: dict = Field(default_factory=dict, description="视口位置、缩放等 UI 状态")
