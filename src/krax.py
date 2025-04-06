#Ниже идет Ваша программа
from pyplc.config import plc
from sys import platform
from project import name as project_name,version_short as project_version
from concrete import Factory,Weight,Container,Dosator,FlowMeter,Lock,Transport,MSGate,Motor,Mixer,Readiness,Loaded,Manager
from concrete.dosator import DescendingDosator
from concrete.vibrator import Vibrator,UnloadHelper
from concrete.container import Retarder
from pyplc.utils.misc import BLINK

print(f'\tЗапуск проекта {project_name} {project_version}')

factory_1 = Factory()

cement_m_1 = Weight(raw = plc.CEMENT_M_1, mmax = 1500)
silage_1 = Container( m = lambda: cement_m_1.m, out = plc.AUGER_ON_1, lock = Lock(key=~plc.DCEMENT_CLOSED_1) )
dcement_1 = Dosator( m = lambda: cement_m_1.m, closed = plc.DCEMENT_CLOSED_1, out = plc.DCEMENT_OPEN_1, lock = Lock(key=lambda: plc.AUGER_ON_1 or not plc.MIXER_ISON_1 ),containers=[silage_1] )
dc_vibrator_1 = UnloadHelper(q=plc.DC_VIBRATOR_ON_1,dosator=dcement_1,weight=cement_m_1)
aerator_1 = BLINK(enable=plc.AUGER_ON_1, q = plc.AERATOR_ON_1, t_off = 3000 )

additions_m_1 = Weight(raw=plc.ADDITIONS_M_1,mmax=50)
addition_1 = Container(m=lambda: additions_m_1.m,out=plc.APUMP_ON_1,closed=~plc.APUMP_ON_1,max_sp=10)
dadditions_1 = DescendingDosator(m = lambda: additions_m_1.m, out = plc.DADDITIONS_OPEN_1,closed=plc.DADDITIONS_CLOSED_1, containers=(addition_1,),lock=Lock(key=lambda: not plc.MIXER_ISON_1 or plc.APUMP_ON_1 ) )

water_m_1 = Weight(raw = plc.WATER_M_1, mmax = 500)
water_1 = Container( m = lambda: water_m_1.m, out = plc.WPUMP_ON_1, lock = Lock(key=~plc.DWATER_CLOSED_1) )
addition_2 = FlowMeter(out=plc.APUMP_ON_2,cnt=plc.ADDITION_Q_2,impulseWeight=0.0035,closed=True)
dwater_1 = Dosator( m = lambda: water_m_1.m, closed = plc.DWATER_CLOSED_1, out = plc.DWATER_OPEN_1, lock = Lock(key=lambda: plc.WPUMP_ON_1 or not plc.MIXER_ISON_1 ),containers=(water_1,addition_2) )

tconveyor_1= Transport(power = plc.TCONVEYOR_ON_1, ison = plc.TCONVEYOR_ISON_1,out=plc.CONVEYOR_ON_1)
fillers_m_1 = Weight(raw=plc.FILLERS_M_1, mmax = 8000)
retarder_1 = Retarder(m=lambda:fillers_m_1.m, outs=(plc.FILLER_OPEN_1,plc.FILLER_OPEN_2,plc.FILLER_OPEN_3),sts=(plc.FILLER_CLOSED_1,plc.FILLER_CLOSED_2,plc.FILLER_CLOSED_3))
filler_1 = Container(m = lambda: fillers_m_1.m, out=retarder_1.out(0), closed=retarder_1.closed(0), lock = Lock(key=lambda: retarder_1.lock(0) or plc.CONVEYOR_ON_1 ))
filler_2 = Container(m = lambda: fillers_m_1.m, out=retarder_1.out(1), closed=retarder_1.closed(1), lock = Lock(key=lambda: retarder_1.lock(1) or plc.CONVEYOR_ON_1 ))
filler_3 = Container(m = lambda: fillers_m_1.m, out=retarder_1.out(2), closed=retarder_1.closed(2), lock = Lock(key=lambda: retarder_1.lock(2) or plc.CONVEYOR_ON_1 ))
dfillers_1 = Dosator(m = lambda: fillers_m_1.m, out=tconveyor_1.set_auto, containers=(filler_1,filler_2,filler_3),lock=Lock(key=lambda: plc.FILLER_OPEN_1 or plc.FILLER_OPEN_2 or plc.FILLER_OPEN_3 or not plc.MIXER_ISON_1))
vibrator_1 = Vibrator(q = plc.VIBRATOR_ON_1,containers =(plc.FILLER_OPEN_1,),weight=fillers_m_1)
vibrator_2 = Vibrator(q = plc.VIBRATOR_ON_2,containers =(plc.FILLER_OPEN_2,),weight=fillers_m_1)
vibrator_3 = Vibrator(q = plc.VIBRATOR_ON_3,containers =(plc.FILLER_OPEN_3,),weight=fillers_m_1)

gate_1 = MSGate( closed = plc.MIXER_CLOSED_1, opened = plc.MIXER_OPENED_1,open=plc.MIXER_OPEN_1)
motor_1 = Motor( ison = plc.MIXER_ISON_1, powered = plc.MIXER_ON_1)
mixer_1 = Mixer( gate=gate_1, motor = motor_1,flows=tuple( x.q for x in (silage_1,water_1,dadditions_1,addition_2,filler_1,filler_2,filler_3) ) )

