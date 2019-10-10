import sys, os,tarfile
import socket, datetime, time, shutil, re, errno, stat, traceback, subprocess
#import numpy as np
from variables import *
from os import listdir
#from run import *
#sys.path.append('../')
#import variables

fBC_BL_name = "BC_BL.bin"
fBC_OP_name = "BC_OP.bin"
fBC_SB_name = "BC_SB.bin"
fBC_FP_name = "BC_FP.bin"
fIM_BL_name = "IM_BL.bin"
fIM_OP_name = "IM_OP.bin"
fIM_SB_name = "IM_SB.bin"
 
dict_image_Names = [fBC_BL_name, fBC_OP_name, fBC_SB_name, fBC_FP_name, fIM_BL_name, fIM_OP_name, fIM_SB_name]
#up_pkg_list = {'G5_up_pkg_name':G5_up_pkg_name}
#down_pkg_list = {'G5_donw_pkg_name':G5_donw_pkg_name}
up_pkg_list = {'G55_up_pkg_name':G55_up_pkg_name}
down_pkg_list = {'G55_down_pkg_name':G55_down_pkg_name}

FAIL = 'FAIL'
PASS = 'PASS'
ip_of_mc = ''
fw_pkg_verification_log = ''
#################################################################################################################
def logging(my_string):
	global fw_pkg_verification_log,current_dir,subdir
	try:
		filepath = os.path.join(current_dir, subdir, str(ip_of_mc), fw_pkg_verification_log)
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
def create_log_folder(log_files, MC_IP):
	global fw_pkg_verification_log,current_dir,subdir
	try:
		current_dir = os.path.dirname(os.path.realpath(__file__))
		subdir = "./logs"

		if not os.path.exists(current_dir+"/"+subdir):
			os.mkdir(os.path.join(current_dir, subdir))

		if not os.path.exists(current_dir+"/"+subdir+"/"+str(MC_IP)):
			os.mkdir(os.path.join(current_dir, subdir,str(MC_IP)))

		fw_pkg_verification_log = log_files
		New_FW_pkg_verification_test_log = current_dir + "/" + subdir + "/" + str(MC_IP) + "/" + fw_pkg_verification_log
		old_fw_varification_log = New_FW_pkg_verification_test_log+"_old"

		if os.path.exists(old_fw_varification_log):
			os.remove(old_fw_varification_log)

		if os.path.exists(New_FW_pkg_verification_test_log):
			os.rename(New_FW_pkg_verification_test_log,old_fw_varification_log)

	except:
		for frame in traceback.extract_tb(sys.exc_info()[2]):
			fname,lineno,fn,text = frame
			print logging("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
		raise RuntimeError('create_log_folder failed')
	else:
		print logging("\ncreate %s successfully"%(New_FW_pkg_verification_test_log))
		#~ print logging logging("\ncreate ./logs/%s/%s successfully"%(MC_IP,log_files))
#################################################################################################################
def extract_tgz_file(fw_pkg_name):
	try:
		print ("Going to extract firmware package:%s"%fw_pkg_name)
		
		print logging("------------------------------------------------------------------")
		print logging("|File name in tgz pkg| fw type | fw version|    result           |")
		print logging("------------------------------------------------------------------")
		
		tar = tarfile.open(fw_pkg_name, "r:gz")
		tar.extractall()
		tar.close()
	except tarfile.ReadError:
		print logging("Exit on exception for tar file extraction!")
		return FAIL
#################################################################################################################
def verify_images(image_file_name,file_version):
	# validating input file to get fw
	try:
		#~ print ("verify_images image_file_name:%s"%image_file_name)
		file = open(image_file_name,"rb")
		file.seek(526,0)        #507-8
		IMAGE_FW_VER = file.read(8)
		file.seek(603,0)
		FILE_IMAGE_TYPE = file.read(5)
		file.close()
		
		if(IMAGE_FW_VER != file_version):
			#~ print (image_file_name + " : " + FILE_IMAGE_TYPE + " : " + IMAGE_FW_VER + " verification failed!")
			print logging("      " + image_file_name + "      : " + FILE_IMAGE_TYPE + "   : " + IMAGE_FW_VER + "  : verification failed!")
			return FAIL
		else:
			#~ print (image_file_name + " : " + FILE_IMAGE_TYPE + " : " + IMAGE_FW_VER + " verified!")
			print logging("      " + image_file_name + "      : " + FILE_IMAGE_TYPE + "   : " + IMAGE_FW_VER + "  : verified!")
			return PASS
			
	except IOError:
		print logging("Error: can\'t find" + fBC_BL_name + " or read data!")
		return FAIL
#################################################################################################################
def download_pkg_to_local_desktop():
	try:
		for key,val in up_pkg_list.items():
			cmd = "sshpass -p " + scp_password + " scp " + scp_username + "@" + scp_ip + ":" + pkg_path_of_tftp_system + val + " ./"
			print logging("\n***************************************************************************************************************************************")
			print logging("Copying %s from %s to current working directory."%(val, pkg_path_of_tftp_system))
			#~ print ("cmd = %s"%(cmd))
			os.system(cmd)
			#~ print key, "=>", val
		for key,val in down_pkg_list.items():
			cmd = "sshpass -p " + scp_password + " scp " + scp_username + "@" + scp_ip + ":" + pkg_path_of_tftp_system + val + " ./"
			print logging("\n***************************************************************************************************************************************")
			print logging("Copying %s from %s to current working directory."%(val, pkg_path_of_tftp_system))
			#~ print ("cmd = %s"%(cmd))
			#~ print ("***************************************************************************************************************************************")
			os.system(cmd)
			#~ print key, "=>", val
		return "PASS"
	except:
		for frame in traceback.extract_tb(sys.exc_info()[2]):
			fname,lineno,fn,text = frame
			print logging("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
			#~ print .logging("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
#################################################################################################################
def usage():
	#~ print("\nusage : python G5fw_version_verify.py <Input FW Version>")
	print logging("\nusage : python G5fw_version_verify.py <MC_IP>")
	sys.exit()
#################################################################################################################
def start_fw_verification(MC_IP):
	try:
		global ip_of_mc
		ip_of_mc = MC_IP
		timestr = time.strftime("%Y%m%d-%H%M%S")
		log_file_name = "FW_pkg_verification_test_" + timestr + ".log"
		create_log_folder(log_file_name,MC_IP)
		
		download_pkg_to_local_desktop()
		fail_count = 0
		result = FAIL
		for index in range(len(up_pkg_list)):
			print logging("\n***************************************************************************************************************************************")
			if int(index) == 0:
				extract_tgz_file(G5_up_pkg_name)
			elif int(index) == 1:
				extract_tgz_file(G55_up_pkg_name)
		
			for index in range(len(dict_image_Names)):
				result = verify_images(dict_image_Names[index],upgrade_package_fw_version)
				if result == FAIL:
					fail_count = fail_count + 1
		
		for index in range(len(down_pkg_list)):
			print logging("\n***************************************************************************************************************************************")
			if int(index) == 0:
				extract_tgz_file(G5_donw_pkg_name)
			elif int(index) == 1:
				extract_tgz_file(G55_down_pkg_name)
		
			for index in range(len(dict_image_Names)):
				result = verify_images(dict_image_Names[index],downgrade_package_fw_version)
				if result == FAIL:
					fail_count = fail_count + 1
		
		print logging("\n***************************************************************************************************************************************")
		print logging('Failure count of firmware version mismatch is : %s'%fail_count)
              
		print logging("Deleting copied packages and extracted files from current working directory.")
		test=os.listdir("./")
		for item in test:
			if item.endswith(".bin"):
				os.remove(item)
			elif item.endswith(".d7"):
				os.remove(item)
			elif item.endswith(".tgz"):
				os.remove(item)
		
		if int(fail_count) != int(0):
			retrun_to_main = 'FAIL'
			return FAIL
		else:
			retrun_to_main = 'PASS'
			return PASS
		
	except:
		for frame in traceback.extract_tb(sys.exc_info()[2]):
			fname,lineno,fn,text = frame
			print logging("Exception from %s line_no: %d fun_name: %s statement: %s " % (fname, lineno, fn, text))
#################################################################################################################
if __name__ == "__main__":
	#~ print('len(sys.argv):%d'%len(sys.argv))
	if len(sys.argv) != 2:
		usage()
	verification_result = start_fw_verification(sys.argv[1])
	#~ print('verification_result:%s'%verification_result)
