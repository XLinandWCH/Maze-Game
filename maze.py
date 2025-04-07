# maze.py - 迷宫生成和绘制逻辑

import pygame as pg
import random
from settings import * # 导入设置

class Maze:
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        """
        初始化迷宫对象。
        :param width: 迷宫的网格宽度
        :param height: 迷宫的网格高度


        """
        self.grid_width = width #
        self.grid_height = height
        self.grid = []          # 存储迷宫布局的二维列表
        self.wall_rects = []    # 存储所有墙壁 Rect 对象的列表，用于碰撞检测
        self.start_cell = None  # 起点单元格坐标 (列, 行)
        self.exit_cell = None   # 出口单元格坐标 (列, 行)
        self.exit_rect = None   # 出口单元格的 Rect 对象
        self.floor_coords = [] # 存储所有非墙壁单元格中心像素坐标的列表

        self._generate()        # 生成迷宫布局
        self._create_rects()    # 根据布局创建 Rect 对象

    def _generate(self):
        """
        使用随机深度优先搜索 (Randomized DFS) 生成迷宫布局。
        确保迷宫被单层墙壁包围。
        """
        # 1. 初始化网格，全部填充满墙壁
        self.grid = [[WALL for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        # 用于DFS的访问标记数组，大小与 grid 相同
        visited = [[False for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        # 2. DFS 算法生成路径
        #    DFS 只在内部区域操作 (1 到 width-2, 1 到 height-2)
        #    选择一个内部的奇数坐标作为起点（如果宽高允许），或者直接从(1,1)开始
        start_x, start_y = 1, 1
        # 确保起点在网格内且不是边界
        if start_x <= 0 or start_x >= self.grid_width - 1 or start_y <= 0 or start_y >= self.grid_height - 1:
             print(f"警告：起点 ({start_x},{start_y}) 无效或在边界上，迷宫可能无法生成。")
             # 可以选择一个默认的安全起点，如 (1,1)
             start_x, start_y = 1, 1
             # 再次检查，如果网格太小(<=2)，无法进行内部生成
             if self.grid_width <= 2 or self.grid_height <= 2:
                 print("错误：网格尺寸过小，无法生成内部迷宫路径。")
                 # 可以选择生成一个全空的迷宫或者直接返回
                 for r in range(1, self.grid_height - 1):
                     for c in range(1, self.grid_width - 1):
                         self.grid[r][c] = FLOOR
                 self._place_start_exit() # 尝试放置起点终点
                 return # 提前结束生成

        stack = [(start_x, start_y)]
        self.grid[start_y][start_x] = FLOOR # 将起点标记为地板
        visited[start_y][start_x] = True   # 标记起点已访问

        while stack:
            cx, cy = stack[-1]
            neighbors = []

            # 检查潜在的邻居 (间隔一个单元格)
            for dx, dy in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                nx, ny = cx + dx, cy + dy
                # 确保邻居在内部网格边界内 (1 到 width-2, 1 到 height-2) 且未被访问
                if 0 < nx < self.grid_width - 1 and 0 < ny < self.grid_height - 1 and not visited[ny][nx]:
                    # 计算需要打通的墙壁的坐标
                    wall_x, wall_y = cx + dx // 2, cy + dy // 2
                    # 确保墙壁也在内部网格（虽然理论上应该在）
                    if 0 < wall_x < self.grid_width - 1 and 0 < wall_y < self.grid_height - 1:
                         neighbors.append((nx, ny, wall_x, wall_y))

            if neighbors:
                nx, ny, wall_x, wall_y = random.choice(neighbors)
                # 打通邻居单元格
                self.grid[ny][nx] = FLOOR
                visited[ny][nx] = True
                # 打通中间的墙壁
                self.grid[wall_y][wall_x] = FLOOR
                visited[wall_y][wall_x] = True # 墙壁单元格也标记为已访问（因为它变成了路）
                stack.append((nx, ny)) # 将新单元格加入栈
            else:
                stack.pop() # 回溯

        # 3. 放置起点和终点 (这个辅助函数应该在 _generate 内部调用，或者合并进来)
        self._place_start_exit()

        # 新增：修正右侧和底部的双层墙壁问题
        # 处理右侧倒数第二列（grid_width - 2）
        for y in range(1, self.grid_height - 1):
            if self.grid[y][self.grid_width - 2] == WALL and self.grid[y][self.grid_width - 1] == WALL:
                self.grid[y][self.grid_width - 2] = FLOOR

        # 处理底部倒数第二行（grid_height - 2）
        for x in range(1, self.grid_width - 1):
            if self.grid[self.grid_height - 2][x] == WALL and self.grid[self.grid_height - 1][x] == WALL:
                self.grid[self.grid_height - 2][x] = FLOOR

    def _place_start_exit(self):
        """在生成的路径中放置起点和终点。"""
        # 查找所有可放置的路径单元格 (非墙壁单元格)
        floor_cells_list = []
        # 迭代整个网格查找 FLOOR, START, EXIT
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                 # 注意：此时 grid 中可能已经标记了 START/EXIT，查找 FLOOR 即可
                 if self.grid[r][c] == FLOOR:
                    floor_cells_list.append((c, r))

        if not floor_cells_list:
            print("错误：迷宫生成后找不到可用的地板单元格！")
            # 尝试把中心设为地板？这只是极端情况的处理
            if self.grid_width > 2 and self.grid_height > 2:
                cx, cy = self.grid_width // 2, self.grid_height // 2
                self.grid[cy][cx] = FLOOR
                floor_cells_list.append((cx,cy))
            else: # 网格太小，无法放置
                return

        # 随机选择起点
        self.start_cell = random.choice(floor_cells_list)

        # 随机选择终点，确保与起点不同且有一定距离
        min_dist_sq = (self.grid_width * 0.3)**2 + (self.grid_height * 0.3)**2 # 稍微减小距离要求，防止找不到
        possible_exits = [cell for cell in floor_cells_list if cell != self.start_cell]

        if not possible_exits: # 如果只有一个地板单元格
             self.exit_cell = self.start_cell
             print("警告：只有一个可用地板单元，起点和终点相同。")
        else:
             self.exit_cell = random.choice(possible_exits)
             attempts = 0
             max_attempts = len(possible_exits) * 2 # 增加尝试次数
             # 检查距离，如果点太少或距离要求太高，可能死循环
             while ((self.start_cell[0] - self.exit_cell[0])**2 + (self.start_cell[1] - self.exit_cell[1])**2 < min_dist_sq) and attempts < max_attempts:
                 self.exit_cell = random.choice(possible_exits)
                 attempts += 1
             if attempts == max_attempts:
                 print("警告：无法找到距离足够远的终点，使用随机选择的终点。")


        # 在网格上标记起点和终点 (覆盖掉原来的 FLOOR)
        self.grid[self.start_cell[1]][self.start_cell[0]] = START
        self.grid[self.exit_cell[1]][self.exit_cell[0]] = EXIT


    def _create_rects(self):
        """根据生成的网格布局，创建墙壁、出口的 Rect 对象，并记录地板坐标。"""
        self.wall_rects = []
        self.floor_coords = [] # 用于敌人随机生成的位置
        self.exit_rect = None
        # 迭代整个网格 (0 到 width-1, 0 到 height-1)
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                rect = pg.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                cell_type = self.grid[r][c]

                if cell_type == WALL:
                    # 只有墙壁才加入碰撞列表
                    self.wall_rects.append(rect)
                elif cell_type == EXIT:
                    self.exit_rect = rect # 记录出口矩形
                    self.floor_coords.append(rect.center) # 出口也是可通行的地板
                elif cell_type == START:
                    self.floor_coords.append(rect.center) # 起点也是可通行的地板
                elif cell_type == FLOOR:
                     self.floor_coords.append(rect.center) # 普通地板


    def draw(self, surface):
        """
        在指定的 Surface 上绘制迷宫。
        :param surface: 要绘制的目标 Surface (通常是 screen)
        """
        # 迭代整个网格进行绘制
        for r in range(self.grid_height):
            for c in range(self.grid_width):
                rect = pg.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                cell_type = self.grid[r][c]

                if cell_type == WALL:
                    # 绘制墙壁主体
                    pg.draw.rect(surface, COLOR_WALL, rect)
                    # 绘制墙壁边框
                    pg.draw.rect(surface, COLOR_WALL_BORDER, rect, 2) # 2像素宽的边框
                elif cell_type == START:
                    # 绘制起点标识
                    start_marker_rect = rect.inflate(-TILE_SIZE * 0.2, -TILE_SIZE * 0.2)
                    pg.draw.rect(surface, COLOR_START, start_marker_rect, border_radius=3)
                elif cell_type == EXIT:
                    # 绘制出口标识
                    exit_marker_rect = rect.inflate(-TILE_SIZE * 0.2, -TILE_SIZE * 0.2)
                    pg.draw.rect(surface, COLOR_EXIT, exit_marker_rect, border_radius=3)
                # 地板颜色是背景色，不需要特意绘制地板单元格

    def get_start_pixel_pos(self):
        """获取起点单元格左上角的像素坐标。"""
        if self.start_cell:
            return (self.start_cell[0] * TILE_SIZE, self.start_cell[1] * TILE_SIZE)
        print("警告：无法获取起点位置，返回(0,0)")
        return (0, 0) # 默认返回左上角

    def get_random_floor_coord(self, exclude_rect=None, min_dist_sq_from=None, source_pos=None):
        """
        获取一个随机的非墙壁单元格的中心像素坐标。
        :param exclude_rect: 可选，需要排除的 Rect 区域 (例如玩家初始位置)
        :param min_dist_sq_from: 可选，与指定点 source_pos 的最小距离平方
        :param source_pos: 可选，计算最小距离的源点坐标 (元组或 vec)
        :return: 一个随机的地板中心坐标 (x, y) 元组，如果找不到则返回 None
        """
        # 确保 floor_coords 已经生成
        if not self.floor_coords:
            print("错误：无法获取随机地板坐标，列表为空。")
            return None

        valid_coords = list(self.floor_coords) # 创建副本以进行修改

        # 应用排除区域
        if exclude_rect:
            valid_coords = [coord for coord in valid_coords if not exclude_rect.collidepoint(coord)]

        # 应用最小距离
        if min_dist_sq_from is not None and source_pos is not None:
            valid_coords = [coord for coord in valid_coords
                            if (coord[0] - source_pos[0])**2 + (coord[1] - source_pos[1])**2 >= min_dist_sq_from]

        if valid_coords:
            return random.choice(valid_coords)
        else:
            # 如果经过筛选后没有合适的点，尝试返回任意一个地板点（除了排除区域）
            print("警告：无法找到满足所有条件的随机地板坐标，尝试返回备选点。")
            fallback_coords = list(self.floor_coords)
            if exclude_rect:
                 fallback_coords = [coord for coord in fallback_coords if not exclude_rect.collidepoint(coord)]
            if fallback_coords:
                return random.choice(fallback_coords)
            else: # 连备选都没有（迷宫太小或排除区域太大）
                print("错误：连备选随机地板坐标也找不到！")
                return None