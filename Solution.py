import re


PATTERN = (
    r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?"
    r"(?:\+(?P<build>[0-9A-Za-z.-]+))?$"
)


class Version:
    """Represents a semantic version and provides comparison operators."""

    def __init__(self, version):
        """Initialize the Version instance from a version string."""
        match = re.match(PATTERN, version)

        if not match:
            raise ValueError(f"'{version}' is not a valid semantic version.")

        self.major = match.group("major")
        self.minor = match.group("minor")
        self.patch = match.group("patch")
        self.prerelease = match.group("prerelease")
        self.build = match.group("build")
        self.version = version

    def compare_core(self, other):
        """Compare the core version (major, minor, patch) parts."""
        core_parts = zip(
            [self.major, self.minor, self.patch],
            [other.major, other.minor, other.patch],
        )
        for self_part, other_part in core_parts:
            if self_part < other_part:
                return -1
            if self_part > other_part:
                return 1
        return 0

    def compare_prerelease(self, other):
        """Compare the prerelease parts of two versions."""
        # Avoid None exception in case a version doesn't contain prerelease
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

            if not is_num1 and not is_num2:
                if id1 < id2:
                    return -1
                if id1 > id2:
                    return 1

            if is_num1 and not is_num2:
                return -1

            if is_num2 and not is_num1:
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
        if pre_cmp == -1:
            return True
        if pre_cmp == 1:
            return False

        return False

    def __eq__(self, other):
        """Return true if versions are equal."""
        return self.compare_core(other) == 0 and self.compare_prerelease(other) == 0


    def __gt__(self, other):
        return not self.__lt__(other) and not self.__eq__(other)


    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)


    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)


def main():
    """Run basic tests for the Version comparison implementation."""
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1-b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),
    ]

    for left, right in to_test:
        assert Version(left) < Version(right), "le failed"
        assert Version(right) > Version(left), "ge failed"
        assert Version(right) != Version(left), "neq failed"


if __name__ == "__main__":
    main()
