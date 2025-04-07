# settings.py - Maze Runner Redux 配置文件

import pygame as pg
from pathlib import Path # 导入 Path 对象用于处理路径

# --- 屏幕尺寸 ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 540

# --- 网格和单元格 ---
TILE_SIZE = 30 # 每个网格单元的大小
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# --- 颜色定义 (RGB) ---
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_FLOOR = (40, 40, 40)
COLOR_WALL = (100, 100, 150)
COLOR_WALL_BORDER = (20, 20, 40)
COLOR_PLAYER = (255, 100, 100)
COLOR_PLAYER_BORDER = (100, 0, 0)
COLOR_PLAYER_SPRINT = (255, 150, 150)
COLOR_START = (100, 255, 100)
COLOR_EXIT = (100, 100, 255)
COLOR_ENEMY = (255, 255, 0)
COLOR_ENEMY_BORDER = (150, 150, 0)
COLOR_PROJECTILE = (120, 130, 119)

# --- 游戏设置 ---
GAME_TITLE = "迷宫奔跑者 Redux"
FPS = 60

# --- 字体设置 ---
# !! 新增：定义资源和字体目录 !!
# 获取 settings.py 文件所在的目录
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
FONT_DIR = ASSETS_DIR / "fonts"
# !! 新增：指定要使用的字体文件名 (你需要将这个文件放到 assets/fonts/ 目录下) !!
# 例如使用 "simhei.ttf" (黑体) 或 "msyh.ttf" (微软雅黑) 等
FONT_NAME = "simhei.ttf"

# --- 玩家设置 ---
PLAYER_SIZE_FACTOR = 0.7
PLAYER_SPEED = 3
PLAYER_SPRINT_SPEED = 5
PLAYER_SHOOT_DELAY = 200

# --- 敌人设置 ---
ENEMY_SIZE_FACTOR = 0.6
ENEMY_SPEED = 2
NUM_ENEMIES = 5

# --- 射弹设置 ---
PROJECTILE_RADIUS = 5
PROJECTILE_SPEED = 8
PROJECTILE_LIFETIME = 1000 # 可选

# --- 迷宫生成 ---
WALL = 'W'
FLOOR = 'F'
START = 'S'
EXIT = 'E'