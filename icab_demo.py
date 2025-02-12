from enum import IntEnum
import itertools
import glob
import json
import os
import random
import pandas as pd
from pathlib import Path
import tempfile
from typing import Any, Callable, Iterable

from manim import *
from manim.typing import *
import segno

# config.disable_caching = True
# config.quality = 'low_quality'

# Tool for creating voiceovers with Manim: https://www.manim.community/plugin/manim-voiceover/

# Example of making a neural network with Manim: https://medium.com/@andresberejnoi/using-manim-and-python-to-create-animations-like-3blue1brown-andres-berejnoi-34f755606761

class CustomSuccession(Succession):
    
    def _setup_scene(self, scene) -> None:
        if scene is None:
            return
        if self.is_introducer():
            for anim in self.animations:
                if not anim.is_introducer() and anim.mobject is not None:
                    print(f"adding: {anim}")
                    scene.add(anim.mobject)

        self.scene = scene



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
            print(f"{i=}")
            yield (self.submobjects[i], self.submobjects[i+1])

class TestScene(Scene):
    def construct(self):
        
        objs = {}
        
        # pgbar = always_redraw(lambda: Rectangle(height=0.2, width=, color=BLUE, fill_opacity=0.5).to_edge(DOWN, buff=0))
        
        objs['text-exp-19'] = MarkupText("The key takeaways are:", font_size=32).to_edge(UP, buff=2)
        objs['text-exp-20'] = IconList(
            *[
                MarkupText("Quantum entangled learning can <b>improve performance</b> and <b>couple agent behavior</b>", font_size=28),
                MarkupText("eQMARL <b>eliminates experience sharing</b>", font_size=28),
                MarkupText("eQMARL can be deployed to <b>learn a diverse environments</b>", font_size=28),
            ],
            icon=Star(color=YELLOW, fill_opacity=0.5).scale(0.3),
            buff=(.2, .5),
            col_alignments='rl',
        ).next_to(objs['text-exp-19'], DOWN, buff=0.5)
        self.play(Write(objs['text-exp-19']))
        
        for icon, text in objs['text-exp-20'].enumerate_rows():
            self.play(Write(icon), Write(text))
            self.wait(1)
        
        self.eqmarl_logo = Text("eQMARL", font_size=32)
        
        self.play(
            ReplacementTransform(
                Group(objs['text-exp-19'], objs['text-exp-20']),
                self.eqmarl_logo
            ),
        )
        
        
        
        # objs['text-exp-20'] = BulletedList(
        #     MarkupText("Quantum entanglement couples agent experiences to learn optimal strategies"),
        #     font_size=32,
        # )
        # self.add(objs['text-exp-20'])
        

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

        # qr = segno.make("https://arxiv.org/abs/2405.17486", micro=False, error='H')
        
        config = {
            'light': None,
            'dark': WHITE.to_hex(),
            'border': 0,
            'scale': 100,
        }
        config.update(kwargs)
        # default_save_config.update(save_kwargs)

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

# class MiniGridPlayer(VGroup):

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


