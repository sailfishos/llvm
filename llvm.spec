Name: llvm
Version: 3.0
Release: 0
Summary: The Low Level Virtual Machine (An Optimizing Compiler Infrastructure)
License: University of Illinois/NCSA Open Source License
Group: Development/Tools
URL: http://llvm.org/
Source: http://llvm.org/releases/%{version}/%{name}-%{version}.tar.gz
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
BuildRequires: gcc >= 3.4, python

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
%setup -q -n llvm-3.0.src

%build
./configure \
--prefix=%{_prefix} \
--bindir=%{_bindir} \
--datadir=%{_datadir} \
--includedir=%{_includedir} \
--libdir=%{_libdir} \
--enable-optimized \
%ifarch %{arm}
--disable-jit \
%endif
--enable-assertions \
--disable-docs
make tools-only

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-, root, root)
%doc CREDITS.TXT LICENSE.TXT README.txt
%{_bindir}/*
%attr(744,-,-) %{_libdir}/*.so

%files devel
%defattr(-, root, root)
%attr(744,-,-) %{_libdir}/*.a
%{_includedir}/llvm
%{_includedir}/llvm-c

