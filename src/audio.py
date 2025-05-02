from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from moviepy import AudioFileClip, CompositeAudioClip, concatenate_audioclips, VideoClip
import librosa

from img_util import MiSansFont


def create_audio_visualizer(
    audio_paths, background_image_path, output_path, title: str
):
    terra = "泰拉旅社"
    fps = 60
    resolution = (1920, 1080)
    logo_size = 50

    bkg = Image.open(background_image_path).resize(resolution).convert("RGBA")

    logo = Image.open("resources/logo.jpeg").resize((logo_size, logo_size))
    logo_mask = Image.new("L", (logo_size, logo_size), color="black")
    logo_mask_draw = ImageDraw.Draw(logo_mask)
    logo_mask_draw.circle(
        ((logo_size // 2, logo_size // 2)), logo_size // 2, fill="white"
    )

    logo_font = MiSansFont.Semibold(36)
    title_font = MiSansFont.Bold(64)

    text_card = Image.new("L", resolution, color="black")
    text_card_draw = ImageDraw.Draw(text_card)
    text_card_draw.text((140, 80), terra, font=logo_font, anchor="la", fill="white")
    text_card_draw.text((1840, 1000), title, font=title_font, anchor="rd", fill="white")

    text_bkg = bkg.copy().filter(ImageFilter.GaussianBlur(20))
    text_bkg.alpha_composite(Image.new("RGBA", bkg.size, color="#ffffffee"))

    text_bkg_black = bkg.copy().filter(ImageFilter.GaussianBlur(20))
    text_bkg_black.alpha_composite(Image.new("RGBA", bkg.size, color="#00000055"))

    text_bkg_black_mask = Image.new("L", resolution, color="black")
    text_bkg_black_mask_draw = ImageDraw.Draw(text_bkg_black_mask)
    title_width = title_font.getlength(title)
    text_bkg_black_mask_draw.rectangle(
        (1840 - title_width - 10, 1000 - 80 - 8, 1840 + 10, 1000), fill="white"
    )
    text_bkg_black_mask_draw.rounded_rectangle(
        (80 - 5, 77 - 5, 80 + logo_size + 165 + 5, 77 + logo_size + 5),
        radius=25,
        fill="white",
    )

    bar_bkg = bkg.copy().filter(ImageFilter.GaussianBlur(5))
    bar_bkg.alpha_composite(Image.new("RGBA", bkg.size, color="#ffffff44"))

    num_bars = 192 + 102
    bar_offset_x = 0
    bar_offset_y = 1080
    bar_height = 350
    bar_width = 8
    bar_spacing = 2

    # 合并所有音频文件
    audio_clips = [AudioFileClip(audio_path) for audio_path in audio_paths]

    combined_audio = concatenate_audioclips(audio_clips)
    total_duration = combined_audio.duration
    # 预先加载音频数据用于可视化
    all_audio_data = []
    current_position = 0

    audio_list = [
        librosa.load(Path(audio_path), mono=True)[0] for audio_path in audio_paths
    ]
    
    audio_NDArray  = np.hstack(audio_list)
    
    sr_list = [
        librosa.load(Path(audio_path), mono=True)[1] for audio_path in audio_paths
    ]

    # for audio_path in audio_paths:
    #     p = Path(audio_path)
    #     y, sr = librosa.load(p, mono=True)
    #     duration = librosa.get_duration(y=y, sr=sr)
    #     all_audio_data.append((y, sr, current_position, current_position + duration))
    #     current_position += duration

    def make_frame(t):
        bkg_copy_card = Image.new("L", resolution, color="black")
        bkg_copy_draw = ImageDraw.Draw(bkg_copy_card)


        y, sr = audio_NDArray, sr_list[0]

        n_fft = 4096

        start_sample = int(t * sr)

        # 确保我们有足够的样本进行FFT
        if start_sample + n_fft < len(y):
            # 获取当前时间段的音频样本
            audio_segment = y[start_sample : start_sample + n_fft]

            # 计算频谱
            D = np.abs(librosa.stft(audio_segment, n_fft=n_fft))

            # 将频谱转换为分贝刻度
            D = librosa.amplitude_to_db(D)

            # 将频谱分成与柱子数量相同的段
            D_resized = []
            length = D.shape[0]

            # 生成对数间隔的分割点
            log_points = np.logspace(
                0, np.log10(length), num=num_bars + 1, endpoint=True
            )

            # 转换为整数索引并确保唯一性
            split_indices = np.unique(np.round(log_points).astype(int))
            split_indices = np.clip(split_indices, 0, length)

            while len(split_indices) < num_bars + 1:
                split_indices = np.sort(
                    np.concatenate([split_indices, [length // 2]])
                )

            for i in range(num_bars):
                start = split_indices[i]
                end = split_indices[i + 1]
                if start < end:
                    D_resized.append(np.mean(D[start:end]))

            # 确保有足够的数据
            # if len(D_resized) < num_bars:
            #     D_resized = D_resized + [D_resized[-1]] * (
            #         num_bars - len(D_resized)
            #     )

            # 归一化并缩放到可视化区域高度
            db_min, db_max = np.min(D_resized), np.max(D_resized)
            D_normalized = [
                (x - db_min) / (db_max - db_min + 0.000001) for x in D_resized
            ]

            # 绘制柱状图
            for i in range(len(D_resized)):
                height = max(3, int(D_normalized[i] * bar_height * 0.8))
                x_start = bar_offset_x + int(i * (bar_width + bar_spacing))

                bkg_copy_draw.rectangle(
                    (
                        x_start,
                        bar_offset_y - height,
                        x_start + bar_width,
                        bar_offset_y,
                    ),
                    fill="white",
                )
                # bkg_copy_draw.pieslice(
                #     (
                #         x_start,
                #         viz_bottom - height + 1 - bar_width / 2,
                #         x_start + bar_width,
                #         viz_bottom - height + 1 + bar_width / 2,
                #     ),
                #     -180,
                #     0,
                #     fill=bar_color,
                # )
        bkg_copy = bkg.copy()
        bkg_copy.paste(bar_bkg, mask=bkg_copy_card)
        bkg_copy.paste(text_bkg_black, mask=text_bkg_black_mask)
        bkg_copy.paste(text_bkg, mask=text_card)
        bkg_copy.paste(logo, (80, 77), logo_mask)
        return np.array(bkg_copy.convert("RGB"))

    video = VideoClip(make_frame, duration=total_duration)
    video = video.with_audio(combined_audio)

    video.write_videofile(output_path, fps=fps, codec="libx264", audio_codec="aac")

    print(f"视频已生成: {output_path}")


# 使用示例
if __name__ == "__main__":
    # 设置输入和输出路径
    audio_paths = ["out/m_bat_rglk4DLC2_intro.wav"]
    background_image_path = "data/img/bkg.png"
    output_path = "out/output_video.mp4"
    title = "主界面"

    # 创建音频可视化视频
    create_audio_visualizer(
        audio_paths=audio_paths,
        background_image_path=background_image_path,
        output_path=output_path,
        title=title,
    )
