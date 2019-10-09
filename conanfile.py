from conans import ConanFile, CMake, tools

class LibopusConan(ConanFile):
    name = "libopus"
    version = "1.3.1"
    license = "BSD-Like"
    author = "Chris Collins <kuroneko@sysadninjas.net>"
    url = "https://git.sysadninjas.net/conan/opus"
    description = "the Xiph Opus audio codec reference implementation"
    topics = ("audio", "compression", "codec")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "optimise_sse": [True, False],
        "optimise_sse2": [True, False],
        "optimise_sse4_1": [True, False],
        "optimise_avx": [True, False],
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        "optimise_sse": True,
        "optimise_sse2": True,
        "optimise_sse4_1": False,
        "optimise_avx": False,
        }
    generators = "cmake"

    def configure(self):
        if self.settings.arch != 'x86':        
            del self.options.optimise_sse
            del self.options.optimise_sse2
        if self.settings.arch != 'x86' and self.settings.arch != 'x86_64':
            del self.options.optimise_sse4_1
            del self.options.optimise_avx
        if self.settings.os == 'Windows':
            # irrelevant on Windows.
            del self.options.fPIC

    def source(self):
        git = tools.Git(folder='opus')
        git.clone('https://github.com/xiph/opus.git')
        git.checkout('v%s'%self.version)
        # ugh.  The upstream tarball is missing a critical cmake build file.
        #tools.get('https://archive.mozilla.org/pub/opus/opus-1.3.1.tar.gz')
        tools.replace_in_file("opus/CMakeLists.txt", "project(Opus LANGUAGES C VERSION ${PROJECT_VERSION})",
                              '''project(Opus LANGUAGES C VERSION ${PROJECT_VERSION})
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def _configure_cmake(self):
        cmake = CMake(self)
        if 'fPIC' in self.options:
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        if self.settings.arch == 'x86':
            cmake.definitions['OPUS_X86_MAY_HAVE_SSE'] = self.options.optimise_sse
            cmake.definitions['OPUS_X86_PRESUME_SSE'] = self.options.optimise_sse
            cmake.definitions['OPUS_X86_MAY_HAVE_SSE2'] = self.options.optimise_sse2
            cmake.definitions['OPUS_X86_PRESUME_SSE2'] = self.options.optimise_sse2
        if self.settings.arch == 'x86' or self.settings.arch == 'x86_64':
            cmake.definitions['OPUS_X86_MAY_HAVE_SSE4_1'] = self.options.optimise_sse4_1
            cmake.definitions['OPUS_X86_PRESUME_SSE4_1'] = self.options.optimise_sse4_1
            cmake.definitions['OPUS_X86_MAY_HAVE_AVX'] = self.options.optimise_avx
            cmake.definitions['OPUS_X86_PRESUME_AVX'] = self.options.optimise_avx
        cmake.configure(source_folder="opus")
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()
        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["opus"]

