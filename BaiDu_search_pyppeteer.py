import os
import random
import time
import asyncio
from urllib.parse import urlsplit
from pyppeteer import launch
BASE_DIR = os.path.dirname(__file__)

# 反爬JS
js1 = '''() =>{

           Object.defineProperties(navigator,{
             webdriver:{
               get: () => false
             }
           })
        }'''

js2 = '''() => {
        window.navigator.chrome = {
    runtime: {},
    // etc.
  };
    }'''

js3 = '''() =>{
Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en']
    });
        }'''

js4 = '''() =>{
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5,6],
  });
        }'''

js5 = '''() => {
        alert (
            window.navigator.webdriver
        )
    }'''

# 禁止获取图片 只打印了fetch和xhr类型response 的内容
async def intercept_request(req):
    """请求过滤"""
    if req.resourceType in ['image', 'media', 'eventsource', 'websocket']:
        await req.abort()
    else:
        await req.continue_()


async def intercept_response(res):
    resourceType = res.request.resourceType
    if resourceType in ['xhr', 'fetch']:
        resp = await res.text()
        url = res.url
        tokens = urlsplit(url)
        folder = BASE_DIR + '/' + 'data/' + tokens.netloc + tokens.path + "/"
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, str(int(time.time())) + '.json')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(resp)





async def main():


    browser = await launch({'headless': False,#'headless': False如果想要浏览器隐藏更改False为True
        'args': [
            '--disable-extensions',
            '--hide-scrollbars',
            '--disable-bundled-ppapi-flash',
            '--mute-audio',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            # '--no-sandbox', '--proxy-server=127.0.0.1:1080'  # 127.0.0.1:1080为代理ip和端口，这个根据自己的本地代理进行更改，如果是vps里或者全局模式可以删除掉'--proxy-server=127.0.0.1:1080'
        ],
        'dumpio': True, # 减少内存消耗
        # "slowMo": 25  # 让执行慢下来
    })


    page = await browser.newPage()
    # await page.setUserAgent(userAgent=random.choice(UA))  # 随机UA
    await page.setViewport({'width': 1200, 'height': 800})

    # 是否启用JS，enabled设为False，则无渲染效果
    await page.setJavaScriptEnabled(enabled=True)

    await page.evaluate(js1) # 执行反爬JS
    await page.evaluate(js2) # 执行反爬JS
    await page.evaluate(js3) # 执行反爬JS
    await page.evaluate(js4) # 执行反爬JS
    # await page.evaluate(js5) # 查看反爬JS执行结果

    await page.goto('https://www.baidu.com')

    # 监控网络请求，可以做过滤
    # page.on('request', intercept_request) # 设置请求处理函数
    # page.on('response', intercept_response) # 设置响应处理函数

    # frames 切换，[0]是主框
    # await page.setContent('<iframe></iframe>')
    # const iframe = await page.frames()[1]
    # const body = await iframe.$('body')


    # 在搜索框中输入python
    await page.type('input#kw.s_ipt', 'python')
    # 点击搜索按钮
    await page.click('input#su')
    # await page.mouse.click('input#su')  # 模拟真实点击
    # 第二种方法，在while循环里强行查询某元素进行等待

    while not await page.querySelector('.t'):
        pass
    # 这些等待方法都不好用
    # await page.waitForXPath('h3', timeout=300)
    # await page.waitForNavigation(waitUntil="networkidle0")
    # await page.waitForFunction('document.getElementByTag("h3")')
    # await page.waitForSelector('.t')
    # await page.waitFor('document.querySelector("#t")')
    # await page.waitForNavigation(waitUntil='networkidle0')
    # await page.waitForFunction('document.querySelector("").inner‌​Text.length == 7')

    title_elements = await page.xpath('//h3[contains(@class,"t")]/a')
    for item in title_elements:
        # 获取当前元素的文本
        title_str = await (await item.getProperty('textContent')).jsonValue()
        print(title_str)
    # 执行下拉到底
    await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
    # 强制等待5秒
    await asyncio.sleep(5)
    # 获取源代码
    html = await page.content()
    # 删除本地缓存数据
    await page.evaluate("window.localStorage.clear();")
    # 删除Cookies
    await page.deleteCookie()
    # 退出浏览器
    await browser.close()
asyncio.get_event_loop().run_until_complete(main())