#
# Red Hat BIND package .spec file
#
# vim:expandtab ts=2:

#%%global PATCHVER P1
#%%global PREVER rc1
%global BINDVERSION %{version}%{?PREVER}%{?PATCHVER:-%{PATCHVER}}

# bcond_without is built by default, unless --without X is passed
# bcond_with is built only when --with X is passed to build
%bcond_with    SYSTEMTEST
%bcond_without GSSTSIG
# it is not possible to build the package without PKCS11 sub-package
# due to extensive changes to Makefiles
%bcond_without PKCS11
%bcond_without JSON
%bcond_without DLZ
# New MaxMind GeoLite support
%bcond_without GEOIP2
%if 0%{?fedora} >= 28
# Disabled temporarily until kyua is fixed on rawhide, bug #1926779
%bcond_with UNITTEST
%bcond_without DNSTAP
%bcond_without LMDB
%bcond_without DOC
%else
%bcond_with    UNITTEST
%bcond_with    DNSTAP
%bcond_with    LMDB
%bcond_with    DOC
%endif
# Because of issues with PDF rebuild, include only HTML pages
%bcond_with    DOCPDF
%bcond_with    TSAN

%{?!bind_uid:  %global bind_uid  25}
%{?!bind_gid:  %global bind_gid  25}
%{!?_pkgdocdir:%global _pkgdocdir %{_docdir}/%{name}-%{version}}
%global        bind_dir          /var/named
%global        chroot_prefix     %{bind_dir}/chroot
%global        chroot_create_directories /dev /run/named %{_localstatedir}/{log,named,tmp} \\\
                                         %{_sysconfdir}/{crypto-policies/back-ends,pki/dnssec-keys,named} \\\
                                         %{_libdir}/bind %{_libdir}/named %{_datadir}/GeoIP

%global        selinuxbooleans   named_write_master_zones=1
## The order of libs is important. See lib/Makefile.in for details
%define bind_export_libs isc dns isccfg irs
%{!?_export_dir:%global _export_dir /bind9-export/}
# libisc-nosym requires to be linked with unresolved symbols
# When libisc-nosym linking is fixed, it can be defined to 1
# Visit https://bugzilla.redhat.com/show_bug.cgi?id=1540300
%undefine _strict_symbol_defs_build
#
# significant changes:
# no more isc-config.sh and bind9-config
# lib*.so.X versions of selected libraries no longer provided,
# lib*-%%{version}-RH.so is provided as an internal implementation detail


Summary:  The Berkeley Internet Name Domain (BIND) DNS (Domain Name System) server
Name:     bind
License:  MPLv2.0
Version:  9.16.15
Release:  1%{?PATCHVER:.%{PATCHVER}}%{?PREVER:.%{PREVER}}%{?dist}
Epoch:    32
Url:      https://www.isc.org/downloads/bind/
#
Source0:  https://downloads.isc.org/isc/bind9/%{BINDVERSION}/bind-%{BINDVERSION}.tar.xz
Source1:  named.sysconfig
Source2:  https://downloads.isc.org/isc/bind9/%{BINDVERSION}/bind-%{BINDVERSION}.tar.xz.asc
Source3:  named.logrotate
Source4:  https://downloads.isc.org/isc/pgpkeys/codesign2021.txt
Source16: named.conf
# Refresh by command: dig @a.root-servers.net. +tcp +norec
# or from URL
Source17: https://www.internic.net/domain/named.root
Source18: named.localhost
Source19: named.loopback
Source20: named.empty
Source23: named.rfc1912.zones
Source25: named.conf.sample
Source27: named.root.key
Source35: bind.tmpfiles.d
Source36: trusted-key.key
Source37: named.service
Source38: named-chroot.service
Source41: setup-named-chroot.sh
Source42: generate-rndc-key.sh
Source43: named.rwtab
Source44: named-chroot-setup.service
Source46: named-setup-rndc.service
Source47: named-pkcs11.service
Source48: setup-named-softhsm.sh
Source49: named-chroot.files

# Common patches
Patch10: bind-9.5-PIE.patch
Patch16: bind-9.16-redhat_doc.patch
Patch72: bind-9.5-dlz-64bit.patch
Patch106:bind93-rh490837.patch
Patch112:bind97-rh645544.patch
Patch130:bind-9.9.1-P2-dlz-libdb.patch
Patch133:bind99-rh640538.patch
# Make PKCS11 used only for pkcs11 parts
Patch135:bind-9.14-config-pkcs11.patch
# Fedora specific patch to distribute native-pkcs#11 functionality
Patch136:bind-9.10-dist-native-pkcs11.patch
# Do not use isc-pkcs11.
Patch149:bind-9.11-kyua-pkcs11.patch

