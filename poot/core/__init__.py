import time,functools
#异常
NOT_FOUND_UI="未找到对应ui控件"
def inforPrint(infor,beforeTime=0,endTime=0):
    def decorator(fux):
        functools.wraps(fux)
        def wrapper(self,*args,**kwargs):
            tempInfor=infor
            if 'infor' in kwargs:
                if kwargs['infor']!=None:
                    tempInfor=kwargs['infor']
            print(self.device_id+'：'+tempInfor)
            tempBeforeTime=beforeTime
            if 'beforeTime' in kwargs:
                if kwargs['beforeTime']!=0:
                    tempBeforeTime=kwargs['beforeTime']
            time.sleep(tempBeforeTime)
            re=fux(self,*args,**kwargs)
            tempEndTime=endTime
            if 'endTime' in kwargs:
                if kwargs['endTime']!=0:
                    tempEndTime=kwargs['endTime']
            time.sleep(tempEndTime)
            return re
        return wrapper
    return decorator