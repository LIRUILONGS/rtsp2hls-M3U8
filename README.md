# rtsp2hls2M3U8

摄像头 rtsp 实时流转 hls m3u8 格式 web 端播放


实现方案：

在服务器上安装并配置 `FFmpeg`,从 `RTSP` 摄像头获取实时视频流,并将其转码为 `HLS` 格式,生成 `m3u8` 播放列表和 `TS` 分段文件。
将生成的 `HLS` 文件托管到 `Nginx` 服务器的 `Web` 根目录下,并在 `Nginx` 配置文件中添加相应的配置,以正确处理 HLS 文件的 MIME 类型和跨域访问等。
在 Web 页面中使用 HTML5 的 <video> 标签或 HLS.js 库来播放 Nginx 托管的 HLS 视频流。

常见的两个转码方式：


rtsp 转 rtmp

`ffmpeg  rtsp 2 rtmp`

```bash
ffmpeg.exe -i rtsp://admin:hik12345@10.112.205.103:554/Streaming/Channels/101?transportmode=multicast -acodec aac -strict experimental -ar 44100 -ac 2 -b:a 96k -r 25 -b:v 500k   -c:v libx264 -c:a copy -f flv rtmp://127.0.0.1:1935/live/demo
```

`ffmpeg  rtsp 2 hls`

rtsp 转 hls

```bash
ffmpeg -f rtsp -rtsp_transport tcp -i rtsp://admin:hik12345@10.112.205.103:554/Streaming/Channels/101?transportmode=multicast -acodec aac -strict experimental -ar 44100 -ac 2 -b:a 96k -r 25 -b:v 500k -s 640*480  -c:v libx264 -c:a copy -cpu-used 0  -threads 1  -f hls -hls_time 2.0 -hls_list_size 3 -hls_wrap 50 X:\nginx-rtmp-win32-dev\nginx-rtmp-win32-dev\html\hls\test777.m3u8
```

### 名词解释:


`RTSP 协议`: RTSP (Real-Time Streaming Protocol) 是一种用于实时音视频流传输的网络协议,通常用于监控摄像头等设备的实时视频流传输。

`HLS 格式`: HLS (HTTP Live Streaming) 是苹果公司开发的自适应比特率流式传输协议,可以将视频流转码为 HTTP 可访问的 TS 分段文件和 m3u8 播放列表。HLS 具有良好的跨平台和兼容性。

`FFmpeg` : FFmpeg 是一个强大的多媒体框架,可以用于音视频的编码、解码、转码等操作。它可以将 RTSP 流转码为 HLS 格式。

`Nginx`: Nginx 是一款高性能的 Web 服务器,也可作为反向代理服务器使用。它可以`托管 HLS 格式的 m3u8 播放列表和 TS 分段文件`,为 `Web 端提供 HLS 流`的访问。

`HLS.js`: HLS.js 是一款 JavaScript 库,可以在不支持 HLS 原生播放的浏览器上实现 HLS 流的播放。


pyinstaller --add-data "config.yaml;."  --add-data "templates/*;templates"   main.py   


