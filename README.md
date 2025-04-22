# Ark-tools

一些方便提取和处理《明日方舟》游戏资源的小工具

## 文件说明

- `download_res.py` 检查并自动下载更新的游戏资源
- `gen_avg.py` 解包剧情人物立绘差分资源

## 如何使用

1. 确保你的电脑安装有 Python@3.12 以及 [PDM](https://pdm-project.org/zh-cn/latest/)
2. clone 仓库到本地，执行 `pdm install` 安装依赖
3. 运行 `download_res.py` 下载近期更新的资源内容
4. 若目录 `download/<resVersion>/new/avg/characters` 中有新增的资源文件，运行 `gen_avg.py` 自动解析并导出立绘图片

## 感谢

- [UnityPy](https://github.com/K0lb3/UnityPy) 以及 MooncellWiki 对最新压缩格式提供的[解决方案](https://github.com/MooncellWiki/UnityPy/)
