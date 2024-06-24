FROM python:3.10
WORKDIR /bot
COPY requirements.txt /bot/
RUN apt-get update && apt-get install -y vim
RUN pip install -r requirements.txt
COPY . /bot
CMD python src/bot.py
