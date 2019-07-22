# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class LibpqConan(ConanFile):
    name = "libpq"
    version = "11.4"
    description = "The library used by all the standard PostgreSQL tools."
    topics = ("conan", "libpq", "postgresql", "database", "db")
    url = "https://github.com/bincrafters/conan-libpq"
    homepage = "https://www.postgresql.org/docs/current/static/libpq.html"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "PostgreSQL"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "with_openssl": [True, False]}
    default_options = {'shared': False, 'fPIC': True, 'with_zlib': False, 'with_openssl': False}
    generators = "cmake"
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return os.path.join(self.build_folder, "output")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.os == 'Windows' and self.options.shared:
            raise ConanInvalidConfiguration("libpq can not be built as shared library on Windows")

    def requirements(self):
        if self.options.with_zlib:
            self.requires.add("zlib/1.2.11@conan/stable")
        if self.options.with_openssl:
            #self.requires.add("OpenSSL/1.0.2s@conan/stable")
            self.requires.add("OpenSSL/1.1.1c@conan/stable")

    def source(self):
        source_url = "https://ftp.postgresql.org/pub/source"
        sha256 = "2043ab71f2a435a9e77b4419f804525a0b9ec1ef37d19c1c2e4013dc1cae01a7"
        tools.get("{0}/v{1}/postgresql-{2}.tar.gz".format(source_url, self.version, self.version), sha256=sha256)
        extracted_dir = "postgresql-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            args = ['--without-readline']
            args.append('--with-zlib' if self.options.with_zlib else '--without-zlib')
            args.append('--with-openssl' if self.options.with_openssl else '--without-openssl')
            with tools.chdir(self._source_subfolder):
                self._autotools.configure(args=args)
        return self._autotools

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            cmake = self._configure_cmake()
            cmake.definitions["USE_OPENSSL"] = self.options.with_openssl
            cmake.definitions["USE_ZLIB"] = self.options.with_zlib
            cmake.build()
        else:
            autotools = self._configure_autotools()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "common")):
                autotools.make()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "interfaces", "libpq")):
                autotools.make()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "include")):
                autotools.make()

    def package(self):
        self.copy(pattern="COPYRIGHT", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            cmake = self._configure_cmake()
            cmake.install()
        else:
            autotools = self._configure_autotools()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "common")):
                autotools.install()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "interfaces", "libpq")):
                autotools.install()
            with tools.chdir(os.path.join(self._source_subfolder, "src", "include")):
                autotools.install()
            self.copy(pattern="*.h", dst="include", src=os.path.join(self._build_subfolder, "include"))
            self.copy(pattern="*.h", dst=os.path.join("include", "catalog"), src=os.path.join(self._source_subfolder, "src", "include", "catalog"))
        self.copy(pattern="*.h", dst=os.path.join("include", "catalog"), src=os.path.join(self._source_subfolder, "src", "backend", "catalog"))
        self.copy(pattern="postgres_ext.h", dst="include", src=os.path.join(self._source_subfolder, "src", "include"))
        self.copy(pattern="pg_config_ext.h", dst="include", src=os.path.join(self._source_subfolder, "src", "include"))
        if self.settings.os == "Linux":
            pattern = "*.so*" if self.options.shared else "*.a"
        elif self.settings.os == "Macos":
            pattern = "*.dylib" if self.options.shared else "*.a"
        elif self.settings.os == "Windows":
            pattern = "*.a"
            self.copy(pattern="*.dll", dst="bin", src=os.path.join(self._build_subfolder, "bin"))
        self.copy(pattern=pattern, dst="lib", src=os.path.join(self._build_subfolder, "lib"))

    def package_info(self):
        self.env_info.PostgreSQL_ROOT = self.package_folder
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.libs.extend(["ws2_32", "secur32", "advapi32", "shell32", "crypt32"])
