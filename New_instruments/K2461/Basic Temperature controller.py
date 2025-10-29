"""
temperature control
"""

import instruments
tec = instruments.TEC1089SV()
tec.connect(7)

temp = -16

tec.enable_control()
tec.set_ramp_rate(0.02)
tec.set_target_temperature(temp)
#tec.disable_control()

