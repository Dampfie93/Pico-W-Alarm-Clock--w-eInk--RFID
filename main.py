from dfplayer import *
from eink2in9 import *
from rc522      import *
from utils      import *
from webserver  import *
from alarm_manager import Alarm

from time import sleep, time
import machine  #type: ignore
import _thread

led_onboard = machine.Pin('LED', machine.Pin.OUT, value=0)
display = Display()
player = DFPlayer(uartInstance=0, txPin=16, rxPin=17, busyPin=20)
keys = [Key(0, pin=2), Key(1, pin=3), Key(2, pin=15)]

MAIN_STATE = None

def testAlarmList():
    alarm_list_init = [
        # Alarm(True, time()+20,  0),
        # Alarm(True, time()+7200, 1, "1111111")
    ]
    Alarm.setAlarmListtoJson(alarm_list_init)

def init():
    Alarm.getAlarmListfromJson()
    log ("DEBUG",  f"ALARMS: {len(Alarm.alarm_list)}")
    log ("DEBUG",  f"RFIDS: {len(RFIDManager.rfids)}")
    log ("DEBUG", f"{convert_unix('date')}")
    display.show("hello", True)

    # server.run()
    state("time")

def state(state=None):
    global MAIN_STATE

    if state is None:
        return MAIN_STATE
    
    if state == "alarm":
        display.show("alarm", True)

    elif state == "alarm_off":
        display.show("alarm_off", True)
        log("ALARM", f"disarmed")

    elif state == "time":
        display.show("time", False)

    MAIN_STATE = state


def main():     
    restart=True
    while restart:
        restart = False
        # Check if time is correct every hour
        if time() % 3600 == 0:
            setTimeAPI()
        # Check if alarm list is updated every minute
        if time() % 60 == 0:
            Alarm.getAlarmListfromJson()
        # Check if alarm is active
        if state() != "alarm":
            if Alarm.checkList():
                state("alarm")
        
        # Check if key is pressed
                
        # Update Time
        if state() == "time":
            display.update_time()

        # Alarm State
        elif state() == "alarm":
            print(f"[{convert_unix('time')}] [ALARM] wartet auf rfid")
            if RFIDManager.check():
                state("alarm_off")
                state("time")
        sleep(0.25)
        blinkLED()
        restart = True


def blinkLED():
    if time() % 2 == 0:
        led_onboard.on()
    else:
        led_onboard.off()


if __name__ == "__main__":
    if not connect_wifi():
        core1 = _thread.start_new_thread(start, ("ap", ))
    else:
        setTimeAPI()
        core1 = _thread.start_new_thread(start, ("sta", ))
    init()
    main()
    # if not connect_wifi():
    #     start("ap")
    # else:
    #     setTimeAPI()
    #     start("app")