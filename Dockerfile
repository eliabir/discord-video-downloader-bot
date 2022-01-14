FROM python:3

WORKDIR /usr/src/bot

COPY . .

RUN mkdir -p /usr/src/bot/videos

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "bot.py" ]
