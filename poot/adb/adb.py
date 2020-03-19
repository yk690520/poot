import os
import subprocess
import re,hashlib
from airtest.core.android.ime import YosemiteIme
from .. import tools
from io import StringIO
from airtest.core.android.adb import ADB as AirtestADB
from . import ADB_PATH,IME_PATH,DEVICE_NOT_FOUND,TEMP_UI_XML_SAVE_PATH,TEMP_XML
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
        self._cmd_prefix="%s -s %s " % (self._adb_path,device_id)
        self._airtestADB=AirtestADB(device_id)
        self._ime=YosemiteIme(self._airtestADB)
        self._ime.start()
        # self.__install_ime()
    def __install_ime(self):
        re = self.__make_shell_by_pope_return_re("ime list -a -s")
        if "com.android.adbkeyboard/.AdbIME" in re:
            return
        else:
            self.install_app(IME_PATH)

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
        return self.__make_cmd_by_pope_return_sucess("install -r %s",path,sucess="Success")


    def get_screen_size(self):
        '''
        获取屏幕分辨率，
        :return: （宽，高)
        '''
        width,hight=self.__make_shell_by_pope_return_re("wm size").split(":")[1].split("x")
        return int(width),int(hight)
    def tap_x_y(self,x,y,times=None):
        '''
        点击【x,y】对应的坐标点
        :param x:
        :param y:
        :return:
        '''
        if times!=None:
            self.__make_shell_by_pope("input swipe %s %s %s %s %s",x,y,x,y,times*1000)
        else:
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

    def tap_move_home(self):
        '''
        将输入光标移至最前面
        :return:
        '''
        self.__make_shell_by_pope('input keyevent 122')

    def tap_del(self,count=1):
        '''
        点击删除键
        :param count: 次数
        :return:
        '''
        cmd="input keyevent "
        for i in range(0,count):
            cmd+="112 "
        self.__make_shell_by_pope(cmd)

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
        self.rm_computer_file(TEMP_XML)
        self.pull_file_to_dsc("/mnt/sdcard/prefs.xml",TEMP_XML)
        self.rm_file("/mnt/sdcard/prefs.xml")
        with open(TEMP_XML) as file:
            strs=file.read()
        uid=(re.compile(r'_uin" value="([-]*[\d]+)"').findall(strs))[0]
        self.rm_computer_file(TEMP_XML)
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
        #结束pocoservice
        # self.__make_shell_by_pope('am force-stop com.netease.open.pocoservice')
        self.__make_cmd_by_pope('shell rm /mnt/sdcard/%s.xml', self._device_id)
        self.__make_shell_by_pope('uiautomator dump /mnt/sdcard/%s.xml', self._device_id)
        self.__make_shell_by_pope_onle_return_sucess('ls /mnt/sdcard/%s.xml',self._device_id,sucess='/mnt/sdcard/%s.xml' % self._device_id)
        if os.path.exists(TEMP_UI_XML_SAVE_PATH):
            if os.path.exists("%s/%s.xml" % (TEMP_UI_XML_SAVE_PATH,self._device_id)):
                os.remove("%s/%s.xml" % (TEMP_UI_XML_SAVE_PATH,self._device_id))
        else:
            os.mkdir(TEMP_UI_XML_SAVE_PATH)
        if self.__make_cmd_by_pope_return_sucess('pull /mnt/sdcard/%s.xml %s',self._device_id, TEMP_UI_XML_SAVE_PATH,sucess="pulled"):
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
        # tools.get_logger().info(cmd)
        resault=self.__execu_cmd(cmd)
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
        # tools.get_logger().info(cmd)
        resault=self.__execu_cmd(cmd).strip()
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
        # tools.get_logger().info(cmd)
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
        # tools.get_logger().info(cmd)
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
        # tools.get_logger().info(cmd)
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
        # tools.get_logger().info(cmd)
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
        # tools.get_logger().info(cmd)
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
        # tools.get_logger().info(cmd)
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
        # tools.get_logger().info(cmd)
        resault=self.__execu_cmd(cmd)
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
        # tools.get_logger().info(cmd)
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
        # tools.get_logger().info(cmd)
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
        # tools.get_logger().info(cmd)
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
        # tools.get_logger().info(cmd)
        resault=self.__execu_cmd(cmd).strip()
        if sucess!=None:
            resault=resault.strip()
            self.__check_device_not_connect()
            if sucess==resault:
                return True
            else:
                return False
        return False

    @staticmethod
    def __execu_cmd(cmd:str):
        '''
        执行cmd
        :return:
        '''
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   errors='ignore',
                                   encoding='gbk')
        process.wait()
        resault=process.stdout.read()
        process.stdout.close()
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