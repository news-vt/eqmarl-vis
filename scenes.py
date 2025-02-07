from manim import *
import manim.typing
import itertools
from enum import IntEnum

config.disable_caching = True


# # Objects for reuse.
# # obj_grid_empty = Square(color=GRAY, fill_opacity=0.5)
# obj_grid_empty = Square(color=GRAY, fill_opacity=0)
# obj_grid_lava = Square(color=ORANGE, fill_opacity=0.5)
# obj_grid_goal = Square(color=GREEN, fill_opacity=0.5)
# obj_player_base = obj_grid_empty.copy()
# # obj_player_core = Triangle(color=RED, fill_opacity=0.5).rotate(270*DEGREES).move_to(obj_player_base.get_center())
# # obj_player_core = Triangle(color=RED, fill_opacity=0.5).rotate(270*DEGREES)
# obj_player_core = VGroup(*[
#     Triangle(color=RED, fill_opacity=0.5).rotate(270*DEGREES),
# ])
# obj_player_core += Dot(obj_player_core.get_right()) # Dot represents the leading tip of the player triangle.
# obj_player = VGroup(*[
#     obj_player_base,
#     obj_player_core,
# ])



# def build_minigrid(
#     grid_size: tuple[int, int] = (5,5),
#     player_pos: tuple[int, int] | None = None, # Defaults to top-left.
#     goal_pos: tuple[int, int] | None = None, # Defaults to bottom-right.
#     hazards: list[tuple[int, int]] = [],
#     grid_obj_default: Mobject = obj_grid_empty,
#     grid_obj_hazard: Mobject = obj_grid_lava,
#     grid_obj_goal: Mobject = obj_grid_goal,
#     grid_obj_player: Mobject = obj_player,
#     ) -> list[list[VMobject]]:
#     """Helper function to generate a MiniGrid environment.
    
#     Returns a 2D matrix of Manim `VMobject`.
#     """
#     if player_pos == None: # Defaults to top-left.
#         player_pos = (0,0)
#     if goal_pos == None: # Defaults to bottom-right.
#         goal_pos = (grid_size[0]-1, grid_size[1]-1)

#     # Build the grid.
#     rows = []
#     for r in range(grid_size[0]):
#         cols = []
#         for c in range(grid_size[1]):
#             # if (r,c) == player_pos:
#             #     cols.append(grid_obj_player.copy())
#             if (r,c) == goal_pos:
#                 cols.append(grid_obj_goal.copy())
#             elif (r,c) in hazards:
#                 cols.append(grid_obj_hazard.copy())
#             else:
#                 cols.append(grid_obj_default.copy())
#         rows.append(cols)
#     return rows


class MinigridAction(IntEnum):
    LEFT = 0
    RIGHT = 1
    FORWARD = 2

