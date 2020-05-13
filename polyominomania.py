# Welcome to Polyominomania
# See the README.md and github.com/Jelmerro/Polyominomania for more details
# Released into the public domain, see UNLICENSE for details
__license__ = "UNLICENSE"

import abc
import calendar
import datetime
import json
import os
import pyglet
import sys
import threading
import time
from argparse import ArgumentParser
from random import SystemRandom

import polyomino
import util


class MainWindow(pyglet.window.Window):

    def __init__(self, vsync):
        super(MainWindow, self).__init__(
            caption="Polyominomania",
            visible=False,
            vsync=vsync)
        pyglet.gl.glClearColor(0.15, 0.15, 0.15, 255)
        # main loop
        pyglet.clock.schedule_interval(self.loop, 1/60.0)
        # keyboard inputs
        self.keyboard = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keyboard)
        # scenes
        self.scenes = {}
        self.scenes["menu"] = MenuScene()
        self.current_scene = "menu"
        # show
        util.set_current_res(self.width, self.height)
        self.set_visible()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.F11:
            self.set_fullscreen(not self.fullscreen)
            util.set_current_res(self.width, self.height)
            self.scenes[self.current_scene].make_labels()
        if symbol in [pyglet.window.key.RIGHT, pyglet.window.key.D]:
            self.scenes[self.current_scene].key("right")
        if symbol in [pyglet.window.key.LEFT, pyglet.window.key.A]:
            self.scenes[self.current_scene].key("left")
        if symbol in [pyglet.window.key.UP, pyglet.window.key.W]:
            self.scenes[self.current_scene].key("up")
        if symbol in [pyglet.window.key.DOWN, pyglet.window.key.S]:
            self.scenes[self.current_scene].key("down")
        if symbol in [pyglet.window.key.ENTER, pyglet.window.key.SPACE]:
            self.scenes[self.current_scene].key("select")
        if symbol in [pyglet.window.key.BACKSPACE, pyglet.window.key.ESCAPE]:
            self.scenes[self.current_scene].key("back")
        if symbol in [pyglet.window.key.RCTRL, pyglet.window.key.E]:
            self.scenes[self.current_scene].key("other")
        return pyglet.event.EVENT_HANDLED

    def on_draw(self):
        self.clear()
        self.scenes[self.current_scene].draw()

    def loop(self, dt):
        desired = self.scenes[self.current_scene].desired_scene
        if desired == "menu" and "menu" != self.current_scene:
            self.scenes["score"].clear()
            self.scenes["menu"] = MenuScene()
            self.scenes["menu"].make_labels()
            self.current_scene = "menu"
        elif desired == "game" and "game" != self.current_scene:
            self.scenes["menu"].clear()
            self.scenes["game"] = GameScene(self.scenes["menu"].config)
            thr = threading.Thread(target=self.scenes["game"].init_blocks)
            thr.start()
            self.scenes["game"].make_labels()
            self.current_scene = "game"
        elif desired == "score" and "score" != self.current_scene:
            self.scenes["game"].clear()
            self.scenes["score"] = ScoreScene(
                self.scenes["game"].config,
                self.scenes["game"].score,
                self.scenes["game"].lines)
            self.scenes["score"].make_labels()
            self.current_scene = "score"
        # print(self.keyboard)
        keys = {}
        keys["right"] = self.combine_inputs(65363, 100)  # Arrow-right - D
        keys["left"] = self.combine_inputs(65361, 97)  # Arrow-left - A
        keys["up"] = self.combine_inputs(65362, 119)  # Arrow-up - W
        keys["down"] = self.combine_inputs(65364, 115)  # Arrow-down - S
        keys["select"] = self.combine_inputs(65293, 32)  # Enter - Space
        keys["back"] = self.combine_inputs(65288, 65307)  # Backspace - Esc
        keys["other"] = self.combine_inputs(65508, 101)  # RCTRL - E
        self.scenes[self.current_scene].loop(dt, keys)

    def combine_inputs(self, input1, input2):
        if input1 in self.keyboard:
            if self.keyboard[input1]:
                return True
        if input2 in self.keyboard:
            if self.keyboard[input2]:
                return True
        return False


class Scene(metaclass=abc.ABCMeta):

    def __init__(self):
        self.name = ""
        self.desired_scene = ""

    @abc.abstractmethod
    def make_labels(self):
        pass

    @abc.abstractmethod
    def key(self, name):
        pass

    @abc.abstractmethod
    def loop(self, dt, keys):
        pass

    @abc.abstractmethod
    def draw(self):
        pass

    @abc.abstractmethod
    def clear(self):
        pass


