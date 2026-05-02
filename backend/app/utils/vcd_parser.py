"""
VCD (Value Change Dump) 波形解析器

将仿真生成的 .vcd 文件解析为结构化 JSON，供前端波形可视化。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SignalChange:
    """单个信号的一次值变化"""
    time_ns: int
    value: str  # 二进制字符串，如 "1", "0", "z", "x", "1010"


@dataclass
class SignalTrace:
    """单个信号的完整波形轨迹"""
    name: str
    width: int = 1
    signed: bool = False
    changes: list[SignalChange] = field(default_factory=list)

    @property
    def max_time(self) -> int:
        if not self.changes:
            return 0
        return self.changes[-1].time_ns


@dataclass
class WaveformData:
    """完整波形数据"""
    signals: list[SignalTrace] = field(default_factory=list)
    total_time_ns: int = 0
    timescale: str = "1ns"

    def to_dict(self) -> dict:
        return {
            "signals": [
                {
                    "name": s.name,
                    "width": s.width,
                    "signed": s.signed,
                    "changes": [
                        {"time_ns": c.time_ns, "value": c.value} for c in s.changes
                    ],
                }
                for s in self.signals
            ],
            "total_time_ns": self.total_time_ns,
            "timescale": self.timescale,
        }


class VCDParser:
    """VCD 文件解析器

    支持基本 VCD 语法：
    - $var / $end 信号定义
    - $dumpvars 初始值
    - #time 时间标记 + 值变化
    """

    def __init__(self):
        self._signals: dict[str, SignalTrace] = {}
        self._id_to_name: dict[str, str] = {}
        self._current_time: int = 0
        self._timescale: str = "1ns"

    def parse(self, filepath: str) -> WaveformData:
        """解析 VCD 文件并返回波形数据"""
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        lines = content.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            if line.startswith("$timescale"):
                i = self._parse_timescale(lines, i)
            elif line.startswith("$var"):
                i = self._parse_var(lines, i)
            elif line.startswith("$dumpvars"):
                i = self._parse_dumpvars(lines, i)
            elif line.startswith("#"):
                self._current_time = int(line[1:])
                i += 1
            elif line.startswith("$end"):
                i += 1
            elif line.startswith("$comment") or line.startswith("$date") or line.startswith("$version"):
                i = self._skip_to_end(lines, i)
            else:
                self._parse_value_change(line)
                i += 1

        return self._build_waveform()

    # ─── internal parsers ────────────────────────────────────────────────────

    def _parse_timescale(self, lines: list[str], i: int) -> int:
        """解析 $timescale，支持单行和多行格式"""
        line = lines[i].strip()
        # 单行: $timescale 1ns $end
        if "$end" in line:
            # 提取 timescale 值
            parts = line.replace("$timescale", "").replace("$end", "").strip()
            if parts:
                self._timescale = parts
            return i + 1
        # 多行格式
        i += 1
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("$end"):
                return i + 1
            self._timescale = line
            i += 1
        return i

    def _parse_var(self, lines: list[str], i: int) -> int:
        """解析 $var，支持单行和多行格式"""
        line = lines[i].strip()
        # 单行: $var wire 1 ! clk $end
        if "$end" in line:
            inner = line.replace("$var", "").replace("$end", "").strip()
            self._parse_var_tokens(inner)
            return i + 1
        # 多行格式
        i += 1
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("$end"):
                return i + 1
            self._parse_var_tokens(line)
            i += 1
        return i

    def _parse_var_tokens(self, text: str) -> None:
        """解析 $var 内容: wire 1 ! clk"""
        parts = text.split()
        if len(parts) >= 4:
            id_code = parts[2]
            name = parts[3]
            width = int(parts[1]) if parts[1].isdigit() else 1
            self._id_to_name[id_code] = name
            self._signals[id_code] = SignalTrace(name=name, width=width)

    def _parse_dumpvars(self, lines: list[str], i: int) -> int:
        """解析初始值 dump，支持单行和多行格式"""
        line = lines[i].strip()
        # 单行: $dumpvars ... $end
        if "$end" in line:
            inner = line.replace("$dumpvars", "").replace("$end", "").strip()
            if inner:
                for token in inner.split():
                    self._parse_value_change(token)
            return i + 1
        # 多行格式
        i += 1
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("$end"):
                return i + 1
            self._parse_value_change(line)
            i += 1
        return i

    def _skip_to_end(self, lines: list[str], i: int) -> int:
        """跳过 $comment / $date / $version 等不需要解析的段"""
        if "$end" in lines[i]:
            return i + 1
        i += 1
        while i < len(lines):
            if "$end" in lines[i] or lines[i].strip().startswith("$end"):
                return i + 1
            i += 1
        return i

    def _parse_value_change(self, line: str) -> None:
        """解析值变化: bxxxx <id 或 0<id 或 1<id"""
        if not line or line.startswith("$"):
            return

        # 多行值: bxxxx 后面跟 id_code
        # 单 bit 值: 0<id 或 1<id
        value = ""
        id_code = ""

        # 查找 id_code (以非空白字符结尾的 token)
        tokens = line.split()
        if len(tokens) >= 2:
            value = tokens[0]
            id_code = tokens[1]
        elif len(tokens) == 1:
            # 可能是 "0!" 格式 (值+id 连在一起)
            token = tokens[0]
            if token[0] in "01xzXZ":
                value = token[0]
                id_code = token[1:]
            elif token[0] == "b":
                # b1010! 格式
                idx = 1
                while idx < len(token) and token[idx] in "01xzXZ":
                    idx += 1
                value = token[:idx]
                id_code = token[idx:]

        if id_code and id_code in self._signals:
            signal = self._signals[id_code]
            # 规范化 value
            if value.startswith("b"):
                value = value[1:]  # 去掉 b 前缀
            signal.changes.append(SignalChange(time_ns=self._current_time, value=value))

    # ─── build result ────────────────────────────────────────────────────────

    def _build_waveform(self) -> WaveformData:
        max_time = 0
        for sig in self._signals.values():
            if sig.max_time > max_time:
                max_time = sig.max_time

        return WaveformData(
            signals=list(self._signals.values()),
            total_time_ns=max_time,
            timescale=self._timescale,
        )
