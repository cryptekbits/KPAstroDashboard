# kpTools package initialization
import os
import sys

# Add the package directory to sys.path to enable relative imports
__path__ = [os.path.dirname(os.path.abspath(__file__))]
sys.path.insert(0, __path__[0])

# Import key modules to make them available at package level
from .VedicAstro import VedicHoroscopeData
from .horary_chart import find_exact_ascendant_time, get_horary_ascendant_degree
from .utils import dms_to_decdeg, utc_offset_str_to_float