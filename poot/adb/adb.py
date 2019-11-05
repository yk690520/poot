import os
import poot.adb as adb
import re,hashlib
import poot.tools as tools
from io import StringIO
class ADB():
    @staticmethod
    def getNowConnectDevice():
        adb_path = "%s" % adb.ADB_PATH
        str = os.popen('%s devices' % adb_path)
        str = str.read()
        f = StringIO(str)
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
        self._adb_path="%s" % adb.ADB_PATH
        self._cmd_prefix="%s -s %s " % (self._adb_path,device_id)
        self.__install_ime()
        self._ime=None
    def __install_ime(self):
        re = self.__make_shell_by_pope_return_re("ime list -a -s")
        if "com.android.adbkeyboard/.AdbIME" in re:
            return
        else:
            self.install_app(adb.IME_PATH)
    def __change_ime(self):
        self._ime = self.__make_shell_by_pope_return_re("ime list -s").split("\n")[0]
        self.__make_shell_by_pope_return_sucess("ime set com.android.adbkeyboard/.AdbIME",sucess="com.android.adbkeyboard/.AdbIME")

    def __restore_ime(self):
        self.__make_shell_by_pope_return_sucess("ime set %s" % self._ime,
                                                sucess=self._ime)
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
        self.__make_shell_by_pope("input swipe %s %s %s %s %s", x1, y1,x2,y2,time)





    def input(self,text):
        '''
        直接输入文字
        :param text: 需要输入的文字
        :return: 无返回值
        '''
        self.__change_ime()
        #需要输入的test
        self.__make_shell_by_pope("am broadcast -a ADB_INPUT_TEXT --es msg '%s'",text)
        self.__restore_ime()

    def set_key(self,will_input_text,now_text):
        '''
        先清楚原有的text，再输入
        :param will_input_text:
        :param now_text:
        :return:
        '''
        for n in now_text:
            self.tap_backspace()
        self.__change_ime()
        self.__make_shell_by_pope("am broadcast -a ADB_INPUT_TEXT --es msg '%s'", will_input_text)
        self.__restore_ime()



    def install_app(self,path):
        '''
        安装path的apk
        :param path:
        :return:
        '''
        return self.__make_cmd_by_pope_return_sucess("install -r %s",path,sucess="Success")


    def get_screen_size(self):
        '''
        获取屏幕分辨率，
        :return: （宽，高)
        '''
        width,hight=self.__make_shell_by_pope_return_re("wm size").split(":")[1].split("x")
        return int(width),int(hight)
    def tap_x_y(self,x,y):
        '''
        点击【x,y】对应的坐标点
        :param x:
        :param y:
        :return:
        '''
        self.__make_shell_by_pope("input tap %s %s",x,y)
    def tap_backspace(self):
        '''
        点击退格键
        :return:
        '''
        self.__make_shell_by_pope("input keyevent 67")
    def tap_return(self):
        '''
        点击返回键
        :return:
        '''
        self.__make_shell_by_pope("input keyevent 4")

    def returnHome(self):
        self.__make_cmd_by_pope("shell input keyevent 3")
    def rm_file(self,file):
        self.__make_shell_by_pope("rm %s" % file)
    def cp_src_file_to_dsc(self,src_file,dsc):
        '''
        将手机指定文件移动到指定位置
        :param src_file:
        :param dsc_file:
        :return:
        '''
        self.__make_shell_su_by_pope("cp %s %s",src_file,dsc)
    def pull_file_to_dsc(self,src_file,dsc):
        '''
        将src_file提取到电脑上的dsc文件夹
        :param src_file:
        :param dsc:
        :return:
        '''
        self.__make_cmd_by_pope_return_sucess('pull %s %s' % (src_file,dsc),sucess="pulled")
    def get_imei(self):
        res=self.__make_shell_by_pope_return_re("service call iphonesubinfo 1")
        imei1 = (re.compile(r"'[\.]+((\d\.)+)'").findall(res))[0][0]
        imei2 = (re.compile(r"'((\d\.)+)'").findall(res))[0][0]
        imei3 = (re.compile(r"'((\d\.)+).+ +'").findall(res))[0][0]
        imei1 = "".join(imei1.split("."))
        imei2 = "".join(imei2.split("."))
        imei3 = "".join(imei3.split("."))
        imei = imei1 + imei2 + imei3
        return imei
    def get_wx_databases(self,src):
        '''
        将微信数据库提取至【src】目录,并计算其数据库密码
        :param src:
        :return:
        '''
        resautl=self.__make_shell_su_by_pope_return_re("ls /data/data/com.tencent.mm/MicroMsg")
        databases_path="/data/data/com.tencent.mm/MicroMsg/%s/EnMicroMsg.db" % resautl.split("\n\n")[0]
        self.cp_src_file_to_dsc(databases_path,"/mnt/sdcard/micro_db.db")
        self.pull_file_to_dsc("/mnt/sdcard/micro_db.db",src)
        self.rm_file("/mnt/sdcard/micro_db.db")
        self.cp_src_file_to_dsc("/data/data/com.tencent.mm/shared_prefs/system_config_prefs.xml","/mnt/sdcard/prefs.xml")
        self.rm_computer_file(adb.TEMP_XML)
        self.pull_file_to_dsc("/mnt/sdcard/prefs.xml",adb.TEMP_XML)
        self.rm_file("/mnt/sdcard/prefs.xml")
        with open(adb.TEMP_XML) as file:
            strs=file.read()
        uid=(re.compile(r'_uin" value="([-]*[\d]+)"').findall(strs))[0]
        self.rm_computer_file(adb.TEMP_XML)
        imei=self.get_imei()
        m2 = hashlib.md5()
        m2.update(("%s%s" % (imei,uid)).encode("utf-8"))
        return m2.hexdigest()[:7]
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
        self.__make_cmd_by_pope('shell rm /mnt/sdcard/%s.xml', self._device_id)
        count=1
        while True:
            self.__make_shell_by_pope('uiautomator dump /mnt/sdcard/%s.xml', self._device_id)
            if self.__make_shell_by_pope_onle_return_sucess('ls /mnt/sdcard/%s.xml',self._device_id,sucess='/mnt/sdcard/%s.xml' % self._device_id):
                break
            count+=1
            if count>=5:
                return False
        if os.path.exists(adb.TEMP_UI_XML_SAVE_PATH):
            if os.path.exists("%s/%s.xml" % (adb.TEMP_UI_XML_SAVE_PATH,self._device_id)):
                os.remove("%s/%s.xml" % (adb.TEMP_UI_XML_SAVE_PATH,self._device_id))
        else:
            os.mkdir(adb.TEMP_UI_XML_SAVE_PATH)
        if self.__make_cmd_by_pope_return_sucess('pull /mnt/sdcard/%s.xml %s',self._device_id, adb.TEMP_UI_XML_SAVE_PATH,sucess="pulled"):
           self.__make_cmd_by_pope('shell rm /mnt/sdcard/%s.xml', self._device_id)
           return True
        return False

    def __make_cmd_by_pope(self,cmd,*args):
        '''
        无需返回结果，只要执行则认为成功
        :param cmd:shell
        :param args:
        :return:
        '''
        if (args!=None):
            cmd=self._cmd_prefix+(cmd % args)
        tools.get_logger().info(cmd)
        resault=os.popen(cmd)
        resault=resault.read()
        resault = resault.strip()
        self.__check_device_not_connect()
        if resault=="":
            return True
        else:
            return False
    def __make_cmd_by_pope_return_sucess(self,cmd,*args,sucess):
        '''
        此方法需要返回包含指定的sucess，否则认为执行失败
        :param cmd:
        :param args:
        :param sucess:
        :return:
        '''
        if (args!=None):
            cmd = self._cmd_prefix + (cmd % args)
        tools.get_logger().info(cmd)
        resault=os.popen(cmd)
        resault=resault.read()
        if sucess!=None:
            resault=resault.strip()
            self.__check_device_not_connect()
            if sucess in resault:
                return True
            else:
                return False
        return False
    def __make_cmd_by_pope_return_true_or_false(self,cmd,*args):
        '''
        只有有结果返回，即认为执行成功
        :param cmd:
        :param args:
        :return:
        '''
        if (args != None):
            cmd = self._cmd_prefix + (cmd % args)
        tools.get_logger().info(cmd)
        resault = os.popen(cmd)
        resault = resault.read()
        if resault:
            self.__check_device_not_connect()
            return True
        else:
            return False
    def __make_cmd_by_pope_return_re(self,cmd,*args):
        '''
        此方法返回执行后的结果
        :param cmd:
        :param args:
        :return:
        '''
        if (args != None):
            cmd = self._cmd_prefix + (cmd % args)
        tools.get_logger().info(cmd)
        resault = os.popen(cmd)
        resault = resault.read()
        if resault:
            self.__check_device_not_connect()
            return str(resault).strip()
    def __make_shell_su_by_pope(self,cmd,*args):
        '''
        无需返回结果，只要执行返回“”则认为成功，否则认为失败
        :param cmd:shell
        :param args:
        :return:
        '''
        cmd_prefix=self._cmd_prefix+"shell su -c \""
        if (args!=None):
            cmd=cmd_prefix+(cmd % args)+"\""
        tools.get_logger().info(cmd)
        resault=os.popen(cmd)
        resault=resault.read()
        resault = resault.strip()
        self.__check_device_not_connect()
        if resault=="":
            return True
        else:
            return False
    def __make_shell_su_by_pope_return_sucess(self,cmd,*args,sucess):
        '''
        此方法需要返回指定的sucess，否则认为执行失败
        :param cmd:
        :param args:
        :param sucess:
        :return:
        '''
        cmd_prefix = self._cmd_prefix + "shell su -c \""
        if (args!=None):
            cmd = cmd_prefix + (cmd % args)+"\""
        tools.get_logger().info(cmd)
        resault=os.popen(cmd)
        resault=resault.read()
        if sucess!=None:
            resault=resault.strip()
            self.__check_device_not_connect()
            if sucess in resault:
                return True
            else:
                return False
        return False
    def __make_shell_su_by_pope_return_true_or_false(self,cmd,*args):
        '''
        只有有结果返回，即认为执行成功
        :param cmd:
        :param args:
        :return:
        '''
        cmd_prefix = self._cmd_prefix + "shell su -c \""
        if (args != None):
            cmd = cmd_prefix + (cmd % args)+"\""
        tools.get_logger().info(cmd)
        resault = os.popen(cmd)
        resault = resault.read()
        if resault:
            self.__check_device_not_connect()
            return True
        else:
            return False
    def __make_shell_su_by_pope_return_re(self,cmd,*args):
        '''
        此方法返回执行后的结果
        :param cmd:
        :param args:
        :return:
        '''
        cmd_prefix=self._cmd_prefix + "shell su -c \""
        if (args != None):
            cmd = cmd_prefix + (cmd % args)+"\""
        tools.get_logger().info(cmd)
        resault = os.popen(cmd)
        resault = resault.read()
        if resault:
            self.__check_device_not_connect()
            return str(resault).strip()
    def __make_shell_by_pope(self,cmd,*args):
        '''
        无需返回结果，只要执行则认为成功
        :param cmd:shell
        :param args:
        :return:
        '''
        cmd_prefix = self._cmd_prefix + "shell "
        if (args!=None):
            cmd=cmd_prefix+(cmd % args)
        tools.get_logger().info(cmd)
        resault=os.popen(cmd)
        resault=resault.read()
        resault = resault.strip()
        self.__check_device_not_connect()
        if resault=="":
            return True
        else:
            return False
    def __make_shell_by_pope_return_sucess(self,cmd,*args,sucess):
        '''
        此方法需要返回包含指定的sucess，否则认为执行失败
        :param cmd:
        :param args:
        :param sucess:
        :return:
        '''
        cmd_prefix = self._cmd_prefix + "shell "
        if (args!=None):
            cmd = cmd_prefix + (cmd % args)
        tools.get_logger().info(cmd)
        resault=os.popen(cmd)
        resault=resault.read()
        if sucess!=None:
            resault=resault.strip()
            self.__check_device_not_connect()
            if sucess in resault:
                return True
            else:
                return False
        return False
    def __make_shell_by_pope_return_true_or_false(self,cmd,*args):
        '''
        只有有结果返回，即认为执行成功
        :param cmd:
        :param args:
        :return:
        '''
        cmd_prefix = self._cmd_prefix + "shell "
        if (args != None):
            cmd = cmd_prefix+ (cmd % args)
        tools.get_logger().info(cmd)
        resault = os.popen(cmd)
        resault = resault.read()
        if resault:
            self.__check_device_not_connect()
            return True
        else:
            return False
    def __make_shell_by_pope_return_re(self,cmd,*args):
        '''
        此方法返回执行后的结果
        :param cmd:
        :param args:
        :return:
        '''
        cmd_prefix= self._cmd_prefix + "shell "
        if (args != None):
            cmd = cmd_prefix + (cmd % args)
        tools.get_logger().info(cmd)
        resault = os.popen(cmd)
        resault = resault.read()
        if resault:
            self.__check_device_not_connect()
            return str(resault).strip()
    def __make_shell_by_pope_onle_return_sucess(self,cmd,*args,sucess):
        '''
        此方法需要返回指定的sucess，否则认为执行失败
        :param cmd:
        :param args:
        :param sucess:
        :return:
        '''
        cmd_prefix = self._cmd_prefix + "shell "
        if (args!=None):
            cmd = cmd_prefix + (cmd % args)
        tools.get_logger().info(cmd)
        resault=os.popen(cmd)
        resault=resault.read()
        if sucess!=None:
            resault=resault.strip()
            self.__check_device_not_connect()
            if sucess==resault:
                return True
            else:
                return False
        return False

    def __check_device_not_connect(self):
        '''
        检查设备是否连接
        :return:
        '''
        devices=ADB.getNowConnectDevice()
        if self._device_id not in devices:
            raise BaseException(adb.DEVICE_NOT_FOUND)

    @property
    def device_id(self):
        return self._device_id