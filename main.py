# game.py - 主游戏逻辑和循环

import pygame as pg
import sys
import random

# 从其他模块导入类和设置
from settings import *
from utils import draw_text, vec
from maze import Maze
from player import Player
from enemy import Enemy
# Projectile 类在 Player shoot 时被实例化，这里不需要直接导入

class Game:
    def __init__(self):
        """初始化 Pygame、屏幕、时钟和游戏变量。"""
        pg.init()
        pg.mixer.init() # 初始化音频（如果需要）
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption(GAME_TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.game_state = "START" # 游戏状态: START, PLAYING, GAME_OVER, WIN

        self.maze = None          # 当前迷宫对象
        self.player = None        # 玩家对象
        self.enemies = []         # 敌人对象列表
        self.projectiles = []     # 射弹对象列表

        # !! 新增：初始化关卡数 !!
        self.current_level = 1

    def reset_game(self):
        """重置游戏状态，生成新迷宫和对象。"""
        print("正在重置游戏...")
        self.maze = Maze()              # 创建新迷宫
        self.enemies = []             # 清空敌人列表
        self.projectiles = []         # 清空射弹列表

        # --- 创建玩家 ---
        start_pixel_pos = self.maze.get_start_pixel_pos()
        player_start_x = start_pixel_pos[0] + (TILE_SIZE - int(TILE_SIZE * PLAYER_SIZE_FACTOR)) // 2
        player_start_y = start_pixel_pos[1] + (TILE_SIZE - int(TILE_SIZE * PLAYER_SIZE_FACTOR)) // 2
        self.player = Player(self, player_start_x, player_start_y)
        print(f"玩家放置在: ({player_start_x}, {player_start_y})")

        # --- 创建敌人 ---
        min_enemy_dist_sq = (TILE_SIZE * 4)**2 # 敌人距离玩家起点的最小距离平方
        player_start_center = self.player.rect.center

        for _ in range(NUM_ENEMIES):
             # 获取一个合适的随机地板坐标作为敌人出生点
            spawn_coord = self.maze.get_random_floor_coord(
                exclude_rect=self.player.rect, # 避免出生在玩家身上
                min_dist_sq_from=min_enemy_dist_sq,
                source_pos=player_start_center
            )
            if spawn_coord:
                self.enemies.append(Enemy(spawn_coord[0], spawn_coord[1]))
                # print(f"敌人在 {spawn_coord} 生成")
            else:
                print("警告：无法为敌人找到合适的生成位置！")


        self.game_state = "PLAYING" # 设置游戏状态为进行中

    def run(self):
        """游戏主循环。"""
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0 # 获取帧间隔时间(秒)，如果需要基于时间的移动

            self.events() # 处理事件
            self.update() # 更新游戏状态
            self.draw()   # 绘制画面

        self.quit_game() # 退出循环后清理

    def events(self):
        """处理所有事件 (键盘、鼠标、退出等)。"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            if event.type == pg.KEYDOWN:
                if self.game_state == "START":
                    if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                        self.reset_game() # 按回车开始游戏
                    elif event.key == pg.K_ESCAPE:
                         self.running = False
                elif self.game_state == "PLAYING":
                     if event.key == pg.K_ESCAPE: # 游戏中按 ESC 退出
                         self.running = False
                     # 玩家移动和射击输入在 Player.handle_input 中处理
                elif self.game_state in ["GAME_OVER", "WIN"]:
                     if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                         self.game_state = "START" # 按回车返回开始界面
                         # self.reset_game() # 或者直接重新开始
                     elif event.key == pg.K_ESCAPE:
                         self.running = False

    def update(self):
        """更新所有游戏对象和逻辑。"""
        if self.game_state != "PLAYING":
            return # 如果游戏不在进行中，则不更新逻辑

        # --- 更新玩家 ---
        if self.player:
            self.player.handle_input() # 处理输入必须在 update 前
            self.player.update(self.maze.wall_rects)

        # --- 更新敌人 ---
        for enemy in self.enemies:
            enemy.update(self.maze.wall_rects)

        # --- 更新射弹 ---
        # 使用列表副本进行迭代，因为可能在循环中移除元素
        for projectile in self.projectiles[:]:
            projectile.update()

        # --- 碰撞检测 ---
        self.check_collisions()

        # --- 检查游戏状态改变条件 ---
        if self.player:
            # 检查胜利条件
            if self.maze.exit_rect and self.player.rect.colliderect(self.maze.exit_rect):
                # !! 新增：增加关卡数 !!
                self.current_level += 1
                print(f"到达出口！进入第 {self.current_level} 关")
                self.reset_game() # 重置游戏，开始下一关


    def check_collisions(self):
        """处理不同对象之间的碰撞。"""
        if not self.player: return # 如果没有玩家对象，则不进行碰撞检测

        # 1. 射弹 vs 墙壁
        for projectile in self.projectiles[:]: # 迭代副本
            for wall in self.maze.wall_rects:
                # 使用射弹的 rect 进行粗略检测
                if projectile.rect.colliderect(wall):
                    projectile.kill() # 射弹撞墙消失
                    break # 一个射弹只处理一次撞墙

        # 2. 射弹 vs 敌人
        # 使用列表推导式来高效地移除被击中的敌人和对应的射弹
        enemies_hit = []
        projectiles_to_remove = []
        remaining_enemies = []

        for enemy in self.enemies:
            enemy_was_hit = False
            for projectile in self.projectiles[:]: # 迭代射弹副本
                 # 用 circle-rect 碰撞可能更精确，但 rect-rect 通常足够
                 if enemy.rect.colliderect(projectile.rect):
                     enemies_hit.append(enemy) # 标记敌人被击中
                     projectiles_to_remove.append(projectile) # 标记射弹待移除
                     projectile.kill() # 立即从列表中移除，避免重复标记
                     enemy_was_hit = True
                     break # 一个敌人被一个子弹击中即可
            if not enemy_was_hit:
                 remaining_enemies.append(enemy) # 保留未被击中的敌人

        self.enemies = remaining_enemies # 更新敌人列表

        # print(f"击中敌人: {len(enemies_hit)}, 剩余敌人: {len(self.enemies)}")


        # 3. 玩家 vs 敌人
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.game_state = "GAME_OVER"
                print("被敌人抓住了！")
                break # 碰到一个敌人就结束


    def draw(self):
        """绘制所有游戏元素到屏幕上。"""
        # --- 绘制背景 (地板色) ---
        self.screen.fill(COLOR_FLOOR)

        # --- 根据游戏状态绘制不同内容 ---
        if self.game_state == "START":
            self.show_start_screen()
        elif self.game_state == "PLAYING":
            # 绘制迷宫
            if self.maze:
                self.maze.draw(self.screen)
            # 绘制敌人
            for enemy in self.enemies:
                enemy.draw(self.screen)
            # 绘制射弹
            for projectile in self.projectiles:
                projectile.draw(self.screen)
            # 绘制玩家 (最后绘制，覆盖在其他东西上面)
            if self.player:
                self.player.draw(self.screen)

            # !! 新增：绘制当前关卡数 !!
            level_text = f"关卡: {self.current_level}"
            draw_text(self.screen, level_text, 24, COLOR_WHITE, 10, 10, align="topleft")


        elif self.game_state == "GAME_OVER":
            self.show_end_screen("游戏结束", COLOR_PLAYER)
        elif self.game_state == "WIN":
            self.show_end_screen("你赢了!", COLOR_EXIT)

        # --- 刷新屏幕显示 ---
        pg.display.flip()

    def show_start_screen(self):
        """显示开始界面。"""
        draw_text(self.screen, GAME_TITLE, 64, COLOR_WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4)
        draw_text(self.screen, "方向键或WASD移动", 30, COLOR_WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40)
        draw_text(self.screen, "按住 Shift 加速", 30, COLOR_WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        draw_text(self.screen, "按 空格键 射击", 30, COLOR_WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40)
        draw_text(self.screen, "到达蓝色方块获胜", 30, COLOR_EXIT, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 80)
        draw_text(self.screen, "躲避黄色方块", 30, COLOR_ENEMY, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 120)
        draw_text(self.screen, "按 Enter 开始游戏", 35, COLOR_WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.85)

    def show_end_screen(self, message, message_color):
         """显示游戏结束或胜利界面。"""
         # 先绘制游戏最后一帧（可选）
         if self.maze: self.maze.draw(self.screen)
         for enemy in self.enemies: enemy.draw(self.screen)
         if self.player: self.player.draw(self.screen) # 即使输了也画出来

         # 绘制半透明遮罩
         overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
         overlay.fill((0, 0, 0, 180)) # 半透明黑色
         self.screen.blit(overlay, (0,0))

         # 绘制结束信息
         draw_text(self.screen, message, 72, message_color, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
         draw_text(self.screen, "按 Enter 返回标题界面", 35, COLOR_WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.6)
         draw_text(self.screen, "按 ESC 退出游戏", 35, COLOR_WHITE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.6 + 50)


    def quit_game(self):
        """清理并退出 Pygame。"""
        print("退出游戏中...")
        pg.quit()
        sys.exit()

# --- 主程序入口 ---
if __name__ == '__main__':
    print("游戏启动...")
    game_instance = Game()
    game_instance.run()