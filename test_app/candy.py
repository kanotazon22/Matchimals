import os
import math
import random

from kivy.app import App
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.graphics import PushMatrix, PopMatrix, Rotate
from kivy.core.audio import SoundLoader
import os

BASE_PATH = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_PATH, 'assets', 'images')
SOUND_DIR = os.path.join(BASE_PATH, 'assets', 'sound')

def destroy_tile_and_ice(logic, tile):
    logic.tiles[tile.row][tile.col] = None
    tile.disabled = True
    if getattr(tile, 'has_ice', False):
        tile.has_ice = False
        if hasattr(tile, 'ice_overlay'):
            tile.remove_widget(tile.ice_overlay)
    tile.hide()

class candycornHandler:
    def __init__(self, logic, ui):
        self.logic = logic
        self.ui = ui

    def handle(self, tile1, tile2):
        if tile1.candy_type == "candycorn" and tile2.candy_type == "candycorn":
            return self._double_corn(tile1, tile2)
        elif tile1.candy_type == "candycorn":
            return self._single_corn(tile1)
        elif tile2.candy_type == "candycorn":
            return self._single_corn(tile2)
        return False

    def _find_valid_pairs(self):
        logic = self.logic
        pairs = []
        for r1 in range(logic.rows):
            for c1 in range(logic.cols):
                t1 = logic.tiles[r1][c1]
                if not t1 or t1.candy_type in ["block", "candycorn"]:
                    continue
                for r2 in range(logic.rows):
                    for c2 in range(logic.cols):
                        if r1 == r2 and c1 == c2:
                            continue
                        t2 = logic.tiles[r2][c2]
                        if not t2 or t2.candy_type in ["block", "candycorn"]:
                            continue
                        if t1.candy_type == t2.candy_type and t1.color == t2.color:
                            if logic.is_connectable(t1, t2):
                                pairs.append((t1, t2))
        return pairs

    def _double_corn(self, corn1, corn2):
        pairs = self._find_valid_pairs()
        if not pairs:
            return False
        t1, t2 = random.choice(pairs)
        self._fly_and_destroy(corn1, t1)
        self._fly_and_destroy(corn2, t2)
        return True

    def _single_corn(self, corn):
        pairs = self._find_valid_pairs()
        if not pairs:
            return False
        t1, _ = random.choice(pairs)
        self._fly_and_destroy(corn, t1)
        return True

    def _fly_and_destroy(self, t_from, t_target):
        fx, fy = t_from.center
        tx, ty = t_target.center
        ghost = Image(
            source=os.path.join(ASSETS_DIR, "candycorn.png"),
            size_hint=(None, None),
            size=(self.ui.tile_size, self.ui.tile_size),
            pos=(fx, fy)
        )
        screen = App.get_running_app().root.get_screen('game')
        screen.layout.add_widget(ghost)

        mx = (fx + tx) / 2
        my = (fy + ty) / 2 + 80
        anim1 = Animation(x=mx, y=my, duration=0.4, t='out_quad')
        anim2 = Animation(x=tx, y=ty, duration=0.4, t='in_quad')

        def done(*_):
            screen.layout.remove_widget(ghost)
            if t_target:
                self.logic.tiles[t_target.row][t_target.col] = None
                t_target.hide()
                screen.matched_tiles += 1
                screen.progress_bar.value = 100 * screen.matched_tiles / screen.total_tiles
                screen.check_win()
            self.logic.tiles[t_from.row][t_from.col] = None
            t_from.hide()
            screen.matched_tiles += 1  # ← thêm dòng này không đổi indent

        anim2.bind(on_complete=done)
        anim1.start(ghost)
        anim1.bind(on_complete=lambda *_: anim2.start(ghost))


from collections import defaultdict
from kivy.app import App