Patch140:bind-9.11-rh1410433.patch
Patch157:bind-9.11-fips-tests.patch
Patch164:bind-9.11-rh1666814.patch
Patch170:bind-9.11-feature-test-named.patch
Patch171:bind-9.11-tests-variants.patch

Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
Requires:       coreutils
Requires(pre):  shadow-utils
Requires(post): shadow-utils
Requires(post): glibc-common
Requires(post): grep
Requires:       bind-libs%{?_isa} = %{epoch}:%{version}-%{release}
# This wild require should satisfy %%selinux_set_boolean macro only
# in case it needs to be used
# selinux_set_booleans requires
Requires(post):      policycoreutils-python, libselinux-utils, selinux-policy
Requires(postun):    policycoreutils-python, libselinux-utils, selinux-policy
# Ensures at least one selinux-policy-X is installed when post is executed.
# Needed for selinux-policy-targeted to be already installed, but not requiring it explicitly
# Should be satisfied with selinux-policy-minimum if no selinux policy is used
Requires(post):      selinux-policy-base
Requires(postun):    selinux-policy-base
BuildRequires:  gcc, make
BuildRequires:  openssl-devel, libtool, autoconf, pkgconfig, libcap-devel
BuildRequires:  libidn2-devel, libxml2-devel
BuildRequires:  systemd
BuildRequires:  selinux-policy
# needed for %%{__python3} macro
BuildRequires:  python3-devel
BuildRequires:  python3-ply
BuildRequires:  findutils sed
%if 0%{?fedora}
BuildRequires:  gnupg2
%endif
BuildRequires:  libuv-devel
%if %{with DLZ}
BuildRequires:  openldap-devel, libpq-devel, sqlite-devel, mariadb-connector-c-devel
%endif
%if %{with UNITTEST}
# make unit dependencies
BuildRequires:  libcmocka-devel kyua
%endif
%if %{with PKCS11} && (%{with UNITTEST} || %{with SYSTEMTEST})
BuildRequires:  softhsm
%endif
%if %{with SYSTEMTEST}
# bin/tests/system dependencies
BuildRequires:  perl(Net::DNS) perl(Net::DNS::Nameserver) perl(Time::HiRes) perl(Getopt::Long)
# manual configuration requires this tool
BuildRequires:  iproute
%endif
%if %{with GSSTSIG}
BuildRequires:  krb5-devel
%endif
%if %{with LMDB}
BuildRequires:  lmdb-devel
%endif
%if %{with JSON}
BuildRequires:  json-c-devel
%endif
%if %{with GEOIP2}
BuildRequires:  libmaxminddb-devel
%endif
%if %{with DNSTAP}
BuildRequires:  fstrm-devel protobuf-c-devel
%endif
# Needed to regenerate dig.1 manpage
%if %{with DOC}
BuildRequires:  python3-sphinx python3-sphinx_rtd_theme
BuildRequires:  doxygen
%endif
%if %{with DOCPDF}
# Because remaining issues with COPR, allow turning off PDF (re)generation
BuildRequires:  python3-sphinx-latex latexmk texlive-xetex texlive-xindy
%endif
%if %{with TSAN}
BuildRequires: libtsan
%endif

%description
BIND (Berkeley Internet Name Domain) is an implementation of the DNS
(Domain Name System) protocols. BIND includes a DNS server (named),
which resolves host names to IP addresses; a resolver library
(routines for applications to use when interfacing with DNS); and
tools for verifying that the DNS server is operating properly.

%if %{with PKCS11}
%package pkcs11
Summary: Bind with native PKCS#11 functionality for crypto
Requires: systemd
Requires: bind%{?_isa} = %{epoch}:%{version}-%{release}
Requires: bind-libs%{?_isa} = %{epoch}:%{version}-%{release}
Requires: bind-pkcs11-libs%{?_isa} = %{epoch}:%{version}-%{release}

%description pkcs11
This is a version of BIND server built with native PKCS#11 functionality.
It is important to have SoftHSM v2+ installed and some token initialized.
For other supported HSM modules please check the BIND documentation.

%package pkcs11-utils
Summary: Bind tools with native PKCS#11 for using DNSSEC
Requires: bind-pkcs11-libs%{?_isa} = %{epoch}:%{version}-%{release}
Obsoletes: bind-pkcs11 < 32:9.9.4-16.P2
Requires: bind-dnssec-doc = %{epoch}:%{version}-%{release}

%description pkcs11-utils
This is a set of PKCS#11 utilities that when used together create rsa
keys in a PKCS11 keystore. Also utilities for working with DNSSEC
compiled with native PKCS#11 functionality are included.

%package pkcs11-libs
Summary: Bind libraries compiled with native PKCS#11
Requires: bind-license = %{epoch}:%{version}-%{release}
Requires: bind-libs%{?_isa} = %{epoch}:%{version}-%{release}

%description pkcs11-libs
This is a set of BIND libraries (dns, isc) compiled with native PKCS#11
functionality.

%package pkcs11-devel
Summary: Development files for Bind libraries compiled with native PKCS#11
Requires: bind-pkcs11-libs%{?_isa} = %{epoch}:%{version}-%{release}
Requires: bind-devel%{?_isa} = %{epoch}:%{version}-%{release}

%description pkcs11-devel
This a set of development files for BIND libraries (dns, isc) compiled
with native PKCS#11 functionality.
%endif

%package libs
Summary: Libraries used by the BIND DNS packages
Requires: bind-license = %{epoch}:%{version}-%{release}
Provides: bind-libs-lite = %{epoch}:%{version}-%{release}
Obsoletes: bind-libs-lite < 32:9.16.13

%description libs
Contains heavyweight version of BIND suite libraries used by both named DNS
server and utilities in bind-utils package.

%package license
Summary:  License of the BIND DNS suite
BuildArch:noarch

%description license
Contains license of the BIND DNS suite.

%package utils
Summary: Utilities for querying DNS name servers
Requires: bind-libs%{?_isa} = %{epoch}:%{version}-%{release}
# For compatibility with Debian package
Provides: dnsutils = %{epoch}:%{version}-%{release}

%description utils
Bind-utils contains a collection of utilities for querying DNS (Domain
Name System) name servers to find out information about Internet
hosts. These tools will provide you with the IP addresses for given
host names, as well as other information about registered domains and
network addresses.

You should install bind-utils if you need to get information from DNS name
servers.

%package dnssec-utils
Summary: DNSSEC keys and zones management utilities
Requires: bind-libs%{?_isa} = %{epoch}:%{version}-%{release}
Requires: python3-bind = %{epoch}:%{version}-%{release}
Requires: bind-dnssec-doc = %{epoch}:%{version}-%{release}

