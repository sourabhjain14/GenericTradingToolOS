"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


#import importlib  # Import the importlib module
#import TraderSystem  # Import your module
import globalvar
from zerodha import create_kite

# Reload the module whenever you make changes
#importlib.reload(TraderSystem)

def setup_kite():
    globalvar.g_kite=create_kite()

#def create_gui():
#    TraderSystem.GUIBox