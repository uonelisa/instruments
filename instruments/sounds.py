import winsound

__all__ = ['error_sound', 'alert_sound']


def error_sound():
    """
    Simply plays the windows error sound

    :returns: None
    """
    winsound.PlaySound('.\Windows Background.wav', winsound.SND_FILENAME)


def alert_sound():
    """
    Simply plays a windows alert sound

    :returns: None
    """
    winsound.PlaySound('.\Windows Notify System Generic.wav', winsound.SND_FILENAME)
