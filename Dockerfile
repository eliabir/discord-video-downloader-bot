FROM python:3.7-alpine

WORKDIR /usr/src/bot

COPY app/ .

RUN mkdir -p /usr/src/bot/videos && \
    pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "bot.py" ]
