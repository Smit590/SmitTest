# -*- coding: utf-8 -*-
import commands,threading,argparse
import os, sys, time, shutil, re, errno, stat
import socket, datetime, telnetlib, getopt
import traceback, subprocess
from robot.libraries.BuiltIn import BuiltIn
from G5fw_version_verify import start_fw_verification

run_log = ''
ip_of_mc = ''
#######################################################################################################################################
class run_py:

	def __init__(self):
		global ip_of_mc
		self.MC_IP = ''
		self.exclude = ''
		self.include = ''
		self.user = 'root'
		self.password = 'calvin'
		timestr = time.strftime("%Y%m%d-%H%M%S")
		file_name = "Main_run_" + timestr + ".log"
		self.log_file = file_name
		self.setup_mode = ''
		self.rerun_log = 'NO'

#######################################################################################################################################
	def usage(self):
		print "usage : python run.py"
		print "Common OPTIONS:"
		print "               -h,               --help               -- show Usage, Options"
		print "               -u <user>,        --user=<usernm>      -- username of MC"
		print "               -p <passwd>,      --password=<passwd>  -- password of username"
		print "               -r <rhost>,       --rhost=<rhost>      -- MC IP"
		print "               -i <include>,     --Exclude=<include>  -- Includes test cases from [ TAG ]"
		print "               -e <exclude>,     --Include=<exclude>  -- Excludes test cases from [ TAG ]"

		print "\nNote  : --include and --exclude both should not be execute concurrently"
		print "[ TAG ] - Description\
									\n\t\tInfrastructure_Test     - To check whether all controllers present in Rack having same infrastructure i.e. G5 or G5.5.\
									\n\t\tPackage_Upgrade_Test    - To check successfully Package upgrade for G5 or G5.5 system.\
									\n\t\tCLI_Users_Test          - To check successfully login into MC with all default users of G5 and G5.5 using \"calvin\" password\
									\n\t\tLlcDebug_Command_Test   - To check successfully execute all llcdebug commands on system.\
									\n\t\tIdLed_ON/OFF_Test       - To check the IdLed status of all controllers including sleds present in Rack.\
									\n\t\tRedfish_Start_Stop_Test - To check successfully Start/Stop the Redfish service.\
									\n\t\tRedfish_APIs_Test       - To check successfully execute the all Redfish requests on MC.\
									\n\t\tSSL_certificate_Test    - To check successfully load SSL certificate on system and check whether it is valid or not.\
									\n\t\tPowerCapping_Test       - To check the PowerCapping status at node level.\
									\n\t\tPowerGrouping_Test      - To check successfully on/off sleds in PowerGrouping.\
									\n\t\tACSB_Start/Stop_Test    - To check successfully Start/Stop the AC Switch Box.\
									\n\t\tRack_Start/Stop_Test    - To check successfully Start/Stop the Rack.\
									\n\t\tDCS/DSS_Test            - To check successfully DellProductGroup functionality in DCS/DSS mode.\
									\n\t\tPackage_Downgrade_Test  - To check successfully Package downgrade for G5 or G5.5 system.\n"

#################################################################################################################
	def logging(self, my_string):
		global run_log,current_dir,subdir
		try:
			filepath = os.path.join(current_dir, subdir, str(self.MC_IP), run_log)
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
		global run_log,current_dir,subdir
		try:
			current_dir = os.path.dirname(os.path.realpath(__file__))
			subdir = "./logs"

			cmd = current_dir+"/"+subdir
			if not os.path.exists(current_dir+"/"+subdir):
				os.mkdir(os.path.join(current_dir, subdir))

			#~ print("current_dir :%s subdir:%s str(self.MC_IP):%s"%(current_dir,subdir,str(self.MC_IP)))
			
			if not os.path.exists(current_dir+"/"+subdir+"/"+str(self.MC_IP)):
				os.mkdir(os.path.join(current_dir, subdir,str(self.MC_IP)))

			run_log = log_files
			print("run_log:%s"%run_log)
			New_run_log = current_dir + "/" + subdir + "/" + str(self.MC_IP) + "/" + run_log
			print self.logging ("New_main_run_log:%s"%New_run_log)
			old_setup_log = New_run_log+"_old"

			if os.path.exists(old_setup_log):
				os.remove(old_setup_log)

			if os.path.exists(New_run_log):
				os.rename(New_run_log,old_setup_log)

		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
			raise RuntimeError('create_log_folder failed')
		else:
			print self.logging ("\ncreate %s successfully"%(New_run_log))
			#~ print self.logging self.logging("\ncreate ./logs/%s/%s successfully"%(self.MC_IP,log_files))
