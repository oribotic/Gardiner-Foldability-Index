# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
    
import bpy
import bmesh
import math
import os
from mathutils import Vector
from collections import Counter
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

print(argv[0])  # --> ['example', 'args', '123']

file_loc = argv[0]
imported_object = bpy.ops.import_scene.obj(filepath=file_loc)
obj = bpy.context.selected_objects[0] ####<--Fix

print('Imported name: ', obj.name)

#obj = bpy.context.object
me = obj.data

edgeLengthDict = {}
edgeLengths = []

edgeAngleDict = {}
edgeAngles = []

cornerAngleDict = {}
cornerAngles = []


# vertmap is a dict of vertice indexes that store related edge lengths and edge angles
vertexMap = {}

for v in me.vertices:
    vertexMap[v.index] = {"edges": [], "radians": [], "degrees": []}
    
# adjust this for decimal place accuracy, amount of decimal places to round
# given possible innacuracies in drafting of patterns, I kept this value low at 1.
accuracy = 1    
totalEdgeLength = 0
allcriteria = {}
regularity = {}

#make file pointers to save results
path = os.getcwd()+"/output/"

try:
    os.mkdir(path)
except FileExistsError:
    print("output dir exists.")

file    = open(path + me.name + ".txt", 'w')
summary = open(path + me.name + "_summary.txt", 'w')
ln      = open(path + me.name + "_line.txt", 'w')
graph   = open(path + me.name + "_graph.txt", 'w')

# ---------------------------------------------
# function definitions
# ---------------------------------------------
# write to the debug file
def debug(str):
    global file
    file.write(str + "\n")
    #print(str)

# write to the summary file
def sm(str):
    global summary
    file.write(str + "\n")
    summary.write(str + "\n")
    #print(str)

# write to the graph file - in a format understood by adobe illustrator
def grph (str):
    global graph
    graph.write(str + "\n")
    print(str)

# write to single line file
def liner (str):
    global ln
    ln.write(str + "\n")

# get a value from an array and return it with a defined decimal point accuracy
def getVal (arr, index, val, accuracy):
    n = arr[index][val]
    if n > 10000:
        return str(n)[0:-3]+"K"
    elif n > 1000:
        n = n/1000
        return str(round(n, 1))+"K"
    else:
        return str(round(arr[index][val], accuracy))

# create an abbreviation from a string
def getAbr (s):
    ret = ""
    spl = s.split(" ")
    for n in spl:
        ret += str(n[0:1])
    return ret

# which object is this
debug(me.name)

# ------------------------------------------------------------------------------
## MEASURE PARALLELITY
# ------------------------------------------------------------------------------

debug ("\n")  
debug ("--------------------------------")
debug ("PARALLELITY\t\t\t\t1 point")
debug ("--------------------------------")
debug ("e\tt")

# iterate over every edge in the mesh, store its global angle, if the value already exists
# add the incremental counter for that angle, therefore it has one value for parallelity
# record all edge lengths in edgeLengthDict
# record all edge angles in edgeAngleDict
# ------------------------------------------------------------------------------

for e in me.edges:
    # edge lengths
    vert = []
    eL = round((me.vertices[e.vertices[0]].co - me.vertices[e.vertices[1]].co).length, accuracy)
    totalEdgeLength += eL
    if eL in edgeLengthDict:
        edgeLengthDict[eL] +=1
    else:
        edgeLengthDict[eL] = 1
        edgeLengths.append(eL)
 
    # angle parallelity
    xV = Vector((1,0,0)) 
    eV = me.vertices[e.vertices[0]].co - me.vertices[e.vertices[1]].co
    a = eV.angle(xV)
    eA = round(math.degrees(a), accuracy)
  
    if eA in edgeAngleDict:
        edgeAngleDict[eA] +=1
    else:
        edgeAngleDict[eA] = 1
        edgeAngles.append(eA)     

    debug("{}\t{}".format(eA, eL))
    
