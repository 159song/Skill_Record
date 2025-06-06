### ssh 命令

- **连接服务器**: 
    ```bash
    ssh -i /key_path  username@ip
    ```


- **从服务器下载文件**: 
    ```bash
    scp -i {name.pem} {user}@{ip}:{source_path} {target_path}
    ```




- **使用 rsync 从服务器下载文件**:
    ```bash
    rsync -avz -e "ssh -i /path/to/key.pem" username@server_ip:/path/to/remote/file /path/to/local/destination
    ```

    参数说明：
    - `-a`: 归档模式，保持文件属性（等价于-rlptgoD）
    - `-v`: 显示详细信息
    - `-z`: 传输时进行压缩
    - `-e "ssh -i /path/to/key.pem"`: 指定SSH登录方式和密钥文件
    - `username@server_ip:/path/to/remote/file`: 服务器上的文件路径
    - `/path/to/local/destination`: 本地目标路径