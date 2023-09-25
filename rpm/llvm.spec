%ifarch %ix86 x86_64
# ARM/AARCH64 enabled due to rhbz#1627500
%global llvm_targets X86;AMDGPU;NVPTX;BPF;ARM;AArch64;WebAssembly
%endif
%ifarch aarch64
%global llvm_targets AArch64;AMDGPU;BPF;WebAssembly
%endif
%ifarch %{arm}
%global llvm_targets ARM;AMDGPU;BPF;WebAssembly
%endif

Name: llvm
Version: 16.0.6
Release: 0
Summary: The Low Level Virtual Machine (An Optimizing Compiler Infrastructure)
License: University of Illinois/NCSA Open Source License
URL: http://llvm.org/
Source: %{version}/%{name}-%{version}.tar.gz

Patch1: 0001-LLVM-Add-MeeGo-vendor-type.patch
Patch2: 0002-Add-Triple-isMeeGo.patch
Patch3: 0003-Clang-SailfishOS-toolchain.patch
Patch4: 0004-Make-funwind-tables-the-default-for-all-archs.patch
Patch5: 0005-Disable-out-of-line-atomics-on-MeeGo.patch

Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
BuildRequires: cmake, ninja
BuildRequires: gcc, python3-base
Requires: %{name}-libs = %{version}-%{release}

%description
LLVM is a compiler infrastructure designed for compile-time, link-time, runtime,
and idle-time optimization of programs from arbitrary programming languages.
LLVM is written in C++ and has been developed since 2000 at the University of
Illinois and Apple. It currently supports compilation of C and C++ programs, 
using front-ends derived from GCC 4.0.1. A new front-end for the C family of
languages is in development. The compiler infrastructure
includes mirror sets of programming tools as well as libraries with equivalent
functionality.

%package libs
Summary:        LLVM shared libraries

%description libs
Shared libraries for the LLVM compiler infrastructure.

%package devel
Summary:        Libraries and Header Files for LLVM
Group:          Development/Tools
Requires:       %{name} = %{version}-%{release}

%description devel
LLVM Header files

%prep
%autosetup -p1 -n %{name}-%{version}/%{name}

%build
pushd llvm

mkdir -p build
pushd build

# Decrease debuginfo verbosity to reduce memory consumption during final library linking
%global optflags %(echo %{optflags} | sed 's/-g /-g0 /')

%cmake .. -G Ninja \
-DBUILD_SHARED_LIBS:BOOL=OFF \
-DCMAKE_BUILD_TYPE=Release \
-DCMAKE_INSTALL_RPATH=";" \
-DCMAKE_C_FLAGS="%{optflags} -DNDEBUG" \
-DCMAKE_CXX_FLAGS="%{optflags} -DNDEBUG" \
%if 0%{?__isa_bits} == 64
-DLLVM_LIBDIR_SUFFIX=64 \
%else
-DLLVM_LIBDIR_SUFFIX= \
%endif
-DLLVM_BUILD_DOCS:BOOL=OFF \
-DLLVM_BUILD_LLVM_DYLIB:BOOL=ON \
-DLLVM_BUILD_RUNTIME:BOOL=OFF \
-DLLVM_ENABLE_ASSERTIONS:BOOL=OFF \
-DLLVM_INCLUDE_BENCHMARKS:BOOL=OFF \
-DLLVM_INCLUDE_DIRS:PATH=%{_includedir} \
-DLLVM_INCLUDE_EXAMPLES:BOOL=OFF \
-DLLVM_INCLUDE_TEST:BOOL=OFF \
-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
-DLLVM_PARALLEL_LINK_JOBS=1 \
-DLLVM_TARGETS_TO_BUILD="%{llvm_targets}" \
-DLLVM_TOOLS_BINARY_DIR:PATH=%{_bindir} \
-DLLVM_INCLUDE_UTILS:BOOL=ON \
-DLLVM_UTILS_INSTALL_DIR:PATH=%{_bindir}

%ninja_build
popd

popd

%install
pushd llvm

rm -rf %{buildroot}
%ninja_install -C build

popd

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-, root, root)
%license llvm/LICENSE.TXT
%{_bindir}/*
%{_datadir}/opt-viewer

%files libs
%license llvm/LICENSE.TXT
%{_libdir}/*.so.*
%{_libdir}/libLLVM-*.so

%files devel
%defattr(-, root, root)
%{_libdir}/*.a
%{_libdir}/*.so
%exclude %{_libdir}/libLLVM-*.so
%{_includedir}/llvm
%{_includedir}/llvm-c
%{_libdir}/cmake