%description dnssec-utils
Bind-dnssec-utils contains a collection of utilities for editing
DNSSEC keys and BIND zone files. These tools provide generation,
revocation and verification of keys and DNSSEC signatures in zone files.

You should install bind-dnssec-utils if you need to sign a DNS zone
or maintain keys for it.

%package dnssec-doc
Summary: Manual pages of DNSSEC utilities
Requires: bind-license = %{epoch}:%{version}-%{release}
BuildArch:noarch

%description dnssec-doc
Bind-dnssec-doc contains manual pages for bind-dnssec-utils.

%package devel
Summary:  Header files and libraries needed for bind-dyndb-ldap
Provides: bind-lite-devel = %{epoch}:%{version}-%{release}
Obsoletes: bind-lite-devel < 32:9.16.6-3
Requires: bind-libs%{?_isa} = %{epoch}:%{version}-%{release}
Requires: openssl-devel%{?_isa} libxml2-devel%{?_isa}
Requires: libcap-devel%{?_isa}
%if %{with GSSTSIG}
Requires: krb5-devel%{?_isa}
%endif
%if %{with LMDB}
Requires: lmdb-devel%{?_isa}
%endif
%if %{with JSON}
Requires:  json-c-devel%{?_isa}
%endif
%if %{with DNSTAP}
Requires:  fstrm-devel%{?_isa} protobuf-c-devel%{?_isa}
%endif
%if %{with GEOIP2}
Requires:  libmaxminddb-devel%{?_isa}

%description devel
The bind-devel package contains full version of the header files and libraries
required for building bind-dyndb-ldap. Upstream no longer supports nor recommends
bind libraries for third party applications.
%endif

%package chroot
Summary:        A chroot runtime environment for the ISC BIND DNS server, named(8)
Prefix:         %{chroot_prefix}
# grep is required due to setup-named-chroot.sh script
Requires:       grep
Requires:       bind%{?_isa} = %{epoch}:%{version}-%{release}

%description chroot
This package contains a tree of files which can be used as a
chroot(2) jail for the named(8) program from the BIND package.
Based on the code from Jan "Yenya" Kasprzak <kas@fi.muni.cz>


%if %{with DLZ}
%package dlz-filesystem
Summary: BIND server filesystem DLZ module
Requires: bind%{?_isa} = %{epoch}:%{version}-%{release}

%description dlz-filesystem
Dynamic Loadable Zones filesystem module for BIND server.

%package dlz-ldap
Summary: BIND server ldap DLZ module
Requires: bind%{?_isa} = %{epoch}:%{version}-%{release}

%description dlz-ldap
Dynamic Loadable Zones LDAP module for BIND server.

%package dlz-mysql
Summary: BIND server mysql and mysqldyn DLZ modules
Requires: bind%{?_isa} = %{epoch}:%{version}-%{release}
Provides: %{name}-dlz-mysqldyn = %{epoch}:%{version}-%{release}
Obsoletes: %{name}-dlz-mysqldyn < 32:9.16.6-3

%description dlz-mysql
Dynamic Loadable Zones MySQL module for BIND server.
Contains also mysqldyn module with dynamic DNS updates (DDNS) support.

%package dlz-sqlite3
Summary: BIND server sqlite3 DLZ module
Requires: bind%{?_isa} = %{epoch}:%{version}-%{release}

%description dlz-sqlite3
Dynamic Loadable Zones sqlite3 module for BIND server.
%endif


%package -n python3-bind
Summary:   A module allowing rndc commands to be sent from Python programs
Requires:  bind-license = %{epoch}:%{version}-%{release}
Requires:  python3 python3-ply %{?py3_dist:%py3_dist ply}
BuildArch: noarch
%{?python_provide:%python_provide python3-bind}
%{?python_provide:%python_provide python3-isc}

%description -n python3-bind
This package provides a module which allows commands to be sent to rndc directly from Python programs.

%if %{with DOC}
%package doc
Summary:   BIND 9 Administrator Reference Manual
Requires:  bind-license = %{epoch}:%{version}-%{release}
Requires:  python3-sphinx_rtd_theme
BuildArch: noarch

%description doc
BIND (Berkeley Internet Name Domain) is an implementation of the DNS
(Domain Name System) protocols. BIND includes a DNS server (named),
which resolves host names to IP addresses; a resolver library
(routines for applications to use when interfacing with DNS); and
tools for verifying that the DNS server is operating properly.

This package contains BIND 9 Administrator Reference Manual
in HTML and PDF format.
%end

%endif

%prep
%if 0%{?fedora}
# RHEL does not yet support this verification
%{gpgverify} --keyring='%{SOURCE4}' --signature='%{SOURCE2}' --data='%{SOURCE0}'
%endif
%setup -q -n %{name}-%{BINDVERSION}

# Common patches
%patch10 -p1 -b .PIE
%patch16 -p1 -b .redhat_doc
%patch72 -p1 -b .64bit
%patch106 -p1 -b .rh490837
%patch112 -p1 -b .rh645544
%patch130 -p1 -b .libdb
%patch140 -p1 -b .rh1410433
%patch157 -p1 -b .fips-tests
%patch164 -p1 -b .rh1666814
%patch170 -p1 -b .featuretest-named
%patch171 -p1 -b .test-variant

%if %{with PKCS11}
%patch135 -p1 -b .config-pkcs11
cp -r bin/named{,-pkcs11}
cp -r bin/dnssec{,-pkcs11}
cp -r lib/dns{,-pkcs11}
cp -r lib/ns{,-pkcs11}
%patch136 -p1 -b .dist_pkcs11
%patch149 -p1 -b .kyua-pkcs11
%endif

%patch133 -p1 -b .rh640538

