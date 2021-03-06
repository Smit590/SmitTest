
| *** Settings *** |
| Documentation  | This is the v1 test of G5/G5.5 FW release using telent protocol. |
| Library        | Infrastructure_Check.py |
| Library        | PPID_TEST.py |

| *** Variables *** |
| ${MC_IP}         | ${EMPTY} |
| ${USER_NAME}     | ${EMPTY} |
| ${PASSWORD}      | ${EMPTY} |
| ${INFRA}         | ${EMPTY} |
| ${output}        | ${EMPTY} |
| ${Loop}          | 1 |

| ${UPGRADE}       | upgrade  |
| ${DOWNGRADE}     | downgrade |
| ${UPGRADE_DOWNGRADE}     | upgrade_downgrade |
| ${RERUN_LOG}         | ${EMPTY} |

| *** Test Cases *** |

| Infrastructure_Test |
|	 | [Tags] | Infrastructure_Test |
|    | ${INFRA}=     | Infrastructure | ${MC_IP} | ${Loop} |  ${USER_NAME} | ${PASSWORD} |
|    | Run Keyword If | '${INFRA}' != 'G5'  and  '${INFRA}' != 'G5.5' | FAIL |
|    | Log | ${INFRA} |
|    | Set Global Variable | ${INFRA} |

| PPID_TEST |
|	 | [Tags] | PPID_TEST |
|    | ${output}=      | PPID SET Test | ${MC_IP} | ${Loop} | ${USER_NAME} | ${PASSWORD} |
|    | Run Keyword If  | '${output}' == 'FAIL' | FAIL |


| *** Keywords *** |

| Infrastructure |
|    | [Arguments] | ${arg_0} | ${arg_1} | ${arg_2} | ${arg_3} |
|    | ${iRet} =   | check_Infrastructure | ${arg_0} | ${arg_1} | ${arg_2} | ${arg_3} |
|    | [Return]    | ${iRet} |

| PPID SET Test |
|    | [Arguments] | ${arg_0} | ${arg1} | ${arg_2} | ${arg_3} |
|    | ${iRet} =   | SET_PPID_TEST  | ${arg_0} | ${arg1} | ${arg_2} | ${arg_3} |
|    | [Return]    | ${iRet} |