#################################################################################################################
	def CheckIsDir(self,directory):
	  try:
		return stat.S_ISDIR(os.stat(directory).st_mode)
	  except OSError, e:
		if e.errno == errno.ENOENT:
		  return False
		raise

#######################################################################################################################################
	def copy_report_directories(self,src,dest):
		try:
			if(os.path.exists(dest) == True):
				os.system("rm -rf " + dest)#~ shutil.rmtree(dest)
				print ("removing merged_reports")
			os.mkdir(dest)
			if "rerun" in src:
				for sub_d_name in os.listdir(src):
					os.mkdir(dest+"/"+sub_d_name)
					#~ print ("sub_d_name:%s"%sub_d_name)
					for f_name in os.listdir(src+"/"+sub_d_name):
						#~ print ("	f_name:%s"%f_name)
						os.system("cp " + src +"/"+sub_d_name+"/"+f_name + " " + dest +"/"+sub_d_name)
			else:	
				for f_name in os.listdir(src):
					os.system("cp " + src +"/"+ f_name + " " + dest +"/")
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
					
#######################################################################################################################################
	def recursive_copy_files(self, source_path, destination_path):
		try:
			for file_name in os.listdir(source_path):
				if file_name != "backup":
					if file_name == "merged" or file_name == "combined" or file_name == "rerun":
						sourse_dir = source_path+"/"+file_name
						merged_report = destination_path + "/" + file_name
						self.copy_report_directories(sourse_dir,merged_report)
					else:
						os.system("cp " + source_path+"/"+file_name + " " + destination_path+"/")
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
						
#######################################################################################################################################
	def verify_fw_package(self, ip_of_mc):
		try:
			fw_verification_result = 'FAIL'
			print self.logging("\n***************************************************** FW VERIFICATION START *************************************************************")
			fw_verification_result = start_fw_verification(ip_of_mc)
			print self.logging("fw_verification_result : %s"%fw_verification_result)
			print self.logging("\n****************************************************** FW VERIFICATION END **************************************************************")
			if str(fw_verification_result) == 'FAIL':
				print self.logging("PACKAGE VERIFICATON FAILED")
				#~ sys.exit() # for debugging
				return 'FAIL'
			else:
				print ("FW_PACKAGE_VERIFIED")
				return 'PASS'
				
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
		#~ sys.exit() # debug
