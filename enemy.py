# enemy.py - 敌人（怪物）类

import pygame as pg
import random
from settings import * # 导入设置
from utils import vec # 导入向量

class Enemy:
    def __init__(self, x_center, y_center):
        """
        初始化敌人对象。
        :param x_center: 敌人初始中心 x 坐标
        :param y_center: 敌人初始中心 y 坐标
        """
        self.size = int(TILE_SIZE * ENEMY_SIZE_FACTOR)
        self.rect = pg.Rect(0, 0, self.size, self.size)
        self.pos = vec(x_center, y_center) # 使用中心精确位置向量
        self.rect.center = self.pos
        self.vel = vec(random.choice([-ENEMY_SPEED, ENEMY_SPEED]),
                       random.choice([-ENEMY_SPEED, ENEMY_SPEED])) # 初始随机速度

    def update(self, wall_rects):
        """
        更新敌人位置，并处理与墙壁的碰撞反弹。
        :param wall_rects: 包含所有墙壁 Rect 对象的列表
        """
        # --- 更新精确位置 ---
        self.pos += self.vel

        # --- 碰撞检测与位置修正 + 反弹 ---
        self.rect.centerx = self.pos.x
        collided_x = self._collide_and_bounce(wall_rects, 'x')
        self.rect.centery = self.pos.y
        collided_y = self._collide_and_bounce(wall_rects, 'y')

        # --- 屏幕边界碰撞与反弹 ---
        if self.rect.left < 0:
            self.rect.left = 0
            if not collided_x: self.vel.x *= -1 # 如果不是因为撞墙而是撞屏幕边界
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            if not collided_x: self.vel.x *= -1
        if self.rect.top < 0:
            self.rect.top = 0
            if not collided_y: self.vel.y *= -1
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            if not collided_y: self.vel.y *= -1

        # --- 最后，根据修正后的 rect 更新精确位置 pos ---
        self.pos.x = self.rect.centerx
        self.pos.y = self.rect.centery


    def _collide_and_bounce(self, wall_rects, direction):
        """
        私有方法：检测碰撞并反弹。
        :param wall_rects: 墙壁 Rect 列表
        :param direction: 'x' 或 'y'
        :return: True 如果发生碰撞，否则 False
        """
        collided = False
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                collided = True
                if direction == 'x':
                    if self.vel.x > 0:
                        self.rect.right = wall.left
                    elif self.vel.x < 0:
                        self.rect.left = wall.right
                    self.vel.x *= -1 # 反弹
                    self.pos.x = self.rect.centerx # 更新精确位置
                elif direction == 'y':
                    if self.vel.y > 0:
                        self.rect.bottom = wall.top
                    elif self.vel.y < 0:
                        self.rect.top = wall.bottom
                    self.vel.y *= -1 # 反弹
                    self.pos.y = self.rect.centery # 更新精确位置
                break # 处理完一次碰撞即可退出循环
        return collided


    def draw(self, surface):
        """
        在指定的 Surface 上绘制敌人。
        :param surface: 目标 Surface
        """
        # --- 绘制边框 ---
        border_size_increase = 1
        border_rect = pg.Rect(0, 0, self.rect.width + border_size_increase * 2, self.rect.height + border_size_increase * 2)
        border_rect.center = self.rect.center
        pg.draw.rect(surface, COLOR_ENEMY_BORDER, border_rect, border_radius=5)

        # --- 绘制敌人主体 ---
        pg.draw.rect(surface, COLOR_ENEMY, self.rect, border_radius=5)