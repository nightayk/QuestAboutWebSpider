from multiprocessing import Pool
import os

def RunDouBan():
    import DouBan.py

def RunBillBill():
    import BillBill.py
if __name__=='__main__':
    p = Pool(2)
    p.apply_async(RunDouBan)
    p.apply_async(RunBillBill)
    p.close()
    p.join()
    p.join()
    print('所有进程均结束')
