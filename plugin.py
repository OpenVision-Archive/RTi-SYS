from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from enigma import eTimer
from Components.Sources.List import List
import os
import Screens.InfoBar
from enigma import *
from Components.config import configfile, getConfigListEntry, ConfigEnableDisable, \
	ConfigYesNo, ConfigText, ConfigDateTime, ConfigClock, ConfigNumber, ConfigSelectionNumber, ConfigSelection, \
	config, ConfigSubsection, ConfigSubList, ConfigSubDict, ConfigIP, ConfigSlider, ConfigDirectory, ConfigInteger
from time import gmtime, strftime, localtime, mktime, time, sleep, mktime
from datetime import datetime, timedelta

config.plugins.RtiSYS = ConfigSubsection()
config.plugins.RtiSYS.FanMode = ConfigSelection(choices = {"0": _("Always ON"), "998": _("Always Off"), "1": _("Off in Standby"), "2": _("Cycle (5 Min ON ~ 5 Min Off)"), "999": _("Custom - Cycle")}, default="0")
config.plugins.RtiSYS.FanON = ConfigSelection(choices = {"6": _("1min"), "30": _("5min"), "60": _("10min"), "90": _("15min"), "120": _("20min"), "150": _("25min"), "180": _("30min")}, default="60")
config.plugins.RtiSYS.FanOff = ConfigSelection(choices = {"6": _("1min"), "30": _("5min"), "60": _("10min"), "90": _("15min"), "120": _("20min"), "150": _("25min"), "180": _("30min")}, default="60")
config.plugins.RtiSYS.CRClock = ConfigSlider(default = 357, increment = 1, limits = (300, 1600))
config.plugins.RtiSYS.CRVoltage = ConfigSelection(choices = {"0": _("5V"), "1": _("3.3V")}, default="0")
config.plugins.RtiSYS.ScanMode = ConfigSelection(choices = {"1": _("Source"), "2": _("Progressive"), "3": _("Interlaced_TopFieldFirst"), "4": _("Interlaced_BotFieldFirst")}, default="1")
config.plugins.RtiSYS.Interlaced = ConfigSelection(choices = {"1": _("DECODER_SPECIFICATION"), "2": _("MPEG2_PROGRESSIVE_SEQ"), "3": _("MPEG2_MENU_PROGRESSIVE")}, default="1")
#config.plugins.RtiSYS.DeinterlacingMode = ConfigSelection(choices = {"1": _("Discard_Bob"), "2": _("Weave"), "3": _("ConstantBlend"), "4": _("MotionAdaptative")}, default="1")
config.plugins.RtiSYS.DeinterlacingMode = ConfigSelection(choices = {"1": _("Discard_Bob"), "2": _("Weave"), "3": _("ConstantBlend")}, default="1")


class FanCtrlConfig(ConfigListScreen, Screen):
  
	skin = """
		<screen position="center,center" size="320,225" title="FANSet v.2.1" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="10,180" size="140,40" transparent="1" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="170,180" size="140,40" transparent="1" alphatest="on" />
		<widget source="key_red" render="Label" position="10,180" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget source="key_green" render="Label" position="170,180" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="config" position="10,10" size="300,80" scrollbarMode="showOnDemand" />
		<widget name="poraka" position="10,130" font="Regular;16" halign="center" size="300,50" />
		</screen>"""

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self.session = session
		self["poraka"] = Label(_("please setup fan control mode when the receiver is in Standby"))
		self.list = []
		self["actions"] = ActionMap(["ChannelSelectBaseActions","WizardActions", "DirectionActions","MenuActions","NumberActions","ColorActions"],
		{
			"save": self.SaveCfg, 
			"back": self.Izlaz, 
			"ok": self.SaveCfg,
			"green": self.SaveCfg,
			"red": self.Izlaz,
		}, -2)
		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("Save Conf"))
		ConfigListScreen.__init__(self, self.list)
		self.createSetup()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.createSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.createSetup()

	def createSetup(self):
		self.list = [ ]
		self.list.append(getConfigListEntry(_("FAN:"), config.plugins.RtiSYS.FanMode))
