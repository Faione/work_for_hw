class Flags:
    def __init__(self, flag_base=""):
        self.flag_ranges = {}
        self.flag_base = flag_base

    def with_flag(self, flag, vranges):
        assert flag not in self.flag_ranges, "flag redefined"

        self.flag_ranges[flag] = vranges
        return self

    def flag_list(self):
        flags = [self.flag_base]
        for k, v in self.flag_ranges.items():
            temp_flags = []
            for val in v:
                sflag = f"{k} {val}"
                for flag in flags:
                    temp_flags.append(f"{flag} {sflag}")
            flags = temp_flags

        if flags[0] == self.flag_base:
            return []
        else:
            return flags

    def iter(self):
        flags = self.flag_list()
        for flag in flags:
            yield flag
            

    