%define svn_revision r247

Name:           psdparse
Version:        0.1
Release:        1.0.svn%{svn_revision}%{?dist}
Summary:        PSD file parser

Group:          System Environment/Libraries
License:        GPLv2
URL:            http://www.telegraphics.com.au/sw/#psdparse
Source0:        psdparse-r247.tar.gz
Patch0:         psdparse-locale.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libpng-devel glibc-headers
Requires:       glibc

%description
This utility parses and prints a description of various structures
inside an Adobe Photoshop(TM) PSD or PSB format file.
It can optionally extract raster layers and spot/alpha channels to PNG files.


%prep
%setup -q -n psdparse-1.0
%patch0 -p1

%build
%configure --disable-static CFLAGS=-D_GNU_SOURCE
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'


%clean
rm -rf $RPM_BUILD_ROOT


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc README.txt INSTALL
%{_bindir}/psdparse

%changelog
* Wed Aug 6 2008 Sylvain Baubeau <bob@glumol.com> 0.1-1.0.svnr247
- Initial packaging for Fedora
