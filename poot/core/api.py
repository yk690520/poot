#通过poot获取到将节点信息进行解析
from shutil import rmtree
from xml.dom.minidom import parse
import os
from io import StringIO
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
    def __init__(self,device_id:str=None,screenshot_each_action=False):
        self._device_id=device_id #当前设备的连接id
        if not device_id:
            #主动获取device_id
            devices = ADB.getNowConnectDevice()
            if len(devices) > 0:
                self._device_id=devices[0]
            else:
                raise BaseException("无设备连接！")
            pass
        self._is_freeze=False  #是否处于冻结ui状态
        self._node=None  #ui信息
        self._adb=ADB(self._device_id) #adb 实例
        self._time_out=2#获取ui的超时时间
        self._sleep_spacing=1#单次获取ui睡眠间隔
        self._screenshot_each_action=screenshot_each_action

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
            proxy = self.__resolve_node(self._node,self._screenshot_each_action)
            proxy=proxy.offspring(**kwargs)
            if not proxy:
                raise BaseException(NOT_FOUND_UI)
            return proxy
        else:
            # 返回根节点代理ui
            return self.__resolve_node(self._node,self._screenshot_each_action)

    def freeze(self):
        self._is_freeze=True
        self.__get_ui()
        return self

    def clear_freezed(self):
        self._is_freeze=False
        return self

    def unfreeze(self):
        self._is_freeze = False
        return self

    def __enter__(self):
        self._is_freeze = True
        self.__get_ui()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._is_freeze=False
    def __resolve_node(self,node,screenshot_each_action:bool)->UiProxy:
        #传入xml文件信息，并解析其节点信息存储至node
        return UiProxy(node,self._adb,screenshot_each_action)
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

    @property
    def adb(self):
        return self._adb

    def get_ui(self):
        '''
        返回xml文件内容
        :return:
        '''
        return self().get_tree()


    @inforPrint(infor="返回桌面")
    def return_home(self,*,infor=None,beforeTime=0,endTime=0):
        '''
        回到桌面
        :return:
        '''
        self._adb.returnHome()

    @inforPrint(infor="滚动")
    def scroll(self, direction='vertical', percent=0.6, duration=2000,*,infor=None,beroeTime=0,endTime=0):
        """
        来自airtest的源代码
        :param direction:滑动方向
        :param percent:滑动百分比
        :param duration:滑动时间
        """
        if direction not in ('vertical', 'horizontal'):
            raise ValueError('Argument `direction` should be one of "vertical" or "horizontal". Got {}'
                             .format(repr(direction)))
        x1,x2,y1,y2=0.5,0.5,0.5,0.5
        half_distance = percent / 2
        if direction == 'vertical':
            y1+=half_distance
            y2-=half_distance
        else:
            x1+=half_distance
            x2-=half_distance
        return self.swipe(x1,y1,x2,y2,time=duration)


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
        x1,y1=width*x1,hight*y1
        x2,y2=width*x2,hight*y2
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
