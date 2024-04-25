import re
import typing


_RXP = re.compile(
    r"""^
    \D*
    (?P<major>\d+)\.
    (?P<minor>\d+)\.?
    (?P<revision>\d+)?
    (?P<note>.*)
    $""",
    re.VERBOSE,
)


class _Version(typing.NamedTuple):
    major: int
    minor: int
    revision: int
    note: str

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}" f".{self.revision}{self.note}"


def Version(vstring: str = "0.0.0") -> "_Version":
    if (match := _RXP.search(vstring)) is None:
        print("Unable to parse version: %s", vstring)
        return _Version(0, 0, 0, "")

    return _Version(
        int(match.group("major")),
        int(match.group("minor")),
        int(match.group("revision") or "0"),
        match.group("note"),
    )
