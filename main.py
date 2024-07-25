#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2024/07/24 17:20:21
@Author  :   Li Ruilong
@Version :   1.0
@Contact :   liruilonger@gmail.com
@Desc    :   python 取流转化
"""

# here put the import lib

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import signal
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Request, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ping3 import ping, verbose_ping

from datetime import datetime, timezone

from jinja2 import Environment, FileSystemLoader
import uvicorn

import re
import logging
import asyncio
import uuid
import subprocess
import sqlite3
import psutil
import yaml_util
import threading
import datetime
from fastapi.responses import HTMLResponse
# 创建 Jinja2 环境


env = Environment(loader=FileSystemLoader("templates"))


lock = threading.Lock()


# 创建一个处理程序，用于处理 DEBUG 级别的日志消息
debug_handler = logging.StreamHandler()
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))


config = yaml_util.get_yaml_config()

nginx = config["ngxin"]
fastapi = config["fastapi"]

app = FastAPI()


locad_id = nginx['nginx_ip']
locad_port = nginx['nginx_port']
locad_fix = nginx['nginx_fix']
nginx_path = nginx['nginx_path']
nginx_config_path  =  nginx['nginx_config_path']

port = fastapi['port']
hls_dir = fastapi['hls_dir']
ffmpeg_dir = fastapi['ffmpeg_dir']


# 最大取流时间
max_stream_threads = fastapi['max_stream_threads']
# 扫描时间
max_scan_time = fastapi['max_scan_time']


comm = fastapi['comm']

# 添加 CORS 中间件 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = AsyncIOScheduler()


@app.get("/")
async def get_index():

    return {"status": 200, "message": "Holler  Camera "}


@app.post("/sc_view/get_video_stream")
async def get_video_stream(
    ip: str = Query("192.168.2.25", description="IP地址"),  # 设置默认值为 1
    width: int = Query(320, description=" 流宽度"),  # 设置默认值为 10
    height: int = Query(170, description=" 流高度"),  # 设置默认值为 'name'
):
    """
    @Time    :   2024/07/23 11:04:31
    @Author  :   liruilonger@gmail.com
    @Version :   1.0
    @Desc    :    ffmag 解码推流
    """

    if width is None or ip is None or height is None:
        raise HTTPException(status_code=400, detail="参数不能为空")
    import time
    # 获取前端传递的参数
    uuid_v = str(uuid.uuid4())
    if validate_ip_address(ip) is False:
        return {"message": "no validate_ip_address", "code": 600}

    if ping_test(ip) is False:
        return {"message": "ping no pong", "code": 600}
    with lock:
        # 流是否在采集判断
        dictc = get_process_by_IP("ffmpeg.exe", ip)
        if len(dictc) != 0:
            return dictc[0]

        hls_dir = fastapi['hls_dir']
        ffmpeg_dir = fastapi["ffmpeg_dir"]
        print(vars())
        command = comm.format_map(vars())
        try:

            print(command.strip())
            process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(1)
            if process.pid:
                t_d = {
                    "pid": process.pid,
                    "v_url": f'http://{locad_id}:{locad_port}{locad_fix}{ip}-{uuid_v}.m3u8',
                    "ip": ip
                }

                print("摄像头数据更新完成...")
                time.sleep(3)
                pss = get_process_by_name("ffmpeg.exe", process.pid)
                print("创建的进程为:", pss)
                if len(pss) > 0:
                    return t_d
                else:
                    return {"status": 400, "message": "IP 取流失败!,请重新尝试"}
        except subprocess.CalledProcessError as e:
            return {"error": f"Error running ffmpeg: {e}"}


@app.post("/sc_view/stop_video_stream")
async def stop_video_stream(pid: int = Query(2000, description="进程ID")):
    """
    @Time    :   2024/07/24 14:10:43
    @Author  :   liruilonger@gmail.com
    @Version :   1.0
    @Desc    :   结束推流
    """

    if pid is None:
        raise HTTPException(status_code=400, detail="参数不能为空")

    pss = get_process_by_name("ffmpeg.exe", pid)
    print(pss)
    if len(pss) == 0:
        print("未获取到进程信息", pid)
        return {
            "status": 200,
            "message": "未获取到进程信息"
        }
    print("获取到进程信息：", pss)
    try:
        # 发送 SIGTERM 信号以关闭进程
        os.kill(int(pid), signal.SIGTERM)
        print(f"Process {pid} has been terminated.{str(pss)}")
        return {"status": 200, "message": "关闭成功!"}
    except OSError as e:
        # 调用 kill 命令杀掉
        pss[0].kill()
        print(f"Error terminating process {pid}: {e}")
        return {"status": 200, "message": "关闭成功!"}


@app.post("/sc_view/all_stop_video_stream")
async def all_stop_video_stream():
    """
    @Time    :   2024/07/24 14:10:43
    @Author  :   liruilonger@gmail.com
    @Version :   1.0
    @Desc    :   批量结束推流
    """
    pss = get_process_by_name("ffmpeg.exe")
    print(pss)
    if len(pss) == 0:
        return {
            "status": 200,
            "message": "转码全部结束"
        }
    print("获取到进程信息：", pss)
    process_list = []
    for p in pss:
        process_list.append({
            "pid": p.info['pid'],
            "name":  p.info['name'],
            "status": p.status(),
            "started": datetime.datetime.fromtimestamp(p.info['create_time']),
            "memory_info": str(p.memory_info().rss / (1024 * 1024)) + " MB",
            "cpu_percent": str(p.cpu_percent()) + " %",
            "cmdline": p.cmdline()
        })
        try:
            # 发送 SIGTERM 信号以关闭进程
            os.kill(int(p.info['pid']), signal.SIGTERM)
            print(f"Process {p.info['pid']} has been terminated.{str(pss)}")
        except OSError as e:
            # 调用 kill 命令杀掉
            pss[0].kill()
            print(f"Error terminating process {p.info['pid']}: {e}")
    return {"status": 200, "message": "关闭成功!", "close_list": process_list}


@app.post("/sc_view/get_video_stream_process_list")
async def get_video_stream_process_list():
    """
    @Time    :   2024/07/24 15:46:38
    @Author  :   liruilonger@gmail.com
    @Version :   1.0
    @Desc    :   返回当前在采集的流处理进程信息
    """

    pss = get_process_by_name("ffmpeg.exe")
    process_list = []
    for p in pss:
        ip_file = str(p.info['cmdline'][-1]).split("/")[-1]
        process_list.append({
            "pid": p.info['pid'],
            "name":  p.info['name'],
            "status": p.status(),
            "started": datetime.datetime.fromtimestamp(p.info['create_time']),
            "memory_info": str(p.memory_info().rss / (1024 * 1024)) + " MB",
            "cpu_percent": str(p.cpu_percent()) + " %",
            "cmdline": p.cmdline(),
            "v_url":  f'http://{locad_id}:{locad_port}{locad_fix}{ip_file}',
        })
    return {"message": "当前在采集的流信息", "process_list": process_list}


@app.post("/sc_view/get_video_stream_process_live")
async def get_video_stream_process_live(pid: int = Query(2000, description="进程ID")):
    """
    @Time    :   2024/07/24 15:46:38
    @Author  :   liruilonger@gmail.com
    @Version :   1.0
    @Desc    :   返回当前在采集的流处理进程是否存活
    """
    if pid is None:
        raise HTTPException(status_code=400, detail="参数不能为空")

    pss = get_process_by_name("ffmpeg.exe", pid)
    for p in pss:
        return {"is_running": p.is_running()}

    return {"is_running": False}

@app.get("/sc_view/get_video_player",response_class=HTMLResponse)
async def get_video_player(request: Request):
    """
    @Time    :   2024/07/24 15:46:38
    @Author  :   liruilonger@gmail.com
    @Version :   1.0
    @Desc    :   返回当前在采集的所有流处理页面
    """
    
    pss = get_process_by_IP("ffmpeg.exe")
    
    if len(pss) == 0:
        template = env.get_template("empty_page.html")
        return template.render()
    m3u8_urls =  [  p['v_url'] for p in pss]
    template = env.get_template("video_player.html")
    return template.render(m3u8_urls=m3u8_urls, request=request)


@scheduler.scheduled_job('interval', seconds=60*60)
async def scan_video_stream_list():
    """
    @Time    :   2024/07/24 16:29:49
    @Author  :   liruilonger@gmail.com
    @Version :   1.0
    @Desc    :   扫描取流列表，超过最大时间自动结束
    """
    pss = get_process_by_name("ffmpeg.exe")
    return pss


@app.on_event("startup")
async def startup_event():
    scheduler.start()
    # 重启 nginx
    restart_nginx()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()




# 启动 Nginx
def start_nginx():
    """
    @Time    :   2024/07/24 21:13:25
    @Author  :   liruilonger@gmail.com
    @Version :   1.0
    @Desc    :   启动 nginx
    """
    try:
        os.chdir(nginx_path)
        print("当前执行路径："+ str(nginx_path + "nginx.exe"))
        subprocess.Popen([nginx_path + "nginx.exe", "-c", nginx_config_path],stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
        print("===================  Nginx has been started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start Nginx: {e}")
    finally:
        os.chdir(os.path.dirname(__file__))  # 切换回用户主目录    

# 停止 Nginx
def stop_nginx():
    """
    @Time    :   2024/07/24 21:13:41
    @Author  :   liruilonger@gmail.com
    @Version :   1.0
    @Desc    :   关闭 nginx
    """
    try:
        os.chdir(nginx_path)
        print("当前执行路径："+ str(nginx_path + "nginx.exe"))
        subprocess.Popen([nginx_path+ "nginx.exe", "-s", "stop"], stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
        print("============  Nginx has been stopped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop Nginx: {e}")
    finally:
        os.chdir(os.path.dirname(__file__))  # 切换回用户主目录    

# 重启 Nginx
def restart_nginx():
    ns =  get_process_by_name("nginx.exe")
    if len(ns) > 0 :
        stop_nginx()
    start_nginx()

def get_process_by_name(process_name, pid=None):
    """
    @Time    :   2024/07/24 14:21:31
    @Author  :   liruilonger@gmail.com
    @Version :   1.1
    @Desc    :   获取指定进程名和进程 ID 的进程列表

    Args:
        process_name (str): 进程名称
        pid (int, optional): 进程 ID，默认为 None 表示不筛选 ID

    Returns:
        list: 包含指定进程名和进程 ID 的进程对象的列表
    """

    processes = []
    attrs = ['pid', 'memory_percent', 'name', 'cmdline', 'cpu_times',
             'create_time', 'memory_info', 'status', 'nice', 'username']
    for proc in psutil.process_iter(attrs):
        #print(proc.info['name'])
        try:
            if proc.info['name'] == process_name:
                if pid is None or proc.info['pid'] == pid:
                    processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    print("Process==================end")    
    return processes


def get_process_by_IP(process_name, ip=None):
    """
    @Time    :   2024/07/24 14:21:31
    @Author  :   liruilonger@gmail.com
    @Version :   1.1
    @Desc    :   获取指定进程名和 IP 的进程列表

    Args:
        process_name (str): 进程名称
        pid (int, optional): IP，默认为 None 表示不筛选 IP

    Returns:
        list: 包含指定进程名和进程 IP 的进程对象的列表
    """
    attrs = ['pid', 'memory_percent', 'name', 'cmdline', 'cpu_times',
             'create_time', 'memory_info', 'status', 'nice', 'username']
    press= []
    for proc in psutil.process_iter(attrs):
        try:
            if proc.info['name'] == process_name:

                if ip is None or any(ip in s for s in proc.info['cmdline']):
                    ip_file = str(proc.info['cmdline'][-1]).split("/")[-1]
                    press.append({
                        "pid": proc.info['pid'],
                        "v_url":  f'http://{locad_id}:{locad_port}{locad_fix}{ip_file}',
                        "ip": ip
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return press


def ping_test(ip_address, timeout=1, count=4):
    """
    @Time    :   2024/07/24 14:08:27
    @Author  :   liruilonger@gmail.com
    @Version :   1.0
    @Desc    :   Ping 测试
    """

    boo = []
    for i in range(count):
        delay = ping(ip_address, timeout)
        if delay is not None:
            print(f"{ip_address} 在 {delay:.2f} 毫秒内响应")
            boo.append(True)
        else:
            print(f"{ip_address} 无响应")
            boo.append(False)
    return all(boo)


def validate_ip_address(ip_address):
    """
    @Time    :   2024/07/24 09:49:51
    @Author  :   liruilonger@gmail.com
    @Version :   1.0
    @Desc    :   IP  地址校验
    """
    import re
    """
    验证 IP 地址的合法性
    """
    # 定义 IPv4 地址的正则表达式
    ipv4_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'

    # 检查 IP 地址是否匹配正则表达式
    match = re.match(ipv4_pattern, ip_address)
    if not match:
        return False

    # 验证每个字段是否在合法范围内
    for i in range(1, 5):
        if int(match.group(i)) < 0 or int(match.group(i)) > 255:
            return False

    return True


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=port)

#  uvicorn main:app --reload
