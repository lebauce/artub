Name:           poujol
Version:        1.0
Release:        1%{?dist}
Summary:        Poujol is the Glumol runtime library.

Group:          System Environment/Libraries
License:        GPL
URL:            http://www.glumol.com
Source0:        poujol-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  ClanLib-devel /usr/bin/bjam boost-devel graphviz-devel
Requires:       ClanLib boost

%description
Poujol is the Glumol runtime library.

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%setup -q


%build
BOOST_BUILD_PATH=/home/bob/dev/boost_1_35_0
bjam toolset=gcc variant=release

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
%doc
%{_libdir}/*.so.*

%files devel
%defattr(-,root,root,-)
%doc
%{_includedir}/*
%{_libdir}/*.so


%changelog