class MiniGrid(VMobject):
    
    # Common objects for reuse.
    assets: dict[str, VMobject] = {
        'grid_empty': Square(color=GRAY, fill_opacity=0),
        'grid_lava': Square(color=ORANGE, fill_opacity=0.5),
        'grid_goal': Square(color=GREEN, fill_opacity=0.5),
        'player': VGroup(*[
            Triangle(color=RED, fill_opacity=0.5),
            Dot(Triangle().get_top()) # Dot represents the leading tip of the player triangle.
        ],z_index=1).rotate(270*DEGREES), # Higher z-index sets on top.
    }
    
    def __init__(self, 
        grid_size: tuple[int,int], 
        *args,
        player_look_angle: float = 270, # degrees, RIGHT
        player_grid_pos: tuple[int,int] = (0,0), # Top-left.
        goal_grid_pos: tuple[int,int] = (-1, -1),
        hazards_grid_pos: list[tuple[int,int]] = [],
        **kwargs,
        ):
        super().__init__(*args, **kwargs)
        self.grid_size = grid_size
        
        # Support for negative indexing.
        def negative_index_rollover(i: int, size: int):
            return i if i >= 0 else i+size
        player_grid_pos = tuple(negative_index_rollover(i, size) for i,size in zip(player_grid_pos, grid_size))
        goal_grid_pos = tuple(negative_index_rollover(i, size) for i,size in zip(goal_grid_pos, grid_size))
        hazards_grid_pos = [tuple(negative_index_rollover(i, size) for i,size in zip(haz, grid_size)) for haz in hazards_grid_pos]
        
        
        # Defaults to `RIGHT`, and upper-left (0,0).
        self.player_look_angle = player_look_angle
        self.player_grid_pos = player_grid_pos
        self.goal_pos = goal_grid_pos
        self.hazards_grid_pos = hazards_grid_pos
        
        # # Build the grid using assets.
        # objs_in_grid = self.build_minigrid(
        #     grid_size=grid_size,
        #     player_pos=self.player_grid_pos,
        #     goal_pos=self.goal_pos,
        #     hazards=self.hazards_grid_pos,
        #     grid_obj_default=self.assets['grid_empty'],
        #     grid_obj_hazard=self.assets['grid_lava'],
        #     grid_obj_goal=self.assets['grid_goal'],
        # )
        # self.grid = VGroup(*[o for o in itertools.chain(*objs_in_grid)])
        # self.grid.arrange_in_grid(rows=grid_size[0], cols=grid_size[1], buff=0)
        
        # self.player = self.assets['player'].copy()
        # # player_pos = (0,0)
        # player_target_pos = self.grid[self.player_grid_pos[0]*grid_size[0] + self.player_grid_pos[1]].get_center()
        # self.player.move_to(player_target_pos)
        # self.world = VGroup(self.player, self.grid)
        self.world = self.build_minigrid(
            grid_size=grid_size,
            player_pos=self.player_grid_pos,
            goal_pos=self.goal_pos,
            hazards=self.hazards_grid_pos,
            grid_obj_default=self.assets['grid_empty'],
            grid_obj_hazard=self.assets['grid_lava'],
            grid_obj_goal=self.assets['grid_goal'],
            grid_obj_player=self.assets['player'],
        )
        
        # IMPORTANT - we must add all sub-objects that we want displayed.
        self.add(self.world)
        
        self.ref_player_pos = VectorizedPoint(self.world['player'].get_center())
    
    def pos_to_index(self, pos: tuple[int,int]) -> int:
        """Converts a 2D position to a 1D index."""
        return pos[0]*self.grid_size[0] + pos[1]
    
    def index_to_pos(self, index: int) -> tuple[int,int]:
        """Converts a 1D index to a 2D position."""
        return (index//self.grid_size[0], index%self.grid_size[1])


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
        # grid_obj_player: Mobject = obj_player,
        ) -> VDict:
        """Helper function to generate a MiniGrid environment.
        
        Returns a 2D matrix of Manim `VMobject`.
        """
        if player_pos == None: # Defaults to top-left.
            player_pos = (0,0)
        if goal_pos == None: # Defaults to bottom-right.
            goal_pos = (grid_size[0]-1, grid_size[1]-1)
        
        # # Support for negative indexing.
        # def negative_index_rollover(i: int, size: int):
        #     return i if i >= 0 else i+size
        # player_pos = tuple(negative_index_rollover(i, size) for i,size in zip(player_pos, grid_size))
        # goal_pos = tuple(negative_index_rollover(i, size) for i,size in zip(goal_pos, grid_size))
        # hazards = [tuple(negative_index_rollover(i, size) for i,size in zip(haz, grid_size)) for haz in hazards]

        # Build the grid.
        rows = []
        for r in range(grid_size[0]):
            cols = []
            for c in range(grid_size[1]):
                # if (r,c) == player_pos:
                #     cols.append(grid_obj_player.copy())
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
        # player_pos = (0,0)
        player_target_pos = grid[player_pos[0]*grid_size[0] + player_pos[1]].get_center()
        player.move_to(player_target_pos)
        # world = VGroup(player, grid)
        world = VDict({
            'player': player,
            'grid': grid,
        })
        return world
    
    def animate_move_player(self, action: MinigridAction, *args, **kwargs) -> Animation:
        return MiniGridMovePlayer(self, action, *args, **kwargs)

    # def move_player(self, direction: manim.typing.Vector3D):
    #     """Move player relative direction using one of (UP, LEFT, DOWN, RIGHT)."""
        
    #     # assert direction in (UP, LEFT, DOWN, RIGHT), "Can only move player UP/LEFT/DOWN/RIGHT."
        
    #     r,c = self.player_grid_pos
        
    #     # Calculate turning angle relative to current angle.
    #     if (direction == UP).all():
    #         turn_angle = 360
    #         r -= 1
    #     elif (direction == LEFT).all():
    #         turn_angle = 90
    #         c -= 1
    #     elif (direction == DOWN).all():
    #         turn_angle = 180
    #         r += 1
    #     elif (direction == RIGHT).all():
    #         turn_angle = 270
    #         c += 1
    #     new_angle = (turn_angle - self.player_look_angle)
        
    #     # Update current player look angle.
    #     self.player_look_angle = turn_angle
        
    #     # Perform animation for rotation and shift.
    #     if (r >= 0 and r < self.grid_size[0]) and (c >= 0 and c < self.grid_size[1]):
    #         self.player_grid_pos = (r,c)
    #         # return self.player.rotate(new_angle*DEGREES).shift(direction)
    #         self.world['player'].rotate(new_angle*DEGREES).shift(direction)
    #     # Boundary of grid reached, only perform rotation.
    #     else:
    #         # return self.player.rotate(new_angle*DEGREES)
    #         self.world['player'].rotate(new_angle*DEGREES)
        
    #     return self

    def move_player_forward(self):
        """Move player forward in the direction it is facing."""
        r,c = self.player_grid_pos
        if self.player_look_angle % 360 == 0:
            shift_direction = UP
            r -= 1
        elif self.player_look_angle == 90:
            shift_direction = LEFT
            c -= 1
        elif self.player_look_angle == 180:
            shift_direction = DOWN
            r += 1
        elif self.player_look_angle == 270:
            shift_direction = RIGHT
            c += 1
        
        # Only move if does not exceed grid boundary.
        if (r >= 0 and r < self.grid_size[0]) and (c >= 0 and c < self.grid_size[1]):
            self.player_grid_pos = (r,c)
            # return self.player.shift(shift_direction)
            self.world['player'].shift(shift_direction)
            self.world['player'].set_angle
        
        return self

    def move_player_left(self):
        """Move player left."""
        turn_amount = +90
        new_angle = (self.player_look_angle + turn_amount)
        self.player_look_angle = new_angle % 360
        self.world['player'].rotate(turn_amount*DEGREES)
        return self
    
    def move_player_right(self):
        """Move player right."""
        turn_amount = -90
        new_angle = (self.player_look_angle + turn_amount)
        self.player_look_angle = new_angle % 360
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


    def player_action(self, action: MinigridAction, *args, **kwargs):
        """Moves player corresponding to an action, which is one of (LEFT, RIGHT, FORWARD)."""
        
        # print(f"{self.player_look_angle=}, {self.player_grid_pos=}")
        
        print(f"{kwargs=}")
        anims = []
        alpha = kwargs.get('alpha', 1.)
        
        # THIS IS NOT WORKING
        # self.world['player'].move_to(self.ref_player_pos.get_center())
        
        if action in (MinigridAction.LEFT, MinigridAction.RIGHT):
            if action == MinigridAction.LEFT:
                turn_amount = +90*alpha
                new_angle = (self.player_look_angle + turn_amount)
            elif action == MinigridAction.RIGHT:
                turn_amount = -90*alpha
                new_angle = (self.player_look_angle + turn_amount)
            self.player_look_angle = new_angle % 360
            # return self.world['player'].rotate(turn_amount*DEGREES)
            self.world['player'].rotate(turn_amount*DEGREES*alpha)
            # anims.append(
            #     self.world['player'].animate.rotate(turn_amount*DEGREES)
            # )

        elif action == MinigridAction.FORWARD:
            r,c = self.player_grid_pos
            if self.player_look_angle % 360 == 0:
                shift_direction = UP
                r -= 1*alpha
            elif self.player_look_angle == 90:
                shift_direction = LEFT
                c -= 1*alpha
            elif self.player_look_angle == 180:
                shift_direction = DOWN
                r += 1*alpha
            elif self.player_look_angle == 270:
                shift_direction = RIGHT
                c += 1*alpha

            # Only move if does not exceed grid boundary.
            # print(f"{(r,c)=}, {(r >= 0 and r < self.grid_size[0]) and (c >= 0 and c < self.grid_size[1])}")
            if (r >= 0 and r < self.grid_size[0]) and (c >= 0 and c < self.grid_size[1]):
                self.player_grid_pos = (r,c)
                self.ref_player_pos.shift(shift_direction)
                # print(f"{(r,c)=}, {(r >= 0 and r < self.grid_size[0]) and (c >= 0 and c < self.grid_size[1])}")
                # return self.world['player'].shift(shift_direction)
                # return self.world['player'].animate.shift(shift_direction)
                self.world['player'].shift(shift_direction*alpha)
                # anims.append(
                #     self.world['player'].animate.shift(shift_direction)
                # )
            
            # # Play a flash whenever the maze is solved.
            # if self.player_grid_pos == self.goal_pos:
            #     anims.append(
            #         Flash(self.world['grid'][self.goal_pos[0]*self.grid_size[0] + self.goal_pos[1]], color=GREEN),
            #     )
            #     return LaggedStart(*anims, *args, **kwargs, lag_ratio=0.15)
        
        return self
        # return AnimationGroup(*anims, *args, **kwargs)
    
    def animate_player_action(self, action: MinigridAction, *args, **kwargs) -> AnimationGroup:
        
        # pos_before = self.player_grid_pos
        # anims = []
        # anims.append(
        #     self.animate.player_action(action),
        # )
        # pos_after = self.player_grid_pos
        # print(f"{pos_before=}, {pos_after=}")
        # if self.player_grid_pos == self.goal_pos:
        #     anims.append(
        #         Flash(self.world['grid'][self.goal_pos[0]*self.grid_size[0] + self.goal_pos[1]]),
        #     )
        
        # return AnimationGroup(*anims, *args, **kwargs)
        
        ############
        
        anims = []
        print(action)
        
        if action in (MinigridAction.LEFT, MinigridAction.RIGHT):
            if action == MinigridAction.LEFT:
                turn_amount = +90
                new_angle = (self.player_look_angle + turn_amount)
            elif action == MinigridAction.RIGHT:
                turn_amount = -90
                new_angle = (self.player_look_angle + turn_amount)
            self.player_look_angle = new_angle % 360
            # return self.world['player'].rotate(turn_amount*DEGREES)
            # self.world['player'].animate.rotate(turn_amount*DEGREES)
            anims.append(
                self.world['player'].animate.rotate(turn_amount*DEGREES)
            )

        elif action == MinigridAction.FORWARD:
            r,c = self.player_grid_pos
            if self.player_look_angle % 360 == 0:
                shift_direction = UP
                r -= 1
            elif self.player_look_angle == 90:
                shift_direction = LEFT
                c -= 1
            elif self.player_look_angle == 180:
                shift_direction = DOWN
                r += 1
            elif self.player_look_angle == 270:
                shift_direction = RIGHT
                c += 1

            # Only move if does not exceed grid boundary.
            # print(f"{(r,c)=}, {(r >= 0 and r < self.grid_size[0]) and (c >= 0 and c < self.grid_size[1])}")
            if (r >= 0 and r < self.grid_size[0]) and (c >= 0 and c < self.grid_size[1]):
                self.player_grid_pos = (r,c)
                self.ref_player_pos.shift(shift_direction)
                # print(f"{(r,c)=}, {(r >= 0 and r < self.grid_size[0]) and (c >= 0 and c < self.grid_size[1])}")
                # return self.world['player'].shift(shift_direction)
                # return self.world['player'].animate.shift(shift_direction)
                # self.world['player'].shift(shift_direction)
                anims.append(
                    self.world['player'].animate.shift(shift_direction)
                )
        print(anims)
        if anims:
            return AnimationGroup(*anims)
        else:
            return []


