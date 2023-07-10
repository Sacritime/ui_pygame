import pygame as pg
pg.init()


def is_valid_form_arg(form: tuple):
    if type(form) not in (str, tuple, list):
        raise TypeError(f"form argument must be str, tuple or list type, not {type(form)}\n"
                        f"You entered: form={str(form)}")
    elif type(form) in (tuple, list):
        if type(form[0]) is not str:
            raise TypeError(f"figure argument (form[0]) must be str type, not {type(form[0])}\n"
                            f"You entered: form={str(form)}")


def rect_form(form) -> tuple:
    if form == "rect" or form == ("rect",):
        angles = (-1, -1, -1, -1)
    else:
        if type(form[1]) not in (tuple, list):
            form = form[0], form[1:]
        angles = form[1]
        if len(angles) == 0:
            angles = (-1, -1, -1, -1)
        elif len(angles) == 1:
            angles = angles*4
        elif len(angles) == 2:
            angles = (angles[0], angles[1])*2

    if len(angles) == 3 or len(angles) > 4:
        raise IndexError(f"len of rect parametres must be 1, 2, or 4, not {len(angles)}.\n"
                         f"You entered: form={str(form)}")
    return ("rect", *angles)


def triangle_form(form) -> tuple:
    if form == "triangle" or form == ("triangle",):
        form = ("triangle", False, "up")
    elif len(form) == 2:
        if type(form[1]) not in (bool, str):
            raise TypeError(f"form[1] argument must be str or bool type, not {type(form[1])}\n"
                            f"You entered: form={str(form)}")
        if type(form[1]) is bool:
            form = (form[0], form[1], "up")
        else:
            form = (form[0], False, form[1])
    elif len(form) == 3:
        if type(form[1]) is not bool:
            form = (form[0], form[2], form[1])
    else:
        raise IndexError(f"len of triangle parameters must be 1 or 2, not {len(form[1:])}.\n"
                         f"You entered: form={str(form)}")
    if form[2] not in ("up", "down", "left", "right"):
        raise TypeError(f"side argument must be \"up\", \"down\", \"left\" or \"right\", not {form[2]}")

    return form


def circle_form(form) -> tuple:
    if form == "circle" or form == ("circle",):
        form = ("circle",)
    else:
        raise IndexError(f"there is no parameters for circle.\n"
                         f"You entered: form={str(form)}")
    return form


def custom_form(form) -> tuple:
    if form == "custom" or form == ("custom",):
        form = ("custom",)
    else:
        raise IndexError(f"there is no parameters for custom image.\n"
                         f"You entered: form={str(form)}")

    return form


def draw_triangle(side: str,
                  surf: pg.Surface,
                  color: str | tuple | pg.Color,
                  width: int, height: int):
    if side == "up":
        pg.draw.polygon(surf, color,
                        ((0, height), (width/2, 0), (width, height)))
    elif side == "down":
        pg.draw.polygon(surf, color,
                        ((0, 0), (width / 2, height), (width, 0)))
    elif side == "right":
        pg.draw.polygon(surf, color,
                        ((0, 0), (width, height/2), (0, height)))
    elif side == "left":
        pg.draw.polygon(surf, color,
                        ((width, 0), (0, height/2), (width, height)))


