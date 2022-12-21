from transitions.extensions import GraphMachine
from utils import send_text_message, send_carousel_message, send_button_message, send_image_message
from bs4 import BeautifulSoup
import requests
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction

country=''
server=''
tag=0

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
        elif text=='eletrical outlets':
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
        send_text_message(event.reply_token,content)
        send_text_message(event.reply_token,"請輸入『back』回到開頭，即可重新選擇服務項目")
