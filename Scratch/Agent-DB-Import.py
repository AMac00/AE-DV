import pymongo



agentlist_full = [
["Suraj","Andrew","1005550070","sandrew","Emu!830r","sandrew@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Rodney","Iles","1005550071","riles","Emu!830r","riles@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Roshan","Randall","1005550072","rrandall","Emu!830r","rrandall@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Mccauley","Hancock","1005550073","mhancock","Emu!830r","mhancock@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Alan","Montes","1005550074","amontes","Emu!830r","amontes@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Montague","Wardle","1005550075","mwardle","Emu!830r","mwardle@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Margie","Blundell","1005550076","mblundell","Emu!830r","mblundell@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Gideon","Mckeown","1005550077","gmckeown","Emu!830r","gmckeown@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Jagoda","Appleton","1005550078","jappleton","Emu!830r","jappleton@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Shanai","Bass","1005550079","sbass","Emu!830r","sbass@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Aran","Stanton","1005550080","astanton","Emu!830r","astanton@dv.ccenterprisecloud.com","Membership","Tim Lopez"],
["Graeme","Dorsey","1005550081","gdorsey","Emu!830r","gdorsey@dv.ccenterprisecloud.com","Membership","Tim Lopez"],
["Malia","Chang","1005550082","mchang","Emu!830r","mchang@dv.ccenterprisecloud.com","Membership","Tim Lopez"],
["Brandi","Fuentes","1005550083","bfuentes","Emu!830r","bfuentes@dv.ccenterprisecloud.com","Membership","Tim Lopez"],
["Faith","Gill","1005550084","fgill","Emu!830r","fgill@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Markus","Neal","1005550085","mneal","Emu!830r","mneal@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Dominique","Wolfe","1005550086","dwolfe","Emu!830r","dwolfe@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Jada","Harwood","1005550087","jharwood","Emu!830r","jharwood@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Tiana","Manning","1005550088","tmanning","Emu!830r","tmanning@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Zahara","Ferry","1005550089","zferry","Emu!830r","zferry@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Aya ","Mccabe","1005550090","amccabe","Emu!830r","amccabe@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Shaunna","Gilliam","1005550091","sgilliam","Emu!830r","sgilliam@dv.ccenterprisecloud.com","TechSupport","Tim Lopez"],
["Colm","Cresswell","1005550092","ccresswell","Emu!830r","ccresswell@dv.ccenterprisecloud.com","TechSupport","Tim Lopez"],
["Elouise","Smart","1005550093","esmart","Emu!830r","esmart@dv.ccenterprisecloud.com","TechSupport","Tim Lopez"],
["Walter","Roosevelt","1005550094","wroosevelt","Emu!830r","wroosevelt@dv.ccenterprisecloud.com","TechSupport","Tim Lopez"],
["Haseeb","Sinclair","1005550095","hsinclair","Emu!830r","hsinclair@dv.ccenterprisecloud.com","TechSupport","Tim Lopez"],
["Elaine","George","1005550096","egeorge","Emu!830r","egeorge@dv.ccenterprisecloud.com","TechSupport","Tim Lopez"],
["Shiv","Holcomb","1005550097","sholcomb","Emu!830r","sholcomb@dv.ccenterprisecloud.com","VIP","Tim Lopez"],
["Ingrid","Sheldon","1005550098","isheldon","Emu!830r","isheldon@dv.ccenterprisecloud.com","VIP","Tim Lopez"],
["Emrys","Floyd","1005550099","efloyd","Emu!830r","efloyd@dv.ccenterprisecloud.com","VIP","Tim Lopez"]]

