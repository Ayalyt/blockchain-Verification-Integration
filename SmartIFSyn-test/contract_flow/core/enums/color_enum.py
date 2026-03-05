# enum for color ANSI

from enum import Enum


class ColorEnum(Enum):
    red_color = '\033[91m'
    green_color = '\033[92m'
    yellow_color = '\033[93m'
    blue_color = '\033[94m'
    reset_color = '\033[0m'
    magenta_color = '\033[35m'
    cyan_color = '\033[36m'
