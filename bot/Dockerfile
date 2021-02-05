FROM python:3
WORKDIR /bot
COPY bot/requirements.txt /bot
RUN pip install --no-cache-dir -r requirements.txt
COPY bot/. /bot
CMD ["python3", "main.py"]
