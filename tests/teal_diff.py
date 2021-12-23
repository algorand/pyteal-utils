import re
from typing import List, Union


class LineDiff:
    def __init__(self, line_num: int, x: str, y: str):
        self.line_num = line_num
        self.x = x
        self.y = y
        self.same = x == y

    def __repr__(self) -> str:
        LN = f"<LINE {self.line_num}>"
        return LN + ("(same)" if self.same else f"[{self.x}] --> [{self.y}]")


class TEALDiff:
    def __init__(self, program_x: str, program_y: str, strip_comments: bool = True):
        self.x = program_x
        self.y = program_y
        self.strip_comments = strip_comments

        self.diffs: List["LineDiff"] = self.diff()

    def all_the_same(self) -> bool:
        return all(map(lambda d: d.same, self.diffs))

    def assert_equals(self, msg: str = None) -> None:
        assert self.all_the_same(), msg

    def first_diff(self) -> Union["LineDiff", None]:
        for diff in self.diffs:
            if not diff.same:
                return diff

        return None

    @classmethod
    def decomment(cls, line: str) -> str:
        m = re.search('(// [^"]+$)', line)
        if not m:
            return line

        return line[: -len(m.groups()[-1])]

    @classmethod
    def lines(cls, src: str, strip_comments: bool = True) -> List[str]:
        lines = map(lambda s: s.strip(), src.splitlines())
        if strip_comments:
            lines = map(lambda s: cls.decomment(s).strip(), lines)

        return list(lines)

    def diff(self) -> List["LineDiff"]:
        xlines = self.lines(self.x, strip_comments=self.strip_comments)
        ylines = self.lines(self.y, strip_comments=self.strip_comments)
        len_diff = len(ylines) - len(xlines)
        if len_diff < 0:
            ylines += [""] * -len_diff
        elif len_diff > 0:
            xlines += [""] * len_diff

        n = len(xlines)

        line_diffs = list(
            map(lambda z: LineDiff(*z), zip(range(1, n + 1), xlines, ylines))
        )
        return line_diffs
