# DEgraphics.py
"""Object-oriented graphics library that modifies the
   original graphics.py module with added functionality,
   particularly for the DE NonLinear Dynamics course,
   creating a standalone window called a DEGraphWin.

   The original library was designed to make it very easy
   for novice programmers to experiment with computer graphics
   in an object-oriented fashion, as written by John Zelle for
   use with the book "Python Programming: An Introduction to
   Computer Science" (Franklin, Beedle & Associates).

   LICENSE: This is open-source software released under the
   terms of the GPL (http://www.gnu.org/licenses/gpl.html).

   PLATFORMS: The package is a wrapper around Tkinter and
   should run on any platform where Tkinter is available.

   Latest version modified February 2020 by JS Iwanski
   Originally modified in 2018 by JS Iwanski
   See original graphics.py for other version information.
"""

import time, os, sys

try:  # import as appropriate for 2.x vs. 3.x
   import tkinter as tk
except:
   import Tkinter as tk


##########################################################################
# Module Exceptions

class GraphicsError(Exception):
    """Generic error class for graphics module exceptions."""
    pass

OBJ_ALREADY_DRAWN = "Object currently drawn"
UNSUPPORTED_METHOD = "Object doesn't support operation"
BAD_OPTION = "Illegal option value"

##########################################################################
# global variables and functions

_root = tk.Tk()
_root.withdraw()

_update_lasttime = time.time()

def update(rate=None):
    global _update_lasttime
    if rate:
        now = time.time()
        pauseLength = 1/rate-(now-_update_lasttime)
        if pauseLength > 0:
            time.sleep(pauseLength)
            _update_lasttime = now + pauseLength
        else:
            _update_lasttime = now

    _root.update()

