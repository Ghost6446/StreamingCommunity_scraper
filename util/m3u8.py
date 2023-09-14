# 4.08.2023 -> 14.09.2023

# Import
import os, glob, time, tqdm, requests, shutil, ffmpeg
from functools import partial
from multiprocessing.dummy import Pool

# [ util ]
def delete_file(path):
    if os.path.exists(path):
        os.remove(path)

def save_in_part(folder_ts, merged_mp4):

    # Get list of ts file order
    os.chdir(folder_ts)
    ordered_ts_names = glob.glob("*.ts")

    open("concat.txt", "wb")
    open("part_list.txt", "wb")

    # Variable for download
    list_mp4_part = []
    part = 0
    start = 0
    end = 200

    # Create mp4 from start ts to end
    def save_part_ts(start, end, part):
        print("PROCESS PART => ", part, end = "\r")
        list_mp4_part.append(f"{part}.mp4")
        with open("concat.txt", "w") as f:
            for i in range(start, end):
                f.write(f"file {ordered_ts_names[i]} \n")
                
        ffmpeg.input("concat.txt", format='concat', safe=0).output(f"{part}.mp4", c='copy', loglevel="quiet").run()
        #subprocess.run(["ffmpeg", "-f", "concat", "-i", "concat.txt", "-codec", "copy", f"{part}.mp4"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        
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
    with open("part_list.txt", 'w') as f:
        for mp4_fname in list_mp4_part:
            f.write(f"file {mp4_fname}\n")
    ffmpeg.input("part_list.txt", format='concat', safe=0).output(merged_mp4, c='copy', loglevel="quiet").run()
    #subprocess.run(['ffmpeg', "-f", "concat", "-i", "part_list.txt", '-codec', 'copy', merged_mp4], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print("\r")

# [ func ]
def download_ts_file(ts_url: str, store_dir: str, headers):

    # Get ts name and folder
    ts_name = ts_url.split('/')[-1].split("?")[0]
    ts_dir = store_dir + "/" + ts_name

    # Check if exist
    if(not os.path.isfile(ts_dir)):

        # Download
        ts_res = requests.get(ts_url, headers=headers)

        if(ts_res.status_code == 200):
            with open(ts_dir, 'wb+') as f:
                f.write(ts_res.content)
        else:
            print(f"Failed to download streaming file: {ts_name}.") 

        time.sleep(0.5)

def download(m3u8_link, m3u8_content, m3u8_headers, merged_mp4):

    # Reading the m3u8 file
    m3u8_http_base = m3u8_link.rstrip(m3u8_link.split("/")[-1]) + ".ts"
    m3u8 = m3u8_content.split('\n')
    ts_url_list = []
    ts_names = []

    # Parsing the content in m3u8 with creation of url_list with url of ts file
    for i_str in range(len(m3u8)):
        line_str = m3u8[i_str]
        if line_str.startswith("#EXTINF"):
            ts_url = m3u8[i_str+1]
            ts_names.append(ts_url.split('/')[-1])
            if not ts_url.startswith("http"):
                ts_url = m3u8_http_base + ts_url
            ts_url_list.append(ts_url)


    #  Using multithreading to download all ts file
    os.makedirs("temp_ts", exist_ok=True)
    pool = Pool(20)
    gen = pool.imap(partial(download_ts_file, store_dir="temp_ts", headers=m3u8_headers), ts_url_list)
    for _ in tqdm.tqdm(gen, total=len(ts_url_list), desc="Download "):
        pass
    pool.close()
    pool.join()

    # Start to merge all *.ts files
    save_in_part("temp_ts", merged_mp4)
    os.chdir("..")

    # Clean temp file
    shutil.move("temp_ts\\"+merged_mp4 , ".")
    shutil.rmtree("temp_ts")