class BombHandler:
    def __init__(self, logic, ui):
        self.logic = logic
        self.ui = ui

    def handle(self, bomb1, bomb2):
        destroyed_counter = defaultdict(int)
        self._explode_cross(bomb1, destroyed_counter)
        self._explode_cross(bomb2, destroyed_counter)
        self._fix_odd_counts(destroyed_counter)

        # Cập nhật 1 lần để giảm lag
        screen = App.get_running_app().root.get_screen('game')
        screen.progress_bar.value = 100 * screen.matched_tiles / screen.total_tiles
        screen.check_win()
        return True
        
    def _explode_cross(self, center_tile, counter):
        row, col = center_tile.row, center_tile.col
        screen = App.get_running_app().root.get_screen('game')

        # Chỉ phá: trên, dưới, trái, phải (không phá góc)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        positions = [(row, col)] + [(row + dr, col + dc) for dr, dc in directions]

        destroyed = 0
        for r, c in positions:
            if 0 <= r < self.logic.rows and 0 <= c < self.logic.cols:
                tile = self.logic.tiles[r][c]
                if tile and tile.candy_type != "block":
                    counter[tile.animal_type] += 1
                    self.logic.tiles[r][c] = None
                    destroy_tile_and_ice(self.logic, tile)
                    destroyed += 1

        screen.matched_tiles += destroyed

    def _fix_odd_counts(self, counter):
        screen = App.get_running_app().root.get_screen('game')
        extra = 0
        for animal_type, count in counter.items():
            if count % 2 == 1:
                closest = self._find_closest_tile(animal_type)
                if closest:
                    r, c = closest.row, closest.col
                    self.logic.tiles[r][c] = None
                    closest.hide()
                    extra += 1

        screen.matched_tiles += extra

    def _find_closest_tile(self, animal_type):
        for r in range(self.logic.rows):
            for c in range(self.logic.cols):
                tile = self.logic.tiles[r][c]
                if tile and not tile.disabled and tile.animal_type == animal_type:
                    return tile
        return None


class RainbowHandler:
    def __init__(self, logic, ui):
        self.logic = logic
        self.ui = ui
        self.shared_rotation_event = None
        self.shared_ghosts = []
        self.rotation_speed = 10  # bắt đầu từ 10, tăng dần theo thời gian

    def handle(self, tile1, tile2):
        screen = App.get_running_app().root.get_screen('game')

        # Tìm ra các ô hợp lệ (trừ tile1, tile2, và rainbow)
        all_tiles = [
            tile for row in self.logic.tiles for tile in row
            if tile and tile != tile1 and tile != tile2 and tile.candy_type not in ("rainbow", None)
        ]

        # Gom theo màu
        color_groups = {}
        for tile in all_tiles:
        	key = (tile.candy_type, tile.color)
        	color_groups.setdefault(key, []).append(tile)

        # Chọn mỗi màu đúng 1 cặp (2 ô), tối đa 3 màu khác nhau
        selected_pairs = []
        for color, tiles in color_groups.items():
            if len(tiles) >= 2:
                random.shuffle(tiles)
                pair = (tiles[0], tiles[1])
                selected_pairs.append(pair)

        random.shuffle(selected_pairs)
        selected_pairs = selected_pairs[:3]  # chỉ lấy 3 cặp khác màu

        # rainbow + 3 cặp = tối đa 8 viên
        affected_tiles = [tile1, tile2]
        for a, b in selected_pairs:
            affected_tiles.extend([a, b])

        for tile in affected_tiles:
            self._rotate_in_place(tile)

        # Xoay chung sau 1.5s
        Clock.schedule_once(self._start_shared_rotation, 1.5)
        # Kết thúc toàn bộ sau 3s
        Clock.schedule_once(lambda dt: self._stop_all(affected_tiles), 3)
        return True

    def _rotate_in_place(self, tile):
        screen = App.get_running_app().root.get_screen('game')

        # Tạo ghost rainbow
        ghost = Image(
            source=os.path.join(ASSETS_DIR, "rainbow.png"),
            size_hint=(None, None),
            size=(self.ui.tile_size, self.ui.tile_size),
            pos=(tile.center_x - self.ui.tile_size / 2, tile.center_y - self.ui.tile_size / 2),
            opacity=0
        )
        screen.layout.add_widget(ghost)

        # Fade-in rainbow ghost
        anim_show = Animation(opacity=1, duration=0.3)
        anim_show.start(ghost)

        # Xoay
        rotation = Rotate(angle=0, origin=(0, 0))
        with ghost.canvas.before:
            PushMatrix()
            ghost._rotation = rotation
            ghost.canvas.before.add(rotation)
        with ghost.canvas.after:
            PopMatrix()

        def set_origin(dt):
            rotation.origin = ghost.center
        Clock.schedule_once(set_origin, 0)

        # Solo rotate trước shared
        def solo_rotate(dt):
            rotation.angle += 10
        solo_event = Clock.schedule_interval(solo_rotate, 1 / 30)

        # Lưu ghost và rotation
        self.shared_ghosts.append((ghost, rotation))

        # Dừng solo sau 1.5s
        def stop_solo(dt):
            Clock.unschedule(solo_event)
        Clock.schedule_once(stop_solo, 1.5)

    def _start_shared_rotation(self, dt):
        # Tăng tốc độ xoay theo thời gian
        def shared_rotate(dt):
            self.rotation_speed += 0.5  # mỗi frame tăng 0.5 độ/giây
            for ghost, rotation in self.shared_ghosts:
                rotation.angle += self.rotation_speed

        self.rotation_speed = 10  # reset khi bắt đầu
        self.shared_rotation_event = Clock.schedule_interval(shared_rotate, 1 / 30)
        
    def _stop_all(self, tiles):
        screen = App.get_running_app().root.get_screen('game')

        if self.shared_rotation_event:
            Clock.unschedule(self.shared_rotation_event)

        for ghost, _ in self.shared_ghosts:
            screen.layout.remove_widget(ghost)
        self.shared_ghosts.clear()

        for tile in tiles:
            self.logic.tiles[tile.row][tile.col] = None
            destroy_tile_and_ice(self.logic, tile)
            screen.matched_tiles += 1

        screen.progress_bar.value = 100 * screen.matched_tiles / screen.total_tiles
        screen.check_win()


