# projectile.py - 射弹（子弹）类

import pygame as pg
from settings import * # 导入设置
from utils import vec # 导入向量

class Projectile:
    def __init__(self, game, pos, direction):
        """
        初始化射弹对象。
        :param game: 对主游戏对象的引用，用于将其添加到射弹列表
        :param pos: 射弹的初始位置 (中心点向量 vec)
        :param direction: 射弹的初始方向 (单位向量 vec)
        """
        self.game = game
        self.pos = vec(pos) # 复制位置向量
        self.vel = direction.normalize() * PROJECTILE_SPEED # 速度向量
        self.radius = PROJECTILE_RADIUS
        self.rect = pg.Rect(pos.x - self.radius, pos.y - self.radius,
                             self.radius * 2, self.radius * 2) # 用于粗略碰撞检测的矩形
        self.spawn_time = pg.time.get_ticks() # 记录生成时间，用于判断寿命

        # 将自身添加到游戏主类的射弹列表中
        self.game.projectiles.append(self)

    def update(self):
        """更新射弹位置并检查寿命。"""
        self.pos += self.vel
        self.rect.center = self.pos # 更新碰撞矩形的位置

        # --- 检查寿命 ---
        # if pg.time.get_ticks() - self.spawn_time > PROJECTILE_LIFETIME:
        #     self.kill() # 标记为待移除

        # --- 检查是否超出屏幕边界 ---
        if not (0 < self.pos.x < SCREEN_WIDTH and 0 < self.pos.y < SCREEN_HEIGHT):
            self.kill() # 超出边界也移除

    def kill(self):
        """从游戏列表中移除自身。"""
        if self in self.game.projectiles:
            self.game.projectiles.remove(self)

    def draw(self, surface):
        """
        在指定的 Surface 上绘制射弹。
        :param surface: 目标 Surface
        """
        pg.draw.circle(surface, COLOR_PROJECTILE, self.rect.center, self.radius)