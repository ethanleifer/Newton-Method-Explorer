# python lab exercise to explore the relationship between the initial guess in Newton's Method and the root that the method converges to.
# Lab exercise for Nonlinear Dynamics at Dwight-Englewood
# Me and Garrett colabed for the change in the zoom function

# imports
from DEgraphics import *
import cmath as cm
import math as m
from NLDUtils import *

#
# globals
SIZE = 400
winNewtons = DEGraphWin(width=SIZE, height=SIZE,
                        defCoords=[-5, -5, 5, 5], offsets=[50, 50], hasTitlebar=False,
                        title="Newton's Method Explorer by Ethan Leifer", hBGColor="black")

# below is the creation of my gui. I have seperated it into sections to make it easy to see what does what.

# control pannel window:
winCP = DEGraphWin(title="CONTROL PANNEL", width=400, height=380, defCoords=[0, 0, 8, 6], offsets=[450, 50], hBGColor='black')

# global list to hold the roots of the respective functions
# and their root-dots (graphical Circles) for display purposes
roots = []
rootDots = []
dotSizeRatio = 0.01  # 1% size

# epsilon value for stopping while loop
eps = .000000001

# color multipler to control the spread of RGB values
multCol = 5

# global list to hold colors for the various roots
colors = [[0, 255, 0], [255, 0, 0], [0, 0, 255], [255, 255, 0], [255, 0, 255], [0, 255, 255]]

# global list to hold function names
functions = ["(z-1)*(z+1)", "z*(z*z-1)", "z*z*z*z-1"]

# global font variable to change the font of all buttons
font = "arial"

# main buttons for the control pannel below:
btnExit = Button(win=winCP, center=Point(2, .5), width=3.8, height=.8, text="EXIT", fontSize=32, backcolor="red", fontFace=font)
btnDraw = Button(win=winCP, center=Point(3, 1.5), width=1.8, height=.8, text="DRAW", fontSize=25, backcolor='blue', fontFace=font, textcolor='white')
btnClear = Button(win=winCP, center=Point(1, 1.5), width=1.8, height=.8, text="CLEAR", fontSize=25, backcolor='blue', fontFace=font, textcolor='white')
btnChangeScheme = Button(win=winCP, center=Point(3, 2.5), width=1.8, height=.8, text="SWITCH\nCOLOR\nSCHEME", fontSize=12, backcolor='blue', fontFace=font, textcolor='white')
btnZoom = Button(win=winCP, center=Point(1, 3.5), width=1.8, height=.8, text="ZOOM", fontSize=25, backcolor='blue', fontFace=font, textcolor='white')
btnHideShowRootDots = Button(win=winCP, center=Point(1, 2.5), width=1.8, height=.8, text="SHOW\nROOTS", fontSize=16, backcolor='blue', fontFace=font, textcolor='white')

# zoom in and zoom out buttons
btnIn = Button(win=winCP, center=Point(3, 3.75), width=1.8, height=.4, text="IN", fontSize=25, backcolor='blue', fontFace=font, textcolor='white')
btnOut = Button(win=winCP, center=Point(3, 3.25), width=1.8, height=.4, text="OUT", fontSize=25, backcolor='blue', fontFace=font, textcolor='white')

# title text object
txtTitle = Text(Point(4, 5.5), "Newtons Method Explorer")
txtTitle.setFace(font)
txtTitle.setSize(30)
txtTitle.draw(winCP)


# maximum iterations entry object
entIters = Entry(Point(5, .25,), 10)
entIters.draw(winCP)
entIters.setText("")
entIters.setFace(font)
btnEnterIters = Button(winCP, center=Point(7.25, .5), width=1.25, height=.8, text="Enter", fontSize=15, backcolor='blue', fontFace=font, textcolor='white')
txtIters = Text(Point(5.25, .75), "Max Iterations = ")
txtIters.setFace(font)
txtIters.draw(winCP)


