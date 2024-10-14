FROM pytorch/pytorch:2.2.2-cuda12.1-cudnn8-runtime

RUN sed -i 's/archive.ubuntu.com/repo.huaweicloud.com/g' /etc/apt/sources.list && \
    apt-get update && \
    pip config set global.index-url https://mirrors.huaweicloud.com/repository/pypi/simple && \
    pip config set global.trusted-host repo.huaweicloud.com && \
    pip config set global.timeout 120 && \
    pip install --upgrade pip

# ffmpeg for whisper
# wget to download model
# pkg-config/libmysqlclient-dev/build-essential for mysqlclient,
RUN apt-get install -y ffmpeg wget pkg-config libmysqlclient-dev build-essential

WORKDIR /app/srt
RUN mkdir "models" && \
    wget https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt -O models/small.pt

COPY requirements.txt /app/srt/requirements.txt
RUN pip install -r requirements.txt
# 使用原始源安装 mcelery, 镜像不够新
RUN pip install -i https://pypi.org/simple mcelery==0.1.0

COPY *.py /app/srt/

CMD celery -A srt_celery worker --loglevel=INFO -P solo -Q srt_infer -n srt_worker
