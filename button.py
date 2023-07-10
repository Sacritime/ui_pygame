from typing import Literal
from element import Element

import pygame as pg
pg.init()


class Button(Element):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.color_hover = kwargs.get("color_hover", "gray75")
        self.color_pressed = kwargs.get("color_pressed", "gray50")

        if self.form[0] == "triangle" and self.form[1]:
            self.images += (self.images[0].copy(), self.images[0].copy())
            w, h = self.images[0].get_size()
            for x in range(w):
                for y in range(h):
                    if self.images[0].get_at((x, y)) == pg.Color(self.color):
                        self.images[1].set_at((x, y), self.color_hover)
                        self.images[2].set_at((x, y), self.color_pressed)

        if self.text is not None:
            self.text_color_hover = kwargs.get("text_color_hover", self.text_args[3])
            self.text_color_pressed = kwargs.get("text_color_pressed", self.text_args[3])

        self.func = kwargs.get("function", None)
        if self.func is not None:
            self.func_args = kwargs.get("function_args", ())
            self.func_is_multiple = kwargs.get("is_multiple", False)
        self.state = 0
        self.pressed = False

    def handle_events(self, event: list[pg.event.Event]):
        if event and type(event) is list:
            for ev in event:
                self.handle_events(ev)
            return

        elif self.pressed and self.func is not None:
            if not self.rect.collidepoint(pg.mouse.get_pos()) or not self.func_is_multiple:
                self.pressed = False
            self.func(self, *self.func_args)

        if not event or event.type not in (pg.MOUSEMOTION, pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
            return
        if self.rect.collidepoint(pg.mouse.get_pos()):
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.change(2)
                self.pressed = True
            elif event.type == pg.MOUSEBUTTONUP:
                self.change(1)
                self.pressed = False
            elif event.type == pg.MOUSEMOTION:
                if pg.mouse.get_pressed()[0]:
                    self.change(2)
                else:
                    self.change(1)
        else:
            self.change(0)

    def change(self, state: Literal[0, 1, 2] = 0):
        if self.state == state:
            return
        if state == 0:
            self.color_current = self.color
            if self.text is not None:
                self.text_color_current = self.text_args[3]
        elif state == 1:
            self.color_current = self.color_hover
            if self.text is not None:
                self.text_color_current = self.text_color_hover
        elif state == 2:
            self.color_current = self.color_pressed
            if self.text is not None:
                self.text_color_current = self.text_color_pressed
        if self.form[0] == "triangle" and self.form[1]:
            self.image_current = state
        self.state = state
        self.update(update_surface=True)


def up(_, block):
    block.update(y="-1")

def down(_, block):
    block.update(y="1")

def left(_, block):
    block.update(x="-1")

def right(_, block):
    block.update(x="1")

def big(button):
    button.update(x="-15", y="-15", width="30", height="30")


def game(*_):
    block = Button(x=250, y=150, form="circle", function=big, text="click!")
    buttons = [
        Button(x=50, y=250, width=50, height=50, text="up", form=("triangle", "up", True),
               color="blue", color_hover="green", color_pressed="red", text_color="black",
               function=up, function_args=(block,), is_multiple=True),
        Button(x=50, y=350, width=50, height=50, text="down", form=("triangle", "down", True),
               color="blue", color_hover="green", color_pressed="red", text_color="black",
               function=down, function_args=(block,), is_multiple=True),
        Button(x=0, y=300, width=50, height=50, text="left", form=("triangle", "left", True),
               color="blue", color_hover="green", color_pressed="red", text_color="black",
               function=left, function_args=(block,), is_multiple=True),
        Button(x=100, y=300, width=50, height=50, text="right", form=("triangle", "right", True),
               color="blue", color_hover="green", color_pressed="red", text_color="black",
               function=right, function_args=(block,), is_multiple=True),
        block
    ]
    clock = pg.time.Clock()

    pg.display.update()
    tick = 0
    flag = 1
    while True:
        sc.fill((50, 50, 50))
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                quit()
        if not tick:
            block.update(x=str(5*flag//1), y=str(5*flag//1), width=str(-10*flag//1), height=str(-10*flag//1))
        block.draw()
        for button in buttons:
            button.handle_events(events)
            button.draw()
        tick += 1
        if not tick % 60:
            flag += 0.1
            tick = 0
        if block.width < 50:
            game_over(sc)
        pg.display.update()
        clock.tick(120)

def game_over(sc):
    Element(parent_surf=sc, width=sc.get_width(), height=sc.get_height(), text="GAME OVER", text_color="white", color=(0, 0, 0, 150)).draw()
    butt = Button(x=200, y=300, width=200, height=50, text="Restart?", function=game)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            butt.handle_events(event)
        butt.draw()
        pg.display.flip()



if __name__ == "__main__":
    sc = pg.display.set_mode((600, 400), pg.SRCALPHA, 32)
    game()
