# -*- coding:utf-8 -*-
'''
__author__: nmask by 2016.2
__Blog__: http://thief.one
'''
import socket
import urlparse
import sys
import wx
import xlrd
import threading
import time
from multiprocessing import Lock
import webbrowser
from wx.lib.embeddedimage import PyEmbeddedImage
from collections import *
reload(sys) 
sys.setdefaultencoding('utf-8') 

'''
这是TcpingScan V1.2版本！
此版本修改了页面布局，调整为了3个显示文本框！增加了nslookup动态解析功能，并显示有多个ip的网站
'''
class myapp(wx.App):
    def __init__(self,redirect):
        wx.App.__init__(self,redirect)
        pass
     
    def OnInit(self):
        frame = myframe(None,-1,'Tcping Scanner')
        frame.SetMaxSize((980,700))   #固定窗口大小
        frame.Show()
        self.SetTopWindow(frame)
        return True

class MyTextCtrl(wx.TextCtrl):                                            #定义TextCtrl类，构造鼠标单击url弹出浏览器事件。
    def __init__(self, parent, id=wx.ID_ANY, value=wx.EmptyString,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.TE_MULTILINE | wx.TE_AUTO_URL,
                 val=wx.DefaultValidator):
        wx.TextCtrl.__init__(self, parent, id, value, pos, size, style, val)
        self.BindEvents()

    def BindEvents(self):
        self.Bind(wx.EVT_TEXT_URL, self.OnTextURL)

    def OnTextURL(self, event):
        if event.MouseEvent.LeftUp():
            url = self.GetRange(event.GetURLStart(), event.GetURLEnd())
            webbrowser.open_new_tab(url)
        event.Skip()
     