############################################################################
# Graphics classes start here
class DEGraphWin(tk.Canvas):
    """A DEGraphWin is a toplevel window for displaying graphics. It
       stores its current custom coordinates, default coordinates,
       size in pixels (width,height), two forms of coordinate axes,
       and various display characteristics of those axes."""

    def __init__(self, title = "Dwight-Englewood graphics window",
    	         defCoords=[-10,-10,10,10],
                 margin = [0,0],
                 axisType = 0,
                 axisColor = 'black',
                 width = 600, height = 600,
                 offsets=[0,0], autoflush = False,
                 hasTitlebar = True,
                 hThickness=2,hBGColor="green",
                 borderWidth=0):

        assert type(title) == type(""), "Title must be a string"
        self.master = tk.Toplevel(_root)
        self.master.protocol("WM_DELETE_WINDOW", self.close)
        tk.Canvas.__init__(self, self.master, width=width, height=height,
                           highlightthickness=hThickness,highlightbackground=hBGColor, bd=borderWidth)
        self.master.title(title)
        if hasTitlebar == False:
            self.master.overrideredirect(True) # removes title bar
        self.master.geometry('%dx%d+%d+%d' % (width, height, offsets[0], offsets[1]))

        self.pack()

        # margin = [h,v], where
        #          h : left and right margins as percentage of total width
        #          v : top and bottom margins as percentage of total height
        # (in other words, h and v should be between 0 and 0.5)

        # axisType:
        #     0 - classic x-y axes
        #     1 - 'box' axis around window

        self.axisType = axisType
        self.axesDrawn = False
        self.axisColor = axisColor
        self.margin = margin

        # zoomBox is a Rectangle that will be drawn when
        # a zoom IN is requested, and then undrawn.
        self.zoomBox = Rectangle(Point(0,0),Point(0,0))
        self.zoomBoxColor = 'black'

        # maintain a list of previous zooms
        self.zoomList = []

        # default coordinates that we can return to
        self.defaultCoords = defCoords

        # default foreground color is black
        self.foreground = "black"

        self.title = title
        self.height = int(height)
        self.width = int(width)
        self.master.resizable(0,0)
        self.items = []
        self.mouseX = None
        self.mouseY = None

        self.bind("<Button-1>", self._onClick)
        self.bind_all("<Key>", self._onKey)

        self.autoflush = autoflush
        self._mouseCallback = None
        self.trans = None
        self.closed = False

        self.currentCoords = []
        self.setCoords(defCoords[0],defCoords[1],defCoords[2],defCoords[3])

        # axes will store two sets of axes:
        #    0 - classic x-y axes (2)
        #    1 - box axes around edges (4)
        self.axes = []
        self.updateAxes(self.axisType,'dotted')
        self.currentAxes = self.axes[self.axisType]

        self.master.lift()
        self.lastKey = ""
        if autoflush: _root.update()

    def __repr__(self):
        if self.isClosed():
            return "<Closed DEGraphWin>"
        else:
            return "DEGraphWin('{}', {}, {})".format(self.master.title(),
                                             self.getWidth(),
                                             self.getHeight())

    def __str__(self):
        return repr(self)

    def __checkOpen(self):
        if self.closed:
            raise GraphicsError("window is closed")

    def _onKey(self, evnt):
        self.lastKey = evnt.keysym

    def clear(self):
        """clears drawn elements on the DEGraphWin"""
        self.delete("all")
        self.redraw()

    def setTitle(self,newTitle):
       """change the title to newTitle"""
       self.master.title(newTitle)

    def setBackground(self, color):
        """Set background color of the window"""
        self.__checkOpen()
        self.config(bg=color)
        self.__autoflush()

    def close(self):
        """Close the window"""
        if self.closed: return
        self.delItems()
        self.closed = True
        self.master.destroy()
        self.__autoflush()

    def isClosed(self):
        return self.closed

    def isOpen(self):
        return not self.closed

    def __autoflush(self):
        if self.autoflush:
            _root.update()

    def __onScreen(self,x,y):
        return (self.currentCoords[0] <= x <= self.currentCoords[2]) and self.currentCoords[1] <= y <= self.currentCoords[3]

    def plot(self, x, y, color="black"):
        """Set pixel (x,y) to the given color"""
        if self.__onScreen(x,y):
            self.__checkOpen()
            xs,ys = self.toScreen(x,y)
            self.create_line(xs,ys,xs+1,ys, fill=color)
            self.__autoflush()

    def plotPixel(self, x, y, color="black"):
        """Set pixel raw (independent of window coordinates) pixel (x,y) to color"""
        self.__checkOpen()
        self.create_line(x,y,x+1,y, fill=color)
        self.__autoflush()

    def flush(self):
        """Update drawing to the window"""
        self.__checkOpen()
        self.update_idletasks()

    def getMouse(self):
        """Wait for mouse click and return Point object representing the click"""
        self.update()      # flush any prior clicks
        self.mouseX = None
        self.mouseY = None
        while self.mouseX == None or self.mouseY == None:
            self.update()
            if self.isClosed(): raise GraphicsError("getMouse in closed window")
            time.sleep(.1) # give up thread
        x,y = self.toWorld(self.mouseX, self.mouseY)
        self.mouseX = None
        self.mouseY = None
        return Point(x,y)

    def checkMouse(self):
        """Return last mouse click or None if mouse has
        not been clicked since last call"""
        if self.isClosed():
            raise GraphicsError("checkMouse in closed window")
        self.update()
        if self.mouseX != None and self.mouseY != None:
            x,y = self.toWorld(self.mouseX, self.mouseY)
            self.mouseX = None
            self.mouseY = None
            return Point(x,y)
        else:
            return None

    def getKey(self):
        """Wait for user to press a key and return it as a string."""
        self.lastKey = ""
        while self.lastKey == "":
            self.update()
            if self.isClosed(): raise GraphicsError("getKey in closed window")
            time.sleep(.1) # give up thread

        key = self.lastKey
        self.lastKey = ""
        return key

    def checkKey(self):
        """Return last key pressed or None if no key pressed since last call"""
        if self.isClosed():
            raise GraphicsError("checkKey in closed window")
        self.update()
        key = self.lastKey
        self.lastKey = ""
        return key

    def getHeight(self):
        """Return the height of the window"""
        return self.height

    def getWidth(self):
        """Return the width of the window"""
        return self.width

    def toScreen(self, x, y):
        trans = self.trans
        if trans:
            return self.trans.screen(x,y)
        else:
            return x,y

    def toWorld(self, x, y):
        trans = self.trans
        if trans:
            return self.trans.world(x,y)
        else:
            return x,y

    def setMouseHandler(self, func):
        self._mouseCallback = func

    def _onClick(self, e):
        self.mouseX = e.x
        self.mouseY = e.y
        if self._mouseCallback:
            self._mouseCallback(Point(e.x, e.y))

    def addItem(self, item):
        self.items.append(item)

    def delItem(self, item):
        self.items.remove(item)

    def delItems(self):
       for n in range(len(self.items)-1,-1,-1):
          self.items[n].undraw()

    def redraw(self):
        for item in self.items[:]:
            item.undraw()
            item.draw(self)
        self.update()

    def toggleAxes(self):
        """toggles axes from shown to hidden and vice-versa"""
        if self.axesDrawn: # already drawn, so undraw
            for i in range(len(self.currentAxes)):
                self.currentAxes[i].undraw()
        else: # not drawn, so draw 'em
            for i in range(len(self.currentAxes)):
                self.currentAxes[i].setFill(self.axisColor)
                self.currentAxes[i].draw(self)
        self.axesDrawn = not self.axesDrawn

    def updateAxes(self, axType, axisStyle):
        """updates coordinate axes for current scaling"""
        # 0. get rid of old axes
        # first undraw 'em (if drawn)
        if self.axesDrawn:
           for i in range(len(self.currentAxes)):
                self.currentAxes[i].undraw()
        # then empty the list
        while len(self.axes) > 0:
            waste = self.axes.pop()

        # 1. store necessary variables
        xm = self.currentCoords[0]
        xM = self.currentCoords[2]
        ym = self.currentCoords[1]
        yM = self.currentCoords[3]

        # 2. take care of classic axes
        xAxis = Line(Point(xm,0),Point(xM,0),axisStyle)
        yAxis = Line(Point(0,ym),Point(0,yM),axisStyle)
        axes_classic = [xAxis,yAxis]
        self.axes.append(axes_classic)

        # 3. take care of box axes
        hTop = Line(Point(xm,yM - 0.1*(yM-ym)),Point(xM,yM - 0.1*(yM-ym)),axisStyle)
        hBot = Line(Point(xm,ym + 0.1*(yM-ym)),Point(xM,ym + 0.1*(yM-ym)),axisStyle)
        vLef = Line(Point(xm + 0.1*(xM-xm),ym),Point(xm + 0.1*(xM-xm),yM),axisStyle)
        vRgt = Line(Point(xM - 0.1*(xM-xm),ym),Point(xM - 0.1*(xM-xm),yM),axisStyle)
        axes_box = [hTop,hBot,vLef,vRgt]
        self.axes.append(axes_box)

        #4. update axis style
        self.axisType = axType
        self.currentAxes = self.axes[self.axisType]

        #5. redraw axes if necessary
        if self.axesDrawn:
           for i in range(len(self.currentAxes)):
                self.currentAxes[i].setFill(self.axisColor)
                self.currentAxes[i].draw(self)

    def setMargins(self, newMargins):
        # if either new margin percentage is not in [0,0.5)
        # it gets set to 0
        for i in range(len(newMargins)):
            if not(0 <= newMargins[i] < 0.5):
                newMargins[i] = 0
        self.margin = newMargins
        xm = self.currentCoords[0]
        xM = self.currentCoords[2]
        ym = self.currentCoords[1]
        yM = self.currentCoords[3]
        self.setCoords(xm,ym,xM,yM)
        self.clear()

    def setDefaultCoords(self, newDefault):
        self.defaultCoords = newDefault

    def setCoords(self,x1,y1,x2,y2):

        # force x1 < x2 and y1 < y2
        if x1 > x2:
            temp = x1
            x1 = x2
            x2 = temp
        if y1 > y2:
            temp = y1
            y1 = y2
            y2 = temp

        width  = abs(x2 - x1)
        height = abs(y2 - y1)

        self.currentCoords=[x1,y1,x2,y2]

        # calculate new x,y values incorporating margins
        newx1 = x1 - self.margin[0] * width
        newx2 = x2 + self.margin[0] * width
        newy1 = y1 - self.margin[1] * height
        newy2 = y2 + self.margin[1] * height

        # call parent setCoords
        #self.setCoords(newx1,newy1,newx2,newy2)
        self.trans = Transform(self.width, self.height, newx1, newy1, newx2, newy2)
        self.redraw()

    def displayGrid(self, step=1):
        color = 'lightgray'
        lines = []
        for n in range(1, self.currentCoords[2], step):
            line = Line(Point(n,0), Point(n, self.currentCoords[3]))
            line.setOutline(color)
            lines.append(line)
        for n in range(1, self.currentCoords[3], step):
            line = Line(Point(0, n), Point(self.currentCoords[2], n))
            line.setOutline(color)
            lines.append(line)
        for l in lines:
            l.draw(self)

    def zoom(self, whichWay = "in"):
        """permits zooming IN or zooming OUT (back to default)"""
        if whichWay == "in":
            print("Click on " + self.title + " to input one corner of the zoom box")
            pt1 = self.getMouse()
            print("clicked")
            print("Click on " + self.title + " to input the opposite corner of the zoom box")
            pt2 = self.getMouse()
            print("clicked")

            # if the second point results in a degenerate area,
            # must re-select the second point.
            while (pt1.getX() == pt2.getX()) or (pt1.getY() == pt2.getY()):
                print("Click on " + self.title + " to input the opposite corner of the zoom box")
                pt2 = self.getMouse()

            # form the zoomBox - shows the zoom area graphically to user

            pt1X = pt1.getX()
            pt1Y = pt1.getY()
            pt2X = pt2.getX()
            pt2Y = pt2.getY()

            centerX = (pt1X + pt2X) / 2
            centerY = (pt1Y + pt2Y) / 2
            center = Point(centerX, centerY)
            self.zoomBox = Button(self, center, width=abs(pt1X-pt2X), height=abs(pt1Y-pt2Y), text="Please click inside box if this is the zoom you want", backcolor="")
            self.zoomBox.activate()
            clickPoint = self.getMouse()
            if self.zoomBox.clicked(clickPoint):
                doyouwanttozoom = 'y'
            else:
                doyouwanttozoom = 'n'
            # ask if they are sure they want this zoom
            # doyouwanttozoom = input("Is this the zoom you want? (type 'y' or 'n')")
            # while not(doyouwanttozoom == 'y' or doyouwanttozoom == 'n'):
                # doyouwanttozoom = input("Please type 'y' or 'n': ")
            if doyouwanttozoom == 'y':
                # erase the zoomBox
                self.zoomBox.undraw()
                # erase the window
                self.clear()
                x1 = min(pt1.x,pt2.x)
                x2 = max(pt1.x,pt2.x)
                y1 = min(pt1.y,pt2.y)
                y2 = max(pt1.y,pt2.y)
                self.setCoords(x1,y1,x2,y2)
                print("Zoomed in to [" + '{:03.4f}'.format(self.currentCoords[0])
                      + "," + '{:03.4f}'.format(self.currentCoords[1])
                      + "," + '{:03.4f}'.format(self.currentCoords[2])
                      + "," + '{:03.4f}'.format(self.currentCoords[3]) + "]")
                return True
            else:
                self.zoomBox.undraw()
                return False
        elif whichWay == "out":
            # zooms back to defaultCoords
            print("Zooming OUT to [" + '{:03.4f}'.format(self.defaultCoords[0])
                      + "," + '{:03.4f}'.format(self.defaultCoords[1])
                      + "," + '{:03.4f}'.format(self.defaultCoords[2])
                      + "," + '{:03.4f}'.format(self.defaultCoords[3]) + "]")
            x1 = self.defaultCoords[0]
            y1 = self.defaultCoords[1]
            x2 = self.defaultCoords[2]
            y2 = self.defaultCoords[3]

            # erase the window
            self.clear()
            self.setCoords(x1,y1,x2,y2)
            return True

