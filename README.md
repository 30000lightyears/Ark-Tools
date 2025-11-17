# Ark-tools

一些方便提取和处理《明日方舟》游戏资源的小工具

## 功能特性

### 核心功能模块

1. **资源下载** (`download_res.py`) - 检查并自动下载更新的游戏资源
2. **资源解包** (`unpacker.py`) - 从Unity Asset Bundle中提取图片、音频等资源
3. **立绘导出** (`avg_export.py`) - 解包剧情人物立绘差分资源
4. **表情生成** (`avg_gen_face.py`) - 生成角色表情差分展示卡片
5. **音频可视化** (`audio.py`) - 创建音频频谱可视化视频
6. **图像处理** (`img_util.py`) - 图像超分辨率处理等工具

### 🎨 GUI界面

现在提供了图形用户界面，让您可以更方便地使用这些工具！

GUI支持以下功能标签页：
- 📥 **资源下载** - 检查版本更新、下载游戏资源
- 📦 **资源解包** - 解包Unity资源文件
- 🎨 **立绘导出** - 导出角色立绘和差分
- 😊 **表情生成** - 生成表情差分展示卡片
- 🎵 **音频可视化** - 创建音频频谱视频
- ⚙️ **设置** - 配置路径和参数

## 如何使用

### 安装依赖

1. 确保你的电脑安装有 Python@3.12 以及 [PDM](https://pdm-project.org/zh-cn/latest/)
2. clone 仓库到本地，执行 `pdm install` 安装依赖

### 使用GUI界面（推荐）

启动图形用户界面：

```bash
# 方法1: 直接运行启动脚本
python run_gui.py

# 方法2: 通过命令行工具（安装后）
pdm run ark-tools-gui
```

### 使用命令行

如果您更喜欢命令行方式：

1. 运行 `download_res.py` 下载近期更新的资源内容
2. 若目录 `download/<resVersion>/new/avg/characters` 中有新增的资源文件，运行 `avg_export.py` 自动解析并导出立绘图片

## 目录结构

```
Ark-Tools/
├── src/                          # 源代码目录
│   ├── gui.py                   # GUI主程序
│   ├── download_res.py          # 资源下载模块
│   ├── unpacker.py              # 资源解包模块
│   ├── avg_export.py            # 立绘导出模块
│   ├── avg_gen_face.py          # 表情生成模块
│   ├── audio.py                 # 音频可视化模块
│   ├── img_util.py              # 图像处理工具
│   ├── util.py                  # 通用工具函数
│   └── config.py                # 配置管理
├── data/                         # 数据目录
│   └── game_data/               # 游戏数据缓存
├── resources/                    # 资源文件
│   ├── fonts/                   # 字体文件
│   └── logo.jpeg                # Logo图片
├── output/                       # 输出目录（自动创建）
│   ├── unpacked/                # 解包后的资源
│   ├── chararts/                # 导出的立绘
│   └── face_cards/              # 表情卡片
├── run_gui.py                    # GUI启动脚本
├── pyproject.toml               # 项目配置
└── README.md                    # 说明文档
```

## 感谢

- [UnityPy](https://github.com/K0lb3/UnityPy) 以及 MooncellWiki 对最新压缩格式提供的[解决方案](https://github.com/MooncellWiki/UnityPy/)
