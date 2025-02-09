import itertools
import os
import tempfile
from typing import Callable

from manim import *
import segno

# config.disable_caching = True
# config.quality = 'low_quality'

# Tool for creating voiceovers with Manim: https://www.manim.community/plugin/manim-voiceover/

# Example of making a neural network with Manim: https://medium.com/@andresberejnoi/using-manim-and-python-to-create-animations-like-3blue1brown-andres-berejnoi-34f755606761

def batched(iterable, n: int):
    """Converts a list into a list of tuples of every `n` elements.
    
    For n=2, the function will produce:
    x -> [(x0, x1), (x2, x3), ...]
    """
    x = iter(iterable)
    return zip(*([x]*n))


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
            # (self.section_outro, dict(name="Outro", skip_animations=True)), # Play last.
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
        
        attribution_text_full = Text("Alexander DeRieux & Walid Saad (2025)", font_size=24)
        attribution_text_full.next_to(subtitle_text, DOWN, buff=0.5)
        
        self.attribution_text = Text("A. DeRieux & W. Saad (2025)", font_size=12)
        self.attribution_text.to_edge(DOWN, buff=0.1)
        
        # Combine the glyphs.
        eqmarl_glyphs = list(zip(eqmarl_acronym_glyphs, eqmarl_full_glyphs))
        
        # Animate the title.
        self.play(FadeIn(eqmarl_acronym))
        self.play(Write(eqmarl_full))
        self.play(Write(subtitle_text))
        
        # self.play(Create(self.attribution_text))
        self.play(Write(attribution_text_full))
        
        self.medium_pause()
        
        self.play(FadeOut(eqmarl_full), FadeOut(subtitle_text), eqmarl_acronym.animate.scale(0.5).to_edge(UL), ReplacementTransform(attribution_text_full, self.attribution_text))


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
        
        self.next_section("scenario-start", skip_animations=True) # TODO: delete.
        
        # Create and animate the title.
        section_title = Text("Example Scenario", font_size=self.eqmarl_acronym.font_size) # Match font size of the acronym in the top-left.
        self.play(Write(section_title)) # At origin.
        self.play(section_title.animate.to_edge(UP)) # Move to top edge.
        self.small_pause()
        
        ###
        # Scenario introduction.
        ###
        self.next_section("scenario-intro", skip_animations=False) # TODO: delete.
        
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
        group = Group(*[
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
        group.arrange_in_grid(rows=len(group)//2, cols=2, col_alignments='rl', buff=0.5)
        group.scale_to_fit_width(.9*config.frame_width)
        group.to_edge(LEFT)
        
        Group(VGroup(Text("")))
        
        for (icon, textgroup) in itertools.batched(group, n=2):
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
        
        
        return
        
        
        t0 = Text(
            text="The wildfires in California have spread at an unprecedented rate",
            t2c={'wildfires': RED}
        )
        t0.scale_to_fit_width(.9*config.frame_width)
        print(f"{t0.font_size=}")
        self.play(Write(t0))
        self.wait()
        
        t1 = Text("Rapidly and efficiently extinguishing these fires has arisen to be a major challenge")
        t1.scale_to_fit_width(.8*config.frame_width)
        t1.next_to(t0, DOWN)
        self.play(Write(t1))
        
        # Group text boxes and move them both up as a unit.
        g0 = VGroup(t0, t1)
        self.play(g0.animate.shift(UP*2))
        
        t2 = Text("Firefighters on the ground have a limited localized view of the spreading flames")
        t2.scale_to_fit_width(.9*config.frame_width)
        self.play(Write(t2))
        
        img_fire = ImageMobject("assets/images/fire.png")
        self.add(img_fire)
        
        img_fireman = ImageMobject("assets/images/fireman.png")
        self.add(img_fireman)
        
        img_drone = ImageMobject("assets/images/drone.png")
        self.add(img_drone)
        
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
    
    def section_outro(self):
        
        qr = segno.make("https://arxiv.org/abs/2405.17486", micro=False, error='H')
        img = SegnoQRCodeImageMobject(qr, scale=100, dark=GRAY_A.to_hex(), finder_dark=PURPLE.to_hex(), border=0, light=None).scale(0.1)
        
        t0 = Text("Paper is available on arXiv", font_size=24)
        
        
        self.play(self.eqmarl_acronym.animate.scale(2).move_to(ORIGIN).shift(UP*1.5))
        
        img.next_to(self.eqmarl_acronym, DOWN)
        self.play(FadeIn(img))
        
        t0.next_to(img, DOWN)
        self.play(Write(t0))
        
        t1 = Text("Alexander DeRieux & Walid Saad (2025)", font_size=24).next_to(t0, DOWN)
        self.play(ReplacementTransform(self.attribution_text, t1))
        
        self.play(Wiggle(img))
        
        self.wait(1)


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