class Transform:

    """Internal class for 2-D coordinate transformations"""

    def __init__(self, w, h, xlow, ylow, xhigh, yhigh):
        # w, h are width and height of window
        # (xlow,ylow) coordinates of lower-left [raw (0,h-1)]
        # (xhigh,yhigh) coordinates of upper-right [raw (w-1,0)]
        xspan = (xhigh-xlow)
        yspan = (yhigh-ylow)
        self.xbase = xlow
        self.ybase = yhigh
        self.xscale = xspan/float(w-1)
        self.yscale = yspan/float(h-1)

    def screen(self,x,y):
        # Returns x,y in screen (actually window) coordinates
        xs = (x-self.xbase) / self.xscale
        ys = (self.ybase-y) / self.yscale
        return int(xs+0.5),int(ys+0.5)

    def world(self,xs,ys):
        # Returns xs,ys in world coordinates
        x = xs*self.xscale + self.xbase
        y = self.ybase - ys*self.yscale
        return x,y


# Default values for various item configuration options. Only a subset of
#   keys may be present in the configuration dictionary for a given item
DEFAULT_CONFIG = {"fill":"",
      "outline":"black",
      "width":"1",
      "arrow":"none",
      "text":"",
      "justify":"center",
                  "font": ("helvetica", 12, "normal")}

