import os, sys, time, shutil, re, subprocess
import socket, datetime, telnetlib, getopt, traceback

BC_IpAddress_map = []
Sled_Bit_map = []
BC_IPAddress = []
setup_log, current_dir, subdir = ['','','']

#################################################################################################################
class setup:
	def __init__(self):
		self.tn = None
		self.user = 'root'
		self.password = 'calvin'
		self.debug_mode = 'yes'
		timestr = time.strftime("%Y%m%d-%H%M%S")
		file_name = "Pre_setup_" + timestr + ".log"
		self.log_file = file_name
		self.HOST_IP = ''
		self.setup_mode = ''
#################################################################################################################
	def usage(self):
		print "usage : python PowerCapping_test.py"
		print "Common OPTIONS:"
		print "               -h,               --help               -- show Usage, Options"
		print "               -u <user>,        --user=<usernm>      -- username of MC"
		print "               -p <passwd>,      --password=<passwd>  -- password of username"
		print "               -r <rhost>,       --rhost=<rhost>      -- MC IP"
		print "               -d <yes/no>,      --debug=<yes/no>     -- Debug mode"
#################################################################################################################
	def main(self,argv):
		try:
			if len(argv) == 0:
				self.usage()
				sys.exit()
			opts, args = getopt.getopt(argv, "h:r:u:p:d:s:", ["help","rhost=","user=","password=","debug=","setup="])
		except getopt.GetoptError as err:
			print str(err)
			self.usage()
			sys.exit()

		for o, a in opts:
			if o in ("-h", "--help"):
				self.usage()
				sys.exit()
			elif o in ("-r", "--rhost"):
				self.HOST_IP = a
			elif o in ("-l", "--loop"):
				self.loop = a
			elif o in ("-u", "--user"):
				self.user = a
			elif o in ("-p", "--password"):
				self.password = a
			elif o in ("-s", "--setup"):
				self.setup_mode = a
			elif o in ("-f", "--file"):
				self.log_file = a
			elif o in ("-d", "--debug"):
				self.debug_mode = a
			else:
				print 'wrong opt'
				self.usage()
				sys.exit()

		if self.HOST_IP != '':
			ret = True if os.system("ping -c 3 " + self.HOST_IP + " > /dev/null") is 0 else False
			if ret == False:
				print " MC in not present "
				sys.exit()

			self.start()
#################################################################################################################
	def logging(self, my_string):
		global ACSB_log,current_dir,subdir
		try:
			filepath = os.path.join(current_dir, subdir, str(self.HOST_IP), ACSB_log)
			with open(filepath,'a+') as log_file:
				log_file.write(str(my_string))
				log_file.write("\n")
				log_file.close()
		except IOError as e:
			print "I/O error({0}): {1}".format(e.errno, e.strerror)
		except ValueError:
			print "Could not convert data to an string."
		except:
			print "Unexpected error:", sys.exc_info()[0]
			raise RuntimeError('logging init failed')
		return my_string
#################################################################################################################
	def create_log_folder(self,log_files):
		global setup_log,current_dir,subdir
		try:
			current_dir = os.path.dirname(os.path.realpath(__file__))
			subdir = "./logs"

			if not os.path.exists(current_dir+"/"+subdir):
				os.mkdir(os.path.join(current_dir, subdir))

			if not os.path.exists(current_dir+"/"+subdir+"/"+str(self.HOST_IP)):
				os.mkdir(os.path.join(current_dir, subdir,str(self.HOST_IP)))

			setup_log = log_files
			New_setup_log = current_dir + "/" + subdir + "/" + str(self.HOST_IP) + "/" + setup_log
			print self.logging ("New_setup_log:%s"%New_setup_log)
			old_setup_log = New_setup_log+"_old"

			if os.path.exists(old_setup_log):
				os.remove(old_setup_log)

			if os.path.exists(New_setup_log):
				os.rename(New_setup_log,old_setup_log)

		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
			raise RuntimeError('create_log_folder failed')
		else:
			print self.logging ("\ncreate %s successfully"%(New_setup_log))
			#~ print self.logging self.logging("\ncreate ./logs/%s/%s successfully"%(self.HOST_IP,log_files))
