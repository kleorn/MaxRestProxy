# Installation
cd /var/docker_volumes
git clone https://github.com/kleorn/MaxRestProxy
Скопировать по FTP файл config_secret.py
chmod -R 777 MaxRestProxy
cd MaxRestProxy
docker build . --tag max_rest_proxy
#replace MY_PORT to port number you want to listen
docker run -p MY_PORT:8080 -v /var/docker_volumes/MaxRestProxy:/var/MaxRestProxy --restart unless-stopped max_rest_proxy

# Run
docker start CONTAINER_NAME
e.g.
docker start strange_vaughan