class GraphicsObject:

    """Generic base class for all of the drawable objects"""
    # A subclass of GraphicsObject should override _draw and
    #   and _move methods.

    def __init__(self, options):
        # options is a list of strings indicating which options are
        # legal for this object.

        # When an object is drawn, canvas is set to the DEGraphWin(canvas)
        #    object where it is drawn and id is the TK identifier of the
        #    drawn shape.
        self.canvas = None
        self.id = None

        # config is the dictionary of configuration options for the widget.
        config = {}
        for option in options:
            config[option] = DEFAULT_CONFIG[option]
        self.config = config

    def setFill(self, color):
        """Set interior color to color"""
        self._reconfig("fill", color)

    def setOutline(self, color):
        """Set outline color to color"""
        self._reconfig("outline", color)

    def setWidth(self, width):
        """Set line weight to width"""
        self._reconfig("width", width)

    def isDrawn(self):
       if self.canvas:
          return True
       else:
          return False

    def draw(self, graphwin):

        """Draw the object in graphwin, which should be a DEGraphWin
        object.  A GraphicsObject may only be drawn into one
        window. Raises an error if attempt made to draw an object that
        is already visible."""

        if self.canvas and not self.canvas.isClosed(): raise GraphicsError(OBJ_ALREADY_DRAWN)
        if graphwin.isClosed(): raise GraphicsError("Can't draw to closed window")
        self.canvas = graphwin
        self.id = self._draw(graphwin, self.config)
        graphwin.addItem(self)
        if graphwin.autoflush:
            _root.update()
        return self


    def undraw(self):

        """Undraw the object (i.e. hide it). Returns silently if the
        object is not currently drawn."""

        if not self.canvas: return
        if not self.canvas.isClosed():
            self.canvas.delete(self.id)
            self.canvas.delItem(self)
            if self.canvas.autoflush:
                _root.update()
        self.canvas = None
        self.id = None


    def move(self, dx, dy):

        """move object dx units in x direction and dy units in y
        direction"""

        self._move(dx,dy)
        canvas = self.canvas
        if canvas and not canvas.isClosed():
            trans = canvas.trans
            if trans:
                x = dx/ trans.xscale
                y = -dy / trans.yscale
            else:
                x = dx
                y = dy
            self.canvas.move(self.id, x, y)
            if canvas.autoflush:
                _root.update()

    def _reconfig(self, option, setting):
        # Internal method for changing configuration of the object
        # Raises an error if the option does not exist in the config
        #    dictionary for this object
        if option not in self.config:
            raise GraphicsError(UNSUPPORTED_METHOD)
        options = self.config
        options[option] = setting
        if self.canvas and not self.canvas.isClosed():
            self.canvas.itemconfig(self.id, options)
            if self.canvas.autoflush:
                _root.update()


    def _draw(self, canvas, options):
        """draws appropriate figure on canvas with options provided
        Returns Tk id of item drawn"""
        pass # must override in subclass


    def _move(self, dx, dy):
        """updates internal state of object to move it dx,dy units"""
        pass # must override in subclass