class MiniGridMovePlayer(Animation):
    def __init__(self, minigrid, action, **kwargs):
        super().__init__(minigrid, **kwargs)
        
        self.minigrid = minigrid
        self.action = action
        
        # self.player_start_center = self.minigrid.world['player'].get_center()
        # if self.action in (MinigridAction.LEFT, MinigridAction.RIGHT):
        #     self.player_end_center = self.player_start_center
        # else:
        #     r,c = self.minigrid.player_grid_pos
        #     if self.minigrid.player_look_angle % 360 == 0:
        #         shift_direction = UP
        #         r -= 1
        #     elif self.minigrid.player_look_angle == 90:
        #         shift_direction = LEFT
        #         c -= 1
        #     elif self.minigrid.player_look_angle == 180:
        #         shift_direction = DOWN
        #         r += 1
        #     elif self.minigrid.player_look_angle == 270:
        #         shift_direction = RIGHT
        #         c += 1
            
        #     # Only move if does not exceed grid boundary.
        #     if (r >= 0 and r < self.minigrid.grid_size[0]) and (c >= 0 and c < self.minigrid.grid_size[1]):
        #         self.minigrid.player_grid_pos = (r,c)
        #         self.player_end_center = self.player_start_center + shift_direction
        #     else:
        #         self.player_end_center = self.player_start_center
    
    def begin(self):
        self.player_start_angle = self.minigrid.player_look_angle
        self.player_current_angle = self.player_start_angle
        
        r,c = self.minigrid.player_grid_pos
        # self.player_start_center = self.minigrid.world['player'].get_center()
        self.player_start_center = self.minigrid.world['grid'][self.minigrid.pos_to_index((r,c))].get_center()
        if self.action in (MinigridAction.LEFT, MinigridAction.RIGHT):
            self.player_end_center = self.player_start_center

            self.turn_amount_current = 0
            if self.action == MinigridAction.LEFT:
                self.turn_amount = +90
                new_angle = (self.player_start_angle + self.turn_amount)
                self.player_end_angle = new_angle % 360
                # if self.player_end_angle == 0:
                #     self.player_end_angle = 360
                # self.world['player'].rotate(turn_amount*DEGREES)
            elif self.action == MinigridAction.RIGHT:
                self.turn_amount = -90
                new_angle = (self.player_start_angle + self.turn_amount)
                self.player_end_angle = new_angle % 360
                # if self.player_end_angle == 0:
                #     self.player_end_angle = 360
                print(f"{self.player_end_angle=}")
                # self.world['player'].rotate(turn_amount*DEGREES)
        elif self.action == MinigridAction.FORWARD:
            r,c = self.minigrid.player_grid_pos
            if self.minigrid.player_look_angle % 360 == 0:
                shift_direction = UP
                r -= 1
            elif self.minigrid.player_look_angle == 90:
                shift_direction = LEFT
                c -= 1
            elif self.minigrid.player_look_angle == 180:
                shift_direction = DOWN
                r += 1
            elif self.minigrid.player_look_angle == 270:
                shift_direction = RIGHT
                c += 1
            
            # Only move if does not exceed grid boundary.
            if (r >= 0 and r < self.minigrid.grid_size[0]) and (c >= 0 and c < self.minigrid.grid_size[1]):
                self.minigrid.player_grid_pos = (r,c)
                print(f"{self.minigrid.player_grid_pos=}")
                # self.player_end_center = self.player_start_center + shift_direction
                self.player_end_center = self.minigrid.world['grid'][self.minigrid.pos_to_index((r,c))].get_center()
            else:
                self.player_end_center = self.player_start_center
        
        print('END OF BEGIN')
        super().begin()
    
    def interpolate_mobject(self, alpha: float):
        # Alpha will go from 0 to 1 and will be used to interpolate the movement within the grid.
        # This method is required for use with Succession().
        # self.minigrid.player_action(self.action, alpha=alpha)
        # # self.minigrid.animate.player_action(self.action)
        # # self.minigrid.player_action(self.action)
        # # self.minigrid.animate.player_action(self.action)
        # print(f"{alpha=}, {self.rate_func(alpha)=}, {self.rate_func=}")
        if self.action in (MinigridAction.LEFT, MinigridAction.RIGHT):
            # self.minigrid.world['player'].move_to(self.player_start_center)
            # new_angle = (self.player_start_angle + alpha*(self.player_end_angle - self.player_start_angle)) % 360
            # new_angle = (self.player_start_angle + alpha*(self.player_end_angle - self.player_start_angle)) % 360
            # print(f"HERE: {self.player_end_angle - self.player_start_angle=}, {new_angle=}, {self.player_start_angle=}, {self.player_end_angle=}, {self.player_current_angle}, {alpha=}")
            # print(f"HERE: {self.minigrid.world['player'][0].get_center()}")
            # print(f"{new_angle=}, {(new_angle - self.player_current_angle)}, {(new_angle - self.player_current_angle)%360}")
            # self.minigrid.world['player'].rotate((new_angle - self.player_current_angle))
            # print(f"{alpha=}, {self.action=}, {self.player_start_angle=}, {self.player_end_angle=}")
            # current_rotation = (self.player_start_angle + alpha*(self.player_end_angle - self.player_start_angle)) % 360
            # current_rotation = self.player_start_angle + alpha*self.turn_amount
            incremental_rotation = alpha*self.turn_amount - self.turn_amount_current
            self.minigrid.world['player'].rotate(incremental_rotation*DEGREES)
            self.turn_amount_current += incremental_rotation
            # self.minigrid.world['player'].rotate(alpha*(self.turn_amount - self.turn_amount_current)*DEGREES)
            # self.turn_amount_current = alpha*(self.turn_amount - self.turn_amount_current)
            # self.minigrid.world['player'].rotate(alpha*(self.player_end_angle - self.player_start_angle))
            # self.minigrid.world['player'][0].rotate((new_angle - self.player_current_angle)*DEGREES)
            # self.minigrid.world['player'].rotate(alpha*(self.player_end_angle - self.player_current_angle)*DEGREES)
            # self.player_current_angle = new_angle - self.player_current_angle
            # self.minigrid.world['player'][0].rotate(PI/2)
        elif self.action == MinigridAction.FORWARD:
            new_position = self.player_start_center + alpha*(self.player_end_center - self.player_start_center)
            self.minigrid.world['player'].move_to(new_position)
    
    def finish(self):
        if self.action in (MinigridAction.LEFT, MinigridAction.RIGHT):
            pass
            # self.minigrid.world['player'].rotate(self.player_end_angle*DEGREES)
            # self.minigrid.world['player'].rotate((self.player_end_angle)*DEGREES)
            # self.minigrid.world['player'].rotate((self.player_end_angle - self.player_current_angle)*DEGREES)
            # print(f"{self.player_current_angle=}, {self.player_end_angle=}, {(self.player_end_angle - self.player_current_angle)=}")
            # self.minigrid.world['player'].rotate(0)
            # self.minigrid.world['player'].rotate(self.player_end_angle*DEGREES)
            incremental_rotation = self.turn_amount - self.turn_amount_current
            self.minigrid.world['player'].rotate(incremental_rotation*DEGREES)
            self.minigrid.player_look_angle = self.player_end_angle
            pass
        elif self.action == MinigridAction.FORWARD:
            self.minigrid.world['player'].move_to(self.player_end_center)
    
    
    # def move_player_forward(self, alpha: float):
    #     """Move player forward in the direction it is facing."""
    #     r,c = self.player_grid_pos
    #     if self.player_look_angle % 360 == 0:
    #         shift_direction = UP
    #         r -= 1
    #     elif self.player_look_angle == 90:
    #         shift_direction = LEFT
    #         c -= 1
    #     elif self.player_look_angle == 180:
    #         shift_direction = DOWN
    #         r += 1
    #     elif self.player_look_angle == 270:
    #         shift_direction = RIGHT
    #         c += 1
        
    #     # Only move if does not exceed grid boundary.
    #     if (r >= 0 and r < self.grid_size[0]) and (c >= 0 and c < self.grid_size[1]):
    #         self.player_grid_pos = (r,c)
    #         # return self.player.shift(shift_direction)
    #         self.world['player'].shift(shift_direction)
    #         # self.world['player'].set_angle
        
    #     return self

    # def move_player_left(self, alpha: float):
    #     """Move player left."""
    #     turn_amount = +90
    #     new_angle = (self.player_look_angle + turn_amount)
    #     self.player_look_angle = new_angle % 360
    #     self.world['player'].rotate(turn_amount*DEGREES)
    #     return self
    
    # def move_player_right(self, alpha: float):
    #     """Move player right."""
    #     turn_amount = -90
    #     new_angle = (self.player_look_angle + turn_amount)
    #     self.player_look_angle = new_angle % 360
    #     self.world['player'].rotate(turn_amount*DEGREES)
    #     return self

    # def move_player(self, action: MinigridAction, alpha: float):
    #     """Moves player corresponding to an action, which is one of (LEFT, RIGHT, FORWARD)."""
        
    #     if action == MinigridAction.LEFT:
    #         return self.move_player_left()
    #     elif action == MinigridAction.RIGHT:
    #         return self.move_player_right()
    #     elif action == MinigridAction.FORWARD:
    #         return self.move_player_forward()


