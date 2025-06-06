### 进程操作 命令

- **查看进程的具体执行命令**: 
  在 `top` 命令中按 `c` 键。

- **后台运行 Python 脚本并记录日志**: 
  ```bash
  nohup python bot_runner.py > "link_logs/output_$(date +%Y-%m-%d).log" 2>&1 &
  ```
  - **解释**:
    - `nohup`: 在后台运行进程，即使用户注销后，进程也会继续运行。
    - `python bot_runner.py`: 要运行的 Python 脚本。
    - `>`: 将标准输出重定向到一个文件。
    - `"link_logs/output_$(date +%Y-%m-%d).log"`: 输出日志文件的路径和名称，`$(date +%Y-%m-%d)` 会被替换为当前的日期，格式为 `YYYY-MM-DD`。
    - `2>&1`: 将标准错误输出重定向到标准输出中，因此错误信息也会被记录到同一个日志文件中。
    - `&`: 在后台运行该命令。

- **列出所有以 'python3 -m manual_bot' 开头的进程**: 
  ```bash
  ps aux | grep '/home/ubuntu/miniconda3/envs/multi_language/bin/python -m manual_bot -u' | grep -v grep
  ```

- **杀掉这些进程**: 
  ```bash
  pkill -f '/home/ubuntu/miniconda3/envs/multi_language/bin/python -m manual_bot -u'
  ```

  ```bash
  pkill -f '/home/ubuntu/miniconda3/envs/multi_language/bin/python -m bot_daily -u'
  ```


- **查看在运行的服务**: 
  ```bash
  journalctl -u ai-voice-order-main.service -f
  ```