#################################################################################################################
	def login_to_MC(self):
		try:
			self.tn = telnetlib.Telnet(self.HOST_IP)

			self.tn.read_until("login: ")
			self.tn.write(self.user + "\n")

			self.tn.read_until("Password: ")
			self.tn.write(self.password + "\n")
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging ("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
			raise RuntimeError('login_to_MC_for_status failed')
#################################################################################################################
	def login_to_MC_for_status(self):
		try:
			self.status = telnetlib.Telnet(self.HOST_IP)

			self.status.read_until("login: ")
			self.status.write(self.user + "\n")

			self.status.read_until("Password: ")
			self.status.write(self.password + "\n")
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging ("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
			raise RuntimeError('login_to_MC_for_status failed')
#################################################################################################################
	def parse_response_property(self, tn_buf, property_name):
		upgrade_status = 'NO_UPDATE'
		try:
			tn_buf_ = str(tn_buf)
			for line in tn_buf_.splitlines():
				if str(property_name) in line:
					line = line.strip()
					upgrade_status = line.split(" ",2)[2]
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging ("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
			raise RuntimeError('parse_response_property failed')
		return upgrade_status
#################################################################################################################
	def get_Rack_PowerState(self):
		start_stop_status = 'NA'
		try:
			self.status.write("CLI\n")
			self.status.write("show -d properties=PowerState RACK1\n")
			self.status.write("exit\n")
			Response_buf = self.status.read_until('Exit the Session',120)
			start_stop_status = self.parse_response_property(Response_buf,'PowerState = ')
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging ("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
			raise RuntimeError('get_Rack_LastPowerChangeStatus failed')
		return start_stop_status
#################################################################################################################
	def do_required_changes(self):
		self.login_to_MC()
		try:

			self.tn.write("rm -rf /opt/dell/mc/conf/inventory.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /Password=/s/.*./#Password=calvin/ /opt/dell/mc/conf/manufacturing.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /BlocksToCap=/s/.*./BlocksToCap=\'\"1,2,3,4,5,6,7,8,9,10\"\'""/ /opt/dell/mc/conf/manufacturing.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /Block-1_CapPolicy/s/.*./Block-1_CapPolicy=\'\"8,170,1,80,10,1,0,1\"\'""/ /opt/dell/mc/conf/manufacturing.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /Block-2_CapPolicy/s/.*./Block-2_CapPolicy=\'\"8,170,1,80,10,1,0,2\"\'""/ /opt/dell/mc/conf/manufacturing.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /Block-3_CapPolicy/s/.*./Block-3_CapPolicy=\'\"8,170,1,80,10,1,0,3\"\'""/ /opt/dell/mc/conf/manufacturing.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /Block-4_CapPolicy/s/.*./Block-4_CapPolicy=\'\"8,170,1,80,10,1,0,4\"\'""/ /opt/dell/mc/conf/manufacturing.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /Block-5_CapPolicy/s/.*./Block-5_CapPolicy=\'\"8,170,1,80,10,1,0,5\"\'""/ /opt/dell/mc/conf/manufacturing.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /Block-6_CapPolicy/s/.*./Block-6_CapPolicy=\'\"8,170,1,80,10,1,0,6\"\'""/ /opt/dell/mc/conf/manufacturing.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /Block-7_CapPolicy/s/.*./Block-7_CapPolicy=\'\"8,170,1,80,10,1,0,7\"\'""/ /opt/dell/mc/conf/manufacturing.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /Block-8_CapPolicy/s/.*./Block-8_CapPolicy=\'\"8,170,1,80,10,1,0,8\"\'""/ /opt/dell/mc/conf/manufacturing.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /Block-9_CapPolicy/s/.*./Block-9_CapPolicy=\'\"8,170,1,80,10,1,0,9\"\'""/ /opt/dell/mc/conf/manufacturing.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /Block-10_CapPolicy/s/.*./Block-10_CapPolicy=\'\"8,170,1,80,10,1,0,10\"\'""/ /opt/dell/mc/conf/manufacturing.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /# PPID/s/.*./# MC_PPID/ /opt/dell/mc/conf/manufacturing.conf\n")
			time.sleep(2)
			
			self.tn.write("sed -i /MoreFunc=/s/.*./MoreFunc=NO/ /opt/dell/mc/conf/mc.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /PowerCappingThreshold=/s/.*./PowerCappingThreshold=2000/ /opt/dell/mc/conf/mc.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /PowerCappingEnableThreshold=/s/.*./PowerCappingEnableThreshold=200/ /opt/dell/mc/conf/mc.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /PowerCapping=/s/.*./PowerCapping=DISABLED/ /opt/dell/mc/conf/mc.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /Grouping=/s/.*./Grouping=DISABLE/ /opt/dell/mc/conf/mc.conf\n")
			time.sleep(2)

			self.tn.write("sed -i /InventoryBehavior=/s/.*./InventoryBehavior=DYNAMIC/ /opt/dell/mc/conf/mc.conf\n")
			time.sleep(2)
			
			self.tn.write("sed -i /LogLevel=/s/.*./LogLevel=DEBUG/ /opt/dell/mc/conf/mc.conf\n")
			time.sleep(2)
			
			#~ self.tn.write("rm -rf /opt/dell/mc/tftp_root/*.tar\n")
			#~ time.sleep(2)
			
			#~ self.tn.write("rm -rf /opt/dell/mc/tftp_root/*.d7\n")
			#~ time.sleep(2)
			
			#~ self.tn.write("rm -rf /opt/dell/mc/*_dump\n")
			#~ time.sleep(2)
			
			#~ self.tn.write("rm -rf /opt/dell/mc/*.gz\n")
			#~ time.sleep(2)
			
			#~ self.tn.write("rm -rf /opt/dell/mc/*Manager\n")
			#~ time.sleep(2)
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging ("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
		
#################################################################################################################
	def get_Total_Sleds(self):
		Count = 0
		try:
			self.status.write("CLI\n")
			self.status.write('show -d properties=PresenceState Rack1/Block*/Sled*\n')
			self.status.write("exit\n")
			Response_buf = self.tn.read_until('Exit the Session',120)
			print self.logging ("Response_buf: %s " % (Response_buf))
			self.status.write("exit\n")
			buf=self.status.read_all()

			print self.logging ("All Sleds:%s"%buf)
			for line in buf.splitlines():
				if 'PresenceState = ' in line:
					print self.logging ("Sled present:%s"%line)
					value = line.split()[-1]
					if (value == 'PRESENT'):
						value = line.split()[-1]
						Count += 1
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging ("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
			raise RuntimeError('get_Total_Sleds failed')
		return Count
#################################################################################################################
	def get_BC_IpAddress(self):
		try:
			self.tn.write("CLI\n")
			self.tn.write('show -d properties=IpAddress /DeviceManager/Rack1/Block*/BC\n')				#show ipaddress of present BCs.
			self.tn.write("exit\n")
			buf=self.tn.read_until('Exit the Session')
			print self.logging ("get BC IP:%s"%buf)
			for line in buf.splitlines():
				if 'IpAddress = ' in line:
					value = line.split()[-1]
					BC_IPAddress.append(value)
					value = value.split('.')[-1]
					print self.logging ("get BC IP value :%s"%value)
					if (value != "NA"):
						BC_IpAddress_map.append(value)
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging ("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
#################################################################################################################
	def get_sled_bitmap_per_block(self,block_num):
		global Sled_Bit_map
		try:
			self.status.write("CLI\n")
			self.status.write('show -d properties=SledNumbers Rack1/Block'+block_num+'/BC\n')
			self.status.write("exit\n")
			Response_buf = self.tn.read_until('Exit the Session',120)
			print self.logging ("Response_buf: %s " % (Response_buf))
			self.status.write("exit\n")
			buf=self.status.read_all()
			print self.logging ("bitmap per block :%s"%buf)
			for line in buf.splitlines():
				if 'SledNumbers = ' in line:
					value = line.split()[-1]
					print self.logging ("bitmap per block value :%s"%value)
					if (value != "NA"):
						Sled_Bit_map.append(value)
					else:
						Sled_Bit_map.append("NA")
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging ("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
#################################################################################################################
	def setProperty(self,cmd):
		try:
			self.login_to_MC()
			self.tn.write("CLI\n")
			time.sleep(1)
			self.tn.write("cd Rack1\n")
			time.sleep(1)
			self.tn.write(cmd)
			time.sleep(1)
			self.tn.write("exit\n")
			Response_buf = self.tn.read_until('Exit the Session',120)
			print self.logging ("Response_buf: %s " % (Response_buf))
			time.sleep(1)
			self.tn.write("exit\n")
			time.sleep(1)
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging ("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
#################################################################################################################
	def setUp_SledGrouping_Config(self):
		try:
			self.login_to_MC()
			
			self.tn.write("rm -rf /opt/dell/mc/conf/sledgrouping.conf\n")
			time.sleep(1)

			self.get_BC_IpAddress()
			NumberOfBC = BC_IpAddress_map.__len__()
			print self.logging ("NumberOfBC :%s"%NumberOfBC)
			for index in range(NumberOfBC):
				self.login_to_MC_for_status()
				self.get_sled_bitmap_per_block(str(BC_IpAddress_map[index]))
				sleds = Sled_Bit_map.__len__()
				print self.logging ("sled bit map :%s"%sleds)
			self.tn.write("exit\n")

			self.login_to_MC()
			flag = 0
			parentSledNumber = ""

			for index in range(NumberOfBC):
				sled_list = str(Sled_Bit_map[index]).split(",")
				print self.logging ("sled_list :%s"%sled_list)
				size = sled_list.__len__()
				for S in range(size):
					if sled_list[S] != 'NA' and sled_list[S] != 'N/A':
						if flag == 0:
							parentSledNumber = "Block%s:Sled%s"%(str(BC_IpAddress_map[index]),sled_list[S])
							flag=1
							print "parentSledNumber = %s"%(parentSledNumber)
							break

				if flag == 1:
					sled_list = str(Sled_Bit_map[index]).split(",")
					size = sled_list.__len__()
					count = 0
					for S in range(size):
						if count == 4:
							break;
						else:
							if sled_list[S] != 'NA' and sled_list[S] != 'N/A':
								cmd = "set Block%s/Sled%s ParentSled=%s\n"%(str(BC_IpAddress_map[index]),sled_list[S],parentSledNumber)
								print "cmd = %s"%(cmd)
								iret = self.setProperty(cmd)
								count=count+1
								flag=0
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging ("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
#################################################################################################################
	def blockPrint(self):
		sys.stdout = open(os.devnull, 'w')
#################################################################################################################
	def start(self):
		try:
			self.create_log_folder(self.log_file)
			debug = self.debug_mode.lower()
			if debug == "no":
				self.blockPrint()
			
			
			
			self.setup_mode = self.setup_mode.lower()
			if self.setup_mode == "yes":
				self.login_to_MC_for_status()
				isRackPowerON = self.get_Rack_PowerState()
				if isRackPowerON != "ON":
					self.status.write("CLI\n")
					self.status.write("start -f Rack1\n")
					print self.logging("\nRack is turned ON so wait for 360 secs so that all CLI targets updated with respective properties.")
					print self.logging("Current time :%s"%(time.ctime()))
					time.sleep(360);
				self.status.write("exit\n")
				Response_buf = self.status.read_until('Exit the Session',120)
				print self.logging ("Response_buf: %s " % (Response_buf))
				self.login_to_MC()
				self.tn.write("llcDebug set_debug_mode ENABLE\n")
				print self.logging ("\nBackup MC config files.\n")
				time.sleep(2)
				self.tn.write("exit\n")
				time.sleep(2)

				self.do_required_changes()
				
				self.login_to_MC_for_status()
				#~ totalSleds = self.get_Total_Sleds()
				#~ print self.logging ("totalSleds:%s"%totalSleds)
				#~ self.setUp_SledGrouping_Config()

				self.login_to_MC_for_status()
				self.status.write("reboot\n")
				print self.logging("\nMC is rebooted so script will take 360 sec sleep")
				print self.logging("Current time :%s"%(time.ctime()))
				time.sleep(360);
			else:
				self.login_to_MC()
				self.tn.write("llcDebug set_debug_mode DISABLE\n")
				print self.logging ("\nRevert back MC config files previoulsy made backup.\n")
				self.tn.write("reboot\n")
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging ("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
#################################################################################################################

if __name__ == "__main__":
    obj=setup()
    obj.main(sys.argv[1:])
