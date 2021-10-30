import os.path


class BiTheme:
    """Utilisies for GUI theme"""
    def __init__(self, theme_dir=''):
        if theme_dir == "":
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.theme_dir = os.path.join(current_dir, '..', '..', 'theme', 'dark')
        else:
            self.theme_dir =  theme_dir   

    def icon(self, name):
        return os.path.join(self.theme_dir, f'{name}.svg')     


class BiThemeAccess:
    """Singleton to access the theme

    Parameters
    ----------
    config_file
        JSON file where the config is stored

    Raises
    ------
    Exception: if multiple instantiation of the Config is tried

    """

    __instance = None

    def __init__(self, theme=''):
        """ Virtually private constructor. """
        BiThemeAccess.__instance = BiTheme(theme)

    @staticmethod
    def instance():
        """ Static access method to the Config. """
        if BiThemeAccess.__instance is None:
            BiThemeAccess.__instance = BiTheme()
        return BiThemeAccess.__instance        