class MenuScene(Scene):

    def __init__(self):
        super().__init__()
        self.name = "menu"
        self.desired_scene = "menu"
        self.selected_in_list = "original.json"
        self.list_items = []
        if os.path.isdir("modes"):
            self.list_items = sorted(os.listdir("modes"))
        if len(self.list_items) == 0:
            self.list_items = ["None"]
            self.selected_in_list = self.list_items[0]
        self.config_file = ""
        self.config = {}
        self.valid_config = False
        self.config_log = ""
        self.labels = []

    def make_labels(self):
        self.labels = []
        # title
        self.labels.append(util.make_label(
            "Polyominomania", 66, 320, 440,
            (255, 255, 200, 255), True, None))
        # config list
        height = 350
        for item in self.list_items:
            color = (255, 255, 255, 255)
            if self.selected_in_list == item:
                color = (255, 255, 120, 255)
            name = item.replace(".json", "")[:32]
            if name != item.replace(".json", ""):
                name += ".."
            self.labels.append(util.make_label(
                name, 10, 10, height, color, False, None))
            height -= 10
        # if a valid config is found, show details about the config
        # else list the problem in red
        if self.valid_config:
            color = (255, 255, 255, 255)
            head_color = (200, 200, 255, 255)
            height = 350
            fs = 12
            # Basic information
            self.labels.append(util.make_label(
                "Information", 18, 270, height, head_color, False, None))
            height -= fs
            for part_of_desc in util.split(self.config["description"], 40):
                self.labels.append(util.make_label(
                    part_of_desc, fs, 270, height, color, False, None))
                height -= fs
            color = (200, 255, 200, 255)
            self.labels.append(util.make_label(
                self.config_log, fs, 270, height, color, False, None))
            height -= fs
            color = (255, 255, 255, 255)
            polyomino_string = "Polyominoes: {}".format(
                " ".join(self.config["polyominoes"]))
            for part_of_poly in util.split(polyomino_string, 40):
                self.labels.append(util.make_label(
                    part_of_poly,
                    fs, 270, height, color, False, None))
                height -= fs
            self.labels.append(util.make_label(
                "Lines needed per level: {}".format(
                    self.config["lines_per_level"]),
                fs, 270, height, color, False, None))
            height -= fs
            self.labels.append(util.make_label(
                "First level: {}".format(
                    self.config["first_level"]),
                fs, 270, height, color, False, None))
            height -= fs
            self.labels.append(util.make_label(
                "Next pieces: {}".format(
                    self.config["next_pieces"]),
                fs, 270, height, color, False, None))
            height -= fs
            self.labels.append(util.make_label(
                "Ghost piece: {}".format(
                    "visible" if self.config["ghost"] else "not visible"),
                fs, 270, height, color, False, None))
            height -= fs
            self.labels.append(util.make_label(
                "Grid size: {}x{}".format(
                    self.config["width"],
                    self.config["height"]),
                fs, 270, height, color, False, None))
            height -= 18
            # Scoring information
            self.labels.append(util.make_label(
                "Scoring", 18, 270, height, head_color, False, None))
            height -= fs
            for field in ["polyomino", "softdrop", "harddrop", "level_up"]:
                if self.config["scoring"][field] > 0:
                    self.labels.append(util.make_label(
                        "{} bonus: {}".format(
                            field.title().replace("_", " "),
                            self.config["scoring"][field]),
                        fs, 270, height, color, False, None))
                    height -= fs
            lines_string = "lines:"
            for i in range(1, len(self.config["scoring"]["lines"]) + 1):
                lines_string += " {}".format(
                    self.config["scoring"]["lines"][str(i)])
            for part_of_lines in util.split(lines_string, 40):
                self.labels.append(util.make_label(
                    part_of_lines,
                    fs, 270, height, color, False, None))
                height -= fs
            lines_level_string = "This does not increase per level"
            limit = len(self.config["scoring"]["lines_per_level"]) + 1
            for i in range(1, limit):
                if self.config["scoring"]["lines_per_level"][str(i)] > 0:
                    lines_level_string = "This does increase per level"
                    break
            self.labels.append(util.make_label(
                lines_level_string,
                fs, 270, height, color, False, None))
            height -= fs
        else:
            color = (255, 200, 200, 255)
            height = 350
            fs = 16
            # Show the error information
            for part_of_log in util.split(self.config_log, 36):
                self.labels.append(util.make_label(
                    part_of_log, fs, 270, height, color, False, None))
                height -= fs
        # Select button instructions
        self.labels.append(util.make_label(
            "Press Enter or Space to select",
            18, 270, 10, (255, 255, 255, 255), False, None))

    def key(self, name):
        if name == "select" and self.valid_config:
            self.desired_scene = "game"
        if self.selected_in_list in self.list_items:
            sel = self.list_items.index(self.selected_in_list)
            if name == "up":
                if sel > 0:
                    self.selected_in_list = self.list_items[sel-1]
            if name == "down":
                if sel < len(self.list_items)-1:
                    self.selected_in_list = self.list_items[sel+1]
        else:
            self.selected_in_list = self.list_items[0]
        self.make_labels()

    def loop(self, dt, keys):
        if self.selected_in_list not in self.config_file:
            self.config_file = os.path.join("modes", self.selected_in_list)
            if os.path.isfile(self.config_file):
                with open(self.config_file) as f:
                    try:
                        self.config = json.loads(f.read())
                        self.valid_config, self.config_log = self.check_conf()
                    except json.decoder.JSONDecodeError:
                        self.config = {}
                        self.valid_config = False
                        self.config_log = "Invalid json"
            else:
                self.config = {}
                self.valid_config = False
                self.config_log = "Missing file"
            self.make_labels()

    def check_conf(self):
        # root fields
        root_fields = [
            "description",
            "polyominoes",
            "scoring",
            "lines_per_level",
            "first_level",
            "speed",
            "speed_per_level",
            "width",
            "height",
            "next_pieces",
            "ghost",
            "extra_spacing"
        ]
        for field in root_fields:
            if field not in self.config:
                return False, "Missing an essential field: {}".format(field)
        # description
        if not isinstance(self.config["description"], str):
            return False, "Description must be a string"
        # polyominoes
        if len(self.config["polyominoes"]) == 0:
            return False, "Zero polyomino sets"
        largest_set = 0
        for k, _ in self.config["polyominoes"].items():
            if not k.isdigit():
                return False, "Polyomino id must be a number"
            number = int(k)
            if number > largest_set:
                largest_set = number
            if number > 30 or number < 1:
                return False, "Polyomino id must be between 0 and 31"
            for field in ["next_piece", "colors"]:
                if field not in self.config["polyominoes"][k]:
                    return False, "Missing a polyomino field in number " \
                                  "{}: {}".format(number, field)
                if not isinstance(self.config["polyominoes"][k][field], str):
                    return False, "Field {} in Polyomino {} must be a " \
                                  "str".format(field, number)
            acc = ["random", "jit", "bag"]
            if self.config["polyominoes"][k]["next_piece"] not in acc:
                return False, "next_piece in polyomino {} must be random" \
                              ", bag or jit".format(number)
            supported = polyomino.supported_color_schemes()
            if self.config["polyominoes"][k]["colors"] not in supported:
                return False, "color set in polyomino {} is not " \
                              "a valid set, try original".format(number)
            # chance
            if "chance" not in self.config["polyominoes"][k]:
                return False, "Missing a polyomino field in number " \
                              "{}: chance".format(number)
            if not isinstance(self.config["polyominoes"][k]["chance"], int):
                return False, "chance in polyomino {} must be " \
                              "an int".format(number)
            if self.config["polyominoes"][k]["chance"] < 1:
                return False, "chance in polyomino {} must be " \
                              "at least 1".format(number)

        # scoring
        scoring_fields = [
            "polyomino",
            "lines",
            "lines_per_level",
            "softdrop",
            "harddrop",
            "level_up"
        ]
        for field in scoring_fields:
            if field not in self.config["scoring"]:
                return False, "Missing a scoring field: {}".format(field)
        for field in ["polyomino", "softdrop", "harddrop", "level_up"]:
            if not isinstance(self.config["scoring"][field], int):
                return False, "Field {} in scoring must be an int".format(
                    field)
        for number in range(1, largest_set+1):
            if (
                str(number) in self.config["scoring"]["lines"] and
                str(number) in self.config["scoring"]["lines_per_level"]
            ):
                if (
                    isinstance(
                        self.config["scoring"]["lines"][str(number)], int) and
                    isinstance(
                        self.config["scoring"]["lines_per_level"][str(number)],
                        int)
                ):
                    continue
            return False, "No scoring defined for {} line{}".format(
                number,
                "s" if number > 1 else "")
        # next_pieces
        if not isinstance(self.config["next_pieces"], int):
            return False, "next_pieces must be an int"
        if self.config["next_pieces"] > 4 or self.config["next_pieces"] < 0:
            return False, "next_pieces must be at least 0 and not more than 4"
        # ghost
        if not isinstance(self.config["ghost"], bool):
            return False, "ghost must be a bool"
        # width and height
        for field in ["height", "width"]:
            if not isinstance(self.config[field], int):
                return False, "{} must be an int".format(field)
            if not int(self.config[field]) > largest_set:
                return False, "{} must be above largest set size ({})".format(
                    field,
                    largest_set)
        # extra_spacing
        if not isinstance(self.config["extra_spacing"], bool):
            return False, "extra_spacing must be a bool"
        # other fields
        other_fields = [
            "lines_per_level",
            "first_level",
            "speed",
            "speed_per_level"
        ]
        for field in other_fields:
            if not isinstance(self.config[field], int):
                return False, "{} must be an int".format(field)
            if not int(self.config[field]) > 0:
                return False, "{} must be above zero".format(field)
        # looks good
        return True, "Configuration looks good :)"

    def draw(self):
        for label in self.labels:
            label.draw()

    def clear(self):
        pass


