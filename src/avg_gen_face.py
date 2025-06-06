import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from img_util import draw_card, get_center, get_mask, upscale


def gen_face(img_path: Path, crop_data: list[tuple[int, int, int]], bg_path: Path):
    face_block_width = 180
    gap_width = 8
    unit_width = face_block_width + gap_width
    full_ori_block_width = 1000 + gap_width * 4
    full_ori_block_height = 1000 + gap_width * 4
    file_groups = {}

    for file_path in img_path.glob("*.png"):
        file_name = file_path.name

        # 使用正则表达式提取分类数字
        match = re.search(r"\$(\d+)\.png", file_name)
        if match:
            cate = int(match.group(1))
            if cate not in file_groups:
                file_groups[cate] = []
            file_groups[cate].append(file_name)

    # 按分类处理差分
    for cate, files in file_groups.items():
        print(f"正在处理：{img_path.name}_{cate}.png")
        pic_cnt = len(files)

        # 部分动作差分的头部位置有偏移，这里传入一个列表进行单独处理
        if len(crop_data) == 1:
            crop_lb_x, crop_lb_y, crop_width = crop_data[0]
        else:
            crop_lb_x, crop_lb_y, crop_width = crop_data[cate - 1]

        # 根据数量判断三个一排还是四个一排
        if pic_cnt <= 15:
            g_x = 3
        elif pic_cnt <= 20:
            g_x = 4
        else:
            g_x = 5

        g_y = pic_cnt // g_x
        if pic_cnt % g_x != 0:
            g_y += 1

        # 主体人物
        full_ori = Image.open(img_path / f"1${cate}.png")

        # 需要绘制背景块的坐标列表（x1,y1,x2,y2）
        blur_list = []

        # 主体人物背景块的坐标
        blur_list.append((0, 0, full_ori_block_width, full_ori_block_height))

        # 表情差分处理
        # 裁切坐标（左上和右下）
        # 有的立绘的头顶紧贴着上边框，这里留出 20px 方便调整
        crop_box = (
            crop_lb_x,
            crop_lb_y + 20,
            crop_lb_x + crop_width,
            crop_lb_y + 20 + crop_width,
        )
        # 创建放置表情差分的透明底图
        face_img = Image.new("RGBA", size=(g_x * unit_width, g_y * unit_width))
        # 依次打开差分图片，粘贴到底图
        for i in range(pic_cnt):
            f = Image.new("RGBA", (full_ori.height, full_ori.height))
            f.paste(Image.open(img_path / f"{i+1}${cate}.png"), (0, 20))

            # )
            f = f.crop(crop_box).resize(
                (face_block_width, face_block_width), resample=Image.Resampling.LANCZOS
            )
            face_img.alpha_composite(
                f, (unit_width * (i % g_x), unit_width * (i // g_x))
            )

            # 表情差分背景块的坐标
            blur_list.append(
                (
                    full_ori_block_width + gap_width + unit_width * (i % g_x),
                    unit_width * (i // g_x),
                    full_ori_block_width
                    + gap_width
                    + unit_width * (i % g_x)
                    + face_block_width,
                    unit_width * (i // g_x) + face_block_width,
                )
            )

        # 最后一行空白处理
        space = pic_cnt % g_x
        if space != 0:
            space_width = (g_x - space) * face_block_width + (
                g_x - space - 1
            ) * gap_width
            blur_list.append(
                (
                    full_ori_block_width + gap_width + unit_width * space,
                    unit_width * (pic_cnt // g_x),
                    full_ori_block_width + gap_width + space_width + unit_width * space,
                    face_block_width + unit_width * (pic_cnt // g_x),
                )
            )

        full_ori = full_ori.resize((1000, 1000), resample=Image.Resampling.LANCZOS)

        full_pos = get_center(
            (full_ori_block_width, full_ori_block_height), full_ori.size
        )

        # 创建透明底的全图，下一步超分使用
        t_bg_width = full_ori_block_width + face_img.width
        t_bg_height = max(full_ori_block_height, face_img.height)

        t_bg = Image.new("RGBA", (t_bg_width, t_bg_height))
        t_bg.alpha_composite(full_ori, full_pos)
        t_bg.alpha_composite(face_img, (full_ori_block_width + gap_width, 0))

        save_path = img_path.parent / f"{img_path.name}_{cate}.png"
        t_bg.save(save_path)

        # 对拼好的透明底差分进行超分处理
        t = upscale(save_path)

        # TODO 处理方式改进
        bl = []
        for i in blur_list:
            bl.append((i[0] * 2, i[1] * 2, i[2] * 2, i[3] * 2))
        bg = Image.open(bg_path).resize((1024, 574)).filter(ImageFilter.GaussianBlur(5))
        bg = bg.resize((bg.width * 4, bg.height * 4))
        tt = Image.new("RGBA", t.size)
        tt.paste(t, mask=get_mask(t.size, bl, radius=16))
        # 绘制背景块
        offset = get_center(bg.size, t.size)
        bg = draw_card(bg, bl, radius=16, offset=offset, color="white", brightness=230)
        bg.alpha_composite(tt, offset)
        draw = ImageDraw.Draw(bg)
        # 画边框
        for xy in blur_list:
            pos = (
                xy[0] * 2 + offset[0],
                xy[1] * 2 + offset[1],
                xy[2] * 2 + offset[0],
                xy[3] * 2 + offset[1],
            )
            draw.rounded_rectangle(pos, outline="#c7c8d6", width=1, radius=16)

        # 保存
        bg.save(save_path)
        print("拼接完成.")


def save_label(img_path, crop_data: list[tuple[int, int, int]]):
    file_groups = {}

    for file_path in img_path.glob("*.png"):
        file_name = file_path.name

        # 使用正则表达式提取分类数字
        match = re.search(r"\$(\d+)\.png", file_name)
        if match:
            cate = int(match.group(1))
            if cate not in file_groups:
                file_groups[cate] = []
            file_groups[cate].append(file_name)
    for cate, files in file_groups.items():
        if len(crop_data) == 1:
            crop_lb_x, crop_lb_y, crop_width = crop_data[0]
        else:
            crop_lb_x, crop_lb_y, crop_width = crop_data[cate - 1]
        label_out_file = Path(f"resources/labels/{img_path.name}_{cate}.txt")
        img_out_file = Path(f"resources/img/{img_path.name}_{cate}.png")

        full_ori = Image.open(directory_path / "1$1.png")
        text = (
            "0 "
            + f"{(crop_lb_x + (crop_width / 2)) / full_ori.width} "
            + f"{(crop_lb_y + (crop_width / 2)) / full_ori.width} "
            + f"{crop_width / full_ori.width} "
            + f"{crop_width / full_ori.width}"
        )
        full_ori.save(img_out_file)
        label_out_file.write_text(text)


avg_name = "avg_npc_1723_1"
crop_lb_x =460
crop_lb_y = 60
crop_width = 160

bg_path = Path("data/img") / "60_g1_rhodescorridor_bc.png"

directory_path = Path("out/") / avg_name
gen_face(directory_path, [(crop_lb_x, crop_lb_y, crop_width)], bg_path)
save_label(directory_path, [(crop_lb_x, crop_lb_y, crop_width)])
