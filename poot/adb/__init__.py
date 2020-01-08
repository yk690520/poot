import os
import airtest.core.android.adb as airAdb
#异常
DEVICE_NOT_FOUND="设备已断开连接"
#其它配置
TEMP_UI_XML_SAVE_PATH="%s/uiTemp" % os.getcwd()#ui获取文件
TEMP_XML="%s/temp_xml.xml" % os.getcwd()#临时xml
IME_PATH="%s/core/adb/config/ime.apk" % os.getcwd()
ADB_PATH=airAdb.ADB.builtin_adb_path()

