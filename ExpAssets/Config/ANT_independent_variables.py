from klibs.KLIndependentVariable import IndependentVariableSet


# Initialize object containing project's independent variables

ANT_ind_vars = IndependentVariableSet()


# Define project variables and variable types


## Factors ##
# 'cue_type': the type of cue ("spatial" == same location as 'target_location')
# 'target_location': the location of the target and flanker arrows
# 'target_direction': the direction of the target arrow
# 'flanker_type': the type of flanker arrow (same direction, opposite direction, or plain line)

ANT_ind_vars.add_variable("cue_type", str, ["central", "double", "spatial"])
ANT_ind_vars.add_variable("target_location", str, ["above", "below"])
ANT_ind_vars.add_variable("target_direction", str, ["left", "right"])
ANT_ind_vars.add_variable("flanker_type", str, ["congruent", "neutral", "incongruent"])