class Point(GraphicsObject):
    def __init__(self, x, y):
        GraphicsObject.__init__(self, ["outline", "fill"])
        self.setFill = self.setOutline
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return "Point({}, {})".format(self.x, self.y)

    def _draw(self, canvas, options):
        x,y = canvas.toScreen(self.x,self.y)
        return canvas.create_rectangle(x,y,x+1,y+1,options)

    def _move(self, dx, dy):
        self.x = self.x + dx
        self.y = self.y + dy

    def clone(self):
        other = Point(self.x,self.y)
        other.config = self.config.copy()
        return other

    def equals(self, otherPoint):
       return (self.x == otherPoint.x) and (self.y == otherPoint.y)

    def getX(self): return self.x
    def getY(self): return self.y

class _BBox(GraphicsObject):
    # Internal base class for objects represented by bounding box
    # (opposite corners) Line segment is a degenerate case.

    def __init__(self, p1, p2, options=["outline","width","fill"]):
        GraphicsObject.__init__(self, options)
        self.p1 = p1.clone()
        self.p2 = p2.clone()

    def _move(self, dx, dy):
        self.p1.x = self.p1.x + dx
        self.p1.y = self.p1.y + dy
        self.p2.x = self.p2.x + dx
        self.p2.y = self.p2.y  + dy

    def getP1(self): return self.p1.clone()

    def getP2(self): return self.p2.clone()

    def getCenter(self):
        p1 = self.p1
        p2 = self.p2
        return Point((p1.x+p2.x)/2.0, (p1.y+p2.y)/2.0)


class Rectangle(_BBox):

    def __init__(self, p1, p2):
        _BBox.__init__(self, p1, p2)

    def __repr__(self):
        return "Rectangle({}, {})".format(str(self.p1), str(self.p2))

    def _draw(self, canvas, options):
        p1 = self.p1
        p2 = self.p2
        x1,y1 = canvas.toScreen(p1.x,p1.y)
        x2,y2 = canvas.toScreen(p2.x,p2.y)
        return canvas.create_rectangle(x1,y1,x2,y2,options)

    def clone(self):
        other = Rectangle(self.p1, self.p2)
        other.config = self.config.copy()
        return other


class Oval(_BBox):

    def __init__(self, p1, p2):
        _BBox.__init__(self, p1, p2)

    def __repr__(self):
        return "Oval({}, {})".format(str(self.p1), str(self.p2))


    def clone(self):
        other = Oval(self.p1, self.p2)
        other.config = self.config.copy()
        return other

    def _draw(self, canvas, options):
        p1 = self.p1
        p2 = self.p2
        x1,y1 = canvas.toScreen(p1.x,p1.y)
        x2,y2 = canvas.toScreen(p2.x,p2.y)
        return canvas.create_oval(x1,y1,x2,y2,options)

class Circle(Oval):

    def __init__(self, center, radius):
        p1 = Point(center.x-radius, center.y-radius)
        p2 = Point(center.x+radius, center.y+radius)
        Oval.__init__(self, p1, p2)
        self.radius = radius

    def __repr__(self):
        return "Circle({}, {})".format(str(self.getCenter()), str(self.radius))

    def clone(self):
        other = Circle(self.getCenter(), self.radius)
        other.config = self.config.copy()
        return other

    def getRadius(self):
        return self.radius


