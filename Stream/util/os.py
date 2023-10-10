# 13.09.2023

# Import
import os, shutil

# [ func ]
def forceMergeFlatDir(srcDir, dstDir):
    if not os.path.exists(dstDir):
        os.makedirs(dstDir)
    for item in os.listdir(srcDir):
        srcFile = os.path.join(srcDir, item)
        dstFile = os.path.join(dstDir, item)
        forceCopyFile(srcFile, dstFile)

def forceCopyFile (sfile, dfile):
    if os.path.isfile(sfile) and ".git" not in sfile and "Run.py" in sfile:
        try:
            shutil.copyfile(sfile, dfile)
        except: 
            print(f"ERROR [{sfile} --> {dfile}]")

def isAFlatDir(sDir):
    for item in os.listdir(sDir):
        sItem = os.path.join(sDir, item)
        if os.path.isdir(sItem):
            return False
    return True

def copyTree(src, dst):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isfile(s):
            if not os.path.exists(dst):
                os.makedirs(dst)
            forceCopyFile(s,d)
        if os.path.isdir(s):
            isRecursive = not isAFlatDir(s)
            if isRecursive:
                copyTree(s, d)
            else:
                forceMergeFlatDir(s, d)


def rem_folder(dir_name):
    try:
        shutil.rmtree(dir_name)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))