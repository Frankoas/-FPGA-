"""测试 IR 数据模型"""

import pytest
from app.models.ir import (
    Port, PortDirection, Module, Connection, IR, ProjectFile,
    SimulationConfig, WrappedModule,
)


class TestPort:
    def test_create_simple_port(self):
        p = Port(name="clk", direction=PortDirection.INPUT)
        assert p.name == "clk"
        assert p.direction == PortDirection.INPUT
        assert p.width == 1
        assert not p.signed

    def test_create_bus_port(self):
        p = Port(name="data", direction=PortDirection.OUTPUT, width=8, signed=True)
        assert p.width == 8
        assert p.signed

    def test_auto_id(self):
        p1 = Port(name="a", direction=PortDirection.INPUT)
        p2 = Port(name="b", direction=PortDirection.OUTPUT)
        assert p1.id != p2.id
        assert len(p1.id) == 12


class TestModule:
    def test_create_module(self):
        m = Module(name="counter", type="base")
        assert m.name == "counter"
        assert m.type == "base"
        assert m.ports == []

    def test_module_with_ports(self):
        m = Module(
            name="counter",
            ports=[
                Port(name="clk", direction=PortDirection.INPUT),
                Port(name="q", direction=PortDirection.OUTPUT, width=4),
            ],
        )
        assert len(m.ports) == 2


class TestConnection:
    def test_connection(self):
        c = Connection(
            src_module="abc123",
            src_port="q",
            dst_module="def456",
            dst_port="data_in",
            wire_name="counter_q",
        )
        assert c.wire_name == "counter_q"


class TestIR:
    def test_empty_ir(self):
        ir = IR()
        assert ir.version == "0.1.0"
        assert ir.top_module_name == "top"
        assert ir.modules == []
        assert ir.connections == []

    def test_ir_with_data(self):
        m1 = Module(name="clk_div", id="mod_001",
                    ports=[Port(name="clk_in", direction=PortDirection.INPUT),
                           Port(name="clk_out", direction=PortDirection.OUTPUT)])
        m2 = Module(name="led_drv", id="mod_002",
                    ports=[Port(name="clk", direction=PortDirection.INPUT),
                           Port(name="led", direction=PortDirection.OUTPUT)])
        c = Connection(src_module="mod_001", src_port="clk_out",
                       dst_module="mod_002", dst_port="clk",
                       wire_name="clk_divided")

        ir = IR(modules=[m1, m2], connections=[c], top_module_name="blinky")
        assert len(ir.modules) == 2
        assert len(ir.connections) == 1
        assert ir.top_module_name == "blinky"


class TestProjectFile:
    def test_default_project(self):
        p = ProjectFile(name="test_project")
        assert p.name == "test_project"
        assert p.version == "0.1.0"

    def test_serialize_deserialize(self):
        p = ProjectFile(name="test", ir=IR(top_module_name="my_top"))
        data = p.model_dump(mode="json")
        restored = ProjectFile.model_validate(data)
        assert restored.name == "test"
        assert restored.ir.top_module_name == "my_top"
