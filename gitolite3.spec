%global perl_vendorlib %(eval $(perl -V:vendorlib); echo $vendorlib)
# RHEL uses %%{_prefix}/com for %%{_sharedstatedir} instead of /var/lib
%if 0%{?rhel}
%global gitolite_homedir /var/lib/%{name}
%else
%global gitolite_homedir %{_sharedstatedir}/%{name}
%endif
%global gitolite_sharedir %{_datadir}/%{name}
%global gitolite_suexec_bin %{_localstatedir}/www/gitolite-bin
%global apache_root %{_sysconfdir}/httpd

Name:           gitolite3
Epoch:          1
Version:        3.6.5
Release:        4%{?dist}
Summary:        Highly flexible server for git directory version tracker

Group:          Applications/System
License:        GPLv2 and CC-BY-SA
URL:            http://github.com/sitaramc/gitolite
Source0:        https://github.com/sitaramc/gitolite/archive/v%{version}.tar.gz
Source1:        gitolite3-README-fedora
Source2:        gitolite.conf.inactive
Source3:        gitolite-gitweb.conf.inactive
Source4:        gitweb.conf.gitolite
Source5:        gitolite-suexec-wrapper.sh
Source6:        gitweb-suexec-wrapper.sh
#Patch0:         0001-security-fix-bug-in-pattern-to-detect-path-traversal.patch

BuildArch:      noarch
BuildRequires:      perl-generators
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
install -d $RPM_BUILD_ROOT%{gitolite_suexec_bin}
install -d $RPM_BUILD_ROOT%{apache_root}/conf.d

# Code
cp -pr src/lib/Gitolite $RPM_BUILD_ROOT%{perl_vendorlib}
echo "%{version}-%{release}" >src/VERSION
cp -a src/* $RPM_BUILD_ROOT%{_datadir}/%{name}
ln -s %{_datadir}/%{name}/gitolite $RPM_BUILD_ROOT%{_bindir}/gitolite

# empty authorized_keys file
touch $RPM_BUILD_ROOT%{gitolite_homedir}/.ssh/authorized_keys

# Install suexec-scripts
sed -e "s:@@GITOLITE_HOMEDIR@@:%{gitolite_homedir}:g
	s:@@GITOLITE_SHELL@@:%{_datadir}/%{name}/gitolite-shell:g" %{SOURCE5} > gitolite-suexec-wrapper.sh
sed -e "s:@@GITOLITE_HOMEDIR@@:%{gitolite_homedir}:g
	s:@@GITWEB@@:%{_localstatedir}/www/git/gitweb.cgi:g" %{SOURCE6} > gitweb-suexec-wrapper.sh
install -Dp -m 700 gitolite-suexec-wrapper.sh %{buildroot}/%{gitolite_suexec_bin}/
install -Dp -m 700 gitweb-suexec-wrapper.sh %{buildroot}/%{gitolite_suexec_bin}/

# Apache-Config
sed -e "s:@@NAME@@:%{name}:g
	s:@@GITOLITE_SUEXEC_BIN@@:%{gitolite_suexec_bin}:g" %{SOURCE2} > gitolite.conf.inactive
sed -e "s:@@NAME@@:%{name}:g
	s:@@GITOLITE_SUEXEC_BIN@@:%{gitolite_suexec_bin}:g" %{SOURCE3} > gitolite-gitweb.conf.inactive
install -Dp -m 644 gitolite.conf.inactive %{buildroot}/%{apache_root}/conf.d/
install -Dp -m 644 gitolite-gitweb.conf.inactive %{buildroot}/%{apache_root}/conf.d/

# Gitweb-Gitolite-Config
sed -e "s:@@GITOLITE_HOMEDIR@@:%{gitolite_homedir}:g
	s:@@GITOLITE_SHAREDIR@@:%{gitolite_sharedir}:g" %{SOURCE4} > gitweb.conf.gitolite
install -Dp -m 644 gitweb.conf.gitolite %{buildroot}/%{_sysconfdir}/

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
%attr(755,%{name},%{name}) %dir %{gitolite_suexec_bin}
%config(noreplace) %attr(700,%{name},%{name}) %{gitolite_suexec_bin}/gitolite-suexec-wrapper.sh
%config(noreplace) %attr(700,%{name},%{name}) %{gitolite_suexec_bin}/gitweb-suexec-wrapper.sh
%attr(755,root,root) %dir %{apache_root}/conf.d
%config(noreplace) %attr(644,root,root) %{apache_root}/conf.d/gitolite.conf.inactive
%config(noreplace) %attr(644,root,root) %{apache_root}/conf.d/gitolite-gitweb.conf.inactive
%config(noreplace) %attr(644,root,root) %{_sysconfdir}/gitweb.conf.gitolite
%doc gitolite3-README-fedora COPYING README.markdown CHANGELOG


%changelog
* Fri Aug 19 2016 Alex Pircher <Alexander_Pircher@yahoo.de> 1:3.6.5-4
- Apache-configs and suEXEC-wrappers for HTTP(S) based authentication and
  for usage in combination with GitWeb

* Sun May 15 2016 Jitka Plesnikova <jplesnik@redhat.com> - 1:3.6.5-3
- Perl 5.24 rebuild

* Mon Feb 22 2016 Jon Ciesla <limburgher@gmail.com> - 1:3.6.5-1
- Latest upstream.

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:3.6.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Nov 03 2015 Jon Ciesla <limburgher@gmail.com> - 1:3.6.4-1
- Latest upstream.

* Thu Oct 8 2015 François Cami <fcami@fedoraproject.org> - 1:3.6.3-4
- Fix instructions in README.fedora:
-  gitolite user => gitolite3 user
-  switch setup from -a to -pk (ssh keys) 

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.6.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Jun 03 2015 Jitka Plesnikova <jplesnik@redhat.com> - 1:3.6.3-2
- Perl 5.22 rebuild

* Sun Apr 26 2015 Jon Ciesla <limburgher@gmail.com> - 1:3.6.3-1
- Latest upstream.

* Mon Nov 10 2014 Jon Ciesla <limburgher@gmail.com> - 1:3.6.2-1
- Latest upstream.

* Tue Aug 26 2014 Jitka Plesnikova <jplesnik@redhat.com> - 1:3.6.1-2
- Perl 5.20 rebuild

* Mon Jun 23 2014 Jon Ciesla <limburgher@gmail.com> - 1:3.6.1-1
- Latest upstream.

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon May 12 2014 Jon Ciesla <limburgher@gmail.com> - 1:3.6-1
- Latest upstream.

* Wed Oct 23 2013 Jon Ciesla <limburgher@gmail.com> - 1:3.5.3.1-1
- Latest upstream.

* Wed Oct 16 2013 Jon Ciesla <limburgher@gmail.com> - 1:3.5.3-1
- Latest upstream.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:3.5.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 1:3.5.2-2
- Perl 5.18 rebuild

* Wed Jul 10 2013 Jon Ciesla <limburgher@gmail.com> - 1:3.5.2-1
- Latest upstream.

* Thu Mar 28 2013 Jon Ciesla <limburgher@gmail.com> - 1:3.5.1-1
- Latest upstream.

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
