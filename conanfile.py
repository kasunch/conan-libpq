#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools
import os
import shutil


class LibpqConan(ConanFile):
    name = "libpq"
    version = "9.6.9"
    description = "The library used by all the standard PostgreSQL tools."
    url = "https://github.com/bincrafters/conan-libpq"
    homepage = "https://www.postgresql.org/docs/current/static/libpq.html"
    license = "PostgreSQL"
    exports = ["LICENSE.md", "FindPostgreSQL.cmake"]
    exports_sources = ["OriginalCMakeLists.txt", "CMakeLists.txt"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "with_openssl": [True, False]}
    default_options = "shared=False", "fPIC=True", "with_zlib=False", "with_openssl=False"
    source_subfolder = "source_subfolder"
    generators = "cmake"
    build_subfolder = "build_subfolder"
    autotools = None

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
            self.options.with_openssl = True

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_zlib:
            self.requires.add("zlib/1.2.11@conan/stable")
        if self.options.with_openssl:
            self.requires.add("OpenSSL/1.0.2o@conan/stable")

    def source(self):
        source_url = "https://ftp.postgresql.org/pub/source"
        tools.get("{0}/v{1}/postgresql-{2}.tar.gz".format(source_url, self.version, self.version))
        extracted_dir = "postgresql-" + self.version
        os.rename(extracted_dir, self.source_subfolder)
        shutil.copyfile("OriginalCMakeLists.txt", os.path.join(self.source_subfolder, "CMakeLists.txt"))

    def configure_autotools(self):
        if not self.autotools:
            self.autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            self.build_subfolder = os.path.join(self.build_folder, "output")
            args = ['--without-readline']
            args.append('--with-zlib' if self.options.with_zlib else '--without-zlib')
            args.append('--with-openssl' if self.options.with_openssl else '--without-openssl')
            build_subfolder = tools.unix_path(self.build_subfolder) if self.settings.os == "Windows" else self.build_subfolder
            args.append('--prefix={}'.format(build_subfolder))
            with tools.chdir(self.source_subfolder):
                self.autotools.configure(args=args)
        return self.autotools

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build_autotools(self):
        autotools = self.configure_autotools()
        with tools.chdir(os.path.join(self.source_subfolder, "src", "common")):
            autotools.make()
        with tools.chdir(os.path.join(self.source_subfolder, "src", "interfaces", "libpq")):
            autotools.make()

    def build_cmake(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio" and float(self.settings.compiler.version.value) == 12:
            tools.replace_in_file(os.path.join(self.source_subfolder, "src", "port", "win32error.c"), "_dosmaperr(unsigned long e)", "_dosmaperr_ext(unsigned long e)")
        cmake = self.configure_cmake()
        cmake.build()

    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.build_cmake()
        else:
            self.build_autotools()

    def package(self):
        self.copy(pattern="COPYRIGHT", dst="licenses", src=self.source_subfolder)
        self.copy("FindPostgreSQL.cmake")
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            cmake = self.configure_cmake()
            cmake.install()
        else:
            autotools = self.configure_autotools()
            with tools.chdir(os.path.join(self.source_subfolder, "src", "common")):
                autotools.install()
            with tools.chdir(os.path.join(self.source_subfolder, "src", "interfaces", "libpq")):
                autotools.install()
            self.copy(pattern="*.h", dst="include", src=os.path.join(self.build_subfolder, "include"))
            self.copy(pattern="postgres_ext.h", dst="include", src=os.path.join(self.source_subfolder, "src", "include"))
            self.copy(pattern="pg_config_ext.h", dst="include", src=os.path.join(self.source_subfolder, "src", "include"))
            if self.settings.os == "Linux":
                pattern = "*.so*" if self.options.shared else "*.a"
            elif self.settings.os == "Macos":
                pattern = "*.dylib" if self.options.shared else "*.a"
            self.copy(pattern=pattern, dst="lib", src=os.path.join(self.build_subfolder, "lib"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.libs.extend(["ws2_32", "Secur32"])