# number of sweeps entry object
entSweeps = Entry(Point(5, 1.25,), 10)
entSweeps.draw(winCP)
entSweeps.setText("")
entSweeps.setFace(font)
btnEnterSweeps = Button(winCP, center=Point(7.25, 1.5), width=1.25, height=.8, text="Enter", fontSize=15, backcolor='blue', fontFace=font, textcolor='white')
txtSweeps = Text(Point(5.25, 1.75), "Sweeps = ")
txtSweeps.setFace(font)
txtSweeps.draw(winCP)

# resulotion entry object
entResolution = Entry(Point(5, 2.25,), 10)
entResolution.draw(winCP)
entResolution.setText("")
entResolution.setFace(font)
btnEnterResolution = Button(winCP, center=Point(7.25, 2.5), width=1.25, height=.8, text="Enter", fontSize=15, backcolor='blue', fontFace=font, textcolor='white')
txtResolution = Text(Point(5.25, 2.75), "Resolution = ")
txtResolution.setFace(font)
txtResolution.draw(winCP)

# color multipler entry object
entColorMult = Entry(Point(5, 3.25,), 10)
entColorMult.draw(winCP)
entColorMult.setText("")
entColorMult.setFace(font)
btnEnterColorMult = Button(winCP, center=Point(7.25, 3.5), width=1.25, height=.8, text="Enter", fontSize=15, backcolor='blue', fontFace=font, textcolor='white')
txtColorMult = Text(Point(5.25, 3.75), "Color Multiplier = ")
txtColorMult.setFace(font)
txtColorMult.draw(winCP)

# epsilon entry object
entEpsilon = Entry(Point(5, 4.25,), 10)
entEpsilon.draw(winCP)
entEpsilon.setText("")
entEpsilon.setFace(font)
btnEnterEpsilon = Button(winCP, center=Point(7.25, 4.5), width=1.25, height=.8, text="Enter", fontSize=15, backcolor='blue', fontFace=font, textcolor='white')
txtEpsilon = Text(Point(5.25, 4.75), "Epsilon = ")
txtEpsilon.setFace(font)
txtEpsilon.draw(winCP)


# change buttons and current function text object
reformattedFunctions = ["1. " + str(functions[0]), "2. " + str(functions[1]), "3. " + str(functions[2])]
txtCurrentFunction = Text(Point(2, 4.75), "Current Function = ")
txtCurrentFunction.draw(winCP)
drpFcn = DropDown(Point(1, 4.25), width=7, choices=reformattedFunctions)
drpFcn.draw(winCP)
btnFcnEnter = Button(winCP, center=Point(3, 4.25), width=1.8, height=.4, text="Enter", fontSize=15, backcolor='blue', fontFace=font, textcolor='white')

# these functions and variables make it easy to activate, deactive and update text elements on my GUI
mainBtnsActive = False
zoomBtnsActive = False
fcnBtnsActive = False


def changeActivityMainBtns():
    """Deactivates or activates main buttons on winCP according to boolean variable mainBtnsActive which keeps track of if the according buttons are active"""
    global mainBtnsActive

    if mainBtnsActive:
        btnExit.deactivate()
        btnDraw.deactivate()
        btnClear.deactivate()
        btnChangeScheme.deactivate()
        btnZoom.deactivate()
        btnEnterIters.deactivate()
        btnEnterSweeps.deactivate()
        btnEnterResolution.deactivate()
        btnHideShowRootDots.deactivate()
        btnFcnEnter.deactivate()
        btnEnterColorMult.deactivate()
        btnEnterEpsilon.deactivate()
    else:
        btnExit.activate()
        btnDraw.activate()
        btnClear.activate()
        btnChangeScheme.activate()
        btnZoom.activate()
        btnEnterIters.activate()
        btnEnterSweeps.activate()
        btnEnterResolution.activate()
        btnHideShowRootDots.activate()
        btnFcnEnter.activate()
        btnEnterColorMult.activate()
        btnEnterEpsilon.activate()

    mainBtnsActive = not(mainBtnsActive)

