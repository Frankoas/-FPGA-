"""
FastAPI 路由定义

所有 API 端点:
- /api/health                           健康检查
- POST /api/generate/top                生成 Top 模块
- POST /api/generate/testbench          生成 Testbench
- POST /api/parse/verilog               解析 Verilog 文件
- POST /api/parse/vcd                   解析 VCD 波形
- POST /api/project/save                保存工程
- POST /api/project/load                加载工程
- POST /api/simulate/compile            编译源文件
- POST /api/simulate/run                运行仿真
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from app.models.ir import IR, ProjectFile, SimulationConfig
from app.generators.top import TopGenerator
from app.generators.testbench import TestbenchGenerator
from app.parser.verilog_parser import VerilogParser
from app.utils.vcd_parser import VCDParser

router = APIRouter(prefix="/api")

# ─── 单例 ────────────────────────────────────────────────────────────────────
_top_gen = TopGenerator()
_tb_gen = TestbenchGenerator()
_vlog_parser = VerilogParser()
_vcd_parser = VCDParser()


# ─── Request / Response Models ───────────────────────────────────────────────

class GenerateTopRequest(BaseModel):
    ir: IR


class GenerateTestbenchRequest(BaseModel):
    ir: IR
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)


class ParseVerilogRequest(BaseModel):
    file_path: str


class ParseVCDRequest(BaseModel):
    file_path: str


class SaveProjectRequest(BaseModel):
    project: ProjectFile
    file_path: str


class LoadProjectRequest(BaseModel):
    file_path: str


class CompileRequest(BaseModel):
    sources: list[str]
    work_dir: str


class RunSimRequest(BaseModel):
    top_module: str
    sim_time: str = "1us"
    work_dir: str = "."
    sources: Optional[list[str]] = None


# ─── 健康检查 ────────────────────────────────────────────────────────────────

@router.get("/health")
async def health():
    return {"status": "ok", "service": "fpga-visual-tool-backend"}


# ─── 代码生成 ────────────────────────────────────────────────────────────────

@router.post("/generate/top")
async def generate_top(req: GenerateTopRequest):
    """根据 IR 生成顶层模块 Verilog 代码"""
    try:
        verilog = _top_gen.generate(req.ir)
        return {"success": True, "verilog": verilog}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate/testbench")
async def generate_testbench(req: GenerateTestbenchRequest):
    """根据 IR + 仿真配置生成 Testbench"""
    try:
        verilog = _tb_gen.generate(req.ir, req.simulation)
        return {"success": True, "verilog": verilog}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── 解析 ────────────────────────────────────────────────────────────────────

@router.post("/parse/verilog")
async def parse_verilog(req: ParseVerilogRequest):
    """解析 Verilog 文件，提取模块信息"""
    path = Path(req.file_path)
    try:
        if path.is_dir():
            modules = _vlog_parser.parse_directory(req.file_path)
        else:
            modules = _vlog_parser.parse_file(req.file_path)

        result = []
        for m in modules:
            result.append({
                "name": m.name,
                "ports": [
                    {"name": p.name, "direction": p.direction.value, "width": p.width}
                    for p in m.ports
                ],
                "instantiations": m.instantiations,
            })
        return {"success": True, "modules": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/parse/vcd")
async def parse_vcd(req: ParseVCDRequest):
    """解析 VCD 波形文件"""
    try:
        waveform = _vcd_parser.parse(req.file_path)
        return {"success": True, "waveform": waveform.to_dict()}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── 项目管理 ────────────────────────────────────────────────────────────────

@router.post("/project/save")
async def save_project(req: SaveProjectRequest):
    """保存工程为 .fpga.json 文件"""
    try:
        path = Path(req.file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = req.project.model_dump(mode="json")
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return {"success": True, "path": str(path.absolute())}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/project/load")
async def load_project(req: LoadProjectRequest):
    """加载 .fpga.json 工程文件"""
    try:
        path = Path(req.file_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {req.file_path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        project = ProjectFile.model_validate(data)
        return {"success": True, "project": project.model_dump(mode="json")}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── 仿真控制 ────────────────────────────────────────────────────────────────

@router.post("/simulate/compile")
async def simulate_compile(req: CompileRequest):
    """编译 HDL 源文件（需 ModelSim 环境）"""
    try:
        from app.simulator.modelsim import ModelSimSimulator
        sim = ModelSimSimulator()
        result = await sim.compile(req.sources, req.work_dir)
        return {
            "success": result.success,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-2000:],
            "errors": result.errors,
            "warnings": result.warnings,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate/run")
async def simulate_run(req: RunSimRequest):
    """运行仿真（需 ModelSim 环境）"""
    try:
        from app.simulator.modelsim import ModelSimSimulator
        sim = ModelSimSimulator()

        if req.sources:
            result = await sim.compile_and_run(
                req.sources, req.top_module, req.sim_time, req.work_dir
            )
        else:
            result = await sim.run(req.top_module, req.sim_time, req.work_dir)

        return {
            "success": result.success,
            "vcd_path": result.vcd_path,
            "stdout": result.stdout[-2000:],
            "errors": result.errors,
            "warnings": result.warnings,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