class GameScene(Scene):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.name = "game"
        self.desired_scene = "game"
        self.ready = False
        self.entities = []
        self.batch = pyglet.graphics.Batch()
        self.block_sizes = []
        self.blocks = {}
        self.bags = {}
        self.score = 0
        self.current_level = config["first_level"]
        self.paused = True
        self.pause_text = "Generating polyominoes"
        self.init_blocks_text = ""
        self.pause_label = util.make_label(
            self.pause_text,
            32, 320, 240, (255, 255, 255, 255), True, None)
        self.init_blocks_label = util.make_label(
            "", 12, 320, 200, (255, 255, 255, 255), True, None)
        self.shade = Shade((30, 30, 30, 150))
        self.entities.append(self.shade)
        self.lines = 0
        # labels
        height = 470
        fs = 14
        self.labels = {}
        for label in ["score", "lines", "level"]:
            label_config = [
                fs, 540, height, (255, 255, 255, 255), False, self.batch
            ]
            self.labels["text_{}".format(label)] = util.make_label(
                label.title(), *label_config)
            self.labels["text_{}".format(label)].original_pos = [540, height]
            self.labels["text_{}".format(label)].original_size = fs
            height -= fs
            label_config = [
                fs, 540, height, (255, 255, 255, 255), False, self.batch
            ]
            self.labels[label] = util.make_label("", *label_config)
            self.labels[label].original_pos = [540, height]
            self.labels[label].original_size = fs
            height -= fs
        # block grid
        self.block_grid = []
        for i in range(0, config["height"]):
            self.block_grid.append([])
            for _ in range(0, config["width"]):
                self.block_grid[i].append(None)
        # graphical grid size
        max_width = 540
        max_height = 480
        self.grid_size = int(min([
            max_height / (config["height"] + 1),
            max_width / (config["width"] + 2)
        ]))
        # walls
        wall = {
            "x": 0,
            "y": 480 - int(config["height"]*self.grid_size + self.grid_size),
            "width": int(self.grid_size),
            "height": int(config["height"]*self.grid_size)
        }
        self.entities.append(Wall(wall, self.batch))
        width = config["width"]*int(self.grid_size) + 2*int(self.grid_size)
        wall["x"] = width - int(self.grid_size)
        self.entities.append(Wall(wall, self.batch))
        wall["x"] = 0
        wall["width"] = width
        wall["height"] = int(self.grid_size)
        self.entities.append(Wall(wall, self.batch))
        # initial speed
        spl = config["speed_per_level"]
        speed = 10 / config["speed"] + spl * (self.current_level - 1)
        pyglet.clock.schedule_interval(self.game_loop, speed)
        # loop counter
        self.loop_counter = 0

    def make_labels(self):
        self.labels["score"].text = str(self.score)
        self.labels["lines"].text = str(self.lines)
        self.labels["level"].text = str(self.current_level)
        self.pause_label = util.make_label(
            self.pause_text,
            32, 320, 240, (255, 255, 255, 255), True, None)
        self.init_blocks_label = util.make_label(
            self.init_blocks_text,
            12, 320, 200, (255, 255, 255, 255), True, None)
        for name, label in self.labels.items():
            pos = util.res(*label.original_pos)
            label.x = pos["w"]
            label.y = pos["h"]
            label.font_size = pos["wr"] * label.original_size
            self.labels[name] = label

    def key(self, name):
        if not self.ready:
            return
        if name == "select" and self.pause_text != "PAUSED":
            self.init_block_queue()
            self.pause_text = "PAUSED"
            self.init_blocks_text = ""
            self.paused = False
            return
        if name == "back":
            if self.pause_text != "PAUSED":
                self.init_block_queue()
                self.pause_text = "PAUSED"
                self.init_blocks_text = ""
            self.paused = not self.paused
        if self.paused:
            return
        self.loop_counter = 0
        if name == "right":
            self.move("right")
        if name == "left":
            self.move("left")
        if name == "up":
            self.rotate()
        if name == "down":
            if self.drop_piece():
                self.score += self.config["scoring"]["softdrop"]
        if name == "select":
            while self.drop_piece():
                self.score += self.config["scoring"]["harddrop"]
        if name == "other":
            self.rotate(False)

    def loop(self, dt, keys):
        self.make_labels()
        self.loop_counter += 1
        lc = self.loop_counter
        if self.paused:
            return
        if keys["right"] and lc > 30 and lc % 3 == 0:
            self.move("right")
        if keys["left"] and lc > 30 and lc % 3 == 0:
            self.move("left")
        if keys["down"] and lc > 10 and lc % 2 == 0:
            if self.drop_piece():
                self.score += self.config["scoring"]["softdrop"]

    def draw(self):
        # entities
        self.batch.draw()
        for e in self.entities:
            e.fix_pos()
        # pause overlay
        if self.paused:
            self.shade.draw()
            self.pause_label.draw()
            self.init_blocks_label.draw()

    def game_loop(self, dt):
        if self.paused:
            return
        self.drop_piece()

    def rotate(self, clockwise=True):
        rotated = polyomino.rotate(self.current_block, clockwise)
        left = self.config["width"]
        top = self.config["height"]
        for e in self.entities:
            if isinstance(e, CurrentBlock):
                if e.grid_y < top:
                    top = e.grid_y
                if e.grid_x < left:
                    left = e.grid_x
        new_blocks = []
        shift_x, shift_y = polyomino.fix_rotation_position(
            self.current_block, rotated)
        for y in range(0, len(rotated)):
            for x in range(0, len(rotated[y])):
                if rotated[y][x] == 1:
                    new_x = left + x + shift_x
                    new_y = top + y + shift_y
                    if self.check_grid(new_x, new_y) is not None:
                        return
                    if new_x >= self.config["width"]:
                        return
                    if new_y >= self.config["height"]:
                        return
                    if new_x < 0 or new_y < 0:
                        return
                    new_blocks.append(CurrentBlock(
                        new_x, new_y, self.current_color,
                        self.grid_size, self.batch,
                        self.config["extra_spacing"]))
        self.entities = [
            e for e in self.entities if not isinstance(e, CurrentBlock)]
        for block in new_blocks:
            self.entities.append(block)
        self.current_block = rotated
        if self.config["ghost"]:
            self.update_ghost()

    def move(self, direction):
        if direction == "right":
            movement = 1
        elif direction == "left":
            movement = -1
        can_move = True
        for e in self.entities:
            if isinstance(e, CurrentBlock):
                if e.grid_x + movement == self.config["width"]:
                    can_move = False
                    break
                if e.grid_x + movement < 0:
                    can_move = False
                    break
                if self.check_grid(e.grid_x + movement, e.grid_y) is not None:
                    can_move = False
                    break
        if can_move:
            for e in self.entities:
                if isinstance(e, CurrentBlock):
                    e.update(e.grid_x + movement, e.grid_y)
            if self.config["ghost"]:
                self.update_ghost()
            return True
        return False

    def drop_ghost(self):
        can_fall = True
        for e in self.entities:
            if isinstance(e, GhostBlock):
                if e.grid_y + 1 == self.config["height"]:
                    can_fall = False
                    break
                if self.check_grid(e.grid_x, e.grid_y+1) is not None:
                    can_fall = False
                    break
        if can_fall:
            for e in self.entities:
                if isinstance(e, GhostBlock):
                    e.update(e.grid_x, e.grid_y+1)
            return True
        return False

    def drop_piece(self):
        can_fall = True
        for e in self.entities:
            if isinstance(e, CurrentBlock):
                if e.grid_y + 1 == self.config["height"]:
                    can_fall = False
                    break
                if self.check_grid(e.grid_x, e.grid_y+1) is not None:
                    can_fall = False
                    break
        if can_fall:
            for e in self.entities:
                if isinstance(e, CurrentBlock):
                    e.update(e.grid_x, e.grid_y+1)
            return True
        self.score += self.config["scoring"]["polyomino"]
        self.next_piece()
        self.process_lines()
        return False

    def process_lines(self):
        found_line = True
        number_of_lines = 0
        while found_line:
            found_line = False
            for line in range(0, self.config["height"]):
                block_count = 0
                for col in range(0, self.config["width"]):
                    if self.check_grid(col, line) is not None:
                        block_count += 1
                if block_count != self.config["width"]:
                    continue
                found_line = True
                number_of_lines += 1
                remove_blocks = []
                for e in self.entities:
                    if type(e) == Block:
                        if e.grid_y == line:
                            remove_blocks.append(e)
                        elif e.grid_y < line:
                            e.update(e.grid_x, e.grid_y+1)
                self.entities = list(
                    set(self.entities).difference(set(remove_blocks)))
        self.update_score_by_lines(number_of_lines)
        if self.config["ghost"]:
            self.update_ghost()

    def check_grid(self, x, y):
        for e in self.entities:
            if type(e) == Block:
                if e.grid_x == x and e.grid_y == y:
                    return e
        return None

    def next_level(self):
        self.score += self.config["scoring"]["level_up"]
        self.current_level += 1
        pyglet.clock.unschedule(self.game_loop)
        spl = self.config["speed_per_level"]
        speed = 10 / (self.config["speed"] + spl * (self.current_level - 1))
        pyglet.clock.schedule_interval(self.game_loop, speed)

    def update_score_by_lines(self, n):
        if n == 0:
            return
        self.lines += n
        required_level = int(self.lines / self.config["lines_per_level"])
        required_level -= self.config["first_level"]
        required_level += 2
        while required_level > self.current_level:
            self.next_level()
        base_score = self.config["scoring"]["lines"][str(n)]
        level_score = self.config["scoring"]["lines_per_level"][str(n)]
        self.score += base_score + level_score * (self.current_level - 1)

    def new_piece(self):
        size = SystemRandom().choice(self.block_sizes)
        if size in self.bags:
            length = len(self.bags[size])
            if length == 0:
                self.bags[size] = self.blocks[size][:]
                length = len(self.bags[size])
            return self.bags[size].pop(SystemRandom().randrange(length))
        if size in self.blocks:
            return SystemRandom().choice(self.blocks[size])
        return polyomino.generate(size)

    def init_block_queue(self):
        self.block_queue = []
        self.block_queue_colors = []
        for _ in range(0, self.config["next_pieces"]):
            new_piece = self.new_piece()
            self.block_queue.append(new_piece)
            scheme = self.config["polyominoes"][str(sum(sum(
                new_piece, []), 0))]["colors"]
            self.block_queue_colors.append(polyomino.color(new_piece, scheme))
        self.next_piece()

    def next_piece(self):
        new_piece = self.new_piece()
        self.block_queue.append(new_piece)
        scheme = self.config["polyominoes"][str(sum(sum(
            new_piece, []), 0))]["colors"]
        self.block_queue_colors.append(polyomino.color(new_piece, scheme))
        self.current_block = self.block_queue.pop(0)
        self.current_color = self.block_queue_colors.pop(0)
        block_width = len(self.current_block)
        width = int(self.config["width"] / 2 + 1 - block_width / 2)
        old_blocks = [e for e in self.entities if isinstance(e, CurrentBlock)]
        for block in old_blocks:
            if block.grid_y < 3:
                self.desired_scene = "score"
                return
            self.entities.append(Block(
                block.grid_x,
                block.grid_y,
                block.stored_color,
                self.grid_size,
                self.batch,
                self.config["extra_spacing"]))
        self.entities = [
            e for e in self.entities if not isinstance(e, CurrentBlock)]
        for y in range(0, len(self.current_block)):
            for x in range(0, len(self.current_block[y])):
                if self.current_block[y][x] == 1:
                    block = CurrentBlock(
                        width + x,
                        y,
                        self.current_color,
                        self.grid_size,
                        self.batch,
                        self.config["extra_spacing"])
                    self.entities.append(block)
        self.preview_pieces()
        if self.config["ghost"]:
            self.update_ghost()

    def update_ghost(self):
        self.entities = [
            e for e in self.entities if not isinstance(e, GhostBlock)]
        for e in self.entities:
            if isinstance(e, CurrentBlock):
                block = GhostBlock(
                    e.grid_x,
                    e.grid_y,
                    self.current_color,
                    self.grid_size,
                    self.batch,
                    self.config["extra_spacing"])
                self.entities.append(block)
        while self.drop_ghost():
            pass

    def preview_pieces(self):
        self.entities = [
            e for e in self.entities if not isinstance(e, PreviewBlock)]
        base_y = 350
        number = 0
        smaller_grid = int(80 / max(self.block_sizes))
        for block in self.block_queue:
            for y in range(0, len(block)):
                for x in range(0, len(block[y])):
                    if block[y][x] == 1:
                        self.entities.append(PreviewBlock(
                            {
                                "x": 540 + x * smaller_grid,
                                "y": base_y - y * smaller_grid,
                                "width": smaller_grid - 1,
                                "height": smaller_grid - 1,
                                "color": self.block_queue_colors[number]
                            }, self.batch))
            number += 1
            base_y -= 80

    def init_blocks(self):
        time.sleep(1)
        for k, v in self.config["polyominoes"].items():
            for _ in range(0, v["chance"]):
                self.block_sizes.append(int(k))
            if v["next_piece"] != "jit":
                self.blocks[int(k)] = self.generate_all_polyominoes(int(k))
            if v["next_piece"] == "bag":
                self.bags[int(k)] = self.blocks[int(k)][:]
        self.pause_text = "Ready to go"
        self.init_blocks_text = "Press Enter or Space to start"
        self.ready = True

    def generate_all_polyominoes(self, number):
        pieces = []
        while len(pieces) < polyomino.A000988[number]:
            piece = polyomino.generate(number)
            if not polyomino.duplicate(pieces, piece):
                message = "Number {}: Generated {} out " \
                          "of {} so far, normally takes {}".format(
                              number,
                              len(pieces),
                              polyomino.A000988[number],
                              polyomino.install_times(number))
                self.init_blocks_text = message
                pieces.append(piece)
        return pieces

    def clear(self):
        pyglet.clock.unschedule(self.game_loop)
        self.batch.invalidate()