#
		if config.plugins.RtiSYS.FanMode.value == "999":
			self.list.append(getConfigListEntry(_("  ON:"), config.plugins.RtiSYS.FanON))
			self.list.append(getConfigListEntry(_("  Off:"), config.plugins.RtiSYS.FanOff))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def SaveCfg(self):
		if config.plugins.RtiSYS.FanOff.value == "": config.plugins.RtiSYS.FanOff.value = "*99#"
		config.plugins.RtiSYS.FanMode.save()
		config.plugins.RtiSYS.FanON.save()
		config.plugins.RtiSYS.FanOff.save()
		self.close()

	def Izlaz(self):
		self.close()

class CRClock(ConfigListScreen, Screen):
  
	skin = """
		<screen position="center,center" size="380,225" title="Card Reader Set v.1.0" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="10,180" size="140,40" transparent="1" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="230,180" size="140,40" transparent="1" alphatest="on" />
		<widget source="key_red" render="Label" position="10,180" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget source="key_green" render="Label" position="230,180" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="config" position="10,10" size="350,50" scrollbarMode="showOnDemand" />
		<widget name="poraka" position="10,130" font="Regular;16" halign="center" size="360,50" />
		</screen>"""

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self.session = session
		self["poraka"] = Label(_("Please use ChUp, ChDown, Left, Right buttons to SetUp Card Reader Clock & Voltage."))
		self.list = []
		self["actions"] = ActionMap(["ChannelSelectBaseActions","WizardActions", "DirectionActions","MenuActions","NumberActions","ColorActions"],
		{
			"save": self.SaveCfg, 
			"back": self.Izlaz, 
			"ok": self.SaveCfg,
			"green": self.SaveCfg,
			"red": self.Izlaz,
			"nextBouquet": self.keyUp,
			"prevBouquet": self.keyDwon,
		}, -2)
		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("Set Clock"))
		ConfigListScreen.__init__(self, self.list)
		self.createSetup()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.createSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.createSetup()

	def keyUp(self):
		config.plugins.RtiSYS.CRClock.value = config.plugins.RtiSYS.CRClock.value + 9
		ConfigListScreen.keyRight(self)
		self.createSetup()

	def keyDwon(self):
		config.plugins.RtiSYS.CRClock.value = config.plugins.RtiSYS.CRClock.value - 9
		ConfigListScreen.keyLeft(self)
		self.createSetup()

	def createSetup(self):
		self.list = [ ]
		clockstr = str(config.plugins.RtiSYS.CRClock.value) + "MHz"
		self.list.append(getConfigListEntry(_("CR Clock   : " + clockstr), config.plugins.RtiSYS.CRClock))
		self.list.append(getConfigListEntry(_("CR Voltage:"), config.plugins.RtiSYS.CRVoltage))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def SaveCfg(self):
		config.plugins.RtiSYS.CRClock.save()
		config.plugins.RtiSYS.CRVoltage.save()
		try:
			open("/proc/sc_clock", "w").write(str(config.plugins.RtiSYS.CRClock.value))
			open("/proc/sc_clock", "w").close()
		except Exception, e:
			print e
		try:
			open("/proc/sc_35v", "w").write(str(config.plugins.RtiSYS.CRVoltage.value))
			open("/proc/sc_35v", "w").close()
		except Exception, e:
			print e
		self.close()

	def Izlaz(self):
		self.close()

