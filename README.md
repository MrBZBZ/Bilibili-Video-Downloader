# Bilibili-Video-Downloader
可以解析下载B站高清视频 
# 有什么功能？🤔
* 💪解析视频地址：输入BV号以后可下载任意清晰度视频到本地
* 💪Cookie登录：可以使用B站Cookie发送请求从而下载到高清视频
* 💪配置保存：可以保存Cookie，不用每次打开软件都输一遍
# 如何使用？🤔
* 下载release中的exe，启动
* 看到GUI正常出现即为成功启动程序
* ![GUI](GUI.jpg "GUI图片")
* 保存配置时会生成cookie_config.txt这个是您保存的Cookie文件，请妥善保管(注意：明文存储！)
# 什么是Cookie？我要怎么使用？🤔：
### Cookie是您登录B站后获得的身份令牌，在发送网络请求时携带Cookie可以证明您的身份(本软件不会非法利用您的任何Cookie)
# 如何获取我的B站Cookie🤔？：
### 打开您的浏览器，登录www.bilibili.com(一定要先处于已登录状态下)
### 按F12打开开发者工具，进行网络抓包，刷新网页  
![GUI](edge1.jpg "e")
![GUI](edge2.jpg "e")
### 随便找一个包含Cookie的请求，复制其中的Cookie，并将Cookie粘贴到软件中的Cookie输入框去(点击保存配置下一次就不用再抓包拿Cookie了)
![GUI](edge3.jpg "e")  
![GUI](edge4.jpg "e")
### 此时请保持你的B站的登录状态，因为Cookie是有时效期的，并且当你退出登录时，Cookie就会直接失效，这时只有重新登陆才能获取到新的Cookie
### 之后软件就可以使用你的Cookie向B站发送请求下载高清视频
# 特别注意：
* 充电视频以及大会员才能观看的视频都需要鉴权，所以请不要妄想使用此软件白嫖视频