class ScoreScene(Scene):

    def __init__(self, config, score, lines):
        super().__init__()
        self.name = "score"
        self.desired_scene = "score"
        self.config = config
        self.score = score
        self.lines = lines
        self.generate_config_string()
        self.highscores = {}
        self.chars = [e for e in " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"]
        self.writer_index = 0
        self.character_ids = []
        for _ in range(0, 9):
            self.character_ids.append(0)
        # read and fix highscore json file
        if os.path.isfile("highscores.json"):
            with open("highscores.json") as f:
                try:
                    self.highscores = json.loads(f.read())
                except json.decoder.JSONDecodeError:
                    pass
        remove_broken_highscore_configs = []
        for k, v in self.highscores.items():
            if not isinstance(v, list):
                continue
            remove_broken_scores = []
            for person in v:
                if not isinstance(person, dict):
                    remove_broken_scores.append(person)
                    continue
                for field in ["name", "date", "score", "lines"]:
                    if field not in person:
                        remove_broken_scores.append(person)
                        continue
                    if field in ["name"]:
                        if not isinstance(person[field], str):
                            remove_broken_scores.append(person)
                            continue
                    if field in ["date", "score", "lines"]:
                        if not isinstance(person[field], int):
                            remove_broken_scores.append(person)
                            continue
            for s in remove_broken_scores:
                self.highscores[k].remove(s)
        for k in remove_broken_highscore_configs:
            self.highscores.pop(k)
        # loop counter
        self.loop_counter = 0
        self.labels = []
        self.make_labels()

    def make_labels(self):
        self.labels = []
        for c in range(0, 9):
            color = (255, 255, 255, 255)
            if self.writer_index == c:
                color = (100, 255, 100, 255)
            self.labels.append(util.make_label(
                self.chars[self.character_ids[c]].replace(" ", "."),
                26, 20+c*26, 10, color, False, None))
        color = (255, 255, 255, 255)
        if self.writer_index == 9:
            color = (100, 255, 100, 255)
        self.labels.append(util.make_label(
            "OK",
            26, 260, 10, color, False, None))
        no_highscores = False
        if self.config_string not in self.highscores:
            no_highscores = True
        elif len(self.highscores[self.config_string]) == 0:
            no_highscores = True
        if no_highscores:
            self.labels.append(util.make_label(
                "No Highscores for this config yet!",
                12,
                320,
                400,
                (255, 255, 255, 255), True, None))
        else:
            number = 1
            height = 400
            fs = 12
            self.labels.append(util.make_label(
                "pos{}name{}score{}lines{}date".format(
                    " "*6,
                    " "*16,
                    " "*11,
                    " "*22
                ), fs, 16, height, (255, 255, 255, 255), False, None))
            height -= fs
            scores = self.highscores[self.config_string]
            for player_score in sorted(scores,
                                       key=lambda k: k["score"],
                                       reverse=True):
                self.labels.append(util.make_label(
                    "{} {} {} {} {}".format(
                        str(number).rjust(2, " "),
                        str(player_score["name"]).rjust(9, " "),
                        str(player_score["score"]).rjust(20, " "),
                        str(player_score["lines"]).rjust(15, " "),
                        str(self.dt(player_score["date"])).rjust(25, " ")
                    ), fs, 24, height, (255, 255, 255, 255), False, None))
                height -= fs
                number += 1
                if number > 30:
                    break
        self.labels.append(util.make_label(
            "Highscores", 40, 320, 440, (255, 255, 255, 255), True, None))
        self.labels.append(util.make_label(
            "Score: {}".format(self.score),
            26, 320, 10, (255, 255, 255, 255), False, None))

    def key(self, name):
        self.loop_counter = 0
        if name == "select":
            if self.writer_index > 8:
                player = ""
                for c in range(0, 9):
                    player += self.chars[self.character_ids[c]]
                player = player.strip()
                if player:
                    self.add_highscore(player)
            else:
                self.writer_index = 9
        if name == "left":
            if self.writer_index > 0:
                self.writer_index -= 1
        if name == "right":
            if self.writer_index < 9:
                self.writer_index += 1
        if self.writer_index > 8:
            self.make_labels()
            return
        if name == "up":
            if self.character_ids[self.writer_index] == len(self.chars) - 1:
                self.character_ids[self.writer_index] = 0
            else:
                self.character_ids[self.writer_index] += 1
        if name == "down":
            if self.character_ids[self.writer_index] == 0:
                self.character_ids[self.writer_index] = len(self.chars) - 1
            else:
                self.character_ids[self.writer_index] -= 1
        self.make_labels()

    def loop(self, dt, keys):
        if self.writer_index > 9:
            return
        self.loop_counter += 1
        lc = self.loop_counter
        if keys["up"] and lc > 20 and lc % 3 == 0:
            if self.character_ids[self.writer_index] == len(self.chars) - 1:
                self.character_ids[self.writer_index] = 0
            else:
                self.character_ids[self.writer_index] += 1
            self.make_labels()
        if keys["down"] and lc > 20 and lc % 3 == 0:
            if self.character_ids[self.writer_index] == 0:
                self.character_ids[self.writer_index] = len(self.chars) - 1
            else:
                self.character_ids[self.writer_index] -= 1
            self.make_labels()

    def draw(self):
        for label in self.labels:
            label.draw()

    def generate_config_string(self):
        output = ""
        for n, v in sorted(self.config["polyominoes"].items()):
            output += "{}:{},".format(n, v["next_piece"])
            output += "{}:{},".format(n, v["chance"])
        output += "{},".format(self.config["scoring"]["polyomino"])
        output += "{},".format(self.config["scoring"]["softdrop"])
        output += "{},".format(self.config["scoring"]["harddrop"])
        output += "{},".format(self.config["scoring"]["level_up"])
        for n, v in sorted(self.config["scoring"]["lines"].items()):
            output += "{}:{},".format(n, v)
        for n, v in sorted(self.config["scoring"]["lines_per_level"].items()):
            output += "{}:{},".format(n, v)
        other_fields = [
            "lines_per_level", "first_level", "speed", "speed_per_level",
            "width", "height", "next_pieces", "ghost"
        ]
        for field in other_fields:
            output += "{}:{},".format(field, self.config[field])
        self.config_string = output[:-1]

    def add_highscore(self, name):
        if self.config_string not in self.highscores:
            self.highscores[self.config_string] = []
        self.highscores[self.config_string].append({
            "name": name,
            "date": self.ut(datetime.datetime.utcnow()),
            "score": self.score,
            "lines": self.lines,
        })
        with open("highscores.json", "w") as f:
            f.write(json.dumps(self.highscores, indent=4))
        self.desired_scene = "menu"

    def dt(self, u):
        return datetime.datetime.fromtimestamp(u)

    def ut(self, d):
        return calendar.timegm(d.timetuple())

    def clear(self):
        pass


