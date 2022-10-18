Name:           fonts-compare
Version:        1.0.2
Release:        2%{?dist}
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
install -D -m 755 fonts-compare %{buildroot}%{_bindir}/fonts-compare
install -D -m 644 fonts_compare.py %{buildroot}%{_datadir}/fonts-compare/fonts_compare.py

%check

%files
%doc README.md
%license LICENSE
%{_bindir}/fonts-compare
%{_datadir}/fonts-compare/fonts_compare.py

%changelog
* Tue Oct 18 2022 Sudip Shil <sshil@redhat.com> - 1.0.2-2
- fixed broken macros

* Sun Oct 16 2022 Sudip Shil <sshil@redhat.com> - 1.0.2-1
- updated version 1.0.2-1
- Bug 1 fixed: errors and warning removed - checked pylint, 
  pylintrc parameters updated for this project specificly
- Bug 2 fixed: If I type japanese text in gtkEntry then no font detected in font button
  https://github.com/sudipshil9862/fonts-compare/issues/3
- Bug 3 fixed: If click ‘bn’ then font button dialog has bengali text below 
  but not happening this for ‘ja’ -> showing some english text instead of japanese 
  https://github.com/sudipshil9862/fonts-compare/issues/2
- Bug 4 fixed: If I write japanese in gtkEntry field and then I select ‘bn’ from drop then everything changed 
  but the japanese text still there in gtkEntry
- Bug 5 fixed: When a language is detected by typing a text, 
  the combobox(drop-down) doesn’t change
  https://github.com/sudipshil9862/fonts-compare/issues/5
- Bug 6 fixed: code_rendering - detecting combo box lang using for loop and making it general 
  so that any language can be selected from drop-down if it’s there  (use dictionary)
- Bug 7 fixed: Text in the entry suddenly changes to sample text 
  for the detected language when typing into the entry
  https://github.com/sudipshil9862/fonts-compare/issues/6

* Tue Sep 27 2022 Sudip Shil <sshil@redhat.com> - 1.0.1-1
- updated version 1.0.1-1

* Fri Sep 23 2022 Sudip Shil <sshil@redhat.com> - 1.0.0-1
- Initial RPM release
