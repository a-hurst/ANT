__author__ = "Austin Hurst"

import klibs
from klibs.KLConstants import TK_MS, RC_KEYPRESS
from klibs import P
from klibs.KLKeyMap import KeyMap
from klibs.KLUtilities import deg_to_px
from klibs.KLUserInterface import any_key
from klibs.KLGraphics import KLDraw as kld
from klibs.KLGraphics import fill, flip, blit, clear
from klibs.KLEventInterface import TrialEventTicket as ET

import sdl2

# Define colours for the experiment

WHITE = [255, 255, 255, 255]
BLACK = [0, 0, 0, 255]


class ANT(klibs.Experiment):

    def __init__(self, *args, **kwargs):
        super(ANT, self).__init__(*args, **kwargs)

    def setup(self):
        
        # Stimulus sizes
        
        fixation_size = deg_to_px(0.5)
        fixation_thickness = deg_to_px(0.05)
        cue_size = deg_to_px(0.5)
        cue_thickness = deg_to_px(0.05)
        arrow_tail_len = deg_to_px(0.35)
        arrow_tail_width = deg_to_px(0.1)
        arrow_head_len = deg_to_px(0.2)
        arrow_head_width = deg_to_px(0.3, even=True)
        
        # Stimuli
        
        self.fixation = kld.FixationCross(fixation_size, fixation_thickness, fill=BLACK)
        self.cue = kld.Asterisk(cue_size, thickness=cue_thickness, fill=BLACK, spokes=8)
        self.arrow_l = kld.Arrow(arrow_tail_len, arrow_tail_width, arrow_head_len, arrow_head_width, fill=BLACK)
        self.arrow_r = kld.Arrow(arrow_tail_len, arrow_tail_width, arrow_head_len, arrow_head_width, fill=BLACK, rotation=180)
        self.line = kld.Rectangle(arrow_tail_len+arrow_head_len, arrow_tail_width, stroke=[0, BLACK, 1], fill=BLACK)
        self.arrow_l.render()
        self.arrow_r.render()
        
        # Layout
        
        height_offset = deg_to_px(1.06)
        flanker_offset = arrow_tail_len + arrow_head_len + deg_to_px(0.06)
        self.above_loc = (P.screen_c[0], P.screen_c[1]-height_offset)
        self.below_loc = (P.screen_c[0], P.screen_c[1]+height_offset)
        self.above_flanker_locs = []
        self.below_flanker_locs = []
        for offset in [-2, -1, 1, 2]:
            x_pos = P.screen_c[0] + (offset * flanker_offset)
            self.above_flanker_locs.append((x_pos, self.above_loc[1]))
            self.below_flanker_locs.append((x_pos, self.below_loc[1]))
            
        # Initialize ResponseCollector keymaps
        
        self.response_keymap = KeyMap(
            "Responses", # Name
            ['z', '/'], # UI labels
            ['left', 'right'], # Data labels
            [sdl2.SDLK_z, sdl2.SDLK_SLASH] # SDL2 Keysyms
        )
        

    def block(self):
        pass

    def setup_response_collector(self):
        
        # Set up Response Collector to get keypress responses
        
        self.rc.uses(RC_KEYPRESS)
        self.rc.terminate_after = [1700, TK_MS] # response period times out after 1700ms
        self.rc.keypress_listener.interrupts = True
        self.rc.keypress_listener.key_map = self.response_keymap

    def trial_prep(self):
        
        # Determine cue location for spatial cue trials
        
        self.cue_loc = self.above_loc if self.cue_location == 'above' else self.below_loc
        
        # Set central arrow and flanker arrow types
        if self.target_direction == "left":
            self.target = self.arrow_l
            if self.flanker_type == "congruent":
                self.flanker = self.arrow_l
            elif self.flanker_type == "incongruent":
                self.flanker = self.arrow_r
            else:
                self.flanker = self.line
        else:
            self.target = self.arrow_r
            if self.flanker_type == "congruent":
                self.flanker = self.arrow_r
            elif self.flanker_type == "incongruent":
                self.flanker = self.arrow_l
            else:
                self.flanker = self.line
        
        # Add timecourse of events to EventManager

        events = []
        events.append([1000, 'cue_on']) # should be random 400-1600
        events.append([events[-1][0] + 100, 'cue_off'])
        events.append([events[-1][0] + 400, 'target_on'])
        events.append([4000, 'trial_end'])
        for e in events:
            self.evm.register_ticket(ET(e[1], e[0]))

    def trial(self):
        
        while self.evm.before('target_on', pump_events=True):
            self.display_refresh()
            if self.evm.between('cue_on', 'cue_off'):
                self.draw_cues()
            flip()
        
        fill()
        blit(self.fixation, 5, P.screen_c)
        blit(self.target, 5, self.above_loc)
        for loc in self.above_flanker_locs:
            blit(self.flanker, 5, loc)
        flip()
        self.rc.collect()
        
        self.display_refresh()
        flip()
        
        while self.evm.before('trial_end', pump_events=True):
            self.display_refresh()
            flip()

        return {
            "block_num": P.block_number,
            "trial_num": P.trial_number
        }

    def trial_clean_up(self):
        pass

    def clean_up(self):
        pass
        
    def display_refresh(self):
        # Clear the display and draw fixation
        fill()
        blit(self.fixation, 5, P.screen_c)
        
    def draw_cues(self):
        if self.cue_type == 'central':
            blit(self.cue, 5, P.screen_c)
        elif self.cue_type == 'double':
            blit(self.cue, 5, self.above_loc)
            blit(self.cue, 5, self.below_loc)
        elif self.cue_type == 'spatial':
            blit(self.cue, 5, self.cue_loc)
        elif self.cue_type == 'none':
            pass
            
