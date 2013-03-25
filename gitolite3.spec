%global perl_vendorlib %(eval $(perl -V:vendorlib); echo $vendorlib)
# RHEL uses %%{_prefix}/com for %%{_sharedstatedir} instead of /var/lib
%if 0%{?rhel}
%global gitolite_homedir /var/lib/%{name}
%else
%global gitolite_homedir %{_sharedstatedir}/%{name}
%endif

Name:           gitolite3
Epoch:          1
Version:        3.5
Release:        1%{?dist}
Summary:        Highly flexible server for git directory version tracker

Group:          Applications/System
License:        GPLv2 and CC-BY-SA
URL:            http://github.com/sitaramc/gitolite
Source0:        gitolite-3.5.tar.gz
Source1:        gitolite3-README-fedora
#Patch0:         0001-security-fix-bug-in-pattern-to-detect-path-traversal.patch

BuildArch:      noarch
Provides:       perl(%{name}) = %{version}-%{release}
Requires:       git
Requires:       openssh-clients
Requires:       perl(:MODULE_COMPAT_%(eval $(%{__perl} -V:version); echo $version))
Requires(pre):  shadow-utils
Requires:       subversion

%description
Gitolite allows a server to host many git repositories and provide access
to many developers, without having to give them real userids on the server.
The essential magic in doing this is ssh's pubkey access and the authorized
keys file, and the inspiration was an older program called gitosis.

Gitolite can restrict who can read from (clone/fetch) or write to (push) a
repository. It can also restrict who can push to what branch or tag, which
is very important in a corporate environment. Gitolite can be installed
without requiring root permissions, and with no additional software than git
itself and perl. It also has several other neat features described below and
elsewhere in the doc/ directory.


%prep
%setup -qn gitolite-%{version}
cp %{SOURCE1} .

#%patch0 -p1

%build
#This page intentionally left blank.

%install
rm -rf $RPM_BUILD_ROOT

# Directory structure
install -d $RPM_BUILD_ROOT%{gitolite_homedir}
install -d $RPM_BUILD_ROOT%{gitolite_homedir}/.ssh
install -d $RPM_BUILD_ROOT%{_bindir}
install -d $RPM_BUILD_ROOT%{perl_vendorlib}
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}

# Code
cp -pr src/lib/Gitolite $RPM_BUILD_ROOT%{perl_vendorlib}
echo "%{version}-%{release}" >src/VERSION
cp -a src/* $RPM_BUILD_ROOT%{_datadir}/%{name}
ln -s %{_datadir}/%{name}/gitolite $RPM_BUILD_ROOT%{_bindir}/gitolite

# empty authorized_keys file
touch $RPM_BUILD_ROOT%{gitolite_homedir}/.ssh/authorized_keys


%pre
# Add "gitolite" user per https://fedoraproject.org/wiki/Packaging:UsersAndGroups
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
useradd -r -g %{name} -d %{gitolite_homedir} -s /bin/sh \
        -c "git repository hosting" %{name}
exit 0


%files
%{_bindir}/*
%{perl_vendorlib}/*
%{_datadir}/%{name}
# make homedir non world readable
%attr(750,%{name},%{name}) %dir %{gitolite_homedir}
%attr(750,%{name},%{name}) %dir %{gitolite_homedir}/.ssh
%config(noreplace) %attr(640,%{name},%{name}) %{gitolite_homedir}/.ssh/authorized_keys
%doc gitolite3-README-fedora COPYING README.txt CHANGELOG


%changelog
* Mon Mar 25 2013 Jon Ciesla <limburgher@gmail.com> - 1:3.5-1
- Latest upstream.

* Tue Mar 05 2013 Jon Ciesla <limburgher@gmail.com> - 1:3.4-1
- Latest upstream.

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jan 03 2013 Jon Ciesla <limburgher@gmail.com> - 1:3.3-1
- Latest upstream.

* Mon Nov 19 2012 Jon Ciesla <limburgher@gmail.com> - 1:3.2-1
- Latest upstream.

* Wed Oct 10 2012 Jon Ciesla <limburgher@gmail.com> - 1:3.1-1
- 3.1, rewuiring Epoch bump.

* Tue Oct 09 2012 Jon Ciesla <limburgher@gmail.com> - 3.04-4
- Patch for directory traversal bug.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.04-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jun 28 2012 Petr Pisar <ppisar@redhat.com> - 3.04-2
- Perl 5.16 rebuild

* Wed Jun 27 2012 Jon Ciesla <limburgher@gmail.com> - 3.04-1
- Latest upstream, docs now includable.

* Thu Jun 07 2012 Petr Pisar <ppisar@redhat.com> - 3.03-3
- Perl 5.16 rebuild

* Thu Jun 07 2012 Petr Pisar <ppisar@redhat.com> - 3.03-2
- Perl 5.16 rebuild

* Wed May 23 2012 Jon Ciesla <limburgher@gmail.com> - 3.03-1
- Latest upstream.

* Mon May 21 2012 Jon Ciesla <limburgher@gmail.com> - 3.02-1
- Latest upstream.

* Tue May 15 2012 Jon Ciesla <limburgher@gmail.com> - 3.01-2
- Added license file, fixed duplicate files, dropped defattr.
- Dropped clean and buildroot.
- Added script to generate tarball in comments.

* Thu May 03 2012 Jon Ciesla <limburgher@gmail.com> - 3.01-1
- Initial packaging based on gitolite 2.3-2.
