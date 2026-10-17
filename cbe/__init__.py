"""
CBE Mobile Banking Unofficial Python Client & Interactive TUI
Reverse-engineered from Commercial Bank of Ethiopia (com.combanketh.mobilebanking)
"""

from .config import CBEConfig
from .client import CBEClient
from .tui import CBEMobileTUI

__version__ = "0.1.0"
__author__ = "NeuralS"
__license__ = "MIT"

__all__ = ["CBEClient", "CBEConfig", "CBEMobileTUI", "__version__"]
