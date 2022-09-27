Name:           fonts-compare
Version:        1.0.1
Release:        1%{?dist}
Summary:        fonts rendering and comparing

License:        GPLv3
URL:            https://github.com/sudipshil9862/fonts-compare
Source0:        https://github.com/sudipshil9862/fonts-compare/archive/refs/tags/%{version}.tar.gz#/fonts-compare-%{version}.tar.gz

BuildArch: noarch

BuildRequires:  python3-devel
Requires: python3-gobject
Requires: python3-langtable
Requires: python3-langdetect

%description
Needed to compare fonts with various langugages
Summary: needed to compare fonts with various langugages



%prep
%setup


%build


%install
/usr/bin/install -m 755 fonts-compare %{buildroot}/%{bindir}/fonts-compare
/usr/bin/install -D -m 644 fonts_compare.py %{buildroot}/%{datadir}/fonts-compare/fonts_compare.py

%check

%files
%doc README.md
%license LICENSE
%{bindir}/fonts-compare
%{datadir}/fonts-compare/fonts_compare.py

%changelog
* Tue Sep 27 2022 Sudip Shil <sshil@redhat.com> - 1.0.1-1
- updated version 1.0.1-1

* Fri Sep 23 2022 Sudip Shil <sshil@redhat.com> - 1.0.0-1
- Initial RPM release
