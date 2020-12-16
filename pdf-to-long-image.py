# -*- coding: utf-8 -*-

import sys
import os
import datetime
import random
import shutil
import argparse

import fitz
from PIL import Image
from tqdm import tqdm


def gen_random_tmp_path(path_str_len: int = 16) -> str:
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result_list = list()
    result_list.append("tmp_")
    for _ in range(path_str_len):
        result_list.append(random.choice(seed))
    return "".join(result_list)


def convert_pdf_to_images(pdf_path: str, images_path: str) -> int:
    try:
        pdf_doc = fitz.open(pdf_path)
        images_amount = pdf_doc.pageCount
        print("Converting PDF to images...")
        with tqdm(total=images_amount) as pbar:
            for image_id in range(images_amount):
                page = pdf_doc[image_id]
                rotate = int(0)
                # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
                # 此处若是不做设置，默认图片大小为：792X612, dpi=96
                # (1.33333333-->1056x816)   (2-->1584x1224)
                zoom_x = 1.33333333
                zoom_y = 1.33333333
                mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
                pix = page.getPixmap(matrix=mat, alpha=False)

                if not os.path.exists(images_path):
                    os.makedirs(images_path)

                pix.writePNG(images_path + "/" + "images_%s.png" % image_id)
                pbar.update(1)
        return images_amount
    except Exception as exc:
        print(exc)
        return -1


def merge_images_as_long_image(images_path: str, images_amount: int, long_image_path: str) -> bool:
    try:
        long_image = None
        each_tmp_image_size = None
        print("Merging {} images as long image...".format(images_amount))
        with tqdm(total=images_amount) as pbar:
            for image_id in range(images_amount):
                tmp_image = Image.open(
                    images_path + "/" + "images_%s.png" % image_id)
                if long_image is None:
                    each_tmp_image_size = tmp_image.size
                    long_image = Image.new(
                        "RGB", (each_tmp_image_size[0], images_amount * each_tmp_image_size[1]), (250, 250, 250))
                long_image.paste(
                    tmp_image, (0, image_id * each_tmp_image_size[1]))
                pbar.update(1)
        long_image.save(long_image_path, "JPEG")
    except Exception as exc:
        print(exc)
        return False
    return True


def clean_tmp_images(images_path: str) -> bool:
    try:
        shutil.rmtree(images_path)
    except Exception as exc:
        print(exc)
        return False
    return True


def convert_pdf_to_long_image(
        pdf_path: str, long_image_path: str = None,
        images_path: str = None) -> bool:
    if images_path is None:
        images_path = gen_random_tmp_path()
    if long_image_path is None:
        long_image_path = pdf_path.replace(
            ".PDF", ".jpg").replace(".pdf", ".jpg")
    images_amount = convert_pdf_to_images(pdf_path, images_path)
    assert images_amount > 0
    assert merge_images_as_long_image(
        images_path, images_amount, long_image_path)
    assert clean_tmp_images(images_path)


if "__main__" == __name__:
    parser = argparse.ArgumentParser(description='Convert PDF to Long Image.')
    parser.add_argument(
        '--pdf_path', help='the path of PDF wanna to convert', type=str, required=True)
    parser.add_argument('--long_image_path', help='the PDF convert result long image path',
                        type=str, required=False, default=None)
    parser.add_argument('--tmp_images_path', help='the images path before converted to long image',
                        type=str, required=False, default=None)

    args = parser.parse_args()
    convert_pdf_to_long_image(
        args.pdf_path, args.long_image_path, args.tmp_images_path)
