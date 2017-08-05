#coding=utf-8
import os, sys, json, random, re, time, datetime

def feature_hash(string):
    string = string.strip()
    seed = long(5381)
    hashValue = long(0)
    for i in range(0, len(string)):
        hashValue = (hashValue * seed) + ord(string[i])
        hashValue = hashValue % (2 ** 64)
    hashValue = hashValue & 0x7FFFFFFF
    hashValue = str(hashValue % 10000000)
    #print 'hash\t' + string + '\t' + hashValue
    return hashValue

def run():
    for line in sys.stdin:
        line = line.strip()
        part = line.split("\003")        
        features = part[1].strip().split('\t')
        arr = part[0].split('\t')
        stamp = arr[0]     
        log_type = arr[1]
        label = None
        if g_feature_type == 'ctr':
            if 'ins' in log_type:
                continue
            if 'impression' in log_type:
                label = '0'
            else:
                label = '1'
        if g_feature_type == 'cvr':
            if  'impression' in log_type:
                continue
            if 'click' in log_type:
                label = '0'
            else:
                label = '1'
        ps = stamp + '\t' + label
        for fea in features:
            ps += '\t' + feature_hash(fea) + ':1'
        print ps
        
        
 
if __name__ == "__main__":
    global g_feature_type
    g_feature_type = os.environ.get('feature_type')
    run()