class myframe(wx.Frame):
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,id,title=u'Tcping Scanner V1.2            Blog:   http://thief.one        那一年，风陵渡口......',size=(980,710))  
        self.dict_web={}
        list_time=['2','6','10','16','20','30','36','40','46','50','56','60']  ##间隔时间列表
        list_num=['1','2','3','4','5','6','7','8','9','10'] ##中断次数筛选
        self.biaozhi=1
        self.x=0
        self.y=0
        self.d=0
        self.dict_break={}
        self.dict_ip={}
        self.Bind(wx.EVT_CLOSE,self.exits)   #设定点击关闭事件函数

        panel=wx.Panel(self,-1)
        self.SetIcon(tzc.GetIcon())
        panel.Bind(wx.EVT_ERASE_BACKGROUND,self.OnEraseBack)         #给panel设置背景图片

        self.excel=wx.TextCtrl(panel,-1,pos=(30,20),size=(200,30))                      #excel文本框
        self.excel.SetValue('.\url.xls')

        ######第一行控件###############
        self.button_liulan= wx.Button(panel,-1,u'浏览',pos=(250,20),size=(50,30),style=0)       #浏览按钮
        self.button_jiance= wx.Button(panel,-1,u'检测',pos=(320,20),size=(50,30))  
        self.button_clear= wx.Button(panel,-1,u'清除',pos=(390,20),size=(50,30)) 

        self.time=wx.StaticText(panel,-1,u'运行间隔:',pos=(460,25),size=(60,20))  #静态文本
        self.choice=wx.Choice(panel,-1,pos=(530,25),size=(40,30),choices=list_time,validator=wx.DefaultValidator) #下拉列表框
        self.choice.SetStringSelection(s='30')   #设置下拉列表框默认值

        self.num=wx.StaticText(panel,-1,u'中断筛选:',pos=(580,25),size=(60,20))  #静态文本
        self.choice_num=wx.Choice(panel,-1,pos=(650,25),size=(40,30),choices=list_num,validator=wx.DefaultValidator) #下拉列表框
        self.choice_num.SetStringSelection(s='5') 

        self.dns=wx.StaticText(panel,-1,u'nslookup:',pos=(700,25),size=(60,20))  #静态文本
        self.choice_dns=wx.Choice(panel,-1,pos=(770,25),size=(40,30),choices=list_num,validator=wx.DefaultValidator) #下拉列表框
        self.choice_dns.SetStringSelection(s='5') 

        self.button_start= wx.Button(panel,-1,u'开始',pos=(840,10),size=(100,80)) 

        ######第二行控件#################################
        self.jiance_status=wx.StaticText(panel,-1,u'【*】开始运行程序前，请先检测EXCEL......',pos=(30,60),size=(250,20))  #静态文本
        self.yunxing_status=wx.StaticText(panel,-1,u'【*】运行状态:',pos=(30,100),size=(200,20))  
        ######第三行控件#################################
        self.que=wx.StaticText(panel,-1,u'筛选中断网站',pos=(30,130),size=(100,20))
        self.zho=wx.StaticText(panel,-1,u'出现中断网站',pos=(340,130),size=(100,20))
        self.al=wx.StaticText(panel,-1,u'所有监测网站',pos=(650,130),size=(100,20))
        #####第四行控件##################################
        self.queren=MyTextCtrl(panel,pos=(30,150),size=(300,420),style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_AUTO_URL|wx.TE_RICH2) #实例化MyTextCtrl类，确认中断网站
        self.zhongjian=MyTextCtrl(panel,pos=(340,150),size=(300,420),style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_AUTO_URL|wx.TE_RICH2) #中断一次就显示
        self.all=MyTextCtrl(panel,pos=(650,150),size=(300,420),style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_AUTO_URL|wx.TE_RICH2) #所有网站状态

        #####第五行控件##################################
        self.information=wx.StaticText(panel,-1,u'版本:   Tcping Scanner V1.2    \n2016年2月4日，界面改动较大，增加了动态nslookup！--nMask',pos=(30,590),size=(280,50))
        self.nslook=MyTextCtrl(panel,pos=(650,575),size=(300,90),style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_AUTO_URL|wx.TE_RICH2)
        ######设定字体大小以及颜色#######################
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)      #设置字体颜色大小
        self.all.SetFont(font)
        self.queren.SetFont(font)
        self.zhongjian.SetFont(font)
        self.jiance_status.SetForegroundColour('red')
        self.yunxing_status.SetForegroundColour('red')
        self.dns.SetBackgroundColour("white")
        self.num.SetBackgroundColour("white")
        self.que.SetBackgroundColour("white")
        self.zho.SetBackgroundColour("white")
        self.al.SetBackgroundColour("white")
        self.que.SetForegroundColour("blue")
        self.zho.SetForegroundColour("blue")
        self.al.SetForegroundColour("blue")
        self.jiance_status.SetBackgroundColour("white")
        self.yunxing_status.SetBackgroundColour("white")
        self.information.SetBackgroundColour("white")
        self.time.SetBackgroundColour("white")
        ######绑定事件函数###############################
        self.filedialog=wx.FileDialog(panel,message='选择字典文件',style=wx.OPEN) #弹出导入文件框
        self.button_liulan.Bind(wx.EVT_BUTTON,self.liulan)  #浏览按钮绑定事件
        self.button_jiance.Bind(wx.EVT_BUTTON,self.thread_jc)  #检测按钮绑定事件
        self.button_clear.Bind(wx.EVT_BUTTON,self.clear)  #清除按钮绑定事件
        self.button_start.Bind(wx.EVT_BUTTON,self.start)  #检测按钮绑定事件



    def exits(self,event):
        wx.Exit()

    def OnEraseBack(self,event):
        dc = event.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap("1.jpg")   #panel设置背景图片方法
        dc.DrawBitmap(bmp, 0, 0)

    def run(self,name,list_web,lock):
        try:
            ip=list_web[0]
            port=list_web[1]
            domain=list_web[2]
            timeout=3              #设置超时时间
            NORMAL=0               #0代表端口开放
            ERROR=1                #1代表端口关闭

            cs=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            cs.settimeout(timeout) 
            address=(str(ip),int(port))

            status = cs.connect_ex(address)
        
            if status != NORMAL:
                lock.acquire()
                content=u''+name+' http://'+str(domain)+':'+str(port)+' ('+ip+')'    #中断网站
                self.all.AppendText(content+'\n')
                if name in self.dict_break:
                    self.dict_break[name]+=1               #中断一次增加一
                else:
                    self.dict_break[name]=1                #第一次出现则设置为一
            else:
                if name in self.dict_break:
                    self.dict_break[name]-=1               #如果没有中断，则减一
                lock.acquire()
                content=u''+name+' http://'+str(domain)+':'+str(port)+' ('+ip+')'    #全部网站
                self.all.AppendText(content+'\n')
            lock.release()  

        except Exception ,e:  
            pass


    def liulan(self,event):
        self.jiance_status.SetLabel(u'【*】开始运行程序前，请先检测EXCEL......')
        if self.filedialog.ShowModal()==wx.ID_OK:
            self.path=self.filedialog.GetPath()
            self.excel.SetValue(self.path)

    def thread_jc(self,event):
        threads_jc=[]
        t=threading.Thread(target=self.jiance,args=())
        threads_jc.append(t)
        for i in threads_jc:
            i.start()

    def jiance(self):
        try:
            self.dict_web={}
            self.jiance_status.SetLabel(u'【*】正在检测.....')
            path=self.excel.GetValue()
            workbook=xlrd.open_workbook(path)
            worksheet1 = workbook.sheet_by_index(0)
            num_rows = worksheet1.nrows
            status=0
            error=[]
            for i in range(1,num_rows):
                list_web=[]
                name=worksheet1.cell_value(i,0)
                ip=worksheet1.cell_value(i,1)
                port=int(worksheet1.cell_value(i,2))
                domain=worksheet1.cell_value(i,3)

                # try:
                #     domain=urlparse.urlparse(url).netloc
                #     ip= socket.getaddrinfo(domain,'http')[0][4][0]          #获取网站ip地址
                #     lens=len(ip.strip().split('.'))
                # except Exception,e:
                #     list_web.append(ip)
                #     list_web.append(port)   
                #     list_web.append(domain)
                #     self.dict_web[name]=list_web

                list_web.append(ip)
                list_web.append(port)   
                list_web.append(domain)
                self.dict_web[name]=list_web

            if status==1:
                errors=[i+1 for i in error]
                self.jiance_status.SetLabel(u'【*】excel第'+str(errors)+u'行url填写有误，请修改后重新提交,或者多检测几次！')
            else:
                self.jiance_status.SetLabel(u'【*】导入excel成功！')
                return self.dict_web
        except:
            self.jiance_status.SetLabel(u'【*】导入excel有误！')


    def clear(self,event):
        self.biaozhi=1
        self.all.SetValue('')
        self.queren.SetValue('')
        self.zhongjian.SetValue('')
        self.dict_break={}
        self.y=0
        self.x=0
     
    def start(self,event):             #创建一个线程，防止程序崩溃

        if self.biaozhi==1:            #设置标识符，用来结束线程
            self.biaozhi=0
            self.button_start.SetLabel(u'暂停')
            self.jiance_status.SetLabel(u'【*】正在运行......')
        else:
            self.biaozhi=1
            self.button_start.SetLabel(u'开始')
            self.jiance_status.SetLabel(u'【*】暂停运行......')
        self.thread_start=[]
        for i in range(1):
            t=threading.Thread(target=self.threads,args=())
            self.thread_start.append(t)
        for i in self.thread_start:
            i.start()


    def nslookups(self):
        list1=self.dict_ip.items()             #动态nslookup解析
        ddict=defaultdict(list)
        for k,v in list1: 
            ddict[v].append(k) 
        list2=[(i,ddict[i]) for i in ddict if len(ddict[i])>1] 
        dict_ns=dict(list2)
        for i in dict_ns:
            content=''
            content=i+':'
            for j in dict_ns[i]:
                content=content+j+','
            self.nslook.AppendText(content)

    def threads(self):           #创建多个线程，用来执行主函数
        lock=Lock()
        times=int(self.choice.GetStringSelection())
        nums=int(self.choice_num.GetStringSelection())
        dnss=int(self.choice_dns.GetStringSelection())
        while True:
            if self.d<dnss:
                self.d+=1
            else:
                self.d=0
            if self.x>=20:
                self.dict_break={}          #20次一轮回，清空中断的网站信息。
                self.x=0
                self.all.SetValue('')
            if self.biaozhi==0:
                self.y+=1
                self.x+=1
                threads=[]
                self.all.SetValue('')
                for i in self.dict_web:
                    if self.d>dnss:
                        domain=self.dict_web[i][2]
                        self.ip=self.dict_web[i][0]=socket.getaddrinfo(domain,'http')[0][4][0]  #重新获取ip
                        self.dict_ip[self.ip]=domain
                    t=threading.Thread(target=self.run,args=(i,self.dict_web[i],lock))
                    threads.append(t)
                self.nslookups()
                for i in threads:
                    i.start()
                for i in threads:
                    i.join()

                self.yunxing_status.SetLabel(u'【*】运行状态:   正在进行第'+str(self.y)+u'轮检测，'+u' 网站数量：'+str(len(self.dict_web))+u'家！')

                self.queren.SetValue('')                #还原清空确认中断的网站内容
                self.zhongjian.SetValue('')
                

                f=open('log.txt','a')             #创建日志

                i='%Y-%m-%d %X'                   #获取当前时间
                t=time.strftime(i,time.localtime())

                for name in self.dict_break:            #将计算完的中断网站列表重新显示到文本框内
                    num=self.dict_break[name]
                    list_web=self.dict_web[name]
                    if num>0:                         #如果当前次数大于0，则显示。
                        ip=list_web[0]
                        port=list_web[1]
                        domain=list_web[2]
                        content=u'['+str(num)+']'+name+str(domain)+':'+str(port)+' ('+ip+')'    #中断网站
                        self.zhongjian.AppendText(content+'\n')
                        if num>=nums:
                            self.queren.AppendText(content+'\n')
                        f.write(str(content)+'    '+str(t)+'\n')
                f.close()
                time.sleep(times)            #设定时间间隔

            else:
                break


if __name__ == '__main__':
    tzc = PyEmbeddedImage(
    "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")
    mainapp = myapp(redirect = False)
    mainapp.MainLoop()




