class AVpSet(ConfigListScreen, Screen):
  
	skin = """
		<screen position="center,center" size="760,395" title="A/V settings + v.1.0" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="10,350" size="140,40" transparent="1" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="610,350" size="140,40" transparent="1" alphatest="on" />
		<widget source="key_red" render="Label" position="10,350" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget source="key_green" render="Label" position="610,350" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="config" position="10,10" size="740,75" scrollbarMode="showOnDemand" />
		<widget name="poraka" position="10,150" font="Regular;16" halign="center" valign="center" foregroundColor="#ffff00" size="740,54" />
		<widget name="poraka1" position="10,210" font="Regular;16" halign="center" valign="center" foregroundColor="#ff2222" size="740,130" />
		</screen>"""

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self.session = session
		self["poraka"] = Label(_("."))
		self["poraka1"] = Label(_("."))
		self.list = []
		self["actions"] = ActionMap(["ChannelSelectBaseActions","WizardActions", "DirectionActions","MenuActions","NumberActions","ColorActions"],
		{
			"save": self.SaveCfg, 
			"back": self.Izlaz, 
			"ok": self.SaveCfg,
			"green": self.SaveCfg,
			"red": self.Izlaz,
			"down": self.keyUp,
			"up": self.keyDwon,
		}, -2)
		self["key_red"] = StaticText(_("Exit"))
		self["key_green"] = StaticText(_("Save"))
		ConfigListScreen.__init__(self, self.list)
		self.createSetup()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.createSetup()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.createSetup()

	def keyUp(self):
		self["config"].setCurrentIndex(self["config"].getCurrentIndex() + 1)
		self.createSetup()

	def keyDwon(self):
		self["config"].setCurrentIndex(self["config"].getCurrentIndex() - 1)
		self.createSetup()

	def createSetup(self):
		expl = ""
		self.list = [ ]
		self.list.append(getConfigListEntry(_("Scan Mode   : "), config.plugins.RtiSYS.ScanMode))
		self.list.append(getConfigListEntry(_("Interlaced Algo:"), config.plugins.RtiSYS.Interlaced))
		self.list.append(getConfigListEntry(_("Deinterlacing Mode:"), config.plugins.RtiSYS.DeinterlacingMode))
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		ind = self["config"].getCurrentIndex()
		if ind == 0 :
			self["poraka"].setText("The set property allows an application to force the decoder to mark the pictures in a certain way, including forcing progressive, and forcing interlaced bottom first or top first.")
			el = str(config.plugins.RtiSYS.ScanMode.value)
			if el == "1": expl = "EMhwlibScanMode_Source  Use the information given by the video decoder (default)."
			if el == "2": expl = "EMhwlibScanMode_Progressive  Forces the input to be progressive."
			if el == "3": expl = "EMhwlibScanMode_Interlaced_TopFieldFirst  Forces the input to be interlaced top field first."
			if el == "4": expl = "EMhwlibScanMode_Interlaced_BotFieldFirst  Forces the input to be interlaced bottom field first."
		elif ind == 1 :
			self["poraka"].setText("The set property allows an application to force a preferred interlace or progressive algorithm in case of unsure output format (usually stream).")
			el = str(config.plugins.RtiSYS.Interlaced.value)
			if el == "1": expl = "INTERLACED_PROGRESSIVE_ALGORITHM_USING_DECODER_SPECIFICATION  Use the decoder defined method (default)."
			if el == "2": expl = "INTERLACED_PROGRESSIVE_ALGORITHM_USING_MPEG2_PROGRESSIVE_SEQ  When the extended sequence header is defined as progressive and the picture header says otherwise, force the sequence to be progressive."
			if el == "3": expl = "INTERLACED_PROGRESSIVE_ALGORITHM_USING_MPEG2_MENU_PROGRESSIVE  When playing a DVD menu stream, this flags forces the decoder to make decoded pictures progressive to make displayed images stable. Only valid for MPEG-2 streams."
		elif ind == 2 :
			self["poraka"].setText("The set property allows an application to select the scaler's deinterlacing mode. Deinterlacing is used only when the scaler's input pictures are interlaced. If the scaler is set to deinterlacing but the input is progressive, then the scaler will not use any deinterlacing.")
			el = str(config.plugins.RtiSYS.DeinterlacingMode.value)
			if el == "1": expl = "No deinterlacing is used. At each instance, only one field is taken from the source to generate the output picture. This can result in half the vertical resolution on the display."
			if el == "2": expl = "Weave deinterlacing is used. This is the opposite of Bob deinterlacing where the complete input frame is used each time. There is no problem with half resolution, but in the case of motion between the two fields, the result is very bad."
			if el == "3": expl = "This is a slightly different form of EMhwlibDeinterlacingMode_Weave where a weight is applied on each field in order to diminish the motion's artifacts."
			if el == "4": expl = "Both Weave and Bob deinterlacing are used. Two scalers are used, one to compute the movement between field N-1 and N+1, and the other to generate a Weave N frame from field N-1 and field N+1. The other scaler applies a Bob algorithm on field N to generate the frame N. Finally, the two frames are mixed, with an alpha modulated by the movement detection. In the areas where no motion or little motion is detected, the Weave frame N is used, but in case of motion the Bob frame is used. Finally, the alpha can be also statically modified (on top of movement detection) with two weight factors to increase the Weave or Bob weight in the final frame."
		self["poraka1"].setText(expl)
		self.ActCfg()

	def ActCfg(self):
		try:
			open("/proc/input_scan_mode", "w").write(str(config.plugins.RtiSYS.ScanMode.value))
			open("/proc/input_scan_mode", "w").close()
		except Exception, e:
			print e
		try:
			open("/proc/interlaced_algo", "w").write(str(config.plugins.RtiSYS.Interlaced.value))
			open("/proc/interlaced_algo", "w").close()
		except Exception, e:
			print e
		try:
			open("/proc/deinterlace_mode", "w").write(str(config.plugins.RtiSYS.DeinterlacingMode.value))
			open("/proc/deinterlace_mode", "w").close()
		except Exception, e:
			print e

	def SaveCfg(self):
		config.plugins.RtiSYS.ScanMode.save()
		config.plugins.RtiSYS.Interlaced.save()
		config.plugins.RtiSYS.DeinterlacingMode.save()
		self.ActCfg()
		self.close()

	def Izlaz(self):
		self.close()

