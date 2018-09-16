# Origami Regularity Index

This python script works in Blender (www.blender.org), analyses origami crease patterns. The crease pattern must be defined as a mesh. Crease patterns exported in .OBJ format from in Jun Mitani's software ORIPA http://mitani.cs.tsukuba.ac.jp/oripa/ work. A mesh should not contain duplicate vertices.

For complete details about the rationale of the index, see the pdf file Origami-Regularity-Index.pdf

## How to Use

Download the Origami-Regularity-Index.blend file and open in blender, then:

1. Import your mesh into the blend file.
2. Select the mesh, and run the script by pressing the RUN SCRIPT button in the script window. 
3. The script will write its output to the same directory as the .blend file. 
4. The script produces 4 files:
	 a. summary file, contains markdown style tables of the key data.
	 b. graph file, contains data to import into adobe illustrator graphs.
	 c. line file, a one line summary of the index results.
	 d. debug file, contains all of the data points.


## Command Line Python Script

Prerequisites: Blender > 2.78 from www.blender.org
On linux systems such as debian: sudo apt-get install blender

1. Download Origami-Regularity-Index.py
2. Copy a crease pattern to the same directory
3. Run: path/to/blender -b -P Origami-Regularity-Index.py -- creasepattern.obj
4. Collect the data from the output directory 

