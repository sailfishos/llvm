%global maj_ver 14
%global min_ver 0
%global patch_ver 6

# Opt out of https://fedoraproject.org/wiki/Changes/fno-omit-frame-pointer
# https://bugzilla.redhat.com/show_bug.cgi?id=2158587
%undefine _include_frame_pointers

%global pkg_name lld
%global install_prefix /usr

Name:		lld
Version:	%{maj_ver}.%{min_ver}.%{patch_ver}
Release:	1
Summary:	The LLVM Linker
License:	Apache-2.0 WITH LLVM-exception OR NCSA
URL:		http://llvm.org
Source:		%{version}/%{name}-%{version}.tar.gz

Patch1: 0001-LLVM-Add-MeeGo-vendor-type.patch
Patch2: 0002-Add-Triple-isMeeGo.patch
Patch3: 0003-Clang-SailfishOS-toolchain.patch
Patch4: 0004-Make-funwind-tables-the-default-for-all-archs.patch
Patch5: 0005-Disable-out-of-line-atomics-on-MeeGo.patch
Patch6:	0006-PATCH-lld-Import-compact_unwind_encoding.h-from-libu.patch

BuildRequires:	clang
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	llvm-devel >= %{version}
BuildRequires:	ncurses-devel
BuildRequires:	zlib-devel

Requires: %{name}-libs = %{version}-%{release}

%description
The LLVM project linker.

%package devel
Summary:	Libraries and header files for LLD
Requires: %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
This package contains library and header files needed to develop new native
programs that use the LLD infrastructure.

%package libs
Summary:	LLD shared libraries

%description libs
Shared libraries for LLD.

%prep

%autosetup -p1 -n %{name}-%{version}/llvm

%build

pushd lld
mkdir -p build
pushd build

%cmake .. \
	-GNinja \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_INSTALL_PREFIX=%{install_prefix} \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DLLVM_DYLIB_COMPONENTS="all" \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
	-DPYTHON_EXECUTABLE=%{__python3} \
	-DLLVM_INCLUDE_TESTS=OFF \
	-DLLVM_EXTERNAL_LIT=%{_bindir}/lit \
	-DLLVM_LIT_ARGS="-sv \
	--path %{_libdir}/llvm" \
	-DLLVM_LIBDIR_SUFFIX= \
	-DLLVM_MAIN_SRC_DIR=%{_datadir}/llvm/src

%ninja_build
popd
popd

%install
pushd lld
%ninja_install -C build

rm %{buildroot}%{_includedir}/mach-o/compact_unwind_encoding.h

# Required when using update-alternatives:
# https://docs.fedoraproject.org/en-US/packaging-guidelines/Alternatives/
touch %{buildroot}%{_bindir}/ld
install -D -m 644 -t  %{buildroot}%{_mandir}/man1/ docs/ld.lld.1

popd

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license lld/LICENSE.TXT
%ghost %{_bindir}/ld
%{_bindir}/lld*
%{_bindir}/ld.lld
%{_bindir}/ld64.lld
%{_bindir}/wasm-ld
%{_mandir}/man1/ld.lld.1*

%files devel
%{_includedir}/lld
%{_libdir}/liblld*.so
%{_libdir}/cmake/lld/

%files libs
%license lld/LICENSE.TXT
%{_libdir}/liblld*.so.*
