#coding=utf-8
import os, sys, json, random, re, time, datetime

reload(__import__('sys' )).setdefaultencoding('utf-8')
cur_stamp = time.mktime(datetime.datetime.now().timetuple())

'''
image_size:
    UNKNOWN = 0,
    NONE = 1,
    SIZE_320x50 = 2,
    SIZE_300x250 = 3,
    SIZE_480x320 = 4,
    SIZE_320x480 = 5,
    SIZE_300x300 = 6,
    SIZE_1200x627 = 7,
    SIZE_REWARDED_VIDEO = 8
platform:
    UNKNOWN = 0,
    ANDROID = 1,
    IOS = 2
NetworkType:
    UNKNOWN = 0,
    NET_2G = 2,
    NET_3G = 3,
    NET_4G = 4,
    NET_WIFI = 9
    
'''

def get_publisher():
    global  g_publisher
    g_publisher = {}

    fin = open('pub_unit.cfg')
    for line in fin:
        arr = line.split('\t')
        pub = arr[0].strip()
        app = arr[1].strip()
        unit = arr[2].strip()
        g_publisher[pub + '_' + app + '_' + unit] = 1
    fin.close()

def run():
    for line in sys.stdin:
        line = line.strip()
        part = line.split("\t")         
        if len(part) < 40:
            continue
        
        publisher_id = part[3]
        app_id = part[4]    
        unit_id = part[5]
        #only reserve m system publisher.
        if publisher_id + '_' + app_id + '_' + unit_id not in g_publisher:
            continue
        country = part[19]
        if re.match('^[a-zA-Z]+$', country) == None:
            continue
        extra9 = part[31]
        redu = part[39]
        #only reserve m system data
        if g_log_type == 'install' and (extra9 == '2' or redu == '2'):
            continue
        campaigns = ''
        ad_type = part[10]
        if g_log_type == 'only_impression':
            if 'wall' not in ad_type:
                continue
            campaigns = part[24].strip()
            if len(campaigns) == 0:
                continue
        else:
            campaigns = part[7].strip()
        campaigns = campaigns.split(',')
        #flap the campaigns for only_impression log.
        for cam in campaigns:
            print cam + '\t' + line
        
            
 
if __name__ == "__main__":
    global g_log_type
    g_log_type = os.environ.get('log_type')
    get_publisher()
    run()





