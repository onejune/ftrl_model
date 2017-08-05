#!/usr/bin/env bash
#!/bin/bash
if [ ! -n "$1" ]
then
    echo "input argv is null."
    exit
else
    feature_type=$1
fi

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

job_name="FTRL_feature_merge"

date_old=$(date +%Y/%m/%d)
last_hour=$(date +%Y%m%d%H -d "1 hours ago")

calculate_days=1
input_path="s3://mob-emr-test/wanjun/m_sys_model/feature_process/*/${time_now:0:8}/$time_now/"
#input_path="s3://mob-emr-test/wanjun/m_sys_model/feature_process/*/${time_now:0:8}/*/"
hadoop fs -test -e ${input_path}/_SUCCESS
if [ $? -ne 0 ]; then
	input_path="s3://mob-emr-test/wanjun/m_sys_model/feature_process/*/${last_hour:0:8}/$last_hour/"
fi

echo $input_path

output_path="s3://mob-emr-test/wanjun/m_sys_model/feature_merge_$feature_type/${time_now:0:8}/$time_now/"
hadoop fs -rmr ${output_path}

hadoop-streaming \
-D mapreduce.job.name="${job_name}" \
-D mapred.reduce.tasks=100 \
-D mapreduce.reduce.memory.mb=3000 \
-D mapred.output.key.comparator.class=org.apache.hadoop.mapred.lib.KeyFieldBasedComparator \
-D mapred.output.compress=false \
-input ${input_path} \
-output ${output_path} \
-cacheArchive s3://mob-emr/data/will/tools/python272.tar.gz#python27 \
-file merge_mapper.py \
-file merge_reducer.py \
-cmdenv "feature_type=$feature_type" \
-mapper "python merge_mapper.py" \
-reducer "python merge_reducer.py"
