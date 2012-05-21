%global perl_vendorlib %(eval $(perl -V:vendorlib); echo $vendorlib)
# RHEL uses %%{_prefix}/com for %%{_sharedstatedir} instead of /var/lib
%if 0%{?rhel}
%global gitolite_homedir /var/lib/%{name}
%else
%global gitolite_homedir %{_sharedstatedir}/%{name}
%endif

Name:           gitolite3
Version:        3.02
Release:        1%{?dist}
Summary:        Highly flexible server for git directory version tracker

Group:          Applications/System
License:        GPLv2
URL:            http://github.com/sitaramc/gitolite
# The gitolite docs are licensed Creative Commons
# Attribution-NonCommercial-ShareAlike 3.0 Unported License,
# so we have to strip them from the tarball.
# tar -xzf sitaramc-gitolite-v3.01-0-g88b4c86.tar.gz
# rm -rf sitaramc-gitolite-06b56f4/doc/
# tar -czf sitaramc-gitolite-v3.01-0-g88b4c86-nodocs.tar.gz sitaramc-gitolite-06b56f4/
Source0:        sitaramc-gitolite-v3.02-0-g8aba6ec-nodocs.tar.gz
Source1:        gitolite3-README-fedora

BuildArch:      noarch
#BuildRequires:  perl(Text::Markdown)
# We provide the module, but don't create a package/name space
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
%setup -qn sitaramc-gitolite-eba8d03
cp %{SOURCE1} .


%build
## Format documentation
#for F in doc/*.mkd
#do
#        perl -MText::Markdown >$(echo $F |sed s/.mkd/.html/) <$F \
#                -e 'print Text::Markdown::markdown (join "", <>)'
#done


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
%doc gitolite3-README-fedora COPYING


%changelog
* Mon May 21 2012 Jon Ciesla <limburgher@gmail.com> - 3.02-1
- Latest upstream.

* Tue May 15 2012 Jon Ciesla <limburgher@gmail.com> - 3.01-2
- Added license file, fixed duplicate files, dropped defattr.
- Dropped clean and buildroot.
- Added script to generate tarball in comments.

* Thu May 03 2012 Jon Ciesla <limburgher@gmail.com> - 3.01-1
- Initial packaging based on gitolite 2.3-2.