class Line(_BBox):

    def __init__(self, p1, p2,style='solid'):
        _BBox.__init__(self, p1, p2, ["arrow","fill","width"])
        self.setFill(DEFAULT_CONFIG['outline'])
        self.setOutline = self.setFill
        self.style = style

    def __repr__(self):
        return "Line({}, {})".format(str(self.p1), str(self.p2))

    def clone(self):
        other = Line(self.p1, self.p2)
        other.config = self.config.copy()
        return other

    def _draw(self, canvas, options):
        p1 = self.p1
        p2 = self.p2
        x1,y1 = canvas.toScreen(p1.x,p1.y)
        x2,y2 = canvas.toScreen(p2.x,p2.y)
        if self.style == 'dashed':
           return canvas.create_line(x1,y1,x2,y2,dash=(10,5), width = 2)
        elif self.style == 'dotted':
           return canvas.create_line(x1,y1,x2,y2,dash=(2,2), width = 2)
        return canvas.create_line(x1,y1,x2,y2,options)

    def setArrow(self, option):
        if not option in ["first","last","both","none"]:
            raise GraphicsError(BAD_OPTION)
        self._reconfig("arrow", option)


class Polygon(GraphicsObject):

    def __init__(self, *points):
        # if points passed as a list, extract it
        if len(points) == 1 and type(points[0]) == type([]):
            points = points[0]
        self.points = list(map(Point.clone, points))
        GraphicsObject.__init__(self, ["outline", "width", "fill"])

    def __repr__(self):
        return "Polygon"+str(tuple(p for p in self.points))

    def clone(self):
        other = Polygon(*self.points)
        other.config = self.config.copy()
        return other

    def getPoints(self):
        return list(map(Point.clone, self.points))

    def _move(self, dx, dy):
        for p in self.points:
            p.move(dx,dy)

    def _draw(self, canvas, options):
        args = [canvas]
        for p in self.points:
            x,y = canvas.toScreen(p.x,p.y)
            args.append(x)
            args.append(y)
        args.append(options)
        return DEGraphWin.create_polygon(*args)

class Text(GraphicsObject):

    def __init__(self, p, text):
        GraphicsObject.__init__(self, ["justify","fill","text","font"])
        self.setText(text)
        self.anchor = p.clone()
        self.setFill(DEFAULT_CONFIG['outline'])
        self.setOutline = self.setFill

    def __repr__(self):
        return "Text({}, '{}')".format(self.anchor, self.getText())

    def _draw(self, canvas, options):
        p = self.anchor
        x,y = canvas.toScreen(p.x,p.y)
        return canvas.create_text(x,y,options)

    def _move(self, dx, dy):
        self.anchor.move(dx,dy)

    def clone(self):
        other = Text(self.anchor, self.config['text'])
        other.config = self.config.copy()
        return other

    def setText(self,text):
        self._reconfig("text", text)

    def getText(self):
        return self.config["text"]

    def getAnchor(self):
        return self.anchor.clone()

    def setFace(self, face):
        if face in ['helvetica','arial','courier','times roman','verdana','comic sans']:
            f,s,b = self.config['font']
            self._reconfig("font",(face,s,b))
        else:
            raise GraphicsError(BAD_OPTION)

    def setSize(self, size):
        if 5 <= size <= 36:
            f,s,b = self.config['font']
            self._reconfig("font", (f,size,b))
        else:
            raise GraphicsError(BAD_OPTION)

    def setStyle(self, style):
        if style in ['bold','normal','italic', 'bold italic']:
            f,s,b = self.config['font']
            self._reconfig("font", (f,s,style))
        else:
            raise GraphicsError(BAD_OPTION)

    def setTextColor(self, color):
        self.setFill(color)


class Entry(GraphicsObject):

    def __init__(self, p, width):
        GraphicsObject.__init__(self, [])
        self.anchor = p.clone()
        #print self.anchor
        self.width = width
        self.text = tk.StringVar(_root)
        self.text.set("")
        self.fill = "gray"
        self.color = "black"
        self.font = DEFAULT_CONFIG['font']
        self.entry = None

    def __repr__(self):
        return "Entry({}, {})".format(self.anchor, self.width)

    def _draw(self, canvas, options):
        p = self.anchor
        x,y = canvas.toScreen(p.x,p.y)
        frm = tk.Frame(canvas.master)
        self.entry = tk.Entry(frm,
                              width=self.width,
                              textvariable=self.text,
                              bg = self.fill,
                              fg = self.color,
                              font=self.font,
                              justify='center')
        self.entry.pack()
        #self.setFill(self.fill)
        self.entry.focus_set()
        return canvas.create_window(x,y,window=frm)

    def getText(self):
        return self.text.get()

    def _move(self, dx, dy):
        self.anchor.move(dx,dy)

    def getAnchor(self):
        return self.anchor.clone()

    def clone(self):
        other = Entry(self.anchor, self.width)
        other.config = self.config.copy()
        other.text = tk.StringVar()
        other.text.set(self.text.get())
        other.fill = self.fill
        return other

    def setText(self, t):
        self.text.set(t)

    def setFill(self, color):
        self.fill = color
        if self.entry:
            self.entry.config(bg=color)

    def _setFontComponent(self, which, value):
        font = list(self.font)
        font[which] = value
        self.font = tuple(font)
        if self.entry:
            self.entry.config(font=self.font)


    def setFace(self, face):
        if face in ['helvetica','arial','courier','times roman']:
            self._setFontComponent(0, face)
        else:
            raise GraphicsError(BAD_OPTION)

    def setSize(self, size):
        if 5 <= size <= 36:
            self._setFontComponent(1,size)
        else:
            raise GraphicsError(BAD_OPTION)

    def setStyle(self, style):
        if style in ['bold','normal','italic', 'bold italic']:
            self._setFontComponent(2,style)
        else:
            raise GraphicsError(BAD_OPTION)

    def setTextColor(self, color):
        self.color=color
        if self.entry:
            self.entry.config(fg=color)

