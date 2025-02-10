import itertools
import glob
import json
import os
import pandas as pd
from pathlib import Path
import tempfile
from typing import Any, Callable

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
            # (self.section_title, dict(name="Title", skip_animations=True)),
            # (self.section_motivation, dict(name="Motivation", skip_animations=True)),
            # (self.section_scenario, dict(name="Scenario", skip_animations=True)),
            (self.section_results, dict(name="Results", skip_animations=False)),
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
        
        
        # self.play(FadeIn(*[group_graphs['series'][series_kwargs['key']]['std'] for series_kwargs in series]))
        
        self.long_pause()

    
    def section_outro(self):
        """Outro section.
        
        This is the last section played in the video.
        """
        
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