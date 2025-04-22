import shutil
from pathlib import Path

from PIL import Image

from download_res import get_res_version
from unpacker import ArkMediaUnPacker
from util import extract_package


def gen_avg_chararts(unpack_info: dict) -> list[Path]:
    """生成人物差分

    Args:
        url (str): 群文件 url
        source_file (str): 下载文件名

    Returns:
        List[Path]: 生成图片的地址列表
    """
    base_path: Path = unpack_info["output_path"]
    type_cnt = unpack_info["type_cnt"]
    face_alpha_set = unpack_info["pics"]["face_alpha"]
    full_alpha_set = unpack_info["pics"]["full_alpha"]
    file_name = unpack_info["pics"]["full"][0].split("$")[0]
    result_list = []

    for avg_type in range(type_cnt):
        avg_type_name = avg_type + 1
        # 各种路径
        avg_img_path = base_path / "full" / f"{file_name}${avg_type_name}.png"
        avg_alpha_path = ""
        if full_alpha_set:
            avg_alpha_path = (
                base_path / "full" / f"{file_name}${avg_type_name}[alpha].png"
            )

        pos_info = unpack_info["pos_info"][avg_type]
        face_size = (pos_info["face_size_x"], pos_info["face_size_y"])
        face_pos = (pos_info["face_pos_x"], pos_info["face_pos_y"])
        face_list = unpack_info["pics"]["face"]

        if face_list:
            save_path: Path = base_path.parent.parent / "out" / file_name
        else:
            save_path: Path = base_path.parent.parent / "out"

        if not save_path.exists():
            save_path.mkdir()

        # 确定有差分
        if face_list:
            for i in face_list:
                if not i.endswith(f"{avg_type_name}.png"):
                    continue
                # 打开图片
                avg_img = Image.open(avg_img_path)
                base_img = Image.new("RGBA", size=avg_img.size)

                if full_alpha_set:
                    avg_alpha = Image.open(avg_alpha_path).convert(mode="L")
                    base_img.paste(avg_img, mask=avg_alpha)
                else:
                    base_img.paste(avg_img)

                f = Image.open(base_path / "face" / i)
                head = Image.new("RGBA", f.size)

                if face_alpha_set:
                    # 脸部遮罩路径
                    f_alpha_path = ""
                    for alpha in face_alpha_set:
                        if i.startswith(alpha):
                            f_alpha_path = base_path / "face" / f"{alpha}[alpha].png"
                    # 没有指定遮罩的时候使用默认遮罩
                    if not f_alpha_path:
                        f_alpha_path = (
                            base_path / "face" / f"{avg_type_name}$[alpha].png"
                        )

                    f_alpha = Image.open(f_alpha_path).convert(mode="L")
                    head.paste(f, mask=f_alpha)
                else:
                    head.paste(f)

                if head.width <= 256:
                    head = head.resize(face_size, resample=Image.LANCZOS)
                    base_img.paste(head, box=face_pos)
                else:
                    # 处理脸部差分变成全身立绘的情况
                    base_img.paste(head)

                base_img.save(save_path / i, quality=100)
                result_list.append(save_path / i)
        else:
            avg_img = Image.open(avg_img_path)
            base_img = Image.new("RGBA", size=avg_img.size)
            if full_alpha_set:
                avg_alpha = Image.open(avg_alpha_path).convert(mode="L")
                base_img.paste(avg_img, mask=avg_alpha)
            else:
                base_img.paste(avg_img)

            base_img.save(save_path / avg_img_path.name, quality=100)
            result_list.append(save_path / avg_img_path.name)
    # 删除缓存文件
    shutil.rmtree(base_path)
    return result_list


error_ls = []
res_version = get_res_version()

for p in Path(f"download/{res_version}/new/avg/characters/").glob("*.zip"):
# for p in Path(f"cache/download/{res_version}/new/avg/characters/").glob("*.zip"):
    file_name = p.name
    print(f"processing: {file_name}")
    unpack_info = ArkMediaUnPacker(extract_package(p)).export_avg_chararts()
    # try:
    gen_avg_chararts(unpack_info)
    # except Exception as e:
    #     error_ls.append(file_name)
    #     print(e)

for i in error_ls:
    print(i)

