from shared_state import SharedState
from driver import driver_loop
from app import FlaskApp
from threading import Thread, Event
import signal
import sys
from time import sleep

if __name__ == "__main__":
    #shared instance of state because driver and flask need to communicate only about this
    shared_state = SharedState()
    
    stop_event = Event()
    
    driver_thread = Thread(target=driver_loop, args=(shared_state, stop_event))
    driver_thread.start()
    
    app = FlaskApp(shared_state)
    app.daemon = True
    app.start()
    
    def signal_handler(signum, frame):
        print("\nStopping threads")
        stop_event.set()
        driver_thread.join()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)
