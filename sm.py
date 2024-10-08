import os  # 用于文件和路径操作的标准库模块
import random  # 用于生成随机数的标准库模块
import sys  # 用于访问系统参数和函数
import time  # 用于时间相关操作的模块
import pygame as pg  # Pygame库，处理游戏中的图形、声音和事件

# 设置游戏窗口的宽度和高度
WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ

# 切换当前工作目录为脚本所在目录，确保资源文件可以被找到
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 函数：检测物体是否超出窗口边界
def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True  # 初始化横向和纵向标志为True
    # 如果物体的左边缘超出左边界或右边缘超出右边界，则横向标志设为False
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    # 如果物体的顶部超出上边界或底部超出下边界，则纵向标志设为False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate  # 返回物体是否在横向和纵向内

# 类：鸟（游戏主角）
class Bird:
    # 定义按键与对应移动方向的字典
    delta = {
        pg.K_UP: (0, -5),    # 按上键，鸟向上移动
        pg.K_DOWN: (0, +5),  # 按下键，鸟向下移动
        pg.K_LEFT: (-5, 0),  # 按左键，鸟向左移动
        pg.K_RIGHT: (+5, 0), # 按右键，鸟向右移动
    }

    # 加载和处理鸟的图像
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)  # 加载并缩放鸟的图片
    img = pg.transform.flip(img0, True, False)  # 翻转图片，使鸟默认朝右

    # 为不同方向的移动设置对应的图片
    imgs = {
        (+5, 0): img,  # 向右移动时使用的图片
        (+5, -5): pg.transform.rotozoom(img, 45, 1.0),   # 向右上移动时的图片
        (0, -5): pg.transform.rotozoom(img, 90, 1.0),    # 向上移动时的图片
        (-5, -5): pg.transform.rotozoom(img, 135, 1.0),  # 向左上移动时的图片
        (-5, 0): pg.transform.rotozoom(img, 180, 1.0),   # 向左移动时的图片
        (-5, +5): pg.transform.rotozoom(img, -135, 1.0), # 向左下移动时的图片
        (0, +5): pg.transform.rotozoom(img, -90, 1.0),   # 向下移动时的图片
        (+5, +5): pg.transform.rotozoom(img, -45, 1.0),  # 向右下移动时的图片
    }

    # 构造函数，初始化鸟对象
    def __init__(self, xy: tuple[int, int]):
        self.img = __class__.imgs[(+5, 0)]  # 设置初始图片为鸟向右的图片
        self.rct: pg.Rect = self.img.get_rect()  # 获取图片的矩形区域
        self.rct.center = xy  # 设置鸟的初始位置

    # 更改鸟的图像，通常在游戏结束时调用
    def change_img(self, num: int, screen: pg.Surface):
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)  # 根据数字加载新图片并缩放
        screen.blit(self.img, self.rct)  # 将新图像绘制到屏幕上

    # 更新鸟的移动和图像
    def update(self, key_lst: list[bool], screen: pg.Surface):
        sum_mv = [0, 0]  # 移动量初始化为0
        for k, mv in __class__.delta.items():  # 遍历按键字典
            if key_lst[k]:  # 如果对应按键被按下
                sum_mv[0] += mv[0]  # 横向移动量
                sum_mv[1] += mv[1]  # 纵向移动量

        self.rct.move_ip(sum_mv)  # 根据移动量更新矩形的位置
        if check_bound(self.rct) != (True, True):  # 如果超出边界
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])  # 撤销移动

        if not (sum_mv[0] == 0 and sum_mv[1] == 0):  # 如果鸟移动了
            self.img = __class__.imgs[tuple(sum_mv)]  # 更新对应方向的图像
        screen.blit(self.img, self.rct)  # 将鸟绘制到屏幕上

# 类：炸弹
class Bomb:
    # 构造函数，初始化炸弹对象
    def __init__(self, color: tuple[int, int, int], rad: int):
        self.img = pg.Surface((2*rad, 2*rad))  # 创建炸弹的Surface对象
        pg.draw.circle(self.img, color, (rad, rad), rad)  # 画一个指定颜色的圆形炸弹
        self.img.set_colorkey((0, 0, 0))  # 设置透明色为黑色
        self.rct = self.img.get_rect()  # 获取炸弹的矩形区域
        # 将炸弹的位置随机设置在窗口内
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        # 设置初始速度
        self.vx, self.vy = +5, +5

    # 更新炸弹的位置
    def update(self, screen: pg.Surface):
        yoko, tate = check_bound(self.rct)  # 检查是否碰到窗口边界
        if not yoko:  # 如果撞到横向边界
            self.vx *= -1  # 反转横向速度
        if not tate:  # 如果撞到纵向边界
            self.vy *= -1  # 反转纵向速度
        self.rct.move_ip(self.vx, self.vy)  # 根据速度更新炸弹的位置
        screen.blit(self.img, self.rct)  # 将炸弹绘制到屏幕上

# 主程序
def main():
    pg.display.set_caption("逃げろ！こうかとん")  # 设置窗口标题
    screen = pg.display.set_mode((WIDTH, HEIGHT))  # 创建窗口
    bg_img = pg.image.load("fig/pg_bg.jpg")  # 加载背景图片
    bird = Bird((900, 400))  # 创建鸟对象，初始位置(900, 400)
    bomb = Bomb((255, 0, 0), 10)  # 创建红色炸弹，半径为10像素
    clock = pg.time.Clock()  # 创建时钟对象用于控制帧率
    key_lst = pg.key.get_pressed()  # 获取按键状态列表

    while True:  # 游戏主循环
        for event in pg.event.get():  # 遍历事件队列
            if event.type == pg.QUIT:  # 如果用户关闭窗口
                return  # 退出游戏

        screen.blit(bg_img, [0, 0])  # 绘制背景图
        bird.update(key_lst, screen)  # 更新鸟的位置并绘制
        bomb.update(screen)  # 更新炸弹的位置并绘制
        if bird.rct.colliderect(bomb.rct):  # 如果鸟和炸弹碰撞
            bird.change_img(8, screen)  # 改变鸟的图像
            pg.display.update()  # 更新屏幕
            time.sleep(1)  # 暂停1秒
            return  # 退出游戏

        pg.display.update()  # 更新屏幕
        clock.tick(60)  # 控制帧率为60FPS

if __name__ == "__main__":
    pg.init()  # 初始化Pygame
    main()  # 运行主程序
    pg.quit()  # 退出Pygame
    sys.exit()  # 退出程序
