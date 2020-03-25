import os
import subprocess
import re,hashlib
import airtest.core.android.adb as airAdb
from airtest.core.android.ime import YosemiteIme
from io import StringIO
from airtest.core.android.adb import ADB as AirtestADB
#异常
DEVICE_NOT_FOUND="设备已断开连接"
#其它配置
TEMP_UI_XML_SAVE_PATH="%s/uiTemp" % os.getcwd()#ui获取文件
TEMP_XML="%s/temp_xml.xml" % os.getcwd()#临时xml
IME_PATH="%s/core/adb/config/ime.apk" % os.getcwd()
ADB_PATH=airAdb.ADB.builtin_adb_path()
airAdb.LOGGING.disabled=True
class ADB():
    @staticmethod
    def getNowConnectDevice():
        adb_path = "%s" % ADB_PATH
        resault = ADB.__execu_cmd('%s devices' % adb_path).strip()
        f = StringIO(resault)
        deviceList = []
        while True:
            s = f.readline()
            if s == '':
                break
            s = s.split()
            if s != [] and (s[0] != 'List' or s[0]=="*"):
                deviceList.append(s[0])
        if deviceList == []:
            return []
        return deviceList

    def __init__(self,device_id:str):
        self._device_id=device_id
        self._adb_path=ADB_PATH
        self._cmd_prefix=(self._adb_path,"-s",device_id)
        self._airtestADB=AirtestADB(device_id)
        self._ime=YosemiteIme(self._airtestADB)
        self._ime.start()
        self.__width=-1
        self.__height=-1
        # self.__install_ime()

    def __install_ime(self):
        re = self.__exe_shell_cmd("ime","list","-a","-s")
        if "com.android.adbkeyboard/.AdbIME" in re:
            return
        else:
            self.install_app(IME_PATH)

    def __restore_ime(self):
        self.__exe_shell_cmd("ime","set",self._ime,success=self._ime)

    def swipe(self,x1,y1,x2,y2,time):
        '''
        在屏幕上滑动
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :param time: 滑动时间
        :return:
        '''
        self.__exe_shell_cmd("input","swipe",x1, y1,x2,y2,time)


    def input(self,text):
        '''
        直接输入文字
        :param text: 需要输入的文字
        :return: 无返回值
        '''
        #需要输入的test
        self._ime.text(text)

    def set_text(self,will_input_text,now_text:str):
        '''
        先清楚原有的text，再输入
        :param will_input_text:
        :param now_text:
        :return:
        '''
        #将光标置于最前面
        self.tap_move_home()
        #清楚所有字符
        self.tap_del(len(now_text)+1)
        #输入字符
        self._ime.text(will_input_text)

    def install_app(self,path):
        '''
        安装path的apk
        :param path:
        :return:
        '''
        return self.__exe_cmd("install","-r",path,success="Success")

    def get_screen_size(self):
        '''
        获取屏幕分辨率，
        :return: （宽，高)
        '''
        if self.__width==-1:
            display=self._airtestADB.get_display_info()
            width,height=display['width'],display['height']
            self.__width=int(width)
            self.__height=int(height)
        return self.__width,self.__height

    def tap_x_y(self,x,y,times=None):
        '''
        点击【x,y】对应的坐标点
        :param x:
        :param y:
        :return:
        '''
        if times!=None:
            self.__exe_shell_cmd("input","swipe",x,y,x,y,times*1000)
        else:
            self.__exe_shell_cmd("input","tap",x,y)

    def tap_backspace(self):
        '''
        点击退格键
        :return:
        '''
        self.__exe_shell_cmd("input","keyevent","67")

    def tap_return(self):
        '''
        点击返回键
        :return:
        '''
        self.__exe_shell_cmd("input","keyevent","4")

    def tap_move_home(self):
        '''
        将输入光标移至最前面
        :return:
        '''
        self.__exe_shell_cmd("input","keyevent","122")

    def tap_del(self,count=1):
        '''
        点击删除键
        :param count: 次数
        :return:
        '''
        cmd=["input","keyevent"]
        for i in range(0,count):
            cmd.append("112")
        self.__exe_shell_cmd(*cmd)

    def returnHome(self):
        self.__exe_shell_cmd("input","keyevent","3")

    def rm_file(self,file):
        self.__exe_shell_cmd("rm",file)

    def pull_file_to_dsc(self,src_file,dsc):
        '''
        将src_file提取到电脑上的dsc文件夹
        :param src_file:
        :param dsc:
        :return:
        '''
        self.__exe_cmd("pull",src_file,dsc,success="pulled")

    def get_imei(self):
        res=self.__exe_shell_cmd("service","call","iphonesubinfo","1")
        imei1 = (re.compile(r"'[\.]+((\d\.)+)'").findall(res))[0][0]
        imei2 = (re.compile(r"'((\d\.)+)'").findall(res))[0][0]
        imei3 = (re.compile(r"'((\d\.)+).+ +'").findall(res))[0][0]
        imei1 = "".join(imei1.split("."))
        imei2 = "".join(imei2.split("."))
        imei3 = "".join(imei3.split("."))
        imei = imei1 + imei2 + imei3
        return imei


    def rm_computer_file(self,file):
        '''
        删除电脑上的文件
        :param file:
        :return:
        '''
        if os.path.exists(file):
            os.remove(file)

    def getNowUI(self):
        '''
        如果没有成功取得ui文件，则返回False
        :return:
        '''
        #结束pocoservice
        # self.__make_shell_by_pope('am force-stop com.netease.open.pocoservice')
        self.__exe_shell_cmd("rm","/mnt/sdcard/%s.xml" % self._device_id)
        self.__exe_shell_cmd("uiautomator","dump","/mnt/sdcard/%s.xml" % self._device_id)
        if os.path.exists(TEMP_UI_XML_SAVE_PATH):
            if os.path.exists("%s/%s.xml" % (TEMP_UI_XML_SAVE_PATH,self._device_id)):
                os.remove("%s/%s.xml" % (TEMP_UI_XML_SAVE_PATH,self._device_id))
        else:
            os.mkdir(TEMP_UI_XML_SAVE_PATH)
        if self.__exe_cmd("pull","/mnt/sdcard/%s.xml" % self._device_id,TEMP_UI_XML_SAVE_PATH,success="pulled"):
            self.__exe_shell_cmd("rm","/mnt/sdcard/%s.xml" % self._device_id)
            return True
        return False


    def __exe_cmd(self,*cmd,success=None):
        '''
        执行cmd
        :param cmd:
        :param success:
        :return:
        '''
        cmd = self.__building_cmd(*cmd)
        resault = self.__execu_cmd(cmd)
        resault = resault.strip()
        self.__check_device_not_connect()
        if success != None:
            if success in resault:
                return True
            else:
                return False
        return resault


    def __exe_shell_cmd(self,*cmd,success=None):
        '''
        执行cmd
        :param cmd:
        :param success:如果传入success，则表示结果中包含success才执行成功
        :return:
        '''
        cmd = self.__building_cmd("shell",*cmd)
        resault = self.__execu_cmd(cmd)
        resault = resault.strip()
        self.__check_device_not_connect()
        if success!=None:
            if success in resault:
                return True
            else:
                return False
        return resault




    def __building_cmd(self,*args):
        '''
        构造cmd
        :param args:
        :return:
        '''
        cmdTuple=self._cmd_prefix+args
        cmdList=[]
        for word in cmdTuple:
            word=str(word)
            if " " in word:
                cmdList.append('"%s"' % word)
            else:
                cmdList.append(word)
        return " ".join(cmdList)



    @staticmethod
    def __execu_cmd(cmd:str):
        '''
        执行cmd
        :return:
        '''
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   errors='ignore')
        process.wait()
        resault=process.stdout.read()
        process.stdout.close()
        process.stdin.close()
        return resault

    def __check_device_not_connect(self):
        '''
        检查设备是否连接
        :return:
        '''
        devices=ADB.getNowConnectDevice()
        if self._device_id not in devices:
            raise BaseException(DEVICE_NOT_FOUND)

    @property
    def device_id(self):
        return self._device_id