class LoopSyncMain(ConfigListScreen, Screen):
	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self.session = session
		self.gotSession()

	def gotSession(self):
		self.FanState = 0
		self.FOnTest = 0
		self.FOffTest = 0
		self.testno = 60
		self.testRTCSet = 0
		self.rstate = 1
		self.recf = 0
		self.ledstatus = 1
		self.FANtimeTimer = eTimer()
		self.LEDtimeTimer = eTimer()
		self.RtimeTimer = eTimer()
		self.RtiminimeTimer = eTimer()
		self.AVptimeTimer = eTimer()
		f = open("/proc/stb/info/model",'r')
		hw_type = f.readline().strip()
		f.close()
		if hw_type in ("me", "minime"):
			self.LEDtimeTimer.callback.append(self.updateLED)
			if hw_type == "minime":
				self.RtiminimeTimer.callback.append(self.updateCR)
		elif hw_type in ('elite', 'premium', 'premium+', 'ultra'):
			self.LEDtimeTimer.callback.append(self.updateLEDHD)
		if hw_type in ('ultra', 'premium+'):
			self.FANtimeTimer.callback.append(self.updateFAN)
		self.RtimeTimer.callback.append(self.updateRT)
		self.AVptimeTimer.callback.append(self.updateAVp)
		self.LEDtimeTimer.start(12000, True)
		self.RtimeTimer.start(12000, True)
		self.FANtimeTimer.start(12000, True)
		self.RtiminimeTimer.start(12000, True)
		self.AVptimeTimer.start(12000, True)

	def updateAVp(self):
		try:
			strScan_mode = str(config.plugins.RtiSYS.ScanMode.value)
			open("/proc/input_scan_mode", "w").write(strScan_mode)
			open("/proc/input_scan_mode", "w").close()
		except Exception, e:
			print e
		try:
			strInterlaced_algo = str(config.plugins.RtiSYS.Interlaced.value)
			open("/proc/interlaced_algo", "w").write(strInterlaced_algo)
			open("/proc/interlaced_algo", "w").close()
		except Exception, e:
			print e
		try:
			strDeinterlace_mode = str(config.plugins.RtiSYS.DeinterlacingMode.value)
			open("/proc/deinterlace_mode", "w").write(strDeinterlace_mode)
			open("/proc/deinterlace_mode", "w").close()
		except Exception, e:
			print e

	def updateFAN(self):
		oInd = config.plugins.RtiSYS.FanMode.value
		if oInd == "998" and self.FanState == 0:
			self.FanState = 1
			try:
				open("/proc/fan", "w").write("0")
				open("/proc/fan", "w").close()
			except OSError:
				print " ==>> Fan turned Off - failed."
		if oInd == "999":
			self.FanON = config.plugins.RtiSYS.FanON.value
			self.FanOff = config.plugins.RtiSYS.FanOff.value
		else:
			self.FanON = "5"
			self.FanOff = "5"
		if Screens.Standby.inStandby and oInd <> "0":
			if (oInd == "1" or oInd == "998") and self.FanState == 0:
				self.FanState = 1
				try:
					open("/proc/fan", "w").write("0")
					open("/proc/fan", "w").close()
				except OSError:
					print " ==>> Fan turned Off - failed."
			elif oInd <> "0" and oInd <> "1" and oInd <> "998":
				if self.FanState == 0:
					self.FOnTest += 1
					if self.FOnTest >= int(self.FanON):
						self.FOnTest = 0
						self.FanState = 1
						try:
							open("/proc/fan", "w").write("0")
							open("/proc/fan", "w").close()
						except OSError:
							print " ==>> Fan turned Off - failed."
				else:
					self.FOffTest += 1
					if self.FOffTest >= int(self.FanOff):
						self.FOffTest = 0
						self.FanState = 0
						try:
							open("/proc/fan", "w").write("1")
							open("/proc/fan", "w").close()
						except OSError:
							print " ==>> Fan turned On - failed."
		else:
			if oInd <> "998" and self.FanState == 1:
				try:
					open("/proc/fan", "w").write("1")
					open("/proc/fan", "w").close()
				except OSError:
					print " ==>> Fan turned On - failed."
				self.FanState = 0
			self.FOnTest = int(self.FanON)
			self.FOffTest = 0
		self.FANtimeTimer.start(10000, True)

	def updateCR(self):
		try:
			strCRClock = str(config.plugins.RtiSYS.CRClock.value)
			open("/proc/sc_clock", "w").write(strCRClock)
			open("/proc/sc_clock", "w").close()
		except Exception, e:
			print e
		try:
			strCRVoltage = str(config.plugins.RtiSYS.CRVoltage.value)
			open("/proc/sc_35v", "w").write(str(config.plugins.RtiSYS.CRVoltage.value))
			open("/proc/sc_35v", "w").close()
		except Exception, e:
			print e
		return

	def updateRT(self):
		f = open("/proc/stb/info/model",'r')
		hw_type = f.readline().strip()
		f.close()
		godina = int(datetime.utcnow().timetuple() [0])
		if self.testRTCSet <> 0 : 
			return
		if godina >= 2012 : 
			return
		else:
			if self.testno >= 60:
				self.testno = 0
				self.SetTime()
			else:
				self.testno += 1
			self.RtimeTimer.start(10000, True)

	def SetTime(self):
		f = open("/proc/stb/info/model",'r')
		hw_type = f.readline().strip()
		f.close()
		TBefore = mktime(datetime.utcnow().timetuple())
		cmd = str("ntpdate 0.debian.pool.ntp.org")
		if hw_type in ('elite', 'premium', 'premium+', 'ultra'): return
		TAfter = mktime(datetime.utcnow().timetuple())
		self.testRTCSet = 1
		deviation = abs(TAfter - TBefore)
		if deviation <= 60: return
		UTCTim = datetime.utcnow().timetuple()
		godina = '0000' + str(UTCTim [0])
		godina = godina [len(godina) - 4:]
		mesec = '00' + str(UTCTim [1])
		mesec = mesec [len(mesec) - 2:]
		den = '00' + str(UTCTim [2])
		den = den [len(den) - 2:]
		saat = '00' + str(UTCTim [3])
		saat = saat [len(saat) - 2:]
		minuti = '00' + str(UTCTim [4])
		minuti = minuti [len(minuti) - 2:]
		sekundi = '00' + str(UTCTim [5])
		sekundi = sekundi [len(sekundi) - 2:]
		TimeString = godina + mesec + den + saat + minuti + sekundi
		TimeZoneS = config.timezone.val.value
		ipos1 = TimeZoneS.find("(GMT")
		ipos2 = TimeZoneS.find(")")
		tmp = TimeZoneS[ipos1+4:ipos2]
		if len(tmp) == 0 : tmp = "+00"
		tzpredznak = tmp[:1]
		tzvalue = str(int(tmp[1:3]))
		TimeString = TimeString + tzpredznak + tzvalue
		cmd = 'echo "' + str(TimeString) + '" > /proc/settime'
		os.system(cmd)

	def updateLEDHD(self):
		try:
			line = len(self.session.nav.getRecordings())
			if line == 1:
				try:
					os.system('echo "4" > /proc/led')
				except:
					pass
			elif line == 0:
				try:
					os.system('echo "3" > /proc/led')
				except:
					pass
		except:
			try:
				os.system('echo "3" > /proc/led')
			except:
				pass
		if self.recf == 0:
			self.recf = 1
		else:
			self.recf = 0
			try:
				os.system('echo "3" > /proc/led')
			except:
				pass
		self.LEDtimeTimer.start(1000, True)

	def updateLED(self):
		try:
			line = len(self.session.nav.getRecordings())
			if line == 1:
				if self.recf == 0:
					try:
						f = open("/proc/led", "r")
						self.ledstatus = int(f.readline(), 16)
					except:
						self.ledstatus = 1
				self.recf = 1
				self.rstate += 1
				if self.rstate > 2: self.rstate = 1
				try:
					os.system('echo "' + str(self.rstate) + '" > /proc/led')
				except:
					pass
			else:
				if self.recf == 1:
					try:
						os.system('echo "' + str(self.ledstatus) + '" > /proc/led')
					except:
						pass
					self.recf = 0
		except:
			pass

		self.LEDtimeTimer.start(1000, True)

