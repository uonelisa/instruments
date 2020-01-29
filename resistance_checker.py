import time
import instruments

resses = {"A": 50, "B": 50, "C": 50, "D": 50, "E": 50, "F": 50, "G": 50, "H": 50}
balance_box = instruments.BalanceBox()
balance_box.connect(5)

balance_box.disable_all()
time.sleep(5)
balance_box.enable_all()
time.sleep(5)
balance_box.set_resistances(resses)
time.sleep(5)
balance_box.reset_resistances()
time.sleep(5)