def changeActivityZoomBtns():
    """Deactivates or activates zoom buttons on winCP according to boolean variable, zoomBtnsActive, which keeps track of if the according buttons are active"""

    global zoomBtnsActive
    if zoomBtnsActive:
        btnIn.deactivate()
        btnOut.deactivate()
    else:
        btnIn.activate()
        btnOut.activate()

    zoomBtnsActive = not(zoomBtnsActive)

def updateTextBoxes(maxIters, sweeps, resolution, fcn):
    """Updates each of the textboxes on winCP according to variables"""
    txtIters.setText("Max Iterations = " + str(maxIters))
    txtSweeps.setText("# of Sweeps = " + str(sweeps))
    txtResolution.setText("Resolution = " + str(resolution))
    txtCurrentFunction.setText("Current Function = " + str(functions[fcn]))
    txtEpsilon.setText("Epsilon = " + str(eps))
    txtColorMult.setText("Color Multiplier = " + str(multCol))

def f(z, whichFunction=0):
    """f(z)"""
    if whichFunction == 0:
        return (z - 1) * (z + 1)

    elif whichFunction == 1:
        return z * (z - 1) * (z + 1)

    elif whichFunction == 2:
        return z * z * z * z - 1

def fprime(z, whichFunction=0):
    """f'(z)"""
    if whichFunction == 0:
        return 2.0 * z

    elif whichFunction == 1:
        return 3.0 * z * z - 1.0

    elif whichFunction == 2:
        return 4.0 * z * z * z

def newtons(z, fcn, numIters):
    """iterates newtons root-finding algorithm for specified function"""
    for n in range(numIters):
        z = z - f(z, fcn) / fprime(z, fcn)
    return z

def newtonsNumIters(z, fcn, maxIters, epsilon=.01):
    """iterates newtons root-finding algorithm for specified function while the distance between the closest root and z is greater then epsilon"""
    numIters = 0
    while maxIters > numIters and epsilon < getDistanceOfCloseRoot(z, roots[fcn]):
        # iterate z if condition fails
        z = z - (f(z, fcn) / fprime(z, fcn))
        numIters += 1
    return (z, numIters)

def getColorGradient(z, fcn, numIters, maxIters, colorscheme='1'):
    """returns a color scheme based on the number of iterations"""
    # note: I was going to add the ability to add different color schemes but I realized that this one is the best. You can change it by changing the default color scheme in the function if you want.
    if colorscheme == '1':
        # get the color of the close root
        closeRoot = getCloseRootIndex(z, roots[fcn])
        rootColor = colors[closeRoot]
        color = [0, 0, 0]  # THIS IS THE FINAL COLOR
        # go through each rgb value
        for i in range(3):
            # this transformation:
                # if rootColor[i] is 0 then the whole thing will stay 0, otherwise it will scale to 255
                # multCol expands the distance between each color
                # 255 - ... inverts the color scheme
            color[i] = (255 - abs(int(numIters / maxIters * multCol * rootColor[i]))) % 255
        return color_rgb(color[0], color[1], color[2])

    # THESE ARE OTHER COLOR SCHEMES I DEVELOPED (MOST ARE GRAYSCALES BUT WORTH A LOOK) (most are similar to the one above)
    if colorscheme == '2':
        color = colors[getCloseRootIndex(z, roots[fcn])]
        for i in range(3):
            color[i] = (int(255 - float(numIters) / maxIters * 10000)) % 255  # gradient from light to dark
        return color_rgb(color[0], color[1], color[2])

    if colorscheme == '3':
        # THIS IS AN AMAZING GRAYSCALE!!!
        color = colors[getCloseRootIndex(z, roots[fcn])]
        for i in range(3):
            color[i] = (255 - numIters) * 10 % 255
        return color_rgb(color[0], color[1], color[2])

    if colorscheme == '4':
        color2 = colors[getCloseRootIndex(z, roots[fcn])]
        color = [0, 0, 0]  # new color
        for i in range(3):
            if color2[i] == 255:
                color[i] = abs((color2[i] - (numIters * 10000 % 255)) % 255)
        return color_rgb(color[0], color[1], color[2])

    if colorscheme == '5':
        color2 = colors[getCloseRootIndex(z, roots[fcn])]
        color = [0, 0, 0]  # new color
        for i in range(3):
            # if color2[i] == 255:
                color[i] = int((float(numIters) / maxIters) * 10000) % 255
        return color_rgb(color[0], color[1], color[2])

    if colorscheme == '6':
        color2 = colors[getCloseRootIndex(z, roots[fcn])]
        color = [0, 0, 0]  # new color
        for i in range(3):
            color[i] = abs(int((((color2[i] * multCol) / maxIters) * multCol * numIters + color2[i]) % 255))
        return color_rgb(color[0], color[1], color[2])

