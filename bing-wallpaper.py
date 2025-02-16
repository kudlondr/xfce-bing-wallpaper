##TODO add parameters loading from commandline
##TODO add output help

from datetime import date
import datetime
import pyexiv2
import json
import os
import subprocess
from urllib.request import urlopen, Request
import glob

FEED_URL = 'https://peapix.com/bing/feed?country='
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0',
}

# Load configuration from environment variable
COUNTRY = os.environ.get('BING_WALLPAPER_COUNTRY', '')
WALLPAPERS_DIR = os.environ.get('BING_WALLPAPER_PATH', os.path.expanduser('~/.wallpapers'))
DAYS_OLD_WALLPAPER = os.environ.get('BING_WALLPAPER_AGE', 7)
PRINT_DEBUG = os.environ.get('BING_WALLPAPER_DEBUG', True)

def debug_print(text) -> None:
    if PRINT_DEBUG:
        print(text)


def prepareWallpapersDir() -> None:
    # check store directory
    os.makedirs(WALLPAPERS_DIR, exist_ok=True)


def downloadNewWallpapers() -> None:
    # download feed json
    with urlopen(Request(f'{FEED_URL}{COUNTRY}', headers=DEFAULT_HEADERS)) as resp:
        feed = json.load(resp)
    # download new wallpapers
    for item in feed:
        imageUrlSplit = item['imageUrl'].split("/")
        path = os.path.join(WALLPAPERS_DIR, f'{item["date"]}' + "_" + imageUrlSplit[len(imageUrlSplit) -1])
        if os.path.exists(path):
            debug_print("skipping, image already downloaded: "+path)
            continue
        debug_print("downloading wallpaper: "+path)
        with urlopen(Request(item['imageUrl'], headers=DEFAULT_HEADERS)) as resp:
            data = resp.read()
        with open(path, 'wb') as f:
            f.write(data)
        writeMetadata(path, item)


def writeMetadata(imagePath, jsonData) -> None:
    debug_print("writing metadata to image "+imagePath)
    userdata={'title':jsonData['title'], 'copyright':jsonData['copyright'], 'date':jsonData['date'], 'pageUrl':jsonData['pageUrl'], 'imageUrl':jsonData['imageUrl']}
    metadata = pyexiv2.ImageMetadata(imagePath)
    metadata.read()
    metadata['Exif.Photo.UserComment']=json.dumps(userdata)
    metadata.write()
   

def removeOldWallpapers() -> None:
    if DAYS_OLD_WALLPAPER < 0:
        debug_print("removal of old wallpapers disabled")
        return
    allWalpapers = glob.glob(WALLPAPERS_DIR + "/*")
    for wallpaper in allWalpapers:
        wallpaperCreated = datetime.datetime.fromtimestamp(os.path.getmtime(wallpaper), datetime.UTC)
        now = datetime.datetime.now(wallpaperCreated.tzinfo)
        if wallpaperCreated + datetime.timedelta(days = DAYS_OLD_WALLPAPER + 1) < now:
            debug_print("removing wallpaper "+wallpaper)
            os.remove(wallpaper)


def updateWallpaper() -> None:
    today_wallpapers = glob.glob(os.path.join(WALLPAPERS_DIR, f'{datetime.date.today().isoformat()}' + "*"))
    if len(today_wallpapers) == 0:
        return
    today_wallpaper = today_wallpapers[0]
    if not os.path.exists(today_wallpaper):
        return
    proc = subprocess.run(['xrandr | grep " connected"'], capture_output=True, shell=True, text=True)
    monitors = [line.split()[0] for line in proc.stdout.split('\n') if line]
    for monitor in monitors:
        prop_name = f'/backdrop/screen0/monitor{monitor}/workspace0/last-image'
        subprocess.run(['xfconf-query', '-c', 'xfce4-desktop', '-p', prop_name, '-s', today_wallpaper])


def main() -> None:
    if not os.environ.get('DISPLAY', None):
        debug_print('$DISPLAY not set')
        return
    prepareWallpapersDir()
    downloadNewWallpapers()
    removeOldWallpapers()
    updateWallpaper()

if __name__ == '__main__':
    main()
