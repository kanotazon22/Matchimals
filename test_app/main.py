import os
import random
from kivy.config import Config
Config.set('graphics', 'maxfps', '60')
from collections import deque

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.image import Image as CoreImage
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window

from kivy.graphics import Color, Rectangle
from kivy.graphics.context_instructions import PopMatrix, PushMatrix, Translate

from kivy.animation import Animation
from kivy.properties import NumericProperty, StringProperty

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import FadeTransition, Screen, ScreenManager
from kivy.uix.video import Video
from kivy.uix.widget import Widget

from levels import LEVELS
from candy import *

GRID_ROWS = 10
GRID_COLS = 15

COLORS = ['red', 'green', 'blue', 'yellow', 'purple', 'white', 'pink', 'orange']
TYPES = ['bean', 'heart', 'candycorn', 'round', 'bomb', 'rainbow', 'cake', 'jelly']
ANIMAL_TYPES = [f"{t}_{c}" for t in TYPES for c in COLORS]

BASE_PATH = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_PATH, 'assets', 'images')
SOUND_DIR = os.path.join(BASE_PATH, 'assets', 'sound')
FONT_PATH = os.path.join("assets", "fonts", "candy.ttf")

class Account:
    def __init__(self, initial_candy=0):
        self.candy = initial_candy

    def add_candy(self, amount):
        self.candy += amount

    def spend_candy(self, amount):
        if amount <= self.candy:
            self.candy -= amount
            return True
        return False

    def get_candy(self):
        return self.candy
acc = Account(initial_candy=0)

class ExplosionEffect(Image):
    _cached_textures = []
    def __init__(self, pos, size, **kwargs):
        super().__init__(**kwargs)
        if not ExplosionEffect._cached_textures:
            for i in range(1, 6):
                path = os.path.join(ASSETS_DIR, f"explosionblue0{i}.png")
                tex = CoreImage(path).texture
                ExplosionEffect._cached_textures.append(tex)
        self.frames = ExplosionEffect._cached_textures
        self.frame_index = 0
        scale = 1.2
        self.size = (size[0] * scale, size[1] * scale)
        self.size_hint = (None, None)
        self.pos = (
            pos[0] - (self.size[0] - size[0]) / 2,
            pos[1] - (self.size[1] - size[1]) / 2
        )
        self.allow_stretch = True
        self.keep_ratio = True
        self.texture = self.frames[0]
        self.update_event = Clock.schedule_interval(self.update_frame, 0.07)

    def update_frame(self, dt):
        self.frame_index += 1
        if self.frame_index >= len(self.frames):
            self.update_event.cancel()
            if self.parent:
                self.parent.remove_widget(self)
            return
        self.texture = self.frames[self.frame_index]


graphics_quality = "Low"
sound_enabled = True
LOW_DIR = os.path.join(BASE_PATH, 'assets', 'low-quality')
HIGH_DIR = os.path.join(BASE_PATH, 'assets', 'high-quality')

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
from kivy.app import App
import os

