
# Getting started
Here is a general overview of how to get started with using our Blender add-on to begin analyzing aspects of salamander locomotion. More details and functions will be added in the future, so stay tuned!

## Section A: Download Blender
1. Download the latest version of Blender at [https://www.blender.org/download/](https://www.blender.org/download/)
2. Double-click the file that was downloaded.
3. Follow the on-screen instructions to install Blender to your computer. 
4. Our Blender add-on does NOT require prior knowledge of Blender but users who are interested in navigating the Blender software can refer to this [Introduction](https://docs.blender.org/manual/en/latest/getting_started/about/introduction.html) or [video tutorials](https://www.youtube.com/results?search_query=%23b3d+tutorial&sp=EgIIBQ%253D%253D) on YouTube. 


## Section B: Downloading our blender-tetrapod-toolkit
1. Navigate to our [GitHub repo](https://github.com/JohnsonLM/blender-tetrapod-toolkit/tree/main).
2. Download our folder of files by clicking on the <kbd>green button labeled <>Code</kbd> and then
	a. selecting *"Download ZIP"*, or
	b. cloning the repo using the *web URL* or selecting *"Open with GitHub Desktop."*
3. Save the folder to a convenient location on your computer (e.g., your Desktop). 


## Section C: Loading the Tetrapod Toolkit as an add-on in Blender
In order to use our toolkit, you will need to load our [Blender add-on](https://docs.blender.org/manual/en/latest/editors/preferences/addons.html).
However, you will only need to do this once after installing Blender. If you install a new version of Blender, you may need to load the add-on again. 
1. Double-click on the file labeled *"Andrias_Salamander_procedural_bending_04.blend."*
2. On the top header, click on <kbd>"Edit"</kbd> and then select <kbd>"Preferences."</kbd>
3. A "Blender Preferences" window will pop up; click on the left-hand button that says <kbd>"Add-ons."</kbd>
4. On the righthand side of the window, click on <kbd>"Install."</kbd>
5. A new window will pop up to select the add-on file. Navigate to where you downloaded the Blender-tetrapod-toolkit repo and then select *tetrapod-toolkit-addon.py*.
6. After you click <kbd>Install</kbd>, you will be taken back to the "Blender Preferences" window. Make sure that the box next to "View 3D: Tetrapod Toolkit" is checked. If it is not, click on the box to add a check mark. 
7. Click on the "X" on the top-right corner of the "Blender Preferences" window to return to the main workspace for Blender. 
8. You will now see a new tab labeled "Tetrapod Toolkit" to the right side of the grid. If not, you may need to click the "<" symbol next to "Options" to expand the tabs.  

## Section D: Overview of the Tetrapod Toolkit
[!IMPORTANT]
Blender does not perform well when working with small values, so we changed the Unit Scale to 0.1 meters rather than 1 meters to make the output in units of centimeters. You can double-check information about the {units and scaling](https://docs.blender.org/manual/en/latest/scene_layout/scene/properties.html) under the <kbr>Scene Properties</kbr> button that looks like a teardrop next to a circle. 
/

You will see three models of *Andrias japonicus* that exhibit different degrees of lateral bending, where the leftmost has no lateral bending, the middle has slight lateral bending, and the rightmost has extreme lateral bending.
The ground is represented by a grid composed of 10 cm x 10 cm squares. The frame rate is 30 fps (frames per second), which you can double-check under [Output Properties](https://www.skillademia.com/3d/blender/how-to-use-animation-timeline-in-blender/). /


1. By default, Blender will likely open in "Object Mode." If you click on the "Tetrapod Toolkit" tab, the pop-up window will largely be empty. 
2. To use the Tetrapod Toolkit, you will need to click "Object Mode" and then select "Pose Mode." 
3. You should now see one of the salamander models highlighted in red and the Tetrapod Toolkit window become populated with numbers. 
4. Select the bones that you want to measure by clicking the <kbr>Left Mouse Button</kbr> for one bone or <kbr>Shift + Left Mouse Button</kbr> to select multiple bones. 
5. The Tetrapod Toolkit collects the following data:
	a. **Timecode** in HH:MM:SS:FF, which is Hours:Minutes:Seconds:Frames
	b. **Rot** (Rotation in degrees) values represent the rotations of the bone along each of the XYZ axes in the global environment. 
	c. **Head Loc** (Head Location in centimeters)
	d. **Tail Loc** (Tail Location in centimeters)
	e. **Loc Change** (Location Change in centimeters); a negative value just says that the animal was moving towards the bottom of the screen. 
	f. **Rot Change** (Rotational Change in degrees)
	g. **Min Angle** (Minimum Angle in degrees)
	h. **Max Angle** (Maximum Angle in degrees)
6. Select the range of frames that you want to analyze by changing the values for <kbd>Frame Range Start:</kbd> and <kbd>Frame Range End:</kbd>. 
7. Click on <kbr>Calculate Active Bone Travel</kbr> to calculate the data from Frame Start to Frame End.
8. The new values displayed in the Tetrapod Toolkit window are the data collected from your designated Frame Range. 
9. You can then export the rotational data from the Tetrapod Toolkit by using:
	a. <kbd>Export Selected Bone Rotations</kbd> for the entire length of the simulation
	b. <kbd>Export Selected Bone Rotations in Range</kbd> to save the data within the frame range specified
	c. Note: at the moment, only the rotational data are exported into the spreadsheet with these operations. Location data can be manually collected from the Tetrapod Toolkit window. 

[!NOTE] "Create Muscle" button is currently in development; it will enable you to create 3D muscles between bones to simulate the effects of soft tissue on bone mobility. 


