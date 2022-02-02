# ======================================================================================================================
#        File:  b.py
#     Project:  B Bug Tracker
# Description:  Distributed Bug Tracker Extention for Mercurial
#      Author:  Jared Julien <jaredjulien@exsystems.net>
#   Copyright:  (c) 2010-2011 Michael Diamond <michael@digitalgemstones.com>
#               (c) 2022 Jared Julien, Nexteer Automotive
# ---------------------------------------------------------------------------------------------------------------------
"""Entry point for b bug tracker.

This script serves as the entry point for both the b Mercurial extension AND for the standalone command line version
that doesn't integrate with Mercurial.
"""
# ======================================================================================================================
# Import Statements
# ----------------------------------------------------------------------------------------------------------------------
import sys
import os




# ======================================================================================================================
# Version Number
# ----------------------------------------------------------------------------------------------------------------------
__version__ = "1.1.0"




# ======================================================================================================================
# Main Function
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Run from the command line - use argparser.
    print('Command line')

elif __name__ == "hgext_b":
    # Run via Mercurial - use extension interface.
    # This is a little wonkey because of the way the Mercurial interfaces with extensions.

    # First we need to add this package manually to the system path so as to allow importing other python scripts (which
    # would be out of scope for the context from which Mercurial is invoking us).
    sys.path.append(os.path.dirname(__file__))

    # Next, we need to import everything from the extension.py module into this scope which will get "returned" to
    # Mercurial.  Anything that's a global in extension.py can be considered a part of the interface.
    from extension import *


# End of File