class GridTest(Scene):
    def construct(self):
        grid = MiniGrid(
            grid_size=(5,5),
            hazards_grid_pos=[
                (1,1),
                (1,2),
                (1,3),
            ],
            goal_grid_pos=(-1,-1),
            player_grid_pos=(0,0),
        )
        grid = grid.scale(0.5)
        
        # grid.world['player'].rotate((45)*DEGREES)
        
        self.add(grid)
        # self.play(Create(grid))
        
        # self.play(grid.grid[0].animate.rotate(90*DEGREES))
        # self.play(grid.grid[0].animate.rotate(90*DEGREES))
        
        actions = [
            MinigridAction.FORWARD,
            # MinigridAction.FORWARD,
            # MinigridAction.FORWARD,
            # MinigridAction.FORWARD,
            MinigridAction.RIGHT,
            MinigridAction.FORWARD,
            # MinigridAction.FORWARD,
            # MinigridAction.FORWARD,
            # MinigridAction.FORWARD,
        ]
        # print(f"{grid.player_grid_pos=}")
        # for a in actions:
        #     self.play(grid.animate.player_action(a), run_time=0.5)
        # self.play(Succession(*[
        #     # ApplyMethod(grid.player_action, a)
        #     grid.animate.player_action(a)
        #     for a in actions]))
        
        
        
        # Play the actions and then add the grid.
        # a1 = MiniGridMovePlayer(grid, MinigridAction.FORWARD)
        # a2 = MiniGridMovePlayer(grid, MinigridAction.FORWARD)
        action = MinigridAction.LEFT
        print(action)
        self.play(Succession(*[
            # MiniGridMovePlayer(grid, MinigridAction.FORWARD, run_time=0.5),
            # MiniGridMovePlayer(grid, MinigridAction.FORWARD, run_time=0.5),
            # MiniGridMovePlayer(grid, MinigridAction.FORWARD, run_time=0.5),
            # MiniGridMovePlayer(grid, MinigridAction.FORWARD, run_time=0.5),
            # MiniGridMovePlayer(grid, MinigridAction.FORWARD, run_time=0.5),
            # MiniGridMovePlayer(grid, MinigridAction.FORWARD, run_time=0.5),
            # MiniGridMovePlayer(grid, MinigridAction.FORWARD, run_time=0.5),
            # MiniGridMovePlayer(grid, MinigridAction.FORWARD, run_time=0.5),
            # MiniGridMovePlayer(grid, action, run_time=5),
            # MiniGridMovePlayer(grid, MinigridAction.LEFT, run_time=1),
            # MiniGridMovePlayer(grid, MinigridAction.RIGHT, run_time=0.5),
            # MiniGridMovePlayer(grid, MinigridAction.RIGHT, run_time=0.5),
            # MiniGridMovePlayer(grid, MinigridAction.RIGHT, run_time=0.5),
            # MiniGridMovePlayer(grid, MinigridAction.LEFT, run_time=0.5),
            # MiniGridMovePlayer(grid, MinigridAction.RIGHT, run_time=0.5),
            # MiniGridMovePlayer(grid, MinigridAction.FORWARD, run_time=0.5),
            # MiniGridMovePlayer(grid, MinigridAction.FORWARD, run_time=0.5),
            grid.animate_move_player(MinigridAction.FORWARD),
            grid.animate_move_player(MinigridAction.FORWARD),
            grid.animate_move_player(MinigridAction.RIGHT),
            grid.animate_move_player(MinigridAction.FORWARD),
            grid.animate_move_player(MinigridAction.FORWARD),
        ], lag_ratio=1), run_time=1)
        # self.play(MiniGridMovePlayer(grid, MinigridAction.LEFT))
        # self.play(MiniGridMovePlayer(grid, MinigridAction.LEFT))
        # self.play(MiniGridMovePlayer(grid, MinigridAction.LEFT))
        # self.play(Succession(*[
        #     MiniGridMovePlayer(grid, MinigridAction.FORWARD),
        # ], lag_ratio=1))
        print(f"{grid.player_grid_pos=}")
        # for a in actions:
        #     # grid.player_action(a)
        #     self.play(grid.animate.move_player(a), )
        # self.add(grid)
        
        # self.play(Succession(*[
        #     grid.animate_player_action(MinigridAction.FORWARD),
        #     grid.animate_player_action(MinigridAction.FORWARD),
        #     grid.animate_player_action(MinigridAction.FORWARD),
        #     grid.animate_player_action(MinigridAction.RIGHT),
        # ], lag_ratio=1))
        
        # self.play(
        #     Succession(
        #         # grid.animate.player_action(MinigridAction.FORWARD),
        #         # grid.animate.player_action(MinigridAction.FORWARD),
        #         # grid.animate.player_action(MinigridAction.RIGHT),
        #         MiniGridMovePlayer(grid, MinigridAction.FORWARD),
        #         MiniGridMovePlayer(grid, MinigridAction.RIGHT),
        #         MiniGridMovePlayer(grid, MinigridAction.FORWARD),
        #         lag_ratio=1
        #     )
        # )
        
        # for a in actions:
        #     self.play(grid.animate.player_action(a))
        
        self.wait()



