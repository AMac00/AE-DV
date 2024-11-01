# Agent Emulator DV Version #
Notes
* This version of the software provides pre-canned features for agent and phone functions


## Components ##
* Asterisk LoadGenerator
* Agent Emulator 

### Load Generator ###
#### Asterisk Box (X.X.X.X)-(Name) ####
#### Functions of test cases are stored in extension_cases.conf 
[testcase]
exten => lab,1,Answer
exten => lab,n,Wait(3)
exten => lab,n,SendDTMF(1)
exten => lab,n,Wait(2)
exten => lab,n,MusicOnHold(manolo_camp-morning_coffee,${RAND(240,480)})
exten => lab,n,Hangup()


[testcase_3min]
exten => lab,1,Answer
exten => lab,n,Wait(3)
exten => lab,n,MusicOnHold(manolo_camp-morning_coffee,${180})
exten => lab,n,Hangup()

[testcase_5min]
exten => lab,1,Answer
exten => lab,n,Wait(5)
exten => lab,n,MusicOnHold(manolo_camp-morning_coffee,${300})
exten => lab,n,Hangup()

then you use testcase1.call for variables.
[root@loadgen01 asterisk]# more testcase1.call 
Channel: SIP/lab/5122412550
CallerID: "Load Test" <4155551212>
Context: testcase
Extension: lab 

to execute  ./createLoadTest.sh
[root@loadgen01 asterisk]# more createLoadTest.sh 
if [ $1 -eq 0 ]

  then
    echo "enter the number of the testcase"
fi
if [ $2 -eq 0 ]
  then
    echo "enter the number of calls to create"
fi
echo $1
echo $2
for (( i=0 ; i < $2 ; i++ )) ; 
do cp testcase$1.call /var/spool/asterisk/outgoing/testcases$1-$i.call ; 
sleep .5
done



### Agent Emulator ###

