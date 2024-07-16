%global maj_ver 18
%global min_ver 1
%global patch_ver 8

%global clang_tools_binaries \
	%{_bindir}/amdgpu-arch \
	%{_bindir}/clang-apply-replacements \
	%{_bindir}/clang-change-namespace \
	%{_bindir}/clang-check \
	%{_bindir}/clang-doc \
	%{_bindir}/clang-extdef-mapping \
	%{_bindir}/clang-format \
	%{_bindir}/clang-include-cleaner \
	%{_bindir}/clang-include-fixer \
	%{_bindir}/clang-linker-wrapper \
	%{_bindir}/clang-move \
	%{_bindir}/clang-offload-bundler \
	%{_bindir}/clang-offload-packager \
	%{_bindir}/clang-pseudo \
	%{_bindir}/clang-query \
	%{_bindir}/clang-refactor \
	%{_bindir}/clang-reorder-fields \
	%{_bindir}/clang-rename \
	%{_bindir}/clang-repl \
	%{_bindir}/clang-scan-deps \
	%{_bindir}/clang-tidy \
	%{_bindir}/clangd \
	%{_bindir}/diagtool \
	%{_bindir}/hmaptool \
	%{_bindir}/nvptx-arch \
	%{_bindir}/pp-trace \
	%{_bindir}/run-clang-tidy

%global clang_binaries \
	%{_bindir}/clang \
	%{_bindir}/clang++ \
	%{_bindir}/clang-%{maj_ver} \
	%{_bindir}/clang++-%{maj_ver} \
	%{_bindir}/clang-cl \
	%{_bindir}/clang-cpp

Name:		clang
Version:	%{maj_ver}.%{min_ver}.%{patch_ver}
Release:	0
Summary:	A C language family front-end for LLVM
License:	NCSA
URL:		http://llvm.org
Source:		%{version}/%{name}-%{version}.tar.gz

Patch1: 0001-LLVM-Add-MeeGo-vendor-type.patch
Patch2: 0002-Add-Triple-isMeeGo.patch
Patch3: 0003-Clang-SailfishOS-toolchain.patch
Patch4: 0004-Make-funwind-tables-the-default-for-all-archs.patch

BuildRequires:	gcc
BuildRequires:	gcc-c++
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	llvm-devel
BuildRequires:	libxml2-devel
BuildRequires:	python3-devel

# clang requires gcc, clang++ requires libstdc++-devel
# - https://bugzilla.redhat.com/show_bug.cgi?id=1021645
# - https://bugzilla.redhat.com/show_bug.cgi?id=1158594
Requires:	libstdc++-devel
Requires:	gcc-c++

Provides:	clang(major) = %{maj_ver}
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

%description
clang: noun
    1. A loud, resonant, metallic sound.
    2. The strident call of a crane or goose.
    3. C-language family front-end toolkit.

The goal of the Clang project is to create a new C, C++, Objective C
and Objective C++ front-end for the LLVM compiler. Its tools are built
as libraries and designed to be loosely-coupled and extensible.

%package libs
Summary:	Runtime library for clang

%description libs
Runtime library for clang.

%package devel
Summary:	Development header files for clang
Requires:	%{name}%{?_isa} = %{version}-%{release}
# The clang CMake files reference tools from clang-tools-extra.
Requires:	%{name}-tools-extra%{?_isa} = %{version}-%{release}

%description devel
Development header files for clang.

%package analyzer
Summary:	A source code analysis framework
License:	NCSA and MIT
BuildArch:	noarch
Requires:	%{name} = %{version}-%{release}

%description analyzer
The Clang Static Analyzer consists of both a source code analysis
framework and a standalone tool that finds bugs in C and Objective-C
programs. The standalone tool is invoked from the command-line, and is
intended to run in tandem with a build of a project or code base.

%package tools-extra
Summary:	Extra tools for clang
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description tools-extra
A set of extra tools built using Clang's tooling API.

%package tools-extra-devel
Summary: Development header files for clang tools
Requires: %{name}-tools-extra = %{version}-%{release}

%description tools-extra-devel
Development header files for clang tools.


%prep
%autosetup -p1 -n %{name}-%{version}/llvm

# symlink clang extra tools to enable build
ln -s ../../clang-tools-extra clang/tools/extra || :

%build

pushd clang

mkdir -p build
pushd build

# Decrease debuginfo verbosity to reduce memory consumption during final library linking
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')

# -DCMAKE_INSTALL_RPATH=";" is a workaround for llvm manually setting the
# rpath of libraries and binaries.  llvm will skip the manual setting
# if CAMKE_INSTALL_RPATH is set to a value, but cmake interprets this value
# as nothing, so it sets the rpath to "" when installing.
%cmake .. -G Ninja \
	-DLLVM_PARALLEL_LINK_JOBS=1 \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DCMAKE_BUILD_TYPE=Release \
	-DPYTHON_EXECUTABLE=%{__python3} \
	-DCMAKE_INSTALL_RPATH:BOOL=";" \