class EnvironmentIntroduction(Scene):
    def construct(self):
        
        
        
        # t1.
        t1 = Tex("What is MiniGrid?")
        self.play(Write(t1)) # Animates text writing.
        self.play(t1.animate.shift(UP*3))
        # self.play(FadeOut(t1)) # Animates text fading out.
        
        
        # Create a grid using matrix design.
        grid_size = (5,5)
        ###########
        # objs_in_grid = build_minigrid(
        #     grid_size=grid_size,
        #     player_pos=(0,0),
        #     goal_pos=(4,4),
        #     hazards=[
        #         (1,1),
        #         (1,2),
        #         (1,3),
        #     ],
        # )
        # grid = VGroup(*[o for o in itertools.chain(*objs_in_grid)])
        # grid.arrange_in_grid(rows=grid_size[0], cols=grid_size[1], buff=0)
        
        # player = obj_player_core.copy()
        # player_pos = (0,0)
        # player_target_pos = grid[player_pos[0]*grid_size[0] + player_pos[1]].get_center()
        # player.move_to(player_target_pos)
        # grid = VGroup(player, grid)
        # grid = grid.scale(0.5)
        ###########
        grid = MiniGrid(
            grid_size=(5,5),
            hazards_grid_pos=[
                (1,1),
                (1,2),
                (1,3),
            ],
            goal_grid_pos=(-1,-1)
        )
        grid = grid.scale(0.5)
        ###########
        
        # self.play(Write(grid))
        # self.play(grid.animate.shift(LEFT*2))
        
        # grid = grid.shift(LEFT*2)
        
        
        t2 = Tex(r"This is an example of a $5 \times 5$ grid for 1 player:").move_to(t1.get_center())
        
        self.play(
            ReplacementTransform(t1, t2),
            Write(grid),
        )
        self.play(
            grid.animate.align_to(t2, LEFT),
        )
        
        
        # Introduce the grid.
        vgroup = VGroup(*[
            VGroup(*[
                grid.assets['grid_empty'].copy().scale(0.25),
                Tex("Empty grid square"),
            ]).arrange(),
            VGroup(*[
                grid.assets['grid_lava'].copy().scale(0.25),
                Tex("Lava hazard"),
            ]).arrange(),
            VGroup(*[
                grid.assets['grid_goal'].copy().scale(0.25),
                Tex("Goal"),
            ]).arrange(),
            VGroup(*[
                grid.assets['player'].copy().scale(0.25),
                Tex("Player"),
            ]).arrange(),
        ])
        vgroup.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        
        vgroup.next_to(grid, RIGHT)
        self.play(Write(vgroup))
        
        
        
        # Describe the actions.
        t3 = Tex(r"The player can take actions $a \in \{\textrm{LEFT}, \textrm{RIGHT}, \textrm{FORWARD}\}$").scale(0.6)
        t3.next_to(grid, DOWN, aligned_edge=LEFT)
        self.play(Write(t3))
        
        # Animate the player moving around a little.
        actions = [
            MinigridAction.FORWARD,
            MinigridAction.FORWARD,
            MinigridAction.FORWARD,
            MinigridAction.FORWARD,
            MinigridAction.RIGHT,
            MinigridAction.FORWARD,
            MinigridAction.FORWARD,
            MinigridAction.FORWARD,
            MinigridAction.FORWARD,
        ]
        for a in actions:
            self.play(grid.animate.player_action(a), run_time=0.5)
        
        
        self.wait()





