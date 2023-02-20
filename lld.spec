%global maj_ver 12
%global min_ver 0
%global patch_ver 1

# Don't include unittests in automatic generation of provides or requires.
%global __provides_exclude_from ^%{_libdir}/lld/.*$
%global __requires_exclude ^libgtest.*$

Name:		lld
Version:	%{maj_ver}.%{min_ver}.%{patch_ver}
Release:	1
Summary:	The LLVM Linker

License:	NCSA
URL:		http://llvm.org
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/lld-%{version}.src.tar.xz

Patch1:		0001-fedora-PATCH-lld-Import-compact_unwind_encoding.h-from-libu.patch

BuildRequires:	clang
BuildRequires:	cmake
BuildRequires:	ninja-build
BuildRequires:	llvm-devel = %{version}
BuildRequires:	ncurses-devel
BuildRequires:	zlib-devel
BuildRequires:	python3-devel

# For make check:
BuildRequires:	python3-rpm-macros
BuildRequires:	python3-lit

Requires(post): %{_sbindir}/update-alternatives
Requires(preun): %{_sbindir}/update-alternatives

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
%autosetup -n lld-%{version}.src -p2

%build
mkdir -p _build
cd _build
%cmake .. -G Ninja \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DLLVM_DYLIB_COMPONENTS="all" \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
	-DPYTHON_EXECUTABLE=%{__python3} \
	-DLLVM_INCLUDE_TESTS=OFF \
	-DLLVM_MAIN_SRC_DIR=%{_datadir}/llvm/src

%ninja_build

%install
%ninja_install -C _build

rm %{buildroot}%{_includedir}/mach-o/compact_unwind_encoding.h

%check

%files
%license LICENSE.TXT
%{_bindir}/lld*
%{_bindir}/ld.lld
%{_bindir}/ld64.lld
%{_bindir}/ld64.lld.darwinnew
%{_bindir}/wasm-ld

%files devel
%{_includedir}/lld
%{_libdir}/liblld*.so
%{_libdir}/cmake/lld/

%files libs
%{_libdir}/liblld*.so.*

%changelog
* Mon Feb 18 2023 cf-zhao <zhaochuanfeng@huawei.com> - 12.0.1-1
- Package init

