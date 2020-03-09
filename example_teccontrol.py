import instruments

tec = instruments.TEC1089SV()
tec.connect(4)
print(tec.query('#0015AA?IF'))
