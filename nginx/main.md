# Nginx 常用命令

## 配置
```bash
# Edit default site configuration
sudo vi /etc/nginx/sites-available/default
```

## 服务管理
```bash
# Restart Nginx service
sudo systemctl restart nginx

# Stop Nginx service
sudo systemctl stop nginx

# Start Nginx service
sudo systemctl start nginx
```

## 日志和状态
```bash
# View error logs
cat /var/log/nginx/error.log

# View access logs
cat /var/log/nginx/access.log

# Check Nginx status
sudo systemctl status nginx
```
