The Topics file contains a list of the ROS topics to record separated by groups. The sole purpose of these groups is organize the topics, and they can be enable/disabled together without going one by one.

A group is specified in the Topics file like follows
```yaml
GroupName:
  record_group: true/false
  topics:
    - record_topic: true/false
      name: /topic_1
    - record_topic: true/false
      name: /topic_2
```

## Example
```yaml
Estimator:
  record_group: true
  topics:
  - record_topic: true
    name: /estimator/current_pose
Test:
  record_group: true
  topics:
  - record_topic: false
    name: /birdwatch/console_log
IMU:
  record_group: false
  topics:
  - record_topic: false
    name: /mavros/imu/data_raw
  - record_topic: true
    name: /mavros/magnetometer/mag
```