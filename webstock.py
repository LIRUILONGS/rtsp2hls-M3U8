import asyncio
import websockets
import json
import time
from datetime import datetime


async def connect():
    uri = "ws://127.0.0.1:33686/"
    async with websockets.connect(uri) as websocket:
        # 连接成功
        print("WebSocket connection opened")

        
        # 发送消息
        await websocket.send( json.dumps({"sequence":"83ae4ae8-52b2-45de-a66e-54be262ef02c","cmd":"system.webconnect"}))
        print("Message sent to server")
        #await websocket.send( json.dumps({"cmd":"window.destroyWnd","sequence":"e4897d34-413a-40b4-b679-f7be95e87128","uuid":"{508f4f46-7932-4453-bce4-ebc6a6ae01ff}","timestamp":"1721996023024"})) 
        # 接收消息
        response = await websocket.recv()
        print(f"Message from server=============: {response}")
       
        time.sleep(1)
        # 发送消息
        await websocket.send( json.dumps({"sequence":"83ae4ae8-52b2-45de-a66e-54be262ef02c","cmd":"system.webconnect"}))
        print("Message sent to server")
        await websocket.send( json.dumps({"cmd":"window.destroyWnd","sequence":"e4897d34-413a-40b4-b679-f7be95e87128","uuid":"{508f4f46-7932-4453-bce4-ebc6a6ae01ff}","timestamp":"1721996023024"})) 
        # 接收消息
        response = await websocket.recv()
        print(f"Message from server=============: {response}")
        
        time.sleep(2)
        # 发送消息
        await websocket.send( json.dumps({"cmd":"window.createWnd","rect":{"left":16,"top":56,"width":1094,"height":680},"className":"Chrome","embed":True,"sequence":"bfdfdda7-7e87-441c-a754-2e18d4282d8c","uuid":"{508f4f46-7932-4453-bce4-ebc6a6ae01ff}","timestamp":"1721996023031"}))
        print("Message sent to server")
        exit()
        # 接收消息
        response = await websocket.recv()
        print(f"Message from server=============: {response}")

        time.sleep(1)
        # 发送消息
        await websocket.send( json.dumps({"cmd":"video.arrangeWindow","type":1,"custom":[],"sequence":"a8eaab74-de5b-41ab-adb4-2aa16916343c","uuid":"{508f4f46-7932-4453-bce4-ebc6a6ae01ff}","timestamp":"1721996023165"}))
        print("Message sent to server")
        #await websocket.send( json.dumps({"cmd":"window.destroyWnd","sequence":"e4897d34-413a-40b4-b679-f7be95e87128","uuid":"{508f4f46-7932-4453-bce4-ebc6a6ae01ff}","timestamp":"1721996023024"})) 
        # 接收消息
        response = await websocket.recv()
        print(f"Message from server=============: {response}")

        time.sleep(1)
        # 发送消息
        await websocket.send( json.dumps({"sequence":"83ae4ae8-52b2-45de-a66e-54be262ef02c","cmd":"system.webconnect"}))
        print("Message sent to server")
        #await websocket.send( json.dumps({"cmd":"window.destroyWnd","sequence":"e4897d34-413a-40b4-b679-f7be95e87128","uuid":"{508f4f46-7932-4453-bce4-ebc6a6ae01ff}","timestamp":"1721996023024"})) 
        # 接收消息
        response = await websocket.recv()
        print(f"Message from server=============: {response}")

        time.sleep(5)
        # 关闭连接
        await websocket.close()
        print("WebSocket connection closed")

# 运行事件循环
asyncio.get_event_loop().run_until_complete(connect())
