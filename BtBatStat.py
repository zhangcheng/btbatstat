import subprocess,re,time,sys,webbrowser,urllib2,decimal,threading
from Foundation import NSDate,NSObject,NSTimer,NSRunLoop,NSDefaultRunLoopMode
from AppKit import NSImage,NSStatusBar,NSMenuItem,NSApplication,NSMenu,NSVariableStatusItemLength,NSRunAlertPanel
from PyObjCTools import AppHelper
from optparse import OptionParser

if len(sys.argv) > 1 and sys.argv[1][:4] == '-psn':
  del sys.argv[1]

VERSION = '0.8'

AboutText = """Writen by: Joris Vandalon
Code License: New BSD License

This software will always be free of charge.
Donation can be done via the website and will be much appreciated.
"""

updateText = """There is a new version of BtBatStat Available.
"""

debug = None
parser = OptionParser()
parser.add_option("-d", action="store_true", dest="debug")
(options, args)= parser.parse_args()

if options.debug is True:
  debug = 1

start_time = NSDate.date()

def versionCheck():
    try:
	LATEST = urllib2.urlopen("http://btbatstat.vandalon.org/VERSION", None, 1).read().strip()
    except:
	return 0
    if LATEST and decimal.Decimal(LATEST) > decimal.Decimal(VERSION):
	return 1

#Check for new version
def checkForUpdates():
    if versionCheck():
	check = NSRunAlertPanel("BtBatStat 0.8", updateText , "Download Update", "Ignore for now", None )
	if check == 1:
	    webbrowser.open(self.updateUrl)

class Timer(NSObject):
  statusbar = None
  barItem = dict()
  noDevice = None
  appUrl = 'http://code.google.com/p/btbatstat/'
  updateUrl = 'http://code.google.com/p/btbatstat/downloads/list'


  # Load images
  noDeviceImage = NSImage.alloc().initByReferencingFile_('icons/no_device.png')
  barImage = dict(kb1 = NSImage.alloc().initByReferencingFile_('icons/kb.png'),
	kb2 = NSImage.alloc().initByReferencingFile_('icons/kb.png'),
	magicMouse = NSImage.alloc().initByReferencingFile_('icons/magic_mouse.png'),
	mightyMouse = NSImage.alloc().initByReferencingFile_('icons/mighty_mouse.png'),
	magicTrackpad = NSImage.alloc().initByReferencingFile_('icons/TrackpadIcon.png'))

  #Define menu items
  statusbar = NSStatusBar.systemStatusBar()
  menuAbout = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('About BtBatStat', 'about:', '')
  separator_menu_item = NSMenuItem.separatorItem()
  menuQuit = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Quit', 'terminate:', '')

  def about_(self, notification):
    if versionCheck():
	AboutTitle = "BtBatstat " + VERSION + " (Update Available!)"
        about = NSRunAlertPanel(AboutTitle, AboutText , "OK", "Visit Website", "Download Update" )
    else:
	AboutTitle = "BtBatstat " + VERSION
        about = NSRunAlertPanel(AboutTitle, AboutText , "OK", "Visit Website", None )
    if about == 0:
      webbrowser.open(self.appUrl)
    elif about == -1:
      webbrowser.open(self.updateUrl)
	
  def applicationDidFinishLaunching_(self, notification):
    #Create menu
    self.menu = NSMenu.alloc().init()

    # Get the timer going
    self.timer = NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(start_time, 10.0, self, 'tick:', None, True)
    NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer, NSDefaultRunLoopMode)
    self.timer.fire()

    self.menu.addItem_(self.menuAbout)
    self.menu.addItem_(self.separator_menu_item)
    self.menu.addItem_(self.menuQuit)

    #Check for updates
    checkForUpdates()

  def tick_(self, notification):
    if debug:
	start = time.time()

    devicesFound = 0

    
    deviceCmd = dict( kb1 = subprocess.Popen(["/usr/sbin/ioreg", "-rc", "AppleBluetoothHIDKeyboard"], stdout=subprocess.PIPE).communicate()[0],
	kb2 = subprocess.Popen(["/usr/sbin/ioreg", "-n", "IOAppleBluetoothHIDDriver"], stdout=subprocess.PIPE).communicate()[0],
	mightyMouse = subprocess.Popen(["/usr/sbin/ioreg", "-rc", "AppleBluetoothHIDMouse"], stdout=subprocess.PIPE).communicate()[0],
	magicMouse = subprocess.Popen(["/usr/sbin/ioreg", "-rc", "BNBMouseDevice"], stdout=subprocess.PIPE).communicate()[0],
	magicTrackpad = subprocess.Popen(["/usr/sbin/ioreg", "-rc", "BNBTrackpadDevice"], stdout=subprocess.PIPE).communicate()[0])

    for device,Output in deviceCmd.items():
	if Output:
	    Percentage = re.search('BatteryPercent" = (\d{1,2})', Output)
	    print Percentage
	    if Percentage:
	        print Percentage
		if debug:
		    print "Found " + device
		deviceFound += 1
		if not device in self.barItem:
		    self.barItem[device] = self.statusbar.statusItemWithLength_(NSVariableStatusItemLength)
		    self.barItem[device].setImage_(self.barImage[device])
		    self.barItem[device].setHighlightMode_(1)
		    self.barItem[device].setMenu_(self.menu)
		self.barItem[device].setTitle_(Percentage.group(1) + '%')
	    elif device in self.barItem:
	    	self.statusbar.removeStatusItem_(self.barItem[device])
		del self.barItem[device]
    
    if debug:
	print "Found", devicesFound, "Devices."

    if devicesFound == 0 and self.noDevice is None:
	if debug:
	    print "Did not found any Apple BT devices..."
	self.noDevice = self.statusbar.statusItemWithLength_(NSVariableStatusItemLength)
	self.noDevice.setImage_(self.noDeviceImage)
        self.noDevice.setHighlightMode_(1)
        menuNotice = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('BtBatStat: No devices found.', '', '')
        self.menu.addItem_(menuNotice)
        self.noDevice.setMenu_(self.menu)
        self.noDevice.setToolTip_('BtBatStat: No devices found.')
    elif devicesFound > 0 and self.noDevice is not None:
	self.statusbar.removeStatusItem_(self.noDevice)
	del self.noDevice

    if debug:
	end = time.time()
	print "Time elapsed = ", end - start, "seconds"

if __name__ == "__main__":
  app = NSApplication.sharedApplication()
  delegate = Timer.alloc().init()
  app.setDelegate_(delegate)
  AppHelper.runEventLoop()

