"""
Contains variables that should be accessible from any scope
"""

class Globals:
    XRes = 1280
    YRes = 720
    NumCols = 120
    NumRows = 35
    Timestep = 0.033
    FontName = 'Courier New'
    FontSize = 14
    IsDev = True
    AssetsRootPath = 'assets'
    SavePaths = [
        'savefiles/sav0.txt',
        'savefiles/sav1.txt',
        'savefiles/sav2.txt',
        'savefiles/sav3.txt',
    ]
    MapsPaths = [
        ('test_map.txt', 'test_map_color_mask.txt', 'test_map_travel_mask.txt'),
        ('test_map.txt', 'test_map_color_mask.txt', 'test_map_travel_mask.txt'),
    ]
    AreasConfigPath = 'areas.yml'
    ItemsConfigPath = 'items.yml'
    KeybindingsConfigPath = 'keybindings.yml'
    CmdMaxLength = 48