# Sparc and s390 arches need to use -fPIE
%ifarch sparcv9 sparc64 s390 s390x
for i in bin/named/{,unix}/Makefile.in; do
  sed -i 's|fpie|fPIE|g' $i
done
%endif

sed -e 's|"$TOP/config.guess"|"$TOP_SRCDIR/config.guess"|' -i bin/tests/system/ifconfig.sh
:;


%build
## We use out of tree configure/build for export libs
%define _configure "../configure"

# normal and pkcs11 unit tests
%define unit_prepare_build() \
  cp -uv Kyuafile "%{1}/" \
  find lib -name 'K*.key' -exec cp -uv '{}' "%{1}/{}" ';' \
  find lib -name 'Kyuafile' -exec cp -uv '{}' "%{1}/{}" ';' \
  find lib -name 'testdata' -type d -exec cp -Tav '{}' "%{1}/{}" ';' \
  find lib -name 'testkeys' -type d -exec cp -Tav '{}' "%{1}/{}" ';' \

%define systemtest_prepare_build() \
  cp -Tuav bin/tests "%{1}/bin/tests/" \
  cp -uv version "%{1}" \

CFLAGS="$CFLAGS $RPM_OPT_FLAGS"
%if %{with TSAN}
  CFLAGS+=" -O1 -fsanitize=thread -fPIE -pie"
%endif
export CFLAGS
export STD_CDEFINES="$CPPFLAGS"


sed -i -e \
's/RELEASEVER=\(.*\)/RELEASEVER=\1-RH/' \
version

libtoolize -c -f; aclocal -I libtool.m4 --force; autoconf -f

mkdir build

%if %{with DLZ}
# DLZ modules do not support oot builds. Copy files into build
mkdir -p build/contrib/dlz
cp -frp contrib/dlz/modules build/contrib/dlz/modules
%endif

pushd build
LIBDIR_SUFFIX=
export LIBDIR_SUFFIX
%configure \
  --with-python=%{__python3} \
  --with-libtool \
  --localstatedir=%{_var} \
  --with-pic \
  --disable-static \
  --includedir=%{_includedir}/bind9 \
  --with-tuning=large \
  --with-libidn2 \
%if %{with GEOIP2}
  --with-maxminddb \
%endif
%if %{with PKCS11}
  --enable-native-pkcs11 \
  --with-pkcs11=%{_libdir}/pkcs11/libsofthsm2.so \
%endif
  --with-dlopen=yes \
%if %{with GSSTSIG}
  --with-gssapi=yes \
%endif
%if %{with LMDB}
  --with-lmdb=yes \
%else
  --with-lmdb=no \
%endif
%if %{with JSON}
  --without-libjson --with-json-c \
%endif
%if %{with DNSTAP}
  --enable-dnstap \
%endif
%if %{with UNITTEST}
  --with-cmocka \
%endif
  --enable-fixed-rrset \
  --enable-full-report \
;
%if %{with DNSTAP}
  pushd lib
  SRCLIB="../../../lib"
  (cd dns && ln -s ${SRCLIB}/dns/dnstap.proto)
%if %{with PKCS11}
  (cd dns-pkcs11 && ln -s ${SRCLIB}/dns-pkcs11/dnstap.proto)
%endif
  popd
%endif

%if %{with DOCPDF}
# avoid using home for pdf latex files
export TEXMFVAR="`pwd`"
export TEXMFCONFIG="`pwd`"
fmtutil-user --listcfg || :
fmtutil-user --missing || :
%endif

%make_build

# Regenerate dig.1 manpage
pushd bin/dig
make man
popd
pushd bin/python
make man
popd

%if %{with DOC}
  make doc
%endif

%if %{with DLZ}
  pushd contrib/dlz/modules
  for DIR in mysql mysqldyn; do
    sed -e 's/@DLZ_DRIVER_MYSQL_INCLUDES@/$(shell mysql_config --cflags)/' \
        -e 's/@DLZ_DRIVER_MYSQL_LIBS@/$(shell mysql_config --libs)/' \
        $DIR/Makefile.in > $DIR/Makefile
  done
  for DIR in filesystem ldap mysql mysqldyn sqlite3; do
    make -C $DIR CFLAGS="-fPIC -I../include $CFLAGS $LDFLAGS"
  done
  popd
%endif
popd # build

%unit_prepare_build build
%systemtest_prepare_build build

%check
%if %{with PKCS11} && (%{with UNITTEST} || %{with SYSTEMTEST})
  # Tests require initialization of pkcs11 token
  eval "$(bash %{SOURCE48} -A "`pwd`/softhsm-tokens")"
%endif

%if %{with TSAN}
export TSAN_OPTIONS="log_exe_name=true log_path=ThreadSanitizer exitcode=0"
%endif

%if %{with UNITTEST}
  pushd build
  CPUS=$(lscpu -p=cpu,core | grep -v '^#' | wc -l)
  if [ "$CPUS" -gt 16 ]; then
    ORIGFILES=$(ulimit -n)
    ulimit -n 4096 || : # Requires on some machines with many cores
  fi
  make unit
  e=$?
  if [ "$e" -ne 0 ]; then
    echo "ERROR: this build of BIND failed 'make unit'. Aborting."
    exit $e;
  fi;
  [ "$CPUS" -gt 16 ] && ulimit -n $ORIGFILES || :
  popd
## End of UNITTEST
%endif

%if %{with SYSTEMTEST}
# Runs system test if ip addresses are already configured
# or it is able to configure them
if perl bin/tests/system/testsock.pl
then
  CONFIGURED=already
else
  CONFIGURED=
  sh bin/tests/system/ifconfig.sh up
  perl bin/tests/system/testsock.pl && CONFIGURED=build
