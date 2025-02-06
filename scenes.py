from manim import *
import manim.typing
import itertools


# Objects for reuse.
# obj_grid_empty = Square(color=GRAY, fill_opacity=0.5)
obj_grid_empty = Square(color=GRAY, fill_opacity=0)
obj_grid_lava = Square(color=ORANGE, fill_opacity=0.5)
obj_grid_goal = Square(color=GREEN, fill_opacity=0.5)
obj_player_base = obj_grid_empty.copy()
# obj_player_core = Triangle(color=RED, fill_opacity=0.5).rotate(270*DEGREES).move_to(obj_player_base.get_center())
obj_player_core = Triangle(color=RED, fill_opacity=0.5).rotate(270*DEGREES)
obj_player = VGroup(*[
    obj_player_base,
    obj_player_core,
])



def build_minigrid(
    grid_size: tuple[int, int] = (5,5),
    player_pos: tuple[int, int] | None = None, # Defaults to top-left.
    goal_pos: tuple[int, int] | None = None, # Defaults to bottom-right.
    hazards: list[tuple[int, int]] = [],
    grid_obj_default: Mobject = obj_grid_empty,
    grid_obj_hazard: Mobject = obj_grid_lava,
    grid_obj_goal: Mobject = obj_grid_goal,
    grid_obj_player: Mobject = obj_player,
    ) -> list[list[VMobject]]:
    """Helper function to generate a MiniGrid environment.
    
    Returns a 2D matrix of Manim `VMobject`.
    """
    if player_pos == None: # Defaults to top-left.
        player_pos = (0,0)
    if goal_pos == None: # Defaults to bottom-right.
        goal_pos = (grid_size[0]-1, grid_size[1]-1)

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
    return rows



