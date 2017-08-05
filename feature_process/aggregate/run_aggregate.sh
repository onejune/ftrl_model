#!/usr/bin/env bash
#!/bin/bash
if [ ! -n "$1" ]
then
    echo "input argv is null."
    exit
else
    log_names=$1
fi

function construct_input_path()
{
    input_path=""
    delta=1
    while(($delta <= $1))
    do
        date_old=$(date +%Y/%m/%d/%H -d "$delta days ago")
        path="s3://mob-ad/adn/tracking-v3/$log_names/${date_old:0:10}/*/*/"
        input_path="$input_path,${path}"
        let delta+=1
    done
    echo ${input_path:1:${#input_path}-1}
}

basepath=$(cd `dirname $0`; pwd)
echo $basepath

echo "ScheduleTime: ${ScheduleTime}"
if [ -n "$ScheduleTime" ]; then
    time_now=${ScheduleTime:0:4}${ScheduleTime:5:2}${ScheduleTime:8:2}${ScheduleTime:11:2}
else
    time_now=$(date +"%Y%m%d%H")
fi
echo $time_now

time_old=$(date +%Y%m%d -d "1 days ago")
last_time=$(date +%Y%m%d%H -d "1 hour ago")

his_day=$(date +%Y%m%d -d "30 days ago")

job_name="FTRL_feature_$log_names"

date_old=$(date +%Y/%m/%d)
last_hour=$(date +%Y/%m/%d/%H -d "2 hours ago")

calculate_days=1
input_path="s3://mob-ad/adn/tracking-v3/$log_names/${last_hour:0:10}/*/${last_hour:11:2}/"
#input_path=$(construct_input_path $calculate_days)
echo $calculate_days
echo $input_path

last_hour=$(date +%Y%m%d%H -d "1 hour ago")
cache_file=s3://mob-emr-test/wanjun/adnserver_offline/offline_data/${time_now:0:8}/${time_now}/offline_data.dat
hadoop fs -test -e $cache_file
if [ $? -ne 0 ]; then
    echo "$cache_file not exists!"
	cache_file=s3://mob-emr-test/wanjun/adnserver_offline/offline_data/${last_hour:0:8}/${last_hour}/offline_data.dat
fi

cache_file=s3://mob-emr-test/shenlei.zhong/tmp_job/imp/m_ftrl_offline_feature.dat
feature_conf=s3://mob-emr-test/wanjun/m_sys_model/feature_config/feature_map.conf
output_path="s3://mob-emr-test/wanjun/m_sys_model/feature_process/$log_names/${time_now:0:8}/$time_now/"
hadoop fs -rmr ${output_path}

last_hour=$(date +%Y%m%d%H -d "3 hour ago")

hadoop-streaming \
-D mapreduce.job.name="${job_name}" \
-D mapred.reduce.tasks=300 \
-D mapreduce.reduce.memory.mb=3000 \
-D mapred.output.key.comparator.class=org.apache.hadoop.mapred.lib.KeyFieldBasedComparator \
-D mapred.output.compress=false \
-input ${input_path} \
-output ${output_path} \
-cacheArchive s3://mob-emr/data/will/tools/python272.tar.gz#python27 \
-cacheFile $cache_file#m_ftrl_offline_feature.dat \
-cacheFile $feature_conf#feature_map.conf \
-cacheFile s3://mob-emr-test/wanjun/adnserver_offline/offline_data/${last_hour:0:8}/${last_hour}/pub_unit.cfg#pub_unit.cfg \
-file agg_mapper.py \
-cmdenv "log_type=$1" \
-mapper "python agg_mapper.py" \
-reducer "cat"
