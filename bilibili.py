import wx
import requests as re
import json
import threading
from tkinter import messagebox


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
        sizer.Add(self.bv_result, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.progress_lable, 0,wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.progress, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.save, 0, wx.ALL | wx.CENTER, 5)

        self.panel.SetSizer(sizer)
        self.bv_query_button.Bind(wx.EVT_BUTTON, self.new_download)
        self.save.Bind(wx.EVT_BUTTON, self.new_save)
        self.last_size = None

        try:
            # 尝试以读取模式打开文件
            with open("cookie_config.txt", "r") as file:
                # 读取文件内容
                content = file.read()
                self.cookie_input.SetValue(content)
        except FileNotFoundError:
            self.cookie_input.SetValue("")

    def get_cid(self, bv):
        headers = {
            'referer': 'https://www.bilibili.com/',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            "Cookie": self.cookie_input.GetValue()
        }
        cid = re.get("https://api.bilibili.com/x/player/pagelist?bvid=" + bv, headers=headers).text
        parsed_data = json.loads(cid)
        # 提取"cid"值
        cids = [item['cid'] for item in parsed_data['data']]
        return cids[0]

    def new_download(self, event):
        threading.Thread(target=self.download).start()
    def new_save(self,event):
        threading.Thread(target=self.save_me).start()

    def download(self):
        headers = {
            'referer': 'https://www.bilibili.com/',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            "Cookie": self.cookie_input.GetValue()
        }
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
                "https://api.bilibili.com/x/player/playurl?cid=" + cid + "&bvid=" + bv + "&platform=html5&high_quality=1&qn="+qn,headers=headers).text
            parsed_data = json.loads(result)
            # 提取"url"值
            url = parsed_data['data']['durl'][0]['url']
            response = re.get(url, headers=headers, stream=True)
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
    frame = MyFrame(None, "bilibili视频下载器 by Leaves_awa")
    frame.Show()
    app.MainLoop()
