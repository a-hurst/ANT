__author__ = "Austin Hurst"
from klibs.KLIndependentVariable import IndependentVariableSet

ANT_ind_vars = IndependentVariableSet()

ANT_ind_vars.add_variable("cue_type", str)
ANT_ind_vars["cue_type"].add_values("none", "central", "double", "spatial")

ANT_ind_vars.add_variable("cue_location", str)
ANT_ind_vars["cue_location"].add_values("above", "below")

ANT_ind_vars.add_variable("target_direction", str)
ANT_ind_vars["target_direction"].add_values("left", "right")

ANT_ind_vars.add_variable("flanker_type", str)
ANT_ind_vars["flanker_type"].add_values("congruent", "neutral", "incongruent")
