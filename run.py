# 10.08.2023 -> 11.08.2023 -> 14.09.2023

# Class import
from util.Driver import Driver
from util.m3u8 import download

# Import
from bs4 import BeautifulSoup
from seleniumwire.utils import decode

# Class init
driver = Driver()
driver.create(headless=True)

# [ function ] main
def get_film(vid_id):

    url = "https://streamingcommunity.expert/watch/" + vid_id
    driver.get_page(url=url, sleep=3)

    m3u8_link = ""
    m3u8_data = ""
    m3u8_headers = ""
    is_m3u8_find = False

    for req in driver.driver.requests:
        if("?type=" in req.url):
            is_m3u8_find = True

            # Get response data
            m3u8_data = decode(req.response.body, req.response.headers.get('Content-Encoding', 'identity'))
            m3u8_data = BeautifulSoup(m3u8_data, "lxml").text

            # Add headers and url
            m3u8_headers = dict(req.headers)
            m3u8_link = req.url


    if(is_m3u8_find):
        download(m3u8_link, m3u8_data, m3u8_headers, merged_mp4=vid_id+".mp4")
    else:
        print("ERROR MISSIN KEY OR M3U8")

    driver.close()

get_film(input("INSERT KEY FILM => ").replace(" ", ""))

