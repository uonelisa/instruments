import winsound


__all__ = ['error_sound', 'alert_sound']

def error_sound():
    winsound.PlaySound('.\Windows Background.wav', winsound.SND_FILENAME)


def alert_sound():
    winsound.PlaySound('.\Windows Notify System Generic.wav', winsound.SND_FILENAME)