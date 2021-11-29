![screenshot](assets/screenshot.png)

# PyArcWelderUI

A GUI for [ArcWelder](https://github.com/FormerLurker/ArcWelderLib) Console. This allows a user to see the results and statistics when using ArcWelder as a slicer PostProcessing script.

## Requirements

 - The 'ArcWelder Console' executable from https://github.com/FormerLurker/ArcWelderLib, at least version 1.2.
 - Python 3 (tested on 3.9, but should work with 3.7+)
   - numpy
   - matplotlib

## Setup

 1. Get the ArcWelder console binary, either pre-packaged or build it yourself: https://github.com/FormerLurker/ArcWelderLib. If using a pre-built package, unzip the package somewhere with a convenient path.
 2. Install Python 3 if you don't already have it. If needed, install numpy and matplotlib as well.
 3. Download an appropriate PyArcWelderUI archive from a release here, or from the artifacts in [latest commit action](https://github.com/The-EG/PyArcWelderUI/actions). Extract this into a convenient path simlar to step #1.
 4. Configure PyArcWelderUI; open pyawui.ini and:
    - Modify the value of `ArcWelderPath=` to specify the full absolute path to `ArcWelder` or `ArcWelder.exe`.
    - Enable and specify any ArcWelder options as appropriate
 5. Configure your slicer:
    - Slic3r/PrusaSlicer/SuperSlicer:  
      Specify the path to python3 and the pyawui.zip files in the `Post-Processing scripts` option in the Output Options in your Print Settings profile. *Note: you  will need to enable 'Expert' settings to see this option and you will need to do this for each Print Settings profile you want to use*. For example:  
      `python3 ~/programs/PyArcWelderUI/pyawui.zip` or `C:\Python39\python3.exe c:\Programs\PyArcWelderUI\pyawui.zip`