agentlist= [
["Rodney","Iles","1005550071","riles","Emu!830r","riles@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Roshan","Randall","1005550072","rrandall","Emu!830r","rrandall@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Mccauley","Hancock","1005550073","mhancock","Emu!830r","mhancock@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Alan","Montes","1005550074","amontes","Emu!830r","amontes@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Montague","Wardle","1005550075","mwardle","Emu!830r","mwardle@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Margie","Blundell","1005550076","mblundell","Emu!830r","mblundell@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Gideon","Mckeown","1005550077","gmckeown","Emu!830r","gmckeown@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Jagoda","Appleton","1005550078","jappleton","Emu!830r","jappleton@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Shanai","Bass","1005550079","sbass","Emu!830r","sbass@dv.ccenterprisecloud.com","HelpDesk","Tim Lopez"],
["Aran","Stanton","1005550080","astanton","Emu!830r","astanton@dv.ccenterprisecloud.com","Membership","Tim Lopez"],
["Graeme","Dorsey","1005550081","gdorsey","Emu!830r","gdorsey@dv.ccenterprisecloud.com","Membership","Tim Lopez"],
["Malia","Chang","1005550082","mchang","Emu!830r","mchang@dv.ccenterprisecloud.com","Membership","Tim Lopez"],
["Brandi","Fuentes","1005550083","bfuentes","Emu!830r","bfuentes@dv.ccenterprisecloud.com","Membership","Tim Lopez"],
["Faith","Gill","1005550084","fgill","Emu!830r","fgill@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Markus","Neal","1005550085","mneal","Emu!830r","mneal@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Dominique","Wolfe","1005550086","dwolfe","Emu!830r","dwolfe@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Jada","Harwood","1005550087","jharwood","Emu!830r","jharwood@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Tiana","Manning","1005550088","tmanning","Emu!830r","tmanning@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Zahara","Ferry","1005550089","zferry","Emu!830r","zferry@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Aya ","Mccabe","1005550090","amccabe","Emu!830r","amccabe@dv.ccenterprisecloud.com","Retention","Tim Lopez"],
["Shaunna","Gilliam","1005550091","sgilliam","Emu!830r","sgilliam@dv.ccenterprisecloud.com","TechSupport","Tim Lopez"],
["Colm","Cresswell","1005550092","ccresswell","Emu!830r","ccresswell@dv.ccenterprisecloud.com","TechSupport","Tim Lopez"],
["Elouise","Smart","1005550093","esmart","Emu!830r","esmart@dv.ccenterprisecloud.com","TechSupport","Tim Lopez"],
["Walter","Roosevelt","1005550094","wroosevelt","Emu!830r","wroosevelt@dv.ccenterprisecloud.com","TechSupport","Tim Lopez"],
["Haseeb","Sinclair","1005550095","hsinclair","Emu!830r","hsinclair@dv.ccenterprisecloud.com","TechSupport","Tim Lopez"],
["Elaine","George","1005550096","egeorge","Emu!830r","egeorge@dv.ccenterprisecloud.com","TechSupport","Tim Lopez"],
["Shiv","Holcomb","1005550097","sholcomb","Emu!830r","sholcomb@dv.ccenterprisecloud.com","VIP","Tim Lopez"],
["Ingrid","Sheldon","1005550098","isheldon","Emu!830r","isheldon@dv.ccenterprisecloud.com","VIP","Tim Lopez"],
["Emrys","Floyd","1005550099","efloyd","Emu!830r","efloyd@dv.ccenterprisecloud.com","VIP","Tim Lopez"]]

client = pymongo.MongoClient('localhost',27017)
aedb = client['aedb']
agents = aedb['agents']


# Insert
insert = "off"
if 'on' in insert:
    for agent in agentlist:
        print("Agent Name {0}, Agent DN {1}".format(agent[3],agent[2]))
        agents.insert_one({
            'firstname': agent[0],
            'lastname': agent[1],
            'dn': agent[2],
            'username': agent[3],
            'pwd': 'Emu!830r',
            'email': agent[5],
            'team': agent[6],
            'phonemac': 'SEP00{0}'.format(agent[2])
        })


# Read AGent Information
agent_read = "off"
if "on" in agent_read:
    agent_read_list = agents.find({})
    for agent in agent_read_list:
        print("{0}".format(agent))