class IntroductionScene(Scene):
    def construct(self):
        

        # title_short = Text("eQMARL", t2c={'Q': PURPLE}).scale(1.5)
        # self.play(Write(title_short))
        
        # title_long = Text("Entangled Quantum Multi-Agent Reinforcement Learning", t2c={'Quantum': PURPLE})
        
        # title_long = title_long.scale(0.75)
        # title_long.next_to(title_short, DOWN, buff=0.5)

        # self.play(ReplacementTransform(title_short[0], title_long[0:9]))
        # self.play(ReplacementTransform(title_short[1], title_long[9:16]))
        # self.play(ReplacementTransform(title_short[2:4], title_long[16:27]))
        # self.play(ReplacementTransform(title_short[4], title_long[27:40]))
        # self.play(ReplacementTransform(title_short[5], title_long[40:]))
        
        
        def style1():
        
            title_long = Text("Entangled Quantum Multi-Agent Reinforcement Learning", t2c={'Quantum': PURPLE}).scale(0.8)
            
            title_short = Text("eQMARL", t2c={'Q': PURPLE}).scale(1.5)
            title_short.next_to(title_long, UP, buff=0.5)
            
            self.play(Write(title_long[0:9]), Write(title_short[0]), run_time=0.75)
            self.play(Write(title_long[9:16]), Write(title_short[1]), run_time=0.75)
            self.play(Write(title_long[16:27]), Write(title_short[2:4]), run_time=0.75)
            self.play(Write(title_long[27:40]), Write(title_short[4]), run_time=0.75)
            self.play(Write(title_long[40:]), Write(title_short[5]), run_time=0.75)
            
            self.play(ReplacementTransform(title_long, title_short[1]))
            self.play(title_short.animate.to_edge(UP))
            
            # self.play(
            #     title_short.animate.to_edge(UP),
            #     FadeOut(title_long),
            # )
        
        
        def style2():
            title_long = Text("Entangled Quantum Multi-Agent Reinforcement Learning", t2c={'Quantum': PURPLE}).scale(0.8)
            self.play(Write(title_long), run_time=2)
            title_long_words = [
                title_long[0:9],
                title_long[9:16],
                title_long[16:27],
                title_long[27:40],
                title_long[40:],
            ]
            
            title_short = Text("eQMARL", t2c={'Q': PURPLE}).scale(1.5)
            title_short_letters = [
                title_short[0],
                title_short[1],
                title_short[2:4],
                title_short[4],
                title_short[5],
            ]
            # title_short_letters[0].next_to(title_long_words[1], LEFT)
            # title_short_letters[1].next_to(title_long_words[2], LEFT)
            # title_short_letters[3].next_to(title_long_words[3], LEFT)
            # title_short_letters[4].next_to(title_long_words[3], RIGHT)
            
            title_short_letters[0].next_to(title_long_words[1], LEFT)
            self.play(ReplacementTransform(title_long_words[0], title_short_letters[0]))
            
            self.play(ReplacementTransform(title_long_words[1], title_short_letters[1]))
            # title_short_letters[1].next_to(title_short_letters[0], RIGHT)
            # self.play(
            #     ReplacementTransform(title_long_words[1], title_short_letters[1]),
            #     title_short[0:2].animate.next_to(title_long_words[2], LEFT),
            #     )
            
            
            self.play(ReplacementTransform(title_long_words[2], title_short_letters[2]))
            self.play(ReplacementTransform(title_long_words[3], title_short_letters[3]))
            self.play(ReplacementTransform(title_long_words[4], title_short_letters[4]))
            
            self.play(title_short.animate.to_edge(UP))
        
        
        def style3():
            title_short = Text("eQMARL", t2c={'Q': PURPLE})
            title_short = title_short.scale(1.5)
            title_short_glyphs = [
                title_short[0],
                title_short[1],
                title_short[2:4],
                title_short[4],
                title_short[5],
            ]
            
            underlines = [Underline(glyph, color=RED) for glyph in title_short_glyphs]
            
            title_long = Text("Entangled Quantum Multi-Agent Reinforcement Learning", t2c={'Quantum': PURPLE})
            title_long = title_long.scale(0.75)
            title_long.next_to(title_short, DOWN, buff=0.5)
            title_long_glyphs = [
                title_long[0:9],
                title_long[9:16],
                title_long[16:27],
                title_long[27:40],
                title_long[40:],
            ]
            
            self.play(Write(title_short))
            self.play(
                GrowFromPoint(title_long_glyphs[0], title_short_glyphs[0].get_center()),
                GrowFromCenter(underlines[0]),
                )
            self.play(
                GrowFromPoint(title_long_glyphs[1], title_short_glyphs[1].get_center()),
                ReplacementTransform(underlines[0], underlines[1]),
            )
            self.play(
                GrowFromPoint(title_long_glyphs[2], title_short_glyphs[2].get_center()),
                ReplacementTransform(underlines[1], underlines[2]),
            )
            self.play(
                GrowFromPoint(title_long_glyphs[3], title_short_glyphs[3].get_center()),
                ReplacementTransform(underlines[2], underlines[3]),
            )
            self.play(
                GrowFromPoint(title_long_glyphs[4], title_short_glyphs[4].get_center()),
                ReplacementTransform(underlines[3], underlines[4]),
            )
            self.play(ShrinkToCenter(underlines[-1]), ShrinkToCenter(title_long), run_time=0.25)
            ######
            # self.play(ReplacementTransform(title_short_glyphs[0], title_long_glyphs[0]))
            # self.play(ReplacementTransform(title_short_glyphs[1], title_long_glyphs[1]))
            # self.play(ReplacementTransform(title_short_glyphs[2], title_long_glyphs[2]))
            # self.play(ReplacementTransform(title_short_glyphs[3], title_long_glyphs[3]))
            # self.play(ReplacementTransform(title_short_glyphs[4], title_long_glyphs[4]))
            ######
            self.play(title_short.animate.to_edge(UP).scale(0.5))
        
        
        ######
        
        # style1()
        # style2()
        style3()
        
        # title_long = Text("Entangled Quantum Multi-Agent Reinforcement Learning", t2c={'Quantum': PURPLE}).scale(0.8)
        # self.play(Write(title_long), run_time=2)
        
        # # self.play(Write(title_long[0:9]), run_time=0.75)
        # # self.play(Write(title_long[9:16]), run_time=0.75)
        # # self.play(Write(title_long[16:27]), run_time=0.75)
        # # self.play(Write(title_long[27:40]), run_time=0.75)
        # # self.play(Write(title_long[40:]), run_time=0.75)
        
        
        # title_short = Text("eQMARL", t2c={'Q': PURPLE}).scale(1.5)
        # # title_short.next_to(title_long, UP, buff=0.5)
        # # title_short.next_to(title_long, DOWN, buff=0.5)
        # # self.play(ReplacementTransform(title_long[0:9], title_short[0]))
        # # self.play(ReplacementTransform(title_long[9:16], title_short[1]))
        # # self.play(ReplacementTransform(title_long[16:27], title_short[2:4]))
        # # self.play(ReplacementTransform(title_long[27:40], title_short[4]))
        # # self.play(ReplacementTransform(title_long[40:], title_short[5]))
        
        # # self.play(ReplacementTransform(title_long, title_short), run_time=1.5)
        
        
        # self.play(ReplacementTransform(title_long[0:9], title_short[0]))
        # self.play(ReplacementTransform(title_long[9:16], title_short[1]))
        # self.play(ReplacementTransform(title_long[16:27], title_short[2:4]))
        # self.play(ReplacementTransform(title_long[27:40], title_short[4]))
        # self.play(ReplacementTransform(title_long[40:], title_short[5]))
        
        
        # self.play(title_short.animate.to_edge(UP))
        
        
        
        self.wait()





