import json
import asyncio
from aiohttp import ClientSession, web
import config_secret

async def get_response(url, payload, headers):
    async with ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            original_response_text = await response.text(encoding=None)
            response_headers_multidict = response.headers
            original_response_headers = {}
            for i in response_headers_multidict:
                original_response_headers[i] = response_headers_multidict[i]
            # original_response_headers['Connection'] = 'close'

            # original_response_headers = {
            #     'abc':'wdwdw'
            # }
            # original_response_headers['abc'] = 'qqq'
    return original_response_text, original_response_headers

async def handle(request):
    #request url example: http://localhost:8080/?proxy_auth_key=qwerty&url=https://api.openai.com/v1/chat/completions

    # url = 'https://api.openai.com/v1/chat/completions'
    url = request.rel_url.query['url']
    provided_proxy_auth_key = request.rel_url.query['proxy_auth_key']
    if provided_proxy_auth_key != config_secret.PROXY_AUTH_KEY:
        return web.Response(status=403)

    http_method = request.method
    rel_url = request.rel_url
    headers = request.headers
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

    while True:
        await asyncio.sleep(3600)


if __name__ == '__main__':
    asyncio.run(main())