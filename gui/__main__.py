import sys
from pysca import app
from pysca.device import PYPLC
import pygui.navbar as navbar
from concrete6 import concrete6

def main():
    import argparse
    args = argparse.ArgumentParser(sys.argv)
    args.add_argument('--device', action='store', type=str, default='192.168.2.10', help='IP address of the device')
    args.add_argument('--simulator', action='store_true', default=False, help='Run PYPLC logic simulator')
    
    ns = args.parse_known_args()[0]

    if ns.simulator:
        import subprocess
        logic = subprocess.Popen(["python3", "src/krax.py"])
        ns.device = '127.0.0.1'
    
    dev = PYPLC(ns.device)
    app.devices['PLC'] = dev
    app.animate(concrete6.instance)
    Home = app.window('ui/Home.ui')
    # с использованием navbar
    navbar.append(Home)       
    navbar.tools(app.window('ui/Extensions.ui'))
    navbar.instance.setWindowTitle(Home.windowTitle())
    navbar.instance.setWindowIcon(Home.windowIcon())
    navbar.instance.show( )
    concrete6.setMainWindow(navbar.instance)
    concrete6.setContainerPanels([Home.doserpanel_1,Home.doserpanel_2,Home.doserpanel_3,Home.doserpanel_4,Home.doserpanel_5,Home.doserpanel_6,Home.doserpanel_7])
    concrete6.reload()
    # или 
    # Home.show()               
    
    dev.start(100)
    app.start( ctx = globals() )
    dev.stop( )
    concrete6.save()

    if ns.simulator:
        logic.terminate( )

if __name__=='__main__':
    main( )
    