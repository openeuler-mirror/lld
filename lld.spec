%bcond_without sys_llvm
%bcond_without check

%global maj_ver 15
%global min_ver 0
%global patch_ver 7

%if %{with sys_llvm}
%global pkg_name lld
%global bin_suffix %{nil}
%global install_prefix %{_prefix}
%else
%global pkg_name lld%{maj_ver}
%global bin_suffix -%{maj_ver}
%global install_prefix %{_libdir}/llvm%{maj_ver}
%endif

%global install_bindir %{install_prefix}/bin
%if 0%{?__isa_bits} == 64
%global install_libdir %{install_prefix}/lib64
%else
%global install_libdir %{install_prefix}/lib
%endif
%global install_includedir %{install_prefix}/include
%global pkg_bindir %{install_bindir}
%global pkg_libdir %{install_libdir}
%global pkg_includedir %{install_includedir}

# Don't include unittests in automatic generation of provides or requires.
%global __provides_exclude_from ^%{_libdir}/lld/.*$
%global __requires_exclude ^libgtest.*$

Name:		%{pkg_name}
Version:	%{maj_ver}.%{min_ver}.%{patch_ver}
Release:	2
Summary:	The LLVM Linker

License:	NCSA
URL:		http://llvm.org
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/lld-%{version}.src.tar.xz

Patch1:		fedora-PATCH-lld-Import-compact_unwind_encoding.h-from-libu.patch

BuildRequires:	clang
BuildRequires:	cmake
%if %{with sys_llvm}
BuildRequires:  llvm-devel = %{version}
BuildRequires:  llvm-googletest = %{version}
BuildRequires:  llvm-test = %{version}
%else
BuildRequires:	llvm%{maj_ver}-devel = %{version}
BuildRequires:	llvm%{maj_ver}-googletest = %{version}
BuildRequires:	llvm%{maj_ver}-test = %{version}
%endif
BuildRequires:	ncurses-devel
BuildRequires:	ninja-build
BuildRequires:	python3-rpm-macros
BuildRequires:	python3-lit >= %{version}
BuildRequires:	zlib-devel

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
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_INSTALL_PREFIX=%{install_prefix} \
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DLLVM_DYLIB_COMPONENTS="all" \
	-DCMAKE_SKIP_RPATH:BOOL=ON \
	-DPYTHON_EXECUTABLE=%{__python3} \
	-DLLVM_INCLUDE_TESTS=ON \
	-DLLVM_EXTERNAL_LIT=%{_bindir}/lit \
	-DLLVM_LIT_ARGS="-sv \
	--path %{install_prefix}" \
	-DLLVM_MAIN_SRC_DIR=%{install_prefix}/src

%ninja_build

%install
%ninja_install -C _build

rm %{buildroot}%{install_includedir}/mach-o/compact_unwind_encoding.h

%if %{without sys_llvm}
# Add version suffix to binaries
mkdir -p %{buildroot}/%{_bindir}
for f in %{buildroot}/%{install_bindir}/*; do
  filename=`basename $f`
  ln -s ../../%{install_bindir}/$filename %{buildroot}/%{_bindir}/$filename%{bin_suffix}
done
%endif

%check
%if %{with check}
cd _build
%ninja_build check-lld
%endif

%files
%license LICENSE.TXT
%if %{without sys_llvm}
%{_bindir}/lld%{bin_suffix}
%{_bindir}/lld-link%{bin_suffix}
%{_bindir}/ld.lld%{bin_suffix}
%{_bindir}/ld64.lld%{bin_suffix}
%{_bindir}/wasm-ld%{bin_suffix}
%endif
%{pkg_bindir}/*

%files devel
%{pkg_includedir}/lld
%{pkg_libdir}/liblld*.so
%{pkg_libdir}/cmake/lld/

%files libs
%{pkg_libdir}/liblld*.so.*

%changelog
* Thu May 25 2023 cf-zhao <zhaochuanfeng@huawei.com> - 15.0.7-2
- Support building system llvm and multi-version llvm in one spec file.

* Mon Feb 20 2023 Chenxi Mao <chenxi.mao@suse.com> - 15.0.7-1
- Upgrade to 15.0.7.

* Thu Feb 9 2023 Chenxi Mao <chenxi.mao@suse.com> - 15.0.6-2
- Enable lld unit test.

* Mon Jan 2 2023 Chenxi Mao <chenxi.mao@suse.com> - 15.0.6-1
- Package init
