import time
import threading

from robot.panel import start_panel
from robot.loops.sensors_loop import sensors_loop

def main():
    print("Robot start")
    threading.Thread(target=sensors_loop, daemon=True).start()
    start_panel(port=7123)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()





























