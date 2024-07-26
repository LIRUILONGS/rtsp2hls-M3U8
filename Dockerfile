# 基础镜像
FROM continuumio/miniconda3

COPY . /
RUN pip install -r requirements.txt  -i  https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /

# 设置容器启动时的命令
#CMD ["python", "S3ClientServer.py"]
CMD ["uvicorn", "main:app", "--port", "30115" ,"--host" ,"0.0.0.0"]