from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.clock import Clock
import os
import random

class CakeHandler:
    def __init__(self, logic, ui):
        self.logic = logic
        self.ui = ui
        eat_path = os.path.join(SOUND_DIR, "eat.ogg")
        self.sound_eats = [SoundLoader.load(eat_path) for _ in range(4)]
        self.eat_index = 0
        self._pending_cake = 0  # Đếm số bánh đang phá

    def play_eat_sound(self):
        sound = self.sound_eats[self.eat_index]
        if sound:
            try:
                sound.play()
            except:
                pass
        self.eat_index = (self.eat_index + 1) % len(self.sound_eats)

    def handle(self, tile1, tile2):
        if tile1.candy_type == "cake" and tile2.candy_type == "cake":
            self._broken_types = {}  # ✅ Khởi tạo duy nhất 1 lần
            self._pending_cake = 2   # ✅ Đánh dấu còn 2 bánh chưa xử lý xong
            self._launch_cake(tile1)
            self._launch_cake(tile2)
            return True
        return False

    def _launch_cake(self, tile):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        best = []
        max_count = 0
        for dx, dy in directions:
            cnt = self._count_steps(tile, dx, dy)
            if cnt >= 2:
                if cnt > max_count:
                    best = [(dx, dy)]
                    max_count = cnt
                elif cnt == max_count:
                    best.append((dx, dy))
        if not best:
            self._explode_tile(tile)
            self._on_cake_done()
            return

        dx, dy = random.choice(best)
        steps = random.randint(2, 5)
        path = []
        r, c = tile.row, tile.col
        for _ in range(steps):
            r += dx
            c += dy
            if not (0 <= r < self.logic.rows and 0 <= c < self.logic.cols):
                break
            nxt = self.logic.tiles[r][c]
            if nxt:
                path.append(nxt)
        if not path:
            self._explode_tile(tile)
            self._on_cake_done()
            return

        ghost = Image(
            source=os.path.join(ASSETS_DIR, "cake.png"),
            size_hint=(None, None),
            size=(tile.width, tile.height),
            pos=tile.pos
        )
        screen = App.get_running_app().root.get_screen('game')
        screen.layout.add_widget(ghost)

        self._animate_step(ghost, path, 0, tile)

    def _animate_step(self, ghost, path, index, tile):
        screen = App.get_running_app().root.get_screen('game')

        if index >= len(path):
            anim = Animation(opacity=0, duration=0.2)

            def _end(a, w):
                screen.layout.remove_widget(ghost)
                self._explode_tile(tile)
                self._on_cake_done()

            anim.bind(on_complete=_end)
            anim.start(ghost)
            return

        target = path[index]
        anim = Animation(pos=target.pos, duration=0.12, t='linear')

        def _next(a, w):
            if target and not target.disabled:
                ctype = target.candy_type
                self.logic.tiles[target.row][target.col] = None
                target.hide(play_sound=False)
                self.play_eat_sound()
                screen.matched_tiles += 1
                self._broken_types[ctype] = self._broken_types.get(ctype, 0) + 1
            self._animate_step(ghost, path, index + 1, tile)

        anim.bind(on_complete=_next)
        anim.start(ghost)

    def _on_cake_done(self):
        self._pending_cake -= 1
        if self._pending_cake <= 0:
            self._fix_all_odd_tiles()

    def _fix_all_odd_tiles(self):
        from collections import Counter
        counter = Counter()
        type_to_tiles = {}

        for row in range(self.logic.rows):
            for col in range(self.logic.cols):
                tile = self.logic.tiles[row][col]
                if tile and not tile.disabled:
                    counter[tile.candy_type] += 1
                    type_to_tiles.setdefault(tile.candy_type, []).append(tile)

        screen = App.get_running_app().root.get_screen('game')

        for ctype, count in counter.items():
            if count % 2 == 1:
                tile = type_to_tiles[ctype][0]
                self.logic.tiles[tile.row][tile.col] = None
                tile.hide(play_sound=False)
                self.play_eat_sound()
                screen.matched_tiles += 1

    def _count_steps(self, tile, dx, dy):
        cnt = 0
        r, c = tile.row, tile.col
        for _ in range(5):
            r += dx
            c += dy
            if 0 <= r < self.logic.rows and 0 <= c < self.logic.cols:
                t = self.logic.tiles[r][c]
                if t and not t.disabled:
                    cnt += 1
                else:
                    break
            else:
                break
        return cnt
        
    def _explode_tile(self, tile):
        self.logic.tiles[tile.row][tile.col] = None
        destroy_tile_and_ice(self.logic, tile)
        screen = App.get_running_app().root.get_screen('game')
        screen.matched_tiles += 1
        screen.progress_bar.value = 100 * screen.matched_tiles / screen.total_tiles
        screen.check_win()