debug ("--------------------------------")
debug ("a\t#")
debug ("--------------------------------")

# sum all of the edgeAngles with a count > 1
# more than one edge indicates the edgeAngle has multiple parallel edges

totalEdges = len(me.edges)
sumParallelEdges = 0
for i in edgeAngles:
    if edgeAngleDict[i] > 1:
        sumParallelEdges += edgeAngleDict[i]
    debug("{}\t{}".format(i, edgeAngleDict[i]))

regularity["Parallelity"] = sumParallelEdges/totalEdges
allcriteria["Parallelity"] = {
    "total": totalEdges, 
    "count": sumParallelEdges,
    "points": regularity["Parallelity"]}

# add all values to sumAngleEqualitydebug ("total:\t{}\tregular:\t{}".format(totalEdges, sumParallelEdges))
debug("total:\t{}\tregular:\t{}".format(totalEdges, sumParallelEdges))
debug ("Parallel Line Regularity:\t{}".format(regularity["Parallelity"])) 
debug ("Unique Line Angles:\t{}".format(len(edgeAngleDict)))
debug ("--------------------------------")
debug ("EDGE LENGTH\t\t\t\t1 point")
debug ("--------------------------------sumAngleEquality")
debug ("--------------------------------")


# ------------------------------------------------------------------------------
# MEASURE EDGE LENGTH EQUALITY
# ------------------------------------------------------------------------------

# iterate over every edge in the mesh, calculate its length, if the value already exists
# add the incremental counter for that length 
# ------------------------------------------------------------------------------

sumLengthEquality = 0
for i in edgeLengths:
    if edgeLengthDict[i] > 1:
        sumLengthEquality += edgeLengthDict[i]
    debug("{}\t{}".format(i, edgeLengthDict[i]))
    
regularity["Length Equality"] = sumLengthEquality/totalEdges
regularity["Edge Equality Ratio"] = 1-(len(edgeLengthDict)/totalEdges)

allcriteria["Length Equality"] = {
    "total": totalEdges, 
    "count": sumLengthEquality, 
    "points": regularity["Length Equality"]}
    
allcriteria["Length Equality Inverse"] = {
    "total": totalEdges, 
    "count": len(edgeLengthDict), 
    "points": regularity["Edge Equality Ratio"]}

debug ("total:\t{}\tequal:\t{}".format(totalEdges, sumLengthEquality))
debug ("Edge Length Equality:\t{}".format(regularity["Length Equality"])) 
debug ("Unique Edge Lengths:\t{}".format(len(edgeLengthDict))) 
debug ("Edge Equality Ratio:\t{}".format(regularity["Edge Equality Ratio"])) 


# ------------------------------------------------------------------------------
# MEASURE ANGLE EQUALITY 
# ------------------------------------------------------------------------------

# iterate over every face in the mesh, calculate and record each corner angle
# add the incremental counter for each occurance of that corner angle
# ------------------------------------------------------------------------------


debug ("POLYGONS")
cornerCount = 0
debug("f#\tv#\tangle")
for face in me.polygons:
    verts = face.vertices[:] 
    for i in range(len(verts)):
        cornerCount += 1    
        # get edge vectors
        vplus = i+1
        if  vplus >= len(verts):
            vplus = 0
        #endif
        # calculate the corner angles by finding vector of edges ev1 ev2
        ev1 = me.vertices[verts[i]].co - me.vertices[verts[vplus]].co
        ev2 = me.vertices[verts[i]].co - me.vertices[verts[i-1]].co
        a = ev1.angle(ev2)    
        cA = round(math.degrees(a), accuracy)
        # add the calculated angle to vertex map
        vertexMap[verts[i]]['radians'].append(a)
        vertexMap[verts[i]]['degrees'].append(cA)
        
        debug ("{}\t{}\t{}".format(face.index, verts[i], cA))
        if cA in cornerAngleDict:   
            cornerAngleDict[cA] +=1
        else:
            cornerAngleDict[cA] = 1
            cornerAngles.append(cA)


