# 10.08.2023 -> 11.08.2023

# Import
import os, re, glob, time, tqdm, shutil, requests, subprocess, sys
from functools import partial
from requests.models import Response
from multiprocessing.dummy import Pool

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)

class Video_Decoder(object):
    iv = ""
    uri = ""
    method = ""
    def __init__(self, x_key, uri):
        self.method = x_key["METHOD"] if "METHOD" in x_key.keys() else ""
        self.uri = uri
        self.iv = x_key["IV"].lstrip("0x") if "IV" in x_key.keys() else ""

    def decode_aes_128(self, video_fname: str):
        frame_name = video_fname.split("\\")[-1].split("-")[0] + ".ts"
        if(not os.path.isfile("ou_ts/"+frame_name)):
            subprocess.run(["openssl","aes-128-cbc","-d","-in", video_fname,"-out", "ou_ts/"+frame_name,"-nosalt","-iv", self.iv,"-K", self.uri ])

    def __call__(self, video_fname: str):
        if self.method == "AES-128":
            self.decode_aes_128(video_fname)
        else:
            pass

def decode_ext_x_key(key_str: str):
    key_str = key_str.replace('"', '').lstrip("#EXT-X-KEY:")
    v_list = re.findall(r"[^,=]+", key_str)
    key_map = {v_list[i]: v_list[i+1] for i in range(0, len(v_list), 2)}
    return key_map

def download_ts_file(ts_url: str, store_dir: str, c_headers: dict, attemp=3):
    ts_name = ts_url.split('/')[-1].split("?")[0]
    ts_dir = store_dir + "/" + ts_name
    if(not os.path.isfile(ts_dir)):
        for i in range(attemp):
            try:
                ts_res = requests.get(ts_url, headers=c_headers)
                if(ts_res.status_code != 200):
                    print("GET TS => ", ts_name, " STATUS => ", ts_res.status_code , "RETRY == ", i)
                if(ts_res.status_code == 200):
                    break
                if(ts_res.status_code == 472):
                    print("TOO MUCH REQ")
                    sys.exit(0)
            except Exception:
                pass
            time.sleep(0.5)

        if isinstance(ts_res, Response) and ts_res.status_code == 200:
            with open(ts_dir, 'wb+') as f:
                f.write(ts_res.content)
        else:
            print(f"Failed to download streaming file: {ts_name}.")

def save_in_part(merged_mp4):

    os.chdir("ou_ts")
    ordered_ts_names = glob.glob("*.ts")
    open("concat.txt", "wb")
    open("part_list.txt", "wb")
    list_mp4_part = []
    part = 0
    start = 0
    end = 200

    def save_part_ts(start, end, part):
        print("PROCESS PART => ", part, end = "\r")
        list_mp4_part.append(f"{part}.mp4")
        with open("concat.txt", "w") as f:
            for i in range(start, end):
                f.write(f"file {ordered_ts_names[i]} \n")
        subprocess.run(["ffmpeg", "-f", "concat", "-i", "concat.txt", "-codec", "copy", f"{part}.mp4"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        
    save_part_ts(start, end, part)
    for i in range(start, end):
        start+= 200
        end += 200
        part+=1
        if(end < len(ordered_ts_names)): save_part_ts(start, end, part)
        else:
            save_part_ts(start, len(ordered_ts_names), part)
            break

    with open("part_list.txt", 'w') as f:
        for mp4_fname in list_mp4_part:
            f.write(f"file {mp4_fname}\n")
    subprocess.run(['ffmpeg', "-f", "concat", "-i", "part_list.txt", '-codec', 'copy', merged_mp4], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("\r")

def download(m3u8_link, m3u8_content, m3u8_headers, decrypt_key, merged_mp4):
 
    m3u8_http_base = m3u8_link.rstrip(m3u8_link.split("/")[-1]) + ".ts"
    m3u8 = m3u8_content.split('\n')
    ts_url_list = []
    ts_names = []
    x_key_dict = dict()
    for i_str in range(len(m3u8)):
        line_str = m3u8[i_str]
        if line_str.startswith("#EXT-X-KEY:"):
            x_key_dict = decode_ext_x_key(line_str)
        elif line_str.startswith("#EXTINF"):
            ts_url = m3u8[i_str+1]
            ts_names.append(ts_url.split('/')[-1])
            if not ts_url.startswith("http"):
                ts_url = m3u8_http_base + ts_url
            ts_url_list.append(ts_url)

    video_decoder = Video_Decoder(x_key=x_key_dict, uri=decrypt_key)
    os.makedirs("temp_ts", exist_ok=True)
    os.makedirs("ou_ts", exist_ok=True)
    delete_file(".\\ou_ts\\concat.txt")
    delete_file(".\\ou_ts\\part_list.txt")
    pool = Pool(20)
    gen = pool.imap(partial(download_ts_file, store_dir="temp_ts", c_headers = m3u8_headers), ts_url_list)
    for _ in tqdm.tqdm(gen, total=len(ts_url_list), desc="Download "):
        pass
    pool.close()
    pool.join()
    for ts_fname in tqdm.tqdm(glob.glob("temp_ts\*.ts"), desc="Decoding "):
        video_decoder(ts_fname)
    save_in_part(merged_mp4)
    os.chdir("..")
    shutil.move("ou_ts\\"+merged_mp4 , ".")
    shutil.rmtree("ou_ts")
    shutil.rmtree("temp_ts")