class SpecialCandyManager:
    def __init__(self, logic, ui):
        self.candycorn_handler = candycornHandler(logic, ui)
        self.bomb_handler = BombHandler(logic, ui)
        self.rainbow_handler = RainbowHandler(logic, ui)
        self.cake_handler = CakeHandler(logic, ui)
        self.sound_bomb = SoundLoader.load(os.path.join(SOUND_DIR, "bomb.ogg"))
        self.sound_candycorn = SoundLoader.load(os.path.join(SOUND_DIR, "candycorn.ogg"))
        self.sound_rainbow = SoundLoader.load(os.path.join(SOUND_DIR, "rainbow.ogg"))
        
    def handle_special(self, tile1, tile2):
        if tile1.candy_type == "candycorn" or tile2.candy_type == "candycorn":
            if self.sound_candycorn:
                self.sound_candycorn.play()
            return self.candycorn_handler.handle(tile1, tile2)
        elif tile1.candy_type == "bomb" and tile2.candy_type == "bomb":
            if self.sound_bomb:
                self.sound_bomb.play()
            return self.bomb_handler.handle(tile1, tile2)
        elif tile1.candy_type == "rainbow" and tile2.candy_type == "rainbow":
        	if self.sound_rainbow:
        		self.sound_rainbow.play()
        	return self.rainbow_handler.handle(tile1, tile2)
        elif tile1.candy_type == "cake" and tile2.candy_type == "cake":
        	return self.cake_handler.handle(tile1, tile2)
        return False