%ifarch s390 s390x %{arm} aarch64 %ix86 ppc64le
	-DCMAKE_C_FLAGS="%{optflags} -DNDEBUG" \
	-DCMAKE_CXX_FLAGS="%{optflags} -DNDEBUG" \
%endif
	-DCLANG_INCLUDE_TESTS:BOOL=OFF \
	-DLLVM_MAIN_SRC_DIR=%{_datadir}/llvm/src \
%if 0%{?__isa_bits} == 64
	-DLLVM_LIBDIR_SUFFIX=64 \
%else
	-DLLVM_LIBDIR_SUFFIX= \
%endif
	\
	-DLLVM_TABLEGEN_EXE:FILEPATH=%{_bindir}/llvm-tblgen \
	-DCLANG_ENABLE_ARCMT:BOOL=ON \
	-DCLANG_ENABLE_STATIC_ANALYZER:BOOL=ON \
	-DCLANG_INCLUDE_DOCS:BOOL=ON \
	-DCLANG_PLUGIN_SUPPORT:BOOL=ON \
	-DENABLE_LINKER_BUILD_ID:BOOL=ON \
	-DLLVM_ENABLE_EH=OFF \
	-DLLVM_ENABLE_RTTI=OFF \
	-DLLVM_BUILD_DOCS=OFF \
	-DLLVM_ENABLE_SPHINX=OFF \
	-DCLANG_LINK_CLANG_DYLIB=ON \
	-DSPHINX_WARNINGS_AS_ERRORS=OFF \
	-DBUILD_SHARED_LIBS=OFF \
	-DCLANG_BUILD_EXAMPLES:BOOL=OFF \
	-DCLANG_DEFAULT_UNWINDLIB=libgcc \
	-DLLVM_INCLUDE_TESTS=OFF

%ninja_build
popd

popd

%install
pushd clang

%ninja_install -C build

mkdir -p %{buildroot}%{python3_sitelib}/clang/

# install scanbuild-py to python sitelib.
mv %{buildroot}/%{_libdir}/{libear,libscanbuild} %{buildroot}%{python3_sitelib}

# remove editor integrations (bbedit, sublime, emacs, vim)
rm -vf %{buildroot}%{_datadir}/clang/clang-format-bbedit.applescript
rm -vf %{buildroot}%{_datadir}/clang/clang-format-sublime.py*
rm -vf %{buildroot}%{_datadir}/clang/*.el

# TODO: Package html docs
rm -Rvf %{buildroot}%{_docdir}/%{name}-%{version}}
rm -Rvf %{buildroot}%{_prefix}/share/clang/clang-doc-default-stylesheet.css
rm -Rvf %{buildroot}%{_prefix}/share/clang/index.js
rm -Rvf %{buildroot}%{_mandir}/man1

# TODO: What are the Fedora guidelines for packaging bash autocomplete files?
rm -vf %{buildroot}%{_datadir}/clang/bash-autocomplete.sh

# Add clang++-{version} symlink
ln -s clang++ %{buildroot}%{_bindir}/clang++-%{maj_ver}

# remove static libs
rm -Rvf %{buildroot}%{_libdir}/*.a

# remove git-clang-format
rm -vf %{buildroot}%{_bindir}/git-clang-format

popd

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%license clang/LICENSE.TXT
%{clang_binaries}

%files libs
%license clang/LICENSE.TXT
%{_libdir}/clang/
%{_libdir}/*.so.*

%files devel
%{_libdir}/*.so
%{_includedir}/clang/
%{_includedir}/clang-c/
%{_libdir}/cmake/*
%dir %{_datadir}/clang/

%files analyzer
%{_bindir}/scan-view
%{_bindir}/scan-build
%{_bindir}/analyze-build
%{_bindir}/intercept-build
%{_bindir}/scan-build-py
%{_libexecdir}/ccc-analyzer
%{_libexecdir}/c++-analyzer
%{_libexecdir}/analyze-c++
%{_libexecdir}/analyze-cc
%{_libexecdir}/intercept-c++
%{_libexecdir}/intercept-cc
%{_datadir}/scan-view/
%{_datadir}/scan-build/
%{python3_sitelib}/libear
%{python3_sitelib}/libscanbuild

%files tools-extra
%{clang_tools_binaries}
%{_bindir}/c-index-test
%{_bindir}/find-all-symbols
%{_bindir}/modularize
%{_datadir}/clang/clang-format.py*
%{_datadir}/clang/clang-format-diff.py*
%{_datadir}/clang/clang-include-fixer.py*
%{_datadir}/clang/clang-tidy-diff.py*
%{_datadir}/clang/run-find-all-symbols.py*
%{_datadir}/clang/clang-rename.py*

%files tools-extra-devel
%{_includedir}/clang-tidy/
