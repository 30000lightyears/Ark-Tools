import asyncio
import json

import aiofiles
import httpx
from ruamel.yaml import YAML

from config import DATAPATH, DOWNLOADPATH, ak_hot_update_list, ak_version_api
from util import get_data

yaml = YAML(pure=True)


def diff(old_set: list[dict[str, str]], new_set: list[dict[str, str]]):
    # check new
    set1 = [i["name"] for i in old_set]
    set2 = [i["name"] for i in new_set]
    check_new_set = [i for i in set2 if i not in set1]

    # check update
    set1 = [json.dumps(i) for i in old_set]
    set2 = [json.dumps(i) for i in new_set]
    check_update_set = [json.loads(i)["name"] for i in set2 if i not in set1]
    check_update_set = [i for i in check_update_set if i not in check_new_set]

    return {"new": check_new_set, "update": check_update_set}


async def download_ark_res(resVersion: str, res_type: str, resName: str, dl_path: str):
    res_url = f"https://ak.hycdn.cn/assetbundle/official/Android/assets/{resVersion}/{res_type.replace('/','_')}_{resName}.dat"

    out_path = DOWNLOADPATH / resVersion / dl_path

    out_path.mkdir(parents=True, exist_ok=True)

    out_file = out_path / f"{resName}.zip"
    if out_file.exists():
        print(f"{dl_path}/{resName}.zip 已存在")
        return

    resp = await get_data(res_url)
    if resp.status_code == 200:
        async with aiofiles.open(out_file, "wb") as wf:
            await wf.write(resp.content)
            print(f"{dl_path}/{resName}.zip 下载成功")
    else:
        print(f"下载{resName}时出错：", resp.status_code)
        print(res_url)


# 获取版本号


def get_local_res_version():
    with open(DATAPATH / "resVersion.yaml") as file:
        old_res_version = yaml.load(file)["currentVersion"]
    print(f"本地版本号{old_res_version}")
    return old_res_version


def get_res_version():
    print("获取最新版本信息...")
    res_version = httpx.get(ak_version_api["officialAndroid"]).json()["resVersion"]
    print(f"最新版本号：{res_version}")
    return res_version


old_res_version = get_local_res_version()
res_version = get_res_version()


def check_res_list():
    curr_ver_info = {}
    curr_ver_file = DATAPATH / "hot_update_list" / f"{res_version}.json"
    # 检查本地是否有缓存的版本文件列表
    if curr_ver_file.exists():
        with open(curr_ver_file) as file:
            curr_ver_info = json.load(file)
    else:
        print("下载版本文件列表...")
        # 获取文件列表
        curr_ver_info = httpx.get(ak_hot_update_list.format(res_version)).json()
        print("下载完成.")

        with open(curr_ver_file, "w") as file:
            json.dump(curr_ver_info, file)

    return curr_ver_info["abInfos"]


def parse_res_list(ab_infos: list, res_type_list):
    res_data = {}

    for item in ab_infos:
        name = item["name"]
        for path in res_type_list:
            if name.startswith(f"{path}/"):
                if not res_data.get(path):
                    res_data[path] = []
                res_data[path].append({"name": name, "hash": item["hash"]})
    return res_data


async def dl_excel():
    excel_res_list = [
        "character_table",
        "battle_equip_table",
        "uniequip_table",
        "gacha_table",
        "item_table",
        "activity_table",
    ]
    dl_list = []
    curr_res_list = check_res_list()
    for item in curr_res_list:
        name = item["name"]
        for n in excel_res_list:
            if name.startswith(f"gamedata/excel/{n}"):
                dl_list.append(
                    download_ark_res(
                        res_version, "gamedata/excel", name.split("/")[-1][:-3], "excel"
                    )
                )
    await asyncio.gather(*dl_list)


async def download_ark_anon(resVersion: str, resName: str):
    res_url = f"https://ak.hycdn.cn/assetbundle/official/Android/assets/{resVersion}/anon_{resName}.dat"

    out_path = DOWNLOADPATH / resVersion / "anon"
    out_path.mkdir(parents=True, exist_ok=True)
    out_file = out_path / f"{resName}.zip"
    if out_file.exists():
        print(f"anon/{resName}.zip 已存在")
        return

    resp = await get_data(res_url)
    if resp.status_code == 200:
        async with aiofiles.open(out_file, "wb") as wf:
            await wf.write(resp.content)
            print(f"anon/{resName}.zip 下载成功")
    else:
        print(f"下载{resName}时出错：", resp.status_code)
        print(res_url)


async def dl_anon():
    dl_list = []
    curr_res_list = check_res_list()
    for item in curr_res_list:
        name = item["name"]
        if name.startswith("anon"):

            dl_list.append(download_ark_anon(res_version,  name.split("/")[-1][:-4]))
    await asyncio.gather(*dl_list)


async def dl_res():
    if old_res_version == res_version:
        print("当前版本已是最新.")
        return

    old_res_ver_file = DATAPATH / "hot_update_list" / f"{old_res_version}.json"
    if not old_res_ver_file.exists():
        old_ver_info = httpx.get(ak_hot_update_list.format(old_res_version)).json()
        with open(old_res_ver_file, "w") as file:
            json.dump(old_ver_info, file)
    with open(old_res_ver_file) as file:
        old_ver_info = json.load(file)

    curr_res_list = check_res_list()
    old_res_list = old_ver_info["abInfos"]

    # 剧情背景和 CG, 干员立绘, 干员时装, 立绘差分, 活动 UI 资源
    res_type_list = [
        "avg/imgs",
        "avg/bg",
        "avg/items",
        "chararts",
        "skinpack",
        "avg/characters",
        # "ui/gacha",
        "ui/activity",
        "activity",
        # "gamedata/story"
    ]

    curr_res = parse_res_list(curr_res_list, res_type_list)
    old_res = parse_res_list(old_res_list, res_type_list)

    dl_list = []
    # 所有有修改的文件列表
    for res_type in res_type_list:
        diff_data = diff(old_res[res_type], curr_res[res_type])

        download_new_list = [i.split("/")[-1][:-3] for i in diff_data["new"]]
        download_update_list = [i.split("/")[-1][:-3] for i in diff_data["update"]]

        for resName in download_new_list:
            dl_list.append(
                download_ark_res(res_version, res_type, resName, "new/" + res_type)
            )

        for resName in download_update_list:
            dl_list.append(
                download_ark_res(res_version, res_type, resName, "update/" + res_type)
            )

    await asyncio.gather(*dl_list)
    with open(DATAPATH / "resVersion.yaml", "w") as file:
        yaml.dump({"currentVersion": res_version}, file)


asyncio.run(dl_res())
asyncio.run(dl_anon())