def getDistanceOfCloseRoot(z, rootList):
    """returns the distance of the closet root to z"""
    closeRoot = 0
    minD = abs(z - rootList[closeRoot])
    for rootNum in range(1, len(rootList)):
        d = abs(z - rootList[rootNum])
        if d < minD:
            minD = d
            closeRoot = rootNum
    return minD

def getCloseRootIndex(z, rootList):
    """returns the index of the closet root to z"""
    closeRoot = 0
    minD = abs(z - rootList[closeRoot])
    for rootNum in range(0, len(rootList)):
        d = abs(z - rootList[rootNum])
        if d < minD:
            minD = d
            closeRoot = rootNum
    return closeRoot

def getColorOfCloseRoot(z, rootList):
    """returns the color of the closet root to z"""
    closeRoot = 0
    minD = abs(z - rootList[closeRoot])
    for rootNum in range(0, len(rootList)):
        d = abs(z - rootList[rootNum])
        if d < minD:
            minD = d
            closeRoot = rootNum
    color = colors[closeRoot]
    return color_rgb(color[0], color[1], color[2])

def displayRoots():
    """display root dots"""
    global rootDots
    for dot in rootDots:
        dot.draw(winNewtons)

def undrawRoots():
    """undraws all the root dots"""
    global rootDots
    for dot in rootDots:
        dot.undraw()

def generateRootDots(rootList):
    """generates a small circle for each root and adds it to a list, rootDots"""
    global rootDots
    for i in range(len(rootList)):
        dot = Circle(Point(rootList[i].real, rootList[i].imag), dotSizeRatio * (winNewtons.currentCoords[2] - winNewtons.currentCoords[0]))
        color = colors[i]
        dot.setFill(color_rgb(color[0], color[1], color[2]))
        dot.setOutline("black")
        rootDots.append(dot)

def generateNewtonFractal(fcn, numIters, rootList, resolution=3, numSweeps=4, gradient=True):
    """generates the NewtonsFractal"""
    global rootDots

    # define screen settings parameters
    rm = winNewtons.currentCoords[0]
    im = winNewtons.currentCoords[1]
    rM = winNewtons.currentCoords[2]
    iM = winNewtons.currentCoords[3]
    rstep = resolution * (rM - rm) / winNewtons.width
    istep = resolution * (iM - im) / winNewtons.height

    # clear the window (erase it)
    winNewtons.clear()

    # define custom width for dot-size
    screenW = rM - rm

    # define the actual dots
    generateRootDots(rootList)

    # generates the fractal
    maxIters = numIters
    for sweep in range(numSweeps):
        r = rm + sweep * rstep
        while r < rM:
            i = im
            while i < iM:
                z = complex(r, i)
                # if gradient is true it will graph the newtons fractal using my graident
                if gradient:
                    result = newtonsNumIters(z, fcn, maxIters, epsilon=eps)
                    z = result[0]
                    numIters = result[1]
                    winNewtons.plot(r, i, getColorGradient(z, fcn, numIters, maxIters, colorscheme='1'))
                # use Mr. Iwanski's color scheme
                else:
                    z = newtons(z, fcn, maxIters)
                    winNewtons.plot(r, i, getColorOfCloseRoot(z, rootList))
                i += istep
            r += rstep * numSweeps
            winNewtons.update()