fi
if [ -n "$CONFIGURED" ]
then
  set -e
  pushd build/bin/tests
  chown -R ${USER} . # Can be unknown user
  %make_build test 2>&1 | tee test.log
  e=$?
  popd
  [ "$CONFIGURED" = build ] && sh bin/tests/system/ifconfig.sh down
  if [ "$e" -ne 0 ]; then
    echo "ERROR: this build of BIND failed 'make test'. Aborting."
    exit $e;
  fi;
else
  echo 'SKIPPED: tests require root, CAP_NET_ADMIN or already configured test addresses.'
fi
%endif
:

%install
# Build directory hierarchy
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/{bind,named}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/named/{slaves,data,dynamic}
mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/{man1,man5,man8}
mkdir -p ${RPM_BUILD_ROOT}/run/named
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/log

#chroot
for D in %{chroot_create_directories}
do
  mkdir -p ${RPM_BUILD_ROOT}/%{chroot_prefix}${D}
done

# create symlink as it is on real filesystem
pushd ${RPM_BUILD_ROOT}/%{chroot_prefix}/var
ln -s ../run run
popd

# these are required to prevent them being erased during upgrade of previous
touch ${RPM_BUILD_ROOT}/%{chroot_prefix}%{_sysconfdir}/named.conf
#end chroot

pushd build
%make_install
popd

# Remove unwanted files
rm -f ${RPM_BUILD_ROOT}/etc/bind.keys

# Systemd unit files
mkdir -p ${RPM_BUILD_ROOT}%{_unitdir}
install -m 644 %{SOURCE37} ${RPM_BUILD_ROOT}%{_unitdir}
install -m 644 %{SOURCE38} ${RPM_BUILD_ROOT}%{_unitdir}
install -m 644 %{SOURCE44} ${RPM_BUILD_ROOT}%{_unitdir}
install -m 644 %{SOURCE46} ${RPM_BUILD_ROOT}%{_unitdir}

%if %{with PKCS11}
install -m 644 %{SOURCE47} ${RPM_BUILD_ROOT}%{_unitdir}
%else
# Not packaged without PKCS11
find ${RPM_BUILD_ROOT}%{_includedir}/bind9/pk11 ${RPM_BUILD_ROOT}%{_includedir}/bind9/pkcs11 \
  -name '*.h' \! -name site.h -delete

%endif

mkdir -p ${RPM_BUILD_ROOT}%{_libexecdir}
install -m 755 %{SOURCE41} ${RPM_BUILD_ROOT}%{_libexecdir}/setup-named-chroot.sh
install -m 755 %{SOURCE42} ${RPM_BUILD_ROOT}%{_libexecdir}/generate-rndc-key.sh

%if %{with PKCS11}
install -m 755 %{SOURCE48} ${RPM_BUILD_ROOT}%{_libexecdir}/setup-named-softhsm.sh
%endif

install -m 644 %SOURCE3 ${RPM_BUILD_ROOT}/etc/logrotate.d/named
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE1} ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig/named
install -m 644 %{SOURCE49} ${RPM_BUILD_ROOT}%{_sysconfdir}/named-chroot.files

