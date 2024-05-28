import pickle
import rootpath
import os
import threading
import multiprocessing
import settings
from db_record_management import main_db_management
from main_menu import show_mainmenu
from window_app import open_windows_app


def loadstore():
    with open("".join([rootpath.detect(),"/App/tmnamebuffer.pickle"]), 'rb') as handle:
        b = pickle.load(handle)
    return b['tmname']

# clear_console = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

def runmain():
    settings.tm_name = loadstore()
    main_db_management()
    show_mainmenu()


def runwindowapp():
    open_windows_app()
    settings.tm_name = loadstore()
    main_db_management()


if __name__ == "__main__":
    open_windows_app()
    # settings.init()
    # settings.tm_name = loadstore()
    # # print("Run--->")
    # main_db_management()
    # show_mainmenu()


    # t1 = threading.Thread(target= runwindowapp)
    # t1.start()
    # t2 = threading.Thread(target=show_mainmenu)
    # t2.start()
    # t1.join()
    # t2.join()
    # # show_mainmenu()
    