class Qubit(VMobject):
    
    config = {
        'text_top_color': WHITE,
        'text_bottom_color': WHITE,
        'dots_origin_color': GRAY,
        'dots_top_color': WHITE,
        'dots_bottom_color': WHITE,
        'arrow_color': GRAY,
        'arrow_stroke_width': 6,
        'circle_color': BLUE,
        'ellipse_color': BLUE,
    }
    
    def __init__(self, **kwargs):
        super().__init__()
        
        # Merge the default config with any user-provided config.
        self.config.update(kwargs)
        
        
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
        # shapes.set_color(BLUE_D)
        # dots.set_color(WHITE)
        # dots['origin'].set_color(GRAY)
        # arrow.set_color(GRAY)
        
        text = VGroup(*[
            MathTex(r"|0\rangle", color=self.config['text_top_color']).next_to(dots['top'], UP),
            MathTex(r"|1\rangle", color=self.config['text_bottom_color']).next_to(dots['bottom'], DOWN),
        ])
        
        
        self.group = VDict({
            'shapes': shapes,
            'text': text,
        })
        self.add(self.group)
    
    def set_state_angle(self, angle: float):
        return self.group['shapes']['arrow'].put_start_and_end_on(self.group['shapes']['circle'].get_center(), self.group['shapes']['circle'].point_at_angle(angle))




class EntangledQubits(VMobject):
    
    config = {
        'qubit_0': Qubit.config.copy(),
        'qubit_1': Qubit.config.copy(),
        'wave_0_color': BLUE_C,
        'wave_1_color': BLUE_E,
    }
    
    def __init__(self, **kwargs):
        super().__init__()
        
        # Merge the default config with any user-provided config.
        self.config.update(kwargs)
        
        # 2 qubits within object.
        self.qubits: VGroup[Qubit] = VGroup(*[
            Qubit(**self.config['qubit_0']),
            Qubit(**self.config['qubit_1']),
        ])
        self.qubits[0].shift(LEFT*3)
        self.qubits[1].shift(RIGHT*3)
        
        # Tracker for animating the entanglement waves.
        self.tracker = ValueTracker(0)
        
        # self.reference_height = ValueTracker(abs(self.qubits[0].get_y(DOWN) - self.qubits[0].get_y(UP))*0.75)
        self.reference_height = ValueTracker(self.qubits[0].group['shapes']['circle'].height*0.75)
        self.reference_width = ValueTracker(abs(self.qubits[1].get_x(LEFT) - self.qubits[0].get_x(RIGHT)))
        self.reference_point = VectorizedPoint((self.qubits[0].get_x(RIGHT) + self.qubits[1].get_x(LEFT))/2 * RIGHT)
        
        # self.center_point_tracker = ValueTracker((self.qubits[0].get_x(RIGHT) + self.qubits[1].get_x(LEFT))/2 * RIGHT)
        
        # 2 wave functions to represent entanglement.
        def create_wave_funcs():
            group = VGroup(*[
                FunctionGraph(lambda x: 0.5*np.sin(4*x + self.tracker.get_value()), color=self.config['wave_0_color'], x_range=[self.qubits[0].get_x(RIGHT), self.qubits[1].get_x(LEFT)]),
                FunctionGraph(lambda x: 0.5*np.sin(4*x - self.tracker.get_value() + 180*DEGREES), color=self.config['wave_1_color'], x_range=[self.qubits[0].get_x(RIGHT), self.qubits[1].get_x(LEFT)]),
            ])
            group.move_to(self.reference_point.get_center())
            group.scale_to_fit_width(self.reference_width.get_value())
            group.scale_to_fit_height(self.reference_height.get_value())
            # group.scale(self.reference_scale.get_value())
            return group
            
        # self.wave_graphs = VGroup(*[
        #     always_redraw(lambda: FunctionGraph(lambda x: 0.5*np.sin(4*x + self.tracker.get_value()), color=self.config['wave_0_color'], x_range=[self.qubits[0].get_x(RIGHT), self.qubits[1].get_x(LEFT)])),
        #     always_redraw(lambda: FunctionGraph(lambda x: 0.5*np.sin(4*x - self.tracker.get_value() + 180*DEGREES), color=self.config['wave_1_color'], x_range=[self.qubits[0].get_x(RIGHT), self.qubits[1].get_x(LEFT)])),
        # ])
        self.wave_graphs = always_redraw(create_wave_funcs)
        # self.wave_graphs.move_to((self.qubits[0].get_x(RIGHT) + self.qubits[1].get_x(LEFT))/2 * RIGHT)
        # self.wave_graphs.add_updater(
        #     lambda mob: mob.move_to((self.qubits[0].get_x(RIGHT) + self.qubits[1].get_x(LEFT))/2 * RIGHT)
        # )
        
        self.add(self.qubits, self.wave_graphs)
    
    # def create_wave_funcs(self):
    #     group = VGroup(*[
    #         FunctionGraph(lambda x: 0.5*np.sin(4*x + self.tracker.get_value()), color=self.config['wave_0_color'], x_range=[self.qubits[0].get_x(RIGHT), self.qubits[1].get_x(LEFT)]),
    #         FunctionGraph(lambda x: 0.5*np.sin(4*x - self.tracker.get_value() + 180*DEGREES), color=self.config['wave_1_color'], x_range=[self.qubits[0].get_x(RIGHT), self.qubits[1].get_x(LEFT)]),
    #     ])
    #     # group.move_to((self.qubits[0].get_x(RIGHT) + self.qubits[1].get_x(LEFT))/2 * RIGHT)
    #     return group
    
    def animate_waves_toggle(self) -> AnimationGroup:
        """Animates entanglement waves either forward or backward, depending on the current tracker value."""
        
        if self.tracker.get_value() == 0:
            return self.tracker.animate(run_time=1, rate_func=linear).set_value(4*np.pi)
        else:
            return self.tracker.animate(run_time=1, rate_func=linear).set_value(0)
        
    def shift(self, *args, **kwargs):
        super().shift(*args, **kwargs)
        self.reference_point.shift(*args, **kwargs)
        # self.wave_graphs.move_to((self.qubits[0].get_x(RIGHT) + self.qubits[1].get_x(LEFT))/2 * RIGHT)
        return self

    def scale(self, *args, **kwargs):
        super().scale(*args, **kwargs)
        self.reference_width.set_value(abs(self.qubits[1].get_x(LEFT) - self.qubits[0].get_x(RIGHT))*2)
        self.reference_height.set_value(self.qubits[0].group['shapes']['circle'].height*0.75)
        # self.reference_scale.set_value(*args, **kwargs)
        # self.wave_graphs.move_to((self.qubits[0].get_x(RIGHT) + self.qubits[1].get_x(LEFT))/2 * RIGHT)
        return self


class QubitScene(Scene):
    def construct(self):
        q0 = Qubit()
        self.play(Create(q0))
        self.play(q0.animate.set_state_angle(90*DEGREES))
        self.play(q0.animate.set_state_angle(180*DEGREES))
        
        self.wait()

