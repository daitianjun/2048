import time
import tkinter as tk
import tkinter.messagebox

# You may import any submodules of tkinter here if you wish
# You may also import anything from the typing module
# All other additional imports will result in a deduction of up to 100% of your A3 mark

from a3_support import *


# Write your classes here
# 模型类
class Model:
    def __init__(self) -> None:
        self.new_game()

    # 重置游戏状态
    def new_game(self) -> None:
        self.play_flag = False
        self.matrix = [[None for i in range(NUM_COLS)] for i in range(NUM_ROWS)]
        self.add_tile()
        self.add_tile()

    # 新位置随机生成一个瓷砖 generate_tile
    def add_tile(self) -> None:
        self.add_f = [[None for i in range(NUM_COLS)] for i in range(NUM_ROWS)]
        tile = generate_tile(self.matrix)
        self.matrix[tile[0][0]][tile[0][1]] = tile[1]

        self.add_f[tile[0][0]][tile[0][1]] = tile[1]

    # 获取方块矩阵
    def get_tiles(self):
        return self.matrix

    # 移动到左端,并合并
    def move_left(self) -> None:
        self.matrix = stack_left(combine_left(stack_left(self.matrix))[0])

    # 移动到右端并合并
    def move_right(self) -> None:
        stacked_tiles = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        for i in list(range(NUM_ROWS))[::-1]:
            to_fill = 3
            for j in list(range(NUM_COLS))[::-1]:
                if self.matrix[i][j] is not None:
                    stacked_tiles[i][to_fill] = self.matrix[i][j]
                    to_fill -= 1
        #  合并
        combined_tiles = [row[:] for row in stacked_tiles]
        score_added = 0
        for i in list(range(NUM_ROWS))[::-1]:
            for j in list(range(1, NUM_COLS))[::-1]:
                if combined_tiles[i][j] is not None and combined_tiles[i][j] == combined_tiles[i][j - 1]:
                    combined_tiles[i][j] *= 2
                    combined_tiles[i][j - 1] = None
                    score_added += combined_tiles[i][j]
        # 合并之后移动
        stacked_tiles = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        for i in list(range(NUM_ROWS))[::-1]:
            to_fill = 3
            for j in list(range(NUM_COLS))[::-1]:
                if combined_tiles[i][j] is not None:
                    stacked_tiles[i][to_fill] = combined_tiles[i][j]
                    to_fill -= 1
        self.matrix = stacked_tiles

    # 移动到顶部
    def move_up(self) -> None:
        stacked_tiles = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        for i in range(NUM_ROWS):
            to_fill = 0
            for j in range(NUM_COLS):
                if self.matrix[j][i] is not None:
                    stacked_tiles[to_fill][i] = self.matrix[j][i]
                    to_fill += 1
        #  合并
        combined_tiles = [row[:] for row in stacked_tiles]
        score_added = 0
        for i in range(NUM_ROWS - 1):
            for j in range(NUM_COLS):
                if combined_tiles[i][j] is not None and combined_tiles[i][j] == combined_tiles[i + 1][j]:
                    combined_tiles[i][j] *= 2
                    combined_tiles[i + 1][j] = None
                    score_added += combined_tiles[i][j]
        # 合并之后移动
        stacked_tiles = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        for i in range(NUM_ROWS):
            to_fill = 0
            for j in range(NUM_COLS):
                if combined_tiles[j][i] is not None:
                    stacked_tiles[to_fill][i] = combined_tiles[j][i]
                    to_fill += 1
        self.matrix = stacked_tiles

    # 移动到底部
    def move_down(self) -> None:
        stacked_tiles = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        for i in list(range(NUM_ROWS))[::-1]:
            to_fill = 3
            for j in list(range(NUM_COLS))[::-1]:
                if self.matrix[j][i] is not None:
                    stacked_tiles[to_fill][i] = self.matrix[j][i]
                    to_fill -= 1

        #  合并
        combined_tiles = [row[:] for row in stacked_tiles]
        score_added = 0
        for i in list(range(1, NUM_ROWS))[::-1]:
            for j in range(NUM_COLS):
                if combined_tiles[i][j] is not None and combined_tiles[i][j] == combined_tiles[i - 1][j]:
                    combined_tiles[i][j] *= 2
                    combined_tiles[i - 1][j] = None
                    score_added += combined_tiles[i][j]
        # 合并之后移动
        stacked_tiles = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        for i in list(range(NUM_ROWS))[::-1]:
            to_fill = 3
            for j in list(range(NUM_COLS))[::-1]:
                if combined_tiles[j][i] is not None:
                    stacked_tiles[to_fill][i] = combined_tiles[j][i]
                    to_fill -= 1
        self.matrix = stacked_tiles

    # 根据 wsad进行移动，根据状态是否改变返回bool
    def attempt_move(self, move: str) -> bool:
        self.last = self.matrix
        if move == LEFT:
            self.move_left()
        elif move == RIGHT:
            self.move_right()
        elif move == UP:
            self.move_up()
        elif move == DOWN:
            self.move_down()
        if self.last == self.matrix:
            # 状态未改变
            return False
        else:
            return True

    # 游戏赢了就返回True
    def has_won(self) -> bool:
        for item_list in self.matrix:
            if 2048 in item_list:
                return True
        return False

    # 游戏输了就返回True
    def has_lost(self) -> bool:
        for item_list in self.matrix:
            if None in item_list:
                return False
        return True