%if %{with DLZ}
  pushd build
  pushd contrib/dlz/modules
  for DIR in filesystem ldap mysql mysqldyn sqlite3; do
    %make_install -C $DIR libdir=%{_libdir}/named
  done
  pushd ${RPM_BUILD_ROOT}/%{_libdir}/bind
    cp -s ../named/dlz_*.so .
  popd
  mkdir -p doc/{mysql,mysqldyn}
  cp -p mysqldyn/testing/README doc/mysqldyn/README.testing
  cp -p mysqldyn/testing/* doc/mysqldyn
  cp -p mysql/testing/* doc/mysql
  popd
  popd
%endif

# Install isc/errno2result.h header
install -m 644 lib/isc/unix/errno2result.h ${RPM_BUILD_ROOT}%{_includedir}/bind9/isc

# Remove libtool .la files:
find ${RPM_BUILD_ROOT}/%{_libdir} -name '*.la' -exec '/bin/rm' '-f' '{}' ';';

# PKCS11 versions manpages
%if %{with PKCS11}
pushd ${RPM_BUILD_ROOT}%{_mandir}/man8
ln -s named.8.gz named-pkcs11.8.gz
ln -s dnssec-checkds.8.gz dnssec-checkds-pkcs11.8.gz
ln -s dnssec-dsfromkey.8.gz dnssec-dsfromkey-pkcs11.8.gz
ln -s dnssec-importkey.8.gz dnssec-importkey-pkcs11.8.gz
ln -s dnssec-keyfromlabel.8.gz dnssec-keyfromlabel-pkcs11.8.gz
ln -s dnssec-keygen.8.gz dnssec-keygen-pkcs11.8.gz
ln -s dnssec-revoke.8.gz dnssec-revoke-pkcs11.8.gz
ln -s dnssec-settime.8.gz dnssec-settime-pkcs11.8.gz
ln -s dnssec-signzone.8.gz dnssec-signzone-pkcs11.8.gz
ln -s dnssec-verify.8.gz dnssec-verify-pkcs11.8.gz
popd
%endif

# 9.16.4 installs even manual pages for tools not generated
%if %{without DNSTAP}
rm -f ${RPM_BUILD_ROOT}%{_mandir}/man1/dnstap-read.1* || true
%endif
%if %{without LMDB}
rm -f ${RPM_BUILD_ROOT}%{_mandir}/man8/named-nzd2nzf.8* || true
%endif

pushd ${RPM_BUILD_ROOT}%{_mandir}/man8
ln -s ddns-confgen.8.gz tsig-keygen.8.gz
ln -s named-checkzone.8.gz named-compilezone.8.gz
popd

%if %{with DOC}
mkdir -p ${RPM_BUILD_ROOT}%{_pkgdocdir}
cp -a build/doc/arm/_build/html ${RPM_BUILD_ROOT}%{_pkgdocdir}
rm -rf ${RPM_BUILD_ROOT}%{_pkgdocdir}/html/.{buildinfo,doctrees}
# Share static data from original sphinx package
for DIR in %{python3_sitelib}/sphinx_rtd_theme/static/*
do
  BASE=$(basename -- "$DIR")
  BINDTHEMEDIR="${RPM_BUILD_ROOT}%{_pkgdocdir}/html/_static/$BASE"
  if [ -d "$BINDTHEMEDIR" ]; then
    rm -rf "$BINDTHEMEDIR"
    ln -s "$DIR" "$BINDTHEMEDIR"
  fi
done
%endif
%if %{with DOCPDF}
cp -a build/doc/arm/Bv9ARM.pdf ${RPM_BUILD_ROOT}%{_pkgdocdir}
%endif

# Ghost config files:
touch ${RPM_BUILD_ROOT}%{_localstatedir}/log/named.log

# configuration files:
install -m 640 %{SOURCE16} ${RPM_BUILD_ROOT}%{_sysconfdir}/named.conf
touch ${RPM_BUILD_ROOT}%{_sysconfdir}/rndc.{key,conf}
install -m 644 %{SOURCE27} ${RPM_BUILD_ROOT}%{_sysconfdir}/named.root.key
install -m 644 %{SOURCE36} ${RPM_BUILD_ROOT}%{_sysconfdir}/trusted-key.key
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/named

# data files:
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/named
install -m 640 %{SOURCE17} ${RPM_BUILD_ROOT}%{_localstatedir}/named/named.ca
install -m 640 %{SOURCE18} ${RPM_BUILD_ROOT}%{_localstatedir}/named/named.localhost
install -m 640 %{SOURCE19} ${RPM_BUILD_ROOT}%{_localstatedir}/named/named.loopback
install -m 640 %{SOURCE20} ${RPM_BUILD_ROOT}%{_localstatedir}/named/named.empty
install -m 640 %{SOURCE23} ${RPM_BUILD_ROOT}%{_sysconfdir}/named.rfc1912.zones

# sample bind configuration files for %%doc:
mkdir -p sample/etc sample/var/named/{data,slaves}
install -m 644 %{SOURCE25} sample/etc/named.conf
# Copy default configuration to %%doc to make it usable from system-config-bind
install -m 644 %{SOURCE16} named.conf.default
install -m 644 %{SOURCE23} sample/etc/named.rfc1912.zones
install -m 644 %{SOURCE18} %{SOURCE19} %{SOURCE20}  sample/var/named
install -m 644 %{SOURCE17} sample/var/named/named.ca
for f in my.internal.zone.db slaves/my.slave.internal.zone.db slaves/my.ddns.internal.zone.db my.external.zone.db; do 
  echo '@ in soa localhost. root 1 3H 15M 1W 1D
  ns localhost.' > sample/var/named/$f; 
done
:;

mkdir -p ${RPM_BUILD_ROOT}%{_tmpfilesdir}
install -m 644 %{SOURCE35} ${RPM_BUILD_ROOT}%{_tmpfilesdir}/named.conf

mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/rwtab.d
install -m 644 %{SOURCE43} ${RPM_BUILD_ROOT}%{_sysconfdir}/rwtab.d/named

%pre
if [ "$1" -eq 1 ]; then
  /usr/sbin/groupadd -g %{bind_gid} -f -r named >/dev/null 2>&1 || :;
  /usr/sbin/useradd  -u %{bind_uid} -r -N -M -g named -s /sbin/nologin -d /var/named -c Named named >/dev/null 2>&1 || :;
fi;
:;

%post
%?ldconfig
if [ -e "%{_sysconfdir}/selinux/config" ]; then
  %selinux_set_booleans -s targeted %{selinuxbooleans}
  %selinux_set_booleans -s mls %{selinuxbooleans}
fi
if [ "$1" -eq 1 ]; then
  # Initial installation
  [ -x /sbin/restorecon ] && /sbin/restorecon /etc/rndc.* /etc/named.* >/dev/null 2>&1 ;
  # rndc.key has to have correct perms and ownership, CVE-2007-6283
  [ -e /etc/rndc.key ] && chown root:named /etc/rndc.key
  [ -e /etc/rndc.key ] && chmod 0640 /etc/rndc.key
else
  # Upgrade, use invalid shell
  if getent passwd named | grep ':/bin/false$' >/dev/null; then
    /sbin/usermod -s /sbin/nologin named
  fi
  # Checkconf will parse out comments
  if /usr/sbin/named-checkconf -p /etc/named.conf 2>/dev/null | grep -q named.iscdlv.key
  then
    echo "Replacing obsolete named.iscdlv.key with named.root.key..."
    if cp -Rf --preserve=all --remove-destination /etc/named.conf /etc/named.conf.rpmbackup; then
      sed -e 's/named\.iscdlv\.key/named.root.key/' \
        /etc/named.conf.rpmbackup > /etc/named.conf || \
      mv /etc/named.conf.rpmbackup /etc/named.conf
    fi
  fi
fi
%systemd_post named.service
:;

%preun
# Package removal, not upgrade
%systemd_preun named.service

%postun
%?ldconfig
# Package upgrade, not uninstall
%systemd_postun_with_restart named.service
if [ -e "%{_sysconfdir}/selinux/config" ]; then
  %selinux_unset_booleans -s targeted %{selinuxbooleans}
  %selinux_unset_booleans -s mls %{selinuxbooleans}
fi

%if %{with PKCS11}
%post pkcs11
# Initial installation
%systemd_post named-pkcs11.service

%preun pkcs11
# Package removal, not upgrade
%systemd_preun named-pkcs11.service

%postun pkcs11
# Package upgrade, not uninstall
%systemd_postun_with_restart named-pkcs11.service
%endif

# Fix permissions on existing device files on upgrade
%define chroot_fix_devices() \
if [ $1 -gt 1 ]; then \
  for DEV in "%{1}/dev"/{null,random,zero}; do \
    if [ -e "$DEV" -a "$(/bin/stat --printf="%G %a" "$DEV")" = "root 644" ]; \
    then \
      /bin/chmod 0664 "$DEV" \
      /bin/chgrp named "$DEV" \
    fi \
  done \
fi

%triggerun -- bind < 32:9.9.0-0.6.rc1
/sbin/chkconfig --del named >/dev/null 2>&1 || :
/bin/systemctl try-restart named.service >/dev/null 2>&1 || :

%ldconfig_scriptlets libs

%if %{with PKCS11}
%ldconfig_scriptlets pkcs11-libs
%endif

%post chroot
%systemd_post named-chroot.service
%chroot_fix_devices %{chroot_prefix}
:;

%posttrans chroot
if [ -x /usr/sbin/selinuxenabled ] && /usr/sbin/selinuxenabled; then
  [ -x /sbin/restorecon ] && /sbin/restorecon %{chroot_prefix}/dev/* > /dev/null 2>&1;
fi;

%preun chroot
# wait for stop of both named-chroot and named-chroot-setup services
# on uninstall
%systemd_preun named-chroot.service named-chroot-setup.service
:;

%postun chroot
# Package upgrade, not uninstall
%systemd_postun_with_restart named-chroot.service


%files
# TODO: Move from lib/bind to lib/named, as used by upstream
%dir %{_libdir}/bind
%dir %{_libdir}/named
%{_libdir}/named/*.so
%exclude %{_libdir}/named/dlz_*.so
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/sysconfig/named
%config(noreplace) %attr(0644,root,named) %{_sysconfdir}/named.root.key
%config(noreplace) %{_sysconfdir}/logrotate.d/named
%{_tmpfilesdir}/named.conf
%{_sysconfdir}/rwtab.d/named
%{_unitdir}/named.service
%{_unitdir}/named-setup-rndc.service
%{_sbindir}/named-journalprint
%{_sbindir}/named-checkconf
%{_bindir}/named-rrchecker
%{_bindir}/mdig
%{_sbindir}/named
%{_sbindir}/rndc*
%{_libexecdir}/generate-rndc-key.sh
%{_mandir}/man1/mdig.1*
%{_mandir}/man1/named-rrchecker.1*
%{_mandir}/man5/named.conf.5*
%{_mandir}/man5/rndc.conf.5*
%{_mandir}/man8/rndc.8*
%{_mandir}/man8/named.8*
%{_mandir}/man8/named-checkconf.8*
%{_mandir}/man8/rndc-confgen.8*
%{_mandir}/man8/named-journalprint.8*
%{_mandir}/man8/filter-aaaa.8.gz
%doc CHANGES README named.conf.default
%doc sample/

# Hide configuration
%defattr(0640,root,named,0750)
%dir %{_sysconfdir}/named
%config(noreplace) %verify(not link) %{_sysconfdir}/named.conf
%config(noreplace) %verify(not link) %{_sysconfdir}/named.rfc1912.zones
%defattr(0660,root,named,01770)
%dir %{_localstatedir}/named
%defattr(0660,named,named,0770)
%dir %{_localstatedir}/named/slaves
%dir %{_localstatedir}/named/data
%dir %{_localstatedir}/named/dynamic
%ghost %{_localstatedir}/log/named.log
%defattr(0640,root,named,0750)
%config %verify(not link) %{_localstatedir}/named/named.ca
%config %verify(not link) %{_localstatedir}/named/named.localhost
%config %verify(not link) %{_localstatedir}/named/named.loopback
%config %verify(not link) %{_localstatedir}/named/named.empty
%ghost %config(noreplace) %{_sysconfdir}/rndc.key
# ^- rndc.key now created on first install only if it does not exist
%ghost %config(noreplace) %{_sysconfdir}/rndc.conf
# ^- The default rndc.conf which uses rndc.key is in named's default internal config -
#    so rndc.conf is not necessary.
%defattr(-,named,named,-)
%dir /run/named

%files libs
%{_libdir}/libbind9-%{version}*.so
%{_libdir}/libisccc-%{version}*.so
%{_libdir}/libns-%{version}*.so
%{_libdir}/libdns-%{version}*.so
%{_libdir}/libirs-%{version}*.so
%{_libdir}/libisc-%{version}*.so
%{_libdir}/libisccfg-%{version}*.so

%files license
%{!?_licensedir:%global license %%doc}
%license COPYRIGHT

%files utils
%{_bindir}/dig
%{_bindir}/delv
%{_bindir}/host
%{_bindir}/nslookup
%{_bindir}/nsupdate
%{_bindir}/arpaname
%{_sbindir}/ddns-confgen
%{_sbindir}/tsig-keygen
%{_sbindir}/nsec3hash
%{_sbindir}/named-checkzone
%{_sbindir}/named-compilezone
%if %{with DNSTAP}
%{_bindir}/dnstap-read
%{_mandir}/man1/dnstap-read.1*
%endif
%if %{with LMDB}
%{_sbindir}/named-nzd2nzf
%{_mandir}/man8/named-nzd2nzf.8*
%endif
%{_mandir}/man1/host.1*
%{_mandir}/man1/nsupdate.1*
%{_mandir}/man1/dig.1*
%{_mandir}/man1/delv.1*
%{_mandir}/man1/nslookup.1*
%{_mandir}/man1/arpaname.1*
%{_mandir}/man8/ddns-confgen.8*
%{_mandir}/man8/tsig-keygen.8*
%{_mandir}/man8/nsec3hash.8*
%{_mandir}/man8/named-checkzone.8*
%{_mandir}/man8/named-compilezone.8*
%{_sysconfdir}/trusted-key.key

%files dnssec-utils
%{_sbindir}/dnssec*
%if %{with PKCS11}
%exclude %{_sbindir}/dnssec*pkcs11
%endif

%files dnssec-doc
%{_mandir}/man8/dnssec*.8*
%if %{with PKCS11}
%exclude %{_mandir}/man8/dnssec*-pkcs11.8*
%endif

%files devel
%{_libdir}/libbind9.so
%{_libdir}/libisccc.so
%{_libdir}/libns.so
%{_libdir}/libdns.so
%{_libdir}/libirs.so
%{_libdir}/libisc.so
%{_libdir}/libisccfg.so
%dir %{_includedir}/bind9
%{_includedir}/bind9/bind9
%{_includedir}/bind9/isccc
%{_includedir}/bind9/ns
%{_includedir}/bind9/dns
%{_includedir}/bind9/dst
%{_includedir}/bind9/irs
%{_includedir}/bind9/isc
%dir %{_includedir}/bind9/pk11
%{_includedir}/bind9/pk11/site.h
%{_includedir}/bind9/isccfg

%files chroot
%config(noreplace) %{_sysconfdir}/named-chroot.files
%{_unitdir}/named-chroot.service
%{_unitdir}/named-chroot-setup.service
%{_libexecdir}/setup-named-chroot.sh
%defattr(0664,root,named,-)
%ghost %dev(c,1,3) %verify(not mtime) %{chroot_prefix}/dev/null
%ghost %dev(c,1,8) %verify(not mtime) %{chroot_prefix}/dev/random
%ghost %dev(c,1,9) %verify(not mtime) %{chroot_prefix}/dev/urandom
%ghost %dev(c,1,5) %verify(not mtime) %{chroot_prefix}/dev/zero
%defattr(0640,root,named,0750)
%dir %{chroot_prefix}
%dir %{chroot_prefix}/dev
%dir %{chroot_prefix}%{_sysconfdir}
%dir %{chroot_prefix}%{_sysconfdir}/named
%dir %{chroot_prefix}%{_sysconfdir}/pki
%dir %{chroot_prefix}%{_sysconfdir}/pki/dnssec-keys
%dir %{chroot_prefix}%{_sysconfdir}/crypto-policies
%dir %{chroot_prefix}%{_sysconfdir}/crypto-policies/back-ends
%dir %{chroot_prefix}%{_localstatedir}
%dir %{chroot_prefix}/run
%ghost %config(noreplace) %{chroot_prefix}%{_sysconfdir}/named.conf
%defattr(-,root,root,-)
%dir %{chroot_prefix}/usr
%dir %{chroot_prefix}/%{_libdir}
%dir %{chroot_prefix}/%{_libdir}/bind
%dir %{chroot_prefix}/%{_datadir}/GeoIP
%defattr(0660,root,named,01770)
%dir %{chroot_prefix}%{_localstatedir}/named
%defattr(0660,named,named,0770)
%dir %{chroot_prefix}%{_localstatedir}/tmp
%dir %{chroot_prefix}%{_localstatedir}/log
%defattr(-,named,named,-)
%dir %{chroot_prefix}/run/named
%{chroot_prefix}%{_localstatedir}/run

%if %{with PKCS11}
%files pkcs11
%{_sbindir}/named-pkcs11
%{_unitdir}/named-pkcs11.service
%{_mandir}/man8/named-pkcs11.8*
%{_libexecdir}/setup-named-softhsm.sh

%files pkcs11-utils
%{_sbindir}/dnssec*pkcs11
%{_sbindir}/pkcs11-destroy
%{_sbindir}/pkcs11-keygen
%{_sbindir}/pkcs11-list
%{_sbindir}/pkcs11-tokens
%{_mandir}/man8/pkcs11*.8*
%{_mandir}/man8/dnssec*-pkcs11.8*

%files pkcs11-libs
%{_libdir}/libdns-pkcs11-%{version}*.so
%{_libdir}/libns-pkcs11-%{version}*.so

%files pkcs11-devel
%{_includedir}/bind9/pk11/*.h
%exclude %{_includedir}/bind9/pk11/site.h
%{_includedir}/bind9/pkcs11
%{_libdir}/libdns-pkcs11.so
%{_libdir}/libns-pkcs11.so
%endif

   /usr/lib64/bind/dlz_filesystem_dynamic.so
   /usr/lib64/bind/dlz_ldap_dynamic.so
   /usr/lib64/bind/dlz_mysql_dynamic.so
   /usr/lib64/bind/dlz_mysqldyn_mod.so
   /usr/lib64/bind/dlz_sqlite3_dynamic.so

%files -n python3-bind
%{python3_sitelib}/*.egg-info
%{python3_sitelib}/isc/

%if %{with DOC}
%files doc
%dir %{_pkgdocdir}
%doc %{_pkgdocdir}/html
%endif
%if %{with DOCPDF}
%doc %{_pkgdocdir}/Bv9ARM.pdf
%endif

%changelog
* Thu Apr 29 2021 Petr Menšík <pemensik@redhat.com> - 32:9.16.15-1
- Update to 9.16.15

* Thu Mar 25 2021 Petr Menšík <pemensik@redhat.com> - 32:9.16.13-1
- Update to 9.16.13
- Changed displayed version just to include -RH suffix, not release
- Version is now part of library names, soname versions are no longer provided
- Removed bind-libs-lite subpackage