class MiniGrid(VMobject):
    
    def __init__(self, grid_size: tuple[int,int], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_size = grid_size
        
        # Defaults to `RIGHT`, and upper-left (0,0).
        self.player_look_angle = 270 # degrees, RIGHT
        self.player_grid_pos = (0,0)

        objs_in_grid = build_minigrid(
            grid_size=grid_size,
            player_pos=self.player_grid_pos,
            goal_pos=(4,4),
            hazards=[
                (1,1),
                (1,2),
                (1,3),
            ],
        )
        grid = VGroup(*[o for o in itertools.chain(*objs_in_grid)])
        grid.arrange_in_grid(rows=grid_size[0], cols=grid_size[1], buff=0)
        
        player = obj_player_core.copy()
        player_pos = (0,0)
        player_target_pos = grid[player_pos[0]*grid_size[0] + player_pos[1]].get_center()
        player.move_to(player_target_pos)
        grid = VGroup(player, grid)
        self.grid = grid
        
        # IMPORTANT - we must add all sub-objects that we want displayed.
        self.add(self.grid)

    def move_player(self, direction: manim.typing.Vector3D):
        
        # assert direction in (UP, LEFT, DOWN, RIGHT), "Can only move player UP/LEFT/DOWN/RIGHT."
        
        r,c = self.player_grid_pos
        
        # Calculate turning angle relative to current angle.
        if (direction == UP).all():
            turn_angle = 360
            r -= 1
        elif (direction == LEFT).all():
            turn_angle = 90
            c -= 1
        elif (direction == DOWN).all():
            turn_angle = 180
            r += 1
        elif (direction == RIGHT).all():
            turn_angle = 270
            c += 1
        new_angle = (turn_angle - self.player_look_angle)
        
        # Update current player look angle.
        self.player_look_angle = turn_angle
        
        # Perform animation for rotation and shift.
        if r < self.grid_size[0] and c < self.grid_size[1]:
            self.player_grid_pos = (r,c)
            return self.grid[0].animate.rotate(new_angle*DEGREES).shift(direction)
        # Boundary of grid reached, only perform rotation.
        else:
            return self.grid[0].animate.rotate(new_angle*DEGREES)






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
        grid = MiniGrid(grid_size=grid_size)
        grid = grid.scale(0.5)
        ###########
        
        # self.play(Write(grid))
        # self.play(grid.animate.shift(LEFT*2))
        
        # grid = grid.shift(LEFT*2)
        
        
        t2 = Tex(r"This is an example of a $5 \times 5$ grid for 1 player:").move_to(t1.get_center())
        # t2.next_to(grid, UP, aligned_edge=LEFT)
        # self.play(ReplacementTransform(t1, t2))
        
        self.play(
            ReplacementTransform(t1, t2),
            Write(grid),
        )
        
        self.play(
            # ReplacementTransform(t1, t2),
            grid.animate.shift(LEFT*2),
        )
        
        
        # Introduce the grid.
        vgroup = VGroup(*[
            VGroup(*[
                obj_grid_empty.copy().scale(0.25),
                Tex("Empty grid square"),
            ]).arrange(),
            VGroup(*[
                obj_grid_lava.copy().scale(0.25),
                Tex("Lava hazard"),
            ]).arrange(),
            VGroup(*[
                obj_grid_goal.copy().scale(0.25),
                Tex("Goal"),
            ]).arrange(),
            VGroup(*[
                obj_player_core.copy().scale(0.25),
                Tex("Player"),
            ]).arrange(),
        ])
        vgroup.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        
        vgroup.next_to(grid, RIGHT)
        self.play(Write(vgroup))
        
        
        
        # Animate the player moving around a little.
        
        # self.play(
        #     grid[0].animate.rotate(-90*DEGREES),
        #     # grid[0].animate.rotate(-90*DEGREES).shift(DOWN),
        #     # grid[0].animate.shift(DOWN),
        # )
        # actions = [
        #     DOWN, RIGHT, DOWN, DOWN, UP, UP, LEFT, RIGHT
        # ]
        # actions = [
        #     RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, RIGHT, LEFT 
        # ]
        actions = [
            DOWN, DOWN, RIGHT, DOWN
        ]
        for a in actions:
            self.play(grid.move_player(a))
            # print(grid[0].get_angle())
            # # if a == RIGHT:
            # #     self.play(
            # #         grid[0].animate.rotate(90*)
            # #     )
            # self.play(grid[0].animate.shift(a))
        # self.play(
        #     grid[0].animate.shift(DOWN),
        #     grid[0].animate.shift(DOWN),
        #     # grid[0].animate.shift(DOWN),
        # )
        # self.play(
        #     grid[0].animate.shift(DOWN).shift(DOWN).shift(DOWN),
        # )
        
        # objs_in_grid = build_minigrid(
        #     grid_size=grid_size,
        #     player_pos=(1,0),
        #     goal_pos=(4,4),
        #     hazards=[
        #         (1,1),
        #         (1,2),
        #         (1,3),
        #     ],
        #     grid_obj_player=obj_player.rotate(90*DEGREES),
        # )
        # g2 = VGroup(*[o.scale(0.5) for o in itertools.chain(*objs_in_grid)])
        # g2.arrange_in_grid(rows=grid_size[0], cols=grid_size[1], buff=0)
        # g2.move_to(grid.get_center())
        
        # objs_in_grid = build_minigrid(
        #     grid_size=grid_size,
        #     player_pos=(2,0),
        #     goal_pos=(4,4),
        #     hazards=[
        #         (1,1),
        #         (1,2),
        #         (1,3),
        #     ],
        #     grid_obj_player=obj_player.rotate(90*DEGREES),
        # )
        # g3 = VGroup(*[o.scale(0.5) for o in itertools.chain(*objs_in_grid)])
        # g3.arrange_in_grid(rows=grid_size[0], cols=grid_size[1], buff=0)
        # g3.move_to(g2.get_center())
        # 
        # self.play(
        #     Transform(grid, g2),
        # )
        # self.play(
        #     Transform(g2, g3),
        # )
        
        
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



class EntanglementScene(Scene):
    def construct(self):
        circle = Circle()
        ellipse = Ellipse(width=circle.width, height=0.4).move_to(circle.get_center())
        ellipse = DashedVMobject(ellipse, num_dashes=12, equal_lengths=False)
        dots = VDict({
            'origin': Dot(ORIGIN),
            'top': Dot(circle.get_top()),
            'bottom': Dot(circle.get_bottom()),
        })
        # dots = VGroup(*[
        #     Dot(ORIGIN),
        #     Dot(circle.get_top()),
        #     Dot(circle.get_bottom()),
        # ])
        arrow = Arrow(start=circle.get_center(), end=circle.point_at_angle(45*DEGREES), buff=0)
        shapes = VGroup(*[
            circle,
            arrow,
            ellipse,
            dots,
        ])
        shapes.set_color(BLUE_D)
        dots.set_color(WHITE)
        dots['origin'].set_color(GRAY)
        arrow.set_color(GRAY)
        
        
        text = VGroup(*[
            MathTex(r"|0\rangle").next_to(dots['top'], UP),
            MathTex(r"|1\rangle").next_to(dots['bottom'], DOWN),
        ])
        
        
        master_group = VGroup(shapes, text)
        
        q0 = master_group.copy()
        q1 = master_group.copy()
        
        self.play(GrowFromCenter(q0), GrowFromCenter(q1))
        self.play(q0.animate.move_to(LEFT*3), q1.animate.move_to(RIGHT*3))
        
        # self.play()
        
        self.wait()