#######################################################################################################################################
	def call_robot(self):
		buff = ''
		try:
			if self.MC_IP != '':
				count = 1	# retry for MC login
				rerun_count = 1	# retry for failure cases
				while (int(count) <= int(360)):
					ret = True if os.system("ping -c 3 " + str(self.MC_IP) + " > /dev/null") is 0 else False
					
					if ret == True:
						src_report = "report/" + str(self.MC_IP )
						if(os.path.exists(src_report) == True):
							dest_report = "report/" + self.MC_IP + "/backup"
							if(os.path.exists(dest_report) == True):
								os.system("rm -rf " + dest_report)#~ shutil.rmtree(dest_reportdest)
							os.mkdir(dest_report)
							#~ print ("dest_report:%s"%dest_report)
							self.recursive_copy_files(src_report, dest_report)
							os.system("rm -rf " + src_report+ "/rerun/*")
							os.system("rm -f " + src_report+ "/merged/*")
							os.system("rm -f " + src_report+ "/combined/*")
						
						src_log = "logs/" + str(self.MC_IP )
						if(os.path.exists(src_log) == True):
							dest_log = "logs/" + self.MC_IP + "/backup"
							if(os.path.exists(dest_log) == False):
								os.mkdir(dest_log)
							#~ print ("dest_log:%s"%dest_log)
							self.recursive_copy_files(src_log, dest_log)
							os.system("rm -f " + src_log+ "/*.log")
							os.system("rm -f " + src_log+ "/*.log_old")
							
						self.setup_mode = self.setup_mode.lower()
						if self.setup_mode == "yes":
							print self.logging("Test environment setup is start")
							setup_cmd = "python setup.py -r " + self.MC_IP + " -u " + self.user + " -p " + self.password + " -s YES"
							print self.logging("setup_cmd: %s"%setup_cmd)
							os.system(setup_cmd)
							print self.logging("Test environment setup is done!")
						
						if self.include != '':
							cmd = "robot --log Robot_include_Log.html --reporttitle Robot_include_Test_Report --logtitle Regression_include_Test_Log --report Robot_include_Test_Report -d "+ src_report + " " + "--include " + self.include  + " -v MC_IP:" + self.MC_IP + " -v USER_NAME:" + self.user + " -v PASSWORD:"+ self.password + " -v RERUN_LOG:" + self.rerun_log +" lib/MC_test.robot"
						elif self.exclude != '':
							cmd = "robot --log Robot_exclude_Log.html --reporttitle Robot_exclude_Test_Report --logtitle Regression_exclude_Test_Log --report Robot_exclude_Test_Report -d "+ src_report + " " + "--exclude " + self.exclude + " -v MC_IP:" + self.MC_IP + " -v USER_NAME:" + self.user + " -v PASSWORD:"+ self.password + " -v RERUN_LOG:" + self.rerun_log + " lib/MC_test.robot"
						else:
							cmd = "robot --log Robot_Log.html --reporttitle Robot_Test_Report --logtitle Regression_Test_Log --report Robot_Test_Report --output Original.xml -d " + src_report + " -v MC_IP:" + self.MC_IP + " -v USER_NAME:" + self.user + " -v PASSWORD:"+ self.password + " -v RERUN_LOG:" + self.rerun_log + " MC_test.robot"

						print self.logging("cmd: %s"%cmd)
						ret = os.system(cmd)
						
						if int(ret) != 0:
							while (1):
								if int(rerun_count) > int(3):
									break
								if int(rerun_count) == int(1):			# First time rerun only failed test cases based on Original.xml
									re_run_cmd = "robot --log Robot_Rerun_Log.html --reporttitle Robot_Rerun_Test_Report --logtitle Regression_Rerun_Test_Log --report Robot_Rerun_Test_Report -d " + src_report + "/rerun/" + str(rerun_count) + " --rerunfailed " + src_report + "/Original.xml --output Rerun.xml -v MC_IP:" + self.MC_IP + " -v USER_NAME:" + self.user + " -v PASSWORD:" + self.password + " -v RERUN_LOG:YES lib/MC_test.robot"
									print self.logging("First re_run_cmd: %s"%re_run_cmd)
								else:
									rerun_xml_path = rerun_count - 1	# Rerun again only failed test cases based on previous Rerun.xml
									re_run_cmd = "robot --log Robot_Rerun_Log.html --reporttitle Robot_Rerun_Test_Report --logtitle Regression_Rerun_Test_Log --report Robot_Rerun_Test_Report -d " + src_report + "/rerun/" + str(rerun_count) + " --rerunfailed " + src_report + "/rerun/" + str(rerun_xml_path) + "/Rerun.xml --output Rerun.xml -v MC_IP:" + self.MC_IP + " -v USER_NAME:" + self.user + " -v PASSWORD:" + self.password + " -v RERUN_LOG:YES lib/MC_test.robot"
									print self.logging("Second onwards re_run_cmd: %s"%re_run_cmd)
								rerun_ret = os.system(re_run_cmd)
								if int(rerun_ret) == 0:
									break;
								elif int(rerun_ret) == 64512:
									break
								else:
									#~ count = count + 1
									rerun_count = rerun_count + 1
							
							all_reports_str = ''
							for d_name in os.listdir(src_report+"/"+"rerun"):
								for f_name in os.listdir(src_report+"/rerun/"+d_name):
									if  f_name == "Rerun.xml":
										all_reports_str = all_reports_str+src_report+"/rerun/"+d_name+"/"+f_name+" "
									
							merge_cmd = "rebot --merge --name Merged --log Merged_Robot_Log.html --report Merged_Robot_Test_Report --output Merged.xml -d " + src_report + "/merged " + src_report + "/Original.xml " + all_reports_str
							print self.logging("merge_cmd: %s"%merge_cmd)
							ret = os.system(merge_cmd)
							combiled_cmd = "rebot --name Combined --log Combined_Robot_Log.html --report Combined_Robot_Test_Report --output Combined.xml -d " + src_report + "/combined " + src_report + "/Original.xml " + all_reports_str
							print self.logging("combiled_cmd: %s"%combiled_cmd)
							ret = os.system(combiled_cmd)
							break
						else:
							break
					else:
						print self.logging("Error: %s is can't be reached..!! Please check the host...!!"%self.MC_IP)
						print self.logging("Going to check ping again after 60 seconds..!!")
						count = count + 1
						time.sleep(60);
						
					self.setup_mode = self.setup_mode.lower()
					if self.setup_mode == "yes":
						print self.logging("Going to test environment revert-back")
						setup_cmd = "python setup.py -r " + self.MC_IP + " -u " + self.user + " -p " + self.password + " -s NO"
						print self.logging("setup_cmd: %s"%setup_cmd)
						os.system(setup_cmd)
						print self.logging("Test environment revert-back is done!")
		except:
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				print self.logging("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))

#######################################################################################################################################
	def main(self,argv):
		try:
			if len(argv) == 0:
				self.usage()
				sys.exit()
			opts, args = getopt.getopt(argv, "h:u:p:r:i:e:s:y:", ["help","rhost=","user=","password=","Include=","Exclude=","setup=", "rerun="])
		except getopt.GetoptError as err:
			print str(err)
			self.usage()
			sys.exit()
		
		for o, a in opts:
			if o in ("-h", "--help"):
				self.usage()
				sys.exit()
			elif o in ("-r", "--rhost"):
				self.MC_IP = a
			elif o in ("-u", "--user"):
				self.user = a
			elif o in ("-p", "--password"):
				self.password = a
			elif o in ("-s", "--setup"):
				self.setup_mode = a
			elif o in ("-y", "--rerun"):	# NO -Only rerun failed test if package update PASS
				self.rerun_log = a			# YES-Rerun failed test without checking package update PASS or FAIL
			else:
				print 'wrong opt'
				self.usage()
				sys.exit()
		
		if self.MC_IP != '':
			try:
				self.create_log_folder(self.log_file)
				verify_result = self.verify_fw_package(self.MC_IP)
				if verify_result == 'PASS':
					self.call_robot()
				else:
					print self.logging("Verify FW package and rerun again..!")
			except:
				for frame in traceback.extract_tb(sys.exc_info()[2]):
					fname,lineno,fn,text = frame
					print self.logging("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
				print "Exception occured"
		else:
			self.usage()
			sys.exit()
#######################################################################################################################################

if __name__ == "__main__":
	obj = run_py()
	obj.main(sys.argv[1:])
