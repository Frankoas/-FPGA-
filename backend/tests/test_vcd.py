"""测试 VCD 解析器"""

import pytest
import tempfile
import os
from app.utils.vcd_parser import VCDParser, WaveformData, SignalTrace


class TestVCDParser:
    def setup_method(self):
        self.parser = VCDParser()

    def _write_vcd(self, content: str) -> str:
        """写入临时 VCD 文件并返回路径"""
        fd, path = tempfile.mkstemp(suffix=".vcd")
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def test_parse_simple_vcd(self):
        vcd_content = """$timescale 1ns $end
$var wire 1 ! clk $end
$var wire 4 # data $end
$dumpvars
0!
b0000 #
$end
#10
1!
#20
0!
b1010 #
#30
1!
"""
        path = self._write_vcd(vcd_content)
        try:
            waveform = self.parser.parse(path)

            assert len(waveform.signals) == 2

            clk = [s for s in waveform.signals if s.name == "clk"][0]
            assert clk.width == 1
            assert len(clk.changes) == 4  # initial + 3 transitions

            data = [s for s in waveform.signals if s.name == "data"][0]
            assert data.width == 4
            # values: b0000 initial, b1010 at #20
            assert data.changes[1].value == "1010"
        finally:
            os.unlink(path)

    def test_empty_vcd(self):
        vcd_content = "$timescale 1ns $end"
        path = self._write_vcd(vcd_content)
        try:
            waveform = self.parser.parse(path)
            assert waveform.signals == []
            assert waveform.total_time_ns == 0
        finally:
            os.unlink(path)


class TestWaveformData:
    def test_to_dict(self):
        s = SignalTrace(name="test", width=8)
        from app.utils.vcd_parser import SignalChange
        s.changes.append(SignalChange(time_ns=0, value="00000000"))
        s.changes.append(SignalChange(time_ns=10, value="11111111"))
        wd = WaveformData(signals=[s], total_time_ns=10)

        d = wd.to_dict()
        assert d["signals"][0]["name"] == "test"
        assert len(d["signals"][0]["changes"]) == 2
        assert d["total_time_ns"] == 10