debug ("\n")       
debug ("--------------------------------")
debug ("ANGLE EQUALITY\t\t\t1 point")
debug ("--------------------------------")
debug ("angle\tcount")
debug ("--------------------------------")

# sum all instace of angle equality > 1
sumAngleEquality = 0
for i in cornerAngles:
    if cornerAngleDict[i] > 1:
        sumAngleEquality += cornerAngleDict[i]
    debug("{}\t{}".format(i, cornerAngleDict[i]))
debug ("--------------------------------")    

# record angle equality 
regularity["Angle Equality"] = sumAngleEquality/cornerCount

# record unique angles
regularity["Unique Angles"] = 1-len(cornerAngleDict)/cornerCount

#print(len(cornerAngleDict), cornerAngleDict, cornerCount)

debug ("total:\t{}\tequal:\t{}".format(cornerCount, sumAngleEquality))
debug ("Vertex Angle Equality:\t{}".format(regularity["Angle Equality"]))
debug ("Unique Vertex Angles:\t{}".format(len(cornerAngleDict)))    
debug ("1-(Unique/Total):\t{}".format(regularity["Unique Angles"])) 

allcriteria["Angle Equality"] = {
    "total": cornerCount, 
    "count": sumAngleEquality, 
    "points": regularity["Angle Equality"]}

allcriteria["Angle Uniqueness"] = {
    "total": cornerCount, 
    "count": len(cornerAngleDict), 
    "points": regularity["Unique Angles"]}
    

# ------------------------------------------------------------------------------
# MEASURE ANGLE REGULARITY 
# ------------------------------------------------------------------------------
debug ("\n")    
debug ("--------------------------------")
debug ("ANGLE REGULARITY\t\t1 point")
debug ("--------------------------------")
debug ("Using angles: 90,45,22.5,11.25,60,30,15,7.5")

# define the regular angles
regularAngles = [180,157.5,135,112.5,90,67.5,45,22.5,11.25,165,150,120,105,75,60,30,15,7.5]
# create a list from the intersection of regularAngles and cornerAngles 
# generates a list of matching angle values, accuracy settings affect this significantly
matchedAngles = list(set(regularAngles).intersection(cornerAngles))
matchedAngleCount = 0

# sum all the matches
for m in matchedAngles:
    matchedAngleCount += cornerAngleDict[m]

# record all the matched angles
regularity["Angle Regularity"] = matchedAngleCount/cornerCount

debug ("MATCHED REGULARS:\t{}".format(len(matchedAngles)))  
debug ("ANGLE REGULARITY:\t{}".format(regularity["Angle Regularity"])) 

allcriteria["Angle Regularity"] = {
    "total": cornerCount, 
    "count": matchedAngleCount, 
    "points": regularity["Angle Regularity"]}

# ------------------------------------------------------------------------------
# MEASURE ANGLE DIVISIBILITY 
# ------------------------------------------------------------------------------

debug ("\n")  
debug ("--------------------------------")
debug ("ANGLE DIVISIBILITY\t\t1 point")
debug ("--------------------------------")

