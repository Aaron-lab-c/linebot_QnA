# import 必要的函式庫
from typing import Any
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage , TextMessage
import requests, json

# Linebot的授權TOKEN
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

events=None


def get_answer(message_text):
 
    url = "https://linebotqa.azurewebsites.net/qnamaker/knowledgebases/71e582f9-dd8d-4d0b-be47-1147964d17e6/generateAnswer"

    # 發送request到QnAMaker Endpoint要答案
    response = requests.post(
                   url,
                   json.dumps({'question': message_text}),
                   headers={
                       'Content-Type': 'application/json',
                       'Authorization':'EndpointKey fadacb9d-f2ba-4cd5-a5a8-11377e1e9c8d'
                   }
               )
    
    data = response.json()

    try: 
        #我們使用免費service可能會超過限制（一秒可以發的request數）
        if "error" in data:
            return data["error"]["message"]
        #這裡我們預設取第一個答案
        answer = data['answers'][0]['answer']
        if("No good match found in KB."==answer):
            answer="我想不到該回答你什麼。"
        return answer

    except Exception:

        return "Error occurs when finding answer"


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            messages = (
                "Invalid signature. Please check your channel access token/channel secret."
            )
            logger.error(messages)
            return HttpResponseBadRequest(messages)
        return HttpResponse("OK")


@handler.add(event=MessageEvent, message=TextMessage)
def handl_message(event):
    answer = get_answer(event.message.text)
    outInfo = answer
    message = TextSendMessage(text=outInfo)
    line_bot_api.reply_message(
        event.reply_token,
        message)