class Image(GraphicsObject):

    idCount = 0
    imageCache = {} # tk photoimages go here to avoid GC while drawn

    def __init__(self, p, *pixmap):
        GraphicsObject.__init__(self, [])
        self.anchor = p.clone()
        self.imageId = Image.idCount
        Image.idCount = Image.idCount + 1
        if len(pixmap) == 1: # file name provided
            self.img = tk.PhotoImage(file=pixmap[0], master=_root)
        else: # width and height provided
            width, height = pixmap
            self.img = tk.PhotoImage(master=_root, width=width, height=height)

    def __repr__(self):
        return "Image({}, {}, {})".format(self.anchor, self.getWidth(), self.getHeight())

    def _draw(self, canvas, options):
        p = self.anchor
        x,y = canvas.toScreen(p.x,p.y)
        self.imageCache[self.imageId] = self.img # save a reference
        return canvas.create_image(x,y,image=self.img)

    def _move(self, dx, dy):
        self.anchor.move(dx,dy)

    def undraw(self):
        try:
            del self.imageCache[self.imageId]  # allow gc of tk photoimage
        except KeyError:
            pass
        GraphicsObject.undraw(self)

    def getAnchor(self):
        return self.anchor.clone()

    def clone(self):
        other = Image(Point(0,0), 0, 0)
        other.img = self.img.copy()
        other.anchor = self.anchor.clone()
        other.config = self.config.copy()
        return other

    def getWidth(self):
        """Returns the width of the image in pixels"""
        return self.img.width()

    def getHeight(self):
        """Returns the height of the image in pixels"""
        return self.img.height()

    def getPixel(self, x, y):
        """Returns a list [r,g,b] with the RGB color values for pixel (x,y)
        r,g,b are in range(256)

        """

        value = self.img.get(x,y)
        if type(value) ==  type(0):
            return [value, value, value]
        elif type(value) == type((0,0,0)):
            return list(value)
        else:
            return list(map(int, value.split()))

    def setPixel(self, x, y, color):
        """Sets pixel (x,y) to the given color

        """
        self.img.put("{" + color +"}", (x, y))


    def save(self, filename):
        """Saves the pixmap image to filename.
        The format for the save image is determined from the filname extension.

        """

        path, name = os.path.split(filename)
        ext = name.split(".")[-1]
        self.img.write( filename, format=ext)

class Button:

    '''A button is a labeled rectangle in a window.
    It is activated/deactivated with the activate()/deactivate()
    methods. The clicked(point) method returns true if the
    button is active and point is inside it.'''

    # define the button constructor
    def __init__(self, win, center, width, height,
                 edgeWidth = 2, edgeColor = 'black',
                 text = 'button text', fontSize = 12, fontFace = 'helvetica',
                 backcolor = 'lightgray', textcolor = 'black'):

        w,h = width/2.0, height/2.0
        x,y = center.getX(), center.getY()

        self.xmax, self.xmin = x+w, x-w
        self.ymax, self.ymin = y+h, y-h

        # points defining opposing corners of button
        p1 = Point(self.xmin,self.ymin)
        p2 = Point(self.xmax, self.ymax)

        # define the button rectangle
        self.backcolor = backcolor
        self.rect = Rectangle(p1, p2)
        self.rect.setFill(backcolor)
        self.edgeWidth = edgeWidth
        self.edgeColor = edgeColor
        self.rect.setOutline(self.edgeColor)
        self.rect.setWidth(self.edgeWidth)

        # define the button caption
        self.forecolor = textcolor
        self.caption = Text(center, text)
        self.caption.setSize(fontSize)
        self.caption.setFace(fontFace)
        self.caption.setFill(self.forecolor)

        # draw the button
        self.rect.draw(win)
        self.caption.draw(win)

        # button is created in deactivated state
        self.deactivate()

    def clicked(self, clickPoint):
        "Returns true if button is active and false otherwise"
        return (self.active and self.xmin <= clickPoint.getX() <= self.xmax and self.ymin <= clickPoint.getY() <= self.ymax)

    def getCaption(self):
        "Returns the caption of the button"
        return self.caption.getText()

    def setCaption(self, win, center, text):
        "Sets the caption of the button"
        self.caption.undraw()
        self.caption = Text(center, text)
        self.caption.draw(win)

    def setForeColor(self, newColor):
        "Sets the text color of the button caption"
        self.caption.setFill(newColor)

    def setBackColor(self, newColor):
        "Sets the background color to newColor"
        self.rect.setFill(newColor)

    def draw(self,win):
        self.rect.draw(win)
        self.caption.draw(win)

    def undraw(self):
        self.rect.undraw()
        self.caption.undraw()

    def activate(self):
        "Sets this button to 'active'. "
        self.caption.setFill(self.forecolor)
        self.rect.setWidth(self.edgeWidth)
        self.active = True

    def deactivate(self):
        "Sets this button to 'inactive'."
        self.caption.setFill('darkgrey')
        self.rect.setWidth(1)
        self.active = False


