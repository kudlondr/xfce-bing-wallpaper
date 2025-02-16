# Xfce Bing-Wallpaper

Fork of original https://github.com/kazuki/xfce-bing-wallpaper.

Adds removal of old wallpapers and writes metadata (image title, copyright, ...) to downloaded image metadata.

## Usage

`python3 ./bing-wallpaper.py`

## Usage (systemd unit)

```
$ mkdir -p ~/.config/systemd/user
$ cp systemd/* ~/.config/systemd/user
$ vi ~/.config/systemd/user/bing-wallpaper.service  # edit script path
$ systemctl --user enable --now bing-wallpaper.timer
```

## Configuration (Environment Variable)

* `BING_WALLPAPER_PATH`: Bing wallpaper store directory (default: ~/.wallpapers)
* `BING_WALLPAPER_AGE`: Age of wallpaper images to delete in days (default: 7, < 0 to disable)
