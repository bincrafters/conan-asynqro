from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os


class AsynqroConan(ConanFile):
    name = "asynqro"
    description = "Futures and thread pool for C++ (with optional Qt support)"
    topics = ("conan", "asynqro", "future", "promise")
    url = "https://github.com/bincrafters/conan-asynqro"
    homepage = "https://github.com/dkormalev/asynqro"
    license = "BSD-3-Clause"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"with_qt": [True, False], "shared": [True, False], "fPIC": [True, False]}
    default_options = {"with_qt": False, "shared": False, "fPIC": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    def requirements(self):
        if self.options.with_qt:
            self.requires = ("qt/5.15.2")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support." % (self.name, compiler))
            self.output.warn(
                "%s requires a compiler that supports at least C++%s." % (self.name, minimal_cpp_standard))
            return
        version = tools.Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s." % (self.name, minimal_cpp_standard))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["ASYNQRO_BUILD_TESTS"] = False
            self._cmake.definitions["ASYNQRO_QT_SUPPORT"] = self.options.with_qt
            self._cmake.definitions["ASYNQRO_BUILD_WITH_GCOV"] = False
            self._cmake.definitions["ASYNQRO_BUILD_WITH_DUMMY"] = False
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
