# NOTE: JavaScript version is 1.8.7, implementation version is 1.0.0; what should be package version?
# Some paths (library name, .pc file) seem intentionally not conflict with js < 1.8,
# but some still do (includes path, js-config, js shell).
# It's somehow messy, so let's put this version in separate js187 package for now,
# until upstream decides which way to go in the future.
#
# Conditional build:
%bcond_without	default_js	# build as default js package

Summary:	SpiderMonkey JavaScript 1.8.7 implementation
Summary(pl.UTF-8):	Implementacja SpiderMonkey języka JavaScript 1.8.7
Name:		js187
Version:	1.0.0
Release:	5
License:	MPL 1.1 or GPL v2+ or LGPL v2.1+
Group:		Development/Languages
#Source0:	http://ftp.mozilla.org/pub/mozilla.org/js/%{name}-%{version}.tar.gz
Source0:	%{name}-%{version}.tar.gz
# Source0-md5:	9399466aa36e98e157cb3780c3f96dde
Patch0:		%{name}-install.patch
Patch1:		%{name}-x32.patch
URL:		http://www.mozilla.org/js/
BuildRequires:	libstdc++-devel
BuildRequires:	nspr-devel >= 4.7.0
BuildRequires:	perl-base >= 1:5.6
BuildRequires:	python >= 1:2.5
BuildRequires:	readline-devel
BuildRequires:	rpm-perlprov
BuildRequires:	rpmbuild(macros) >= 1.294
BuildRequires:	sed >= 4.0
Requires:	%{name}-libs = %{version}-%{release}
%if %{with default_js}
Provides:	js = 2:1.8.7
Obsoletes:	js < 2:1.8.7
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
JavaScript Reference Implementation (codename SpiderMonkey). The
package contains JavaScript runtime (compiler, interpreter,
decompiler, garbage collector, atom manager, standard classes) and
small "shell" program that can be used interactively and with .js
files to run scripts.

%description -l pl.UTF-8
Wzorcowa implementacja JavaScriptu (o nazwie kodowej SpiderMonkey).
Pakiet zawiera środowisko uruchomieniowe (kompilator, interpreter,
dekompilator, odśmiecacz, standardowe klasy) i niewielką powłokę,
która może być używana interaktywnie lub z plikami .js do uruchamiania
skryptów.

%package libs
Summary:	SpiderMonkey JavaScript 1.8.7 library
Summary(pl.UTF-8):	Biblioteka SpiderMonkey JavaScript 1.8.7
Group:		Libraries
Requires:	nspr >= 4.7.0
Conflicts:	js187 < 1.0.0-2

%description libs
SpiderMonkey JavaScript 1.8.7 library.

%description libs -l pl.UTF-8
Biblioteka SpiderMonkey JavaScript 1.8.7.

%package devel
Summary:	Header files for JavaScript 1.8.7 reference library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki JavaScript 1.8.7
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	libstdc++-devel
Requires:	nspr-devel >= 4.7.0
%if %{with default_js}
Provides:	js-devel = 2:1.8.7
Obsoletes:	js-devel < 2:1.8.7
%endif

%description devel
Header files for JavaScript 1.8.7 reference library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki JavaScript 1.8.7.

%package static
Summary:	Static JavaScript 1.8.7 reference library
Summary(pl.UTF-8):	Statyczna biblioteka JavaScript 1.8.7
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}
%if %{with default_js}
Provides:	js-static = 2:1.8.7
Obsoletes:	js-static < 2:1.8.7
%endif

%description static
Static version of JavaScript 1.8.7 reference library.

%description static -l pl.UTF-8
Statyczna wersja biblioteki JavaScript 1.8.7.

%prep
%setup -q -n js-1.8.7
%patch0 -p1
%patch1 -p1

sed -i -e 's/-O3//' js/src/Makefile.in js/src/config/Makefile.in

%build
cd js/src
%configure2_13 \
	--enable-readline \
	--enable-threadsafe \
	--enable-system-ffi \
	--disable-methodjit \
	--with-system-nspr

%{__make} \
	HOST_OPTIMIZE_FLAGS= \
	MOZILLA_VERSION=%{version}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -j1 -C js/src install \
	DESTDIR=$RPM_BUILD_ROOT \
	MOZILLA_VERSION=%{version} \
	MODULE=%{name}

# not installed by make install
cp -aL js/src/dist/include/{ds,gc,js,mozilla,vm} $RPM_BUILD_ROOT%{_includedir}/js187

# not installed by make install in new buildsystem
install js/src/shell/js $RPM_BUILD_ROOT%{_bindir}/js187

%{__mv} $RPM_BUILD_ROOT%{_bindir}/js-config $RPM_BUILD_ROOT%{_bindir}/js187-config

# fix symlinks pointing to buildroot
ln -sf libmozjs187.so.1.0 $RPM_BUILD_ROOT%{_libdir}/libmozjs187.so
ln -sf libmozjs187.so.1.0.0 $RPM_BUILD_ROOT%{_libdir}/libmozjs187.so.1.0

%if %{with default_js}
# provide symlinks as default js implementation
# (don't provide libjs.so.1 as the libraries are not binary-compatible)
ln -sf libmozjs187.so $RPM_BUILD_ROOT%{_libdir}/libjs.so
ln -sf libmozjs187-1.0.a $RPM_BUILD_ROOT%{_libdir}/libjs.a
ln -sf js187 $RPM_BUILD_ROOT%{_includedir}/js
ln -sf js187 $RPM_BUILD_ROOT%{_bindir}/js
ln -sf js187-config $RPM_BUILD_ROOT%{_bindir}/js-config
%else
%{__sed} -i -e 's,/js$,/js187,' $RPM_BUILD_ROOT%{_pkgconfigdir}/mozjs187.pc
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%if %{with default_js}
%pretrans devel
if [ -d %{_includedir}/js ] && [ ! -L %{_includedir}/js ]; then
	rm -rf /usr/include/js
fi
%endif

%files
%defattr(644,root,root,755)
%doc js/src/README.html
%attr(755,root,root) %{_bindir}/js187
%if %{with default_js}
%attr(755,root,root) %{_bindir}/js
%endif

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libmozjs187.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libmozjs187.so.1.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/js187-config
%attr(755,root,root) %{_libdir}/libmozjs187.so
%{_includedir}/js187
%{_pkgconfigdir}/mozjs187.pc
%if %{with default_js}
%attr(755,root,root) %{_bindir}/js-config
%attr(755,root,root) %{_libdir}/libjs.so
%{_includedir}/js
%endif

%files static
%defattr(644,root,root,755)
%{_libdir}/libmozjs187-1.0.a
%if %{with default_js}
%{_libdir}/libjs.a
%endif
