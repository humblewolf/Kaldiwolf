"""
Author: humblewolf
Description: <write description here...>
"""

from multiprocessing import Process, Queue
from threading import Thread

q = Queue()

def runA():
    counter = 100
    while True:
        try:
            print('A\n')
            msg = q.get(block=False)
            if msg:
                print(len(msg))
            counter -= 1
        except:
            pass

# def runB():
#     counter1 = 100
#     while counter1:
#         counter1 -= 1
#         print('B\n')


#if __name__ == "main":
t1 = Thread(target = runA)
t1.setDaemon(True)
t1.start()
# t2 = Thread(target = runB)
# #t2.setDaemon(True)
# t2.start()
counter3 = 100
while counter3:
    counter3 -= 1
    print('C\n')

#t1.join()