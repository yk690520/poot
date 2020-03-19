#通过poot获取到将节点信息进行解析
from shutil import rmtree
from xml.dom.minidom import parse
import time,os

from io import StringIO

from airtest.core.android.ime import YosemiteIme

from ..adb.adb import ADB,ADB_PATH,TEMP_UI_XML_SAVE_PATH
from .uIProxy import Node
from . import NOT_FOUND_UI
from .uIProxy import UiProxy
from . import inforPrint
from . import by as By
class Poot():
    @staticmethod
    def getNowConnectDevice():
        adb_path = "%s" % ADB_PATH
        str = os.popen('%s devices' % adb_path)
        str = str.read()
        f = StringIO(str)
        deviceList = []
        while True:
            s = f.readline()
            if s == '':
                break
            s = s.split()

            if s != [] and (s[0] != 'List' or s[0]=='*'):
                deviceList.append([s[0],s[1]])
        if deviceList == []:
            return []
        return deviceList
    def __init__(self,device_id:str):
        self._device_id=device_id #当前设备的连接id
        self._is_freeze=False  #是否处于冻结ui状态
        self._node=None  #ui信息
        self._adb=ADB(self._device_id) #adb 实例
        self._time_out=2#获取ui的超时时间
        self._sleep_spacing=1#单次获取ui睡眠间隔

    def __get_sleep_count(self,time_out:int=None):
        if time_out==None:
            return self._time_out/self._sleep_spacing
        else:
            return time_out/self._sleep_spacing

    def __get_ui(self):
        '''
        获取ui
        :return:
        '''
        count=1
        while count<3:
            if not self._adb.getNowUI():
                count+=1
                continue
            xml = "%s/%s.xml" % (TEMP_UI_XML_SAVE_PATH, self._device_id)
            if os.path.exists(xml):
                DomTree = parse(xml)
                root_Node = DomTree.documentElement
                node = Node(root_Node)
                rmtree(os.path.dirname(xml))
                self._node=node
                return True
        raise BaseException("获取UIxml文件失败")

    def __call__(self,text=None,time_out:int=None,*,resource_id=None,package=None,clazz=None,desc=None,name=None,part_text=None,**kwargs)->UiProxy:
        '''
        :param infor:
        :param by:
        :param time: ui查找时间
        :rtype:UiProxy
        :return:
        '''
        if resource_id:
            kwargs["resource_id"]=resource_id
        if package:
            kwargs["package"]=package
        if clazz:
            kwargs["clazz"]=clazz
        if desc:
            kwargs["desc"]=desc
        if name:
            kwargs["name"]=name
        if text:
            kwargs["text"]=text
        if part_text:
            kwargs["part_text"]=part_text
        if (not self._is_freeze) or (not self._node):
            # 如果ui不是冻结的
            self.__get_ui()
            if kwargs:
                # 返回对应的节点代理ui
                proxy = self.__resolve_node(self._node)
                proxy=proxy.offspring(**kwargs)
                if not proxy:
                    raise BaseException(NOT_FOUND_UI)
                return proxy
            else:
                # 返回根节点代理ui
                return self.__resolve_node(self._node)

        else:
            #如果是冻结的
            if not self._node:
                raise BaseException(NOT_FOUND_UI)
            if text or kwargs:
                # 返回对应的节点代理ui
                proxy = self.__resolve_node(self._node)
                proxy = proxy.offspring(**kwargs)
                if not proxy:
                    raise BaseException(NOT_FOUND_UI)
                return proxy
            else:
                # 返回根节点代理ui
                return self.__resolve_node(self._node)
    def freeze(self):
        self._is_freeze=True
        return self

    def clear_freezed(self):
        self._is_freeze=False
        return self

    def __enter__(self):
        self._is_freeze = True
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._is_freeze=False
    def __resolve_node(self,node)->UiProxy:
        #传入xml文件信息，并解析其节点信息存储至node
        return UiProxy(node,self._adb)
    def set_find_ui_timeout(self,timeout):
        '''
        设置获取ui的超时时间
        :param timeout:
        :return:
        '''
        self._time_out=timeout
    def set_find_ui_time_spacing(self,time_spacing):
        '''
        设置获取ui睡眠间隔时间
        :param time_spacing:
        :return:
        '''
        self._sleep_spacing=time_spacing
    @property
    def device_id(self):
        return self._device_id
    @inforPrint(infor="返回桌面")
    def return_home(self,*,infor=None,beforeTime=0,endTime=0):
        '''
        回到桌面
        :return:
        '''
        self._adb.returnHome()
    @inforPrint(infor="获取微信数据库")
    def get_wx_databases(self,dsc,*,infor=None,beforeTime=0,endTime=0):
        return self._adb.get_wx_databases(dsc)
    @inforPrint(infor="等待UI出现")
    def wait_ui_appear(self,value,by:By=By.text,wait_time:int=30,*,infor=None,beroeTime=0,endTime=0):
        try:
            ui=self(infor=value,by=by,time_out=wait_time)
            if ui:
                return True
        except:
            return False
    @inforPrint(infor="滑动")
    def swipe(self,x1:float,y1:float,x2:float,y2:float,time:int=200,*,infor=None,beroeTime=0,endTime=0):
        '''
        按照比例进行滑动
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :param time:
        :param infor:
        :param beroeTime:
        :param endTime:
        :return:
        '''
        width, hight = self._adb.get_screen_size()#获得屏幕宽高
        x1=width*x1
        y1=hight*y1
        x2=width*x2
        y2=width*y2
        self._adb.swipe(x1,y1,x2,y2,time)
    @inforPrint(infor="点击")
    def tap_x_y(self,x:float,y:float,times:int=None,*,infor=None,beroeTime=0,endTime=0):
        '''
        均按照比例进行点击。
        :param x: 0-1的数
        :param y: 0-1的数
        :param infor:
        :param beroeTime:
        :param endTime:
        :param times:点击时长
        :return:
        '''
        width,hight=self._adb.get_screen_size()
        x=width*x
        y=hight*y
        self._adb.tap_x_y(x,y,times)
    @inforPrint(infor="获得屏幕尺寸")
    def get_screen_size(self,*,infor=None,beroeTime=0,endTime=0):
        return self._adb.get_screen_size()
    @inforPrint(infor="输入文字")
    def input(self,text,*,infor=None,beroeTime=0,endTime=0):
        '''
        本方法需要先获取输入框的焦点
        :param text:
        :param infor:
        :param beroeTime:
        :param endTime:
        :return:
        '''
        self._adb.input(text)
