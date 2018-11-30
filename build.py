#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
from bincrafters import build_template_default

if __name__ == "__main__":
    builder = build_template_default.get_builder()
    for settings, options, env_vars, build_requires, reference in reversed(builder.items):
        new_options = copy.copy(options)
        new_options.update({"libpq:with_openssl": True, "libpq:with_zlib": True})
        builder.add(settings, new_options, env_vars, build_requires)
    builder.run()
