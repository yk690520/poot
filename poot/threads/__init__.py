#多线程操作模块
import threading

import functools,time
from ..core.api import Poot
_func=None
_writing_time=10

def set_writing_time(time:int):
    '''
    设置等待设备进入的时间，默认为10s
    :param time:
    :return:
    '''
    global _writing_time
    _writing_time=time
def poot_thread(funx):
    '''
    脚本方法设置的装饰器方法
    :param funx:
    :return:
    '''
    @functools.wraps(funx)
    def wrapper(*args,**kwargs):
        global _func
        _func=funx
    return wrapper()
def run():
    global _func,_writing_time
    deviceList = []
    count=0
    while True:
        if not _func:
            raise BaseException("未设置要执行的脚本方法,请使用装饰器poot_thread进行设置")
        # 主线程，用来守护新的设备
        temp_deviceList = Poot.getNowConnectDevice()
        for device in temp_deviceList:
            if device[0] not in deviceList:
                if device[1]!="unauthorized":
                    count=0
                    deviceList.append(device[0])
                    threading.Thread(target=_func, args=(device[0],)).start()
        time.sleep(2)
        count+=2
        if count>=_writing_time:
            break


