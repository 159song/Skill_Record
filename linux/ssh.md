### ssh 命令

- **连接服务器**: 
    ```bash
    ssh -i /key_path  username@ip
    ```


- **从服务器下载文件**: 
    ```bash
    scp -i {name.pem} {user}@{ip}:{source_path} {target_path}
    ```