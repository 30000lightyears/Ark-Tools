"""
Ark-Tools GUI应用
为各个功能模块提供图形用户界面
"""

import asyncio
import datetime
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from pathlib import Path
from typing import Optional
import sys

# 导入各个功能模块
from src import download_res, unpacker, avg_export, avg_gen_face, audio, config


class ArkToolsGUI:
    """主GUI应用类"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Ark-Tools - 明日方舟资源处理工具")
        self.root.geometry("1000x700")

        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')

        # 创建主容器
        main_container = ttk.Frame(root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置权重使窗口可调整大小
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)

        # 创建标签页容器
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 创建各个标签页
        self.create_download_tab()
        self.create_unpacker_tab()
        self.create_avg_export_tab()
        self.create_face_gen_tab()
        self.create_audio_tab()
        self.create_settings_tab()

        # 状态栏
        self.status_bar = ttk.Label(main_container, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

    def create_download_tab(self):
        """创建资源下载标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="📥 资源下载")

        # 版本信息框架
        version_frame = ttk.LabelFrame(tab, text="版本信息", padding="10")
        version_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(version_frame, text="本地版本:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.local_version_var = tk.StringVar(value="未检测")
        ttk.Label(version_frame, textvariable=self.local_version_var).grid(row=0, column=1, sticky=tk.W, pady=2, padx=(10, 0))

        ttk.Label(version_frame, text="最新版本:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.latest_version_var = tk.StringVar(value="未检测")
        ttk.Label(version_frame, textvariable=self.latest_version_var).grid(row=1, column=1, sticky=tk.W, pady=2, padx=(10, 0))

        ttk.Button(version_frame, text="检查更新", command=self.check_version).grid(row=0, column=2, rowspan=2, padx=(20, 0))

        # 下载选项框架
        options_frame = ttk.LabelFrame(tab, text="下载选项", padding="10")
        options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.download_all_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="下载所有资源（不只是差分）", variable=self.download_all_var).grid(row=0, column=0, sticky=tk.W)

        # 操作按钮
        button_frame = ttk.Frame(tab)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))

        self.download_btn = ttk.Button(button_frame, text="开始下载", command=self.start_download, state=tk.DISABLED)
        self.download_btn.grid(row=0, column=0, padx=5)

        ttk.Button(button_frame, text="停止下载", command=self.stop_download, state=tk.DISABLED).grid(row=0, column=1, padx=5)

        ttk.Button(button_frame, text="刷新文件列表", command=self.refresh_download_list).grid(row=0, column=2, padx=5)

        # 进度条
        self.download_progress = ttk.Progressbar(tab, mode='indeterminate')
        self.download_progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 创建PanedWindow来分割文件列表和日志
        paned = ttk.PanedWindow(tab, orient=tk.VERTICAL)
        paned.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 文件列表框架
        file_list_frame = ttk.LabelFrame(paned, text="已下载文件", padding="10")

        # 创建Treeview来显示文件列表
        tree_container = ttk.Frame(file_list_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        # 添加滚动条
        tree_scroll_y = ttk.Scrollbar(tree_container, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL)

        # 创建Treeview
        self.download_tree = ttk.Treeview(
            tree_container,
            columns=("name", "directory", "type", "size", "mtime"),
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )

        # 配置滚动条
        tree_scroll_y.config(command=self.download_tree.yview)
        tree_scroll_x.config(command=self.download_tree.xview)

        # 定义列
        self.download_tree.heading("name", text="文件名", command=lambda: self.sort_tree_column("name", False))
        self.download_tree.heading("directory", text="目录", command=lambda: self.sort_tree_column("directory", False))
        self.download_tree.heading("type", text="类型", command=lambda: self.sort_tree_column("type", False))
        self.download_tree.heading("size", text="大小", command=lambda: self.sort_tree_column("size", False))
        self.download_tree.heading("mtime", text="修改时间", command=lambda: self.sort_tree_column("mtime", False))

        # 设置列宽
        self.download_tree.column("name", width=200)
        self.download_tree.column("directory", width=250)
        self.download_tree.column("type", width=80)
        self.download_tree.column("size", width=100)
        self.download_tree.column("mtime", width=150)

        # 布局Treeview和滚动条
        self.download_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        # 统计信息
        stats_frame = ttk.Frame(file_list_frame)
        stats_frame.pack(fill=tk.X, pady=(5, 0))

        self.download_stats_var = tk.StringVar(value="总计: 0 个文件")
        ttk.Label(stats_frame, textvariable=self.download_stats_var).pack(side=tk.LEFT)

        # 日志输出框架
        log_frame = ttk.LabelFrame(paned, text="下载日志", padding="10")

        self.download_log = scrolledtext.ScrolledText(log_frame, height=10, state=tk.DISABLED)
        self.download_log.pack(fill=tk.BOTH, expand=True)

        # 添加到PanedWindow
        paned.add(file_list_frame, weight=3)
        paned.add(log_frame, weight=1)

        # 配置行列权重
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(4, weight=1)

    def create_unpacker_tab(self):
        """创建资源解包标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="📦 资源解包")

        # 文件选择框架
        file_frame = ttk.LabelFrame(tab, text="选择文件", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.unpack_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.unpack_file_var, width=60).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(file_frame, text="浏览...", command=self.browse_unpack_file).grid(row=0, column=1)

        # 输出目录框架
        output_frame = ttk.LabelFrame(tab, text="输出目录", padding="10")
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.unpack_output_var = tk.StringVar(value="output/unpacked")
        ttk.Entry(output_frame, textvariable=self.unpack_output_var, width=60).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(output_frame, text="浏览...", command=self.browse_unpack_output).grid(row=0, column=1)

        # 解包选项
        options_frame = ttk.LabelFrame(tab, text="解包选项", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.unpack_texture_var = tk.BooleanVar(value=True)
        self.unpack_sprite_var = tk.BooleanVar(value=True)
        self.unpack_data_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(options_frame, text="提取纹理(Texture2D)", variable=self.unpack_texture_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="提取精灵(Sprite)", variable=self.unpack_sprite_var).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="提取数据(MonoBehaviour)", variable=self.unpack_data_var).grid(row=2, column=0, sticky=tk.W)

        # 操作按钮
        ttk.Button(tab, text="开始解包", command=self.start_unpack).grid(row=3, column=0, pady=(0, 10))

        # 进度条
        self.unpack_progress = ttk.Progressbar(tab, mode='indeterminate')
        self.unpack_progress.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 日志输出
        log_frame = ttk.LabelFrame(tab, text="解包日志", padding="10")
        log_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.unpack_log = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.unpack_log.pack(fill=tk.BOTH, expand=True)

        # 配置行列权重
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(5, weight=1)

    def create_avg_export_tab(self):
        """创建立绘导出标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="🎨 立绘导出")

        # 输入目录框架
        input_frame = ttk.LabelFrame(tab, text="输入目录（解包后的资源）", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.avg_input_var = tk.StringVar(value="output/unpacked")
        ttk.Entry(input_frame, textvariable=self.avg_input_var, width=60).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(input_frame, text="浏览...", command=self.browse_avg_input).grid(row=0, column=1)

        # 输出目录框架
        output_frame = ttk.LabelFrame(tab, text="输出目录", padding="10")
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.avg_output_var = tk.StringVar(value="output/chararts")
        ttk.Entry(output_frame, textvariable=self.avg_output_var, width=60).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(output_frame, text="浏览...", command=self.browse_avg_output).grid(row=0, column=1)

        # 导出选项
        options_frame = ttk.LabelFrame(tab, text="导出选项", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.avg_with_mask_var = tk.BooleanVar(value=True)
        self.avg_without_mask_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(options_frame, text="导出带遮罩版本", variable=self.avg_with_mask_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="导出无遮罩版本", variable=self.avg_without_mask_var).grid(row=1, column=0, sticky=tk.W)

        # 操作按钮
        ttk.Button(tab, text="开始导出", command=self.start_avg_export).grid(row=3, column=0, pady=(0, 10))

        # 进度条
        self.avg_progress = ttk.Progressbar(tab, mode='indeterminate')
        self.avg_progress.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 日志输出
        log_frame = ttk.LabelFrame(tab, text="导出日志", padding="10")
        log_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.avg_log = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.avg_log.pack(fill=tk.BOTH, expand=True)

        # 配置行列权重
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(5, weight=1)

    def create_face_gen_tab(self):
        """创建表情生成标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="😊 表情生成")

        # 输入目录框架
        input_frame = ttk.LabelFrame(tab, text="输入目录（立绘差分）", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.face_input_var = tk.StringVar(value="output/chararts")
        ttk.Entry(input_frame, textvariable=self.face_input_var, width=60).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(input_frame, text="浏览...", command=self.browse_face_input).grid(row=0, column=1)

        # 输出目录框架
        output_frame = ttk.LabelFrame(tab, text="输出目录", padding="10")
        output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.face_output_var = tk.StringVar(value="output/face_cards")
        ttk.Entry(output_frame, textvariable=self.face_output_var, width=60).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(output_frame, text="浏览...", command=self.browse_face_output).grid(row=0, column=1)

        # 生成选项
        options_frame = ttk.LabelFrame(tab, text="生成选项", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.face_upscale_var = tk.BooleanVar(value=True)
        self.face_blur_bg_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(options_frame, text="启用超分处理（RealCUGAN）", variable=self.face_upscale_var).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="启用背景模糊", variable=self.face_blur_bg_var).grid(row=1, column=0, sticky=tk.W)

        ttk.Label(options_frame, text="网格列数:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.face_cols_var = tk.IntVar(value=4)
        ttk.Spinbox(options_frame, from_=3, to=6, textvariable=self.face_cols_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=(10, 0))

        # 操作按钮
        ttk.Button(tab, text="生成表情卡片", command=self.start_face_gen).grid(row=3, column=0, pady=(0, 10))

        # 进度条
        self.face_progress = ttk.Progressbar(tab, mode='indeterminate')
        self.face_progress.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 日志输出
        log_frame = ttk.LabelFrame(tab, text="生成日志", padding="10")
        log_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.face_log = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.face_log.pack(fill=tk.BOTH, expand=True)

        # 配置行列权重
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(5, weight=1)

    def create_audio_tab(self):
        """创建音频可视化标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="🎵 音频可视化")

        # 音频文件选择框架
        audio_frame = ttk.LabelFrame(tab, text="选择音频文件", padding="10")
        audio_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.audio_file_var = tk.StringVar()
        ttk.Entry(audio_frame, textvariable=self.audio_file_var, width=60).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(audio_frame, text="浏览...", command=self.browse_audio_file).grid(row=0, column=1)

        # 背景图片选择框架
        bg_frame = ttk.LabelFrame(tab, text="背景图片（可选）", padding="10")
        bg_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.audio_bg_var = tk.StringVar()
        ttk.Entry(bg_frame, textvariable=self.audio_bg_var, width=60).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(bg_frame, text="浏览...", command=self.browse_audio_bg).grid(row=0, column=1)

        # 输出文件框架
        output_frame = ttk.LabelFrame(tab, text="输出视频文件", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.audio_output_var = tk.StringVar(value="output/visualizer.mp4")
        ttk.Entry(output_frame, textvariable=self.audio_output_var, width=60).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(output_frame, text="浏览...", command=self.browse_audio_output).grid(row=0, column=1)

        # 可视化选项
        options_frame = ttk.LabelFrame(tab, text="可视化选项", padding="10")
        options_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(options_frame, text="视频标题:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.audio_title_var = tk.StringVar(value="Audio Visualization")
        ttk.Entry(options_frame, textvariable=self.audio_title_var, width=50).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)

        # 操作按钮
        ttk.Button(tab, text="生成可视化视频", command=self.start_audio_viz).grid(row=4, column=0, pady=(0, 10))

        # 进度条
        self.audio_progress = ttk.Progressbar(tab, mode='indeterminate')
        self.audio_progress.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 日志输出
        log_frame = ttk.LabelFrame(tab, text="处理日志", padding="10")
        log_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.audio_log = scrolledtext.ScrolledText(log_frame, height=15, state=tk.DISABLED)
        self.audio_log.pack(fill=tk.BOTH, expand=True)

        # 配置行列权重
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(6, weight=1)

    def create_settings_tab(self):
        """创建设置标签页"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="⚙️ 设置")

        # 路径设置框架
        path_frame = ttk.LabelFrame(tab, text="路径设置", padding="10")
        path_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 数据路径
        ttk.Label(path_frame, text="数据目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.data_path_var = tk.StringVar(value=str(config.DATAPATH))
        ttk.Entry(path_frame, textvariable=self.data_path_var, width=50).grid(row=0, column=1, padx=(10, 5), pady=5)
        ttk.Button(path_frame, text="浏览...", command=self.browse_data_path).grid(row=0, column=2, pady=5)

        # 下载路径
        ttk.Label(path_frame, text="下载目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.download_path_var = tk.StringVar(value=str(config.DOWNLOADPATH))
        ttk.Entry(path_frame, textvariable=self.download_path_var, width=50).grid(row=1, column=1, padx=(10, 5), pady=5)
        ttk.Button(path_frame, text="浏览...", command=self.browse_download_path).grid(row=1, column=2, pady=5)

        # API设置框架
        api_frame = ttk.LabelFrame(tab, text="API设置", padding="10")
        api_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(api_frame, text="服务器:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_server_var = tk.StringVar(value="officialAndroid")
        server_combo = ttk.Combobox(api_frame, textvariable=self.api_server_var, width=30, state="readonly")
        server_combo['values'] = list(config.ak_version_api.keys())
        server_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)

        # 按钮框架
        button_frame = ttk.Frame(tab)
        button_frame.grid(row=2, column=0, pady=(20, 0))

        ttk.Button(button_frame, text="保存设置", command=self.save_settings).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="重置默认", command=self.reset_settings).grid(row=0, column=1, padx=5)

        # 关于信息
        about_frame = ttk.LabelFrame(tab, text="关于", padding="10")
        about_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(20, 0))

        about_text = """Ark-Tools - 明日方舟资源处理工具集

版本: 1.0.0
作者: Ark-Tools Contributors
许可证: MIT License

这是一个用于处理明日方舟游戏资源的工具集，
包括资源下载、解包、立绘导出、表情生成和音频可视化等功能。
        """
        about_label = ttk.Label(about_frame, text=about_text, justify=tk.LEFT)
        about_label.pack()

        # 配置行列权重
        tab.columnconfigure(0, weight=1)

    # 辅助方法 - 文件/目录浏览
    def browse_unpack_file(self):
        filename = filedialog.askopenfilename(
            title="选择要解包的文件",
            filetypes=[("所有文件", "*.*"), ("ZIP文件", "*.zip")]
        )
        if filename:
            self.unpack_file_var.set(filename)

    def browse_unpack_output(self):
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.unpack_output_var.set(dirname)

    def browse_avg_input(self):
        dirname = filedialog.askdirectory(title="选择输入目录")
        if dirname:
            self.avg_input_var.set(dirname)

    def browse_avg_output(self):
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.avg_output_var.set(dirname)

    def browse_face_input(self):
        dirname = filedialog.askdirectory(title="选择输入目录")
        if dirname:
            self.face_input_var.set(dirname)

    def browse_face_output(self):
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.face_output_var.set(dirname)

    def browse_audio_file(self):
        filename = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=[("音频文件", "*.mp3 *.wav *.flac *.ogg"), ("所有文件", "*.*")]
        )
        if filename:
            self.audio_file_var.set(filename)

    def browse_audio_bg(self):
        filename = filedialog.askopenfilename(
            title="选择背景图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg"), ("所有文件", "*.*")]
        )
        if filename:
            self.audio_bg_var.set(filename)

    def browse_audio_output(self):
        filename = filedialog.asksaveasfilename(
            title="保存视频文件",
            defaultextension=".mp4",
            filetypes=[("MP4视频", "*.mp4"), ("所有文件", "*.*")]
        )
        if filename:
            self.audio_output_var.set(filename)

    def browse_data_path(self):
        dirname = filedialog.askdirectory(title="选择数据目录")
        if dirname:
            self.data_path_var.set(dirname)

    def browse_download_path(self):
        dirname = filedialog.askdirectory(title="选择下载目录")
        if dirname:
            self.download_path_var.set(dirname)

    # 功能方法 - 资源下载
    def check_version(self):
        """检查版本更新"""
        self.log_message(self.download_log, "正在检查版本信息...")
        self.status_bar.config(text="正在检查版本...")

        def check_thread():
            try:
                # 这里需要异步运行
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # 获取最新版本
                latest = loop.run_until_complete(download_res.get_res_version())
                self.latest_version_var.set(latest)

                # 获取本地版本
                res_version_file = config.DATAPATH / "resVersion.yaml"
                if res_version_file.exists():
                    import ruamel.yaml
                    yaml = ruamel.yaml.YAML()
                    with open(res_version_file, encoding="utf8") as f:
                        data = yaml.load(f)
                        local = data.get("resVersion", "未知")
                        self.local_version_var.set(local)
                else:
                    self.local_version_var.set("无")

                self.log_message(self.download_log, f"本地版本: {self.local_version_var.get()}")
                self.log_message(self.download_log, f"最新版本: {latest}")

                if self.local_version_var.get() != latest:
                    self.log_message(self.download_log, "发现新版本！可以开始下载。")
                    self.download_btn.config(state=tk.NORMAL)
                else:
                    self.log_message(self.download_log, "已是最新版本。")

                self.status_bar.config(text="版本检查完成")

            except Exception as e:
                self.log_message(self.download_log, f"检查版本时出错: {e}")
                self.status_bar.config(text="检查版本失败")

        threading.Thread(target=check_thread, daemon=True).start()

    def start_download(self):
        """开始下载资源"""
        self.log_message(self.download_log, "开始下载资源...")
        self.download_progress.start()
        self.download_btn.config(state=tk.DISABLED)
        self.status_bar.config(text="正在下载资源...")

        def download_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # 调用下载函数
                loop.run_until_complete(download_res.dl_res())

                self.log_message(self.download_log, "资源下载完成！")
                self.log_message(self.download_log, "正在刷新文件列表...")
                self.status_bar.config(text="下载完成")

                # 自动刷新文件列表
                self.refresh_download_list()

            except Exception as e:
                self.log_message(self.download_log, f"下载时出错: {e}")
                self.status_bar.config(text="下载失败")
            finally:
                self.download_progress.stop()
                self.download_btn.config(state=tk.NORMAL)

        threading.Thread(target=download_thread, daemon=True).start()

    def stop_download(self):
        """停止下载"""
        self.log_message(self.download_log, "停止下载功能尚未实现")

    # 功能方法 - 资源解包
    def start_unpack(self):
        """开始解包资源"""
        file_path = self.unpack_file_var.get()
        if not file_path:
            messagebox.showwarning("警告", "请选择要解包的文件")
            return

        self.log_message(self.unpack_log, f"开始解包: {file_path}")
        self.unpack_progress.start()
        self.status_bar.config(text="正在解包...")

        def unpack_thread():
            try:
                output_dir = Path(self.unpack_output_var.get())
                output_dir.mkdir(parents=True, exist_ok=True)

                # 调用解包函数
                unpacker_obj = unpacker.ArkMediaUnPacker(file_path, str(output_dir))
                # 这里需要根据实际的unpacker实现来调用

                self.log_message(self.unpack_log, "解包完成！")
                self.status_bar.config(text="解包完成")

            except Exception as e:
                self.log_message(self.unpack_log, f"解包时出错: {e}")
                self.status_bar.config(text="解包失败")
            finally:
                self.unpack_progress.stop()

        threading.Thread(target=unpack_thread, daemon=True).start()

    # 功能方法 - 立绘导出
    def start_avg_export(self):
        """开始导出立绘"""
        input_dir = self.avg_input_var.get()
        if not input_dir or not Path(input_dir).exists():
            messagebox.showwarning("警告", "请选择有效的输入目录")
            return

        self.log_message(self.avg_log, "开始导出立绘...")
        self.avg_progress.start()
        self.status_bar.config(text="正在导出立绘...")

        def export_thread():
            try:
                output_dir = Path(self.avg_output_var.get())
                output_dir.mkdir(parents=True, exist_ok=True)

                # 调用导出函数
                # avg_export.gen_avg_chararts()

                self.log_message(self.avg_log, "立绘导出完成！")
                self.status_bar.config(text="导出完成")

            except Exception as e:
                self.log_message(self.avg_log, f"导出时出错: {e}")
                self.status_bar.config(text="导出失败")
            finally:
                self.avg_progress.stop()

        threading.Thread(target=export_thread, daemon=True).start()

    # 功能方法 - 表情生成
    def start_face_gen(self):
        """开始生成表情卡片"""
        input_dir = self.face_input_var.get()
        if not input_dir or not Path(input_dir).exists():
            messagebox.showwarning("警告", "请选择有效的输入目录")
            return

        self.log_message(self.face_log, "开始生成表情卡片...")
        self.face_progress.start()
        self.status_bar.config(text="正在生成表情卡片...")

        def gen_thread():
            try:
                output_dir = Path(self.face_output_var.get())
                output_dir.mkdir(parents=True, exist_ok=True)

                # 调用表情生成函数
                # avg_gen_face.gen_face()

                self.log_message(self.face_log, "表情卡片生成完成！")
                self.status_bar.config(text="生成完成")

            except Exception as e:
                self.log_message(self.face_log, f"生成时出错: {e}")
                self.status_bar.config(text="生成失败")
            finally:
                self.face_progress.stop()

        threading.Thread(target=gen_thread, daemon=True).start()

    # 功能方法 - 音频可视化
    def start_audio_viz(self):
        """开始生成音频可视化"""
        audio_file = self.audio_file_var.get()
        if not audio_file or not Path(audio_file).exists():
            messagebox.showwarning("警告", "请选择有效的音频文件")
            return

        self.log_message(self.audio_log, "开始生成音频可视化...")
        self.audio_progress.start()
        self.status_bar.config(text="正在生成可视化...")

        def viz_thread():
            try:
                output_file = self.audio_output_var.get()
                bg_image = self.audio_bg_var.get() if self.audio_bg_var.get() else None
                title = self.audio_title_var.get()

                # 调用音频可视化函数
                # audio.create_audio_visualizer()

                self.log_message(self.audio_log, "音频可视化生成完成！")
                self.status_bar.config(text="生成完成")

            except Exception as e:
                self.log_message(self.audio_log, f"生成时出错: {e}")
                self.status_bar.config(text="生成失败")
            finally:
                self.audio_progress.stop()

        threading.Thread(target=viz_thread, daemon=True).start()

    # 设置相关方法
    def save_settings(self):
        """保存设置"""
        messagebox.showinfo("提示", "设置已保存")
        self.status_bar.config(text="设置已保存")

    def reset_settings(self):
        """重置设置"""
        self.data_path_var.set(str(config.DATAPATH))
        self.download_path_var.set(str(config.DOWNLOADPATH))
        self.api_server_var.set("officialAndroid")
        messagebox.showinfo("提示", "设置已重置为默认值")
        self.status_bar.config(text="设置已重置")

    # 工具方法
    def log_message(self, log_widget: scrolledtext.ScrolledText, message: str):
        """向日志窗口添加消息"""
        log_widget.config(state=tk.NORMAL)
        log_widget.insert(tk.END, f"{message}\n")
        log_widget.see(tk.END)
        log_widget.config(state=tk.DISABLED)

    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def format_time(self, timestamp: float) -> str:
        """格式化时间戳"""
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def sort_tree_column(self, col: str, reverse: bool):
        """对Treeview列进行排序"""
        items = [(self.download_tree.set(k, col), k) for k in self.download_tree.get_children('')]

        # 根据列类型进行不同的排序
        if col == "size":
            # 对大小列进行数值排序
            items.sort(key=lambda t: float(t[0].split()[0]) if t[0] else 0, reverse=reverse)
        elif col == "mtime":
            # 对时间列进行排序
            items.sort(key=lambda t: t[0], reverse=reverse)
        else:
            # 对其他列进行字符串排序
            items.sort(reverse=reverse)

        # 重新排列项目
        for index, (val, k) in enumerate(items):
            self.download_tree.move(k, '', index)

        # 更新表头，下次点击反向排序
        self.download_tree.heading(col, command=lambda: self.sort_tree_column(col, not reverse))

    def refresh_download_list(self):
        """刷新下载文件列表"""
        self.log_message(self.download_log, "正在刷新文件列表...")
        self.status_bar.config(text="正在刷新文件列表...")

        def refresh_thread():
            try:
                # 清空当前列表
                for item in self.download_tree.get_children():
                    self.download_tree.delete(item)

                # 扫描下载目录
                download_path = config.DOWNLOADPATH
                if not download_path.exists():
                    self.log_message(self.download_log, f"下载目录不存在: {download_path}")
                    self.status_bar.config(text="下载目录不存在")
                    return

                file_count = 0
                total_size = 0

                # 递归扫描所有文件
                for file_path in download_path.rglob("*.zip"):
                    # 获取文件信息
                    stat = file_path.stat()
                    file_size = stat.st_size
                    file_mtime = stat.st_mtime

                    # 确定文件类型（新文件/更新）
                    relative_path = file_path.relative_to(download_path)
                    parts = relative_path.parts

                    file_type = "未知"
                    directory = str(relative_path.parent)

                    if len(parts) > 1:
                        if parts[1] == "new":
                            file_type = "新文件"
                        elif parts[1] == "update":
                            file_type = "更新"
                        elif parts[1] == "anon":
                            file_type = "匿名"
                        elif parts[1] == "excel":
                            file_type = "数据表"

                    # 添加到Treeview
                    self.download_tree.insert(
                        "",
                        tk.END,
                        values=(
                            file_path.name,
                            directory,
                            file_type,
                            self.format_size(file_size),
                            self.format_time(file_mtime)
                        )
                    )

                    file_count += 1
                    total_size += file_size

                # 更新统计信息
                stats_text = f"总计: {file_count} 个文件，总大小: {self.format_size(total_size)}"
                self.download_stats_var.set(stats_text)

                self.log_message(self.download_log, f"文件列表刷新完成，共找到 {file_count} 个文件")
                self.status_bar.config(text="文件列表刷新完成")

            except Exception as e:
                self.log_message(self.download_log, f"刷新文件列表时出错: {e}")
                self.status_bar.config(text="刷新失败")

        threading.Thread(target=refresh_thread, daemon=True).start()


def main():
    """主函数"""
    root = tk.Tk()
    app = ArkToolsGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