def zoom(hasZoomedIn):
    """zoom in or out on the newtons graph window"""

    changeActivityMainBtns()
    changeActivityZoomBtns()

    clickPoint = winCP.getMouse()

    if btnIn.clicked(clickPoint):
        winNewtons.zoom('in')

    if btnOut.clicked(clickPoint):
        winNewtons.zoom('out')

    # if the user doesnt click on either button it puts the user back onto main options menu. I did this because I wanted user to be able to cancel zoom

    changeActivityMainBtns()
    if zoomBtnsActive:
        changeActivityZoomBtns()

def main():
    global winNewtons, roots, multCol, eps

    # append roots of functions
    #   0. roots of (z-1)(z+1)
    roots.append([complex(1, 0), complex(-1, 0)])
    #   1. roots of z(z-1)(z+1)
    roots.append([complex(0, 0), complex(1, 0), complex(-1, 0)])
    #   2. roots of z^4 - 1
    roots.append([complex(1, 0), complex(-1, 0), complex(0, 1), complex(0, -1)])

    # choose function and store its roots in currRoots
    myFcn = 2
    currRoots = roots[myFcn]

    # define number of iterations to run
    iterations = 100
    resolution = 1
    sweeps = 4
    winCP.displayGrid()
    gradient = True
    hasZoomedIn = False

    changeActivityMainBtns()
    updateTextBoxes(iterations, sweeps, resolution, myFcn)

    clickPoint = winCP.getMouse()

    clickPoint = winCP.getMouse()

    while not(btnExit.clicked(clickPoint)):

        generateNewtonFractal(myFcn, iterations, currRoots, resolution, sweeps, gradient)

        if btnClear.clicked(clickPoint):
            winNewtons.clear()

        if btnChangeScheme.clicked(clickPoint):
            gradient = not(gradient)

        if btnZoom.clicked(clickPoint):
            hasZoomedIn = zoom(hasZoomedIn)

        # change maximum iterations
        if btnEnterIters.clicked(clickPoint):
            if isValid(type(1), entIters.getText()):
                iterations = abs(int(entIters.getText()))
            entIters.setText("")

        # change sweeps
        if btnEnterSweeps.clicked(clickPoint):
            if isValid(type(1), entSweeps.getText()):
                sweeps = abs(int(entSweeps.getText()))
            entSweeps.setText("")

        # change resolution
        if btnEnterResolution.clicked(clickPoint):
            if isValidBetween(type(1), [0, 5], entResolution.getText()):
                resolution = abs(int(entResolution.getText()))
            entResolution.setText("")

        # change color multipler
        if btnEnterColorMult.clicked(clickPoint):
            if isValid(type(1.0), entColorMult.getText()):
                multCol = abs(int(entColorMult.getText()))
            entColorMult.setText("")

        # change the epsilon value
        if btnEnterEpsilon.clicked(clickPoint):
            if isValid(type(1.0), entEpsilon.getText()):
                eps = abs(float(entEpsilon.getText()))
            entEpsilon.setText("")

        # hide and show root dots
        if btnHideShowRootDots.clicked(clickPoint):
            generateRootDots(roots[myFcn])
            if rootDots[0].isDrawn():
                undrawRoots()
                btnHideShowRootDots.setCaption(winCP, Point(1, 2.5), "SHOW\nROOTS")

            else:
                displayRoots()
                btnHideShowRootDots.setCaption(winCP, Point(1, 2.5), "HIDE\nROOTS")

            # reset formatting of btn to match
            btnHideShowRootDots.setForeColor('white')
            btnHideShowRootDots.caption.setSize(16)
            btnHideShowRootDots.caption.setFace(font)

        if btnFcnEnter.clicked(clickPoint):
            myFcn = int(drpFcn.getOption()[0]) - 1

        updateTextBoxes(iterations, sweeps, resolution, myFcn)

        clickPoint = winCP.getMouse()

    print("closing windows")
    winNewtons.close()
    winCP.close()


if __name__ == "__main__":
    main()
