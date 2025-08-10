import tkinter as tk
from tkinter import messagebox
import zipfile
import os
import glob
import xml.etree.ElementTree as ET
import http.server
import socketserver
import threading

GLOBAL_zipfilename = 'springmvc4.templates.1.1.0.zip'
GLOBAL_zipEntryNames = ['template.xml', 'template.zip', 'wizard.json']

# 全局变量控制服务器状态
httpd = None
server_thread = None
server_running = False

# 端口和地址
HOST = "localhost"
PORT = 8090

# 自定义 Handler 设置超时
class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

    def handle(self):
        # 设置每个请求的超时时间（秒）
        self.timeout = 5
        super().handle()


# 使用 ThreadingMixIn 支持多线程
class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True  # 守护线程：主线程退出时自动终止
    allow_reuse_address = True
    timeout = 5  # 服务器层面的超时

    def shutdown(self):
        # 先调用父类 shutdown
        super().shutdown()
        # 立即关闭 socket
        self.server_close()

class SpringTemplateBuilderGUI:
    def __init__(self, root):
        # 设置主窗口
        self.root = root
        self.root.title("Spring Template Builder")
        self.root.geometry("500x200")  # 调整窗口大小以适应更宽的按钮

        # 添加顶部状态栏
        self.status_label = tk.Label(root, text="Click the button!", bg="lightgray", fg="black", padx=10, pady=5)
        self.status_label.grid(row=0, column=0, columnspan=5, sticky="ew")  # 横向扩展

        # 添加版本号输入框
        version_frame = tk.Frame(root)
        version_frame.grid(row=1, column=0, columnspan=5, pady=10)

        version_label = tk.Label(version_frame, text="version:", font=("Arial", 12))
        version_label.pack(side=tk.LEFT, padx=10)

        self.version_entry = tk.Entry(version_frame, width=20, font=("Arial", 12))
        self.version_entry.pack(side=tk.LEFT, padx=10)

        # 添加按钮框架
        button_frame = tk.Frame(root)
        button_frame.grid(row=2, column=0, columnspan=5, pady=10)

        # 创建按钮并使用 grid 布局，确保按钮宽度自适应
        buttonsdesc = [
            ("Extract", self.extract),
            ("Read Version", self.read_version),
            ("Update Version", self.update_version),
            ("Repack", self.repack),
            ("Local Server (OFF)", self.local_server)
        ]

        self.buttons = []  # 存储按钮引用以便后续更新状态

        for i, (text, command) in enumerate(buttonsdesc):
            button = tk.Button(button_frame, text=text, command=command)
            button.grid(row=0, column=i, padx=5, sticky="ew")  # 按钮宽度自适应，横向扩展
            self.buttons.append(button)  # 保存按钮引用

        # 配置列权重，使按钮均匀分布并自动扩展
        for i in range(5):
            button_frame.grid_columnconfigure(i, weight=1)

        # 配置主窗口的列权重，确保整体布局可以扩展
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)
        root.grid_columnconfigure(3, weight=1)
        root.grid_columnconfigure(4, weight=1)

    def extract(self):
        unzip_file(GLOBAL_zipfilename)
        self.status_label.config(text="Extracted!")
        messagebox.showinfo("Extract", "Extract operation performed.")

    def read_version(self):
        version = get_descriptor_version(GLOBAL_zipEntryNames[0])
        #version = self.version_entry.get()
        if version:
            self.version_entry.delete(0, tk.END)
            self.version_entry.insert(0, version)
            #messagebox.showinfo("Read Version", f"Current version: {version}")
        else:
            messagebox.showwarning("Read Version", "failed reading Version")

    def update_version(self):
        new_version = self.version_entry.get()
        if new_version:
            update_descriptor_version(GLOBAL_zipEntryNames[0], new_version)
            messagebox.showinfo("Update Version", f"Version updated to: {new_version}")
        else:
            messagebox.showwarning("Update Version", "Version field is empty.")

    def repack(self):
        new_version = self.version_entry.get()
        if not new_version:
            messagebox.showwarning("Repack", "Version field is empty.")
            return
        rtn = False
        rtn = zip_directory('template')
        if not rtn:
            messagebox.showerror("Repack", "Failed to create template.")
            return
        rtn = create_zip3_package()
        if not rtn:
            messagebox.showerror("Repack", "Failed to create zip package.")
            return
        size = os.path.getsize(GLOBAL_zipfilename)
        version = self.version_entry.get()
        files = glob.glob('desc*.xml')
        update_desc = True
        for f in files:
            rtn = update_descriptor_size_by_id(f, size, version)
            if not rtn:
                update_desc = False
                messagebox.showerror("Repack", f"Failed to update descriptor in {f}.")
        if not update_desc:
            self.status_label.config(text="Repackaging failed!")
            return
        self.status_label.config(text=f"Repackaged! size={size}, version={version}")
        messagebox.showinfo("Repack", "Repack operation performed.")

    def local_server(self):
        #messagebox.showinfo("Local Server", "Local server started.")
        #self.status_label.config(text="Local http server running")
        self.toggle_server()

    def update_button_state(self):
        """根据服务器状态更新按钮外观"""
        server_btn = self.buttons[4]
        if server_running:
            server_btn.config(relief="sunken", text="Local Server (ON)", bg="lightgreen")
        else:
            server_btn.config(relief="raised", text="Local Server (OFF)", bg="lightcoral")


    def start_server(self):
        """在子线程中启动 HTTP 服务器"""
        global httpd, server_thread, server_running
        print(" 启动 HTTP Server ...")

        if server_running:
            return

        # 设置服务器
        # handler = http.server.SimpleHTTPRequestHandler
        # try:
        #     httpd = socketserver.TCPServer((HOST, PORT), handler)
        #     httpd.allow_reuse_address = True  # 避免端口占用问题
        # except OSError as e:
        #     print(f"无法绑定到端口 {PORT}: {e}")
        #     return
        try:
            httpd = ThreadedHTTPServer((HOST, PORT), CustomHandler)
        except OSError as e:
            print(f"无法绑定到端口 {PORT}: {e}")
            return

        def run():
            print(f" HTTP Server 运行在 http://{HOST}:{PORT}/")
            httpd.serve_forever(poll_interval=0.5)

        server_thread = threading.Thread(target=run, daemon=True)
        server_thread.start()
        server_running = True
        self.update_button_state()


    def stop_server(self):
        """停止 HTTP 服务器"""
        global httpd, server_running
        print(" 停止 HTTP Server ...")

        if httpd:
            httpd.shutdown()  # 停止 serve_forever()
            httpd.server_close()
            print(f" HTTP Server 已关闭")
            httpd = None

        server_running = False
        self.update_button_state()


    def toggle_server(self):
        """切换服务器状态（on/off）"""
        if server_running:
            self.stop_server()
        else:
            self.start_server()

