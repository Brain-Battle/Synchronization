from muselsl import stream, list_muses, view, view_with_address
from multiprocessing import Process
import sys
from time import sleep

if __name__ == "__main__":
    muses = list_muses()

    stream_processes = []
    view_processes = []

    if muses:
        try:
            for i, muse in enumerate(muses):
                print(f"Connecting to: {muse['address']}")
                stream_processes.append(Process(target=stream, args=(muse["address"], )))
                view_processes.append(Process(target=view_with_address, args=(muse["address"],5, 20, 0.4, "15x6", 2)))
                stream_processes[i].start()

            sleep(10)

            for v in view_processes:
                v.start()

            while True:
                sleep(1)

        except KeyboardInterrupt:
            for v in view_processes:
                if v.is_alive():
                    v.kill()

            for s in stream_processes:
                if s.is_alive():
                    s.kill()
            
            sys.exit(0)


        