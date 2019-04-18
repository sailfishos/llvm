Name: llvm
Version: 7.0.1
Release: 0
Summary: The Low Level Virtual Machine (An Optimizing Compiler Infrastructure)
License: University of Illinois/NCSA Open Source License
Group: Development/Tools
URL: http://llvm.org/
Source: %{version}/%{name}-%{version}.tar.gz
Source1: LLVMBuild.txt
Patch1: nosse4-avx.patch
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
BuildRequires: cmake
BuildRequires: gcc, python

%description
LLVM is a compiler infrastructure designed for compile-time, link-time, runtime,
and idle-time optimization of programs from arbitrary programming languages.
LLVM is written in C++ and has been developed since 2000 at the University of
Illinois and Apple. It currently supports compilation of C and C++ programs, 
using front-ends derived from GCC 4.0.1. A new front-end for the C family of
languages is in development. The compiler infrastructure
includes mirror sets of programming tools as well as libraries with equivalent
functionality.

%package devel
Summary:        Libraries and Header Files for LLVM
Group:          Development/Tools
Requires:       %{name} = %{version}

%description devel
LLVM Header files

%prep
%setup -q -n %{name}-%{version}/%{name}/llvm
cp %{_sourcedir}/LLVMBuild.txt projects/

%build

mkdir -p build
pushd build

%cmake .. -G "Unix Makefiles" \
-DBUILD_SHARED_LIBS:BOOL=OFF \
-DCMAKE_BUILD_TYPE=Release \
-DLLVM_BUILD_DOCS:BOOL=OFF \
-DLLVM_BUILD_LLVM_DYLIB:BOOL=OFF \
-DLLVM_BUILD_RUNTIME:BOOL=OFF \
-DLLVM_ENABLE_ASSERTIONS:BOOL=OFF \
-DLLVM_INCLUDE_BENCHMARKS:BOOL=OFF \
-DLLVM_INCLUDE_DIRS:PATH=%{_includedir} \
-DLLVM_INCLUDE_EXAMPLES:BOOL=OFF \
-DLLVM_INCLUDE_TEST:BOOL=OFF \
-DLLVM_LINK_LLVM_DYLIB:BOOL=OFF \
-DLLVM_TARGETS_TO_BUILD=Native \
-DLLVM_TOOLS_BINARY_DIR:PATH=%{_bindir}

# Jobs limited to 4 to prevent OBS from running out of memory
make -j4
popd build

%install
rm -rf %{buildroot}
make -C build install/strip DESTDIR=%{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-, root, root)
%{_bindir}/*
%{_libdir}/*.so.*
%{_datadir}/opt-viewer

%files devel
%defattr(-, root, root)
%{_libdir}/*.a
%{_libdir}/*.so
%{_includedir}/llvm
%{_includedir}/llvm-c
%{_libdir}/cmake
