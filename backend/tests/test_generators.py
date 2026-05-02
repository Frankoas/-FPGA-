"""测试代码生成器"""

import pytest
from app.models.ir import (
    IR, Module, Port, PortDirection, Connection, SimulationConfig,
)
from app.generators.top import TopGenerator
from app.generators.testbench import TestbenchGenerator


class TestTopGenerator:
    def setup_method(self):
        self.gen = TopGenerator()

    def test_generate_simple_top(self):
        """两个模块直连 → 生成 Top"""
        m1 = Module(id="m1", name="clk_div",
                    ports=[Port(name="clk_in", direction=PortDirection.INPUT),
                           Port(name="clk_out", direction=PortDirection.OUTPUT)])
        m2 = Module(id="m2", name="led_drv",
                    ports=[Port(name="clk", direction=PortDirection.INPUT),
                           Port(name="led", direction=PortDirection.OUTPUT)])
        c = Connection(src_module="m1", src_port="clk_out",
                       dst_module="m2", dst_port="clk",
                       wire_name="clk_divided")

        ir = IR(modules=[m1, m2], connections=[c], top_module_name="blinky")
        verilog = self.gen.generate(ir)

        assert "module blinky" in verilog
        assert "endmodule" in verilog
        assert "wire" in verilog  # clk_divided should be declared
        assert "clk_div" in verilog
        assert "led_drv" in verilog
        assert "u_clk_div_0" in verilog or "u_led_drv" in verilog

    def test_infer_top_ports(self):
        """未连接的端口暴露为顶层 port"""
        m1 = Module(id="m1", name="buf",
                    ports=[Port(name="in", direction=PortDirection.INPUT),
                           Port(name="out", direction=PortDirection.OUTPUT)])
        # 没有连线 → 两个端口都暴露
        ir = IR(modules=[m1], top_module_name="wrapper")
        verilog = self.gen.generate(ir)

        assert "input" in verilog
        assert "output" in verilog
        assert "in" in verilog
        assert "out" in verilog

    def test_multiple_connections(self):
        """多模块多连线"""
        m1 = Module(id="m1", name="src",
                    ports=[Port(name="a", direction=PortDirection.OUTPUT),
                           Port(name="b", direction=PortDirection.OUTPUT)])
        m2 = Module(id="m2", name="dst",
                    ports=[Port(name="a", direction=PortDirection.INPUT),
                           Port(name="b", direction=PortDirection.INPUT)])
        c1 = Connection(src_module="m1", src_port="a", dst_module="m2", dst_port="a", wire_name="sig_a")
        c2 = Connection(src_module="m1", src_port="b", dst_module="m2", dst_port="b", wire_name="sig_b")

        ir = IR(modules=[m1, m2], connections=[c1, c2])
        verilog = self.gen.generate(ir)

        assert "sig_a" in verilog
        assert "sig_b" in verilog


class TestTestbenchGenerator:
    def setup_method(self):
        self.gen = TestbenchGenerator()

    def test_generate_tb(self):
        m1 = Module(id="m1", name="counter",
                    ports=[Port(name="clk", direction=PortDirection.INPUT),
                           Port(name="rst_n", direction=PortDirection.INPUT),
                           Port(name="q", direction=PortDirection.OUTPUT, width=4)])
        ir = IR(modules=[m1], top_module_name="top")
        sim = SimulationConfig(
            clock_period_ns=10.0,
            reset_cycles=5,
            sim_time_us=50.0,
            monitored_signals=["m1.clk", "m1.q"],
        )

        tb = self.gen.generate(ir, sim)

        assert "tb_top" in tb
        assert "clk" in tb
        assert "rst_n" in tb
        assert "$dumpfile" in tb
        assert "$finish" in tb
        assert "u_dut" in tb

    def test_tb_includes_clock_period(self):
        ir = IR(top_module_name="fast_clk")
        sim = SimulationConfig(clock_period_ns=5.0)
        tb = self.gen.generate(ir, sim)
        assert "5" in tb  # clock period
