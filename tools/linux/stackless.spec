%define _prefix /usr/local
%define pyver 2.5

Name:           stackless
Version:        2.5.2
Release:        1%{?dist}
Summary:        Stackless Python is an enhanced version of the Python programming language.

Group:          Development/Languages
License:        Python Software Foundation License v2
URL:            http://www.stackless.com/
Source0:        http://www.stackless.com/binaries/stackless-252-export.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  readline-devel, openssl-devel, gmp-devel
Requires:       readline, openssl, gmp

%description
It allows programmers to reap the benefits of thread-based
programming without the performance and complexity
problems associated with conventional threads. The
microthreads that Stackless adds to Python are a cheap and
lightweight convenience which can if used properly, give the
following benefits:

    * Improved program structure.
    * More readable code.
    * Increased programmer productivity.

%package devel
Summary: The libraries and header files needed for the stackless version of Python development.
Group: Development/Libraries
Requires: stackless = %{version}-%{release}

%description devel
The stackless version of Python programming language's interpreter
can be extended with dynamically loaded extensions and can be
embedded in other programs. This package contains the header
files and libraries needed to do these types of tasks.

Install stackless-devel if you want to develop Stackless Python extensions.
The python package will also need to be installed.  You'll probably also
want to install the python-docs package, which contains Python
documentation.

%prep
%setup -n stackless-2.52


%build
./configure --prefix=%{_prefix} --enable-unicode=ucs4 --enable-ipv6
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
/usr/local/bin/python%{pyver}
/usr/local/bin/python-config
/usr/local/bin/smtpd.py*
/usr/local/bin/idle
/usr/local/bin/python
/usr/local/bin/pydoc
/usr/local/bin/python%{pyver}-config
/usr/local/share/man/man1/python.1

/usr/local/lib/python%{pyver}

%files devel
/usr/local/include/python%{pyver}

%changelog