vertexAngleCount = 0
divisibilityCount = 0
uniqueVertexAngleDict = {}
for v in vertexMap: 
    vertexAngleCount += len(vertexMap[v]['degrees'])
    dividedAngles = list(round(x/2, 2) for x in vertexMap[v]['degrees'])
    doubledAngles = list(round(x*2, 2) for x in vertexMap[v]['degrees'])
    matchedSameAngles = list(set(vertexMap[v]['degrees']).intersection(vertexMap[v]['degrees']))
    matchedDividedAngles = list(set(dividedAngles).intersection(vertexMap[v]['degrees']))
    matchedDoubledAngles = list(set(doubledAngles).intersection(vertexMap[v]['degrees']))
    matchAngleCount = 0
    thisVertexAngleCount = len(vertexMap[v]['degrees'])
    vertexAngleCounter = Counter(vertexMap[v]['degrees'])
    debug ("vertexAngleCounter {} {}".format(vertexMap[v], vertexAngleCounter))
    
    for a in matchedSameAngles:
        if (vertexAngleCounter[a] > 1): 
            matchAngleCount += vertexAngleCounter[a]
        if a in uniqueVertexAngleDict:
            uniqueVertexAngleDict[a] +=1
        else:       
            uniqueVertexAngleDict[a] = 1
    
    for a in matchedDividedAngles:
        if (vertexAngleCounter[a] > 1):
            matchAngleCount += vertexAngleCounter[a]
        if a in uniqueVertexAngleDict:
            uniqueVertexAngleDict[a] +=1
        else:
            uniqueVertexAngleDict[a] = 1

    for a in matchedDoubledAngles:
        if (vertexAngleCounter[a] > 1):
            matchAngleCount += vertexAngleCounter[a]
        if a in uniqueVertexAngleDict:
            uniqueVertexAngleDict[a] +=1
        else:
            uniqueVertexAngleDict[a] = 1
           
    thisAngleCount = 0 
    if matchAngleCount > thisVertexAngleCount:
        thisAngleCount = matchAngleCount
        matchAngleCount = thisVertexAngleCount
        

    debug("matchAngleCount {} vertexAngleCount {} {} ".format(matchAngleCount, thisVertexAngleCount, thisAngleCount))
    
    divisibilityCount += matchAngleCount
        
    debug ("angles {} sameAngles matched {}".format(vertexMap[v]['degrees'], matchedSameAngles))
    debug ("angles {} dividedAngles {} matched {}".format(vertexMap[v]['degrees'], dividedAngles, matchedDividedAngles))
    debug ("angles {} doubledAngles {} matched {}".format(vertexMap[v]['degrees'], doubledAngles, matchedDoubledAngles))


regularity["Angle Divisibility"] = divisibilityCount/vertexAngleCount

allcriteria["Angle Divisibility"] = {
    "total": vertexAngleCount, 
    "count": divisibilityCount, 
    "points": regularity["Angle Divisibility"]}

# set the default object thickness value at 0.1 (paper)
try: 
    thickness = obj['thickness']
except:
    obj['thickness'] = 0.1
    thickness = 0.1
    
# Calculate fold density by multiplying the length of edges and dividing by area
# super one line python calculation!
meshArea = sum(f.area for f in me.polygons)
density = totalEdgeLength*thickness*math.pi/meshArea

# create a dict to record density specific info
densitydict = {}
densitydict["Fold Density"]  = density
densitydict["Area"] = meshArea
densitydict["Edge Count"]    = totalEdges
densitydict["Edge Length"]   = totalEdgeLength
densitydict["Shortest Edge"] = min(edgeLengths)
densitydict["Longest Edge"]  = max(edgeLengths)
densitydict["Edge Length Average"]    = totalEdgeLength/totalEdges

# record fold density
regularity["Fold Density"] = 1-density

# record fold density inverse
allcriteria["Fold Density Inverse"] = {
    "total": int(meshArea), 
    "count": int(totalEdgeLength), 
    "points": regularity["Fold Density"]}

# ------------------------------------------------------------------------------
# CALCULATE OVERALL REGULARITY 
# ------------------------------------------------------------------------------
# this section calculates the regularity index, at the same time it generates
# tables in markdown pipe syntax. 

totalRegularity = 0
regularAccuracy = 3  
for r in regularity:  
    totalRegularity += regularity[r]

sm("\n")

sm ("| Criteria             | Total   |")
sm ("|----------------------|--------:|")
for d in densitydict:
    sm ("| {}|{} |".format(d.ljust(21), str(round(densitydict[d], 3)).rjust(8)))   