class Tile(RelativeLayout):
    def __init__(self, row, col, animal_type, tile_size, **kwargs):
        super().__init__(**kwargs)

        # Chọn thư mục ảnh theo chất lượng
        if graphics_quality == "High":
            candy_dir = HIGH_DIR
        else:
            candy_dir = LOW_DIR

        self.sound_boom = SoundLoader.load(os.path.join(SOUND_DIR, "boom.ogg"))
        self.row = row
        self.col = col
        self.animal_type = animal_type

        self.has_ice = False
        if self.animal_type.startswith("ice_"):
        	self.has_ice = True
        	self.animal_type = self.animal_type[4:]
        	
        self.tile_size = tile_size
        self.selected = False
        # Xác định loại kẹo và màu
        if self.animal_type == "block":
            self.candy_type = "block"
            self.color = "gray"
        elif self.animal_type == "candycorn":
            self.candy_type = "candycorn"
            self.color = None
        elif self.animal_type == "bomb":
            self.candy_type = "bomb"
            self.color = None
        elif self.animal_type == "rainbow":
            self.candy_type = "rainbow"
            self.color = None
        elif self.animal_type == "cake":
            self.candy_type = "cake"
            self.color = None
        elif "_" in self.animal_type:
            self.candy_type, self.color = self.animal_type.split("_")
        else:
            self.candy_type = "unknown"
            self.color = "gray"

        self.size_hint = (None, None)
        self.size = (tile_size, tile_size)

        # Nền nút (Button để xử lý click)
        self.bg = Button(
            size=self.size,
            size_hint=(None, None),
            background_color=self.get_color(self.color),
            border=(0, 0, 0, 0),
            disabled=(self.candy_type == "block")
        )
        self.add_widget(self.bg)

        # Khung tile mặc định
        self.frame = Image(
            source=os.path.join(ASSETS_DIR, "tile.png"),
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.add_widget(self.frame)

        # Tạo biểu tượng kẹo
        if self.candy_type == "block":
            image_path = os.path.join(ASSETS_DIR, "block.png")
        elif self.candy_type == "cake":
            image_path = os.path.join(ASSETS_DIR, "cake.png")
        elif self.candy_type == "candycorn":
            image_path = os.path.join(candy_dir, "candycorn.png")
        elif self.candy_type == "bomb":
            image_path = os.path.join(candy_dir, "bomb.png")
        elif self.candy_type == "rainbow":
            image_path = os.path.join(candy_dir, "rainbow.png")
        else:
            image_file = self.color
            if self.candy_type == 'heart':
                image_file += '2'
            elif self.candy_type == 'round':
                image_file += '3'
            elif self.candy_type == 'jelly':
                image_file += '4'
            image_path = os.path.join(candy_dir, f"{image_file}.png")

        self.icon = Image(
            source=image_path,
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.8, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        self.add_widget(self.icon)
        # Nếu có băng, phủ lớp băng lên trên
        if self.has_ice:
        	self.ice_overlay = Image(
        		source=os.path.join(ASSETS_DIR, "ice.png"),
        		allow_stretch=True,
        		keep_ratio=True,
        		size_hint=(0.9, 0.9),
        		pos_hint={"center_x": 0.5, "center_y": 0.5}
        	)
        	self.add_widget(self.ice_overlay)

        if self.candy_type != "block":
            self.bg.bind(on_release=self.on_pressed)

    def get_color(self, color_name):
        return {
            'red': (1, 0, 0, 1),
            'green': (0, 1, 0, 1),
            'blue': (0, 0, 1, 1),
            'yellow': (1, 1, 0, 1),
            'purple': (0.6, 0, 0.6, 1),
            'white': (0.95, 0.98, 1, 1),
            'pink': (1, 0.4, 0.7, 1),
            'orange': (1, 0.5, 0, 1),
            'gray': (0.4, 0.4, 0.4, 1),
            None: (1, 1, 1, 1),
        }[color_name]

    def on_pressed(self, *args):
        self.parent.on_tile_pressed(self)

    def select(self):
        self.selected = True
        self.bg.background_color = (1, 1, 1, 1)
        self.frame.source = os.path.join(ASSETS_DIR, "tile2.png")
        self.frame.reload()

    def unselect(self):
        self.selected = False
        self.bg.background_color = self.get_color(self.color)
        self.frame.source = os.path.join(ASSETS_DIR, "tile.png")
        self.frame.reload()

    def hide(self, play_sound=True):
        if getattr(self, 'has_ice', False):
        	self.has_ice = False
        	if hasattr(self, 'ice_overlay'):
        		self.remove_widget(self.ice_overlay)
        self.disabled = True
        self.bg.disabled = True
        self.icon.opacity = 0
        self.sound_boom.play()
        if graphics_quality == "High":
        	self.spawn_explosion()
        self.on_touch_down = lambda touch: False
        self.frame.source = os.path.join(ASSETS_DIR, "tile.png")
        self.frame.reload()
        acc.add_candy(1)
        App.get_running_app().root.get_screen('game').package.update_candy(acc.get_candy())

    def spawn_explosion(self, flight=False, target_pos=None):
        app = App.get_running_app()
        if not (app and app.root):
            return
        container = app.root.get_screen('game').children[0]

        if flight and target_pos:
            flyer = Image(
                texture=self.icon.texture,
                size=self.icon.size,
                size_hint=(None, None),
                pos=self.to_window(*self.pos),
                allow_stretch=True, keep_ratio=True
            )
            container.add_widget(flyer)
            anim = Animation(pos=target_pos, duration=0.2, t='out_quad')
            # khi bay xong thì xóa flyer
            anim.bind(on_complete=lambda a, w: w.parent and w.parent.remove_widget(w))
            anim.start(flyer)
        else:
            # trường hợp High-quality tự nổ tại chỗ (nếu bạn vẫn muốn)
            pos = self.to_window(*self.pos)
            effect = ExplosionEffect(pos=pos, size=(self.tile_size, self.tile_size))
            container.add_widget(effect)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if not self.disabled and self.candy_type != "block" and not self.has_ice:
                self.bg.dispatch('on_release')
            return True
        return super().on_touch_down(touch)


class AnimalGridUI(GridLayout):
    def __init__(self, logic, rows=GRID_ROWS, cols=GRID_COLS, distribution=None, **kwargs):
        super().__init__(**kwargs)
        self.sound_pop = SoundLoader.load(os.path.join(SOUND_DIR, "pop.ogg"))
        self.rows = rows
        self.cols = cols
        self.spacing = 2
        self.logic = logic
        self.special_manager = SpecialCandyManager(self.logic, self)

        # Tính kích thước tile
        ref_rows, ref_cols = 10, 15
        max_tile_width = Window.width / ref_cols
        max_tile_height = Window.height / ref_rows
        tile_size_width = Window.width / cols
        tile_size_height = Window.height / rows
        self.tile_size = min(max_tile_width, max_tile_height, tile_size_width, tile_size_height)

        self.size_hint = (None, None)
        self.size = (self.tile_size * cols, self.tile_size * rows)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        self._generate_valid_layout(distribution)
        self.input_locked = False

    def _generate_valid_layout(self, distribution):
        max_attempts = 20
        for attempt in range(max_attempts):
            self.clear_widgets()
            self.logic.tiles = [[None for _ in range(self.cols)] for _ in range(self.rows)]

            tile_list = []
            if distribution:
                for animal, count in distribution.items():
                    tile_list += [animal] * count
                random.shuffle(tile_list)

            tiles_to_reveal = []

            for row in range(self.rows):
                for col in range(self.cols):
                    coord = (row, col)
                    if self.logic.level_shapes and coord in self.logic.level_shapes:
                        animal = 'block'
                    else:
                        if tile_list:
                            animal = tile_list.pop()
                        else:
                            animal = random.choice([t for t in ANIMAL_TYPES if not t.startswith('block')])

                    tile = Tile(row, col, animal, self.tile_size)
                    self.logic.tiles[row][col] = tile

                    tile.opacity = 0
                    self.add_widget(tile)
                    tiles_to_reveal.append(tile)

            if self.logic.is_solvable():
                break
        else:
            print("⚠ Không thể tạo bản đồ hợp lệ sau nhiều lần thử.")

        random.shuffle(tiles_to_reveal)
        for i, tile in enumerate(tiles_to_reveal):
            delay = i * 0.03
            def reveal_tile(dt, tile=tile, index=i):
                if self.sound_pop and sound_enabled and index % 4 == 0:
                    self.sound_pop.play()
                Animation(opacity=1, duration=0.4, t='out_quad').start(tile)
            Clock.schedule_once(reveal_tile, delay)
            
    def check_melt_ice_around(self, row, col):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Trên, dưới, trái, phải
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbor = self.logic.tiles[nr][nc]
                if neighbor and neighbor.has_ice:
                    if self.check_ice_should_melt(nr, nc):
                        neighbor.has_ice = False
                        if hasattr(neighbor, 'ice_overlay'):
                            neighbor.remove_widget(neighbor.ice_overlay)
                            if graphics_quality == "High":
                            	app = App.get_running_app()
                            	if app and app.root:
                            		pos = neighbor.to_window(*neighbor.pos)
                            		effect = ExplosionEffect(pos=pos, size=(neighbor.tile_size, neighbor.tile_size))
                            		app.root.get_screen('game').children[0].add_widget(effect)
                            
    def check_ice_should_melt(self, row, col):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                tile = self.logic.tiles[nr][nc]
                if tile is None or tile.disabled or tile.opacity == 0:
                    return True
        return False
            
    def on_tile_pressed(self, tile):
        if tile.disabled or self.input_locked:
            return

        if self.sound_pop and sound_enabled and tile.candy_type not in ['bomb', 'candycorn']:
            self.sound_pop.play()

        logic = self.logic
        if logic.first_selected is None:
            logic.first_selected = tile
            tile.select()
        else:
            if tile == logic.first_selected:
                tile.unselect()
                logic.first_selected = None
                return

            if (tile.color == logic.first_selected.color and tile.candy_type == logic.first_selected.candy_type):
                if logic.is_connectable(logic.first_selected, tile):
                    self.input_locked = True

                    if self.special_manager.handle_special(logic.first_selected, tile):
                        screen = App.get_running_app().root.get_screen('game')
                        logic.first_selected = None
                        self.input_locked = False
                        return
                        
                    r1, c1 = logic.first_selected.row, logic.first_selected.col
                    r2, c2 = tile.row, tile.col
                    dist = max(abs(r1 - r2), abs(c1 - c2))

                    # tính mid point (tọa độ giữa hai viên)    
                    x1, y1 = logic.first_selected.to_window(*logic.first_selected.pos)    
                    x2, y2 = tile.to_window(*tile.pos)    
                    mid_pos = ((x1 + x2) / 2, (y1 + y2) / 2)    

                    # xác định xem có bay hay không
                    if dist == 1:
                        flight1 = flight2 = True
                    elif dist <= 2:
                        flight1 = flight2 = (random.random() < 0.5)
                    else:
                        flight1 = flight2 = False

                    # spawn 2 flyers (hoặc nổ tại chỗ)
                    logic.first_selected.spawn_explosion(flight=flight1, target_pos=mid_pos if flight1 else None)    
                    tile.spawn_explosion(         flight=flight2, target_pos=mid_pos if flight2 else None)    

                    # nếu có ít nhất 1 viên bay, tạo nổ giữa sau 0.2s
                    if flight1 or flight2:
                        app = App.get_running_app()
                        Clock.schedule_once(lambda dt:     
                            app.root.get_screen('game').children[0].add_widget(    
                                ExplosionEffect(pos=mid_pos, size=(self.tile_size, self.tile_size))    
                            )    
                        , 0.2)

                    # rồi mới xóa tile thật, cập nhật state    
                    logic.tiles[r1][c1] = None    
                    logic.tiles[r2][c2] = None    
                    logic.first_selected.hide(play_sound=False)    
                    tile.hide(play_sound=False)    

                    self.check_melt_ice_around(r1, c1)    
                    self.check_melt_ice_around(r2, c2)    
                    screen = App.get_running_app().root.get_screen('game')    
                    screen.matched_tiles += 2    
                    percent = 100 * screen.matched_tiles / screen.total_tiles    
                    screen.progress_bar.value = percent    
                    screen.check_win()    
                    logic.first_selected = None    
                    self.input_locked = False    
                    return
                else:
                    logic.first_selected.unselect()
                    logic.first_selected = tile
                    tile.select()
                    return
            else:
                logic.first_selected.unselect()
                logic.first_selected = tile
                tile.select()
                return

class AnimalGrid:
    def __init__(self, rows=GRID_ROWS, cols=GRID_COLS):
        self.rows = rows
        self.cols = cols
        self.tiles = [[None for _ in range(cols)] for _ in range(rows)]
        self.first_selected = None

    def is_empty(self, row, col):
        tile = self.tiles[row][col]
        if tile is None:
            return True
        return not (tile.candy_type == "block" or not tile.disabled)

    def is_clear_row(self, row, col1, col2):
        for col in range(min(col1, col2) + 1, max(col1, col2)):
            if not self.is_empty(row, col):
                return False
        return True

    def is_clear_col(self, col, row1, row2):
        for row in range(min(row1, row2) + 1, max(row1, row2)):
            if not self.is_empty(row, col):
                return False
        return True
        
    def is_solvable(self):
        tiles = [tile for row in self.tiles for tile in row if tile and not tile.disabled and tile.candy_type != 'block']
        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                t1 = tiles[i]
                t2 = tiles[j]
                if t1.animal_type == t2.animal_type and self.is_connectable(t1, t2):
                    return True
        return False

    def is_connectable(self, t1, t2):
        if t1 is None or t2 is None or t1 == t2:
            return False

        r1, c1 = t1.row, t1.col
        r2, c2 = t2.row, t2.col

        if (r1, c1) == (r2, c2):
            return False

        # 1. Cùng hàng hoặc cùng cột
        if r1 == r2 and self.is_clear_row(r1, c1, c2):
            return True
        if c1 == c2 and self.is_clear_col(c1, r1, r2):
            return True

        # 2. Góc chữ L
        if self.is_empty(r1, c2) and self.is_clear_row(r1, c1, c2) and self.is_clear_col(c2, r1, r2):
            return True
        if self.is_empty(r2, c1) and self.is_clear_col(c1, r1, r2) and self.is_clear_row(r2, c1, c2):
            return True

        # 3. Góc 2 lần (dạng U hoặc Z)
        for mid in range(self.rows):
            if self.is_empty(mid, c1) and self.is_empty(mid, c2):
                if self.is_clear_col(c1, r1, mid) and self.is_clear_row(mid, c1, c2) and self.is_clear_col(c2, r2, mid):
                    return True

        for mid in range(self.cols):
            if self.is_empty(r1, mid) and self.is_empty(r2, mid):
                if self.is_clear_row(r1, c1, mid) and self.is_clear_col(mid, r1, r2) and self.is_clear_row(r2, mid, c2):
                    return True

        # 4. BFS tối đa 2 lần rẽ
        visited = [[float('inf')] * self.cols for _ in range(self.rows)]
        queue = deque()
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            nr, nc = r1 + dr, c1 + dc
            while 0 <= nr < self.rows and 0 <= nc < self.cols and self.is_empty(nr, nc):
                visited[nr][nc] = 0
                queue.append((nr, nc, dr, dc, 0))
                nr += dr
                nc += dc

        while queue:
            r, c, dr, dc, turns = queue.popleft()
            if (r, c) == (r2, c2):
                return True
            if turns >= 2:
                continue
            for ndr, ndc in directions:
                if (ndr, ndc) == (-dr, -dc):
                    continue  # không quay đầu
                nr, nc = r + ndr, c + ndc
                n_turns = turns + (0 if (ndr, ndc) == (dr, dc) else 1)
                while 0 <= nr < self.rows and 0 <= nc < self.cols and self.is_empty(nr, nc):
                    if visited[nr][nc] > n_turns:
                        visited[nr][nc] = n_turns
                        queue.append((nr, nc, ndr, ndc, n_turns))
                    nr += ndr
                    nc += ndc

        return False


class ImageButton(ButtonBehavior, Image):
    pass

class SettingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        self.sound_click = SoundLoader.load(os.path.join(SOUND_DIR, "pop.ogg"))

        # Background
        bg = Image(
            source=os.path.join(ASSETS_DIR, "setting_bg.png"),
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        layout.add_widget(bg)

        # === Container căn giữa cho nút ===
        button_container = FloatLayout(size_hint=(1, 1))

        # === Quality Layout ===
        quality_layout = BoxLayout(orientation='vertical', spacing=10,
                                   size_hint=(None, None), size=(150, 190),
                                   pos_hint={'center_x': 0.35, 'center_y': 0.4})
        self.quality_btn = ImageButton(
            source=os.path.join(ASSETS_DIR, "low.png"),
            size_hint=(None, None),
            size=(150, 150),
            allow_stretch=True,
            keep_ratio=True
        )
        self.quality_btn.bind(on_release=self.toggle_quality)
        self.quality_label = Label(
            text="Low Quality",
            font_name=FONT_PATH,
            font_size=32,
            color=(1, 1, 1, 1),
            outline_color=(0, 0, 0, 1),
            outline_width=1,
            size_hint=(1, None),
            height=40
        )
        quality_layout.add_widget(self.quality_btn)
        quality_layout.add_widget(self.quality_label)

        # === Sound Layout ===
        sound_layout = BoxLayout(orientation='vertical', spacing=10,
                                 size_hint=(None, None), size=(150, 190),
                                 pos_hint={'center_x': 0.65, 'center_y': 0.4})
        self.sound_btn = ImageButton(
            source=os.path.join(ASSETS_DIR, "sound-on.png") if sound_enabled else os.path.join(ASSETS_DIR, "sound-off.png"),
            size_hint=(None, None),
            size=(150, 150),
            allow_stretch=True,
            keep_ratio=True
        )
        self.sound_btn.bind(on_release=self.toggle_sound)
        self.sound_label = Label(
            text="Sound On" if sound_enabled else "Sound Off",
            font_name=FONT_PATH,
            font_size=32,
            color=(1, 1, 1, 1),
            outline_color=(0, 0, 0, 1),
            outline_width=1,
            size_hint=(1, None),
            height=40
        )
        sound_layout.add_widget(self.sound_btn)
        sound_layout.add_widget(self.sound_label)

        button_container.add_widget(quality_layout)
        button_container.add_widget(sound_layout)
        layout.add_widget(button_container)

        # Exit button
        exit_btn = ImageButton(
            source=os.path.join(ASSETS_DIR, "exit.png"),
            size_hint=(0.1, 0.1),

            pos_hint={'x': 0.01, 'top': 0.98},
            allow_stretch=True,
            keep_ratio=True
        )
        exit_btn.bind(on_release=self.exit_setting)
        layout.add_widget(exit_btn)

        self.add_widget(layout)

    def toggle_quality(self, *args):
        global graphics_quality
        if self.sound_click and sound_enabled:
            self.sound_click.play()

        if graphics_quality == "Low":
            graphics_quality = "High"
            self.quality_btn.source = os.path.join(ASSETS_DIR, "high.png")
            self.quality_label.text = "High Quality"
        else:
            graphics_quality = "Low"
            self.quality_btn.source = os.path.join(ASSETS_DIR, "low.png")
            self.quality_label.text = "Low Quality"

        print(f"Graphics quality set to {graphics_quality}")

    def toggle_sound(self, *args):
        global sound_enabled
        sound_enabled = not sound_enabled
        self.sound_btn.source = os.path.join(ASSETS_DIR, "sound-on.png") if sound_enabled else os.path.join(ASSETS_DIR, "sound-off.png")
        self.sound_label.text = "Sound On" if sound_enabled else "Sound Off"
        print(f"Sound {'enabled' if sound_enabled else 'disabled'}")
        App.get_running_app().update_music_state()

    def exit_setting(self, *args):
        if self.sound_click and sound_enabled:
            self.sound_click.play()
        self.manager.current = 'start'
        

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        self.sound_click = SoundLoader.load(os.path.join(SOUND_DIR, "pop.ogg"))

        bg = Image(
            source=os.path.join(ASSETS_DIR, "start_background.png"),
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        layout.add_widget(bg)

        # Nút "Play"
        start_btn = ImageButton(
            source=os.path.join(ASSETS_DIR, "play.png"),
            size_hint=(0.15, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.25},
            allow_stretch=True,
            keep_ratio=True
        )
        start_btn.bind(on_release=self.start_game)
        layout.add_widget(start_btn)

        # Nút "Settings" – bên phải nút Play, nhỏ hơn 1 chút
        settings_btn = ImageButton(
            source=os.path.join(ASSETS_DIR, "setting.png"),
            size_hint=(0.12, 0.12),  # nhỏ hơn start_btn
            pos_hint={'center_x': 0.63, 'center_y': 0.25},  # lệch phải một chút
            allow_stretch=True,
            keep_ratio=True
        )
        settings_btn.bind(on_release=self.open_settings)
        layout.add_widget(settings_btn)

        # Nút "Exit"
        exit_btn = ImageButton(
            source=os.path.join(ASSETS_DIR, "exit.png"),
            size_hint=(0.1, 0.1),
            pos_hint={'x': 0.01, 'top': 0.98},  # góc trên trái
            allow_stretch=True,
            keep_ratio=True
        )
        exit_btn.bind(on_release=self.exit_app)
        layout.add_widget(exit_btn)

        self.add_widget(layout)

    def start_game(self, *args):
        self.manager.current = 'level_select'
        if sound_enabled and self.sound_click:
            self.sound_click.play()

    def open_settings(self, *args):
        if sound_enabled and self.sound_click:
            self.sound_click.play()
        self.manager.current = 'setting'

    def exit_app(self, *args):
        Window.close()


class OutlinedLabel(Label):
    def __init__(self, outline_color=(0, 0, 0, 1), outline_width=2, **kwargs):
        self.outline_color = outline_color
        self.outline_width = outline_width
        super().__init__(**kwargs)
        self.bind(pos=self.redraw, size=self.redraw, text=self.redraw, font_size=self.redraw)

    def redraw(self, *args):
        self.canvas.before.clear()
        label = CoreLabel(text=self.text, font_size=self.font_size, font_name=self.font_name, bold=self.bold)
        label.refresh()
        texture = label.texture
        tex_size = list(texture.size)

        offset = self.outline_width
        positions = [
            (-offset, -offset), (-offset, 0), (-offset, offset),
            (0, -offset),               (0, offset),
            (offset, -offset), (offset, 0), (offset, offset)
        ]

        with self.canvas.before:
            PushMatrix()
            Translate(*self.pos)

            for dx, dy in positions:
                Color(*self.outline_color)
                Rectangle(texture=texture, size=tex_size, pos=(dx, dy))

            PopMatrix()

        self.texture = texture
        self.texture_size = tex_size


class LevelSelectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page_index = 0
        self.levels_per_page = 5
        self.max_level = 100
        self.sound_click = SoundLoader.load(os.path.join(SOUND_DIR, "click.ogg"))

        Clock.schedule_once(self.build_ui, 0.1)
        Window.bind(on_resize=self.on_resize)

    def on_resize(self, *args):
        Clock.unschedule(self.build_ui)
        Clock.schedule_once(self.build_ui, 0.05)

    def build_ui(self, *args):
        self.clear_widgets()
        layout = FloatLayout()

        win_w, win_h = Window.size

        bg = Image(
            source=os.path.join(ASSETS_DIR, "select_level.png"),
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        layout.add_widget(bg)

        label_bg = Image(
            source=os.path.join(ASSETS_DIR, "label.png"),
            size_hint=(None, None),
            size=(440, 110),
            pos=(win_w / 2 - 220, win_h - 110)
        )
        layout.add_widget(label_bg)

        start_level = self.page_index * self.levels_per_page + 1
        end_level = min(start_level + self.levels_per_page - 1, self.max_level)

        label_text = Label(
            text=f"Màn {start_level}–{end_level}",
            font_size=40,
            bold=True,
            font_name=FONT_PATH,
            color=(1, 1, 1, 1),
            outline_color=(0, 0, 0, 1),
            outline_width=1,
            size_hint=(None, None),
            size=(440, 110),
            pos=(win_w / 2 - 220, win_h - 110),
            halign='center',
            valign='middle'
        )
        label_text.bind(size=self._update_label_text)
        layout.add_widget(label_text)

        container = FloatLayout(size_hint=(1, 1))
        spacing_x = win_w // (self.levels_per_page + 1)
        base_y = win_h * 0.5
        offset_y = win_h * 0.1

        for i, level_num in enumerate(range(start_level - 1, end_level)):
            btn_x = spacing_x * (i + 1) - 70
            btn_y = base_y + (offset_y if i % 2 == 0 else -offset_y)

            btn_container = RelativeLayout(
                size_hint=(None, None),
                size=(140, 140),
                pos=(btn_x, btn_y)
            )

            if level_num < len(LEVELS):
                image_path = "level_button.png"
                can_click = True
            else:
                image_path = "level_button2.png"
                can_click = False

            btn = ImageButton(
                source=os.path.join(ASSETS_DIR, image_path),
                size_hint=(None, None),
                size=(140, 140),
                pos=(0, 0)
            )

            if can_click:
                btn.level_index = level_num
                btn.bind(on_release=self.select_level)

            label = Label(
                text=str(level_num + 1),
                font_size=52,
                bold=True,
                font_name=FONT_PATH,
                color=(1, 1, 1, 1),
                outline_color=(0, 0, 0, 1),
                outline_width=1,
                size_hint=(None, None),
                size=(140, 140),
                pos=(0, 0),
                halign='center',
                valign='middle'
            )
            label.bind(size=self._update_label_text)

            btn_container.add_widget(btn)
            btn_container.add_widget(label)
            container.add_widget(btn_container)

        layout.add_widget(container)

        exit_btn = ImageButton(
            source=os.path.join(ASSETS_DIR, "exit.png"),
            size_hint=(None, None),
            size=(100, 100),
            pos=(20, win_h - 120),
            allow_stretch=True,
            keep_ratio=True
        )
        exit_btn.bind(on_release=self.exit_to_start)
        layout.add_widget(exit_btn)

        if self.page_index > 0:
            arrow_left = ImageButton(
                source=os.path.join(ASSETS_DIR, "arrow1.png"),
                size_hint=(None, None),
                size=(120, 120),
                pos=(10, win_h / 2 - 60)
            )
            arrow_left.bind(on_release=self.prev_page)
            layout.add_widget(arrow_left)

        if end_level < self.max_level:
            arrow_right = ImageButton(
                source=os.path.join(ASSETS_DIR, "arrow2.png"),
                size_hint=(None, None),
                size=(120, 120),
                pos=(win_w - 130, win_h / 2 - 60)
            )
            arrow_right.bind(on_release=self.next_page)
            layout.add_widget(arrow_right)

        layout.opacity = 0
        self.add_widget(layout)
        Animation(opacity=1, duration=0.2).start(layout)

    def _update_label_text(self, instance, value):
        instance.text_size = value

    def select_level(self, instance):
        level_index = instance.level_index
        self.manager.get_screen('game').load_level(level_index)
        self.manager.current = 'game'
        if sound_enabled and self.sound_click:
            self.sound_click.play()

    def _animate_page_change(self, new_page_index):
        if sound_enabled and self.sound_click:
            self.sound_click.play()

        if len(self.children) == 0:
            self.page_index = new_page_index
            self.build_ui()
            return

        current_layout = self.children[0]
        anim_out = Animation(opacity=0, duration=0.2)

        def on_fade_out_complete(animation, widget):
            self.remove_widget(current_layout)
            self.page_index = new_page_index
            self.build_ui()
        anim_out.bind(on_complete=on_fade_out_complete)
        anim_out.start(current_layout)

    def prev_page(self, instance):
        if self.page_index > 0:
            self._animate_page_change(self.page_index - 1)

    def next_page(self, instance):
        if (self.page_index + 1) * self.levels_per_page < self.max_level:
            self._animate_page_change(self.page_index + 1)

    def exit_to_start(self, *args):
        if sound_enabled and self.sound_click:
            self.sound_click.play()
        self.manager.current = 'start'


class ImageProgressBar(Widget):
    value = NumericProperty(0)
    max = NumericProperty(100)
    background_image = StringProperty()
    fill_image = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bg_tex = CoreImage(self.background_image).texture
        self.fill_tex = CoreImage(self.fill_image).texture

        with self.canvas:
            self.bg_rect = Rectangle(texture=self.bg_tex, pos=self.pos, size=self.size)
            self.fill_rect = Rectangle(texture=self.fill_tex, pos=self.pos, size=(0, self.height))

        self.label = Label(
            text="0%",
            font_size=36,
            font_name=FONT_PATH,
            color=(1, 1, 1, 1),
            outline_color=(0, 0, 0, 1),
            outline_width=1,
            halign='center',
            valign='middle',
            bold=True,
            size_hint=(None, None)
        )
        self.label.bind(size=self._update_label_text_size)
        self.add_widget(self.label)

        self.bind(pos=self._update_all, size=self._update_all, value=self._on_value_change)
        Clock.schedule_once(self._update_all, 0)

    def _update_label_text_size(self, instance, value):
        instance.text_size = value

    def _update_all(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self._update_fill(animate=False)

        self.label.size = self.size
        self.label.text_size = self.size
        self.label.pos = self.pos

    def _on_value_change(self, *args):
        self._update_fill(animate=True)

    def _update_fill(self, animate=True):
        percent = min(1, max(0, self.value / float(self.max)))
        clip_height = self.height * percent
        new_pos = (self.x, self.y)
        new_size = (self.width, clip_height)

        tex = self.fill_tex
        tex_v_start = 0
        tex_v_end = percent
        tex_coords = [
            0, tex_v_start,
            1, tex_v_start,
            1, tex_v_end,
            0, tex_v_end
        ]

        if animate:
            Animation(size=new_size, pos=new_pos, d=0.2).start(self.fill_rect)
        else:
            self.fill_rect.size = new_size
            self.fill_rect.pos = new_pos

        self.fill_rect.texture = tex
        self.fill_rect.tex_coords = tex.get_region(0, 0, tex.width, int(tex.height * percent)).tex_coords

        self.label.text = f"{int(percent * 100)}%"


from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty
from kivy.core.image import Image as CoreImage
from kivy.graphics import Rectangle
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.animation import Animation


class TimeBar(Widget):
    remaining = NumericProperty(0)
    total = NumericProperty(30)
    background_image = StringProperty()
    fill_image = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bg_tex = CoreImage(self.background_image).texture
        self.fill_tex = CoreImage(self.fill_image).texture

        with self.canvas:
            self.bg_rect = Rectangle(texture=self.bg_tex, pos=self.pos, size=self.size)
            self.fill_rect = Rectangle(texture=self.fill_tex, pos=self.pos, size=self.size)

        self.label = Label(
            text=f"{int(self.remaining)}s",
            font_size=36,
            font_name=FONT_PATH,
            color=(1, 1, 1, 1),
            outline_color=(0, 0, 0, 1),
            outline_width=1,
            halign='center',
            valign='middle',
            bold=True,
            size_hint=(None, None)
        )
        self.label.bind(size=self._update_label_text_size)
        self.add_widget(self.label)

        self.bind(pos=self._update_all, size=self._update_all, remaining=self._on_remaining_change)
        Clock.schedule_once(self._update_all, 0)

    def _update_label_text_size(self, instance, value):
        instance.text_size = value

    def _update_all(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

        self.label.size = self.size
        self.label.text_size = self.size
        self.label.pos = self.pos

        self._update_fill(animate=False)

    def _on_remaining_change(self, *args):
        self._update_fill(animate=True)

    def _update_fill(self, animate=True):
        percent = max(0.0, min(1.0, self.remaining / float(self.total)))

        # Resize fill_rect từ dưới lên
        bar_height = self.height * percent
        self.fill_rect.size = (self.width, bar_height)
        self.fill_rect.pos = (self.x, self.y)  # Giữ cố định ở đáy

        # Cắt texture từ dưới lên
        tex = self.fill_tex
        tex_crop_h = int(tex.height * percent)
        v_start = 0.0
        v_end = tex_crop_h / tex.height

        self.fill_rect.texture = tex
        self.fill_rect.tex_coords = [
            0, v_start,
            1, v_start,
            1, v_end,
            0, v_end
        ]

        self.label.text = f"{int(self.remaining)}s"

class WinEffect:
    def __init__(self, layout, grid_ui, font_path, assets_dir):
        self.layout = layout
        self.grid_ui = grid_ui
        self.font_path = font_path
        self.assets_dir = assets_dir

        self.win_sounds = []
        for _ in range(3):
            s = SoundLoader.load(os.path.join(self.assets_dir, "win.ogg"))
            if s:
                self.win_sounds.append(s)
        self.sound_index = 0

    def play(self):
        def show_effect(dt):
            if self.grid_ui:
                self.grid_ui.opacity = 1
                anim = Animation(opacity=0, duration=0.4)
                anim.bind(on_complete=lambda *_: setattr(self.grid_ui, "opacity", 0))
                anim.start(self.grid_ui)

            # Random hiển thị trophy
            chosen = random.choice(["super_candy", "handmade_ballons"])
            is_ballons = (chosen == "handmade_ballons")

            trophy = Image(
                source=os.path.join(self.assets_dir, f"{chosen}.png"),
                size_hint=(0.03, 0.03),
                opacity=1,
                pos_hint={"center_x": 0.5, "center_y": 0.6}
            )

            # Danh sách hũ kẹo và vị trí từng cái
            jars = [
                {
                    "source": "candies.png",   # Hũ 1
                    "drop": "red.png",
                    "pos_x": 0.70,
                    "pos_y": 0.18
                },
                {
                    "source": "candies2.png",  # Hũ 2
                    "drop": "pink.png",
                    "pos_x": 0.82,
                    "pos_y": 0.16
                },
                {
                    "source": "candies3.png",  # Hũ 3
                    "drop": "blue.png",
                    "pos_x": 0.92,
                    "pos_y": 0.20
                }
            ]

            def start_idle_animation():
                idle_anim = (
                    Animation(size_hint=(0.42, 0.42), duration=0.8) +
                    Animation(size_hint=(0.4, 0.4), duration=0.8)
                )
                idle_anim.repeat = True
                idle_anim.start(trophy)

            def spawn_random_candies():
                for _ in range(random.randint(6, 8)):
                    source = "random_heart.png" if is_ballons else "random_candy.png"
                    candy = Image(
                        source=os.path.join(self.assets_dir, source),
                        size_hint=(0.05, 0.05),
                        opacity=1,
                        pos_hint={
                            "center_x": 0.5 + random.uniform(-0.1, 0.1),
                            "center_y": 0.6 + random.uniform(-0.05, 0.05)
                        }
                    )
                    self.layout.add_widget(candy)

                    end_y = candy.pos_hint["center_y"] - random.uniform(0.2, 0.3)
                    anim = Animation(
                        pos_hint={
                            "center_x": candy.pos_hint["center_x"],
                            "center_y": end_y
                        },
                        opacity=0,
                        duration=0.8
                    )
                    anim.bind(on_complete=lambda *_: self.layout.remove_widget(candy))
                    anim.start(candy)

            def spawn_from_jar(jar_widget, drop_image):
                for _ in range(random.randint(4, 6)):
                    drop = Image(
                        source=os.path.join(self.assets_dir, drop_image),
                        size_hint=(0.04, 0.04),
                        opacity=1,
                        pos_hint={
                            "center_x": jar_widget.pos_hint["center_x"] + random.uniform(-0.02, 0.02),
                            "center_y": jar_widget.pos_hint["center_y"] + random.uniform(-0.01, 0.02)
                        }
                    )
                    self.layout.add_widget(drop)

                    end_y = drop.pos_hint["center_y"] + random.uniform(0.15, 0.25)
                    end_x = drop.pos_hint["center_x"] + random.uniform(-0.1, 0.1)

                    anim = Animation(
                        pos_hint={"center_x": end_x, "center_y": end_y},
                        opacity=0,
                        duration=0.8
                    )
                    anim.bind(on_complete=lambda *_: self.layout.remove_widget(drop))
                    anim.start(drop)

            def on_trophy_touch(instance, touch):
                if trophy.collide_point(*touch.pos):
                    press_anim = (
                        Animation(size_hint=(0.44, 0.44), duration=0.1) +
                        Animation(size_hint=(0.4, 0.4), duration=0.1)
                    )
                    press_anim.start(trophy)
                    spawn_random_candies()

                    if sound_enabled and self.win_sounds:
                        sound = self.win_sounds[self.sound_index]
                        sound.stop()
                        sound.play()
                        self.sound_index = (self.sound_index + 1) % len(self.win_sounds)
                    return True
                return False

            trophy.bind(on_touch_down=on_trophy_touch)
            self.layout.add_widget(trophy)

            # Thêm từng hũ vào layout
            for jar in jars:
                jar_widget = Image(
                    source=os.path.join(self.assets_dir, jar["source"]),
                    size_hint=(0.08, 0.08),
                    opacity=1,
                    pos_hint={"center_x": jar["pos_x"], "center_y": jar["pos_y"]}
                )
                def make_jar_touch_callback(jw=jar_widget, drop=jar["drop"]):
                    return lambda instance, touch: spawn_from_jar(jw, drop) if jw.collide_point(*touch.pos) else False
                jar_widget.bind(on_touch_down=make_jar_touch_callback())
                self.layout.add_widget(jar_widget)

            # Hiển thị "You Win!"
            label = Label(
                text='[b][color=ffff00]You Win![/color][/b]',
                markup=True,
                font_name=self.font_path,
                font_size='32sp',
                outline_color=(0, 0, 0, 1),
                outline_width=1,
                opacity=0,
                size_hint=(None, None),
                pos_hint={"center_x": 0.5, "center_y": 0.35}
            )
            self.layout.add_widget(label)

            def after_expand(*_):
                start_idle_animation()

            anim1 = Animation(size_hint=(0.4, 0.4), duration=0.4, t='out_back')
            anim1.bind(on_complete=after_expand)
            anim1.start(trophy)

            Animation(opacity=1, duration=0.5).start(label)

        Clock.schedule_once(show_effect, 0.5)


from kivy.uix.modalview import ModalView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
import os

class LoadingScreen(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = [0, 0, 0, 1]  # Nền đen toàn màn
        self.auto_dismiss = False
        self.size_hint = (1, 1)

        self.layout = FloatLayout()
        self.add_widget(self.layout)

        # Ảnh nền toàn màn hình
        self.image = Image(
            source=os.path.join(ASSETS_DIR, "background.png"),
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        self.layout.add_widget(self.image)

        # Dòng chữ "Loading" cố định, không hiệu ứng
        self.label = Label(
            text="Loading",
            font_name=FONT_PATH,
            font_size='48sp',
            color=(1, 1, 1, 1),
            outline_color=(0, 0, 0, 1),
            outline_width=1,
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.layout.add_widget(self.label)

    def on_dismiss(self):
        pass  # Không còn gì để huỷ nữa


from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.properties import NumericProperty
from random import randint, uniform
import math
import os

class AnimatedLabel(Label):
    scale = NumericProperty(1.0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_font_size = kwargs.get("font_size", 40)
        self.bind(scale=self.on_scale)

    def on_scale(self, instance, value):
        self.font_size = self.base_font_size * value

class Package(RelativeLayout):
    def __init__(self, acc, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (300, 200)
        self.pos_hint = {'x': -0.01, 'top': 0.98}
        self.acc = acc

        # Nền
        label_bg = Image(
            source=os.path.join(ASSETS_DIR, "package.png"),
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(None, None),
            size=(300, 200),
            pos=(0, 0)
        )
        self.add_widget(label_bg)

        # Nhóm chứa label và icon
        self.candy_group = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            size=(160, 50),
            pos_hint={'center_x': 0.55, 'top': 0.3},
            spacing=-5,
            padding=0
        )

        # Label số kẹo (có animation scale)
        self.candy_label = AnimatedLabel(
            text=str(acc.get_candy()),
            font_size=40,
            bold=True,
            font_name=FONT_PATH,
            color=(1, 1, 1, 1),
            outline_color=(0, 0, 0, 1),
            outline_width=2,
            size_hint=(None, None),
            size=(60, 50),
            halign='right',
            valign='middle'
        )
        self.candy_label.bind(size=self.candy_label.setter('text_size'))
        self.candy_label.text_size = (60, 50)

        # Icon
        candy_icon = Image(
            source=os.path.join(ASSETS_DIR, 'candy.png'),
            size_hint=(None, None),
            size=(50, 50)
        )

        self.candy_group.add_widget(self.candy_label)
        self.candy_group.add_widget(candy_icon)
        self.add_widget(self.candy_group)

    def update_candy(self, new_value):
        self.candy_label.text = str(new_value)
        self.play_add_effect()
        self.play_label_effect()

    def play_label_effect(self):
        # Animation scale chữ lên rồi thu về
        anim = (
            Animation(scale=1.4, duration=0.1, t='out_back') +
            Animation(scale=1.0, duration=0.15, t='out_quad')
        )
        anim.start(self.candy_label)

    def play_add_effect(self):
        if graphics_quality != "High": return

        used_positions = []

        def is_far_enough(x, y, others, min_dist=30):
            for ox, oy in others:
                if math.hypot(x - ox, y - oy) < min_dist:
                    return False
            return True

        count = 0
        max_attempts = 50
        while count < 6 and max_attempts > 0:
            offset_x = randint(20, self.width - 50)
            offset_y = randint(10, 80)

            if is_far_enough(offset_x, offset_y, used_positions):
                used_positions.append((offset_x, offset_y))

                img = Image(
                    source=os.path.join(ASSETS_DIR, 'candy.png'),
                    size_hint=(None, None),
                    size=(40, 40),
                    pos=(offset_x, offset_y),
                    opacity=1
                )
                self.add_widget(img)

                # Random thời gian animation mỗi viên
                random_duration = uniform(0.6, 1.5)

                # Hạn chế update layout để giảm lag
                anim = Animation(
                    x=offset_x + uniform(-30, 30),
                    y=offset_y + uniform(50, 80),
                    opacity=0,
                    duration=random_duration,
                    t='out_quad'
                )
                anim.bind(on_complete=self._remove_widget)
                anim.start(img)

                count += 1
            else:
                max_attempts -= 1

    def _remove_widget(self, anim, widget):
        if widget.parent:
            widget.parent.remove_widget(widget)


class CandyIcon(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', size_hint=(None, None), **kwargs)
        self.size = (64, 64)

        self.icon = Image(
            source=os.path.join(ASSETS_DIR, "candy.png"),
            size_hint=(None, None),
            size=(50, 50)
        )
        self.add_widget(self.icon)


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_level_index = None
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        self.time_label = None
        self.timer_event = None
        self.debug_event = None
        self.remaining_time = 0
        self.total_tiles = 0
        self.matched_tiles = 0
        self.progress_bar = None
        self.sound_win2 = SoundLoader.load(os.path.join(SOUND_DIR, "win2.ogg"))
        self.sound_click = SoundLoader.load(os.path.join(SOUND_DIR, "click.ogg"))
        self.loading_screen = LoadingScreen()
        
    def update_fps(self, dt):
        fps = Clock.get_fps()
        self.fps_label.text = f"FPS: {int(fps)}"
        
    def show_debug_overlay(self, message, color=(1, 0, 0, 1)):
        if hasattr(self, "_debug_label") and self._debug_label:
            self._debug_label.text = message
            self._debug_label.color = color
            return

        from kivy.uix.label import Label
        self._debug_label = Label(
            text=message,
            font_name=FONT_PATH,
            font_size=36,
            color=color,
            outline_color=(0, 0, 0, 1),
            outline_width=2,
            size_hint=(None, None),
            size=(800, 50),
            pos=(Window.width - 420, Window.height - 60)
        )
        self.layout.add_widget(self._debug_label)
            
    def debug_check_parity(self, *args):
        if not hasattr(self, 'grid_ui') or not self.grid_ui:
        	return
        from collections import Counter
        counter = Counter()
        for row in self.grid_ui.logic.tiles:
            for tile in row:
                if tile and not tile.disabled:
                    counter[tile.candy_type] += 1

        has_odd = any(v % 2 == 1 for v in counter.values())
        if has_odd:
            self.show_debug_overlay("❌ IMPOSSIBLE – Có ô lẻ", color=(1, 0, 0, 1))
        else:
            self.show_debug_overlay("✅ POSSIBLE – Tất cả chẵn", color=(0, 1, 0, 1))

    def load_level(self, level_index):
        self.loading_screen.open()  # ← Hiện loading screen
        Clock.schedule_once(lambda dt: self._do_load_level(level_index), 0.1)
        

    def _do_load_level(self, level_index):
        self.current_level_index = level_index
        self.layout.clear_widgets()
        level = LEVELS[level_index]
        rows = level['rows']
        cols = level['cols']
        distribution = level['distribution']
        self.remaining_time = level.get('time', 30)
        self.total_tiles = sum(count for k, count in distribution.items() if k != "block")
        self.matched_tiles = 0

        bg = Image(
            source=os.path.join(ASSETS_DIR, "background.png"),
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        self.layout.add_widget(bg, index=0)

        logic = AnimalGrid(rows=rows, cols=cols)
        logic.level_shapes = level.get('shapes', [])
        
        self.grid_ui = AnimalGridUI(logic=logic, rows=rows, cols=cols, distribution=distribution)
        self.layout.add_widget(self.grid_ui)

        self.confirmed_exit = False
        self.confirmed_retry = False

        back_btn = ImageButton(
            source=os.path.join(ASSETS_DIR, "exit.png"),
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={'x': 0.01, 'top': 0.15},
            allow_stretch=True,
            keep_ratio=True
        )
        self.layout.add_widget(back_btn)

        self.loading_screen.dismiss()  # ← Ẩn loading screen

        # Cờ xác nhận
        self.confirmed_exit = False
        self.confirmed_retry = False
        if self.debug_event:
        	self.debug_event.cancel()
        self.debug_event = Clock.schedule_interval(self.debug_check_parity, 1)

        # Nút Thoát
        back_btn = ImageButton(
            source=os.path.join(ASSETS_DIR, "exit.png"),
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={'x': 0.01, 'top': 0.15},
            allow_stretch=True,
            keep_ratio=True
        )

        from kivy.core.window import Window
        from kivy.base import EventLoop
        self.fps_label = Label(
            text='FPS: 0',
            font_name=FONT_PATH,
            font_size=36,
            color=(1, 1, 1, 1),
            outline_color=(0, 0, 0, 1),
            outline_width=1,
            size_hint=(None, None),
            size=(100, 30),
            pos=(75, 5)  # Góc trái dưới
        )
        self.layout.add_widget(self.fps_label)

        # Bắt đầu cập nhật FPS mỗi 0.5s
        Clock.schedule_interval(self.update_fps, 0.5)
        
        def reset_exit_confirm(dt):
            self.confirmed_exit = False
            back_btn.source = os.path.join(ASSETS_DIR, "exit.png")

        def on_back_press(instance):
            if self.confirmed_exit:
                self.back_to_select()
            else:
                back_btn.source = os.path.join(ASSETS_DIR, "exit2.png")
                self.confirmed_exit = True
                Clock.schedule_once(reset_exit_confirm, 3)
            if sound_enabled and self.sound_click:
                self.sound_click.play()

        back_btn.bind(on_release=on_back_press)
        self.layout.add_widget(back_btn)

        # Nút Retry
        reset_btn = ImageButton(
            source=os.path.join(ASSETS_DIR, "refresh.png"),
            size_hint=(None, None),
            size=(100, 100),
            pos_hint={'x': 0.065, 'top': 0.15},
            allow_stretch=True,
            keep_ratio=True
        )

        def reset_retry_confirm(dt):
            self.confirmed_retry = False
            reset_btn.source = os.path.join(ASSETS_DIR, "refresh.png")

        def on_retry_press(instance):
            if self.confirmed_retry:
                self.load_level(self.current_level_index)
            else:
                reset_btn.source = os.path.join(ASSETS_DIR, "refresh2.png")
                self.confirmed_retry = True
                Clock.schedule_once(reset_retry_confirm, 3)
            if sound_enabled and self.sound_click:
                self.sound_click.play()

        reset_btn.bind(on_release=on_retry_press)
        self.layout.add_widget(reset_btn)
        
        self.package = Package(acc)
        self.candy_label = self.package.candy_label  # 🔥 thêm dòng này
        self.layout.add_widget(self.package)
        
        # Thanh progress
        self.progress_bar = ImageProgressBar(
            background_image=os.path.join(ASSETS_DIR, "bar1.png"),
            fill_image=os.path.join(ASSETS_DIR, "bar2.png"),
            size_hint=(None, None),
            size=(180, 650),
            pos_hint={'center_x': 0.03, 'top': 0.8}  # chỉnh nếu cần
        )
        self.layout.add_widget(self.progress_bar)
        
        self.time_bar = TimeBar(
        	background_image=os.path.join(ASSETS_DIR, "bar1.png"),
        	fill_image=os.path.join(ASSETS_DIR, "bar3.png"),
        	total=self.remaining_time,
        	remaining=self.remaining_time,
        	size_hint=(None, None),
        	size=(180, 650),
        	pos_hint={'center_x': 0.085, 'top': 0.8}
        )
        self.layout.add_widget(self.time_bar)
        
        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        self.remaining_time -= 1
        if self.time_bar:
        	self.time_bar.remaining = self.remaining_time
        if self.remaining_time <= 0:
            self.timer_event.cancel()
            self.game_over()

    def game_over(self):
        if self.timer_event:
            self.timer_event.cancel()

        if hasattr(self, 'grid_ui') and self.grid_ui:
            anim = Animation(opacity=0, duration=0.5)
            anim.bind(on_complete=lambda *args: self.load_level(self.current_level_index))
            anim.start(self.grid_ui)

    def back_to_select(self, *args):
        if self.timer_event:
            self.timer_event.cancel()
        self.manager.current = 'level_select'
        
    def check_win(self):  
        if self.matched_tiles >= self.total_tiles:  
            if self.timer_event:  
                self.timer_event.cancel()  
  
            effect = WinEffect(  
                layout=self.layout,  
                grid_ui=self.grid_ui if hasattr(self, 'grid_ui') else None,  
                font_path=FONT_PATH,  
                assets_dir=ASSETS_DIR  
            )  
            effect.play()  
            if sound_enabled and self.sound_win2:  
                self.sound_win2.play()  
  
            button_layout = BoxLayout(  
                orientation='horizontal',  
                spacing=40,  
                size_hint=(None, None),  
                size=(300, 100),  
                pos_hint={'center_x': 0.47, 'y': 0.2}  
            )  
  
            def retry_level(instance):  
                self.load_level(self.current_level_index)  
  
            def go_to_select(instance):  
                self.back_to_select()  
  
            def next_level(instance):  
                next_index = self.current_level_index + 1
                if next_index < len(LEVELS):
                	self.load_level(next_index)
                else:  
                    popup = Popup(title="Thông báo",  
                                  content=Label(text="Đã hết màn chơi."),  
                                  size_hint=(0.6, 0.4))  
                    popup.open()  
  
            retry_btn = ImageButton(  
                source=os.path.join(ASSETS_DIR, "retry.png"),  
                size_hint=(None, None),  
                size=(120, 120)  
            )  
            retry_btn.bind(on_release=retry_level)  
  
            menu_btn = ImageButton(  
                source=os.path.join(ASSETS_DIR, "level.png"),  
                size_hint=(None, None),  
                size=(120, 120)  
            )  
            menu_btn.bind(on_release=go_to_select)  
  
            next_btn = ImageButton(  
                source=os.path.join(ASSETS_DIR, "next.png"),  
                size_hint=(None, None),  
                size=(120, 120)  
            )  
            next_btn.bind(on_release=next_level)  
  
            button_layout.add_widget(retry_btn)  
            button_layout.add_widget(menu_btn)  
            button_layout.add_widget(next_btn)  
  
            button_layout.opacity = 0
            def fade_in_buttons(dt):
                self.layout.add_widget(button_layout)
                Animation(opacity=1, duration=1).start(button_layout)
            Clock.schedule_once(fade_in_buttons, 1)

from jnius import autoclass

sound_enabled = True  # Biến toàn cục

class AnimalMatchApp(App):
    def build(self):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        activity.setRequestedOrientation(0)

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(LevelSelectScreen(name='level_select'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(SettingScreen(name='setting'))
        return sm

    def on_start(self):
        self.music_files = [
            os.path.join(SOUND_DIR, 'crazycandy.ogg'),
            os.path.join(SOUND_DIR, 'supercandy.ogg')
        ]
        self.current_music_index = 0
        self.sound = None
        self.play_next_music()

    def play_next_music(self):
        if self.sound:
            self.sound.unbind(on_stop=self.on_music_end)
            self.sound.stop()
            self.sound.unload()
            self.sound = None

        if not sound_enabled:
            return  # Không chơi nếu bị tắt

        current_file = self.music_files[self.current_music_index]
        self.sound = SoundLoader.load(current_file)
        if self.sound:
            self.sound.play()
            self.sound.bind(on_stop=self.on_music_end)

        self.current_music_index = (self.current_music_index + 1) % len(self.music_files)

    def on_music_end(self, instance):
        if sound_enabled:
            self.play_next_music()
        else:
            if self.sound:
                self.sound.unbind(on_stop=self.on_music_end)
                self.sound.stop()
                self.sound.unload()
                self.sound = None

    def update_music_state(self):
        if not sound_enabled:
            if self.sound:
                self.sound.unbind(on_stop=self.on_music_end)
                self.sound.stop()
                self.sound.unload()
                self.sound = None
        else:
            self.play_next_music()

if __name__ == '__main__':
    try:
        AnimalMatchApp().run()
    except Exception as e:
        import traceback
        with open("log.txt", "w") as f:
            f.write("CRASH\n")
            f.write(traceback.format_exc())