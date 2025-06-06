import os
import shutil


def organize_files_by_prefix(base_dir: str):
    # 确保 base_dir 存在
    if not os.path.exists(base_dir):
        print(f"Directory {base_dir} does not exist.")
        return

    # 遍历 base_dir 下的所有文件
    for filename in os.listdir(base_dir):
        file_path = os.path.join(base_dir, filename)

        # 检查是否为文件
        if os.path.isfile(file_path):
            # 获取文件的前缀（假设前缀是文件名的第一部分，以 '_' 分隔）
            prefix = "_".join(filename.split("_")[:2])  # 获取前两个部分作为前缀

            # 获取前缀命名的文件夹路径
            new_folder_path = os.path.join(base_dir, prefix)

            # 检查文件夹是否存在
            if os.path.exists(new_folder_path) and os.path.isdir(new_folder_path):
                # 移动文件到现有文件夹
                new_file_path = os.path.join(new_folder_path, filename)
                shutil.move(file_path, new_file_path)
                print(f"Moved {filename} to {new_folder_path}")
            else:
                print(f"Folder {new_folder_path} does not exist. Skipping {filename}.")


# 使用示例
organize_files_by_prefix("asserts")
