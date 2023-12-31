Name:           augeas
Version:        1.12.0
Release:        8%{?dist}
Summary:        A library for changing configuration files

Group:          System Environment/Libraries
License:        LGPLv2+
URL:            http://augeas.net/
Source0:        http://download.augeas.net/%{name}-%{version}.tar.gz

# Patches are stored here:
# https://github.com/rwmjones/augeas/tree/rhel-8.8

Patch1:         0001-Grub-support-in-kernel-command-line-option-names-647.patch
Patch2:         0002-Rsyslog-support-multiple-actions-in-filters-and-sele.patch
Patch3:         0003-src-augrun.c-nexttoken-add-more-escape-characters.patch
Patch4:         0004-src-augtool.c-hopefully-fix-readline-quoting-issues.patch
Patch5:         0005-Krb5-improve-dbmodules-and-includes-630.patch
Patch6:         0006-Systemd-fix-parsing-of-envvars-with-spaces-659.patch
Patch7:         0007-Ssh-add-Match-keyword-support-695.patch
Patch8:         0008-Include-mke2fs-lens-and-test-from-upstream.patch
Patch9:         0009-semanage-Fix-parsing-of-ignoredirs-758.patch

BuildRequires:  readline-devel libselinux-devel libxml2-devel
BuildRequires:  autoconf, automake
Requires:       %{name}-libs = %{version}-%{release}

%description
A library for programmatically editing configuration files. Augeas parses
configuration files into a tree structure, which it exposes through its
public API. Changes made through the API are written back to the initially
read files.

The transformation works very hard to preserve comments and formatting
details. It is controlled by ``lens'' definitions that describe the file
format and the transformation into a tree.

%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name}-libs = %{version}-%{release}
Requires:       pkgconfig

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package        libs
Summary:        Libraries for %{name}
Group:          System Environment/Libraries

Provides:       bundled(gnulib)

%description    libs
The libraries for %{name}.

Augeas is a library for programmatically editing configuration files. It parses
configuration files into a tree structure, which it exposes through its
public API. Changes made through the API are written back to the initially
read files.



%prep
%autosetup -p1

%build
%configure \
%ifarch riscv64
    --disable-gnulib-tests \
%endif
    --disable-static
make V=1 %{?_smp_mflags}

%check
# Disable test-preserve.sh SELinux testing. This fails when run under mock due
# to differing SELinux labelling.
export SKIP_TEST_PRESERVE_SELINUX=1

make %{?_smp_mflags} check || {
  echo '===== tests/test-suite.log ====='
  cat tests/test-suite.log
  exit 1
}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT INSTALL="%{__install} -p"
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

# The tests/ subdirectory contains lenses used only for testing, and
# so it shouldn't be packaged.
rm -r $RPM_BUILD_ROOT%{_datadir}/augeas/lenses/dist/tests

