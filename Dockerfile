FROM python:3.11.3-bullseye
# ”казываем рабочую папку
WORKDIR /var/MaxRestProxy
EXPOSE 8080
RUN pip install aiohttp
CMD cd /var/MaxRestProxy && python3 main.py