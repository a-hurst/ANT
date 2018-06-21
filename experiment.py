__author__ = "Austin Hurst"

import klibs
from klibs.KLConstants import TK_MS, TIMEOUT
from klibs import P
from klibs.KLUtilities import deg_to_px, flush
from klibs.KLUserInterface import any_key, ui_request
from klibs.KLGraphics import KLDraw as kld
from klibs.KLGraphics import fill, flip, blit, clear
from klibs.KLCommunication import message
from klibs.KLEventInterface import TrialEventTicket as ET
from klibs.KLResponseCollectors import KeyPressResponse
from klibs.KLTime import CountDown

import random

# Define colours for the experiment

WHITE = [255, 255, 255, 255]
BLACK = [0, 0, 0, 255]


class ANT(klibs.Experiment):

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
        self.arrow_l = kld.Arrow(arrow_tail_len, arrow_tail_width, arrow_head_len, arrow_head_width, fill=BLACK, rotation=180)
        self.arrow_r = kld.Arrow(arrow_tail_len, arrow_tail_width, arrow_head_len, arrow_head_width, fill=BLACK)
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
            
        # Initialize feedback messages for practice block
        
        
        timeout_msg = message('Too slow! Please try to respond more quickly.', blit_txt=False)
        incorrect_str = ("Incorrect response!\n"
            "Please respond to left arrows with the 'z' key and right arrows with the '/' key.")
        incorrect_msg = message(incorrect_str, align='center', blit_txt=False)
        
        self.feedback_msgs = {'incorrect': incorrect_msg, 'timeout': timeout_msg}
            
        # Set up Response Collector to get keypress responses
        
        self.rc.uses(KeyPressResponse)
        self.rc.terminate_after = [1700, TK_MS] # response period times out after 1700ms
        self.rc.keypress_listener.interrupts = True
        self.rc.keypress_listener.key_map = {'z': 'left', '/': 'right'}
        
        # Add practice block of 24 trials to start of experiment
        
        if P.run_practice_blocks:
            self.insert_practice_block(1, trial_counts=24)
        

    def block(self):
        
        # Show block message at start of every block
        header = "Block {0} of {1}".format(P.block_number, P.blocks_per_experiment)
        if P.practicing:
            header = "This is a practice block. ({0})".format(header)
            practice_msg = "During this block you will be given feedback for your responses."
            msg = message(header+"\n"+practice_msg, align="center", blit_txt=False)
        else:
            msg = message(header, blit_txt=False)

        message_interval = CountDown(1)
        while message_interval.counting():
            ui_request() # Allow quitting during loop
            fill()
            blit(msg, 8, (P.screen_c[0], P.screen_y*0.4))
            flip()
        flush()
        
        start_msg = message("Press any key to start.", blit_txt=False)
        fill()
        blit(msg, 8, (P.screen_c[0], P.screen_y*0.4))
        blit(start_msg, 5, [P.screen_c[0], P.screen_y*0.6])
        flip()
        any_key()


    def trial_prep(self):
        
        # Determine location of target and flankers
        if self.target_location == 'above':
            self.target_loc = self.above_loc
            self.flanker_locs = self.above_flanker_locs
        else:
            self.target_loc = self.below_loc
            self.flanker_locs = self.below_flanker_locs
        
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
        
        self.cue_onset = random.randrange(400, 1650, 50) # random interval from 400 to 1600
        events = []
        events.append([self.cue_onset, 'cue_on'])
        events.append([events[-1][0] + 100, 'cue_off'])
        events.append([events[-1][0] + 400, 'target_on'])
        events.append([4000, 'trial_end'])
        for e in events:
            self.evm.register_ticket(ET(e[1], e[0]))


    def trial(self):
        
        # Before target onset, show fixation and draw cues during cue period
        while self.evm.before('target_on', pump_events=True):
            self.display_refresh()
            if self.evm.between('cue_on', 'cue_off'):
                self.draw_cues()
            flip()
        
        # Draw target stimuli/flankers and enter response collection loop
        fill()
        blit(self.fixation, 5, P.screen_c)
        blit(self.target, 5, self.target_loc)
        for loc in self.flanker_locs:
            blit(self.flanker, 5, loc)
        flip()
        self.rc.collect()
        
        # Get response data and preprocess it before logging to database
        response, rt = self.rc.keypress_listener.response()
        if rt == TIMEOUT:
            response = 'NA'
        
        # If practice trial, show participant feedback for bad responses
        if P.practicing and response != self.target_direction:
            fill()
            if response == 'NA':
                blit(self.feedback_msgs['timeout'], 5, P.screen_c)
            else:
                blit(self.feedback_msgs['incorrect'], 5, P.screen_c)
            flip()
            any_key()
        
        # Otherwise, clear screen immediately after response and wait for trial end
        else:
            self.display_refresh()
            flip()
        
            while self.evm.before('trial_end', pump_events=True):
                self.display_refresh()
                flip()
        
        # Log recorded trial data to database
        return {
            "block_num": P.block_number,
            "trial_num": P.trial_number,
            "cue_type": self.cue_type,
            "cue_onset": self.cue_onset if self.cue_type != 'none' else 'NA',
            "target_direction": self.target_direction,
            "target_loc": self.target_location,
            "flanker_type": self.flanker_type,
            "response": response,
            "rt": rt
        }

        
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
            loc = self.above_loc if self.target_location == 'above' else self.below_loc
            blit(self.cue, 5, loc)
        elif self.cue_type == 'none':
            pass
            
