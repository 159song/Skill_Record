Git: fatal: Unable to create '/home/ubuntu/work/zxs/daily_test/.git/index.lock': File exists.

查看ls -l /home/ubuntu/work/zxs/daily_test/.git/index.lock

删除rm /home/ubuntu/work/zxs/daily_test/.git/index.lock

.gitignore 中写入的文件不会上传



git restore --staged filename     取消git的跟踪


git push origin branch_name       推送


git reset --soft HEAD~1     head往前移动一个