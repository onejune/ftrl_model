#coding=utf-8
import os, sys, json, random, re, time, datetime

def run():
    for line in sys.stdin:
        line = line.strip()
        part = line.split("\t")         
        if 'hash' in line:
            print line
            continue
        print '\t'.join(part[1:])
        
if __name__ == "__main__":
    run()