class EntanglementScene(Scene):
    def construct(self):
        
        
        t0 = Text("Entanglement couples the behavior of quantum particles")
        t0.scale(0.5)
        t0.to_edge(UP)
        
        
        e = EntangledQubits(
            qubit_0={
                'circle_color': PURPLE,
                'ellipse_color': PURPLE,
            },
            qubit_1={
                'circle_color': PURPLE,
                'ellipse_color': PURPLE,
            }
        )
        # e.next_to(t0, DOWN)
        # self.play(Write(t0), Write(e))
        
        self.add(e)
        self.play(e.animate.shift(DOWN*2))
        self.play(e.animate.scale(0.5))
        
        # self.play(e.animate_waves_toggle())
        # self.play(e.animate_waves_toggle())
        # self.play(e.animate_waves_toggle())
        # self.play(e.animate_waves_toggle())
        
        
        
        self.play(
            e.animate_waves_toggle(),
            e.qubits[0].animate.set_state_angle(90*DEGREES),
            e.qubits[1].animate.set_state_angle(270*DEGREES),
        )
        self.play(
            e.animate_waves_toggle(),
            e.qubits[0].animate.set_state_angle(180*DEGREES),
            e.qubits[1].animate.set_state_angle(0*DEGREES),
        )
        self.play(
            e.animate_waves_toggle(),
            e.qubits[0].animate.set_state_angle(270*DEGREES),
            e.qubits[1].animate.set_state_angle(90*DEGREES),
        )
        self.play(
            e.animate_waves_toggle(),
            e.qubits[0].animate.set_state_angle(45*DEGREES),
            e.qubits[1].animate.set_state_angle(225*DEGREES),
        )
        
        self.wait()




# This is a qubit.
# The quantum analog of a classical \emph{binary} bit.






class EntangledEnvionment(Scene):
    
    def construct(self):
        
        # def create_env_qubit_group():
        #     env = MiniGrid(
        #         grid_size=(5,5),
        #         hazards_grid_pos=[
        #             (1,1),
        #             (1,2),
        #             (1,3),
        #         ],
        #         goal_grid_pos=(-1,-1)
        #     ).scale(0.3)
        #     qubit = Qubit(arrow_stroke_width=12).scale(0.4)
        #     qubit.next_to(env, UP)
        #     return VDict(dict(env=env, qubit=qubit))
        
        
        env_0 = MiniGrid(
            grid_size=(5,5),
            hazards_grid_pos=[
                (1,1),
                (1,2),
                (1,3),
            ],
            goal_grid_pos=(-1,-1)
        ).scale(0.3)
        qubit_0 = Qubit(arrow_stroke_width=12).scale(0.4)
        qubit_0.next_to(env_0, UP)
        
        env_1 = MiniGrid(
            grid_size=(5,5),
            hazards_grid_pos=[
                (1,1),
                (2,1),
                (3,1),
            ],
            goal_grid_pos=(-1,-1)
        ).scale(0.3)
        qubit_1 = Qubit(arrow_stroke_width=12).scale(0.4)
        qubit_1.next_to(env_1, UP)
        
        
        env_qubit_groups = VGroup(*[
            VDict(dict(env=env_0, qubit=qubit_0)),
            VDict(dict(env=env_1, qubit=qubit_1)),
            # create_env_qubit_group()
            # for _ in range(2)
        ])
        env_qubit_groups[0].shift(LEFT*3)
        env_qubit_groups[1].shift(RIGHT*3)
        
        self.add(env_qubit_groups)
        
        
        qubit_anim_group = AnimationGroup(*[
            Succession(*[
                env_qubit_groups[0]['env'].animate_move_player(MinigridAction.FORWARD),
                env_qubit_groups[0]['env'].animate_move_player(MinigridAction.FORWARD),
                env_qubit_groups[0]['env'].animate_move_player(MinigridAction.RIGHT),
                env_qubit_groups[0]['env'].animate_move_player(MinigridAction.FORWARD),
            ], lag_ratio=1),
            Succession(*[
                env_qubit_groups[1]['env'].animate_move_player(MinigridAction.FORWARD),
                env_qubit_groups[1]['env'].animate_move_player(MinigridAction.FORWARD),
                env_qubit_groups[1]['env'].animate_move_player(MinigridAction.FORWARD),
                env_qubit_groups[1]['env'].animate_move_player(MinigridAction.FORWARD),
                env_qubit_groups[1]['env'].animate_move_player(MinigridAction.RIGHT),
            ], lag_ratio=1),
            # env_qubit_groups[0]['qubit'].animate.set_state_angle(90*DEGREES),
            # env_qubit_groups[0]['qubit'].animate.set_state_angle(180*DEGREES),
            # env_qubit_groups[0]['qubit'].animate.set_state_angle(270*DEGREES),
            # env_qubit_groups[0]['qubit'].animate.set_state_angle(45*DEGREES),
            # env_qubit_groups[0]['qubit'].animate.set_state_angle(225*DEGREES),
        ])
        
        self.play(qubit_anim_group)
        
        
        # self.play(env_qubit_groups[0]['qubit'].animate.set_state_angle(90*DEGREES))
        # self.play(env_qubit_groups[0]['qubit'].animate.set_state_angle(180*DEGREES))
        
        
        
        
        # envs = VGroup(*[
        #     MiniGrid(
        #         grid_size=(5,5),
        #         hazards_grid_pos=[
        #             (1,1),
        #             (1,2),
        #             (1,3),
        #         ],
        #         goal_grid_pos=(-1,-1)
        #     )
        #     for _ in range(2)
        # ])
        # envs.scale(0.3)
        # envs[0].shift(LEFT*3)
        # envs[1].shift(RIGHT*3)
        # for e in envs:
        #     e.shift(DOWN)
        
        # self.add(envs)
        
        # qubits = VGroup(*[
        #     Qubit().scale(0.3)
        #     for _ in range(len(envs))
        #     ])
        
        # for e,q in zip(envs, qubits):
        #     q.next_to(e, UP)
        
        # self.add(qubits)
        
        
        # self.play(
        #     *[
        #         envs[0].player_action(MinigridAction.FORWARD),
        #         AnimationGroup(*[
        #             envs[1].player_action(MinigridAction.RIGHT),
        #             envs[1].player_action(MinigridAction.FORWARD),
        #             ], lag_ratio=1)
        #     ],
        #     run_time=0.5)
        
        self.wait()







class TestPlot(Scene):
    def construct(self):
        
        self.qubits: VGroup[Qubit] = VGroup(*[
            Qubit(),
            Qubit(),
        ])
        self.qubits[0].shift(LEFT*3)
        self.qubits[1].shift(RIGHT*3)
        self.add(self.qubits)
        
        self.tracker = ValueTracker(0)
        
        a = Axes(x_range=[-4,4], y_range=[-1,1], tips=False)
        a.x_axis.set_stroke(width=0)
        a.y_axis.set_stroke(width=0)
        # self.play(Write(a))
        self.add(a)
        func = a.plot(lambda x: 0.5*np.sin(4*x), color=BLUE)
        
        func.add_updater()
        
        self.add(func)
        
        print(self.qubits[0].get_center(), self.qubits[0].get_x(RIGHT))
        print(self.qubits[1].get_center(), self.qubits[1].get_x(LEFT))
        
        # print((self.qubits[0].get_x(RIGHT) + self.qubits[1].get_x(LEFT))/2)
        
        self.play(func.animate.stretch_to_fit_width(4))
        self.play(func.animate.stretch_to_fit_height(2))
        
        # func.scale(0.5)
        
        # self.tracker = ValueTracker(0)
        
        
        self.wait()