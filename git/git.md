# Git 常见问题和命令

## index.lock 文件问题
当遇到以下错误时：`fatal: Unable to create '/home/ubuntu/work/zxs/daily_test/.git/index.lock': File exists.`

解决方法：
1. 检查锁文件：
```bash
ls -l /home/ubuntu/work/zxs/daily_test/.git/index.lock
```
2. 删除锁文件：
```bash
rm /home/ubuntu/work/zxs/daily_test/.git/index.lock
```

## Git 基础命令

### .gitignore
- 在 `.gitignore` 中列出的文件将不会被跟踪或上传

### 取消暂存文件
```bash
git restore --staged filename     # Remove file from staging area
```

### 推送更改
```bash
git push origin branch_name      # Push to specific branch
```

### 重置提交
```bash
git reset --soft HEAD~1          # Move HEAD back one commit
```