import time
import zipfile
from pathlib import Path

import aiofiles
import httpx


async def get_data(url: str, use_proxy=False, params=None, headers=None, cookies=None):

    async with httpx.AsyncClient() as client:
        if headers:
            client.headers = headers
        else:
            client.headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.26"
            }
        resp = await client.get(
            url, params=params, cookies=cookies, timeout=60, follow_redirects=True
        )

    return resp


async def get_json(url: str, use_proxy, params=None, headers=None, cookies=None):
    return (await get_data(url, use_proxy, params=None, headers=None)).json()


async def download_file(
    url: str, use_proxy, name: str, path: str | Path, params=None, headers=None
):
    if isinstance(path, str):
        path = Path(path)

    path.mkdir(exist_ok=True)
    resp = await get_data(url, use_proxy, params, headers)
    async with aiofiles.open(path / name, "wb") as wf:
        await wf.write(resp.content)
        print(f"{name} 下载成功.")


# 与当前相差天数
def diff_days_timestamp(timestamp: int):
    now_time = int(time.time())
    return (timestamp - now_time) // 86400


def extract_package(file_path: Path) -> bytes:
    content = b""
    with zipfile.ZipFile(file_path) as f, f.open(f.infolist()[0].filename) as ab:
        content = ab.read()
    return content
