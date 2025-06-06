sudo vi /etc/nginx/sites-available/default
sudo systemctl restart nginx
sudo systemctl stop nginx
sudo systemctl start nginx
cat /var/log/nginx/error.log;
cat /var/log/nginx/access.log;
sudo systemctl status nginx
