import sys

CLI_TARGET_PATH = "/DEVICEMANAGER/RACK1" 												   	# Static path
pkg_path_of_tftp_system = "/home/dcsg5/public_share/tftpboot/dell/Jignesh/G55_Latest/"

#G5_up_pkg_name		= "G5_ALL_FW_G5_03_65_03.tgz"
#G5_donw_pkg_name 	= "G5_ALL_FW_G5_03_65_02.tgz"
G55_up_pkg_name 	= "G5_ALL_FW_G55_03_75_02.tgz"
G55_down_pkg_name	= "G5_ALL_FW_G55_03_75_01.tgz"

# Provide firmware version
upgrade_package_fw_version 		= '03.75.02'
downgrade_package_fw_version	= '03.75.01'

scp_password = 'rahul2013'
scp_username = 'rdhobi'
scp_ip = '192.168.0.120'
tftp_path = '/dell/Jignesh/G55_Latest/'

# Provide exact package path
# SLS local system
#~ UPGRADE_PKG_PATH_G5   	= "tftp://" + scp_ip + tftp_path + G5_up_pkg_name      		# Modifiable    G5 package upgrade tftp path
#~ DOWNGRADE_PKG_PATH_G5 	= "tftp://" + scp_ip + tftp_path + G5_donw_pkg_name     	# Modifiable    G5 package downgrade tftp path
UPGRADE_PKG_PATH_G55   	= "tftp://" + scp_ip + tftp_path + G55_up_pkg_name  	    # Modifiable    G5.5 package upgrade tftp path
DOWNGRADE_PKG_PATH_G55 	= "tftp://" + scp_ip + tftp_path + G55_down_pkg_name  	    # Modifiable    G5.5 package downgrade tftp path
SSL_PKG_PATH 			= "tftp://" + scp_ip + "/release_test/SSL.tgz"                                 		# Modifiable    SSL certificate tftp path

#~ UPGRADE_PKG_PATH_G5   	= "tftp://192.168.0.120/dell/hardik/Remote/G5_ALL_FW_G5_ping_03_55_06.tgz"      	# Modifiable    G5 package upgrade tftp path
#~ DOWNGRADE_PKG_PATH_G5 	= "tftp://192.168.0.120/dell/hardik/Remote/G5_ALL_FW_G5_ping_03_55_05.tgz"      	# Modifiable    G5 package downgrade tftp path
#~ UPGRADE_PKG_PATH_G55   	= "tftp://192.168.0.120/dell/hardik/Remote/G5_ALL_FW_G55_ping_03_55_06.tgz"  	    # Modifiable    G5.5 package upgrade tftp path
#~ DOWNGRADE_PKG_PATH_G55 	= "tftp://192.168.0.120/dell/hardik/Remote/G5_ALL_FW_G55_ping_03_55_05.tgz"  	    # Modifiable    G5.5 package downgrade tftp path
#~ SSL_PKG_PATH 			= "tftp://192.168.0.120/release_test/SSL.tgz"                                 		# Modifiable    SSL certificate tftp path

# ADC remote system
#~ UPGRADE_PKG_PATH_G5   	= "tftp://192.168.1.1/G5/SLS_TEST/G5_ALL_FW_G5_03_55_05.tgz"      					# Modifiable    G5 package upgrade tftp path
#~ DOWNGRADE_PKG_PATH_G5 	= "tftp://192.168.1.1/G5/SLS_TEST/G5_ALL_FW_G5_03_55_04.tgz"      					# Modifiable    G5 package downgrade tftp path
#~ UPGRADE_PKG_PATH_G55   	= "tftp://192.168.1.1/G5/SLS_TEST/G5_ALL_FW_G55_03_55_05.tgz"  	    				# Modifiable    G5.5 package upgrade tftp path
#~ DOWNGRADE_PKG_PATH_G55 	= "tftp://192.168.1.1/G5/SLS_TEST/G5_ALL_FW_G55_03_55_04.tgz"  	    				# Modifiable    G5.5 package downgrade tftp path
#~ SSL_PKG_PATH 			= "tftp://192.168.1.1/G5/SLS_TEST/SSL.tgz"                                 			# Modifiable    SSL certificate tftp path

# 										Suggested loop count 	No. of times MC Reboot 	Suggestions to decide iterations				Iteration		Approx time taken 
#										as per importance		during each iteration																	for each iteration with minimal HWs
			
INFRASTRUCTURE_TEST_LOOP		= "01"	#         = "2"				0					Just check Infra of Block/MC/IM						1			2	min
PCKG_UP_DOWN_TEST_LOOP  		= "01"	#         = "5"				2					Verify all GET/PATCH/POST/DELETE requests			2			25	min	(1 block)
SSH_LOGIN_TIME_TEST_LOOP		= "10"	#         = "5"				0					Verify average login time							2			2	min
PPID_TEST_LOOP          		= "01"	#         = "1"				1					Verify PPID can be set or not						2			5	min
SLED_RESET_TEST_LOOP    		= "01"	#         = "5"				0					Verify Sled soft/hard reset							5			15	min	(3 sleds)
CLI_USERS_TEST_LOOP     		= "01"	#         = "3"				0					Login with diff default users						2			2	min
LLCDEBUG_TEST_LOOP      		= "01"	#         = "2"				0					Collect response of llcDebug commands				2			10	min
IDLED_TEST_LOOP         		= "01"	#         = "5"				0					Verify on LLCs/MCs									2			5	min	(1 block & 1 sled)
REDFISH_SERVICE_START_STOP_LOOP	= "01"	#		  = "2"				0					Verify service enable/disable						2			7	min
REDFISH_TEST_LOOP       		= "01"	#         = "2"				2					Verify all GET/PATCH/POST/DELETE requests			2			35	min	(1 block & 1 sled)
SSL_CERTIFICATE_TEST_LOOP		= "01"	#		  = "2"				1					Generate/Load/Verify SSL certy						2			10	min
POWER_CAPPING_TEST_LOOP 		= "01"	#         = "3"				0					Verify power capping								3			15	min
POWER_GROUPING_TEST_LOOP		= "01"	#         = "3"				0					Verify power grouping								3			25	min	(1 block & 3 sled)
ACSB_START_STOP_LOOP    		= "01"	#         = "2"				1					Verify ON/OFF/LAST functionalities					2			10	min
RACK_START_STOP_LOOP    		= "01"	#         = "5"				2					Verify ON/OFF power operations of all targets		2			15	min	(1 block & 1 sled)
IDRAC_BIOS_CPLD_TEST_LOOP		= "01"	#		  = "3"				2					Verify sled/node FW versions			 			2			15	min	(1 block & 1 sled)
DSS_TEST_LOOP           		= "01"	#         = "2"				2					Verify DCS/DSS										2			15	min
BC_RESET_TEST_LOOP      		= "01"	#         = "3"				0					Verify PSU SEL event logs on BC reset				2			5	min	(1 block)
IMAGE_UPDATE_TEST_LOOP  		= "01"	#         = "1"				0					Verify individual image update						2			10	min	(1 block)
RACK_NUM_CHANGE_LOOP			= "01"
BC_DISAPPEAR_TEST_LOOP			= "01"
FILE_COMMAND_CHECK_LOOP			= "01"