class Entity(pyglet.sprite.Sprite, metaclass=abc.ABCMeta):

    def __init__(self, p, batch):
        """ Base Entity Class

        A superclass for all entities.
        Can be customised using the following properties:
        x, y, sprite/color, width, height
        """
        if "sprite" in p:
            sprite = pyglet.image.load(p["sprite"])
        else:
            sprite = pyglet.image.create(
                p["width"],
                p["height"],
                pyglet.image.SolidColorImagePattern(p["color"]))
        self.actual_size = [p["width"], p["height"]]
        self.pos = [p["x"], p["y"]]
        super().__init__(sprite, x=p["x"], y=p["y"], batch=batch)
        self.fix_pos()

    def fix_pos(self):
        pos = util.res(*self.pos)
        self.x = pos["w"]
        self.y = pos["h"]
        self.image.width = self.actual_size[0] * pos["wr"]
        self.image.height = self.actual_size[1] * pos["hr"]


class Block(Entity):

    def __init__(self, x, y, color, gs, batch, extra_spacing):
        """ Wall Entity

        A colored block representing the polyomino squares.
        """
        self.grid_size = gs
        self.grid_x = x
        self.grid_y = y
        self.stored_color = color
        self.spacing_between = extra_spacing
        properties = {"color": color}
        properties["x"], properties["y"] = self.grid_to_screen(x, y)
        properties["width"] = int(self.grid_size)
        properties["height"] = int(self.grid_size)
        super().__init__(properties, batch)
        self.fix_pos()

    def grid_to_screen(self, x, y):
        screen_x = int(self.grid_size) + x*int(self.grid_size)
        screen_y = 480 - (y+1)*self.grid_size
        return int(screen_x), int(screen_y)

    def update(self, x, y):
        self.grid_x = x
        self.grid_y = y
        tempx, tempy = self.grid_to_screen(x, y)
        self.pos = self.grid_to_screen(x, y)

    def fix_pos(self):
        if self.spacing_between:
            pos = util.res(self.pos[0] + 1, self.pos[1] + 1)
            self.x = pos["w"]
            self.y = pos["h"]
            self.image.width = (self.actual_size[0] - 2) * pos["wr"]
            self.image.height = (self.actual_size[1] - 2) * pos["hr"]
        else:
            pos = util.res(*self.pos)
            self.x = pos["w"]
            self.y = pos["h"]
            self.image.width = self.actual_size[0] * pos["wr"]
            self.image.height = self.actual_size[1] * pos["hr"]


