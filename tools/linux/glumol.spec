Name:           glumol
Version:        1.0
Release:        1%{?dist}
Summary:        Glumol is an adventure game creator

Group:          Development/Libraries
License:        GPL
URL:            http://www.glumol.com
Source0:        http://www.glumol.com/releases/glumol-1.0.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  stackless-devel ClanLib-devel
Requires:       stackless ClanLib

%description
Glumol provides a framework and IDE to create adventure game, like the LucasArts ones.
Glumol is written in Python / C++, using the Clanlib library.

%prep
%setup -q


%build
%configure
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc



%changelog