# 视图类
class GameGrid(tk.Canvas):
    def __init__(self, master: tk.Tk, **kwargs) -> None:
        super(GameGrid, self).__init__(**kwargs)

    # 返回左上角和右下角坐标
    def _get_bbox(self, position):
        x1 = BUFFER * (position[1] + 1) + position[1] * 90
        y1 = BUFFER * (position[0] + 1) + position[0] * 90
        x2 = x1 + 90
        y2 = y1 + 90
        return x1, y1, x2, y2

    # 获取中心坐标
    def _get_midpoint(self, position):
        center_x = 55 + 100 * position[1]
        center_y = 55 + 100 * position[0]
        return center_x, center_y

    # 清除所有项目
    def clear(self) -> None:
        self.delete(tk.ALL)


    # 根据给定的瓷砖重新绘制网格
    def redraw(self, tiles):
        for row, i in enumerate(tiles):
            for column, j in enumerate(i):
                position = self._get_bbox((row, column))
                text_position = self._get_midpoint((row, column))
                # 参数为对角线两个点的坐标
                color = COLOURS.get(j)
                self.create_rectangle(position[0], position[1], position[2], position[3],
                                      fill=color, outline=BACKGROUND_COLOUR)
                if j:
                    self.create_text(text_position[0], text_position[1], text=j, font=TILE_FONT, fill=FG_COLOURS.get(j))


# 游戏类
class Game:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title('CSSE1001/7030 2022 Semester 2 A3')
        self.model = Model()
        self.master.bind("<KeyPress> ", self.attempt_move)
        self.grid = GameGrid(master, width=BOARD_WIDTH, height=BOARD_HEIGHT, bg=BACKGROUND_COLOUR)

        # 160
        master.geometry(str(BOARD_WIDTH + 10) + 'x' + str(BOARD_HEIGHT + 90))
        title = tk.Label(master, text='2048', font=TITLE_FONT, fg='white', bg='#f4d54b', width=BOARD_WIDTH)
        title.pack()
        self.grid.pack()
        self.draw()
        # self.score_label = tk.Label(master, text='SCORE\n', bg=BACKGROUND_COLOUR, fg=COLOURS.get(None), width=6,
        #                             font=('Arial bold', 16))
        # self.score_label.place(relx=0.04, rely=0.88)
        # self.score = tk.Label(master, text='0', fg='white', bg=BACKGROUND_COLOUR)
        # self.score.place(relx=0.12, rely=0.93, )
        #
        # self.undo_label = tk.Label(master, text='SCORE\n', bg=BACKGROUND_COLOUR, fg=COLOURS.get(None), width=6,
        #                             font=('Arial bold', 16))
        # self.undo_label.place(relx=0.04, rely=0.88)
        # self.score = tk.Label(master, text='0', fg='white', bg=BACKGROUND_COLOUR)
        # self.score.place(relx=0.12, rely=0.93, )

    # 根据状态绘制视图类
    def draw(self) -> None:
            self.grid.redraw(self.model.get_tiles())

    # 根据移动事件移动，重新绘制视图，如果游戏没赢就150ms创建一个新的瓷砖
    def attempt_move(self, event: tk.Event):
        keysym = event.keysym
        if keysym in [LEFT, RIGHT, UP, DOWN]:
            # 状态改变添加新的块
            onchange = self.model.attempt_move(keysym)
            self.draw()
            if onchange:
                import threading
                threading.Thread(target=self.new_tile).start()
            # 判断是否获胜或者淘汰
            if self.model.has_won():
                flag = tkinter.messagebox.askyesno('info',
                                                   WIN_MESSAGE)
                if flag:
                    self.model.new_game()
                    self.grid.redraw(self.model.get_tiles())
                else:
                    self.master.destroy()
            elif self.model.has_lost():
                flag = tkinter.messagebox.askyesno('info', LOSS_MESSAGE)
                if flag:
                    self.model.new_game()
                    self.grid.redraw(self.model.get_tiles())
                else:
                    self.master.destroy()

    # 添加新的瓷砖并且重新绘制
    def new_tile(self):
        time.sleep(NEW_TILE_DELAY / 1000)
        self.model.add_tile()
        for row, i in enumerate(self.model.add_f):
            for column, j in enumerate(i):
                position = self.grid._get_bbox((row, column))
                text_position = self.grid._get_midpoint((row, column))
                color = COLOURS.get(j)
                if j:
                    self.grid.create_rectangle(position[0], position[1], position[2], position[3],
                                               fill=color, outline=BACKGROUND_COLOUR)

                    self.grid.create_text(text_position[0], text_position[1], text=str(j), font=TILE_FONT,
                                          fill=FG_COLOURS.get(j))


def play_game(root):
    # Add a docstring and type hints to this function
    # Then write your code here
    game = Game(root)


if __name__ == '__main__':
    root = tk.Tk()
    play_game(root)
    root.mainloop()