sm("\n")
sm ("Table: Fold Density: {} {}#tbl:{}-ri-fd{}".format(me.name, "{", me.name, "}"))
sm("\n")
sm("\n")

# single table header criteria
sm ("| Criteria                       | Count   | Total   | Index   |")
sm ("|--------------------------------|--------:|--------:|--------:|")
  
for c in allcriteria:
    sm("| {} | {} | {} | {} | ".format(c.ljust(30), 
        str(allcriteria[c]['count']).rjust(7), 
        str(allcriteria[c]['total']).rjust(7), 
        str(round(allcriteria[c]['points'], regularAccuracy)).rjust(7) ))
    grph("{}\t{}".format( getAbr(c) , str(round(allcriteria[c]['points'], regularAccuracy)) ))
    

sm ("|**Origami Regularity Index:**   | {} | {} | {} |\n".format("-".rjust(7), "-".rjust(7), str(round(totalRegularity/len(regularity), regularAccuracy)).rjust(7) ))

# table title
sm ("Table: R.I.: {} {}#tbl:{}-ri-cb{} Thickness: {}mm\n\n".format(me.name, "{", me.name, "}", str(round(thickness, regularAccuracy))))

# multi-model table 
multimodel_head  = "| {} |".format("".ljust(30))
multimodel_data_points  = "| {} R.I. points |".format(me.name.ljust(19))
multimodel_data_count   = "| {} count |".format("".ljust(24))
multimodel_data_total   = "| {} total |".format("".ljust(24))
multimodel_footer = ""
multimodel_abreviations = ""
criteria_names = []

# Calculate Regularity Index

RegularityIndex = totalRegularity/len(regularity)
allcriteria["Total"] = {
    "total": len(regularity), 
    "count": totalRegularity, 
    "points": RegularityIndex }

for c in allcriteria:
    criteria_names.append(c)
criteria_names.sort()

for c in criteria_names:
    multimodel_abreviations += "**{}**:{}, ".format(getAbr(c), c)
    multimodel_head += " {} |".format(getAbr(str(c)).ljust(7)) 
    
    if c == "Total":
        multimodel_data_total  += " **{}**|".format(getVal(allcriteria,c,"total", 3).rjust(5))
        multimodel_data_count  += " **{}**|".format(getVal(allcriteria,c,"count", 0).rjust(5))
        multimodel_data_points += " **{}**|".format(getVal(allcriteria,c,"points",3).rjust(5))
    else:
        multimodel_data_total  += " {} |".format(getVal(allcriteria,c,"total", 0).rjust(7))
        multimodel_data_count  += " {} |".format(getVal(allcriteria,c,"count", 0).rjust(7))
        multimodel_data_points += " {} |".format(getVal(allcriteria,c,"points",3).rjust(7))

multimodel_footer = "Table: R.I. {} #tbl:multmodels".format(multimodel_abreviations[:-2])

# add lines to summary 

sm (multimodel_head)
sm (multimodel_data_points)
liner(multimodel_data_points)
sm (multimodel_data_count)
sm (multimodel_data_total)
sm (multimodel_footer)

file.close()
summary.close()
graph.close()
ln.close()


# analysis of valency to examine nodal valency, criteria was investigated by not implemented in the R.I.

sumvalency = 0
complex_valency = 0
print("##################--------------------")
# caculate valency for each vertex
for i in vertexMap:    
    vertexMap[i]['valency'] = len(vertexMap[i]['degrees'])
    if sum(vertexMap[i]['degrees']) < 360:
        vertexMap[i]['valency'] += 1 
        
    if sum(vertexMap[i]['degrees']) >= 360:    
        sumvalency += vertexMap[i]['valency']
    
    if (vertexMap[i]['valency']) > 6:
        complex_valency +=1
    #print (i, vertexMap[i])
    # valency
print("average:", sumvalency/len(vertexMap), "n", len(vertexMap), "sum", sumvalency)
print("sum complex:", complex_valency)
   