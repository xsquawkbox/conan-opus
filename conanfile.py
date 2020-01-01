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
        "optimise_sse": ["Disable", "Allow", "Force"],
        "optimise_sse2": ["Disable", "Allow", "Force"],
        "optimise_sse4_1": ["Disable", "Allow", "Force"],
        "optimise_avx": ["Disable", "Allow", "Force"],
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        "optimise_sse": "Allow",
        "optimise_sse2": "Allow",
        "optimise_sse4_1": "Allow",
        "optimise_avx": "Allow",
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
        git.clone('https://github.com/xsquawkbox/opus.git')
        git.checkout('v%s-xsb'%self.version)

    def _configure_cmake(self):
        cmake = CMake(self)
        if 'fPIC' in self.options:
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        if self.settings.arch == 'x86':
            cmake.definitions['OPUS_X86_MAY_HAVE_SSE'] = (self.options.optimise_sse != "Disable")
            cmake.definitions['OPUS_X86_PRESUME_SSE'] = (self.options.optimise_sse == "Force")
            cmake.definitions['OPUS_X86_MAY_HAVE_SSE2'] = (self.options.optimise_sse2 != "Disable")
            cmake.definitions['OPUS_X86_PRESUME_SSE2'] = (self.options.optimise_sse2 == "Force")
        if self.settings.arch == 'x86' or self.settings.arch == 'x86_64':
            cmake.definitions['OPUS_X86_MAY_HAVE_SSE4_1'] = (self.options.optimise_sse4_1 != "Disable")
            cmake.definitions['OPUS_X86_PRESUME_SSE4_1'] = (self.options.optimise_sse4_1 == "Force")
            cmake.definitions['OPUS_X86_MAY_HAVE_AVX'] = (self.options.optimise_avx != "Disable")
            cmake.definitions['OPUS_X86_PRESUME_AVX'] = (self.options.optimise_avx == "Force")
        # disable the autovectoriser on macOS - it generates optimisations that may violate the explicit
        # optimisation options we've chosen.
        if (self.settings.compiler == 'apple-clang' or self.settings.compiler == 'clang'):
            arch_flag = ''
            if self.settings.arch == 'x86_64':
                arch_flag = '-m64'
            elif self.settings.arch == 'x86':
                # shouldn't happen
                arch_flag = '-m32'
            if arch_flag != '':
                cmake.definitions['CONAN_C_FLAGS'] = '%s -fno-slp-vectorize -fno-vectorize'%(arch_flag)
                cmake.definitions['CONAN_CXX_FLAGS'] = '%s -fno-slp-vectorize -fno-vectorize'%(arch_flag)
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