def FanCtrlMain(session, **kwargs):
	session.open(FanCtrlConfig)

def CRClockMain(session, **kwargs):
	session.open(CRClock)

def AVpSetMain(session, **kwargs):
	session.open(AVpSet)

def startSetup(menuid):
	if menuid != "system":
		return [ ]
	return [(_("[Fan Set]") , FanCtrlMain, " FanCtrlSetupMain_setup", 9)]

def startSetup1(menuid):
	if menuid != "system":
		return [ ]
	return [(_("[Card Reader Set]") , CRClockMain, " CRClock_setup", 9)]

def startSetup2(menuid):
	if menuid != "system":
		return [ ]
	return [(_("[A/V settings +]") , AVpSetMain, " AVp_setup", 9)]

def sessionstart(session, **kwargs):
	session.open(LoopSyncMain)


def Plugins(**kwargs):
	f = open("/proc/stb/info/model",'r')
	hw_type = f.readline().strip()
	f.close()
	if hw_type in ('ultra', 'premium+'):
		return [
			PluginDescriptor(name="FanCtrl", description="FAN Controll", where = PluginDescriptor.WHERE_MENU, fnc=startSetup),
			PluginDescriptor(name="AVp_setup", description="scan mode & interlaced algo", where = PluginDescriptor.WHERE_MENU, fnc=startSetup2),
			PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart)
			]
	elif hw_type == 'minime':
		return [
			PluginDescriptor(name="CRClock_setup", description="CR set freq", where = PluginDescriptor.WHERE_MENU, fnc=startSetup1),
			PluginDescriptor(name="AVp_setup", description="scan mode & interlaced algo", where = PluginDescriptor.WHERE_MENU, fnc=startSetup2),
			PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart)
			]
	else:
		return [
			PluginDescriptor(name="AVp_setup", description="scan mode & interlaced algo", where = PluginDescriptor.WHERE_MENU, fnc=startSetup2),
			PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart)
			]
