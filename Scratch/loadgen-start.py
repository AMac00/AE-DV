from pymongo import MongoClient

'''   This script build the collection needed to run the LoadGen script within the Agent emulator
        there is local AE cron job that looks ever minute and runs a python script and see if we should be sending calls
        1 is yes. 0 is no for status.
'''

## this connects to the local AE mongoDB and enables the record used by the cron job
db_client = MongoClient('127.0.0.1', 27017)
db = db_client['aedb']
col = db['loadgen']

# Drop the collection
#col.drop()

# 0 is off , 1 is running

insert = {
'loadgen_id': 0,
'status': 1,
'cpm': 8,
'clid': '4155551212',
'dn': '5550011020009500',
'context': 'testcase',
}




#calls = col.find_one({'loadgen_id': 0}, {"__id": 0})

if col.count_documents({'loadgen_id': 0}) == 0:
    print("didn't find any records..lets add one")
    print("{0}".format(col.insert_one(insert)))
else:
    col.update_one({'loadgen_id': 0},{"$set": insert})