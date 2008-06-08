Name:           artub
Version:        1.0
Release:        1%{?dist}
Summary:        Artub is the GUI for the Glumol engine
BuildArch:      noarch

Group:          Applications/Editors
License:        GPV
URL:            http://www.glumol.com
Source0:        artub-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:       stackless wxPython numpy PyOpenGL poujol

%description
Artub is the GUI for the Glumol engine

%prep
%setup -q


%build
# make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
# make install DESTDIR=$RPM_BUILD_ROOT
mkdir -p ${RPM_BUILD_ROOT}/%{_datadir}/%{name}
cp -R * ${RPM_BUILD_ROOT}/%{_datadir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc COPYING
/usr/share/artub


%changelog
