import json
import asyncio
import os
import json
import logging
from logging.handlers import RotatingFileHandler  # просто import logging недостаточно!
from aiohttp import ClientSession, web
import config_secret

async def get_response(url, payload, headers):
    # Logger.debug('GET_RESPONSE_START', 'url: ' + url + ';' + 'payload: ' + json.dumps(payload) +';' + 'headers: ' + json.dumps(headers))
    async with ClientSession() as session:
        # async with session.post(url, json=payload, headers=headers) as response:
        async with session.post(url, json=payload, headers=headers) as response:
            original_response_text = await response.text(encoding=None)
            response_headers_multidict = response.headers
            original_response_headers = {}

            # original_response_headers = {
            #     'abc':'wdwdw'
            # }
            # original_response_headers['abc'] = 'qqq'
    return original_response_text, original_response_headers

def get_headers_dict(aiohttp_headers):
    headers = {}
    for i in aiohttp_headers:
        headers[i.lower()] = aiohttp_headers[i]
    headers.pop('content-length', '')
    headers.pop('host', '')
    # headers = {'Authorization': 'Bearer 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', 'Content-Type': 'text/plain',
    #  'User-Agent': 'PostmanRuntime/7.35.0', 'Accept': '*/*', 'Cache-Control': 'no-cache', 'Host': 'localhost:8080',
    #  'Content-Length': '197'}
    #
    # headers = {'Authorization': 'Bearer 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', 'Content-Type': 'text/plain',
    #  'User-Agent': 'PostmanRuntime/7.35.0', 'Accept': '*/*', 'Cache-Control': 'no-cache', 'Host': 'localhost:8080',
    #  'Content-Length': '197'}
    # original_response_headers['Connection'] = 'close'
    return headers


async def handle(request):
    #request url example: http://localhost:8080/?proxy_auth_key=qwerty&url=https://api.openai.com/v1/chat/completions

    # url = 'https://api.openai.com/v1/chat/completions'
    url = request.rel_url.query['url']
    provided_proxy_auth_key = request.rel_url.query['proxy_auth_key']
    if provided_proxy_auth_key != config_secret.PROXY_AUTH_KEY:
        return web.Response(status=403)

    http_method = request.method
    rel_url = request.rel_url
    headers = get_headers_dict(request.headers)
    if http_method in ('POST', 'PUT'):
        try:
            request_body = await request.json()
        except:
            request_body = None
    else:
        request_body = None

    original_response_text, original_response_headers = await get_response(url=url, payload=request_body, headers=headers)

    # HEADERS SENDING DOESN'T WORK (BROKES BODY) - NOT NEEDED ATM
    # return web.Response(text=original_response_text, headers=original_response_headers)

    return web.Response(text=original_response_text)


async def main():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    app.add_routes([web.post('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', config_secret.PROXY_PORT)
    await site.start()
    Logger.info('SITE_STARTED','Ok')

    while True:
        await asyncio.sleep(3600)


class Logger:
    LOG_FILENAME = 'MaxRestProxy.csv'
    if not os.path.exists('logs'):
        os.mkdir('logs')
    if not os.path.exists('logs/' + LOG_FILENAME):
        with open('logs/' + LOG_FILENAME, 'w', newline='', encoding='utf-8') as logfile:
            # conf_file.write(str(codecs.BOM_UTF8)) - не работает
            bom_utf8 = u'\ufeff'
            header = 'Timestamp;Level;Module;Line;Event;Data\n'
            logfile.write(bom_utf8 + header)  # начинаем файл с UTF-8 Byte Order Mask (BOM)

    file_handler = logging.handlers.RotatingFileHandler(filename='logs/' + LOG_FILENAME, encoding='utf-8', mode='a',
                                                        maxBytes=1000000, backupCount=1, delay=False)
    handlers_list = [file_handler]
    logging.basicConfig(handlers=handlers_list,
                        format='%(asctime)s;%(levelname)s;%(name)s;%(lineno)s;%(message)s',
                        level=config_secret.LOG_LEVEL,
                        datefmt='%d-%m-%Y %H:%M:%S')  # вызывать 1 раз

    @classmethod
    def info(cls, event, text):
        logging.info(event + ';' + text)

    @classmethod
    def debug(cls, event, text):
        logging.debug(event + ';' + text)


if __name__ == '__main__':
    asyncio.run(main())