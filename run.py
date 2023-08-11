# 10.08.2023 -> 11.08.2023

# Class import
from util.Driver import Driver
from util.m3u8 import download

from bs4 import BeautifulSoup
from seleniumwire.utils import decode

driver = Driver()
driver.create(headless=True)

def get_film(vid_id):

    url = "https://streamingcommunity.bet/watch/" + vid_id
    driver.get_page(url=url, sleep=3)
    key_data = ""
    m3u8_link = ""
    m3u8_data = ""
    m3u8_headers = ""
    is_key_find = False
    is_m3u8_find = False

    for req in driver.driver.requests:
        if("enc.key" in req.url): 
            print("KEY FIND => ", req.url)
            is_key_find = True
            response_body = decode(req.response.body, req.response.headers.get('Content-Encoding', 'identity'))
            key_data = "".join(["{:02x}".format(c) for c in response_body])

        if("?type=" in req.url):
            is_m3u8_find = True
            m3u8_data = decode(req.response.body, req.response.headers.get('Content-Encoding', 'identity'))
            m3u8_data = BeautifulSoup(m3u8_data, "lxml").text
            m3u8_headers = dict(req.headers)
            m3u8_link = req.url

    if(is_key_find and is_m3u8_find): download(m3u8_link=m3u8_link, m3u8_content=m3u8_data, m3u8_headers=m3u8_headers, decrypt_key=key_data, merged_mp4=vid_id+".mp4")
    else: print("ERROR MISSIN KEY OR M3U8")
    driver.close()

get_film(input("INSERT KEY FILM => ").replace(" ", ""))