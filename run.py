# 10.08.23 -> 11.08.23 -> 14.09.23 -> 17.09.23 -> 10.10.23 -> 28.11.23

# Class import
from Stream.util.driver import Driver
from Stream.util.m3u8 import donwload_m3u8, parse_list_vvt_sub
from Stream.util.console import console, msg
from Stream.util.message import hello
from Stream.upload.update import main_update

# Import
from bs4 import BeautifulSoup
from seleniumwire.utils import decode
import sys, os, time

# Variable
DONWLOAD_VIDEO = True
DOWNLOAD_SUBTITLE = False

# [ function ] main
def get_film(vid_id):

    m3u8 = {
        "url": "", 
        "key": "",
        "request": {
            "data_response": "",
            "headers": "",
        }, 
        "subtitle": "",
        "main_sub": ""
    }

    # Get page of film id
    url = f"https://streamingcommunity.care/watch/{vid_id}"
    driver.get_page(url=url, sleep=3)
    page_title = driver.driver.title.split("-")[0].replace("\\", "").replace(",", "").strip()

    # If there is not title
    if len(page_title) != 0:
        console.log(f"[blue]Find title [white]=> [red]{page_title}")

    # Use video id 
    else:
        console.log(f"[red]Cant find video title")
        page_title = vid_id

    # --> Find info from all req
    console.log("[blue]Find all info ...")
    for req in driver.driver.requests:

        # Find ecrypt key
        if "enc.key" in req.url: 

            # Get response data
            response_body = decode(req.response.body, req.response.headers.get('Content-Encoding', 'identity'))
            m3u8['key'] = "".join(["{:02x}".format(c) for c in response_body])

        # Find video and main language
        if"type" in req.url:

            # Get response data
            m3u8_data = decode(req.response.body, req.response.headers.get('Content-Encoding', 'identity'))

            # Find video id and content
            if "?type=video" in req.url:
                m3u8['request']['data_response'] = BeautifulSoup(m3u8_data, "lxml").text
                m3u8['request']['headers'] = dict(req.headers)
                m3u8['url'] = req.url

             # Find main language subtitle url
            if "?type=subtitle" in req.url:
                m3u8['main_sub'] = req.url

        # Find all subtitle url
        if "?token=" in req.url and "playlist" in req.url:
            m3u8['subtitle'] = req.url

    # Print info main language of film
    try:
        params = dict(x.split('=') for x in m3u8['main_sub'].split('&'))
        console.log(f"[green]Film language [white]=> [red]{params['rendition']}")
    except:
        console.log("[red]Cant find main subtitle for this video")
    

    # --> Download video or subtitle
    if(m3u8['url'] != "" and DONWLOAD_VIDEO):

            console.log("[blue]Start download video ...")
            
            donwload_m3u8(
                url = m3u8['url'],
                content= m3u8['request']['data_response'],
                headers=m3u8['request']['headers'],
                decrypt_key=m3u8['key'],
                merged_mp4=page_title + ".mp4"
            )

    else:
        console.log("[red]Try reducing quality [SKIP]")

    if m3u8['subtitle'] != "" and DOWNLOAD_SUBTITLE:
            console.log("[blue]Start download subtitles ...")

            parse_list_vvt_sub(
                url=m3u8['subtitle'],
                headers=m3u8['request']['headers'],
                folder_id=page_title
            )

    else:
        console.log("[red]Cant find data of subtitle [SKIP]")

    # Close driver
    driver.close()

if __name__ == '__main__':

    # Hello
    os.system("CLS")
    hello()
    time.sleep(1)

    # Upload to latest version
    console.log(f"[blue]Find system [white]=> [red]{sys.platform}")
    #main_update()

    # Create driver
    driver = Driver()
    driver.create(True)

    # Get id of the film
    film_id = msg.ask("[cyan]Insert film key ").replace(" ", "")

    # Stall all request for download
    if film_id == "":
        console.log("[Red]Insert valid url not empty")
        sys.exit(0)
    else:
        get_film(vid_id=film_id)
