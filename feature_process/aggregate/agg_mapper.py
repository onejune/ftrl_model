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

def get_feature_map():
    global feature_conf_list
    feature_conf_list = []
    fin = open('./feature_map.conf')
    for line in fin:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        arr = line.split(' ')
        brr = arr[0].split('#')
        brr = [a.strip() for a in brr]
        feature_conf_list.append(brr)
    fin.close() 
    

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


def get_offline_data():
    global app_cate_feature, cam_info_feature, pkg_info_feature
    app_cate_feature = {}
    cam_info_feature = {}
    pkg_info_feature = {}
    
    fin = open('m_ftrl_offline_feature.dat')
    try:
        for line in fin:
            parts = line.strip().split('\t')
            if len(parts) < 2:
                continue
            key = parts[0].strip()
            value = json.loads(parts[1])
            data_type, xid = key.split('\001')
            #appid -- category1, category2,......categoryN
            if data_type == 'app_id':
                app_cate_feature[xid] = value
                continue
            #campid info
            if data_type == 'campaign_id':
                if xid.isdigit():
                    cam_info_feature[xid] = value
                continue
            if data_type == 'package':
                pkg_info_feature[xid] = value
                continue
    except:
        pass
    fin.close()
    


def get_app_features(app_id):
    app_info = app_cate_feature.get(app_id)
    if not app_info:
        return ['appid_category=none']
    app_feature_list = app_info
    return app_feature_list


#extract single feature from log line
def extract_single_feature(part, feature_map):
    normal_feature_list = []
    app_feature_list = []
    #单维特征
    date_s = part[0]
    week_s = datetime.datetime(int(date_s[0:4]), int(date_s[4:6]), int(date_s[6:])).strftime("%w")
    week_h = 'week=' + week_s
    feature_map['week'] = week_h
    normal_feature_list.append(week_h)
    time_s = part[1].strip()
    if len(time_s) != 6:
        return None
    hour_s = time_s[0:2]
    hour_h = 'hour=' + hour_s
    feature_map['hour'] = hour_h
    normal_feature_list.append(hour_h)
    publisher_id = part[3]

    app_id = part[4]
    app_id_h = 'app_id=' + app_id
    feature_map['app_id'] = app_id_h
    normal_feature_list.append(app_id_h)
    
    #app category features
    app_feature_list = get_app_features(app_id)
    feature_map['appid_category'] = app_feature_list
    
    unit_id = part[5]
    unit_id_h = 'unit_id=' + unit_id
    feature_map['unit_id'] = unit_id_h
    normal_feature_list.append(unit_id_h)
    if publisher_id + '_' + app_id + '_' + unit_id not in g_publisher:
        return None
    advertiser_id = part[6]
    advertiser_id_h = 'adv=' + advertiser_id
    feature_map['advertiser_id'] = advertiser_id_h
    normal_feature_list.append(advertiser_id_h)
    ad_type = part[10]
    ad_type_h = 'ad_type=' + ad_type
    feature_map['ad_type'] = ad_type_h
    normal_feature_list.append(ad_type_h)
    campaigns = ''
    if g_log_type == 'only_impression':
        if 'wall' not in ad_type:
            return None
        campaigns = part[24].strip()
        if len(campaigns) == 0:
            return None
    else:
        campaigns = part[7].strip()
    feature_map['campaigns'] = campaigns.split(',')
    
    image_size = part[11]
    image_size_h = 'image_size=' + image_size
    feature_map['image_size'] = image_size_h
    normal_feature_list.append(image_size_h)
    
    platform = part[13]
    platform_h = 'platform=' + platform
    feature_map['platform'] = platform_h
    normal_feature_list.append(platform_h)
    
    os_version = part[14]
    os_version_h = 'os_version=' + os_version
    feature_map['os_version'] = os_version_h
    normal_feature_list.append(os_version_h)
    
    sdk_version = part[15]
    sdk_version_h = 'sdk_version=' + sdk_version
    feature_map['sdk_version'] = sdk_version_h
    normal_feature_list.append(sdk_version_h)
    
    device_model = part[16]
    device_model_h = 'device_model=' + device_model
    feature_map['device_model'] = device_model_h
    normal_feature_list.append(device_model_h)
    
    #screen_size = part[17]
    orientation = part[18]
    orientation_h = 'orientation=' + orientation
    feature_map['orientation'] = orientation_h
    normal_feature_list.append(orientation_h)
    
    country = part[19]
    if re.match('^[a-zA-Z]+$', country) == None:
        return None
    country = country.lower()
    country_h = 'country=' + country
    feature_map['country_code'] = country_h
    normal_feature_list.append(country_h)
    
    language = part[20]
    language_h = 'language=' + language
    feature_map['language'] = language_h
    normal_feature_list.append(language_h)
    
    network_type = part[21]
    network_type_h = 'network_type=' + network_type
    feature_map['network_type'] = network_type_h
    normal_feature_list.append(network_type_h)
    
    mcc_mnc = part[22]
    mcc_mnc_h = 'mcc_mnc=' + mcc_mnc
    feature_map['mcc_mnc'] = mcc_mnc_h
    normal_feature_list.append(mcc_mnc_h)
    
    #strategy
    extra3 = part[25]
     
    extra9 = part[31]
    redu = part[39]
    device_brand = part[45]
    device_brand_h = 'device_brand=' + device_brand
    feature_map['device_brand'] = device_brand_h
    normal_feature_list.append(device_brand_h)
    
    #only reserve m system data
    if g_log_type == 'install' and (extra9 == '2' or redu == '2'):
        return None
    
    return app_feature_list


