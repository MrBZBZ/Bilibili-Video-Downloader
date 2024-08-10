import time
import wx
import requests as re
import json
import threading
from tkinter import messagebox
import http.cookiejar as cookielib
import qrcode as qr

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(450, 450))

        ways = ['360P 流畅', '480P 清晰','720P 高清','1080P 高清']
        self.panel = wx.Panel(self)
        self.bv_label = wx.StaticText(self.panel, label="请输入要下载的视频的BV号↓")
        self.bv_input = wx.TextCtrl(self.panel)
        self.cookie_label = wx.StaticText(self.panel, label="请输入你的B站Cookie，没有则默认为不登录↓")
        self.cookie_input = wx.TextCtrl(self.panel)
        self.choice_label = wx.StaticText(self.panel, label="选择下载视频的清晰度，不登录只能下载360P流畅↓")
        self.wayChoice = wx.Choice(self.panel, choices=ways)
        self.wayChoice.SetSelection(0)
        self.bv_query_button = wx.Button(self.panel, label="下载视频")
        self.login_button = wx.Button(self.panel, label="扫码登录获取Cookie")
        self.progress_lable = wx.StaticText(self.panel, label="下载进度↓")
        self.bv_result = wx.StaticText(self.panel, label="", style=wx.ALIGN_LEFT)
        self.save = wx.Button(self.panel, label="保存Cookie配置")
        self.progress = wx.Gauge(self.panel, range=100, pos=(20, 120), size=(350, 25))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.bv_label, 0, wx.ALL, 5)
        sizer.Add(self.bv_input, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.cookie_label, 0, wx.ALL, 5)
        sizer.Add(self.cookie_input, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.choice_label, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.wayChoice, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.bv_query_button, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(self.login_button, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(self.bv_result, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.progress_lable, 0,wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.progress, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.save, 0, wx.ALL | wx.CENTER, 5)

        self.panel.SetSizer(sizer)
        self.bv_query_button.Bind(wx.EVT_BUTTON, self.new_download)
        self.save.Bind(wx.EVT_BUTTON, self.new_save)
        self.login_button.Bind(wx.EVT_BUTTON, self.new_threading)
        self.last_size = None

        self.Center()
        try:
            # 尝试以读取模式打开文件
            with open("cookie_config.txt", "r") as file:
                # 读取文件内容
                content = file.read()
                self.cookie_input.SetValue(content)
        except FileNotFoundError:
            self.cookie_input.SetValue("")

    def extract_sessdata(self,content):
        sessdata_lines = [line for line in content.split('\n') if 'SESSDATA="' in line]

        if sessdata_lines:
            first_sessdata = sessdata_lines[0]
            start_index = first_sessdata.index('SESSDATA="') + len('SESSDATA="')
            end_index = first_sessdata.index('"', start_index)
            sessdata = first_sessdata[start_index:end_index]
            return sessdata
        else:
            return ""

    def get_headers(self):
        sessdata = ""

        if self.bv_input.GetValue() != "":
            content = self.cookie_input.GetValue()
            sessdata = self.extract_sessdata(content)
        else:
            try:
                with open("cookie_config.txt", "r") as file:
                    content = file.read()
                    sessdata = self.extract_sessdata(content)
            except FileNotFoundError:
                pass

        headers_and_cookie = {
            'referer': 'https://www.bilibili.com/',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        }

        if sessdata:
            headers_and_cookie["cookie"] = f"SESSDATA={sessdata}"
            return headers_and_cookie
        else:
            headers_and_cookie["cookie"] = "SESSDATA="
            return headers_and_cookie

    def get_cid(self, bv):
        headers_and_cookie = self.get_headers()
        cid = re.get("https://api.bilibili.com/x/player/pagelist?bvid=" + bv, headers=headers_and_cookie).text
        parsed_data = json.loads(cid)
        # 提取"cid"值
        cids = [item['cid'] for item in parsed_data['data']]
        return cids[0]

    def new_download(self, event):
        threading.Thread(target=self.download).start()
    def new_save(self,event):
        threading.Thread(target=self.save_me).start()

    def download(self):
        headers_and_cookie = self.get_headers()
        bv = self.bv_input.GetValue()
        if bv == "":
            self.bv_result.SetLabel("未检测到输入")
        else:
            self.bv_result.SetLabel("下载中，请等待")
            qn = self.wayChoice.GetString(self.wayChoice.GetSelection())
            if(qn == "360P 流畅"):
                qn = "16"
            elif(qn == "480P 清晰"):
                qn = "32"
            elif(qn == "720P 高清"):
                qn = "64"
            elif(qn == "1080P 高清"):
                qn = "128"
            cid = str(self.get_cid(bv))
            result = re.get(
                "https://api.bilibili.com/x/player/playurl?cid=" + cid + "&bvid=" + bv + "&platform=html5&high_quality=1&qn="+qn,headers=headers_and_cookie).text
            parsed_data = json.loads(result)
            # 提取"url"值
            url = parsed_data['data']['durl'][0]['url']
            response = re.get(url, headers=headers_and_cookie, stream=True)
            if response.status_code == 200:
                total_length = int(response.headers.get('content-length'))
                with open(bv + ".mp4", 'wb') as f:
                    dl = 0
                    for data in response.iter_content(chunk_size=1024):
                        dl += len(data)
                        f.write(data)
                        done = int(100 * dl / total_length)
                        wx.CallAfter(self.progress.SetValue, done)
                    wx.CallAfter(self.progress.SetValue, 0)
                self.bv_result.SetLabel("下载成功")
            else:
                self.bv_result.SetLabel("下载失败，网络好像开小差了")
    def new_login(self):
        headers = {
            'referer': 'https://www.bilibili.com/',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        }
        qrcode = re.get("https://passport.bilibili.com/x/passport-login/web/qrcode/generate?source=main-fe-header",headers=headers).json()
        img = qr.make(qrcode['data']['url'],version=None,box_size=5)
        img.save("qrcode.png")
        threading.Thread(target=self.login).start()
        threading.Thread(target=self.check_qrcode(qrcode,headers)).start()
    def new_threading(self,event):
        threading.Thread(target=self.new_login).start()

    def login(self):
        self.dialog = wx.Dialog(self, title="请使用手机扫描二维码登录",size=(350, 450))
        qrcode_label = wx.StaticText(self.dialog, label="请使用手机扫描二维码，成功后会有弹窗提示")
        qrcode_image = wx.StaticBitmap(self.dialog, bitmap=wx.Bitmap("qrcode.png"))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(qrcode_label, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(qrcode_image, 0, wx.ALL | wx.CENTER, 5)
        self.dialog.SetSizer(sizer)
        self.dialog.ShowModal()

    def check_qrcode(self,qrcode,headers):
        while True:
            qrcodedata = re.get("https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key=" + qrcode['data']['qrcode_key'] + "&source=main-fe-header",headers=headers).json()
            if(qrcodedata['data']['message'] == ""):
                session = re.session()
                session.cookies = cookielib.LWPCookieJar(filename='cookie_config.txt')
                session.get(qrcodedata['data']['url'],headers=headers)
                session.cookies.save()
                with open("cookie_config.txt", "r") as file:
                    # 读取文件内容
                    content = file.read()
                    self.cookie_input.SetValue(content)
                messagebox.showinfo("成功获取Cookie", "已自动覆写Cookie配置文件")
                self.close_dialog_from_thread()
                break
            elif(qrcodedata['data']['message'] == "二维码已失效"):
                messagebox.showinfo("该二维码已失效", "请重新获取二维码")
                self.close_dialog_from_thread()
                break
            elif(not self.dialog.IsShown()):
                messagebox.showinfo("获取Cookie失败", "未扫码，获取Cookie失败")
                break
            elif(qrcodedata['data']['message'] == "未扫码"):
                time.sleep(1)

    def close_dialog_from_thread(self):
        wx.CallAfter(self.dialog.Destroy)
        #关闭二维码显示窗口
    def save_me(self):
        result = messagebox.askyesno("你确定要保存cookie吗", "将会覆盖上一个保存的cookie")
        if result:
            file_name = "cookie_config.txt"
            with open(file_name, "w") as file:
                file.write(self.cookie_input.GetValue())
            messagebox.showinfo("保存配置","成功保存cookie到cookie_config.txt")
        else:
            messagebox.showwarning("保存配置", "已取消保存，保存cookie失败")
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame(None, "bilibili视频下载器V2.0 by Leaves_awa")
    frame.Show()
    app.MainLoop()