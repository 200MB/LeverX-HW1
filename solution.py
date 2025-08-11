import re
from functools import total_ordering


@total_ordering
class Version:
    """Represents a semantic version and provides comparison operators."""

    PATTERN = (
        r"^(?P<major>0|[1-9]\d*)\."
        r"(?P<minor>0|[1-9]\d*)\."
        r"(?P<patch>0|[1-9]\d*)"
        r"(?:-"
        r"(?P<prerelease>"
        r"(?:0|[1-9]\d*|[A-Za-z-][0-9A-Za-z-]*)"
        r"(?:\.(?:0|[1-9]\d*|[A-Za-z-][0-9A-Za-z-]*))*"
        r")"
        r")?"
        r"(?:\+"
        r"(?P<build>"
        r"[0-9A-Za-z-]+"
        r"(?:\.[0-9A-Za-z-]+)*"
        r")"
        r")?$"
    )

    COMPATIBILITY_MODE = (
        r"^(?P<major>0|[1-9]\d*)\."
        r"(?P<minor>0|[1-9]\d*)\."
        r"(?P<patch>0|[1-9]\d*)"
        r"(?:(?P<prerelease>"
        r"(?:rc|[a-zA-Z])\d*"
        r"))?$"
    )

    def _set_values(self, match, comp_match):
        """Set Version values depending on which regex is matched."""
        if match:
            self.major = int(match.group("major"))
            self.minor = int(match.group("minor"))
            self.patch = int(match.group("patch"))
            self.prerelease = match.group("prerelease")
            self.build = match.group("build")
        else:
            self.major = int(comp_match.group("major"))
            self.minor = int(comp_match.group("minor"))
            self.patch = int(comp_match.group("patch"))
            self.prerelease = comp_match.group("prerelease")
            self.build = None

        if self.prerelease and not match:
            self.prerelease = self._normalize_prerelease(self.prerelease)

    @staticmethod
    def _normalize_prerelease(prerelease_str):
        """Convert shorthand prerelease (e.g., 'b1') into a normalized form (e.g., 'b-1')."""
        m = re.match(r"^(rc|[a-zA-Z])(\d*)$", prerelease_str)
        if m:
            prefix, number = m.groups()
            if number:
                return f"{prefix}-{int(number)}"
            return prefix
        return prerelease_str

    def __init__(self, version):
        """Initialize the Version instance from a version string."""
        match = re.match(self.PATTERN, version)
        comp_match = re.match(self.COMPATIBILITY_MODE, version)

        if not match and not comp_match:
            raise ValueError(f"'{version}' is not a valid semantic version.")

        self.major = None
        self.minor = None
        self.patch = None
        self.prerelease = None
        self.build = None
        self.version = version

        self._set_values(match, comp_match)

    def compare_core(self, other):
        """Compare the core version (major, minor, patch) parts."""
        for self_part, other_part in zip(
            [self.major, self.minor, self.patch],
            [other.major, other.minor, other.patch],
        ):
            if self_part < other_part:
                return -1
            if self_part > other_part:
                return 1
        return 0

    def compare_prerelease(self, other):
        """Compare the prerelease parts of two versions."""
        if self.prerelease and not other.prerelease:
            return -1
        if not self.prerelease and other.prerelease:
            return 1
        if not self.prerelease and not other.prerelease:
            return 0

        id1_parts = self.prerelease.split(".")
        id2_parts = other.prerelease.split(".")
        for id1, id2 in zip(id1_parts, id2_parts):
            is_num1 = id1.isdigit()
            is_num2 = id2.isdigit()

            if is_num1 and is_num2:
                if int(id1) < int(id2):
                    return -1
                if int(id1) > int(id2):
                    return 1
            elif not is_num1 and not is_num2:
                if id1 < id2:
                    return -1
                if id1 > id2:
                    return 1
            elif is_num1 and not is_num2:
                return -1
            elif is_num2 and not is_num1:
                return 1

        if len(id1_parts) < len(id2_parts):
            return -1
        if len(id1_parts) > len(id2_parts):
            return 1
        return 0

    def __lt__(self, other):
        """Return true if version is less than the other."""
        core_cmp = self.compare_core(other)
        if core_cmp == -1:
            return True
        if core_cmp == 1:
            return False

        pre_cmp = self.compare_prerelease(other)
        return pre_cmp == -1

    def __eq__(self, other):
        """Return true if versions are equal."""
        return (
            self.compare_core(other) == 0
            and self.compare_prerelease(other) == 0
        )


def main():
    """Run basic tests for the Version comparison implementation."""
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),
    ]

    for left, right in to_test:
        assert Version(left) < Version(right), "le failed"
        assert Version(right) > Version(left), "ge failed"
        assert Version(right) != Version(left), "neq failed"


if __name__ == "__main__":
    main()
