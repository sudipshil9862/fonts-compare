Name:           fonts-compare
Version:        1.0.0
Release:        1%{?dist}
Summary:        fonts rendering and comparing

License:        GPLv3
URL:            https://github.com/sudipshil9862/fonts_compare
Source0:        https://github.com/sudipshil9862/fonts_compare/archive/refs/tags/1.0.0.tar.gz#/fonts-compare-1.0.0.tar.gz

BuildArch: noarch

BuildRequires:  python3-devel
Requires: langtable

%description
Needed to compare fonts with various langugages
Summary: needed to compare fonts with various langugages



%prep
%setup -n fonts_compare-1.0.0


%build


%install
/usr/bin/install -D -m 644 fonts_compare.py %{buildroot}/usr/share/fonts-compare/fonts_compare.py


%check


%files
%doc README.md
%license LICENSE
/usr/share/fonts-compare/fonts_compare.py

%changelog
* Fri Sep 23 2019 Sudip Shil <sshil@redhat.com> - 1.0.0-1
- Initial RPM release
