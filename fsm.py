from transitions.extensions import GraphMachine
from utils import send_text_message, send_carousel_message, send_button_message, send_image_message
from bs4 import BeautifulSoup
import requests
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction
# import os
# os.environ["PATH"] += os.pathsep + "C:/Program Files/Graphviz/bin"

country=''
server=''
tag=0
sour=''
flavor=''

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
    def is_going_to_input_server(self,event):
        text=event.message.text
        if (text.lower()=='hello') or (text.lower()=='back'):
            return True
        return False
    def on_enter_input_server(self,event):
        title='請選擇服務項目'
        text='您想找附近咖啡廳還是想得到咖啡豆的相關資訊'
        btn=[
            MessageTemplateAction(
                label='find the cafe',
                text='find the cafe'
            ),
            MessageTemplateAction(
                label='choose coffee beans',
                text='choose coffee beans'
            ),
        ]
        url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png'
        send_button_message(event.reply_token,title,text,btn,url)
    
    def is_going_to_input_place(self,event):
        global server
        text=event.message.text
        if (text=='find the cafe'):
            server='find the cafe'
            return True
        return False
    
    def on_enter_input_place(self,event):
        send_text_message(event.reply_token,'請輸入想尋找的城市(英文)')
    
    def is_going_to_input_tag(self,event):
        global country
        text=event.message.text
        country=text.lower()
        return True
    def on_enter_input_tag(self,event):
        title='請選擇條件'
        text='請提供您的喜好~'
        btn=[
            MessageTemplateAction(
                label='free wifi',   #tag/87
                text='free wifi'
            ),
            MessageTemplateAction(
                label='electrical outlets',  #tag/88
                text='electrical outlets'
            ),
            MessageTemplateAction(
                label='no time limit',  #tag/89
                text='no time limit'
            ),
            MessageTemplateAction(
                label='environment', #tag/91
                text='environment'
            ),
        ]
        url='https://www.bakesmith.taipei/upload_file/Dachi/397/15864493973.jpg'
        send_button_message(event.reply_token,title,text,btn,url)

    def is_going_to_show_recommand(self,event):
        global tag
        text=event.message.text
        if text=='free wifi':
            tag=87
            return True
        elif text=='electrical outlets':
            tag=88
            return True
        elif text=='no time limit':
            tag=89
            return True
        elif text=='environment':
            tag=91
            return True
        return False

    def on_enter_show_recommand(self,event):
        global country,tag
        url='https://cafenomad.tw/'+country+'/tag/'+str(tag)
        response=requests.get(url)
        soup=BeautifulSoup(response.content,'html.parser')

        cards=soup.find_all('div',{'class':'box-view'},limit=5)
        content=""
        for card in cards:
            title=card.find('span').getText()
            address=card.find('div',{'class':'card one'}).getText().strip()
            content+=f"店名:{title} \n地址:{address} \n\n"
        content+="\n\n\n請輸入『back』回到開頭，即可重新選擇服務項目"
        send_text_message(event.reply_token,content)

    def is_going_to_input_sour(self,event):
        global server
        text=event.message.text
        if (text=='choose coffee beans'):
            server='choose coffee beans'
            return True
        return False
    
    def on_enter_input_sour(self,event):
        title='您喜歡的口感'
        text='咖啡豆的烘焙時間會影響咖啡的口感'
        btn=[
            MessageTemplateAction(
                label='sour',
                text='sour'
            ),
            MessageTemplateAction(
                label='bittersweet',
                text='bittersweet'
            ),
        ]
        url='https://img.ltn.com.tw/Upload/food/page/2018/06/28/180628-7760-0-jYh8n.jpg'
        send_button_message(event.reply_token,title,text,btn,url)

    def is_going_to_input_non_sour_flavor(self,event):
        global sour
        text=event.message.text
        if(text=='bittersweet'):
            sour='bittersweet'
            return True
        return False
    
    def on_enter_input_non_sour_flavor(self,event):
        # send_text_message(event.reply_token,"當咖啡豆的烘焙度較深，酸度會減輕，因此若您喜歡苦甜風味的咖啡可以選擇『中深焙』或『深焙』的烘焙度。")
        title='您喜歡的口味'
        text='中深焙和深焙的咖啡豆，主要有下列幾種口味'
        btn=[
            MessageTemplateAction(
                label='木質花茶香',
                text='木質花茶香'
            ),
            MessageTemplateAction(
                label='堅果巧克力',
                text='堅果巧克力'
            ),
        ]
        url='https://img.haohui2017.com/uploads/2019/09/20190910130210_77.jpg'
        send_button_message(event.reply_token,title,text,btn,url)
        
    def is_going_to_show_non_sour_rm(self,event):
        global flavor
        text=event.message.text
        flavor=text
        return True
    
    def on_enter_show_non_sour_rm(self,event):
        global flavor
        content=''
        if(flavor=='木質花茶香'):
            content="咖啡產地:瓜地馬拉\n焙度:中深焙\n適合搭配點心:馬卡龍"
        if(flavor=='堅果巧克力'):
            content="咖啡產地:巴西\n焙度:中深焙\n適合搭配點心:草莓蛋糕\n\n咖啡產地:哥倫比亞\n焙度:中深焙\n適合搭配點心:栗子蛋糕\n\n咖啡產地:曼特寧\n焙度:深焙\n適合搭配點心:牛肉起司堡"
        content+="\n\n\n請輸入『back』回到開頭，即可重新選擇服務項目"
        send_text_message(event.reply_token,content)
    
    def is_going_to_input_sour_flavor(self,event):
        global sour
        text=event.message.text
        if(text=='sour'):
            sour='sour'
            return True
        return False

    def on_enter_input_sour_flavor(self,event):
        title='您喜歡的口味'
        text='淺焙、淺中焙和中焙的咖啡豆，主要有下列幾種口味'
        btn=[
            MessageTemplateAction(
                label='木質花茶香',
                text='木質花茶香'
            ),
            MessageTemplateAction(
                label='果香',
                text='果香'
            ),
        ]
        url='https://img.haohui2017.com/uploads/2019/09/20190910130210_77.jpg'
        send_button_message(event.reply_token,title,text,btn,url)
    
    def is_going_to_show_sour_rm(self,event):
        global flavor
        text=event.message.text
        flavor=text
        return True
    
    def on_enter_show_sour_rm(self,event):
        global flavor
        content=''
        if(flavor=='木質花茶香'):
            content="咖啡產地:哥斯大黎加\n焙度:中焙\n適合搭配點心:鬆餅\n\n咖啡產地:宏都拉斯\n焙度:中焙\n適合搭配點心:布朗尼、巧克力"
        if(flavor=='果香'):
            content="咖啡產地:衣索比亞\n焙度:淺焙\n適合搭配點心:水果派\n\n咖啡產地:祕魯\n焙度:中淺焙\n適合搭配點心:奶油泡芙、酥餅\n\n咖啡產地:尼加拉瓜\n焙度:中焙\n適合搭配點心:起司蛋糕"
        content+="\n\n\n請輸入『back』回到開頭，即可重新選擇服務項目"
        send_text_message(event.reply_token,content)