class DemoForICAB(PausableScene):
    def construct(self):
        
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
            (self.section_scenario, dict(name="Scenario", skip_animations=False)),
            (self.section_experiment, dict(name="Experiment", skip_animations=False)),
            (self.section_summary, dict(name="Summary", skip_animations=False)),
            (self.section_outro, dict(name="Outro", skip_animations=False)), # Last.
            ######### TRASH.
            # (self.section_motivation, dict(name="Motivation", skip_animations=False)),
            # (self.section_scenario_old, dict(name="Scenario-OLD", skip_animations=True)),
            # (self.section_results, dict(name="Results", skip_animations=False)),
            # (self.section_placeholder, dict(name="Placeholder", skip_animations=False)),
        ]
        for method, section_kwargs in sections:
            self.next_section(**section_kwargs)
            method()
        
        self.wait(1)
    
    def section_placeholder(self):
        """This is a placeholder section.
        Use it to test what comes before or after a new section.
        """
        # c = Circle()
        # self.play(Write(c))
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
        
        self.subtitle_text = Text("Coordination without Communication", font_size=28)
        self.subtitle_text.next_to(eqmarl_full, DOWN, buff=0.5)
        
        self.attribution_text_full = Text("Alexander DeRieux & Walid Saad (2025)", font_size=24)
        self.attribution_text_full.next_to(self.subtitle_text, DOWN, buff=0.5)
        
        self.attribution_text = Text("A. DeRieux & W. Saad (2025)", font_size=12)
        self.attribution_text.to_edge(DOWN, buff=0.1)
        
        # Combine the glyphs.
        eqmarl_glyphs = list(zip(eqmarl_acronym_glyphs, eqmarl_full_glyphs))
        
        # Animate the title.
        self.play(FadeIn(eqmarl_acronym))
        self.small_pause(frozen_frame=False)
        self.play(Write(eqmarl_full))
        self.small_pause(frozen_frame=False)
        self.play(Write(self.subtitle_text))
        self.small_pause(frozen_frame=False)
        
        # self.play(Create(self.attribution_text))
        self.play(Write(self.attribution_text_full))
        
        self.medium_pause(frozen_frame=False)
        
        self.play(FadeOut(eqmarl_full), FadeOut(self.subtitle_text), eqmarl_acronym.animate.scale(0.5).to_edge(UL), ReplacementTransform(self.attribution_text_full, self.attribution_text))

    def section_motivation(self):
        """Motivation section."""
        t0 = Text("Using quantum entanglement", font_size=28).shift(UP*3)
        # self.add(t0)
        self.play(Write(t0), run_time=0.75)
        
        # t1 = Text("to enable coordination", font_size=28).shift(DOWN*2)
        # self.add(t1)
        
        qubit_scale = 0.75
        q0 = Qubit(has_text=False, circle_color=PURPLE, ellipse_color=PURPLE).scale(qubit_scale).next_to(t0, DOWN, buff=0.5).shift(LEFT*2)
        q1 = Qubit(has_text=False, circle_color=BLUE, ellipse_color=BLUE).scale(qubit_scale).next_to(t0, DOWN, buff=0.5).shift(RIGHT*2)
        alpha = ValueTracker(0)
        qubit_gap_width = abs(q1.get_x(LEFT) - q0.get_x(RIGHT))
        wave_height_scale = qubit_scale - 0.15
        waves = VGroup(*[
            always_redraw(
                lambda: FunctionGraph(
                    lambda x: wave_height_scale*np.sin(2*PI*x - alpha.get_value()),
                    x_range=[-1, 1],
                    color=GRAY_C,
                ).stretch_to_fit_width(qubit_gap_width).next_to(q0, RIGHT, buff=0)
            ),
            always_redraw(
                lambda: FunctionGraph(
                    lambda x: wave_height_scale*np.sin(2*PI*x + alpha.get_value() + PI),
                    x_range=[-1, 1],
                    color=GRAY_D,
                ).stretch_to_fit_width(qubit_gap_width).next_to(q0, RIGHT, buff=0)
            ),
        ])
        
        q0_label = Text("Qubit A", font_size=24, color=GRAY).next_to(q0, DOWN, buff=0.2)
        q1_label = Text("Qubit B", font_size=24, color=GRAY).next_to(q1, DOWN, buff=0.2)
        # self.play(Write(q0_label), Write(q1_label))
        
        entangled_group = VGroup(q0, q0_label, q1, q1_label, waves)
        
        # Create the entangled qubit pair.
        self.play(Write(entangled_group))

        t1 = MarkupText(
            (
                f"we can couple the behavior of two <span fgcolor=\"{YELLOW}\">AI drones</span>"
                # "to enable coordination without communication."
            ),
            font_size=28).next_to(entangled_group, DOWN, buff=0.5)
        # self.add(t1)
        self.play(Write(t1))
        
        #####
        agents = VGroup(*[
            Triangle(color=PURPLE, fill_opacity=0.5).scale(0.5).rotate(-90*DEGREES).next_to(t1, DOWN, buff=0.5).shift(LEFT*2.5),
            Triangle(color=BLUE, fill_opacity=0.5).scale(0.5).rotate(+90*DEGREES).next_to(t1, DOWN, buff=0.5).shift(RIGHT*2.5),
        ])
        ####
        # agents = VGroup(*[
        #     SVGMobject("assets/images/drone.svg").scale(0.5).next_to(t1, DOWN, buff=0.5).shift(LEFT*2.5),
        #     SVGMobject("assets/images/drone.svg").scale(0.5).next_to(t1, DOWN, buff=0.5).shift(RIGHT*2.5),
        # ])
        # # Give all drones a grey outline to make them stand out.
        # for d in agents:
        #     path_outline = d.family_members_with_points()[0]
        #     path_outline.set_stroke(GRAY, 1)
        #####
        agent_labels = VGroup(*[
            Text("Drone A", font_size=20, color=GRAY).next_to(agents[0], LEFT, buff=0.2),
            Text("Drone B", font_size=20, color=GRAY).next_to(agents[1], RIGHT, buff=0.2),
        ])
        
        # agent0 = Triangle(color=RED, fill_opacity=0.5).scale(0.5).rotate(-90*DEGREES).next_to(t1, DOWN, buff=0.5).shift(LEFT*2)
        # agent1 = Triangle(color=BLUE, fill_opacity=0.5).scale(0.5).rotate(+90*DEGREES).next_to(t1, DOWN, buff=0.5).shift(RIGHT*2)
        # self.add(agent0, agent1)
        # self.play(Write(agent0), Write(agent1))
        self.play(*[GrowFromCenter(agents), Write(agent_labels)])
        
        
        t2 = MarkupText(f"to enable <span fgcolor=\"{GREEN}\">coordination</span> without <span fgcolor=\"{RED}\">communication</span>.", font_size=28).next_to(agents, DOWN, buff=0.5)
        # self.play(Write(t2[:8]))
        t2_underline = Underline(t2[20:27])
        
        # self.play(
        #     AnimationGroup(*[
        #         alpha.animate.set_value(2*PI),
        #         q0.animate.set_state_angle(90*DEGREES),
        #         q1.animate.set_state_angle(90*DEGREES),
        #         Write(agent0_text),
        #         Write(leftline),
        #     ], run_time=1, rate_func=linear),
        #     GrowFromCenter(t2[8:20]),
        # # AnimationGroup(*[
        # #     alpha.animate.set_value(0),
        # #     q0.animate.set_state_angle(180*DEGREES),
        # #     q1.animate.set_state_angle(180*DEGREES),
        # # ], run_time=1, rate_func=linear),
        # )
        
        
        notcircle = Circle(color=RED).scale(0.3).move_to(agents.get_center())
        notline = Line(start=notcircle.point_at_angle(45*DEGREES), end=notcircle.point_at_angle(225*DEGREES), color=RED)
        nottext = Text("No peer-to-peer", font_size=18).next_to(notcircle, DOWN, buff=0.1)
        
        # self.play(GrowFromCenter(t2[27:]), Write(notcircle), Write(notline), Write(nottext))
        
        agent0_text = Text("\"Turn LEFT\"", font_size=18, color=GREEN).next_to(agents[0], UR, buff=0)
        agent1_text = Text("\"Turn RIGHT\"", font_size=18, color=GREEN).next_to(agents[1], UL, buff=0)
        # self.add(agent0_text, agent1_text)
        
        leftline = DashedLine(start=agents[0].get_right(), end=notcircle.get_left(), color=PURPLE_E)
        rightline = DashedLine(start=agents[1].get_left(), end=notcircle.get_right(), color=BLUE_E)
        # self.add(leftline, rightline)
        
        self.play(Write(t2[:8])) # to enable
        
        # self.play(GrowFromCenter(t2[8:20])) # coordination
        # self.play(
        #     GrowFromCenter(t2[8:20]),
        #     AnimationGroup(*[
        #         alpha.animate.set_value(2*PI),
        #         q0.animate.set_state_angle(90*DEGREES),
        #         q1.animate.set_state_angle(90*DEGREES),
        #         Write(agent0_text),
        #         Write(leftline),
        #     ], run_time=2, rate_func=linear),
        # ) # coordination
        
        # self.play(Write(t2[20:27]), Write(Underline(t2[20:27]))) # without
        # self.play(GrowFromCenter(t2[27:]), Write(notcircle), Write(notline), Write(nottext)) # communication
        
        # # Animate the entangled qubit pair changing states.
        # entangled_animations = [
        #     AnimationGroup(*[
        #         alpha.animate.set_value(2*PI),
        #         q0.animate.set_state_angle(90*DEGREES),
        #         q1.animate.set_state_angle(90*DEGREES),
        #         GrowFromCenter(t2[8:20]),
        #         Write(agent0_text),
        #         # Write(leftline),
        #     ], run_time=1, rate_func=linear),
        #     AnimationGroup(*[
        #         alpha.animate.set_value(0),
        #         q0.animate.set_state_angle(135*DEGREES),
        #         q1.animate.set_state_angle(135*DEGREES),
        #         Write(agent1_text),
        #     ], run_time=1, rate_func=linear),
        #     AnimationGroup(*[
        #         alpha.animate.set_value(2*PI),
        #         q0.animate.set_state_angle(180*DEGREES),
        #         q1.animate.set_state_angle(180*DEGREES),
        #         # Write(agent1_text),
        #         # Write(rightline),
        #         Write(t2[20:27]), Write(Underline(t2[20:27])),
        #     ], run_time=1, rate_func=linear),
        #     AnimationGroup(*[
        #         alpha.animate.set_value(0),
        #         q0.animate.set_state_angle(225*DEGREES),
        #         q1.animate.set_state_angle(225*DEGREES),
        #         GrowFromCenter(t2[27:]), Write(notcircle), Write(notline), Write(nottext), Write(leftline), Write(rightline),
        #     ], run_time=1, rate_func=linear),
        #     AnimationGroup(*[
        #         alpha.animate.set_value(2*PI),
        #         q0.animate.set_state_angle(270*DEGREES),
        #         q1.animate.set_state_angle(270*DEGREES),
        #     ], run_time=1, rate_func=linear),
        #     AnimationGroup(*[
        #         alpha.animate.set_value(0),
        #         q0.animate.set_state_angle(315*DEGREES),
        #         q1.animate.set_state_angle(315*DEGREES),
        #     ], run_time=1, rate_func=linear),
        #     AnimationGroup(*[
        #         alpha.animate.set_value(2*PI),
        #         q0.animate.set_state_angle(0*DEGREES),
        #         q1.animate.set_state_angle(0*DEGREES),
        #     ], run_time=1, rate_func=linear),
        # ]
        # for a in entangled_animations:
        #     self.play(a)
            
            
        
        self.play(*[
            AnimationGroup(*[
                alpha.animate.set_value(2*PI),
                q0.animate.set_state_angle(90*DEGREES),
                q1.animate.set_state_angle(90*DEGREES),
            ], run_time=1, rate_func=linear),
            GrowFromCenter(t2[8:20]),
            Write(agent0_text),
        ], run_time=1)
        self.play(*[
            AnimationGroup(*[
                alpha.animate.set_value(0),
                q0.animate.set_state_angle(135*DEGREES),
                q1.animate.set_state_angle(135*DEGREES),
            ], run_time=1, rate_func=linear),
            Write(agent1_text),
        ], run_time=1)
        self.play(*[
            AnimationGroup(*[
                alpha.animate.set_value(2*PI),
                q0.animate.set_state_angle(180*DEGREES),
                q1.animate.set_state_angle(180*DEGREES),
            ], run_time=1, rate_func=linear),
            Write(t2[20:27]), 
            Write(t2_underline),
            # Write(Underline(t2[20:27])),
        ], run_time=1)
        self.play(*[
            AnimationGroup(*[
                alpha.animate.set_value(0),
                q0.animate.set_state_angle(225*DEGREES),
                q1.animate.set_state_angle(225*DEGREES),
            ], run_time=1, rate_func=linear),
            GrowFromCenter(t2[27:]), Write(notcircle), Write(notline), Write(nottext), Write(leftline), Write(rightline),
        ], run_time=1)
        self.play(*[
            AnimationGroup(*[
                alpha.animate.set_value(2*PI),
                q0.animate.set_state_angle(270*DEGREES),
                q1.animate.set_state_angle(270*DEGREES),
            ], run_time=1, rate_func=linear),
        ], run_time=1)
        self.play(*[
            AnimationGroup(*[
                alpha.animate.set_value(0),
                q0.animate.set_state_angle(315*DEGREES),
                q1.animate.set_state_angle(315*DEGREES),
            ], run_time=1, rate_func=linear),
        ], run_time=1)
        self.play(*[
            AnimationGroup(*[
                alpha.animate.set_value(2*PI),
                q0.animate.set_state_angle(0*DEGREES),
                q1.animate.set_state_angle(0*DEGREES),
            ], run_time=1, rate_func=linear),
        ], run_time=1)
        self.play(*[
            AnimationGroup(*[
                alpha.animate.set_value(0),
                q0.animate.set_state_angle(45*DEGREES),
                q1.animate.set_state_angle(45*DEGREES),
            ], run_time=1, rate_func=linear),
        ], run_time=1)
        
        objectsinscene = [t0, t1, t2, q0, q1, q0_label, q1_label, waves, entangled_group, agents, agent_labels, t2, t2_underline, notcircle, notline, nottext, agent0_text, agent1_text, leftline, rightline]
        self.play(*[FadeOut(o) for o in objectsinscene])
    
    def section_scenario_old(self):
        """Scenario section."""
        
        self.next_section("scenario-start", skip_animations=True) # TODO: delete.
        
        # Create and animate the title.
        section_title = Text("Example Scenario", font_size=self.eqmarl_acronym.font_size) # Match font size of the acronym in the top-left.
        self.play(Write(section_title)) # At origin.
        self.play(section_title.animate.to_edge(UP)) # Move to top edge.
        self.small_pause()
        
        ###
        # Scenario introduction.
        ###
        self.next_section("scenario-intro", skip_animations=True) # TODO: delete.
        
        # group = Group(*[
        #     Group(*[
        #         ImageMobject("assets/images/fire.png").scale(0.3),
        #         Group(*[
        #             Text(
        #                 text="The wildfires in California have spread at an unprecedented rate",
        #                 t2c={'wildfires': RED},
        #                 font_size=24,
        #             ),
        #             Text("Rapidly and efficiently extinguishing these fires has arisen to be a major challenge", font_size=18),
        #         ]).arrange(DOWN, aligned_edge=LEFT),
        #     ]).arrange(),
        #     Group(*[
        #         ImageMobject("assets/images/fireman.png").scale(0.25),
        #         Text("Firefighters on the ground have a limited localized view of the spreading flames", font_size=24),
        #     ]).arrange(),
        # ])
        group_bullet = Group(*[
            # Fire.
            ImageMobject("assets/images/fire.png").scale(0.3),
            VGroup(*[
                Text(
                    text="The wildfires in California have spread at an unprecedented rate",
                    t2c={'wildfires': RED},
                    font_size=24,
                ),
                Text("Rapidly and efficiently extinguishing these fires has arisen to be a major challenge", font_size=18),
            ]).arrange(DOWN, aligned_edge=LEFT),
            
            # Firefighter.
            ImageMobject("assets/images/fireman.png").scale(0.25),
            VGroup(*[
                Text("Firefighters on the ground have a limited localized view of the dynamic environment", font_size=24, t2w={'limited localized view':BOLD, 'dynamic environment':BOLD}),
                Text("Environmental features and limited wireless connectivity obstruct long-range communication", font_size=18),
            ]).arrange(DOWN, aligned_edge=LEFT),
            
            # Drone.
            ImageMobject("assets/images/no-wifi.png").scale(0.25),
            VGroup(*[
                Text("Swarming drones could collaboratively learn an optimal extinguish strategy, with caveats:", font_size=24, t2w={'Swarming drones':BOLD}),
                Text("Obstructions and limited wireless infrastructure hinders communication", font_size=18),
                Text("Aerial observations are comprised of many large data points (e.g., visual acoustic, geospatial, environmental, etc.)", font_size=18),
            ]).arrange(DOWN, aligned_edge=LEFT),
            
            # Qubit.
            Qubit(circle_color=PURPLE, ellipse_color=PURPLE).scale(0.45),
            VGroup(*[
                Text("Quantum entanglement is not limited by distance or obstructions", font_size=24, t2c={'Quantum entanglement':PURPLE_A}),
                Text("Couples the behavior of two entangled entities despite their physical separation", font_size=18),
            ]).arrange(DOWN, aligned_edge=LEFT),
            
            # Swarming Drones.
            ImageMobject("assets/images/quadcopter.png").scale(0.3),
            VGroup(*[
                Text("Quantum entangled drones could collaborate without direct P2P links, regardless of environmental conditions", font_size=24, t2c={'Quantum entangled drones':BLUE}),
                Text("Entangled means something that affects one will also affect another", font_size=18),
            ]).arrange(DOWN, aligned_edge=LEFT),
        ])
        # group.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        group_bullet.arrange_in_grid(rows=len(group_bullet)//2, cols=2, col_alignments='rl', buff=0.5)
        group_bullet.scale_to_fit_width(.9*config.frame_width)
        group_bullet.to_edge(LEFT)
        
        for (icon, textgroup) in itertools.batched(group_bullet, n=2):
            self.play(FadeIn(icon))
            for t in textgroup:
                self.play(Write(t)) # This works because we know that the items in this group are `VMobject`.
                self.small_pause()
        
        
        # t0 = Text(
        #     text="The wildfires in California have spread at an unprecedented rate",
        #     t2c={'wildfires': RED}
        # )
        # img_fire = ImageMobject("assets/images/fire.png")
        # # bullet_group_fire = 
        
        self.play(FadeOut(group_bullet))
        
        
        ###
        # Scenario diagram.
        ###
        self.next_section("scenario-diagram", skip_animations=True) # TODO: delete.
        
        
        
        # # Satellite.
        # img_sat = ImageMobject("assets/images/satellite-2.png").rotate(-45*DEGREES)
        # self.play(GrowFromCenter(img_sat))
        # self.play(img_sat.animate.scale(0.25).next_to(section_title, DOWN, buff=-0.1))
        # #
        # text_sat = Text("Quantum Satellite", font_size=18).next_to(img_sat, UR, buff=-0.4)
        # self.play(Write(text_sat))
        
        # Env left.
        img_drone_left = ImageMobject("assets/images/quadcopter.png").scale(0.3).shift(LEFT*3).shift(UP*.5)
        text_drone_left = Text("Quantum Drone A", font_size=18).next_to(img_drone_left, LEFT, buff=0.1)
        img_rain_left = ImageMobject("assets/images/rain-drops.png").scale(0.25).next_to(img_drone_left, DOWN, buff=-0.2).rotate(30*DEGREES)
        group_drone_left = Group(img_drone_left, img_rain_left, text_drone_left)
        img_fire_house = ImageMobject("assets/images/wildfire-2.png").scale(0.3).next_to(img_drone_left, DOWN*7.5)
        img_fireman_left = ImageMobject("assets/images/fireman.png").scale(0.15).next_to(img_fire_house, LEFT, aligned_edge=DOWN)
        img_nocom_left = ImageMobject("assets/images/no-wifi.png").scale(0.15).next_to(img_fireman_left, UP)
        text_nocom_left = Text("No Wireless", font_size=18).next_to(img_nocom_left, UP, buff=0.1)
        img_nospeak_left = ImageMobject("assets/images/no-speak.png").scale(0.15).next_to(img_drone_left, RIGHT*7)
        text_nospeak_left = Text("Blocked P2P", font_size=18).next_to(img_nospeak_left, UP, buff=0.1)
        text_env_left = Text("House Fire", font_size=18).next_to(img_fire_house, DOWN)
        # self.play(GrowFromCenter(img_drone_left), FadeIn(img_rain_left), Write(text_drone_left))
        # self.add(img_fire_house, img_fireman_left, img_nocom_left, text_env_left, img_nospeak_left, text_nospeak_left)
        group_env_left = Group(group_drone_left, img_fire_house, img_fireman_left, img_nocom_left, text_nocom_left, text_env_left, img_nospeak_left, text_nospeak_left)
        group_env_left.shift(LEFT)
        self.play(
            FadeIn(img_fire_house),
            Write(text_env_left),
            FadeIn(img_fireman_left),
            # FadeIn(img_nocom_left),
        )
        self.play(
            GrowFromCenter(img_drone_left),
            # GrowFromCenter(img_rain_left),
            Write(text_drone_left),
        )
        
        # Env right.
        img_drone_right = ImageMobject("assets/images/quadcopter.png").scale(0.3).shift(RIGHT*3).shift(UP*.5)
        text_drone_right = Text("Quantum Drone B", font_size=18).next_to(img_drone_right, RIGHT, buff=0.1)
        img_rain_right = ImageMobject("assets/images/rain-drops.png").scale(0.25).next_to(img_drone_right, DOWN, buff=-0.2).rotate(30*DEGREES)
        group_drone_right = Group(img_drone_right, img_rain_right, text_drone_right)
        img_fire_trees = ImageMobject("assets/images/wildfire.png").scale(0.3).next_to(img_drone_right, DOWN*7.5)
        img_fireman_right = ImageMobject("assets/images/fireman.png").scale(0.15).next_to(img_fire_trees, RIGHT, aligned_edge=DOWN)
        img_fireman_right.pixel_array = np.fliplr(img_fireman_right.pixel_array) # Horizontal flip, must do this because of bug in `.flip()`. See https://github.com/ManimCommunity/manim/issues/2412
        img_nocom_right = ImageMobject("assets/images/no-wifi.png").scale(0.15).next_to(img_fireman_right, UP)
        text_nocom_right = Text("No Wireless", font_size=18).next_to(img_nocom_right, UP, buff=0.1)
        img_nospeak_right = ImageMobject("assets/images/no-speak.png").scale(0.15).next_to(img_drone_right, LEFT*7)
        text_nospeak_right = Text("Blocked P2P", font_size=18).next_to(img_nospeak_right, UP, buff=0.1)
        text_env_right = Text("Forest Fire", font_size=18).next_to(img_fire_trees, DOWN)
        # self.play(GrowFromCenter(img_drone_right), FadeIn(img_rain_right), Write(text_drone_right))
        # self.add(img_fire_trees, img_fireman_right, img_nocom_right, text_env_right, img_nospeak_right, text_nospeak_right)
        group_env_right = Group(group_drone_right, img_fire_trees, img_fireman_right, img_nocom_right, text_nocom_right, text_env_right, img_nospeak_right, text_nospeak_right)
        group_env_right.shift(RIGHT)
        self.play(
            FadeIn(img_fire_trees),
            Write(text_env_right),
            FadeIn(img_fireman_right),
            # FadeIn(img_nocom_right),
        )
        self.play(
            GrowFromCenter(img_drone_right),
            # GrowFromCenter(img_rain_right),
            Write(text_drone_right),
        )
        
        # Combine both left/right environments into one group to make alignment of future objects easier.
        group_envs = Group(group_env_left, group_env_right)
        
        # Center obstruction.
        img_obstruction = ImageMobject("assets/images/mountain-3.png").scale(1.1)
        text_obstruction = Text("Environmental Obstruction", font_size=18).next_to(img_obstruction, DOWN)
        group_obstruction = Group(img_obstruction, text_obstruction)
        group_obstruction.align_to(group_envs.get_bottom(), DOWN)
        self.play(FadeIn(img_obstruction), Write(text_obstruction))
        
        
        # Animate no-speak arrows.
        arrow_drone_left_to_nospeak_left = Arrow(start=img_drone_left.get_right(), end=img_nospeak_left.get_left(), max_tip_length_to_length_ratio=0.5, color=RED)
        arrow_drone_left_to_nospeak_right = Arrow(start=img_drone_right.get_left(), end=img_nospeak_right.get_right(), max_tip_length_to_length_ratio=0.5, color=RED)
        self.play(Write(arrow_drone_left_to_nospeak_left), Write(arrow_drone_left_to_nospeak_right))
        self.play(FadeIn(img_nospeak_left), Write(text_nospeak_left), FadeIn(img_nospeak_right), Write(text_nospeak_right))
    
        # Animate no communication bubbles for fireman.
        self.play(GrowFromCenter(img_nocom_left), Write(text_nocom_left), GrowFromCenter(img_nocom_right), Write(text_nocom_right))
        
        # Wiggle the no-com and no-speak bubbles.
        self.play(Wiggle(img_nocom_left), Wiggle(img_nocom_right), Wiggle(img_nospeak_left), Wiggle(img_nospeak_right))
        self.play(Wiggle(img_nocom_left), Wiggle(img_nocom_right), Wiggle(img_nospeak_left), Wiggle(img_nospeak_right))
        
        img_nospeak_left_newloc = img_nospeak_left.copy().next_to(img_drone_left, UP, buff=0.1)
        img_nospeak_right_newloc = img_nospeak_right.copy().next_to(img_drone_right, UP, buff=0.1)
        
        # Get rid of the no-com arrows and symbols to make entanglement easier to visualize.
        self.play(
            img_obstruction.animate.scale(0.5).next_to(text_obstruction, UP, buff=0.1),
            # FadeOut(img_nospeak_left),
            ReplacementTransform(img_nospeak_left, img_nospeak_left_newloc),
            # FadeOut(text_nospeak_left),
            text_nospeak_left.animate.next_to(img_nospeak_left_newloc, UP, buff=0.1),
            FadeOut(arrow_drone_left_to_nospeak_left),
            # FadeOut(img_nospeak_right),
            ReplacementTransform(img_nospeak_right, img_nospeak_right_newloc),
            # FadeOut(text_nospeak_right),
            text_nospeak_right.animate.next_to(img_nospeak_right_newloc, UP, buff=0.1),
            FadeOut(arrow_drone_left_to_nospeak_right),
        )
        # Update the old references after animating the position change.
        img_nospeak_left_newloc = img_nospeak_left
        img_nospeak_right_newloc = img_nospeak_right
    
        
        # self.add(img_fire_trees, img_fire_house, img_fireman_left, img_fireman_right, img_nocom_left, img_nocom_right)
        # group_envs = Group(img_fire_trees, img_fire_house, img_fireman_left, img_fireman_right, img_nocom_left, img_nocom_right)
        
        
        # Satellite.
        img_sat = ImageMobject("assets/images/satellite-2.png").rotate(-45*DEGREES).scale(0.25).next_to(section_title, DOWN, buff=-0.1)
        self.play(GrowFromCenter(img_sat))
        # self.play(GrowFromCenter(img_sat))
        # self.play(img_sat.animate.scale(0.25).next_to(section_title, DOWN, buff=-0.1))
        #
        text_sat = Text("Quantum Satellite", font_size=18).next_to(img_sat, UR, buff=-0.4)
        self.play(Write(text_sat))
        
        # # Put a qubit at the center of each arrow.
        # qubit_left = Qubit(circle_color=PURPLE, ellipse_color=PURPLE).scale(0.25).move_to(arrow_sat_to_drone_left.get_center(), UP).shift(DOWN*.3)
        # qubit_right = Qubit(circle_color=PURPLE, ellipse_color=PURPLE).scale(0.25).move_to(arrow_sat_to_drone_right.get_center(), UP).shift(DOWN*.3)
        qubit_left = Qubit(circle_color=PURPLE, ellipse_color=PURPLE).scale(0.3)
        qubit_right = Qubit(circle_color=PURPLE, ellipse_color=PURPLE).scale(0.3)
        qubit_left.next_to(img_sat, DOWN).shift(LEFT*.5)
        qubit_right.next_to(img_sat, DOWN).shift(RIGHT*.5)
        group_qubits = VGroup(qubit_left, qubit_right)
        
        # Create a wave between the qubits to symbolize entanglement.
        wave_entgen = Line(start=qubit_left.get_right(), end=qubit_right.get_left())
        
        tmptext = Text("Entanglement Generation", font_size=18)
        tmptext.next_to(group_qubits, DOWN)
        
        self.play(Write(tmptext), FadeIn(group_qubits))
        self.play(Write(wave_entgen)) # Show wave.
        self.play(Unwrite(wave_entgen), Unwrite(tmptext)) # Remove wave.
        
        
        tmptext = Paragraph("Distribute Qubits\nvia\nQuantum Channel", alignment='center', font_size=18) # Reuse the text variable since we'll need a lot of them :).
        tmptext.next_to(img_sat, DOWN*1.5)
        
        # Move the qubits.
        qubit_left_newloc = qubit_left.copy().next_to(img_drone_left, RIGHT, buff=0.2)
        qubit_right_newloc = qubit_right.copy().next_to(img_drone_right, LEFT, buff=0.2)
        
        # Connect arrows from satellite to qubits.
        arrow_sat_to_drone_left = DashedVMobject(Arrow(start=img_sat.get_corner(DL)+UR*.5, end=qubit_left_newloc.get_corner(UR), max_tip_length_to_length_ratio=0.1, color=PURPLE))
        arrow_sat_to_drone_right = DashedVMobject(Arrow(start=img_sat.get_corner(DR)+UL*.5, end=qubit_right_newloc.get_corner(UL), max_tip_length_to_length_ratio=0.1, color=PURPLE))
        
        # Move the qubits next to the drones.
        self.play(
            Write(tmptext),
            ReplacementTransform(qubit_left, qubit_left_newloc),
            ReplacementTransform(qubit_right, qubit_right_newloc),
            Write(arrow_sat_to_drone_left),
            Write(arrow_sat_to_drone_right),
        )
        # Update qubit references.
        qubit_left = qubit_left_newloc
        qubit_right = qubit_right_newloc
        
        # Remove the temporary text and arrows from the satellite.
        self.play(
            FadeOut(tmptext),
            FadeOut(arrow_sat_to_drone_left),
            FadeOut(arrow_sat_to_drone_right),
        )
        
        
        
        # TODO show that observations on the LEFT side affect the actions on the right side.
        
        # TODO entangled wave between qubits.
        qubit_scale = 0.5
        wave_height_scale = qubit_scale - 0.15
        qubit_gap_width = abs(qubit_left.get_x(RIGHT) - qubit_right.get_x(LEFT))
        alpha = ValueTracker(0)
        waves = VGroup(*[
            always_redraw(
                lambda: FunctionGraph(
                    lambda x: wave_height_scale*np.sin(2*PI*x - alpha.get_value()),
                    x_range=[-1, 1],
                    color=GRAY_C,
                ).stretch_to_fit_width(qubit_gap_width).next_to(qubit_left, RIGHT, buff=0)
            ),
            always_redraw(
                lambda: FunctionGraph(
                    lambda x: wave_height_scale*np.sin(2*PI*x + alpha.get_value() + PI),
                    x_range=[-1, 1],
                    color=GRAY_D,
                ).stretch_to_fit_width(qubit_gap_width).next_to(qubit_left, RIGHT, buff=0)
            ),
        ])
        
        
        # Arrow going down to environment.
        tmparrow_down = DashedVMobject(Arrow(start=img_drone_left.get_bottom(), end=img_fire_house.get_top(), max_tip_length_to_length_ratio=0.15))
        # Arrow going back up to drone.
        tmparrow_up = DashedVMobject(Arrow(start=img_fire_house.get_top(), end=img_drone_left.get_bottom(), max_tip_length_to_length_ratio=0.15))
        # tmptext_left = Paragraph("Local observations\non the LEFT", font_size=18).next_to(tmparrow_down, RIGHT) # Text to the right of the arrow.
        tmptext_left = Paragraph("Local observations\non the LEFT", font_size=18).next_to(midpoint(img_drone_left.get_bottom(), img_fire_house.get_top()), RIGHT) # Text to the right of the arrow.
        self.play(Write(tmptext_left))
        self.play(Write(tmparrow_down), Wiggle(img_drone_left))
        self.play(FadeOut(tmparrow_down))
        self.play(Write(tmparrow_up), Wiggle(img_fire_house))
        # self.play(FadeOut(tmparrow_up))
        
        tmptext_center = Paragraph("Through Quantum Entanglement", font_size=18).next_to(waves, DOWN)
        self.play(
            Write(tmptext_center),
            Create(waves),
        )
        self.play(
            alpha.animate.set_value(2*PI),
            qubit_left.animate.set_state_angle(-45*DEGREES),
            qubit_right.animate.set_state_angle(-45*DEGREES),
        )
        self.play(
            alpha.animate.set_value(0),
            qubit_left.animate.set_state_angle(45*DEGREES),
            qubit_right.animate.set_state_angle(45*DEGREES),
        )
        

        tmptext_right = Paragraph("Effect the actions\non the RIGHT", font_size=18, alignment='right').next_to(midpoint(img_drone_right.get_bottom(), img_fire_trees.get_top()), LEFT)
        self.play(Write(tmptext_right))
        # self.play(alpha.animate.set_value(2*PI))
        # self.play(alpha.animate.set_value(0))
        
        
        
        
        
        
        
        # # Animate the qubits changing state.
        # action_drone_left = Text("Turn LEFT", font_size=16, color=GREEN).next_to(text_drone_left, DOWN)
        # action_drone_right = Text("Turn RIGHT", font_size=16, color=GREEN).next_to(text_drone_right, DOWN)
        
        # Get original rain position and opacity.
        orig_rain_pos = [
            img_rain_left.get_center(),
            img_rain_right.get_center(),
        ]
        
        # self.play(
        #     qubit_left.animate.set_state_angle(-45*DEGREES),
        #     qubit_right.animate.set_state_angle(-45*DEGREES),
        #     Write(action_drone_left),
        #     img_rain_left.animate.move_to(img_fire_house.get_center()).set_opacity(0),
        # )
        
        # img_rain_left.move_to(orig_rain_pos[0]).set_opacity(1) # Restore state before animation.
        # self.play(img_rain_left.animate.move_to(img_fire_house.get_center()).set_opacity(0)) # Animate the rain drop again.
        
        # self.play(qubit_left.animate.set_state_angle(225*DEGREES), qubit_right.animate.set_state_angle(225*DEGREES))
        
        
        self.play(
            qubit_left.animate.set_state_angle(-45*DEGREES),
            qubit_right.animate.set_state_angle(-45*DEGREES),
            # Write(action_drone_right),
            img_rain_right.animate.move_to(img_fire_trees.get_center()).set_opacity(0),
        )
        
        img_rain_right.move_to(orig_rain_pos[1]).set_opacity(1) # Restore state before animation.
        
        # self.play(img_rain_right.animate.move_to(img_fire_trees.get_center()).set_opacity(0)) # Animate the rain drop again.
        
        # # img_rain_right.move_to(orig_rain_pos[1]).set_opacity(1) # Restore state before animation.
        
        # self.play(qubit_left.animate.set_state_angle(225*DEGREES), qubit_right.animate.set_state_angle(225*DEGREES))
        
        
        
        
        
        # # Now play it all again for sync.
        # self.play(
        #     Wiggle(img_fire_house),
        #     AnimationGroup(Write(tmparrow_up), FadeOut(tmparrow_up), lag_ratio=1),
        # )
        # self.play(
        #     # Wiggle(img_fire_house),
        #     # AnimationGroup(Write(tmparrow_up), FadeOut(tmparrow_up), lag_ratio=1),
        #     qubit_left.animate.set_state_angle(45*DEGREES),
        #     qubit_right.animate.set_state_angle(45*DEGREES),
        #     alpha.animate.set_value(2*PI),
        #     img_rain_right.animate.move_to(img_fire_trees.get_center()).set_opacity(0),
        # )
        # img_rain_right.move_to(orig_rain_pos[1]).set_opacity(1) # Restore state before animation.
        # self.play(
        #     Wiggle(img_fire_house),
        #     AnimationGroup(Write(tmparrow_up), FadeOut(tmparrow_up), lag_ratio=1),
        #     qubit_left.animate.set_state_angle(-45*DEGREES),
        #     qubit_right.animate.set_state_angle(-45*DEGREES),
        #     alpha.animate.set_value(0),
        #     img_rain_right.animate.move_to(img_fire_trees.get_center()).set_opacity(0),
        # )
        
        self.play(
            Write(tmparrow_up),
            Wiggle(img_fire_house),
            alpha.animate.set_value(2*PI),
            img_rain_right.animate.move_to(img_fire_trees.get_center()).set_opacity(0),
        )
        img_rain_right.move_to(orig_rain_pos[1]).set_opacity(1) # Restore state before animation.
        alpha.set_value(0) # Reset alpha.
        self.play(
            Write(tmparrow_up),
            Wiggle(img_fire_house),
            alpha.animate.set_value(2*PI),
            img_rain_right.animate.move_to(img_fire_trees.get_center()).set_opacity(0),
        )
        
        # Fade everything out except watermarks and title.
        g = Group(*list(set(self.mobjects) - set([self.eqmarl_acronym, self.attribution_text, section_title])))
        self.play(FadeOut(g))
        
        
        
        
        
        

        
        
        # return
        
        
        # t0 = Text(
        #     text="The wildfires in California have spread at an unprecedented rate",
        #     t2c={'wildfires': RED}
        # )
        # t0.scale_to_fit_width(.9*config.frame_width)
        # print(f"{t0.font_size=}")
        # self.play(Write(t0))
        # self.wait()
        
        # t1 = Text("Rapidly and efficiently extinguishing these fires has arisen to be a major challenge")
        # t1.scale_to_fit_width(.8*config.frame_width)
        # t1.next_to(t0, DOWN)
        # self.play(Write(t1))
        
        # # Group text boxes and move them both up as a unit.
        # g0 = VGroup(t0, t1)
        # self.play(g0.animate.shift(UP*2))
        
        # t2 = Text("Firefighters on the ground have a limited localized view of the spreading flames")
        # t2.scale_to_fit_width(.9*config.frame_width)
        # self.play(Write(t2))
        
        # img_fire = ImageMobject("assets/images/fire.png")
        # self.add(img_fire)
        
        # img_fireman = ImageMobject("assets/images/fireman.png")
        # self.add(img_fireman)
        
        # img_drone = ImageMobject("assets/images/drone.png")
        # self.add(img_drone)
        
        ########
        
        # t0 = Text("Scenario", font_size=32)
        # self.play(Write(t0))
        
        
        # drones = VGroup(*[
        #     SVGMobject("assets/images/drone.svg"),
        #     SVGMobject("assets/images/drone.svg"),
        # ])
        # # Give all drones a grey outline to make them stand out.
        # for d in drones:
        #     path_outline = d.family_members_with_points()[0]
        #     path_outline.set_stroke(GRAY, 1)
        #     d.scale(0.5)
        
        # drones.next_to(t0, UP)
        
        # drones[0].shift(LEFT*2)
        # drones[1].shift(RIGHT*2)
        
        # self.play(GrowFromCenter(drones))
        
        # line = Line(start=drones[0].get_right(), end=drones[1].get_left())
        # self.play(Write(line))
        
        
        # firetree = SVGMobject("assets/images/firetree.svg").scale(0.5)
        # firetree.next_to(drones[0], DOWN)
        # self.add(firetree)
        
        # firehouse = SVGMobject("assets/images/firehouse.svg").scale(0.5)
        # firehouse.next_to(drones[1], DOWN)
        # self.add(firehouse)
        
        
        # self.play(Wiggle(drones[0]))
        # self.play(Wiggle(drones[1]))
        # self.play(Wiggle(firetree))
        # self.play(Wiggle(firehouse))
        
        # # drone = SVGMobject("assets/images/drone.svg")
        # # drone.next_to(t0, DOWN*2)
        # # path_outline = drone.family_members_with_points()[0]
        # # path_outline.set_stroke(GRAY, 1)
        
        # # self.play(FadeIn(drone))
        
        # # self.play(drone.animate.shift(RIGHT*2))
        # # self.play(drone.animate.rotate(45*DEGREES))
    
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
        texts['imagine-0'] = Text("Imagine two separate environments", font_size=32).to_edge(UP, buff=1)
        texts['imagine-1'] = Text("and two AI-powered drones", font_size=32).to_edge(UP, buff=1)
        texts['ideal-0'] = MarkupText(f"In an <u>ideal</u> scenario", font_size=32).to_edge(UP, buff=1)
        texts['ideal-1'] = Text("The drones could learn", font_size=24).next_to(arrows['ideal-com-lr'], UP)
        texts['ideal-2'] = MarkupText(f"by directly sharing their <span fgcolor=\"{self.colors['observation'].to_hex()}\">experiences</span>", font_size=24).next_to(arrows['ideal-com-rl'], DOWN)
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
        
        
        # Imagine.
        self.play(Write(texts['imagine-0']))
        self.play(FadeIn(objs['env-left']), FadeIn(objs['env-right']))
        self.play(ReplacementTransform(texts['imagine-0'], texts['imagine-1']))
        self.play(FadeIn(objs['drone-left']), FadeIn(objs['drone-right']))
        self.play(FadeOut(texts['imagine-1']))
        
        # Ideal.
        self.play(Write(texts['ideal-0']))
        self.play(
            Write(arrows['env-left-up']),
            Write(arrows['env-left-down']),
            Write(arrows['env-right-up']),
            Write(arrows['env-right-down']),
        )
        self.play(Write(texts['ideal-1']), Write(arrows['ideal-com-lr']))
        self.play(FadeIn(texts['ideal-2']), Write(arrows['ideal-com-rl']))
        self.medium_pause(frozen_frame=False)
        self.play(FadeOut(texts['ideal-0']), FadeOut(texts['ideal-1']), FadeOut(arrows['ideal-com-lr']), FadeOut(texts['ideal-2']), FadeOut(arrows['ideal-com-rl']))
        
        # No communication.
        self.play(Write(texts['nocom-0']))
        self.play(FadeIn(objs['obstacle']))
        self.play(
            Write(texts['nocom-1']),
        )
        self.play(
            FadeIn(objs['nocom-left']),
            FadeIn(objs['nocom-right']),
            Write(arrows['no-com-lr']),
            Write(arrows['no-com-rl']),
        )
        self.medium_pause(frozen_frame=False)
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
        self.play(Write(texts['quantum-0']))
        self.wait(1)
        self.play(ReplacementTransform(texts['quantum-0'], texts['quantum-1']))
        self.play(FadeIn(objs['qubit-left']), FadeIn(objs['qubit-right']))
        self.play(Write(waves['ent-0']))
        objs['obstacle'].set_z_index(1) # On top.
        self.small_pause(frozen_frame=False)
        self.play(
            Write(texts['quantum-2']),
            trackers['amp-0'].animate.set_value(.2),
            trackers['freq-0'].animate.set_value(4*PI),
            objs['qubit-left'].animate.next_to(objs['drone-left'], RIGHT),
            objs['qubit-right'].animate.next_to(objs['drone-right'], LEFT),
        )
        self.play(FadeOut(texts['quantum-2']), ReplacementTransform(texts['quantum-1'], texts['quantum-3']))
        arrows['env-left-up'].shift(LEFT*.2) # Move to center.
        arrows['env-right-down'].shift(LEFT*.2) # Move to center.
        self.play(
            Write(arrows['env-left-up']),
        )
        self.play(Write(texts['quantum-4']))
        self.play(
            Write(arrows['env-right-down']),
        )
        self.play(Write(texts['quantum-5']))
        self.medium_pause(frozen_frame=False)
        
        # Lasting point before section change.
        self.play(ReplacementTransform(VGroup(texts['quantum-3'], texts['quantum-4'], texts['quantum-5']), texts['quantum-6']))
        self.play(Write(texts['quantum-7']))
        self.play(arrows['env-left-up'].obj.animate.set_color(YELLOW).set_stroke(width=12, opacity=0.5), rate_func=there_and_back)
        self.play(
            Wiggle(objs['qubit-left']),
            Wiggle(objs['qubit-right']),
            rate_func=linear,
        )
        self.play(arrows['env-right-down'].obj.animate.set_color(YELLOW).set_stroke(width=12, opacity=0.5), rate_func=there_and_back)
        self.medium_pause(frozen_frame=False)

        # Clear the screen of all objects created in this section.
        mobjects_in_scene = list(set(self.mobjects) - set([self.eqmarl_acronym, self.attribution_text]))
        self.play(
            *[FadeOut(o) for o in mobjects_in_scene]
        )

    def section_experiment(self):
        # self.next_section('experiment-debug-start', skip_animations=True) # Do not animate anything below this.
        
        objs = {}
        
        # Text objects.
        objs['text-exp-0'] = Text("Let's see an illustrative example", font_size=32)
        objs['text-exp-1'] = Tex(r"This is an $5\times5$ grid environment for 1 player", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-2'] = Tex(r"The player can take actions $a \in \{\textrm{left}, \textrm{right}, \textrm{forward}\}$ to move in the grid", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-3'] = Text("As the player moves it gathers experiences", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-4'] = Text("The player learns from experiences to find the goal", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-5'] = Text("Now consider 2 parallel environments with different agents", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-6'] = Text("The agents cannot directly communicate with each other", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-7'] = Text("Which means they cannot coordinate using shared experiences", font_size=32).to_edge(UP, buff=1.5)
        objs['text-exp-8'] = MarkupText(f"<span fgcolor=\"{self.colors['quantum'].to_hex()}\">Quantum entanglement</span> between the agents", font_size=32).to_edge(UP, buff=1.2)
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
                obj=objs['grid-big-center'].assets['grid-empty'].copy().scale(0.25),
                label=Text("Empty grid square", font_size=18),
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
            MObjectWithLabel(
                obj=objs['grid-big-center'].assets['player'].copy().scale(0.25),
                label=Text("Drone", font_size=18),
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
        self.play(Write(objs['text-exp-0'])) # Let's see example.
        self.play(ReplacementTransform(objs['text-exp-0'], objs['text-exp-1'])) # This is a grid.
        self.play(FadeIn(objs['grid-big-center'])) # Show big grid in center.
        for m in objs['grid-big-legend']: # Show the legend elements.
            self.play(FadeIn(m))
        
        self.play(ReplacementTransform(objs['text-exp-1'], objs['text-exp-2'])) # Player actions.
        self.play(
            # Succession(
            #     ApplyMethod(objs['grid-big-center'].move_player, a)
            #     for a in minigrid_path_str_to_list('fff')
            # ),
            objs['grid-big-center'].animate_actions(*minigrid_path_str_to_list('fff')),
            run_time=2,
        )
        self.play(ReplacementTransform(objs['text-exp-2'], objs['text-exp-3'])) # Gains experiences.
        self.play(
            # Succession(
            #     ApplyMethod(objs['grid-big-center'].move_player, a)
            #     for a in minigrid_path_str_to_list('frf')
            #     # for a in minigrid_path_str_to_list('ffffrffff')
            # ),
            objs['grid-big-center'].animate_actions(*minigrid_path_str_to_list('frf')),
            run_time=2,
        )
        self.play(ReplacementTransform(objs['text-exp-3'], objs['text-exp-4'])) # To find the goal.
        self.play(
            # Succession(
            #     ApplyMethod(objs['grid-big-center'].move_player, a)
            #     for a in minigrid_path_str_to_list('fff')
            #     # for a in minigrid_path_str_to_list('ffffrffff')
            # ),
            objs['grid-big-center'].animate_actions(*minigrid_path_str_to_list('fff')),
            run_time=2,
        )
        # self.play(
        #     Flash(objs['grid-big-center'].get_goal_coord(), flash_radius=objs['grid-big-center'].get_goal().width*.75, color=GREEN),
        #     rate_func=linear,
        # )
        self.play(FadeOut(objs['grid-big-legend']))
        self.play(FadeOut(objs['text-exp-4']))
        self.play(FadeOut(objs['grid-big-center']))
        
        
        
        # Show two grids.
        self.play(Write(objs['text-exp-5'])) # Now consider 2 environments.
        self.play(
            GrowFromCenter(objs['grid-big-left']),
            GrowFromCenter(objs['grid-big-right']),
        )
        self.play(ReplacementTransform(objs['text-exp-5'], objs['text-exp-6'])) # Cannot communicate.
        self.play(
            # Succession(
            #     ApplyMethod(objs['grid-big-left'].obj.move_player, a)
            #     for a in minigrid_path_str_to_list('fff')
            # ),
            # Succession(
            #     ApplyMethod(objs['grid-big-right'].obj.move_player, a)
            #     for a in minigrid_path_str_to_list('rfff')
            # ),
            objs['grid-big-left'].obj.animate_actions(*minigrid_path_str_to_list('fff')),
            objs['grid-big-right'].obj.animate_actions(*minigrid_path_str_to_list('rfff')),
            run_time=2,
        )
        self.play(ReplacementTransform(objs['text-exp-6'], objs['text-exp-7'])) # Cannot coordinate.
        self.play(
            # Succession(
            #     ApplyMethod(objs['grid-big-left'].obj.move_player, a)
            #     for a in minigrid_path_str_to_list('rfff')
            # ),
            # Succession(
            #     ApplyMethod(objs['grid-big-right'].obj.move_player, a)
            #     for a in minigrid_path_str_to_list('flfff')
            # ),
            objs['grid-big-left'].obj.animate_actions(*minigrid_path_str_to_list('rfff')),
            objs['grid-big-right'].obj.animate_actions(*minigrid_path_str_to_list('flfff')),
            run_time=2,
        )
        
        
        
        
        
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
        self.play(Write(objs['text-exp-9']))
        self.play(
            # Succession(
            #     ApplyMethod(objs['grid-small-left'].obj.move_player, a)
            #     for a in minigrid_path_str_to_list('rffl')
            # ),
            # Succession(
            #     ApplyMethod(objs['grid-small-right'].obj.move_player, a)
            #     for a in minigrid_path_str_to_list('ffr')
            # ),
            objs['grid-small-left'].obj.animate_actions(*minigrid_path_str_to_list('rffl')),
            objs['grid-small-right'].obj.animate_actions(*minigrid_path_str_to_list('ffr')),
            run_time=2,
        )
        self.play(Write(objs['text-exp-10']))
        self.play(
            # Succession(
            #     ApplyMethod(objs['grid-small-left'].obj.move_player, a)
            #     for a in minigrid_path_str_to_list('ffffrff')
            # ),
            # Succession(
            #     ApplyMethod(objs['grid-small-right'].obj.move_player, a)
            #     for a in minigrid_path_str_to_list('fffflff')
            # ),
            objs['grid-small-left'].obj.animate_actions(*minigrid_path_str_to_list('ffffrff')),
            objs['grid-small-right'].obj.animate_actions(*minigrid_path_str_to_list('fffflff')),
            run_time=2,
        )
        # self.play(
        #     Flash(objs['grid-small-left'].obj.get_goal_coord(), flash_radius=objs['grid-small-left'].obj.get_goal().width*.75, color=GREEN),
        #     Flash(objs['grid-small-right'].obj.get_goal_coord(), flash_radius=objs['grid-small-right'].obj.get_goal().width*.75, color=GREEN),
        #     rate_func=linear,
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
        # self.play(
        #     Succession(
        #         ApplyMethod(objs['grid-small-up'].obj.move_player, a)
        #         for a in minigrid_path_str_to_list('ffffrff')
        #     ),
        #     Succession(
        #         ApplyMethod(objs['grid-small-down'].obj.move_player, a)
        #         for a in minigrid_path_str_to_list('fffflff')
        #     ),
        #     run_time=2,
        # )
        
        
        #########################################################
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
        
        # self.next_section('experiment-debug-stop', skip_animations=False) # DEBUG

        # Animate the axis, axis-labels, and the legend-box.
        gap_center = objs['group-grid-small-up/down'].get_right() + np.array([gap_width/2., 0, 0]) # Shift X direction.
        objs['text-exp-11'] = Text("We ran several similar experiments", font_size=32).move_to(gap_center).shift(UP*2)
        objs['text-exp-12'] = Text("to demonstrate the effectiveness of eQMARL", font_size=32).next_to(objs['text-exp-11'], DOWN)
        objs['text-exp-13'] = Text("These are our results...", font_size=32).next_to(objs['text-exp-12'], DOWN*2)
        self.play(Write(objs['text-exp-11']))
        self.play(Write(objs['text-exp-12']))
        self.play(Write(objs['text-exp-13']))
        self.small_pause(frozen_frame=False)
        self.play(
            ReplacementTransform(Group(objs['text-exp-11'], objs['text-exp-12'], objs['text-exp-13']), group_graphs['ax']),
            FadeIn(group_graphs['labels']),
        )
        # self.play(Create(group_graphs['ax']), FadeIn(group_graphs['labels']), Write(group_graphs['legend-box']))

        # self.next_section('experiment-debug-tmp', skip_animations=True) # DEBUG

        objs['text-exp-14'] = Text("These are our baselines", font_size=32).next_to(group_graphs['legend-box'], UP)
        self.play(Write(objs['text-exp-14']))
        self.play(Write(group_graphs['legend-box']))
        self.play(
            Write(group_graphs['legend']['fctde']),
            Write(group_graphs['legend']['qfctde']),
            # Write(group_graphs['legend']['sctde']),
        )
        self.small_pause(frozen_frame=False)
        objs['text-exp-15'] = Text("and this is eQMARL", font_size=32).next_to(group_graphs['legend-box'], UP)
        self.play(
            ReplacementTransform(objs['text-exp-14'], objs['text-exp-15']),
            Write(group_graphs['legend']['eqmarl-psi+']),
        )
        self.small_pause(frozen_frame=False)
        self.play(FadeOut(objs['text-exp-15']))
        
        # Add all the plot series so they can be shown.
        for series_kwargs in series:
            self.add(group_graphs['series'][series_kwargs['key']]['mean'])

        # # Animate the plots in a specific order.
        # # Do not add std plots yet because we don't want those to show when the value tracker is updating.
        # self.play(Write(group_graphs['legend-box']))
        # for series_kwargs in series:
        #     self.add(
        #         group_graphs['series'][series_kwargs['key']]['mean'],
        #         group_graphs['legend'],
        #     )

        # self.next_section('experiment-debug-tmp', skip_animations=True) # DEBUG

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
        
        objs['text-exp-17'] = MarkupText("The agents learn to achieve a <b>higher score</b>", font_size=32).next_to(group_graphs['legend-box'], UP)
        self.play(ReplacementTransform(objs['text-exp-16'], objs['text-exp-17']))
        self.play(group_graphs['series'][series_kwargs['key']]['mean'].animate.set_stroke(8), rate_func=there_and_back, run_time=0.5)
        self.play(group_graphs['series'][series_kwargs['key']]['mean'].animate.set_stroke(8), rate_func=there_and_back, run_time=0.5)
        self.medium_pause(frozen_frame=False)
        
        
        # Fade in the std plots.
        objs['text-exp-18'] = MarkupText("with <b>lower standard deviation</b> than baselines", font_size=32).next_to(group_graphs['legend-box'], UP)
        self.play(ReplacementTransform(objs['text-exp-17'], objs['text-exp-18']))
        for series_kwargs in series:
            self.play(FadeIn(group_graphs['series'][series_kwargs['key']]['std']), run_time=1)
        # self.play(
        #     *[FadeIn(group_graphs['series'][series_kwargs['key']]['std']) for series_kwargs in series],
        #     run_time=4,
        # )
        
        self.medium_pause(frozen_frame=False)
        
        # Fade out everything except watermarks.
        mobjects_in_scene = list(set(self.mobjects) - set([self.eqmarl_acronym, self.attribution_text]))
        self.play(
            *[FadeOut(o) for o in mobjects_in_scene]
        )
        
        
        # # objs['text-exp-19'] = MarkupText("The key takeaways are:", font_size=32).to_edge(UP, buff=2)
        # # objs['text-exp-20'] = BulletedList()
        # # objs['text-exp-20'] = MarkupText("through quantum entanglement", font_size=32).next_to(objs['text-exp-19'], DOWN)
        # # objs['text-exp-21'] = MarkupText("via coupled experiences", font_size=32).next_to(objs['text-exp-20'], DOWN)
        # # objs['text-exp-21'] = MarkupText("agents learn to collaborate", font_size=32).next_to(objs['text-exp-20'], DOWN)
        
        # objs['text-exp-19'] = MarkupText("The key takeaways are:", font_size=36).to_edge(UP, buff=2)
        # objs['text-exp-20'] = IconList(
        #     *[
        #         MarkupText("Quantum entangled learning can <b>improve performance</b> and <b>couple agent behavior</b>", font_size=28),
        #         MarkupText(f"e<span fgcolor=\"{self.colors['quantum'].to_hex()}\">Q</span>MARL <b>eliminates experience sharing</b>", font_size=28),
        #         MarkupText(f"e<span fgcolor=\"{self.colors['quantum'].to_hex()}\">Q</span>MARL can be deployed to <b>learn diverse environments</b>", font_size=28),
        #     ],
        #     icon=Star(color=YELLOW, fill_opacity=0.5).scale(0.3),
        #     buff=(.2, .5),
        #     col_alignments='rl',
        # ).next_to(objs['text-exp-19'], DOWN, buff=0.5)
        # # Clear the screen of all objects created in this section.
        # mobjects_in_scene = list(set(self.mobjects) - set([self.eqmarl_acronym, self.attribution_text]))
        # # self.play(
        # #     ReplacementTransform(Group(*mobjects_in_scene), objs['text-exp-19'])
        # # )
        # self.play(
        #     *[FadeOut(o) for o in mobjects_in_scene]
        # )
        # self.play(Write(objs['text-exp-19']))
        # for icon, text in objs['text-exp-20'].enumerate_rows():
        #     self.play(Write(icon), Write(text))
        #     self.wait(1)
        
        # self.medium_pause(frozen_frame=False)
        
        # # Clear the screen of all objects created in this section.
        # mobjects_in_scene = list(set(self.mobjects) - set([self.eqmarl_acronym, self.attribution_text]))
        # self.play(
        #     *[FadeOut(o) for o in mobjects_in_scene]
        # )
        
        #########################################################
        
    
    def section_results(self):
        """Experiement result graph dispaly."""
        
        # Data to display.
        series: list[dict] = [
            dict(
                key='$\\mathtt{fCTDE}$',
                blob='experiment_output/coingame_maa2c_mdp_fctde/20240501T185443/metrics-[0-9].json',
                # color=[0.8666666666666667,0.5176470588235295,0.3215686274509804],
                color=ORANGE.to_rgb(),
                zorder=1,
            ),
            dict(
                key='$\\mathtt{qfCTDE}$',
                blob='experiment_output/coingame_maa2c_mdp_qfctde/20240503T151226/metrics-[0-9].json',
                # color=[0.8549019607843137, 0.5450980392156862, 0.7647058823529411],
                color=PINK.to_rgb(),
                zorder=2,
            ),
            dict(
                key='$\\mathtt{sCTDE}$',
                blob='experiment_output/coingame_maa2c_mdp_sctde/20240418T133421/metrics-[0-9].json',
                # color=[0.3333333333333333,0.6588235294117647,0.40784313725490196],
                color=GREEN.to_rgb(),
                zorder=3,
            ),
            dict(
                key='$\\mathtt{eQMARL-}\Psi^{+}$',
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
        # Create labels for axis.
        labels = ax.get_axis_labels(
            x_label=Text('Epoch', font_size=24),
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
                'label': Tex(series_kwargs['key'], font_size=18),
            })

        # Set the legend positioning.
        for series_kwargs in series:
            group_graphs['legend'][series_kwargs['key']]['glyph'].scale(0.25)
            group_graphs['legend'][series_kwargs['key']]['label'].next_to(group_graphs['legend'][series_kwargs['key']]['glyph'], RIGHT, buff=0.2)
        group_graphs['legend'].arrange(buff=0.5) # Arrange in a horizontal line.
        group_graphs['legend'].next_to(group_graphs['ax'], UP)
        # Add a bounding box to legend.
        group_graphs['legend-box'] = SurroundingRectangle(group_graphs['legend'], color=GRAY_C, buff=0.2, corner_radius=0.1)


        # Animate the axis, axis-labels, and the legend-box.
        self.play(Create(group_graphs['ax']), FadeIn(group_graphs['labels']), Write(group_graphs['legend-box']))

        # Animate the plots in a specific order.
        # Do not add std plots yet because we don't want those to show when the value tracker is updating.
        for series_kwargs in series:
            self.add(
                group_graphs['series'][series_kwargs['key']]['mean'],
                group_graphs['legend'],
            )
            # self.play(
            #     Create(group_graphs['series'][series_kwargs['key']]['mean']),
            #     # FadeIn(group_graphs['series'][series_kwargs['key']]['std']),
            #     FadeIn(group_graphs['legend'][series_kwargs['key']]),
            # )
        
        # # Add lines for the moving dots.
        # lines = always_redraw(
        #     lambda: VGroup(*[
        #         DashedVMobject(Line(start=))
        #         for series_kwargs in series
        #     ]),
        # )
        
        
        # Create a pointer for animating the epochs.
        pointer = always_redraw(
            lambda: Vector(UP).scale(0.5).next_to(
                ax.x_axis.n2p(tracker_x_value.get_value()),
                DOWN,
            )
        )
        label = always_redraw(
            lambda pointer=pointer: MathTex(f"e={tracker_x_value.get_value():.0f}", font_size=24).next_to(pointer, DOWN)
        ).next_to(pointer, DOWN)
        
        
        # Add the pointer and label.
        self.play(FadeIn(pointer), FadeIn(label))
        
        # Animate the plots from left-to-right by setting the tracker value to the end value.
        self.play(tracker_x_value.animate.set_value(x_range[-1]), run_time=5)
        
        # Remove the pointer and tracker label.
        self.play(FadeOut(pointer), FadeOut(label))
        
        # Fade in the std plots.
        self.play(*[FadeIn(group_graphs['series'][series_kwargs['key']]['std']) for series_kwargs in series], run_time=2)
        
        self.long_pause()


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
        self.play(Write(self.summary_header))
        for icon, text in self.summary_list.enumerate_rows():
            self.play(Write(icon), Write(text))
            self.wait(1)
        
        self.medium_pause(frozen_frame=False)
        
        # # Clear the screen of all objects created in this section.
        # mobjects_in_scene = list(set(self.mobjects) - set([self.eqmarl_acronym, self.attribution_text]))
        # self.play(
        #     *[FadeOut(o) for o in mobjects_in_scene]
        # )

    def section_outro(self):
        """Outro section.
        
        This is the last section played in the video.
        """
        
        qr = segno.make("https://arxiv.org/abs/2405.17486", micro=False, error='H')
        img = SegnoQRCodeImageMobject(qr, scale=100, dark=GRAY_A.to_hex(), finder_dark=PURPLE.to_hex(), border=0, light=None).scale(0.1)
        
        texts = {}
        texts['subtitle'] = Text("Coordination without Communication", font_size=28)
        texts['attribution'] = Text("Alexander DeRieux & Walid Saad (2025)", font_size=24)
        texts['arxiv'] = Text("Paper is available on arXiv", font_size=20)
        
        # Transform summary list into watermark at top-left.
        self.play(ReplacementTransform(Group(self.summary_list, self.summary_header), self.eqmarl_acronym))
        
        # Shift and scale watermark to center as main title.
        self.play(self.eqmarl_acronym.animate.scale(2).move_to(ORIGIN).shift(UP*2))
        
        # Show subtitle.
        texts['subtitle'].next_to(self.eqmarl_acronym, DOWN)
        self.play(Write(texts['subtitle']))
        
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
        self.long_pause()


def make_quantum_gate_1qubit(name: str, color: ManimColor = WHITE):
    label = Tex(name, color=color, font_size=36)
    box = SurroundingRectangle(label, color=color, buff=0.25)
    lines = VDict({
        'left': Line(start=box.get_left(), end=LEFT, color=color),
        'right': Line(start=box.get_right(), end=RIGHT, color=color),
    })
    return VDict({
        'label': label,
        'box': box,
        'lines': lines,
    })


class DiagramScene(Scene):
    def construct(self):
        
        ###
        # Quantum circuit diagram.
        ###
        # g0 = make_quantum_gate_1qubit("$X$")
        # g1 = make_quantum_gate_1qubit(r"$R^{\theta}$").next_to(g0, buff=0)
        # g2 = make_quantum_gate_1qubit("$Z$")
        # self.add(g0, g1)
        
        
        
        ###
        # Block diagram.
        ###
        
        def create_bounded_block(mobject: VMobject, **kwargs):
            """Surrounds anything given with a rectangle.
            
            This is helpful when creating elements inline.
            The items given and the bounding box will be combined and returned as a `VDict` with keys "box" and "object".
            """
            # Default configuration for `SurroundingRectangle`.
            config = dict(
                color=WHITE,
                corner_radius=0.1,
                buff=0.2,
            )
            config.update(kwargs)
            box = SurroundingRectangle(mobject, **config)
            return VDict({
                'box': box,
                'object': mobject,
            })
        
        # def create_block(name: str, text_kwargs: dict = {}, box_kwargs: dict = {}):
        #     label = Tex(name, font_size=20, **text_kwargs)
        #     # box = Square()
        #     # box.surround(label, stretch=True, buff=0.5)
        #     box = SurroundingRectangle(label, color=WHITE, buff=0.2, **box_kwargs)
        #     return VGroup(label, box)
        
        
        
        # b0 = SurroundingRectangle(Tex("A", font_size=26))
        # b1 = SurroundingRectangle(Tex("B", font_size=26))
        # b2 = SurroundingRectangle(Tex("C", font_size=26))
        # b0 = create_block("This is\na multi-line\nblock\nwith math $x=2$", text_kwargs=dict(justify=True)).to_edge(LEFT)
        # b0 = create_bounded_block(Text("A", font_size=20), color=WHITE, buff=0.2).to_edge(LEFT)
        b0 = create_bounded_block(VGroup(Circle().shift(RIGHT), Square())).to_edge(LEFT)
        b1 = create_bounded_block(Text("Central Critic3", color=WHITE, font_size=36)).next_to(b0, RIGHT*3)
        b2 = create_bounded_block(Paragraph("This is a\nMulti line", font_size=36, alignment='center')).next_to(b1, RIGHT*3)
        
        print(f"{b1['object'].color=}, {b1['object'].get_color()=}")
        
        nodes = VGroup(b0, b1, b2)
        
        e0 = Arrow(b0.get_right(), b1.get_left(), buff=0)
        e1 = Arrow(b1.get_right(), b2.get_left(), buff=0)
        edges = VGroup(e0, e1)
        
        self.add(nodes)
        self.add(edges)
        
        
        self.wait(1)


# tmpfile idea: https://stackoverflow.com/questions/3924117/how-to-use-tempfile-namedtemporaryfile-in-python

### FROM CHATGPT.
class BlockDiagramGraphShapes(Scene):
    def construct(self):
        # Define nodes and edges
        nodes = ["A", "B", "C"]
        edges = [("A", "B"), ("B", "C")]

        # Define node positions
        # layout = {"A": LEFT * 3, "B": ORIGIN, "C": RIGHT * 3}
        layout = {"A": LEFT, "B": ORIGIN, "C": RIGHT}

        # Custom shapes for nodes
        shapes = {
            "A": Square(),
            "B": Square(),
            "C": Square(),
            # "A": Rectangle(width=2, height=1, color=BLUE).move_to(layout["A"]),
            # "B": Circle(radius=0.7, color=GREEN).move_to(layout["B"]),
            # "C": Ellipse(width=2, height=1, color=RED).move_to(layout["C"]),
        }
        
        # Create the graph
        graph = DiGraph(nodes, edges, layout=layout, edge_config={"stroke_width": 3}, vertex_mobjects=shapes)

        # Labels for nodes
        labels = {node: Text(node).move_to(shapes[node]) for node in nodes}

        # Add to scene
        self.play(Create(graph))
        for node in nodes:
        #     self.play(Transform(graph.vertices[node], shapes[node]))
            self.play(Write(labels[node]))


        self.wait(2)




class QRCodeScene(Scene):
    def construct(self):
        
        import io
        import os
        import segno
        import tempfile
        import qrcode_artistic
        # img = segno.make("https://arxiv.org/abs/2405.17486", micro=False, error='H')
        # print(f"{img.designator=}")
        
        
        qr = segno.make("https://arxiv.org/abs/2405.17486", micro=False, error='H')
        # qr = qr.to_pil(dark=RED.to_hex(), data_dark=YELLOW.to_hex(), light=None, scale=100, border=0)
        img = SegnoQRCodeImageMobject(qr, scale=100, dark=WHITE.to_hex(), finder_dark=RED.to_hex(), border=0, light=None).scale(0.1)
        # self.add(img)
        
        
        
        # # staticfilename = os.path.expanduser("~/Downloads/testimg.png")
        # # img.save(staticfilename, scale=100, light=None, dark=WHITE.to_hex(), border=0)
        # # print(f"{WHITE.to_hex()=}")
        
        # with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmpfile:
        #     tmpfile_name = tmpfile.name
        #     img.save(tmpfile_name, scale=100, light=None, dark=WHITE.to_hex(), border=0)
        
        
        
        
        # # # img = qrcode.to_pil(scale=10, dark='white')
        # # # img = img.convert("RGBA")
        # # # tmpfile = io.BytesIO()
        # # # img.save(tmpfile, format='PNG')
        # # # tmpfile.seek(0)
        # # # tmpfile = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        # # with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmpfile:
        # #     tmpfile_name = tmpfile.name
        # #     # img.save(tmpfile, scale=10, kind='png')
        # #     # img.save(tmpfile, kind='svg', light=None, dark='white')
        # #     img.save(tmpfile, kind='svg')
        # # # qrcode_img = ImageMobject(tmpfile_name)
        # # # qrcode_img = SVGMobject(tmpfile_name).scale(2)
        
        
        # # qrcode_img = SVGMobject(tmpfile_name, color=WHITE)
        # # qrcode_img = SVGMobject(staticfilename)
        # # qrcode_img = ImageMobject(staticfilename).scale(.1)
        # qrcode_img = ImageMobject(tmpfile_name).scale(.1)
        # # qrcode_img.set_fill(WHITE)
        # # qrcode_img.set_stroke(WHITE, width=1)
        # # qrcode_img[0].set_style(fill_opacity=1,stroke_width=1,stroke_opacity=0,fill_color=RED_A)
        # # surr = SurroundingRectangle(qrcode_img, buff=0)
        # # print(qrcode_img.get_all_points())
        # self.add(qrcode_img)
        # # self.play(GrowFromCenter(qrcode_img))
        
        t0 = Text("Paper is available on arXiv", font_size=24)
        t0.next_to(img, UP)
        
        self.play(Write(t0), FadeIn(img))
        self.play(Wiggle(img))
        self.play(FadeOut(t0), FadeOut(img))
        
        
        # # print(tmpfile_name)
        # # input()
        
        
        # # print(tmpfile_name)
        # os.unlink(tmpfile_name)
        # # assert not os.path.exists(tmpfile_name)
        # # print(f"{os.path.exists(tmpfile_name)=}")
        
        
        self.wait(1)


class GridScene(Scene):
    def construct(self):
        
        # dot1 = Dot(point=LEFT * 2 + UP * 2, radius=0.16, color=BLUE)
        # dot2 = Dot(point=LEFT * 2 + DOWN * 2, radius=0.16, color=MAROON)
        # dot3 = Dot(point=RIGHT * 2 + DOWN * 2, radius=0.16, color=GREEN)
        # dot4 = Dot(point=RIGHT * 2 + UP * 2, radius=0.16, color=YELLOW)
        # self.add(dot1, dot2, dot3, dot4)

        # # self.play(Succession(
        # #     ApplyMethod(dot1.move_to, dot2),
        # #     ApplyMethod(dot2.move_to, dot3),
        # #     Flash(dot2.get_center()),
        # #     ApplyMethod(dot3.move_to, dot4),
        # #     ApplyMethod(dot4.move_to, dot1),
        # # ))
        
        # self.play(LaggedStart(
        #     ApplyMethod(dot1.move_to, dot2),
        #     Flash(dot2.get_center()),
        #     ApplyMethod(dot2.move_to, dot3),
        #     ApplyMethod(dot3.move_to, dot4),
        #     ApplyMethod(dot4.move_to, dot1),
        #     lag_ratio=1,
        # ))
        
        
        ######
        
        objs = {}
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
        self.add(objs['grid-big-left'], objs['grid-big-right'])
        
        # self.play(
        #     Succession(
        #         ApplyMethod(objs['grid-big-left'].obj.move_player, a)
        #         for a in minigrid_path_str_to_list('fff')
        #     ),
        #     Succession(
        #         ApplyMethod(objs['grid-big-right'].obj.move_player, a)
        #         for a in minigrid_path_str_to_list('rfff')
        #     ),
        #     run_time=2,
        # )
        
        self.play(
            # Succession(
            #     ApplyMethod(objs['grid-big-left'].obj.move_player, a)
            #     for a in minigrid_path_str_to_list('rfff')
            # ),
            # objs['grid-big-left'].obj.animate_actions(*minigrid_path_str_to_list('rfff')),
            objs['grid-big-left'].obj.animate_actions(*minigrid_path_str_to_list('fffrfffflf')),
            # Succession(
            #     ApplyMethod(objs['grid-big-right'].obj.move_player, a)
            #     for a in minigrid_path_str_to_list('flfff')
            # ),
            run_time=4,
        )
    
    # def add(self, *args, **kwargs):
    #     super().add(*args, **kwargs)
        
    #     if 'VGroup(Line' in str(args[0].submobjects):
    #         import traceback
    #         print(args[0].submobjects)
    #         traceback.print_stack()



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