class Element:
    parent_surf: pg.Surface
    x: int = 0
    y: int = 0
    width: int = 100
    height: int = 100
    rect: pg.Rect
    surf: pg.Surface
    color: tuple | str | pg.Color = "gray100"
    form: tuple = "rect"
    degree: int = 0
    name: str = "None"
    data: dict = {}
    group: list | None = None

    def __init__(self, *_, **kwargs) -> None:
        for key, value in zip(kwargs.keys(), kwargs.values()):
            self.__setattr__(key, value)

        self.parent_surf = pg.display.get_surface()
        self.color_current = self.color

        form = kwargs.get("form", "rect")
        if form == ():
            form = "rect"

        is_valid_form_arg(form)

        if form == "rect" or form[0] == "rect":
            self.form = rect_form(form)

        elif form == "triangle" or form[0] == "triangle":
            self.form = triangle_form(form)
            if self.form[1]:
                self.image_current = 0
                self.images = ()

        elif form == "circle" or form[0] == "circle":
            self.form = circle_form(form)

        elif form == "custom" or form[0] == "custom":
            self.image = None
            self.form = custom_form(form)

        self.text = kwargs.get("text", None)
        if self.text is not None:
            font_path = kwargs.get("text_font", None)
            text_size = kwargs.get("text_size", "auto")
            text_color = kwargs.get("text_color", "blue1")
            try:
                pg.font.Font(font_path, 0)
                Font = pg.font.Font
            except FileNotFoundError:
                Font = pg.font.SysFont
            self.text_args = (Font, font_path, text_size, text_color)
            if type(text_size) is int:
                if text_size < 10:
                    text_size = 10
                font = Font(font_path, text_size)
                self.text_surfaces = [font.render(self.text, True, text_color)]
            self.text_current = 0

        self.rect = pg.Rect(self.x, self.y, self.width, self.height)
        self.update(update_surface=True)
        if self.group is not None:
            self.group.append(self)

    def __create_figure_surf(self):
        form = self.form
        if form[0] == "rect":
            pg.draw.rect(self.surf, self.color_current, (0, 0, self.width, self.height), 0, *form[1:])
        elif form[0] == "triangle":
            if form[1]:
                if len(self.images) < 1:
                    image = pg.image.load(f"media/images/triangle_{form[2]}.png").convert_alpha()
                    flag = image.get_width() * image.get_height() > self.width * self.height
                    if flag:
                        image = pg.transform.scale(image, (self.width, self.height))
                    self.images = (image.copy(),)
                    _w, _h = image.get_size()
                    for x in range(_w):
                        for y in range(_h):
                            if image.get_at((x, y)) == (0, 0, 0, 255):
                                self.images[0].set_at((x, y), self.color_current)
                    if not flag:
                        self.images = (pg.transform.scale(self.images[0], (self.width, self.height)))
                self.surf.blit(self.images[self.image_current], (0, 0))
            else:
                draw_triangle(form[2], self.surf, self.color_current, self.width, self.height)
        elif form[0] == "circle":
            pg.draw.ellipse(self.surf, self.color_current, (0, 0, self.width, self.height))
        elif form[0] == "custom":
            pass

    def __create_text_surf(self):
        Font, font_path, text_size, text_color = self.text_args
        if text_size == "auto":
            text_size = min(int(self.width * 0.5), int(self.height * 0.5))
            font = Font(font_path, text_size)

            text_surf = font.render(str(self.text), True, text_color)
            while ((text_surf.get_width() > self.width or
                    text_surf.get_height() > self.height) and text_size > 10):
                text_size = int(text_size * 0.7)
                font = Font(font_path, text_size)
                text_surf = font.render(str(self.text), True, text_color)
            self.text_surfaces = [text_surf]

        self.text_surf_xy = self.text_surfaces[self.text_current].get_rect(center=(self.width/2, self.height/2))
        self.surf.blit(self.text_surfaces[self.text_current], self.text_surf_xy)

    def __create_surf(self):
        self.__create_figure_surf()
        if self.text is not None:
            self.__create_text_surf()
        self.surf = pg.transform.rotate(self.surf, self.degree)

    def update(self,
               x: int | str | None = None,
               y: int | str | None = None,
               width: int | str | None = None,
               height: int | str | None = None,
               update_surface: bool = False):
        if x is not None:
            if type(x) in (int, float):
                self.x = x
            else:
                self.x += eval(x)
        if y is not None:
            if type(y) in (int, float):
                self.y = y
            else:
                self.y += eval(y)
        if width is not None:
            if type(width) in (int, float):
                self.width = int(width)
            else:
                self.width += int(eval(width))
        if height is not None:
            if type(height) in (int, float):
                self.height = int(height)
            else:
                self.height += int(eval(height))

        if self.width < 1:
            self.width = 1
        if self.height < 1:
            self.height = 1

        if (x, y, width, height) != (None, None, None, None):
            self.rect = pg.Rect(self.x, self.y, self.width, self.height)

        if (width, height) != (None, None) or update_surface:
            self.surf = pg.Surface((self.width, self.height), pg.SRCALPHA, 32)
            self.__create_surf()

    def draw(self):
        if self.form == "custom":
            self.surf.fill((0, 0, 0, 0))
            if self.image is not None:
                self.surf.blit(self.image, (0, 0))

        self.parent_surf.blit(self.surf, (self.x, self.y))


def upd(el: Element):
    if el.x > 600 - el.width:
        el.update(x=0, y="50")
    if el.y > 400 - el.height:
        el.update(x=0, y=0)
    if el.width > 100:
        el.update(x=str(el.width/2), width=30)
    if el.height > 100:
        el.update(height=30)
    el.update(width="5")


def upd_craze(craze: Element):
    if craze.width > 300 and flag:
        flag = False
    elif craze.width < 50 and not flag:
        flag = True
    if flag:
        craze.update(x="+2", width="+5")
    else:
        craze.update(x="-1", width="-7")
    if 100 < craze.width < 200:
        craze.update(y="+3", height="+2")
    else:
        craze.update(y="-2.5", height="-1")
    if craze.height > 100:
        craze.update(height=20)
    if craze.x > 600:
        craze.update(x=0)
    elif craze.x < 0:
        craze.update(x=500)
    if craze.y > 400:
        craze.update(y=0)
    elif craze.y < 0:
        craze.update(y=350)


if __name__ == "__main__":
    sc = pg.display.set_mode((600, 400))
    craze = Element(x=200, y=200, width=50, height=50, color="green", form=("rect", 10, 15, 20, 25), text="craze")
    elements = [
        Element(text="default args"),
        Element(x=0, y=110, width=150, height=150, color="red", form=("triangle", "down", True), text="element 1"),
        Element(x=150, y=0, width=200, height=100, color="white", form="circle", text="too big text", text_size=70),
        Element(x=400, y=0, form=("triangle",), text="rotated", degree=90),
        craze
        ]
    clock = pg.time.Clock()

    pg.display.update()
    flag = True
    while True:
        sc.fill((50, 50, 50))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        # you can do something like that, what in these functions
        # but it's very unoptimized and can't be that
        # because Element.update() assignment is to update (not to move, make animation and etc.)
        for el in elements:
            # # this
            # upd(el)
            el.draw()

        # # and this
        # upd_craze(craze)

        pg.display.update()
        clock.tick(100)