dadditions_1.map(clear=lambda: mixer_1.qreset)

ready_1 = Readiness( (dcement_1,dwater_1,dfillers_1,dadditions_1) ) #что должно быть loaded перед началом загрузки в смеситель
loaded_1 = Loaded( (dcement_1,dwater_1,dfillers_1,dadditions_1) )  #что должно быть unloaded чтобы смеситель считать загруженным
manager_1 = Manager(collected=ready_1,loaded=loaded_1,mixer=mixer_1,dosators=(dcement_1,dwater_1,dfillers_1,dadditions_1) )  #dosators= кому надо установить unload для начала загрузки

factory_1.on_mode = tuple( x.switch_mode for x in (silage_1,water_1,filler_1,filler_2,filler_3,dcement_1,dwater_1,dfillers_1,addition_1,addition_2,dadditions_1) )
factory_1.on_emergency = tuple(x.emergency for x in (silage_1,water_1,filler_1,filler_2,filler_3,dcement_1,dwater_1,dfillers_1,mixer_1,dfillers_1,addition_1,dadditions_1,addition_2,manager_1) )

instances = (factory_1, cement_m_1, water_m_1, additions_m_1, fillers_m_1, silage_1, dcement_1, aerator_1, water_1,addition_2, dwater_1, addition_1,
             dadditions_1, dfillers_1, filler_1, filler_2, filler_3, vibrator_1, vibrator_2, vibrator_3, tconveyor_1, gate_1, mixer_1, motor_1,
             ready_1,loaded_1,manager_1,retarder_1,dc_vibrator_1)

if platform=='linux':
  from concrete.imitation import iMOTOR,iGATE,iVALVE,iWEIGHT,iROTARYFLOW

  imotor_1 = iMOTOR(simple=True,on=plc.MIXER_ON_1,ison=plc.MIXER_ISON_1)
  igate_1 = iGATE(open = plc.MIXER_OPEN_1,close=~plc.MIXER_OPEN_1,opened = plc.MIXER_OPENED_1,closed=plc.MIXER_CLOSED_1)  
  imixer_i_1 = iWEIGHT(loading=plc.DCEMENT_OPEN_1,unloading=~plc.MIXER_CLOSED_1,q=plc.MIXER_I_1)
  
  idcement_1 = iVALVE(open = plc.DCEMENT_OPEN_1,closed = plc.DCEMENT_CLOSED_1)
  isilage_1 = iMOTOR(simple=True, on = plc.AUGER_ON_1,ison = plc.AUGER_ISON_1)
  icement_m_1 = iWEIGHT( loading=plc.AUGER_ON_1,unloading=plc.DCEMENT_OPEN_1, q = plc.CEMENT_M_1 )
  
  idwater_1 = iVALVE(open = plc.DWATER_OPEN_1,closed = plc.DWATER_CLOSED_1)
  iwpump_1 = iMOTOR(simple=True, on = plc.WPUMP_ON_1,ison = plc.WPUMP_ISON_1)
  iwater_m_1 = iWEIGHT( loading=plc.WPUMP_ON_1,unloading=plc.DWATER_OPEN_1, q = plc.WATER_M_1 )

  idadditions_1 = iVALVE(open = plc.DADDITIONS_OPEN_1,closed = plc.DADDITIONS_CLOSED_1)
  iapump_1 = iMOTOR(simple=True,on=plc.APUMP_ON_1,ison=plc.APUMP_ISON_1 )
  iadditions_m_1 = iWEIGHT( loading=plc.APUMP_ON_1,unloading=plc.DADDITIONS_OPEN_1, q = plc.ADDITIONS_M_1 )
  
  iapump_2 = iMOTOR(simple=True,on=plc.APUMP_ON_2,ison=plc.APUMP_ISON_2 )
  iaddition_q_2 = iROTARYFLOW( loading=plc.APUMP_ON_2,q = plc.ADDITION_Q_2)

  iconveyor_1 = iMOTOR(simple=True,on = plc.CONVEYOR_ON_1,ison = plc.CONVEYOR_ISON_1 )
  itconveyor_1 = iMOTOR(simple=True,on = plc.TCONVEYOR_ON_1,ison = plc.TCONVEYOR_ISON_1 )
  ifillers_m_1 = iWEIGHT( loading=lambda: plc.FILLER_OPEN_1 or plc.FILLER_OPEN_2 or plc.FILLER_OPEN_3,unloading=plc.CONVEYOR_ON_1, q = plc.FILLERS_M_1 )
  ifiller_1 = iVALVE(open = plc.FILLER_OPEN_1,closed=plc.FILLER_CLOSED_1)
  ifiller_2 = iVALVE(open = plc.FILLER_OPEN_2,closed=plc.FILLER_CLOSED_2)
  ifiller_3 = iVALVE(open = plc.FILLER_OPEN_3,closed=plc.FILLER_CLOSED_3)

  instances = (imixer_i_1,imotor_1, igate_1, idcement_1, isilage_1, icement_m_1, idwater_1, iwater_m_1, iconveyor_1, itconveyor_1,
                           ifillers_m_1, idadditions_1, iadditions_m_1, iapump_1, iapump_2, iaddition_q_2, ifiller_1, ifiller_2, ifiller_3, iwpump_1)+instances


plc.run( instances=instances, ctx=globals() )
