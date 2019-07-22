#!/usr/bin/env python

from cpt.packager import ConanMultiPackager

if __name__ == "__main__":
    shared_option_name = False if tools.os_info.is_windows else None
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name=shared_option_name)
    builder.run()