def color_rgb(r,g,b):
    """r,g,b are intensities of red, green, and blue in range(256)
    Returns color specifier string for the resulting color"""
    return "#%02x%02x%02x" % (r,g,b)

class DropDown(GraphicsObject):
    def __init__(self, p, width, choices=[]):
        GraphicsObject.__init__(self, [])
        self.anchor = p.clone()
        #print self.anchor
        self.width = width
        self.text = tk.StringVar(_root)
        self.text.set("")
        self.fill = "gray"
        self.color = "black"
        self.font = DEFAULT_CONFIG['font']
        self.choices = choices
        self.menu = None

    def __repr__(self):
        return "DropDown({}, {})".format(self.anchor, self.width)

    def _draw(self, canvas, options):
        p = self.anchor
        x,y = canvas.toScreen(p.x,p.y)
        frm = tk.Frame(canvas.master)
        self.text.set(self.choices[0])
        self.menu = tk.OptionMenu(frm, self.text, *self.choices)
        self.menu.config(width = self.width)
        self.menu.pack()
        #self.setFill(self.fill)
        self.menu.focus_set()
        return canvas.create_window(x,y,window=frm)

    def _setFontComponent(self, which, value):
        font = list(self.font)
        font[which] = value
        self.font = tuple(font)
        if self.menu:
            self.menu.config(font=self.font)

    def setFace(self, face):
        if face in ['helvetica','arial','courier','times roman']:
            self._setFontComponent(0, face)
        else:
            raise GraphicsError(BAD_OPTION)

    def setSize(self, size):
        if 5 <= size <= 36:
            self._setFontComponent(1,size)
        else:
            raise GraphicsError(BAD_OPTION)

    def setStyle(self, style):
        if style in ['bold','normal','italic', 'bold italic']:
            self._setFontComponent(2,style)
        else:
            raise GraphicsError(BAD_OPTION)

    def setFill(self, color):
        self.fill = color
        if self.menu:
            self.menu.config(bg=color)

    def getOption(self):
        return self.text.get()

    def _setFontComponent(self, which, value):
        font = list(self.font)
        font[which] = value
        self.font = tuple(font)
        if self.menu:
            self.menu.config(font=self.font)

    def setFace(self, face):
        if face in ['helvetica','arial','courier','times roman']:
            self._setFontComponent(0, face)
        else:
            raise GraphicsError(BAD_OPTION)

    def setSize(self, size):
        if 5 <= size <= 36:
            self._setFontComponent(1,size)
        else:
            raise GraphicsError(BAD_OPTION)

    def setStyle(self, style):
        if style in ['bold','normal','italic', 'bold italic']:
            self._setFontComponent(2,style)
        else:
            raise GraphicsError(BAD_OPTION)




def test():
    win = DEGraphWin()
    win.setCoords(0,0,10,10)
    t = Text(Point(5,5), "Centered Text")
    t.draw(win)
    p = Polygon(Point(1,1), Point(5,3), Point(2,7))
    p.draw(win)
    e = Entry(Point(5,6), 10)
    e.draw(win)
    win.getMouse()
    win.zoom("in")
    p.setFill("red")
    p.setOutline("blue")
    p.setWidth(2)
    s = ""
    for pt in p.getPoints():
        s = s + "(%0.1f,%0.1f) " % (pt.getX(), pt.getY())
    t.setText(e.getText())
    e.setFill("green")
    e.setText("Spam!")
    e.move(2,0)
    win.getMouse()
    p.move(2,3)
    s = ""
    for pt in p.getPoints():
        s = s + "(%0.1f,%0.1f) " % (pt.getX(), pt.getY())
    t.setText(s)
    win.getMouse()
    p.undraw()
    e.undraw()
    t.setStyle("bold")
    win.getMouse()
    t.setStyle("normal")
    win.getMouse()
    t.setStyle("italic")
    win.getMouse()
    t.setStyle("bold italic")
    win.getMouse()
    t.setSize(14)
    win.getMouse()
    t.setFace("arial")
    t.setSize(20)
    win.getMouse()
    win.close()

#MacOS fix 2
#tk.Toplevel(_root).destroy()

# MacOS fix 1
update()

if __name__ == "__main__":
    test()
