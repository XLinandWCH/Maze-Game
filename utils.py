# utils.py - 辅助函数

import pygame as pg
from settings import * # 导入设置以便使用颜色、字体路径等
from pathlib import Path # 确保导入 Path

# --- 字体加载缓存 (优化：避免重复加载同一字体) ---
font_cache = {}

def load_font(size):
    """
    加载指定大小的中文字体。
    如果加载失败，则回退到 Pygame 默认字体。
    :param size: 字体大小
    :return: Pygame Font 对象
    """
    # 检查缓存
    if size in font_cache:
        return font_cache[size]

    # 构建完整的字体文件路径
    font_path = FONT_DIR / FONT_NAME
    try:
        # 尝试加载指定的中文字体文件
        font = pg.font.Font(str(font_path), size) # Path 对象需要转为字符串
        print(f"成功加载字体: {font_path} (大小: {size})")
        font_cache[size] = font # 存入缓存
        return font
    except FileNotFoundError:
        print(f"错误：找不到字体文件 '{font_path}'。")
        print("请确保在 'assets/fonts/' 目录下放置了名为 '{FONT_NAME}' 的字体文件。")
    except pg.error as e:
        print(f"错误：加载字体 '{font_path}' 时出错: {e}")
        print("可能是字体文件损坏或不受支持。")
    except Exception as e: # 捕获其他可能的异常
        print(f"加载字体时发生未知错误: {e}")

    # --- 回退逻辑 ---
    print(f"将使用 Pygame 默认字体 (大小: {size}) 作为备选。")
    try:
        default_font = pg.font.Font(None, size) # 加载 Pygame 默认字体
        font_cache[size] = default_font # 默认字体也缓存起来
        return default_font
    except Exception as e:
        print(f"错误：连 Pygame 默认字体也无法加载: {e}")
        # 极端情况：如果连默认字体都加载失败，返回一个最小的替代品或退出
        # 这里我们尝试返回一个固定的小字体
        try:
            return pg.font.Font(None, 12)
        except: # 如果连这个也失败... 就没办法了
             print("!!! 无法加载任何字体，文本将无法显示 !!!")
             # 返回一个“空”字体对象，避免程序崩溃，但不会渲染任何东西
             class DummyFont:
                 def render(self, *args, **kwargs):
                     return pg.Surface((0,0)) # 返回一个空 Surface
                 def get_linesize(self):
                     return 10 # 返回一个合理的值避免其他地方崩溃
             return DummyFont()


def draw_text(surface, text, size, color, x, y, align="center"):
    """
    在屏幕上绘制文本 (使用 load_font 加载字体)。
    :param surface: 目标 Surface 对象 (通常是 screen)
    :param text: 要绘制的字符串
    :param size: 字体大小
    :param color: 文本颜色 (RGB元组或颜色名)
    :param x: 文本位置的 x 坐标
    :param y: 文本位置的 y 坐标
    :param align: 对齐方式 ("center", "topleft", "topright", 等)
    """
    # !! 修改：调用 load_font 获取字体对象 !!
    font = load_font(size)
    # font = pg.font.Font(None, size) # 旧的使用默认字体的方法（注释掉）

    # 使用 font 对象渲染文本
    text_surface = font.render(text, True, color) # 第二个参数 True 表示开启抗锯齿
    text_rect = text_surface.get_rect()

    # 根据对齐方式设置文本位置
    if align == "center":
        text_rect.center = (x, y)
    elif align == "topleft":
        text_rect.topleft = (x, y)
    elif align == "topright":
        text_rect.topright = (x, y)
    elif align == "midleft":
        text_rect.midleft = (x,y)
    elif align == "midright":
        text_rect.midright = (x,y)
    elif align == "midtop":
        text_rect.midtop = (x,y)
    elif align == "midbottom":
        text_rect.midbottom = (x,y)
    # 可以根据需要添加更多对齐方式

    # 在目标 Surface 上绘制文本
    surface.blit(text_surface, text_rect)

# 创建一个向量类型，方便进行数学运算 (如果需要更复杂移动)
vec = pg.math.Vector2