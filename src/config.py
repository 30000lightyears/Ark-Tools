from pathlib import Path

DATAPATH = Path("data/game_data")
DOWNLOADPATH = Path("download")

ak_version_api = {
    "officialAndroid": "https://ak-conf.hypergryph.com/config/prod/official/Android/version",
    "officialIOS": "https://ak-conf.hypergryph.com/config/prod/official/IOS/version",
    "bilibili": "https://ak-conf.hypergryph.com/config/prod/b/Android/version",
}

ak_hot_update_api = {
    "officialAndroid": "https://ak.hycdn.cn/assetbundle/official/Android/assets/{}/hot_update_list.json",
    "officialIOS": "https://ak.hycdn.cn/assetbundle/official/IOS/assets/{}/hot_update_list.json",
}

ak_hot_update_list = (
    "https://ak.hycdn.cn/assetbundle/official/Android/assets/{}/hot_update_list.json"
)

github_raw_url = "https://raw.githubusercontent.com"

