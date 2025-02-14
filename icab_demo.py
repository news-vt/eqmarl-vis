from contextlib import contextmanager
from enum import IntEnum
import itertools
import glob
import json
import os
import random
import pandas as pd
from pathlib import Path
import tempfile
from typing import Any, Callable, Generator, Iterable, Optional

from manim import *
from manim.typing import *
from manim_voiceover import VoiceoverScene, VoiceoverTracker
from manim_voiceover.services.gtts import GTTSService
from manim_voiceover.services.coqui import CoquiService
import segno

# config.disable_caching = True
# config.quality = 'low_quality'

# Tool for creating voiceovers with Manim: https://www.manim.community/plugin/manim-voiceover/

# Example of making a neural network with Manim: https://medium.com/@andresberejnoi/using-manim-and-python-to-create-animations-like-3blue1brown-andres-berejnoi-34f755606761


def load_train_results(filepath: str | Path) -> tuple[list, dict[str, Any]]:
    """Loads training results from JSON file."""
    with open(str(filepath), 'r') as f:
        d = json.load(f)
    return d['reward'], d['metrics']

def remove_nan(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Remove all indices of NaN values detected in `y` from both `x` and `y`."""
    valid_idx = ~np.isnan(y)
    x_valid = x[valid_idx]
    y_valid = y[valid_idx]
    return x_valid, y_valid

def batched(iterable, n: int):
    """Converts a list into a list of tuples of every `n` elements.
    
    For n=2, the function will produce:
    x -> [(x0, x1), (x2, x3), ...]
    """
    x = iter(iterable)
    return zip(*([x]*n))

def negative_index_rollover(i: int, size: int) -> int:
    """Convert an index `i` from negative to positive.
    
    Example:
    size=5, i=-1 -> i=4 # Index from the end.
    size=5, i=3 -> i=3 # No change.
    """
    return i if i >= 0 else i+size

class CustomFlash(AnimationGroup):
    """Custom `Flash` animation to work with `Succession` animation groups."""
    def __init__(
        self,
        point: np.ndarray | Mobject,
        line_length: float = 0.2,
        num_lines: int = 12,
        flash_radius: float = 0.1,
        line_stroke_width: int = 3,
        color: str = YELLOW,
        time_width: float = 1,
        run_time: float = 1.0,
        **kwargs,
    ) -> None:
        if isinstance(point, Mobject):
            self.point = point.get_center()
        else:
            self.point = point
        self.color = color
        self.line_length = line_length
        self.num_lines = num_lines
        self.flash_radius = flash_radius
        self.line_stroke_width = line_stroke_width
        self.run_time = run_time
        self.time_width = time_width
        self.animation_config = kwargs

        self.lines = self.create_lines()
        animations = self.create_line_anims()
        super().__init__(*animations)

    def create_lines(self) -> VGroup:
        lines = VGroup()
        for angle in np.arange(0, TAU, TAU / self.num_lines):
            line = Line(self.point, self.point + self.line_length * RIGHT)
            line.shift((self.flash_radius) * RIGHT)
            line.rotate(angle, about_point=self.point)
            lines.add(line)
        lines.set_color(self.color)
        lines.set_stroke(width=self.line_stroke_width)
        return lines

    def create_line_anims(self) -> Iterable[ShowPassingFlash]:
        return [
            ShowPassingFlash(
                line,
                time_width=self.time_width,
                run_time=self.run_time,
                **self.animation_config,
            )
            for line in self.lines
        ]

class IconList(VGroup):
    def __init__(self, *items: VMobject, icon: VMobject, **kwargs):
        super().__init__()
        n_items = len(items)
        for item in items:
            self.add(icon.copy())
            self.add(item)
        self.arrange_in_grid(rows=n_items, cols=2, **kwargs)
    
    def enumerate_rows(self):
        n_items = len(self.submobjects)
        for i in range(0, n_items-1, 2):
            yield (self.submobjects[i], self.submobjects[i+1])

class MObjectWithLabel(Group):
    def __init__(self, obj: Mobject, label: VMobject, direction: Vector3D = DOWN, buff: float = 0.1, **kwargs):
        super().__init__(**kwargs)
        label = label.next_to(obj, direction=direction, buff=buff)
        self.obj = obj
        self.label = label
        self.add(obj, label)

class VMObjectWithLabel(VGroup):
    def __init__(self, obj: VMobject, label: VMobject, direction: Vector3D = DOWN, buff: float = 0.1, **kwargs):
        super().__init__(**kwargs)
        label = label.next_to(obj, direction=direction, buff=buff)
        self.obj = obj
        self.label = label
        self.add(obj, label)

class SegnoQRCodeImageMobject(ImageMobject):
    """Converts a QR Code generated using `segno` as a Manim `ImageMobject`."""
    def __init__(self, qr: segno.QRCode, **kwargs):
        config = {
            'light': None,
            'dark': WHITE.to_hex(),
            'border': 0,
            'scale': 100,
        }
        config.update(kwargs)

        with tempfile.NamedTemporaryFile(suffix='.png') as tmpfile:
            tmpfile_name = tmpfile.name
            qr.save(tmpfile_name, **config)
            super().__init__(tmpfile_name)
        
        # Ensure the temporary file does not exist anymore.
        assert not os.path.exists(tmpfile_name)


class Qubit(VMobject):
    
    config = {
        'text_top_color': WHITE,
        'text_bottom_color': WHITE,
        'dots_origin_color': GRAY,
        'dots_top_color': GRAY,
        'dots_bottom_color': GRAY,
        'arrow_color': WHITE,
        'arrow_stroke_width': 6,
        'circle_color': PURPLE,
        'ellipse_color': PURPLE,
        'has_text': True,
    }
    
    def __init__(self, **kwargs):
        super().__init__()
        
        # Merge the default config with any user-provided config.
        self.config.update(kwargs)
        
        groupdict = {}
        
        circle = Circle(color=self.config['circle_color'])
        ellipse = Ellipse(width=circle.width, height=0.4, color=self.config['ellipse_color']).move_to(circle.get_center())
        ellipse = DashedVMobject(ellipse, num_dashes=12, equal_lengths=False, color=self.config['ellipse_color'])
        dots = VDict({
            'origin': Dot(ORIGIN, color=self.config['dots_origin_color']),
            'top': Dot(circle.get_top(), color=self.config['dots_top_color']),
            'bottom': Dot(circle.get_bottom(), color=self.config['dots_bottom_color']),
        })
        arrow = Arrow(start=circle.get_center(), end=circle.point_at_angle(45*DEGREES), buff=0, color=self.config['arrow_color'], stroke_width=self.config['arrow_stroke_width'])
        shapes = VDict({
            'circle': circle,
            'arrow': arrow,
            'ellipse': ellipse,
            'dots': dots,
        })
        groupdict['shapes'] = shapes # Preserve the shapes for use outside of the class.
        
        if self.config['has_text']:
            text = VGroup(*[
                MathTex(r"|0\rangle", color=self.config['text_top_color']).next_to(dots['top'], UP),
                MathTex(r"|1\rangle", color=self.config['text_bottom_color']).next_to(dots['bottom'], DOWN),
            ])
            groupdict['text'] = text # Preserve the text for use outside of the class.
        
        # Group the shapes and text (if any) together.
        self.group = VDict(groupdict)
        self.add(self.group)
    
    def set_state_angle(self, angle: float):
        return self.group['shapes']['arrow'].put_start_and_end_on(self.group['shapes']['circle'].get_center(), self.group['shapes']['circle'].point_at_angle(angle))



class MinigridAction(IntEnum):
    LEFT = 0
    RIGHT = 1
    FORWARD = 2

def minigrid_path_str_to_list(s: str) -> list[MinigridAction]:
    """Converts a string of MiniGrid action codes to a list of action objects.
    
    Supported action codes are: ['l', 'r', 'f'] (uppercase also allowed)
    """
    assert all(a in ['l', 'r', 'f'] for a in s.lower()), "Only actions supported are ['l', 'r', 'f'] (uppercase also allowed)"
    path = []
    for a in s.lower():
        if a == 'l':
            path.append(MinigridAction.LEFT)
        elif a == 'r':
            path.append(MinigridAction.RIGHT)
        elif a == 'f':
            path.append(MinigridAction.FORWARD)
    return path


class RotationTrackableGroup(Group):
    """Facilitates tracking the rotation angle of MObjects.
    """
    def __init__(self, *args, angle: float = 0., **kwargs):
        super().__init__(*args, **kwargs)
        self.tracker_angle = ValueTracker(angle)
        self._invisible_line = Line(self.get_left(), self.get_right(), stroke_width=0) # 0 degrees.
        self.add(self._invisible_line)
    
    def get_angle(self):
        return self._invisible_line.get_angle()

class RotationTrackableVGroup(RotationTrackableGroup, VGroup):
    """Facilitates tracking the rotation angle of VMObjects.
    """
    pass

class MiniGrid(Group):
    
    # Common objects for reuse.
    assets: dict[str, Mobject] = {
        'grid-empty': Square(color=GRAY, fill_opacity=0),
        'grid-lava': Square(color=ORANGE, fill_opacity=0.5),
        'grid-goal': Square(color=GREEN, fill_opacity=0.5),
        # 'player': VGroup(*[
        #     Triangle(color=RED, fill_opacity=0.5),
        #     Dot(Triangle().get_top()) # Dot represents the leading tip of the player triangle.
        # ],z_index=1).rotate(270*DEGREES), # Higher z-index sets on top.
        #####
        'player': RotationTrackableVGroup(VGroup(*[
            Triangle(color=RED, fill_opacity=0.5),
            Dot(Triangle().get_top()) # Dot represents the leading tip of the player triangle.
        ],z_index=1)).rotate(270*DEGREES), # Higher z-index sets on top.
        # 'player': RotationTrackableGroup(Group(*[
        #     ImageMobject("assets/images/quadcopter.png").scale(0.5),
        #     # Dot(Triangle().get_top()) # Dot represents the leading tip of the player triangle.
        # ],z_index=1)),
        # .rotate(270*DEGREES), # Higher z-index sets on top.
        # 'player': MiniGridPlayer(),
    }
    
    def __init__(self, 
        grid_size: tuple[int,int], 
        player_look_angle: float = 270, # degrees, RIGHT
        player_grid_pos: tuple[int,int] = (0,0), # Top-left.
        goal_grid_pos: tuple[int,int] = (-1, -1),
        hazards_grid_pos: list[tuple[int,int]] = [],
        **kwargs,
        ):
        super().__init__(**kwargs)
        self.grid_size = grid_size
        
        # Support for negative indexing.
        player_grid_pos = tuple(negative_index_rollover(i, size) for i,size in zip(player_grid_pos, grid_size))
        goal_grid_pos = tuple(negative_index_rollover(i, size) for i,size in zip(goal_grid_pos, grid_size))
        hazards_grid_pos = [tuple(negative_index_rollover(i, size) for i,size in zip(haz, grid_size)) for haz in hazards_grid_pos]
        
        self.goal_pos = goal_grid_pos
        self.hazards_grid_pos = hazards_grid_pos
        
        # Build the grid using assets.
        world_dict = self.build_minigrid(
            grid_size=grid_size,
            player_pos=player_grid_pos,
            goal_pos=self.goal_pos,
            hazards=self.hazards_grid_pos,
            grid_obj_default=self.assets['grid-empty'],
            grid_obj_hazard=self.assets['grid-lava'],
            grid_obj_goal=self.assets['grid-goal'],
            grid_obj_player=self.assets['player'],
        )
        self.world = world_dict

        # IMPORTANT - we must add all sub-objects that we want displayed.
        self.add(*[m for k, m in world_dict.items()])
    
    def pos_to_index(self, pos: tuple[int,int]) -> int:
        """Converts a 2D position to a 1D index."""
        return pos[0]*self.grid_size[0] + pos[1]
    
    def index_to_pos(self, index: int) -> tuple[int,int]:
        """Converts a 1D index to a 2D position."""
        return (index//self.grid_size[0], index%self.grid_size[1])

    def pos_to_coord(self, pos: tuple[int,int]) -> Point3D:
        """2D grid position to 3D frame coordinate."""
        return self.world['grid'][self.pos_to_index(pos)].get_center() # 3D frame coordinate of grid element.
    
    def coord_to_index(self, coord: Point3D) -> int:
        """Convert 3D vector coordinate to a 1D grid position index.
        
        This snaps the 3D coordinate to a 2D position on the grid based on the element's 1D index within the grid.
        Gets the closest grid position based on it's center point.
        """
        closest_mobject = min(self.world['grid'], key=lambda g: np.linalg.norm(g.get_center() - coord))
        closest_index = self.world['grid'].submobjects.index(closest_mobject)
        return closest_index

    def coord_to_pos(self, coord: Point3D) -> tuple[int,int]:
        """Convert 3D vector coordinate to 2D grid position.
        
        This snaps the 3D coordinate to a 2D position on the grid.
        Gets the closest grid position based on it's center point.
        """
        closest_index = self.coord_to_index(coord)
        return self.index_to_pos(closest_index)

    def get_player_coord(self) -> Point3D:
        """Get player position as 3D scene coordinate."""
        return self.world['player'].get_center() # Get scene coordinate for player.

    def get_player_pos(self) -> tuple[int, int]:
        """Get player position as 2D grid coordinate (row, col)."""
        r, c = self.coord_to_pos(self.get_player_coord()) # Converts coordinate to (row,col).
        return int(r), int(c) # Ensure integer.

    def get_player(self) -> Mobject:
        return self.world['player']

    def get_goal_coord(self) -> Point3D:
        """Get goal position as 3D scene coordinate."""
        return self.pos_to_coord(self.goal_pos)
    
    def get_goal_pos(self) -> tuple[int, int]:
        """Get goal position as 2D grid position (row, col)."""
        return self.goal_pos

    def get_goal(self) -> Mobject:
        """Get goal MObject."""
        return self.world['grid'][self.pos_to_index(self.get_goal_pos())]
    
    def get_grid_at_pos(self, pos: tuple[int,int]) -> Mobject:
        """Get grid MObject at 2D grid position (row, col)."""
        return self.world['grid'][self.pos_to_index(pos)]
    
    def get_hazards_pos(self) -> list[tuple[int,int]]:
        """Get list of hazard grid positions (row, col)."""
        return self.hazards_grid_pos

    @staticmethod
    def build_minigrid(
        grid_size: tuple[int, int],
        grid_obj_default: Mobject,
        grid_obj_hazard: Mobject,
        grid_obj_goal: Mobject,
        grid_obj_player: Mobject,
        player_pos: tuple[int, int] | None = None, # Defaults to top-left.
        goal_pos: tuple[int, int] | None = None, # Defaults to bottom-right.
        hazards: list[tuple[int, int]] = [],
        ) -> dict:
        """Helper function to generate a MiniGrid environment.
        
        Returns a 2D matrix of Manim `VMobject`.
        """
        if player_pos == None: # Defaults to top-left.
            player_pos = (0,0)
        if goal_pos == None: # Defaults to bottom-right.
            goal_pos = (grid_size[0]-1, grid_size[1]-1)
        
        # Support for negative indexing.
        if any(i < 0 for i in player_pos):
            player_pos = tuple(negative_index_rollover(i, size) for i,size in zip(player_pos, grid_size))
        if any(i < 0 for i in goal_pos):
            goal_pos = tuple(negative_index_rollover(i, size) for i,size in zip(goal_pos, grid_size))
        if any(i < 0 for haz in hazards for i in haz):
            hazards = [tuple(negative_index_rollover(i, size) for i,size in zip(haz, grid_size)) for haz in hazards]

        # Build the grid.
        rows = []
        for r in range(grid_size[0]):
            cols = []
            for c in range(grid_size[1]):
                if (r,c) == goal_pos:
                    cols.append(grid_obj_goal.copy())
                elif (r,c) in hazards:
                    cols.append(grid_obj_hazard.copy())
                else:
                    cols.append(grid_obj_default.copy())
            rows.append(cols)
        
        grid = VGroup(*[o for o in itertools.chain(*rows)])
        grid.arrange_in_grid(rows=grid_size[0], cols=grid_size[1], buff=0)
        
        player = grid_obj_player.copy()
        player_target_pos = grid[player_pos[0]*grid_size[0] + player_pos[1]].get_center()
        player.move_to(player_target_pos)
        return {
            'player': player,
            'grid': grid,
        }

    @staticmethod
    def round_to_nearest_angle(angle: float) -> int:
        """Round angle to nearest [0, 90, 180, 270, 360].
        
        Supports negative angles.
        
        Examples:
        * 179 -> 180
        * 221 -> 180
        * 14 -> 0
        * 100 -> 90
        * -90 -> 270
        """
        angle = int(round(angle / 90) * 90) # Round to nearest [0, 90, 180, 270, 360].
        angle = angle % 360 # Convert to range [0, 359].
        return angle

    def move_player_forward(self):
        """Move player forward in the direction it is facing."""
        r, c = self.get_player_pos() # Converts coordinate to (row,col).
        player_look_angle = self.round_to_nearest_angle(self.world['player'].get_angle() * (180./PI)) # Get look angle in degrees.
        if player_look_angle % 360 == 0: # UP
            r -= 1
        elif player_look_angle == 90: # LEFT
            c -= 1
        elif player_look_angle == 180: # DOWN
            r += 1
        elif player_look_angle == 270: # RIGHT
            c += 1
        
        # Only move if does not exceed grid boundary.
        if (r >= 0 and r < self.grid_size[0]) and (c >= 0 and c < self.grid_size[1]):
            target_pos = self.world['grid'][r*self.grid_size[0] + c].get_center()
            self.world['player'].move_to(target_pos)
            
        return self

    def move_player_left(self):
        """Move player left."""
        turn_amount = +90
        self.world['player'].rotate(turn_amount*DEGREES)
        return self
    
    def move_player_right(self):
        """Move player right."""
        turn_amount = -90
        self.world['player'].rotate(turn_amount*DEGREES)
        return self

    def move_player(self, action: MinigridAction):
        """Moves player corresponding to an action, which is one of (LEFT, RIGHT, FORWARD)."""
        if action == MinigridAction.LEFT:
            return self.move_player_left()
        elif action == MinigridAction.RIGHT:
            return self.move_player_right()
        elif action == MinigridAction.FORWARD:
            return self.move_player_forward()
    
    @staticmethod
    def event_collision_hazard(grid: 'MiniGrid', shadow: 'MiniGrid', player_pos: tuple[int,int]) -> AnimationGroup:
        hazard = shadow.get_grid_at_pos(player_pos)
        return AnimationGroup(
            # Wiggle(grid.get_grid_at_pos(player_pos)),
            # Wiggle(grid.get_player()),
            CustomFlash(shadow.pos_to_coord(player_pos), flash_radius=hazard.width*.75, color=hazard.get_color()),
        )
    
    @staticmethod
    def event_collision_goal(grid: 'MiniGrid', shadow: 'MiniGrid', player_pos: tuple[int,int]) -> AnimationGroup:
        goal = shadow.get_goal()
        return AnimationGroup(
            # Wiggle(grid.get_grid_at_pos(player_pos)),
            # Wiggle(grid.get_player()),
            CustomFlash(shadow.pos_to_coord(player_pos), flash_radius=goal.width*.75, color=goal.get_color()),
        )
    
    def animate_actions(self,
        *actions: MinigridAction,
        func_event_collision_hazard = event_collision_hazard,
        func_event_collision_goal = event_collision_goal,
        **kwargs,
        ) -> Succession:
        """Animates a path of actions within the grid.
        """
        minigrid_shadow = self.copy() # Create a shadow of the grid to track positions across animations.
        anims = []
        for a in actions:
            anims.append(
                ApplyMethod(self.move_player, a)
            )
            minigrid_shadow.move_player(a) # Move the shadow too.
            player_pos = minigrid_shadow.get_player_pos()
            if player_pos in minigrid_shadow.get_hazards_pos():
                anim = func_event_collision_hazard(self, minigrid_shadow, player_pos)
                if anim is not None:
                    anims.append(anim)
            elif player_pos == minigrid_shadow.get_goal_pos():
                anim = func_event_collision_goal(self, minigrid_shadow, player_pos)
                if anim is not None:
                    anims.append(anim)
        del minigrid_shadow # Remove the shadow.
        return Succession(*anims, **kwargs)


class PausableScene(Scene):
    """Base scene that allows for easy pausing."""
    
    def small_pause(self, duration=0.5, **kwargs):
        self.wait(duration, **kwargs)
    
    def pause_pause(self, duration=1.5, **kwargs):
        self.wait(duration, **kwargs)

    def medium_pause(self, duration=3, **kwargs):
        self.wait(duration, **kwargs)
    
    def long_pause(self, duration=5, **kwargs):
        self.wait(duration, **kwargs)

class CustomVoiceoverScene(VoiceoverScene):
    def safe_wait(self, duration: float, **kwargs) -> None:
        """Waits for a given duration. If the duration is less than one frame, it waits for one frame.

        Args:
            duration (float): The duration to wait for in seconds.
        """
        if duration > 1 / config["frame_rate"]:
            self.wait(duration, **kwargs)
    
    def wait_until_bookmark(self, mark: str, **kwargs) -> None:
        """Waits until a bookmark is reached.

        Args:
            mark (str): The `mark` attribute of the bookmark to wait for.
        """
        self.safe_wait(self.current_tracker.time_until_bookmark(mark), **kwargs)
    
    def wait_for_voiceover(self, **kwargs) -> None:
        """Waits for the voiceover to finish."""
        if not hasattr(self, "current_tracker"):
            return
        if self.current_tracker is None:
            return

        self.safe_wait(self.current_tracker.get_remaining_duration(), **kwargs)
    
    @contextmanager
    def voiceover(
        self, text: Optional[str] = None, ssml: Optional[str] = None, wait_kwargs = {}, **kwargs
    ) -> Generator[VoiceoverTracker, None, None]:
        """The main function to be used for adding voiceover to a scene.

        Args:
            text (str, optional): The text to be spoken. Defaults to None.
            ssml (str, optional): The SSML to be spoken. Defaults to None.

        Yields:
            Generator[VoiceoverTracker, None, None]: The voiceover tracker object.
        """
        if text is None and ssml is None:
            raise ValueError("Please specify either a voiceover text or SSML string.")

        try:
            if text is not None:
                yield self.add_voiceover_text(text, **kwargs)
            elif ssml is not None:
                yield self.add_voiceover_ssml(ssml, **kwargs)
        finally:
            self.wait_for_voiceover(**wait_kwargs)

class DemoForICAB(PausableScene, CustomVoiceoverScene):
    def construct(self):
        # Configure AI text-to-speech service.
        # See Manim Voiceover quickstart for details: https://voiceover.manim.community/en/latest/quickstart.html
        self.set_speech_service(GTTSService(
            lang="en",
            tld="com",
            global_speed=1.15,
            transcription_model='base',
        ))
        # self.set_speech_service(CoquiService(
        #     global_speed=1.15,
        #     transcription_model='base',
        # ))
        
        # Colorway.
        self.colors = {
            'quantum': PURPLE,
            'observation': ORANGE,
            'action': BLUE,
            'no': RED,
            'wave-primary': GRAY_C,
            'wave-secondary': GRAY_D,
        }
        
        # Define the sections of the video.
        # Each section is a tuple of the form (name, method, kwargs).
        # The sections can be reordered here.
        # Objects can be reused between sections as long as they are not removed.
        # To reuse an object, simply save it to a variable using `self.<variable_name> = <object>`.
        # Each section should cleanup any objects after itself if they are not to be used again.
        # Sections can be tested individually, to do this set `skip_animations=True` to turn off all other sections not used (note that the section will still be generated, allowing objects to move to their final position for use with future sections in the pipeline).
        sections: list[tuple[Callable, dict]] = [
            (self.section_title, dict(name="Title", skip_animations=False)), # First.
            # (self.section_scenario, dict(name="Scenario", skip_animations=False)),
            # (self.section_experiment, dict(name="Experiment", skip_animations=False)),
            (self.section_summary, dict(name="Summary", skip_animations=False)),
            (self.section_outro, dict(name="Outro", skip_animations=False)), # Last.
        ]
        for method, section_kwargs in sections:
            self.next_section(**section_kwargs)
            print(f"{self.renderer._original_skipping_status=}")
            method()
        
        self.wait(1)
    
    def section_title(self):
        """Title section."""

        # Short title.
        eqmarl_acronym = Text("eQMARL", t2c={'Q': PURPLE}, font_size=72)
        eqmarl_acronym_glyphs = [
            eqmarl_acronym[0],
            eqmarl_acronym[1],
            eqmarl_acronym[2:4],
            eqmarl_acronym[4],
            eqmarl_acronym[5],
        ]
        self.eqmarl_acronym = eqmarl_acronym # Preserve the acronym for use outside of the section.
        self.eqmarl_acronym.shift(UP)

        # Long form of title.
        eqmarl_full = Text("Entangled Quantum Multi-Agent Reinforcement Learning", t2c={'Quantum': PURPLE}, font_size=36)
        eqmarl_full.next_to(eqmarl_acronym, DOWN, buff=0.5)
        eqmarl_full_glyphs = [
            eqmarl_full[0:9],
            eqmarl_full[9:16],
            eqmarl_full[16:27],
            eqmarl_full[27:40],
            eqmarl_full[40:],
        ]
        eqmarl_full.next_to(eqmarl_acronym, DOWN, buff=0.5)
        
        self.subtitle_text = MarkupText("<i>Coordination without Communication</i>", font_size=28)
        self.subtitle_text.next_to(eqmarl_full, DOWN, buff=0.5)
        
        # self.attribution_text_full = Text("Alexander DeRieux & Walid Saad", font_size=22)
        # self.attribution_text_full = Paragraph("Alexander DeRieux & Walid Saad\nPublished in ICLR 2025", font_size=22, alignment='center', line_spacing=0.7)
        self.attribution_text_full = VGroup(
            Text("Alexander DeRieux & Walid Saad", font_size=22),
            MarkupText("Published in <i>The Thirteenth International Conference on Learning Representations (ICLR)</i> 2025", font_size=20),
        ).arrange(DOWN, buff=0.2)
        self.attribution_text_full.next_to(self.subtitle_text, DOWN, buff=0.5)
        
        self.attribution_text = Text("A. DeRieux & W. Saad (2025)", font_size=12)
        self.attribution_text.to_edge(DOWN, buff=0.1)
        
        # Combine the glyphs.
        eqmarl_glyphs = list(zip(eqmarl_acronym_glyphs, eqmarl_full_glyphs))
        
        # Animate the title.
        with self.voiceover(
            text="""Welcome to our short video presentation for our <bookmark mark='1'/>recently published work titled eQMARL, which stands for <bookmark mark='2'/>Entangled Quantum Multi-Agent Reinforcement Learning.
            """
        ) as tracker:
            self.wait_until_bookmark('1', frozen_frame=False)
            self.play(FadeIn(eqmarl_acronym), run_time=tracker.time_until_bookmark('2'))
            # self.wait_until_bookmark('2')
            self.play(Write(eqmarl_full))
        
        with self.voiceover(
            text="""The key point of our work is that through quantum entanglement eQMARL enables swarms of AI agents to <bookmark mark='1'/>coordinate without direct communication.
            """
        ) as tracker:
            self.wait_until_bookmark('1', frozen_frame=False)
            self.play(Write(self.subtitle_text))

        with self.voiceover(
            text="""Our work has been published in The Thirteenth International Conference on Learning Representations.
            """
        ) as tracker:
            self.play(Write(self.attribution_text_full))
        
        self.small_pause(frozen_frame=False)
        
        self.play(FadeOut(eqmarl_full), FadeOut(self.subtitle_text), eqmarl_acronym.animate.scale(0.5).to_edge(UL), ReplacementTransform(self.attribution_text_full, self.attribution_text))

    def section_scenario(self):
        # Objects with labels.
        objs = {}
        # Environments.
        objs['env-left'] = MObjectWithLabel(
            obj=ImageMobject("assets/images/wildfire-2.png").scale(0.3),
            label=Text("Environment A", font_size=18),
            buff=0.2,
            direction=DOWN,
        ).to_edge(DOWN).to_edge(LEFT, buff=1)
        objs['env-right'] = MObjectWithLabel(
            obj=ImageMobject("assets/images/wildfire.png").scale(0.3),
            label=Text("Environment B", font_size=18),
            buff=0.2,
            direction=DOWN,
        ).to_edge(DOWN).to_edge(RIGHT, buff=1)
        # Drones.
        objs['drone-left'] = MObjectWithLabel(
            obj=ImageMobject("assets/images/quadcopter.png").scale(0.4),
            label=Text("Drone A", font_size=18),
            buff=-0.1,
            direction=UP,
        ).next_to(objs['env-left'], UP, buff=1.75)
        objs['drone-right'] = MObjectWithLabel(
            obj=ImageMobject("assets/images/quadcopter.png").scale(0.4),
            label=Text("Drone B", font_size=18),
            buff=-0.1,
            direction=UP,
        ).next_to(objs['env-right'], UP, buff=1.75)
        # Obstacle.
        objs['obstacle'] = MObjectWithLabel(
            obj=ImageMobject("assets/images/mountain-3.png").scale(1.2),
            label=Text("Environment Obstruction", font_size=18),
            buff=0.2,
            direction=DOWN,
        ).to_edge(DOWN)
        objs['nocom-left'] = MObjectWithLabel(
            obj=ImageMobject("assets/images/no-speak.png").scale(0.15).next_to(objs['drone-left'].obj, RIGHT*8),
            label=Text("Blocked P2P", font_size=18),
            buff=0.1,
            direction=UP,
        ) #.next_to(objs['drone-left'].obj, RIGHT*8)
        objs['nocom-right'] = MObjectWithLabel(
            obj=ImageMobject("assets/images/no-speak.png").scale(0.15).next_to(objs['drone-right'].obj, LEFT*8),
            label=Text("Blocked P2P", font_size=18),
            buff=0.1,
            direction=UP,
        ) #.next_to(objs['drone-right'].obj, LEFT*8)
        # Qubits.
        objs['qubit-left'] = MObjectWithLabel(
            obj=Qubit(has_text=False, circle_color=self.colors['quantum'], ellipse_color=self.colors['quantum']).scale(0.25),
            label=Text("Qubit A", font_size=18),
            buff=0.1,
            direction=UP,
        ).to_edge(UP, buff=1.75).shift(LEFT*.75)
        objs['qubit-right'] = MObjectWithLabel(
            obj=Qubit(has_text=False, circle_color=self.colors['quantum'], ellipse_color=self.colors['quantum']).scale(0.25),
            label=Text("Qubit B", font_size=18),
            buff=0.1,
            direction=UP,
        ).to_edge(UP, buff=1.75).shift(RIGHT*.75)
        
        # Trackers.
        trackers: dict[str, ValueTracker] = {}
        trackers['amp-0'] = ValueTracker(0.1)
        trackers['freq-0'] = ValueTracker(2*PI)
        
        # Waves.
        waves: dict[str, VGroup] = {}
        waves['ent-0'] = VGroup(*[
            always_redraw(
                lambda: FunctionGraph(
                    lambda x: trackers['amp-0'].get_value()*np.sin(trackers['freq-0'].get_value()*x + self.time),
                    x_range=[-1, 1],
                    color=self.colors['wave-primary'],
                ).stretch_to_fit_width(abs(objs['qubit-left'].obj.get_x(RIGHT) - objs['qubit-right'].obj.get_x(LEFT))).next_to(objs['qubit-left'].obj, RIGHT, buff=0)
            ),
            always_redraw(
                lambda: FunctionGraph(
                    lambda x: trackers['amp-0'].get_value()*np.sin(trackers['freq-0'].get_value()*x + self.time + PI),
                    x_range=[-1, 1],
                    color=self.colors['wave-secondary'],
                ).stretch_to_fit_width(abs(objs['qubit-left'].obj.get_x(RIGHT) - objs['qubit-right'].obj.get_x(LEFT))).next_to(objs['qubit-left'].obj, RIGHT, buff=0)
            ),
        ])
        
        # Arrows between the drones.
        arrows = {}
        # Ideal communication arrows.
        arrows['ideal-com-lr'] = DashedVMobject(Arrow(
            start=objs['drone-left'].obj.get_right(),
            end=objs['drone-right'].obj.get_left(),
            stroke_width=2,
            tip_length=.2,
            buff=0.4,
        )).shift(UP*.2)
        arrows['ideal-com-rl'] = DashedVMobject(Arrow(
            start=objs['drone-right'].obj.get_left(),
            end=objs['drone-left'].obj.get_right(),
            stroke_width=2,
            tip_length=.2,
            buff=0.4,
        )).shift(DOWN*.2)
        # No communication arrows.
        arrows['no-com-lr'] = Arrow(
            start=objs['drone-left'].obj.get_right(),
            end=objs['nocom-left'].obj.get_left(),
            stroke_width=2,
            tip_length=.2,
            buff=0.2,
            color=self.colors['no'],
        )
        arrows['no-com-rl'] = Arrow(
            start=objs['drone-right'].obj.get_left(),
            end=objs['nocom-right'].obj.get_right(),
            stroke_width=2,
            tip_length=.2,
            buff=0.2,
            color=self.colors['no'],
        )
        # Environment observation/action arrows.
        arrows['env-left-down'] = VMObjectWithLabel(
            obj=DashedVMobject(Arrow(
                start=objs['drone-left'].obj.get_bottom(),
                end=objs['env-left'].obj.get_top(),
                stroke_width=2,
                tip_length=.2,
                buff=0.1,
                color=self.colors['action'],
            )),
            label=Text("Actions", font_size=18, color=self.colors['action']),
            direction=LEFT,
        ).shift(LEFT*.2)
        arrows['env-left-up'] = VMObjectWithLabel(
            obj=DashedVMobject(Arrow(
                start=objs['env-left'].obj.get_top(),
                end=objs['drone-left'].obj.get_bottom(),
                stroke_width=2,
                tip_length=.2,
                buff=0.1,
                color=self.colors['observation'],
            )),
            label=Text("Experiences", font_size=18, color=self.colors['observation']),
            direction=RIGHT,
        ).shift(RIGHT*.2)
        arrows['env-right-down'] = VMObjectWithLabel(
            obj=DashedVMobject(Arrow(
                start=objs['drone-right'].obj.get_bottom(),
                end=objs['env-right'].obj.get_top(),
                stroke_width=2,
                tip_length=.2,
                buff=0.1,
                color=self.colors['action'],
            )),
            label=Text("Actions", font_size=18, color=self.colors['action']),
            direction=RIGHT,
        ).shift(RIGHT*.2)
        arrows['env-right-up'] = VMObjectWithLabel(
            obj=DashedVMobject(Arrow(
                start=objs['env-right'].obj.get_top(),
                end=objs['drone-right'].obj.get_bottom(),
                stroke_width=2,
                tip_length=.2,
                buff=0.1,
                color=self.colors['observation'],
            )),
            label=Text("Experiences", font_size=18, color=self.colors['observation']),
            direction=LEFT,
        ).shift(LEFT*.2)
        
        # Text objects.
        texts = {}
        # texts['imagine-0'] = Text("Imagine two separate wildfire environments", font_size=32).to_edge(UP, buff=1)
        texts['imagine-0'] = MarkupText(f'Imagine two separate <span fgcolor="{self.colors["observation"].to_hex()}">wildfire environments</span>', font_size=32).to_edge(UP, buff=1)
        # texts['imagine-1'] = Text("and two AI-powered drones", font_size=32).to_edge(UP, buff=1)
        # texts['imagine-1'] = Text("and two AI-powered drones", font_size=32).next_to(texts['imagine-0'], DOWN)
        texts['imagine-1'] = MarkupText(f'and two <span fgcolor="{PINK.to_hex()}">AI-powered drones</span>', font_size=32).next_to(texts['imagine-0'], DOWN)
        # texts['imagine-2'] = Paragraph("The drones are tasked with\nextinguishing the environment fires", font_size=32, alignment='center').to_edge(UP, buff=1.5)
        texts['imagine-2'] = MarkupText(f'tasked with <span fgcolor="{self.colors["action"].to_hex()}">extinguishing</span> the environment fires', font_size=32).next_to(texts['imagine-1'], DOWN)
        texts['ideal-0'] = MarkupText(f"In an <u>ideal</u> scenario", font_size=32).to_edge(UP, buff=1)
        # texts['ideal-1'] = Text("The drones could learn the task faster", font_size=24).next_to(arrows['ideal-com-lr'], UP)
        # texts['ideal-2'] = MarkupText(f"by cooperatively sharing their <span fgcolor=\"{self.colors['observation'].to_hex()}\">experiences</span>", font_size=24).next_to(arrows['ideal-com-rl'], DOWN)
        texts['ideal-1'] = MarkupText(f"The drones can learn the task more efficiently", font_size=24).next_to(arrows['ideal-com-lr'], UP)
        texts['ideal-2'] = MarkupText(f"by cooperatively sharing their <span fgcolor=\"{self.colors['observation'].to_hex()}\">experiences</span>", font_size=24).next_to(arrows['ideal-com-rl'], DOWN)
        ####
        texts['nocom-0'] = Text("But in certain environment conditions", font_size=32).to_edge(UP, buff=1)
        texts['nocom-1'] = MarkupText(f"this sharing of <span fgcolor=\"{self.colors['observation'].to_hex()}\">local information</span> is <span fgcolor=\"{self.colors['no'].to_hex()}\">not possible</span>", font_size=32).next_to(texts['nocom-0'], DOWN) # to_edge(UP, buff=2) # Below above.
        texts['quantum-0'] = Text("However...", font_size=32).to_edge(UP, buff=1)
        texts['quantum-1'] = MarkupText(f"using <span fgcolor=\"{self.colors['quantum'].to_hex()}\">Quantum Entanglement</span>", font_size=32).to_edge(UP, buff=1) # .next_to(texts['quantum-0'], RIGHT)
        texts['quantum-2'] = Text("between the drones", font_size=32).next_to(texts['quantum-1'], DOWN)
        texts['quantum-3'] = MarkupText(f"The drones can use their <span fgcolor=\"{self.colors['observation'].to_hex()}\">local experiences</span>", font_size=32).to_edge(UP, buff=1)
        texts['quantum-4'] = MarkupText(f"to influence the <span fgcolor=\"{self.colors['action'].to_hex()}\">actions</span> of others", font_size=32).next_to(texts['quantum-3'], DOWN)
        texts['quantum-5'] = MarkupText(f"without <b><span fgcolor=\"{self.colors['no'].to_hex()}\">direct communication</span></b>", font_size=32).next_to(texts['quantum-4'], DOWN)
        texts['quantum-6'] = MarkupText(f"<span fgcolor=\"{self.colors['quantum'].to_hex()}\">Quantum Entangled Learning</span>", font_size=32).to_edge(UP, buff=1)
        texts['quantum-7'] = MarkupText(f"<span fgcolor=\"{self.colors['action'].to_hex()}\">Coordination</span> <u>without</u> <span fgcolor=\"{RED.to_hex()}\">Communication</span>", font_size=28).next_to(texts['quantum-6'], DOWN)
        
        
        # Image of rain drops for drone action.
        objs['rain-left'] = ImageMobject("assets/images/rain-drops.png").scale(0.25).next_to(objs['drone-left'], DOWN, buff=-0.2).rotate(30*DEGREES)
        objs['rain-right'] = ImageMobject("assets/images/rain-drops.png").scale(0.25).next_to(objs['drone-right'], DOWN, buff=-0.2).rotate(30*DEGREES)
        
        
        
        # Imagine.
        with self.voiceover(
            text="""Imagine a scenario with two isolated <bookmark mark='1'/> wildfire environments,
            and <bookmark mark='2'/> two AI-powered drones <bookmark mark='3'/> tasked with <bookmark mark='4'/> extinguishing the fires in each environment.
            """
        ) as tracker:
            self.play(Write(texts['imagine-0']), run_time=tracker.time_until_bookmark('1', limit=1))
            self.play(FadeIn(objs['env-left']), FadeIn(objs['env-right']), run_time=tracker.time_until_bookmark('2', limit=1))
            self.wait_until_bookmark('2', frozen_frame=False)
            # self.play(Write(texts['imagine-1']))
            self.play(Write(texts['imagine-1']), FadeIn(objs['drone-left']), FadeIn(objs['drone-right']), run_time=tracker.time_until_bookmark('3', limit=1))
            
            self.wait_until_bookmark('3', frozen_frame=False)
            self.play(Write(texts['imagine-2']))
        
            # Animate the rain drops.
            self.wait_until_bookmark('4', frozen_frame=False)
            n = 3
            for i in range(n):
                objs['rain-left'].save_state()
                objs['rain-right'].save_state()
                self.play(
                    objs['rain-left'].animate.move_to(objs['env-left'].get_center()).set_opacity(0),
                    objs['rain-right'].animate.move_to(objs['env-right'].get_center()).set_opacity(0),
                )
                if i < n-1: # Do not restore last iteraiton.
                    objs['rain-left'].restore()
                    objs['rain-right'].restore()
                
            self.small_pause(frozen_frame=False)
            self.play(*[FadeOut(o) for k,o in texts.items() if 'imagine' in k])
        
        # Ideal.
        with self.voiceover(text="In an ideal scenario") as tracker:
            self.play(
                Write(texts['ideal-0']),
                Write(arrows['env-left-up']),
                Write(arrows['env-left-down']),
                Write(arrows['env-right-up']),
                Write(arrows['env-right-down']),
            )
        with self.voiceover(text="the drones can learn the task more efficiently") as tracker:
            self.play(Write(texts['ideal-1']), Write(arrows['ideal-com-lr']))
        with self.voiceover(text="by cooperatively sharing their unique local experiences.") as tracker:
            self.play(FadeIn(texts['ideal-2']), Write(arrows['ideal-com-rl']))

        self.small_pause(frozen_frame=False)
        self.play(FadeOut(texts['ideal-0']), FadeOut(texts['ideal-1']), FadeOut(arrows['ideal-com-lr']), FadeOut(texts['ideal-2']), FadeOut(arrows['ideal-com-rl']))
        
        # No communication.
        with self.voiceover(text="But in certain environment conditions, <bookmark mark='1'/> such as a mountain between the drones") as tracker:
            self.play(Write(texts['nocom-0']))
            self.wait_until_bookmark('1', frozen_frame=False)
            self.play(FadeIn(objs['obstacle']))
            
        with self.voiceover(text="This sharing of local information is not possible") as tracker:
            self.play(
                Write(texts['nocom-1']),
            )
            self.play(
                FadeIn(objs['nocom-left']),
                FadeIn(objs['nocom-right']),
                Write(arrows['no-com-lr']),
                Write(arrows['no-com-rl']),
            )
        # self.medium_pause(frozen_frame=False)
        self.small_pause(frozen_frame=False)
        self.play(
            FadeOut(texts['nocom-0']),
            FadeOut(texts['nocom-1']),
            FadeOut(objs['nocom-left']),
            FadeOut(objs['nocom-right']),
            FadeOut(arrows['no-com-lr']),
            FadeOut(arrows['no-com-rl']),
        )
        self.play(
            FadeOut(arrows['env-left-up']),
            FadeOut(arrows['env-left-down']),
            FadeOut(arrows['env-right-up']),
            FadeOut(arrows['env-right-down']),
        )
        self.small_pause(frozen_frame=False)
        
        # Quantum.
        with self.voiceover(text="However") as tracker:
            self.play(Write(texts['quantum-0']))
        # self.wait(1)
        with self.voiceover(text="By exploiting the nature of quantum entanglment distributed between the drones, the drones are able to implicitly collaborate regardless of any obstacles.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(ReplacementTransform(texts['quantum-0'], texts['quantum-1']))
            self.play(FadeIn(objs['qubit-left']), FadeIn(objs['qubit-right']), Write(waves['ent-0']))
            # self.play(Write(waves['ent-0']))
            objs['obstacle'].set_z_index(1) # On top.
            # self.small_pause(frozen_frame=False)
            # self.safe_wait(1)
            self.play(
                Write(texts['quantum-2']),
                trackers['amp-0'].animate.set_value(.2),
                trackers['freq-0'].animate.set_value(4*PI),
                objs['qubit-left'].animate.next_to(objs['drone-left'], RIGHT),
                objs['qubit-right'].animate.next_to(objs['drone-right'], LEFT),
                # run_time=tracker.get_remaining_duration(),
            )

        with self.voiceover(text="This means that, using quantum entanglement, <bookmark mark='1'/> the drones can use their unique local experiences <bookmark mark='2'/> to influence the actions of others <bookmark mark='3'/> without the need for direct communication.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.wait_until_bookmark('1', frozen_frame=False)
            self.play(FadeOut(texts['quantum-2']), ReplacementTransform(texts['quantum-1'], texts['quantum-3']))
            arrows['env-left-up'].shift(LEFT*.2) # Move to center.
            arrows['env-right-down'].shift(LEFT*.2) # Move to center.
            self.play(
                Write(arrows['env-left-up']),
            )
            self.wait_until_bookmark('2', frozen_frame=False)
            self.play(Write(texts['quantum-4']))
            self.play(
                Write(arrows['env-right-down']),
            )
            self.wait_until_bookmark('3', frozen_frame=False)
            self.play(Write(texts['quantum-5']))
        # self.medium_pause(frozen_frame=False)
        self.small_pause(frozen_frame=False)
        
        
        # Lasting point before section change.
        with self.voiceover(text="This is the essence of our work. Using quantum entanglement to facilitate multi-agent learning via <bookmark mark='1'/> implicit coordination without direct communication.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(ReplacementTransform(VGroup(texts['quantum-3'], texts['quantum-4'], texts['quantum-5']), texts['quantum-6']))
            self.wait_until_bookmark('1', frozen_frame=False)
            self.play(Write(texts['quantum-7']))
            self.play(arrows['env-left-up'].obj.animate.set_color(YELLOW).set_stroke(width=12, opacity=0.5), rate_func=there_and_back)
            self.play(
                Wiggle(objs['qubit-left']),
                Wiggle(objs['qubit-right']),
                rate_func=linear,
            )
            self.play(arrows['env-right-down'].obj.animate.set_color(YELLOW).set_stroke(width=12, opacity=0.5), rate_func=there_and_back)
        # self.medium_pause(frozen_frame=False)
        self.small_pause(frozen_frame=False)

        # Clear the screen of all objects created in this section.
        mobjects_in_scene = list(set(self.mobjects) - set([self.eqmarl_acronym, self.attribution_text]))
        self.play(
            *[FadeOut(o) for o in mobjects_in_scene]
        )

    def section_experiment(self):
        objs = {}
        
        # Text objects.
        objs['text-exp-0'] = Text("Let's see an illustrative example", font_size=32)
        objs['text-exp-1'] = Tex(r"This is an $5\times5$ maze grid environment for 1 drone", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-2'] = Tex(r"The drone can take actions $a \in \{\textrm{left}, \textrm{right}, \textrm{forward}\}$ to move in the maze", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-3'] = Text("As the drone moves it gathers experiences", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-4'] = Text("The drone learns from experiences to find the goal", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-5'] = Text("Now consider 2 parallel environments with different drones", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-6'] = Text("The drones cannot directly communicate with each other", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-7'] = Text("Which means they cannot coordinate using shared experiences", font_size=32).to_edge(UP, buff=1.5)
        # objs['text-exp-7-1'] = Text("Which means they cannot coordinate using shared experiences", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-8'] = MarkupText(f"<span fgcolor=\"{self.colors['quantum'].to_hex()}\">Quantum entanglement</span> between the drones", font_size=32).to_edge(UP, buff=1.2)
        objs['text-exp-9'] = MarkupText(f"couples their <span fgcolor=\"{self.colors['observation']}\">unique local experiences</span>", font_size=32).next_to(objs['text-exp-8'], DOWN)
        objs['text-exp-10'] = MarkupText(f"allowing them to learn optimal <span fgcolor=\"{self.colors['action']}\">actions</span> <u>without</u> <span fgcolor=\"{self.colors['no']}\">direct communication</span>", font_size=32).next_to(objs['text-exp-9'], DOWN)
        
        # MiniGrids.
        # Big center.
        objs['grid-big-center'] = MiniGrid(
            grid_size=(5,5),
            hazards_grid_pos=[
                (1,1),
                (1,2),
                (1,3),
            ],
            goal_grid_pos=(-1,-1),
        ).scale(0.5).to_edge(DOWN, buff=0.5)
        # MiniGrid legend for big grid.
        objs['grid-big-legend'] = Group(*[
            MObjectWithLabel(
                obj=objs['grid-big-center'].assets['player'].copy().scale(0.25),
                label=Text("Drone", font_size=18),
                buff=0.2,
                direction=RIGHT,
            ),
            MObjectWithLabel(
                obj=objs['grid-big-center'].assets['grid-empty'].copy().scale(0.25),
                label=Text("Safe grid square", font_size=18),
                buff=0.2,
                direction=RIGHT,
            ),
            MObjectWithLabel(
                obj=objs['grid-big-center'].assets['grid-lava'].copy().scale(0.25),
                label=Text("Lava hazard", font_size=18),
                buff=0.2,
                direction=RIGHT,
            ),
            MObjectWithLabel(
                obj=objs['grid-big-center'].assets['grid-goal'].copy().scale(0.25),
                label=Text("Goal", font_size=18),
                buff=0.2,
                direction=RIGHT,
            ),
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.5).next_to(objs['grid-big-center'], RIGHT)
        # Big left.
        objs['grid-big-left'] = MObjectWithLabel(
            obj=MiniGrid(
                grid_size=(5,5),
                hazards_grid_pos=[
                    (1,1),
                    (1,2),
                    (1,3),
                ],
                goal_grid_pos=(-1,-1),
            ).scale(0.5),
            label=Text("Environment A", font_size=18),
            buff=0.1,
            direction=DOWN,
        ).to_edge(DOWN, buff=0.5).shift(LEFT*3)
        # Big right.
        objs['grid-big-right'] = MObjectWithLabel(
            obj=MiniGrid(
                grid_size=(5,5),
                hazards_grid_pos=[
                    (1,1),
                    (2,1),
                    (3,1),
                ],
                goal_grid_pos=(-1,-1),
            ).scale(0.5),
            label=Text("Environment B", font_size=18),
            buff=0.1,
            direction=DOWN,
        ).to_edge(DOWN, buff=0.5).shift(RIGHT*3)
        # Small left.
        objs['grid-small-left'] = objs['grid-big-left'].copy().scale(0.75).shift(LEFT).to_edge(DOWN, buff=0.5)
        objs['grid-small-left'].label.scale(1./0.75) # Undo scaling of text size.
        # Small right.
        objs['grid-small-right'] = objs['grid-big-right'].copy().scale(0.75).shift(RIGHT).to_edge(DOWN, buff=0.5)
        objs['grid-small-right'].label.scale(1./0.75) # Undo scaling of text size.
        # Small up.
        objs['grid-small-up'] = MObjectWithLabel(
            obj=MiniGrid(
                grid_size=(5,5),
                hazards_grid_pos=[
                    (1,1),
                    (1,2),
                    (1,3),
                ],
                goal_grid_pos=(-1,-1),
            ).scale(0.2),
            label=Text("Env. A", font_size=18),
            buff=0.1,
            direction=LEFT,
        ).to_edge(LEFT, buff=0.5).shift(UP*1.5)
        # Small down.
        objs['grid-small-down'] = MObjectWithLabel(
            obj=MiniGrid(
                grid_size=(5,5),
                hazards_grid_pos=[
                    (1,1),
                    (2,1),
                    (3,1),
                ],
                goal_grid_pos=(-1,-1),
            ).scale(0.2),
            label=Text("Env. B", font_size=18),
            buff=0.1,
            direction=LEFT,
        ).to_edge(LEFT, buff=0.5).to_edge(DOWN, buff=0.5)
        objs['group-grid-small-up/down'] = Group(objs['grid-small-up'], objs['grid-small-down'])
        
        # Qubits.
        objs['qubit-left'] = MObjectWithLabel(
            obj=Qubit(has_text=False, circle_color=self.colors['quantum'], ellipse_color=self.colors['quantum']).scale(0.4),
            label=Text("Qubit A", font_size=18),
            buff=0.1,
            direction=UP,
        ).next_to(objs['grid-small-left'].obj, RIGHT)
        objs['qubit-right'] = MObjectWithLabel(
            obj=Qubit(has_text=False, circle_color=self.colors['quantum'], ellipse_color=self.colors['quantum']).scale(0.4),
            label=Text("Qubit B", font_size=18),
            buff=0.1,
            direction=UP,
        ).next_to(objs['grid-small-right'].obj, LEFT)
        objs['qubit-up'] = MObjectWithLabel(
            obj=Qubit(has_text=False, circle_color=self.colors['quantum'], ellipse_color=self.colors['quantum']).scale(0.2),
            label=Text("Qubit A", font_size=18),
            buff=0.1,
            direction=LEFT,
        ).next_to(objs['grid-small-up'], DOWN)
        objs['qubit-down'] = MObjectWithLabel(
            obj=Qubit(has_text=False, circle_color=self.colors['quantum'], ellipse_color=self.colors['quantum']).scale(0.2),
            label=Text("Qubit B", font_size=18),
            buff=0.1,
            direction=LEFT,
        ).next_to(objs['grid-small-down'], UP)
        
        # Trackers.
        objs['tracker-amp-0'] = ValueTracker(0.2)
        objs['tracker-freq-0'] = ValueTracker(2*PI)
        
        # Waves.
        # Left/Right.
        objs['wave-leftright'] = VGroup(*[
            always_redraw(
                lambda: FunctionGraph(
                    lambda x: objs['tracker-amp-0'].get_value()*np.sin(objs['tracker-freq-0'].get_value()*x + self.time),
                    x_range=[-1, 1],
                    color=self.colors['wave-primary'],
                ).stretch_to_fit_width(abs(objs['qubit-left'].obj.get_x(RIGHT) - objs['qubit-right'].obj.get_x(LEFT))).next_to(objs['qubit-left'].obj, RIGHT, buff=0)
            ),
            always_redraw(
                lambda: FunctionGraph(
                    lambda x: objs['tracker-amp-0'].get_value()*np.sin(objs['tracker-freq-0'].get_value()*x - self.time + PI),
                    x_range=[-1, 1],
                    color=self.colors['wave-secondary'],
                ).stretch_to_fit_width(abs(objs['qubit-left'].obj.get_x(RIGHT) - objs['qubit-right'].obj.get_x(LEFT))).next_to(objs['qubit-left'].obj, RIGHT, buff=0)
            ),
        ])
        # Up/Down.
        objs['wave-updown'] = VGroup(*[
            always_redraw(
                lambda: FunctionGraph(
                    lambda x: objs['tracker-amp-0'].get_value()*np.sin(objs['tracker-freq-0'].get_value()*x + self.time),
                    x_range=[-1, 1],
                    color=self.colors['wave-primary'],
                ).stretch_to_fit_width(abs(objs['qubit-up'].obj.get_y(DOWN) - objs['qubit-down'].obj.get_y(UP))).rotate(90*DEGREES).next_to(objs['qubit-up'].obj, DOWN, buff=0)
            ),
            always_redraw(
                lambda: FunctionGraph(
                    lambda x: objs['tracker-amp-0'].get_value()*np.sin(objs['tracker-freq-0'].get_value()*x - self.time + PI),
                    x_range=[-1, 1],
                    color=self.colors['wave-secondary'],
                ).stretch_to_fit_width(abs(objs['qubit-up'].obj.get_y(DOWN) - objs['qubit-down'].obj.get_y(UP))).rotate(90*DEGREES).next_to(objs['qubit-up'].obj, DOWN, buff=0)
            ),
        ])
        
        
        ###
        # Animations.
        ###
        with self.voiceover(text="With this in mind, let's dive deeper through an illustrative example.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(Write(objs['text-exp-0'])) # Let's see example.
        
        self.small_pause(frozen_frame=False)
        
        # return
        
        with self.voiceover(text="This is a five-by-five maze environment for a <bookmark mark='1'/> drone, consisting of <bookmark mark='2'/> safe grid squares, <bookmark mark='3'/> lava hazards, <bookmark mark='4'/> and a goal.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(ReplacementTransform(objs['text-exp-0'], objs['text-exp-1'])) # This is a grid.
            self.play(FadeIn(objs['grid-big-center'])) # Show big grid in center.
            for i, m in enumerate(objs['grid-big-legend']): # Show the legend elements.
                self.wait_until_bookmark(str(i+1), frozen_frame=False)
                self.play(FadeIn(m))
        
        with self.voiceover(text="The drone can move through the maze by taking actions left, right, and forward.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(ReplacementTransform(objs['text-exp-1'], objs['text-exp-2'])) # Player actions.
            self.play(
                objs['grid-big-center'].animate_actions(*minigrid_path_str_to_list('fff')),
                run_time=2,
            )

        with self.voiceover(text="As the drone moves it gathers experiences.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(ReplacementTransform(objs['text-exp-2'], objs['text-exp-3'])) # Gains experiences.
            self.play(
                objs['grid-big-center'].animate_actions(*minigrid_path_str_to_list('frf')),
                run_time=2,
            )
        
        with self.voiceover(text="And the drone learns from these experiences to find the goal.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(ReplacementTransform(objs['text-exp-3'], objs['text-exp-4'])) # To find the goal.
            self.play(
                objs['grid-big-center'].animate_actions(*minigrid_path_str_to_list('fff')),
                run_time=2,
            )
        self.play(FadeOut(objs['grid-big-legend']), FadeOut(objs['text-exp-4']), FadeOut(objs['grid-big-center']))
        
        # Show two grids.
        with self.voiceover(text="Now let's consider an extension of this scenario with two parallel maze environments with different drones in each.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(Write(objs['text-exp-5'])) # Now consider 2 environments.
            self.play(
                GrowFromCenter(objs['grid-big-left']),
                GrowFromCenter(objs['grid-big-right']),
            )
        orig_left = objs['grid-big-left'].copy()
        orig_right = objs['grid-big-right'].copy()
        with self.voiceover(text="The drones are not able to directly communicate with each other, due to the gap between them.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(ReplacementTransform(objs['text-exp-5'], objs['text-exp-6'])) # Cannot communicate.
            self.play(
                objs['grid-big-left'].obj.animate_actions(*minigrid_path_str_to_list('fff')),
                objs['grid-big-right'].obj.animate_actions(*minigrid_path_str_to_list('rff')),
                run_time=2,
            )
        with self.voiceover(text="From a learning perspective, this means that they are not able to coordinate using shared experiences. This is a problem because, we see that drone A fell into the lava, and the information it learned could be helpful for drone B to learn to avoid the hazard, but the lack of direct communication means that drone B will not know what happened and must experience the hazard itself.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(ReplacementTransform(objs['text-exp-6'], objs['text-exp-7'])) # Cannot coordinate.
            # self.play(
            #     objs['grid-big-left'].obj.animate_actions(*minigrid_path_str_to_list('rf')),
            #     objs['grid-big-right'].obj.animate_actions(*minigrid_path_str_to_list('fl')),
            #     run_time=2,
            # )
            path_left = 'rf' # Short abbreviated path.
            path_right = 'fl' # Short abbreviated path.
            while tracker.get_remaining_duration() > 0:
                self.play(
                    objs['grid-big-left'].obj.animate_actions(*minigrid_path_str_to_list(path_left)),
                    objs['grid-big-right'].obj.animate_actions(*minigrid_path_str_to_list(path_right)),
                    run_time=2,
                )
                if tracker.get_remaining_duration() > 0:
                    self.play(
                        ReplacementTransform(objs['grid-big-left'], orig_left),
                        ReplacementTransform(objs['grid-big-right'], orig_right),
                    )
                    objs['grid-big-left'] = orig_left
                    objs['grid-big-right'] = orig_right
                    orig_left = objs['grid-big-left'].copy()
                    orig_right = objs['grid-big-right'].copy()
                    path_left = 'fffrf' # Full path.
                    path_right = 'rfffl' # Full path.
        
        with self.voiceover(text="On the other hand, quantum entanglement can bridge the gap between the drones.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(
                ReplacementTransform(objs['grid-big-left'], objs['grid-small-left']),
                ReplacementTransform(objs['grid-big-right'], objs['grid-small-right']),
            )
            self.play(ReplacementTransform(objs['text-exp-7'], objs['text-exp-8'])) # Using quantum.
            self.play(
                FadeIn(objs['qubit-left']),
                FadeIn(objs['qubit-right']),
                FadeIn(objs['wave-leftright']),
            )
        orig_left = objs['grid-small-left'].copy()
        orig_right = objs['grid-small-right'].copy()
        with self.voiceover(text="In effect, coupling their unique local experiences.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(Write(objs['text-exp-9']))
            self.play(
                objs['grid-small-left'].obj.animate_actions(*minigrid_path_str_to_list('rffl')),
                objs['grid-small-right'].obj.animate_actions(*minigrid_path_str_to_list('ffr')),
                run_time=2,
            )
        with self.voiceover(text="Which allows them to learn optimal actions without the need for direct communication. As you can see from this example, the drones did not fall into the lava because their choice of actions was influenced by both their own local experiences and the implicit experience of the other drone via quantum entanglement.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(Write(objs['text-exp-10']))
            path_left = 'ffffrff' # Short abbreviated path.
            path_right = 'fffflff' # Short abbreviated path.
            while tracker.get_remaining_duration() > 0:
                self.play(
                    objs['grid-small-left'].obj.animate_actions(*minigrid_path_str_to_list(path_left)),
                    objs['grid-small-right'].obj.animate_actions(*minigrid_path_str_to_list(path_right)),
                    run_time=2,
                )
                if tracker.get_remaining_duration() > 0:
                    self.play(
                        ReplacementTransform(objs['grid-small-left'], orig_left),
                        ReplacementTransform(objs['grid-small-right'], orig_right),
                    )
                    objs['grid-small-left'] = orig_left
                    objs['grid-small-right'] = orig_right
                    orig_left = objs['grid-small-left'].copy()
                    orig_right = objs['grid-small-right'].copy()
                    path_left = 'rfflffffrff' # Full path.
                    path_right = 'ffrfffflff' # Full path.
            # self.play(
            #     objs['grid-small-left'].obj.animate_actions(*minigrid_path_str_to_list('ffffrff')),
            #     objs['grid-small-right'].obj.animate_actions(*minigrid_path_str_to_list('fffflff')),
            #     run_time=2,
            # )
        
        self.play(
            FadeOut(objs['text-exp-8']),
            FadeOut(objs['text-exp-9']),
            FadeOut(objs['text-exp-10']),
        )
        self.play(
            objs['tracker-amp-0'].animate.set_value(0.1), # Make wave amplitudes smaller.
            ReplacementTransform(objs['grid-small-left'], objs['grid-small-up']),
            ReplacementTransform(objs['grid-small-right'], objs['grid-small-down']),
            ReplacementTransform(objs['qubit-left'], objs['qubit-up']),
            ReplacementTransform(objs['qubit-right'], objs['qubit-down']),
            ReplacementTransform(objs['wave-leftright'], objs['wave-updown']),
        )
        
        ###
        # Result graphs.
        ###
        
        # Data to display.
        series: list[dict] = [
            dict(
                key='fctde',
                label='No Quantum',
                blob='experiment_output/coingame_maa2c_mdp_fctde/20240501T185443/metrics-[0-9].json',
                # color=[0.8666666666666667,0.5176470588235295,0.3215686274509804],
                color=ORANGE.to_rgb(),
                zorder=1,
            ),
            dict(
                key='qfctde',
                label='No Entanglement',
                blob='experiment_output/coingame_maa2c_mdp_qfctde/20240503T151226/metrics-[0-9].json',
                # color=[0.8549019607843137, 0.5450980392156862, 0.7647058823529411],
                color=PINK.to_rgb(),
                zorder=2,
            ),
            # dict(
            #     key='sctde',
            #     blob='experiment_output/coingame_maa2c_mdp_sctde/20240418T133421/metrics-[0-9].json',
            #     # color=[0.3333333333333333,0.6588235294117647,0.40784313725490196],
            #     color=GREEN.to_rgb(),
            #     zorder=3,
            # ),
            dict(
                key='eqmarl-psi+',
                label='Proposed eQMARL',
                blob='experiment_output/coingame_maa2c_mdp_eqmarl_psi+/20240501T152929/metrics-[0-9].json',
                # color=[0.2980392156862745,0.4470588235294118,0.6901960784313725],
                color=BLUE.to_rgb(),
                zorder=4,
            ),
        ]
        
        # Create data series.
        series_df: dict[str, pd.DataFrame] = {}
        for series_kwargs in series:
            key, blob = series_kwargs['key'], series_kwargs['blob']
            
            files = glob.glob(str(Path(blob).expanduser()))
            assert len(files) > 0, f"No files found for blob: {blob}"
            session_reward_history = []
            session_metrics_history = []
            for f in files:
                reward_history, metrics_history = load_train_results(str(f))
                session_reward_history.append(reward_history)
                # session_metrics_history.append(metrics_history)
                session_metrics_history.append({
                    **metrics_history,
                    # "reward": reward_history,
                    "reward_mean": np.mean(np.array(reward_history), axis=-1),
                    "reward_std": np.std(np.array(reward_history), axis=-1),
                    "reward_max": np.max(np.array(reward_history), axis=-1),
                    "reward_min": np.min(np.array(reward_history), axis=-1),
                    })
                
            # Reshape to proper matrix.
            session_reward_history = session_reward_history
            session_reward_history = np.array(session_reward_history)
            
            df = pd.DataFrame(session_metrics_history)
            series_df[key] = df
        
        # Create axis.
        x_tick_interval = 500
        y_tick_interval = 5
        x_range = (0, 3000)
        y_range = (-5, 30)
        ax = Axes(
            x_range=[x_range[0], x_range[1]+x_tick_interval, x_tick_interval], # +interval includes endpoints
            y_range=[y_range[0], y_range[1]+y_tick_interval, y_tick_interval], # +interval includes endpoints
            axis_config={'include_numbers': True},
            tips=True,
        )
        gap_width = abs(config.frame_width/2 - objs['group-grid-small-up/down'].get_x(RIGHT))
        ax.scale_to_fit_width(gap_width - 0.75).next_to(objs['group-grid-small-up/down'], RIGHT, buff=0.5).to_edge(DOWN, buff=0.5)
        
        # Create labels for axis.
        labels = ax.get_axis_labels(
            x_label=Text('Time', font_size=24),
            y_label=Text('Score', font_size=24),
        )
        tracker_x_value = ValueTracker(x_range[0]) # For animating x-axis.
        
        # Bundle the axis and series graphs together.
        group_graphs = VDict({
            'ax': ax,
            'labels': labels,
            'series': VDict({}), # Keys will match series keys.
            'legend': VDict({}), # Keys will match series keys.
        })
        
        # Create plots for `mean` and `std` metrics.
        metric_key_to_plot = 'undiscounted_reward' # Plot this metric.
        for series_kwargs in series:
            df = series_df[series_kwargs['key']]

            df_arr = np.array(df.values.tolist())
            i = list(df.columns).index(metric_key_to_plot) # Index of metric key within frame column.
            data = df_arr[:,i,:] # Data to plot.
            
            # Plot type: 'mean-rolling'
            metric_df = pd.DataFrame(np.mean(data, axis=0))
            y = metric_df.rolling(10).mean().to_numpy().flatten()
            x = np.arange(data.shape[-1]) # 0, 1, ..., N-1
            
            
            # Remove all NaN values.
            # Manim will linearly interpolate between gaps in data.
            x_valid, y_valid = remove_nan(x, y)
            
            # Plot +/- standard deviation.
            y_std = np.std(data, axis=0)# (3000,)
            n = 1 # Default is 1 std above/below the data.
            y_std_upper_values = y + y_std * n
            y_std_lower_values = y - y_std * n
            # Filter NaN.
            x_std_upper_values, y_std_upper_values = remove_nan(x, y_std_upper_values)
            x_std_lower_values, y_std_lower_values = remove_nan(x, y_std_lower_values)
            
            def make_line(
                x_valid=x_valid,
                y_valid=y_valid,
                color=series_kwargs['color'],
                zorder=series_kwargs['zorder'],
                ):
                """Generates a line plot from (x,y) data points.
                
                This function can be used with `always_redraw`.
                
                Function keyword arguments are set to allow data caching between frame calls.
                """
                # Check that we have data points with the mask, otherwise just return an empty `VGroup` object (this is really only a problem when the tracker is at the first data point).
                mask = x_valid <= tracker_x_value.get_value()
                if len(x_valid[mask]) > 0:
                    zorder = zorder + len(series) + 1 # Offset Z index to ensure on top of shaded plots.
                    graph_mean = ax.plot_line_graph(
                        x_values=x_valid[mask],
                        y_values=y_valid[mask],
                        add_vertex_dots=False,
                        line_color=ManimColor.from_rgb(color), # RGB color.
                        stroke_width=2, # Default is 2.
                    )
                    graph_mean.set_z_index(zorder)
                    return VGroup(*[
                        graph_mean,
                        Dot(ax.c2p(x_valid[mask][-1], y_valid[mask][-1]), color=ManimColor.from_rgb(color)).set_z_index(zorder), # Add a leading dot.
                    ])
                else:
                    return VGroup()

            def make_shaded(
                x_std_upper_values=x_std_upper_values,
                y_std_upper_values=y_std_upper_values,
                x_std_lower_values=x_std_lower_values,
                y_std_lower_values=y_std_lower_values,
                color=series_kwargs['color'],
                zorder=series_kwargs['zorder'],
                ):
                """Generates a plot of shaded regions representing +/- standard deviation around (x,y) data points.
                
                This function can be used with `always_redraw`.
                
                Function keyword arguments are set to allow data caching between frame calls.
                """
                # Check that we have data points with the mask, otherwise just return an empty `VGroup` object (this is really only a problem when the tracker is at the first data point).
                if len(x_valid[x_valid <= tracker_x_value.get_value()]) > 0:
                    y_std_upper_points = [ax.c2p(x, y) for x, y in zip(x_std_upper_values[x_valid <= tracker_x_value.get_value()], y_std_upper_values[x_valid <= tracker_x_value.get_value()])] # +1 std.
                    y_std_lower_points = [ax.c2p(x, y) for x, y in zip(x_std_lower_values[x_valid <= tracker_x_value.get_value()], y_std_lower_values[x_valid <= tracker_x_value.get_value()])] # -1 std.
                    # Create a `Polygon` using the upper and lower points.
                    graph_std = Polygon(*y_std_upper_points, *reversed(y_std_lower_points), color=color, fill_opacity=0.3, stroke_width=0.1) # Points are added in counter-clockwise order. Upper points are ok as-is from increasing X order, but lower points need to be reversed.
                    graph_std.set_z_index(zorder) # Set Z order (larger numbers on top).
                    return graph_std
                else:
                    return VGroup()
            
            # Bundle the mean and std graphs for the current series.
            graph_mean = always_redraw(make_line)
            graph_std = always_redraw(make_shaded)
            g = VDict({
                'mean': graph_mean,
                'std': graph_std,
            })
            
            # Preserve graphs for current series.
            group_graphs['series'][series_kwargs['key']] = g
            
            # Preserve legend elements for current series.
            group_graphs['legend'][series_kwargs['key']] = VDict({
                'glyph': Line(color=ManimColor.from_rgb(series_kwargs['color'])),
                'label': Tex(series_kwargs['label'], font_size=18),
            })

        # Set the legend positioning.
        for series_kwargs in series:
            group_graphs['legend'][series_kwargs['key']]['glyph'].scale(0.25)
            group_graphs['legend'][series_kwargs['key']]['label'].next_to(group_graphs['legend'][series_kwargs['key']]['glyph'], RIGHT, buff=0.2)
        group_graphs['legend'].arrange(buff=0.5) # Arrange in a horizontal line.
        group_graphs['legend'].next_to(group_graphs['ax'], UP).shift(RIGHT*.5)
        # Add a bounding box to legend.
        group_graphs['legend-box'] = SurroundingRectangle(group_graphs['legend'], color=GRAY_C, buff=0.2, corner_radius=0.1)

        # Animate the axis, axis-labels, and the legend-box.
        gap_center = objs['group-grid-small-up/down'].get_right() + np.array([gap_width/2., 0, 0]) # Shift X direction.
        objs['text-exp-11'] = Text("We ran several similar experiments", font_size=32).move_to(gap_center).shift(UP*2)
        objs['text-exp-12'] = Text("to demonstrate the effectiveness of eQMARL", font_size=32).next_to(objs['text-exp-11'], DOWN)
        objs['text-exp-13'] = Text("These are our results...", font_size=32).next_to(objs['text-exp-12'], DOWN*2)
        with self.voiceover(text="We ran several similar experiments <bookmark mark='1'/> to demonstrate the effectiveness of our proposed approach. <bookmark mark='2'/> The following details our results.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(Write(objs['text-exp-11']))
            self.wait_until_bookmark('1', frozen_frame=False)
            self.play(Write(objs['text-exp-12']))
            self.wait_until_bookmark('2', frozen_frame=False)
            self.play(Write(objs['text-exp-13']))

        self.small_pause(frozen_frame=False)
        self.play(
            ReplacementTransform(Group(objs['text-exp-11'], objs['text-exp-12'], objs['text-exp-13']), group_graphs['ax']),
            FadeIn(group_graphs['labels']),
        )

        objs['text-exp-14'] = Text("These are our baselines", font_size=32).next_to(group_graphs['legend-box'], UP)
        with self.voiceover(text="These are our baseline models for comparison.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(Write(objs['text-exp-14']))
            self.play(Write(group_graphs['legend-box']))
            self.play(
                Write(group_graphs['legend']['fctde']),
                Write(group_graphs['legend']['qfctde']),
                # Write(group_graphs['legend']['sctde']),
            )
        
        self.small_pause(frozen_frame=False)
        
        
        objs['text-exp-15'] = Text("and this is eQMARL", font_size=32).next_to(group_graphs['legend-box'], UP)
        with self.voiceover(text="And this is our proposed approach.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(
                ReplacementTransform(objs['text-exp-14'], objs['text-exp-15']),
                Write(group_graphs['legend']['eqmarl-psi+']),
            )
        self.small_pause(frozen_frame=False)
        self.play(FadeOut(objs['text-exp-15']))
        
        # Add all the plot series so they can be shown.
        for series_kwargs in series:
            self.add(group_graphs['series'][series_kwargs['key']]['mean'])

        # Create a pointer for animating the epochs.
        pointer = always_redraw(
            lambda: Vector(DOWN).scale(0.5).next_to(
                ax.x_axis.n2p(tracker_x_value.get_value()),
                UP,
                buff=0.1,
            )
        )
        label = always_redraw(
            lambda pointer=pointer: MathTex(f"t={tracker_x_value.get_value():.0f}", font_size=24).next_to(pointer, UP, buff=0.1)
        ).next_to(pointer, UP, buff=0.1)
        
        objs['text-exp-16'] = Text("After 3,000 unique maze configurations...", font_size=32).next_to(group_graphs['legend-box'], UP)
        with self.voiceover(text="After three-thousand unique maze configurations.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(Write(objs['text-exp-16']))
        
        # Add the pointer and label.
        self.play(FadeIn(pointer), FadeIn(label))
        
        # Animate the plots from left-to-right by setting the tracker value to the end value.
        self.play(
            tracker_x_value.animate.set_value(x_range[-1]),
            Succession(
                *[ApplyMethod(objs['grid-small-up'].obj.move_player, a) for a in [random.choice(list(MinigridAction)) for _ in range(x_range[-1])]],
                *[
                    ApplyMethod(objs['grid-small-up'].obj.get_player().move_to, objs['grid-small-up'].obj.get_goal().get_center()),
                ],
            ),
            Succession(
                *[ApplyMethod(objs['grid-small-down'].obj.move_player, a) for a in [random.choice(list(MinigridAction)) for _ in range(x_range[-1])]],
                *[
                    ApplyMethod(objs['grid-small-down'].obj.get_player().move_to, objs['grid-small-down'].obj.get_goal().get_center()),
                ],
            ),
            run_time=5,
        )
        
        # Remove the pointer and tracker label.
        self.play(FadeOut(pointer), FadeOut(label))
        
        # Emphasize score.
        objs['text-exp-17'] = MarkupText("The drones learn to achieve a <b>higher score</b>", font_size=32).next_to(group_graphs['legend-box'], UP)
        with self.voiceover(text="The drones learn to achieve a higher score.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(ReplacementTransform(objs['text-exp-16'], objs['text-exp-17']))
            for _ in range(2): # Repeat.
                self.play(group_graphs['series'][series_kwargs['key']]['mean'].animate.set_stroke(8), rate_func=there_and_back, run_time=0.5)

        self.medium_pause(frozen_frame=False)
        
        # Emphasize std.
        objs['text-exp-18'] = MarkupText("with <b>lower standard deviation</b> than baselines", font_size=32).next_to(group_graphs['legend-box'], UP)
        with self.voiceover(text="With significantly lower standard deviation than the baselines.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(ReplacementTransform(objs['text-exp-17'], objs['text-exp-18']))
            for series_kwargs in series:
                self.play(FadeIn(group_graphs['series'][series_kwargs['key']]['std']), run_time=1)

        self.medium_pause(frozen_frame=False)
        
        # Fade out everything except watermarks.
        mobjects_in_scene = list(set(self.mobjects) - set([self.eqmarl_acronym, self.attribution_text]))
        self.play(
            *[FadeOut(o) for o in mobjects_in_scene]
        )
    
    def section_summary(self):
        
        self.summary_header = MarkupText("The key takeaways are:", font_size=36).to_edge(UP, buff=2)
        self.summary_list = IconList(
            *[
                MarkupText("Quantum entangled learning can <b>improve performance</b> and <b>couple agent behavior</b>", font_size=28),
                MarkupText(f"e<span fgcolor=\"{self.colors['quantum'].to_hex()}\">Q</span>MARL <b>enhances privacy</b> by eliminating experience sharing", font_size=28),
                MarkupText(f"e<span fgcolor=\"{self.colors['quantum'].to_hex()}\">Q</span>MARL <b>dramatically reduces communication overhead</b>", font_size=28),
                MarkupText(f"e<span fgcolor=\"{self.colors['quantum'].to_hex()}\">Q</span>MARL can be deployed to <b>learn diverse environments</b>", font_size=28),
            ],
            icon=Star(color=YELLOW, fill_opacity=0.5).scale(0.3),
            buff=(.2, .5),
            col_alignments='rl',
        ).next_to(self.summary_header, DOWN, buff=0.5)
        
        with self.voiceover(text="The key takeaways are as follows.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(Write(self.summary_header))
        
        self.small_pause(frozen_frame=False)
        
        # Get list of summary icons and text objects.
        icons, texts = tuple(zip(*list(self.summary_list.enumerate_rows())))
        
        with self.voiceover(text="Quantum entangled learning can improve performance and couple agent behavior.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(Write(icons[0]), Write(texts[0]))
        
        self.small_pause(frozen_frame=False)

        with self.voiceover(text="eQMARL enhances privacy by eliminating experience sharing.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(Write(icons[1]), Write(texts[1]))
        
        self.small_pause(frozen_frame=False)

        with self.voiceover(text="eQMARL dramatically reduces communication overhead.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(Write(icons[2]), Write(texts[2]))
        
        self.small_pause(frozen_frame=False)
        
        with self.voiceover(text="eQMARL can be deployed to learn diverse environments.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            self.play(Write(icons[3]), Write(texts[3]))

        # for icon, text in self.summary_list.enumerate_rows():
        #     self.play(Write(icon), Write(text))
        #     self.wait(1)
        
        # self.medium_pause(frozen_frame=False)
        self.small_pause(frozen_frame=False)

    def section_outro(self):
        """Outro section.
        
        This is the last section played in the video.
        """
        
        qr = segno.make("https://arxiv.org/abs/2405.17486", micro=False, error='H')
        img = SegnoQRCodeImageMobject(qr, scale=100, dark=GRAY_A.to_hex(), finder_dark=PURPLE.to_hex(), border=0, light=None).scale(0.1)
        
        texts = {}
        # texts['subtitle'] = Text("Coordination without Communication", font_size=28)
        texts['subtitle'] = MarkupText("<i>Coordination without Communication</i>", font_size=28)
        # texts['attribution'] = Text("Alexander DeRieux & Walid Saad (2025)", font_size=24)
        texts['attribution'] = VGroup(
            Text("Alexander DeRieux & Walid Saad", font_size=22),
            MarkupText("Published in <i>The Thirteenth International Conference on Learning Representations (ICLR)</i> 2025", font_size=20),
        ).arrange(DOWN, buff=0.2)
        texts['arxiv'] = Text("Paper is available on arXiv", font_size=20)


        with self.voiceover(text="Thank you for watching our presentation on <bookmark mark='1'/> eQMARL, a quantum entangled approach for multi-agent reinforcement learning that facilitates <bookmark mark='2'/> coordination without communication.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            
            # Transform summary list into watermark at top-left.
            self.wait_until_bookmark('1', frozen_frame=False)
            self.play(ReplacementTransform(Group(self.summary_list, self.summary_header), self.eqmarl_acronym))
        
            # Shift and scale watermark to center as main title.
            self.play(self.eqmarl_acronym.animate.scale(2).move_to(ORIGIN).shift(UP*2), run_time=tracker.time_until_bookmark('2'))
            
            # Show subtitle.
            texts['subtitle'].next_to(self.eqmarl_acronym, DOWN)
            self.wait_until_bookmark('2', frozen_frame=False)
            self.play(Write(texts['subtitle']))
        
        self.small_pause(frozen_frame=False)
        
        with self.voiceover(text="Our work is published in The Thirteenth International Conference on Learning Representations, and the paper can be found online through archive by scanning the QR code below.", wait_kwargs=dict(frozen_frame=False)) as tracker:
            # Show QR code.
            img.next_to(texts['subtitle'], DOWN)
            self.play(FadeIn(img))
            
            # Show image text.
            texts['arxiv'].next_to(img, DOWN)
            self.play(Write(texts['arxiv']))
        
            # Show author names.
            texts['attribution'].next_to(texts['arxiv'], DOWN*1.25)
            self.play(ReplacementTransform(self.attribution_text, texts['attribution']))
        
        # Wait.
        self.long_pause(frozen_frame=False)