sudo lsof +L1 | awk '{
    size=$7;
    if (size >= 1073741824) 
        size=sprintf("%.2f GB", size/1073741824);
    else if (size >= 1048576) 
        size=sprintf("%.2f MB", size/1048576);
    else if (size >= 1024) 
        size=sprintf("%.2f KB", size/1024);
    else 
        size=sprintf("%d B", size);
    print $1, $2, $3, $4, $5, $6, size, $8, $9, $10;
}'        查看进程占用内存


ps -f -p 3210271    查看进程