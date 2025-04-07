# player.py - 玩家类

import pygame as pg
from settings import * # 导入设置
from utils import vec # 导入向量类型
from projectile import Projectile # 导入射弹类

class Player:
    def __init__(self, game, x, y):
        """
        初始化玩家对象。
        :param game: 对主游戏对象的引用，用于访问游戏资源 (如射弹列表)
        :param x: 玩家初始 x 坐标 (左上角)
        :param y: 玩家初始 y 坐标 (左上角)
        """
        self.game = game # 保存对游戏主类的引用
        self.size = int(TILE_SIZE * PLAYER_SIZE_FACTOR) # 计算玩家的像素尺寸
        self.rect = pg.Rect(x, y, self.size, self.size) # 玩家的矩形区域
        self.vel = vec(0, 0) # 玩家的速度向量
        self.pos = vec(x + self.size / 2, y + self.size / 2) # 玩家的中心精确位置向量
        self.rect.center = self.pos # 更新矩形中心

        self.sprinting = False # 玩家是否在加速
        self.last_shot_time = 0 # 上次射击的时间戳
        self.last_move_dir = vec(1, 0) # 记录上次移动的方向，用于射击，默认为右

    def handle_input(self):
        """处理玩家的键盘输入。"""
        self.vel = vec(0, 0) # 每帧开始时重置速度
        keys = pg.key.get_pressed()

        # --- 加速 ---
        self.sprinting = keys[pg.K_LSHIFT] or keys[pg.K_p]
        current_speed = PLAYER_SPRINT_SPEED if self.sprinting else PLAYER_SPEED

        # --- 移动 ---
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.vel.x = -current_speed
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vel.x = current_speed
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel.y = -current_speed
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel.y = current_speed

        # --- 防止对角线速度过快 (可选，但推荐) ---
        if self.vel.x != 0 and self.vel.y != 0:
            # 将速度向量长度调整为 current_speed
            self.vel = self.vel.normalize() * current_speed

        # --- 记录最后移动方向 (用于射击) ---
        if self.vel.length_squared() > 0: # 仅在移动时更新方向
            self.last_move_dir = self.vel.normalize()


        # --- 射击 ---
        if keys[pg.K_o]:
            self.shoot()

    def shoot(self):
        """玩家进行射击。"""
        now = pg.time.get_ticks()
        if now - self.last_shot_time > PLAYER_SHOOT_DELAY:
            self.last_shot_time = now
            # 计算射弹的起始位置 (玩家中心 + 稍微向前偏移一点)
            spawn_pos = self.pos + self.last_move_dir * (self.size / 2 + PROJECTILE_RADIUS)
            # 创建射弹实例，并将其添加到游戏主类的射弹列表中
            Projectile(self.game, spawn_pos, self.last_move_dir)


    def update(self, wall_rects):
        """
        更新玩家的位置，并处理与墙壁的碰撞。
        :param wall_rects: 包含所有墙壁 Rect 对象的列表
        """
        # --- 更新精确位置 ---
        # 注意：这里我们不使用 dt (delta time)，因为速度是像素/帧。
        # 如果需要基于时间的移动，需要乘以 self.game.dt
        self.pos += self.vel # 更新中心位置

        # --- 碰撞检测与位置修正 ---
        # 将更新后的中心位置应用到矩形上，分开处理 x 和 y 轴
        self.rect.centerx = self.pos.x
        self._collide_with_walls(wall_rects, 'x') # 水平碰撞检测和修正
        self.rect.centery = self.pos.y
        self._collide_with_walls(wall_rects, 'y') # 垂直碰撞检测和修正

        # --- 确保玩家在屏幕边界内 ---
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        # --- 最后，根据修正后的 rect 更新精确位置 pos ---
        self.pos.x = self.rect.centerx
        self.pos.y = self.rect.centery


    def _collide_with_walls(self, wall_rects, direction):
        """
        私有方法：检测并处理与墙壁的碰撞。
        :param wall_rects: 墙壁 Rect 列表
        :param direction: 'x' 或 'y'，指示当前处理的轴向
        """
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                if direction == 'x':
                    if self.vel.x > 0: # 向右移动撞墙
                        self.rect.right = wall.left # 紧贴墙左边
                    elif self.vel.x < 0: # 向左移动撞墙
                        self.rect.left = wall.right # 紧贴墙右边
                    self.vel.x = 0 # 碰撞后水平速度归零 (可选)
                    self.pos.x = self.rect.centerx # 更新精确位置
                elif direction == 'y':
                    if self.vel.y > 0: # 向下移动撞墙
                        self.rect.bottom = wall.top # 紧贴墙上边
                    elif self.vel.y < 0: # 向上移动撞墙
                        self.rect.top = wall.bottom # 紧贴墙下边
                    self.vel.y = 0 # 碰撞后垂直速度归零 (可选)
                    self.pos.y = self.rect.centery # 更新精确位置


    def draw(self, surface):
        """
        在指定的 Surface 上绘制玩家。
        :param surface: 目标 Surface
        """
        # --- 确定玩家颜色 (是否在加速) ---
        player_color = COLOR_PLAYER_SPRINT if self.sprinting else COLOR_PLAYER

        # --- 绘制边框 ---
        # 计算边框矩形 (比玩家矩形稍大一点)
        border_size_increase = 2 # 边框每边多出的像素
        border_rect = pg.Rect(0, 0, self.rect.width + border_size_increase * 2, self.rect.height + border_size_increase * 2)
        border_rect.center = self.rect.center # 保持中心对齐

        pg.draw.rect(surface, COLOR_PLAYER_BORDER, border_rect, border_radius=3)

        # --- 绘制玩家主体 ---
        pg.draw.rect(surface, player_color, self.rect, border_radius=3)