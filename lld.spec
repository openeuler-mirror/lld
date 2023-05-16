%bcond_without check

%global maj_ver 15
%global min_ver 0
%global patch_ver 7

%global pkg_name lld%{maj_ver}
%global bin_suffix -%{maj_ver}
%global install_prefix %{_libdir}/llvm%{maj_ver}
%global install_includedir %{install_prefix}/include
%global install_libdir %{install_prefix}/lib
%global install_bindir %{install_prefix}/bin
%global pkg_bindir %{install_bindir}

# Don't include unittests in automatic generation of provides or requires.
%global __provides_exclude_from ^%{_libdir}/lld/.*$
%global __requires_exclude ^libgtest.*$

Name:		%{pkg_name}
Version:	%{maj_ver}.%{min_ver}.%{patch_ver}
Release:	1
Summary:	The LLVM Linker

License:	NCSA
URL:		http://llvm.org
Source0:	https://github.com/llvm/llvm-project/releases/download/llvmorg-%{version}/lld-%{version}.src.tar.xz

Patch1:		fedora-PATCH-lld-Import-compact_unwind_encoding.h-from-libu.patch

BuildRequires:	clang
BuildRequires:	cmake
BuildRequires:	llvm%{maj_ver}-devel = %{version}
BuildRequires:	llvm%{maj_ver}-googletest = %{version}
BuildRequires:	llvm%{maj_ver}-test = %{version}
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
	--path %{_libdir}/llvm%{maj_ver}" \
	-DLLVM_MAIN_SRC_DIR=%{_libdir}/llvm%{maj_ver}/src

%ninja_build

%install
%ninja_install -C _build

rm %{buildroot}%{install_includedir}/mach-o/compact_unwind_encoding.h

# Add version suffix to binaries
mkdir -p %{buildroot}/%{_bindir}
for f in %{buildroot}/%{install_bindir}/*; do
  filename=`basename $f`
  ln -s ../../%{install_bindir}/$filename %{buildroot}/%{_bindir}/$filename%{bin_suffix}
done

%check
%if %{with check}
cd _build
%ninja_build check-lld
%endif

%files
%license LICENSE.TXT
%{_bindir}/lld%{bin_suffix}
%{_bindir}/lld-link%{bin_suffix}
%{_bindir}/ld.lld%{bin_suffix}
%{_bindir}/ld64.lld%{bin_suffix}
%{_bindir}/wasm-ld%{bin_suffix}
%{pkg_bindir}

%files devel
%{install_includedir}/lld
%{install_libdir}/liblld*.so
%{install_libdir}/cmake/lld/

%files libs
%{install_libdir}/liblld*.so.*

%changelog
* Mon Feb 20 2023 Chenxi Mao <chenxi.mao@suse.com> - 15.0.7-1
- Upgrade to 15.0.7.

* Thu Feb 9 2023 Chenxi Mao <chenxi.mao@suse.com> - 15.0.6-2
- Enable lld unit test.

* Mon Jan 2 2023 Chenxi Mao <chenxi.mao@suse.com> - 15.0.6-1
- Package init