def unzip_file(zip_path):
    """
    解压指定的 zip 文件到当前目录。

    参数:
        zip_path (str): zip 文件的路径
    """
    # 检查文件是否存在
    if not os.path.exists(zip_path):
        print(f"错误：文件 '{zip_path}' 不存在。")
        return

    # 检查是否为 zip 文件
    if not zipfile.is_zipfile(zip_path):
        print(f"错误：'{zip_path}' 不是一个有效的 zip 文件。")
        return

    # 获取当前目录作为解压目录
    extract_dir = os.getcwd()

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            print(f"正在解压 '{zip_path}' 到 '{extract_dir}' ...")
            zip_ref.extractall(extract_dir)
            print("解压完成。")
    except Exception as e:
        print(f"解压过程中发生错误：{e}")

def zip_directory(folder_path):
    """
    将指定目录打包成一个同名的 zip 文件（位于当前目录）。

    参数:
        folder_path (str): 要压缩的目录路径
    """
    # 检查目录是否存在
    if not os.path.exists(folder_path):
        print(f"错误：目录 '{folder_path}' 不存在。")
        return False

    if not os.path.isdir(folder_path):
        print(f"错误：'{folder_path}' 不是一个目录。")
        return False

    # 获取目录的绝对路径和名称
    folder_path = os.path.abspath(folder_path)
    folder_name = os.path.basename(folder_path)

    # ZIP 文件名与目录名相同，生成在当前工作目录下
    zip_filename = f"{folder_name}.zip"
    zip_filepath = os.path.join(os.getcwd(), zip_filename)

    try:
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            print(f"正在创建 '{zip_filename}' ...")
            # 遍历目录及其子目录
            for root, dirs, files in os.walk(folder_path):
                # 计算相对路径的根目录（用于在 zip 中保持目录结构）
                relative_root = os.path.relpath(root, folder_path)
                if relative_root == ".":
                    relative_root = ""  # 根目录下文件直接放入 zip 根

                # 写入每个文件
                for file in files:
                    file_path = os.path.join(root, file)
                    # 在 zip 中的路径
                    arcname = os.path.join(folder_name, relative_root, file)
                    zipf.write(file_path, arcname)

        print(f"打包完成：'{zip_filepath}'")
        return True
    except Exception as e:
        print(f"打包过程中发生错误：{e}")
    return False
    # 使用示例：
    # zip_directory('my_folder')

