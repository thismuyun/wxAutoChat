#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2018 Kingsoft.com, Inc. All Rights Reserved
#

"""
    auther: limuyun(limuyun@kingsoft.com)
    descrip:

"""

import argparse
import json
import random
from configparser import ConfigParser
import requests
import time
from wxpy import *

parser = argparse.ArgumentParser(description="this is wechat auto replies with AI ")
parser.add_argument('--mode', '-m', type=str, help='this is distinguish with user or group ',
                    choices=['friend', 'group'])
parser.add_argument('--username', '-u', type=str, help='type a user name who you want to talk to ')
parser.add_argument('--content', '-c', type=str, help='type a content which you want to say instead of hello ')
parser.add_argument('--auto', '-a', type=bool, help='if you want tag this program with [AI auto reply] please type <True> ',choices=[True, False])

args = parser.parse_args()

print(args)
if args.mode is None or args.username is None or args.content is None or args.auto is None:
    print("please type --help for help")
    sys.exit(1)

mode = args.mode
username = args.username
content = args.content
auto = args.auto

# linux执行登陆请调用下面的这句
bot = Bot(console_qr=2, cache_path="wxpy.pkl")

bot.friends().stats_text()


class AutoAI:

    def __init__(self):
        cp = ConfigParser()
        cp.read("conf/tuling.conf", encoding='UTF-8')
        sections = cp.sections()
        tuling = sections[0]
        self.url = cp.get(tuling, 'url')
        self.api_key = cp.get(tuling, 'api_key')
        self.userId = cp.get(tuling, 'userId')

    def auto_ai(self, text):
        payload = {
            "key": self.api_key,
            "reqType": 0,
            "perception": {
                "inputText": {
                    "text": text
                },
            },
            "userInfo": {
                "apiKey": self.api_key,
                "userId": self.userId
            }
        }

        r = requests.post(self.url, data=json.dumps(payload))
        result = json.loads(r.content)

        if auto:
            if 'url' in result["results"][0]["values"].keys():
                return u"[这是AI在回复] " + result["results"][1]["values"]["text"] + result["results"][0]["values"]["url"]
            else:
                return u"[这是AI在回复] " + result["results"][0]["values"]["text"]
        else:
            if 'url' in result["results"][0]["values"].keys():
                return result["results"][1]["values"]["text"] + result["results"][0]["values"]["url"]
            else:
                return result["results"][0]["values"]["text"]

    # content 为0 时候调用，随机生成一个打招呼语句
    def getHelloWord(self):
        hello_list = []
        hello_list.append(u"干哈呢呀？[奸笑]")
        hello_list.append(u"晚上去哪浪？")
        hello_list.append(u"忙么？[嘿哈]")
        hello_list.append(u"吃啥了？")
        hello_list.append(u"上班呢？")
        hello_list.append(u"嘚瑟啥呢？[皱眉]")
        hello_list.append(u"晚上啥安排？")
        hello_list.append(u"哼哼")
        hello_list.append(u"人呢？")
        hello_list.append(u"有人没？")
        hello_list.append(u"唠会啊？")

        return hello_list[random.randint(0, len(hello_list) - 1)]

    # 聊天遇到图片时调用， 随机生成一个返回
    def getEmo(self):
        emo_list = []
        emo_list.append(u"[奸笑][奸笑]")
        emo_list.append(u"[害羞]")
        emo_list.append(u"发的啥玩意")
        emo_list.append(u"[嘿哈]整的跟谁不会似的")
        emo_list.append(u"我跟你说，就你这样的表情，搁东北东容易挨揍~")
        emo_list.append(u"你咋这么欠呢")
        emo_list.append(u"你行不行")
        emo_list.append(u"臭不要脸的")
        emo_list.append(u"完犊子玩意")
        emo_list.append(u"有本事你再发一次[皱眉]")
        emo_list.append(u"跟谁俩呢")

        return emo_list[random.randint(0, len(emo_list) - 1)]

    # 如果对方回答下列语句，那么会返回 就问你崩溃不
    def return_bengkui(self, msg):
        hello_list = []
        hello_list.append(u"干啥")
        hello_list.append(u"啥事")
        hello_list.append(u"啥事儿")
        hello_list.append(u"？")
        hello_list.append(u"?")
        hello_list.append(u"嘎哈")
        hello_list.append(u"哈？")
        hello_list.append(u"哈?")
        hello_list.append(u"怎么啦")
        hello_list.append(u"肿么啦")
        hello_list.append(u"啊？")
        hello_list.append(u"啊?")
        if msg in hello_list:
            return u'没事发错了 就问你崩溃不 [奸笑]'

    # 对方发送语音时，随机生成一个返回
    def get_recording_back(self):
        record_list = []
        record_list.append(u"说的啥玩意，乱儿乱儿的，你再说一次~ [机智]")
        record_list.append(u"现在不方便语音")
        record_list.append(u"你再说一次，啥玩意")
        record_list.append(u"太吵了，听不清")
        record_list.append(u"听不清啊[炸弹]")
        return record_list[random.randint(0, len(record_list) - 1)]


ai = AutoAI()

print('AI已经启动')

if mode == "group":
    my_friend = bot.groups().search(username)[0]
elif mode == "friend":
    my_friend = bot.friends().search(username)[0]
else:
    # 默认启动
    my_friend = bot.groups().search(u'your default group which you want to talk to')[0]

if content == u'0':
    my_friend.send(ai.getHelloWord())
else:
    my_friend.send(content)


@bot.register(my_friend)
def group_message(msg):
    print('[接收]' + str(msg))

    if msg.type == u'Text':
        back = ai.return_bengkui(msg.text)
        if back is None:
            ret = ai.auto_ai(msg.text)
        else:
            ret = back

    elif msg.type == u'Picture':
        ret = ai.getEmo()
    elif msg.type == u'Recording':
        ret = ai.get_recording_back()
    else:
        ret = u"[奸笑]"
    time.sleep(3)
    print(ret)
    return ret


embed()
