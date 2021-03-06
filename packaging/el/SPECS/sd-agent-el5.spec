# SO references
# http://stackoverflow.com/questions/880227/what-is-the-minimum-i-have-to-do-to-create-an-rpm-file

# Init script references
# http://fedoraproject.org/wiki/Packaging/SysVInitScript#InitscriptScriptlets

%define        __spec_install_post %{nil}
%define          debug_package %{nil}
%define        __os_install_post %{_dbpath}/brp-compress
%global        __venv %{_tmppath}/venv
%global          longdescription %include description
%global        __sd_python_version 2.6

Summary: Server Density Monitoring Agent
Name: sd-agent
BuildArch: x86_64 i386
%include %{_topdir}/inc/version
%include %{_topdir}/inc/release
Requires: python26, sysstat, libyaml
BuildRequires: symlinks
License: Simplified BSD
Group: System/Monitoring
Source: %{name}-%{version}.tar.gz
URL: http://www.serverdensity.com/

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description
%{longdescription}

%prep
curl -LO https://pypi.python.org/packages/source/v/virtualenv/virtualenv-13.1.2.tar.gz
tar xzf virtualenv-13.1.2.tar.gz
python26 virtualenv-13.1.2/virtualenv.py %{__venv}

%setup -qn sd-agent
# Get rid of conflictive dependencies for el5
sed -ie 's/^\(pycurl\|psycopg2\)/# \1/' requirements-opt.txt
%{__venv}/bin/python %{__venv}/bin/pip install -r requirements.txt
%{__venv}/bin/python %{__venv}/bin/pip install -r requirements-opt.txt

%build
%{__venv}/bin/python setup.py build
%{__venv}/bin/python setup.py install
%include %{_topdir}/inc/fix_virtualenv

%include %{_topdir}/inc/install.el5

%clean
rm -rf %{buildroot}

%post
chmod +x /etc/init.d/sd-agent
getent group sd-agent > /dev/null || groupadd -r sd-agent
getent passwd sd-agent > /dev/null || useradd -r -g sd-agent -d /usr/bin/sd-agent/ -s /bin/bash -c "Server Density Agent User" sd-agent
mkdir -p /var/log/sd-agent/
mkdir -p /var/run/sd-agent/
chown -R sd-agent:sd-agent /var/log/sd-agent/
chown -R sd-agent:sd-agent /var/run/sd-agent/
chown -R sd-agent:sd-agent /etc/sd-agent/
chown -R sd-agent:sd-agent /etc/sd-agent/config.cfg
chmod 0660 /etc/sd-agent/config.cfg
chown -R sd-agent:sd-agent /etc/sd-agent/plugins.cfg
chmod 0660 /etc/sd-agent/plugins.cfg
/sbin/chkconfig --add sd-agent
/etc/init.d/sd-agent restart

%pre
case "$1" in
  2)
    /sbin/service sd-agent stop >/dev/null 2>&1
  ;;
esac

%preun
case "$1" in
  0)
    /sbin/service sd-agent stop >/dev/null 2>&1
    /sbin/chkconfig --del /etc/init.d/sd-agent
    rm /etc/init.d/sd-agent
    rm -rf /var/log/sd-agent/
    rm -rf /var/run/sd-agent/
  ;;
esac

%include %{_topdir}/inc/files.el5
%include %{_topdir}/inc/subpackages
%include %{_topdir}/inc/changelog
