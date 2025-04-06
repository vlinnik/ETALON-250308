# Проект АСУ PYSCA-HMI 

Проект автоматизации линии приготовления бетона 

- Логика управления написана для контроллера KRAX PLC-932
- Визуализация написана на python3+PyQt5

# Запуск

## Зависимости

AnyQt, PyQt5, pyplc, pysca, pygui

# Установка

Если есть сборка pyinstaller то ее необходимо 

- скопировать в /usr/local/ и выполнить 
- скопировать .desktop в /usr/share/applications/ и выполнить

```
xdg-desktop-menu install --novendor --mode user /usr/share/applications/pysca-hmi.desktop
```

Если запускаем из исходников, то

```
python3 <SOURCE_DIR_LOCATION>/__main__.py -w <SOURCE_DIR_LOCATION>
```

# Сборка pyinstaller

## Создание spec файла

```
$ pyi-makespec  --windowed --icon=resources/power.png --name=pysca-hmi --exclude PyQt6 --exclude PySide2 __main__.py
        --hidden-import=qwt
        --hidden-import=AnyQt.QtSql
        --hidden-import=pygui.animation
        --hidden-import=pygui.runtimetrend
```
### Дополнительно в spec

Если АСУ зависит от необходимых файлов и бинарников, которые надо добавить вручную, пример как сделать

```
import os
from AnyQt.QtCore import QLibraryInfo

datas = [ ('default.scada','.'),('ui','./ui'),('resources','./resources'),('SCADA.rcc','.'),('concrete6.dat','.') ]
binaries = [
    (os.path.join(QLibraryInfo.location(QLibraryInfo.LibraryLocation.PluginsPath), 'SCADA/modules', 'libconcrete6.so'), 'PyQt5/Qt5/plugins/SCADA/modules'),
    (os.path.join(QLibraryInfo.location(QLibraryInfo.LibraryLocation.PluginsPath), 'sqldrivers', 'libqsqlmysql.so'), 'PyQt5/Qt5/plugins/sqldrivers'),
    (os.path.join(QLibraryInfo.location(QLibraryInfo.LibraryLocation.LibraryExecutablesPath), 'QtWebEngineProcess'), 'PyQt5/Qt5/libexec'),
]
```

в секции 

```
a = Analysis(...)
```

изменить параметры binaries и datas

# Кастомные Widget на python

Home.ui использует Widgets, которые сделаны на python-е. Чтобы стали доступны в панели нужно

Из каталога проекта (где файлы *plugin.py)

```
PYQTDESIGNERPATH=. designer
```

в designer должен быть установлен libpyqt5/libpyqt5 