class CurrentBlock(Block):
    pass


class PreviewBlock(Entity):
    pass


class GhostBlock(Block):

    def __init__(self, x, y, color, gs, batch, extra_spacing):
        color = (*color[0:3], 100)
        super().__init__(x, y, color, gs, batch, extra_spacing)


class Wall(Entity):

    def __init__(self, properties, batch):
        """ Wall Entity

        A completely stateless entity with no movement.
        Always drawn as a white square at the specified location.
        Properties: x, y, width, height
        """
        properties["color"] = (255, 255, 255, 255)
        super().__init__(properties, batch)


class Shade(Entity):

    def __init__(self, color):
        """ Shade Entity

        Draws a shade over the entire screen.
        Only requires the color property.
        """
        properties = {}
        properties["x"] = 0
        properties["y"] = 0
        properties["width"] = 640
        properties["height"] = 480
        properties["color"] = color
        super().__init__(properties, None)


if __name__ == "__main__":
    # Parse the arguments
    parser = ArgumentParser(description="Polyominomania can parse command "
                            "line arguments, to change critical settings.")
    parser.add_argument("--disable-vsync", action="store_true",
                        help="Enable or disable vsync")
    parser.add_argument("--skip-font", action="store_true",
                        help="Skip the installation of required fonts.")
    args = parser.parse_args()
    # install font if needed
    if not args.skip_font:
        success = util.install_font("font/FSEX300.ttf")
        if not success:
            sys.exit(1)
    vsync = True
    if args.disable_vsync:
        vsync = False
    MainWindow(vsync)
    pyglet.app.run()