def get_campaign_features(campaign_id, feature_map):
    campaign_id_h = 'campaign_id=' + campaign_id
    feature_map['campaign_id'] = campaign_id_h
    campaign_info = cam_info_feature.get(campaign_id)
    if not campaign_info:
        return None
    for key in campaign_info:
        value = campaign_info[key]
        feature_map[key] = value
    package = campaign_info.get('package_name')
    if package:
        package = package.split('=')[1]
        package_info = pkg_info_feature.get(package)
        if package_info:
            for key in package_info:
                value = package_info[key]
                feature_map[key] = value
    return
        
    
def run():
    fin = open('install_log')
    #for line in sys.stdin:
    for line in fin:
        feature_map = {}
        cur_stamp = str(time.mktime(datetime.datetime.now().timetuple()))
        part = line.strip().split("\t")         
        if len(part) < 40:
            continue
        #get single feature from line
        r = extract_single_feature(part, feature_map)
        if not r:
            continue
        #figure features by config
        #traverse by campaign
        campaigns = feature_map['campaigns']
        for campaign_id in campaigns:
            final_features = []
            get_campaign_features(campaign_id, feature_map)

            #traverse each rule
            for f_lst in feature_conf_list:
                if not f_lst:
                    continue
                result_list = ['']
                #parse each feature name in rule
                for f_name in f_lst:
                    #flap the features which the type is list
                    if f_name == 'appid_category' or f_name == 'dmp_tag':
                        cate_list = feature_map.get(f_name)
                        print f_name, cate_list
                        if not cate_list:
                            cate_list = [f_name + '=none']
                        r_lst = result_list
                        result_list = []
                        for fea in cate_list:
                            temp_list = [(r + '\001' + fea).strip('\001') for r in r_lst]
                            result_list += temp_list
                    else:
                        fea = feature_map.get(f_name, f_name + '=none')
                        temp_list = [(r + '\001' + fea).strip('\001') for r in result_list]
                        result_list = temp_list
                final_features += result_list

            #print by campaign
            ps = cur_stamp + '\t' + g_log_type + '\003'
            for feature in final_features:
                ps += feature + '\t'
            print ps.strip()
        
            
 
if __name__ == "__main__":
    global g_log_type, g_label
    #g_log_type = os.environ.get('log_type')
    g_log_type = 'install'
    get_publisher()
    get_offline_data()
    get_feature_map()
    run()





