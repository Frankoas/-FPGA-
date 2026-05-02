"""测试 FastAPI 端点"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_generate_top(client: AsyncClient):
    ir = {
        "version": "0.1.0",
        "modules": [
            {
                "id": "m1",
                "name": "counter",
                "type": "base",
                "ports": [
                    {"name": "clk", "direction": "input", "width": 1, "signed": False},
                    {"name": "q", "direction": "output", "width": 4, "signed": False},
                ],
                "position": [0, 0],
                "config": {},
            }
        ],
        "connections": [],
        "wrapped_modules": [],
        "top_module_name": "demo_top",
    }
    resp = await client.post("/api/generate/top", json={"ir": ir})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"]
    assert "module demo_top" in data["verilog"]
    assert "endmodule" in data["verilog"]


@pytest.mark.asyncio
async def test_generate_testbench(client: AsyncClient):
    ir = {
        "version": "0.1.0",
        "modules": [],
        "connections": [],
        "wrapped_modules": [],
        "top_module_name": "test_top",
    }
    sim = {
        "clock_period_ns": 20.0,
        "reset_cycles": 5,
        "sim_time_us": 100.0,
    }
    resp = await client.post("/api/generate/testbench", json={"ir": ir, "simulation": sim})
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"]
    assert "tb_test_top" in data["verilog"]


@pytest.mark.asyncio
async def test_save_and_load_project(client: AsyncClient, tmp_path):
    proj = {
        "version": "0.1.0",
        "name": "test_project",
        "ir": {
            "version": "0.1.0",
            "modules": [],
            "connections": [],
            "wrapped_modules": [],
            "top_module_name": "top",
        },
    }
    file_path = str(tmp_path / "test.fpga.json")

    # Save
    save_resp = await client.post("/api/project/save", json={"project": proj, "file_path": file_path})
    assert save_resp.status_code == 200
    assert save_resp.json()["success"]

    # Load
    load_resp = await client.post("/api/project/load", json={"file_path": file_path})
    assert load_resp.status_code == 200
    data = load_resp.json()
    assert data["success"]
    assert data["project"]["name"] == "test_project"


@pytest.mark.asyncio
async def test_parse_vcd_not_found(client: AsyncClient):
    resp = await client.post("/api/parse/vcd", json={"file_path": "/nonexistent.vcd"})
    assert resp.status_code == 404
