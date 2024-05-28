from multiprocessing import Process
import matplotlib.pyplot as plt
import inquirer
import os
import sys
from pprint import pprint
from pick import pick
# from main2 import f1
import main2 as m

def f2(name):
    print('hello', name)
    print('....................')
    sys.path.append(os.path.realpath("."))

    # questions = [
    #     inquirer.Confirm('continue',
    #                 message="Should I continue"),
    #     inquirer.Confirm('stop',
    #                 message="Should I stop", default=True),
    # ]

    # answers = inquirer.prompt(questions)

    # pprint(answers)

    title = 'Please choose an option: '
    options = [{'label': 'option1'}, {'label': 'option2'}, {'label': 'option3'}]
    def get_label(option): return option.get('label')
  
    selected = pick(options, title, indicator='>', options_map_func=get_label)
    print(selected)
   

def main_plot():
    procs = []
    p1 = Process(target=m.f1, args=('bob',))
    p1.start()
    procs.append(p1)
    p2 = Process(target=f2, args=('jerry',))    
    p2.start()
    procs.append(p2)
    for p in procs:
         p.join()

    
# if __name__ == '__main__':
#     main_plot()
    # procs = []
    # p1 = Process(target=m.f1, args=('bob',))
    # p1.start()
    # procs.append(p1)
    # p2 = Process(target=f2, args=('jerry',))    
    # p2.start()
    # procs.append(p2)
    # for p in procs:
    #      p.join()

    # print('tyor -----')
    # f1('Duangklang')
    # f2('parinya')
    

    