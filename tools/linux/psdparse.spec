Name:           psdparse
Version:        1.0
Release:        1%{?dist}
Summary:        PSD file parser

Group:          System Environment/Libraries
License:        GPL
URL:            http://www.telegraphics.com.au/sw/#psdparse
Source0:        psdparse-1.0.tar.gz
Patch0:		psdparse-locale.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libpng-devel glibc-headers
Requires:       libpng glibc

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