def get_descriptor_version(xml_file_path):
    """
    从指定的 XML 文件中查找 descriptor 节点，并返回其 version 属性。

    参数:
        xml_file_path (str): XML 文件的路径

    返回:
        str 或 None: 如果找到 version 属性则返回其值，否则返回 None
    """
    # 检查文件是否存在
    if not os.path.exists(xml_file_path):
        print(f"错误：文件 '{xml_file_path}' 不存在。")
        return None

    try:
        # 解析 XML 文件
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # 查找 descriptor 节点
        descriptor = root.find('descriptor')
        if descriptor is not None:
            version = descriptor.get('version')
            if version:
                return version
            else:
                print("警告：descriptor 节点存在，但没有 'version' 属性。")
                return None
        else:
            print("警告：XML 文件中未找到 'descriptor' 节点。")
            return None

    except ET.ParseError as e:
        print(f"XML 解析失败：{e}")
        return None
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
        return None

    # 使用示例：
    # version = get_descriptor_version('template.xml')
    # if version:
    #     print(f"descriptor version: {version}")

def update_descriptor_version(xml_file_path, new_version):
    """
    更新指定 XML 文件中 descriptor 节点的 version 属性。

    参数:
        xml_file_path (str): XML 文件的路径
        new_version (str): 要设置的新 version 值

    返回:
        bool: 更新成功返回 True，否则返回 False
    """
    # 检查文件是否存在
    if not os.path.exists(xml_file_path):
        print(f"错误：文件 '{xml_file_path}' 不存在。")
        return False

    try:
        # 解析 XML 文件
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # 查找 descriptor 节点
        descriptor = root.find('descriptor')
        if descriptor is not None:
            old_version = descriptor.get('version')
            # 更新 version 属性
            descriptor.set('version', new_version)
            # 保存回原文件
            tree.write(xml_file_path, encoding='UTF-8', xml_declaration=True)
            print(f"成功更新 version：'{old_version}' → '{new_version}'")
            return True
        else:
            print("错误：XML 文件中未找到 'descriptor' 节点。")
            return False

    except ET.ParseError as e:
        print(f"XML 解析失败：{e}")
        return False
    except Exception as e:
        print(f"更新文件时发生错误：{e}")
        return False

    # 使用示例：
    # update_descriptor_version('template.xml', '1.2.0')

def create_zip3_package():
    """
    将 GLOBAL_zipEntryNames 中的文件打包为 GLOBAL_zipfilename 指定的 zip 文件。
    """
    # 检查是否有文件需要打包
    if not GLOBAL_zipEntryNames:
        print("错误：没有指定要打包的文件。")
        return False

    # 准备 ZIP 文件路径（在当前目录下）
    zip_path = GLOBAL_zipfilename

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_name in GLOBAL_zipEntryNames:
                if os.path.isfile(file_name):
                    print(f"正在添加文件: {file_name}")
                    # 在 ZIP 中保持原始文件名，不包含路径
                    zipf.write(file_name, arcname=file_name)
                else:
                    print(f"错误：文件 '{file_name}' 不存在或不是文件，跳过。")
                    return False  # 可选：改为 continue 如果允许部分文件缺失

        print(f" 打包成功：'{zip_path}' 已创建，包含 {len(GLOBAL_zipEntryNames)} 个文件。")
        return True

    except Exception as e:
        print(f"x 打包过程中发生错误：{e}")
        return False

def update_descriptor_size_by_id(xml_file_path, new_size, new_version):
    """
    查找 id="springmvc41.template" 的 descriptor 节点，
    并更新其 size 和 version 属性。

    参数:
        xml_file_path (str): XML 文件路径
        new_size (str 或 int): 新的 size 值
        new_version (str): 新的 version 值

    返回:
        bool: 成功更新返回 True，否则返回 False
    """
    # 转换为字符串
    new_size = str(new_size)
    new_version = str(new_version)

    # 检查文件是否存在
    if not os.path.exists(xml_file_path):
        print(f"错误：文件 '{xml_file_path}' 不存在。")
        return False

    try:
        # 解析 XML
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # 查找 id="springmvc41.template" 的 descriptor 节点
        found = False
        for descriptor in root.findall('descriptor'):
            if descriptor.get('id') == 'springmvc41.template':
                # 获取旧值用于输出
                old_size = descriptor.get('size', 'N/A')
                old_version = descriptor.get('version', 'N/A')

                # 更新属性
                descriptor.set('size', new_size)
                descriptor.set('version', new_version)

                # 保存文件
                tree.write(xml_file_path, encoding='UTF-8', xml_declaration=True)
                print(f"成功更新 descriptor (id='springmvc41.template'):")
                print(f"  size:   '{old_size}' -> '{new_size}'")
                print(f"  version: '{old_version}' -> '{new_version}'")
                found = True
                break  # 假设只有一个匹配节点

        if not found:
            print("警告：未找到 id='springmvc41.template' 的 descriptor 节点。")
            return False

        return True

    except ET.ParseError as e:
        print(f"XML 解析失败：{e}")
        return False
    except Exception as e:
        print(f"更新过程中发生错误：{e}")
        return False

    # 使用示例：
    # update_descriptor_size_by_id('descriptors.xml', 135000， '1.1.17')

# 创建主窗口
root = tk.Tk()
app = SpringTemplateBuilderGUI(root)
root.mainloop()