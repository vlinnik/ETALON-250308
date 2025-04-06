Source: <pysca-hmi>
Section: devel
Priority: optional
Maintainer: vlinnik <vlinnik@mail.ru>
Rules-Requires-Root: no
Build-Depends:
 debhelper-compat (= 13),
 dh-sequence-python3,
 python3-setuptools,
 python3-all,
Standards-Version: 4.6.2
Homepage: https://github.com/vlinnik/<pysca-hmi>

Package: python3-pysca-hmi
Architecture: all
Multi-Arch: foreign
Depends:
 ${python3:Depends},
 ${misc:Depends},
 ${shlibs:Depends},
 qt5-image-formats-plugins
Suggests:
Description: Factory Automation HMI (Python 3)
 Project based on PYSCA-Framework
 .
 This package installs the library for Python 3.
