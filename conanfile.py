from conans import ConanFile, CMake, tools
import os


class AsynqroConan(ConanFile):
    name = "asynqro"
    description = "Futures and thread pool for C++ (with optional Qt support)"
    topics = ("conan", "asynqro", "future", "promise")
    url = "https://github.com/bincrafters/conan-asynqro"
    homepage = "https://github.com/dkormalev/asynqro"
    license = "MIT"  # Indicates license type of the packaged library; please use SPDX Identifiers https://spdx.org/licenses/
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"with_qt": [True, False], "shared": [True, False], "fPIC": [True, False]}
    default_options = {"with_qt": False, "shared": False, "fPIC": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    def requirements(self):
        if self.options.with_qt == True:
            self.requires = ("qt/5.14.2@bincrafters/stable")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["ASYNQRO_BUILD_TESTS"] = False
            self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
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

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