%clean
rm -rf $RPM_BUILD_ROOT

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%{_bindir}/augmatch
%{_bindir}/augparse
%{_bindir}/augtool
%{_bindir}/fadot
%doc %{_mandir}/man1/*
%{_datadir}/vim/vimfiles/syntax/augeas.vim
%{_datadir}/vim/vimfiles/ftdetect/augeas.vim

%files libs
%defattr(-,root,root,-)
# _datadir/augeas and _datadir/augeas/lenses are owned
# by filesystem.
%{_datadir}/augeas/lenses/dist
%{_libdir}/*.so.*
%doc AUTHORS COPYING NEWS

%files devel
%defattr(-,root,root,-)
%doc
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/augeas.pc

%changelog
* Wed Oct 12 2022 Richard W.M. Jones <rjones@redhat.com> - 1.12.0-8
- Fix parsing of semanage.conf ignoredirs
  resolves: rhbz#1931058

* Wed Jan 12 2022 Richard W.M. Jones <rjones@redhat.com> - 1.12.0-7
- Fix parsing of mke2fs.conf files
  resolves: rhbz#1807010

* Tue Jan 05 2021 Pino Toscano <ptoscano@redhat.com> - 1.12.0-6
- Ssh: parse Match options (RHBZ#1716359)

* Mon Feb 10 2020 Pino Toscano <ptoscano@redhat.com> - 1.12.0-5
- Fix completion with special characters in augtool. (RHBZ#1232224)
- Krb5: improve handling of [dbmodules]; allow include/includedir directives
  everywhere (RHBZ#1798486)
- Systemd: improve parsing of quoted variables of Environment (RHBZ#1798922)

* Thu Nov 14 2019 Pino Toscano <ptoscano@redhat.com> - 1.12.0-4
- Rsyslog: support multiple actions in filters and selectors (RHBZ#1660884)

* Thu Nov 07 2019 Pino Toscano <ptoscano@redhat.com> - 1.12.0-3
- Grub: handle '+' in kernel command line options (RHBZ#1769314)

* Mon Jun 03 2019 Pino Toscano <ptoscano@redhat.com> - 1.12.0-2
- Disable static libraries, not needed in RHEL.

* Tue May 14 2019 Pino Toscano <ptoscano@redhat.com> - 1.12.0-1
- New upstream release (RHBZ#1709416)
  * Fstab: allow leading whitespaces (RHBZ#1671950)

* Thu Dec 13 2018 Pino Toscano <ptoscano@redhat.com> - 1.10.1-8
- Add simple tests (RHBZ#1653994)

* Wed Dec 12 2018 Pino Toscano <ptoscano@redhat.com> - 1.10.1-7
- Anaconda: new lens (RHBZ#1657192)

* Thu Nov 29 2018 Pino Toscano <ptoscano@redhat.com> - 1.10.1-6
- Semanage: new lens (RHBZ#1652840)
- Add "Provides: bundled(gnulib)" to augeas-libs, as it embeds gnulib
  (RHBZ#1653768)

* Fri Nov 23 2018 Pino Toscano <ptoscano@redhat.com> - 1.10.1-5
- Rsyslog: support include() directive (RHBZ#1652832)

* Tue Nov 13 2018 Pino Toscano <ptoscano@redhat.com> - 1.10.1-4
- Grub: better handle invalid grub.conf files (RHBZ#1649262)
- Sudoers: handle "always_query_group_plugin" option (RHBZ#1649299)

* Mon Oct 08 2018 Pino Toscano <ptoscano@redhat.com> - 1.10.1-3
- Backport some upstream commits to fix few memory leaks, and potential
  memory issues (RHBZ#1602446)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.10.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Jan 29 2018 David Lutterkort <lutter@watzmann.net> - 1.10.1-1
- New upstream version 1.10.1

* Fri Jan 26 2018 Richard W.M. Jones <rjones@redhat.com> - 1.10.0-1
- New upstream version 1.10.0 (RHBZ#1538846).
- Remove upstream patch.
- New tool ‘augmatch’.

* Tue Nov 21 2017 David Lutterkort <lutter@watzmann.net> - 1.9.0
- New upstream version 1.9.0 (RHBZ#1482713)
- Add -static subpackage (RHBZ#1405600)

* Thu Aug 24 2017 Richard W.M. Jones <rjones@redhat.com> - 1.8.1-1
- New upstream version 1.8.1.
- Fixes CVE-2017-7555 (RHBZ#1482340).

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Mar 21 2017 Dominic Cleal <dominic@cleal.org> - 1.8.0-1
- Update to 1.8.0

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.7.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 12 2017 Igor Gnatenko <ignatenko@redhat.com> - 1.7.0-3
- Rebuild for readline 7.x

* Sat Nov 12 2016 Richard W.M. Jones <rjones@redhat.com> - 1.7.0-2
- riscv64: Disable gnulib tests on riscv64 architecture.

* Wed Nov 09 2016 Dominic Cleal <dominic@cleal.org> - 1.7.0-1
- Update to 1.7.0

* Mon Aug 08 2016 Dominic Cleal <dominic@cleal.org> - 1.6.0-1
- Update to 1.6.0

* Thu May 12 2016 Dominic Cleal <dominic@cleal.org> - 1.5.0-1
- Update to 1.5.0

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.4.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Jun 02 2015 Dominic Cleal <dcleal@redhat.com> - 1.4.0-1
- Update to 1.4.0

* Sat Nov 08 2014 Dominic Cleal <dcleal@redhat.com> - 1.3.0-1
- Update to 1.3.0; remove all patches

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Mar 31 2014 Dominic Cleal <dcleal@redhat.com> - 1.2.0-2
- Add patch for Krb5, parse braces in values (RHBZ#1079444)

* Wed Feb 12 2014 Dominic Cleal <dcleal@redhat.com> - 1.2.0-1
- Update to 1.2.0, add check section
- Update source URL to download.augeas.net (RHBZ#996032)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jun 19 2013 David Lutterkort <lutter@redhat.com> - 1.1.0-1
- Update to 1.1.0; remove all patches

* Tue Jun 18 2013 Richard W.M. Jones <rjones@redhat.com> - 1.0.0-4
- Fix /etc/sysconfig/network (RHBZ#904222).

* Wed Jun  5 2013 Richard W.M. Jones <rjones@redhat.com> - 1.0.0-3
- Don't package lenses in tests/ subdirectory.

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jan  4 2013 David Lutterkort <lutter@redhat.com> - 1.0.0-1
- New version; remove all patches

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jan 10 2012 David Lutterkort <lutter@redhat.com> - 0.10.0-3
- Add patches for bugs 247 and 248 (JSON lens)

* Sat Dec  3 2011 Richard W.M. Jones <rjones@redhat.com> - 0.10.0-2
- Add patch to resolve missing libxml2 requirement in augeas.pc.

* Fri Dec  2 2011 David Lutterkort <lutter@redhat.com> - 0.10.0-1
- New version

* Mon Jul 25 2011 David Lutterkort <lutter@redhat.com> - 0.9.0-1
- New version; removed patch pathx-whitespace-ea010d8

* Tue May  3 2011 David Lutterkort <lutter@redhat.com> - 0.8.1-2
- Add patch pathx-whitespace-ea010d8.patch to fix BZ 700608

* Fri Apr 15 2011 David Lutterkort <lutter@redhat.com> - 0.8.1-1
- New version

* Wed Feb 23 2011 David Lutterkort <lutter@redhat.com> - 0.8.0-1
- New version

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Nov 22 2010 Matthew Booth <mbooth@redhat.com> - 0.7.4-1
- Update to version 0.7.4

* Thu Nov 18 2010 Richard W.M. Jones <rjones@redhat.com> - 0.7.3-2
- Upstream patch proposed to fix GCC optimization bug (RHBZ#651992).

* Fri Aug  6 2010 David Lutterkort <lutter@redhat.com> - 0.7.3-1
- Remove upstream patches

* Tue Jun 29 2010 David Lutterkort <lutter@redhat.com> - 0.7.2-2
- Patches based on upstream fix for BZ 600141

* Tue Jun 22 2010 David Lutterkort <lutter@redhat.com> - 0.7.2-1
- Fix ownership of /usr/share/augeas. BZ 569393

* Wed Apr 21 2010 David Lutterkort <lutter@redhat.com> - 0.7.1-1
- New version

* Thu Jan 14 2010 David Lutterkort <lutter@redhat.com> - 0.7.0-1
- Remove patch vim-ftdetect-syntax.patch. It's upstream

* Tue Dec 15 2009 David Lutterkort <lutter@redhat.com> - 0.6.0-2
- Fix ftdetect file for vim

* Mon Nov 30 2009 David Lutterkort <lutter@redhat.com> - 0.6.0-1
- Install vim syntax files

* Mon Sep 14 2009 David Lutterkort <lutter@redhat.com> - 0.5.3-1
- Remove separate xorg.aug, included in upstream source

* Tue Aug 25 2009 Matthew Booth <mbooth@redhat.com> - 0.5.2-3
- Include new xorg lens from upstream

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 13 2009 David Lutterkort <lutter@redhat.com> - 0.5.2-1
- New version

* Fri Jun  5 2009 David Lutterkort <lutter@redhat.com> - 0.5.1-1
- Install fadot

* Fri Mar 27 2009 David Lutterkort <lutter@redhat.com> - 0.5.0-2
- fadot isn't being installed just yet

* Tue Mar 24 2009 David Lutterkort <lutter@redhat.com> - 0.5.0-1
- New program /usr/bin/fadot

* Mon Mar  9 2009 David Lutterkort <lutter@redhat.com> - 0.4.2-1
- New version

* Fri Feb 27 2009 David Lutterkort <lutter@redhat.com> - 0.4.1-1
- New version

* Fri Feb  6 2009 David Lutterkort <lutter@redhat.com> - 0.4.0-1
- New version

* Mon Jan 26 2009 David Lutterkort <lutter@redhat.com> - 0.3.6-1
- New version

* Tue Dec 23 2008 David Lutterkort <lutter@redhat.com> - 0.3.5-1
- New version

* Mon Feb 25 2008 David Lutterkort <dlutter@redhat.com> - 0.0.4-1
- Initial specfile
