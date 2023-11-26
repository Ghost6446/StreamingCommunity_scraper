# 4.08.2023 -> 14.09.2023 -> 17.09.2023

# Import
import re, os, glob, time, requests, shutil, ffmpeg, subprocess
from functools import partial
from multiprocessing.dummy import Pool
from tqdm.rich import tqdm

# Class import
from Stream.util.util import console

# Disable warning
import warnings
from tqdm import TqdmExperimentalWarning
warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)

# [ decoder ]
class Video_Decoder(object):

    iv = ""
    uri = ""
    method = ""

    def __init__(self, x_key, uri):
        self.method = x_key["METHOD"] if "METHOD" in x_key.keys() else ""
        self.uri = uri
        self.iv = x_key["IV"].lstrip("0x") if "IV" in x_key.keys() else ""

    def decode_aes_128(self, video_fname: str):
        frame_name = video_fname.split(os.path.sep)[-1].split("-")[0] + ".ts"

        if(not os.path.isfile(os.path.join("ou_ts", frame_name))):
            subprocess.run(["openssl","aes-128-cbc","-d","-in", video_fname,"-out", os.path.join("ou_ts", frame_name),"-nosalt","-iv", self.iv,"-K", self.uri ])

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


# [ util ] 
def save_in_part(folder_ts, merged_mp4):

    # Get list of ts file in order
    os.chdir(folder_ts)

    try: ordered_ts_names = sorted(glob.glob("*.ts"), key=lambda x:float(re.findall("(\d+)", x.split("_")[1])[0]))
    except: 
        try: ordered_ts_names = sorted(glob.glob("*.ts"), key=lambda x:float(re.findall("(\d+)", x.split("-")[1])[0]))
        except: ordered_ts_names = sorted(glob.glob("*.ts"))

    open("concat.txt", "wb")
    open("part_list.txt", "wb")

    # Variable for download
    list_mp4_part = []
    part = 0
    start = 0
    end = 200

    # Create mp4 from start ts to end
    def save_part_ts(start, end, part):
        console.log(f"[blue]Process part [green][[red]{part}[green]]")
        list_mp4_part.append(f"{part}.mp4")

        with open(f"{part}_concat.txt", "w") as f:
            for i in range(start, end):
                f.write(f"file {ordered_ts_names[i]} \n")
                
        ffmpeg.input(f"{part}_concat.txt", format='concat', safe=0).output(f"{part}.mp4", c='copy', loglevel="quiet").run()
        
    # Save first part
    save_part_ts(start, end, part)

    # Save all other part
    for _ in range(start, end):

        # Increment progress ts file
        start+= 200
        end += 200
        part+=1

        # Check if end or not
        if(end < len(ordered_ts_names)): 
            save_part_ts(start, end, part)
        else:
            save_part_ts(start, len(ordered_ts_names), part)
            break

    # Merge all part
    console.log("[purple]Merge mp4")
    with open("part_list.txt", 'w') as f:
        for mp4_fname in list_mp4_part:
            f.write(f"file {mp4_fname}\n")
    ffmpeg.input("part_list.txt", format='concat', safe=0).output(merged_mp4, c='copy', loglevel="quiet").run()
    

# [ donwload ]
def download_ts_file(ts_url: str, store_dir: str, headers):
    # Get ts name and folder
    ts_name = ts_url.split('/')[-1].split("?")[0]
    ts_dir = os.path.join(store_dir, ts_name)

    # Check if exist
    if(not os.path.isfile(ts_dir)):
        retry = 1
        while retry <= 10:
            try:
                # Download
                ts_res = requests.get(ts_url, headers=headers)

                if(ts_res.status_code == 200):
                    with open(ts_dir, 'wb+') as f:
                        f.write(ts_res.content)
                        return
                else:
                    console.log(f"[red]Failed to download streaming file: {ts_name}.")

                time.sleep(0.5)

            except Exception as e:
                console.log(f'[yellow]Failed to download: {ts_name} - Retry: #{retry}')
                time.sleep(0.5*retry)

            retry+=1

        console.log(f"[red]Failed to download streaming file: {ts_name}.")


def download(m3u8_link, m3u8_content, m3u8_headers, decrypt_key, merged_mp4):

    # Reading the m3u8 file
    m3u8_http_base = m3u8_link.rstrip(m3u8_link.split("/")[-1]) + ".ts"
    m3u8 = m3u8_content.split('\n')
    ts_url_list = []
    ts_names = []
    x_key_dict = dict()

    # Parsing the content in m3u8 with creation of url_list with url of ts file
    for i_str in range(len(m3u8)):
        line_str = m3u8[i_str]

        if line_str.startswith("#EXT-X-KEY:"):
            x_key_dict = decode_ext_x_key(line_str)

        if line_str.startswith("#EXTINF"):
            ts_url = m3u8[i_str+1]
            ts_names.append(ts_url.split('/')[-1])

            if not ts_url.startswith("http"):
                ts_url = m3u8_http_base + ts_url

            ts_url_list.append(ts_url)
    console.log(f"[blue]Find [white]=> [red]{len(ts_url_list)}[blue] ts file to download")

    if decrypt_key != "":
        console.log(f"[blue]Use decrypting")

        video_decoder = Video_Decoder(x_key=x_key_dict, uri=decrypt_key)
        os.makedirs("ou_ts", exist_ok=True)

    #  Using multithreading to download all ts file
    os.makedirs("temp_ts", exist_ok=True)
    pool = Pool(15)
    gen = pool.imap(partial(download_ts_file, store_dir="temp_ts", headers=m3u8_headers), ts_url_list)
    for _ in tqdm(gen, total=len(ts_url_list), unit="bytes", unit_scale=True, unit_divisor=1024, desc="[yellow]Download"):
        pass
    pool.close()
    pool.join()

    console.log("[green]ALL PARTS DOWNLOADED")


    if decrypt_key != "":
        for ts_fname in tqdm(glob.glob(os.path.join(os.path.curdir, "temp_ts", "*.ts")), desc="[yellow]Decoding"):
            video_decoder(ts_fname)

        # Start to merge all *.ts files
        save_in_part("ou_ts", merged_mp4)
    else:
        save_in_part("temp_ts", merged_mp4)


    # Clean temp file
    os.chdir("..")
    console.log("[green]Clean")

    os.makedirs("videos", exist_ok=True)


    if decrypt_key != "": shutil.move(os.path.join(os.path.curdir, "ou_ts", merged_mp4) , "videos")
    else: shutil.move(os.path.join(os.path.curdir, "temp_ts", merged_mp4) , "videos")

    shutil.rmtree("ou_ts", ignore_errors=True)
    shutil.rmtree("temp_ts", ignore_errors=True)
