FROM python:3.9

# 基础3.9

RUN gpg --keyserver keyserver.ubuntu.com --recv 467B942D3A79BD29
RUN gpg --export --armor 467B942D3A79BD29 | apt-key add -

WORKDIR /app
COPY . /app

RUN pip install -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 8898

CMD ["python", "app.py"]