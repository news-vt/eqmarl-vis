from typing import Callable
from manim import *

# config.disable_caching = True
# config.quality = 'low_quality'

# Tool for creating voiceovers with Manim: https://www.manim.community/plugin/manim-voiceover/

# Example of making a neural network with Manim: https://medium.com/@andresberejnoi/using-manim-and-python-to-create-animations-like-3blue1brown-andres-berejnoi-34f755606761


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


class PausableScene(Scene):
    """Base scene that allows for easy pausing."""
    
    def small_pause(self, n=0.5):
        self.wait(n)
    
    def pause_pause(self, n=1.5):
        self.wait(n)

    def medium_pause(self, n=3):
        self.wait(n)
    
    def long_pause(self, n=5):
        self.wait(n)


class DemoForICAB(PausableScene):
    def construct(self):
        
        # Define the sections of the video.
        # Each section is a tuple of the form (name, method, kwargs).
        # The sections can be reordered here.
        # Objects can be reused between sections as long as they are not removed.
        # To reuse an object, simply save it to a variable using `self.<variable_name> = <object>`.
        # Each section should cleanup any objects after itself if they are not to be used again.
        # Sections can be tested individually, to do this set `skip_animations=True` to turn off all other sections not used (note that the section will still be generated, allowing objects to move to their final position for use with future sections in the pipeline).
        sections: list[tuple[Callable, dict]] = [
            (self.section_title, dict(name="Title", skip_animations=True)),
            (self.section_motivation, dict(name="Motivation", skip_animations=True)),
            (self.section_scenario, dict(name="Scenario", skip_animations=False)),
            (self.section_placeholder, dict(name="Placeholder", skip_animations=False)),
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
        
        subtitle_text = Text("Coordination without Communication", font_size=28)
        subtitle_text.next_to(eqmarl_full, DOWN, buff=0.5)
        
        attribution_text = Text("A. DeRieux & W. Saad (2025)", font_size=12)
        attribution_text.to_edge(DOWN, buff=0.1)
        
        # Combine the glyphs.
        eqmarl_glyphs = list(zip(eqmarl_acronym_glyphs, eqmarl_full_glyphs))
        
        # Animate the title.
        self.play(FadeIn(eqmarl_acronym))
        self.play(Write(eqmarl_full))
        self.play(Write(subtitle_text))
        self.play(Create(attribution_text))
        self.play(FadeOut(eqmarl_full), FadeOut(subtitle_text), eqmarl_acronym.animate.scale(0.5).to_edge(UL))


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
    
    def section_scenario(self):
        """Scenario section."""
        t0 = Text("Scenario", font_size=32)
        self.play(Write(t0))
        
        
        drones = VGroup(*[
            SVGMobject("assets/images/drone.svg"),
            SVGMobject("assets/images/drone.svg"),
        ])
        # Give all drones a grey outline to make them stand out.
        for d in drones:
            path_outline = d.family_members_with_points()[0]
            path_outline.set_stroke(GRAY, 1)
            d.scale(0.5)
        
        drones.next_to(t0, UP)
        
        drones[0].shift(LEFT*2)
        drones[1].shift(RIGHT*2)
        
        self.play(GrowFromCenter(drones))
        
        line = Line(start=drones[0].get_right(), end=drones[1].get_left())
        self.play(Write(line))
        
        
        firetree = SVGMobject("assets/images/firetree.svg").scale(0.5)
        firetree.next_to(drones[0], DOWN)
        self.add(firetree)
        
        firehouse = SVGMobject("assets/images/firehouse.svg").scale(0.5)
        firehouse.next_to(drones[1], DOWN)
        self.add(firehouse)
        
        
        self.play(Wiggle(drones[0]))
        self.play(Wiggle(drones[1]))
        self.play(Wiggle(firetree))
        self.play(Wiggle(firehouse))
        
        # drone = SVGMobject("assets/images/drone.svg")
        # drone.next_to(t0, DOWN*2)
        # path_outline = drone.family_members_with_points()[0]
        # path_outline.set_stroke(GRAY, 1)
        
        # self.play(FadeIn(drone))
        
        # self.play(drone.animate.shift(RIGHT*2))
        # self.play(drone.animate.rotate(45*DEGREES))


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
        
        # box = Square(side_length=2)
        # label = Text
        
        # label = Tex("$X$")
        # box = SurroundingRectangle(label, color=WHITE, buff=0.25)
        # lines = VGroup(
        #     Line(start=box.get_left(), end=LEFT),
        #     Line(start=box.get_right(), end=RIGHT),
        # )
        
        # gate = VGroup(label, box, lines)
        
        g0 = make_quantum_gate_1qubit("$X$")
        g1 = make_quantum_gate_1qubit(r"$R^{\theta}$").next_to(g0, buff=0)
        
        self.add(g0, g1)
        
        self.wait(1)