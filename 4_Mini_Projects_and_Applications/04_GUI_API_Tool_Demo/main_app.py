import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import time
import random
import string
import re
import urllib.parse
import urllib.request
import threading
import queue # 用于线程间通信
import sys # 用于处理可能存在的编码问题


# --- 配置 ---
BASE_URL = "https://jx.oxah.cn"

# 文件列表 API 路径
FILE_LIST_API_PATH = "/api/v1/user/parse/get_file_list"
# 获取下载链接 API 路径
DOWNLOAD_LINKS_API_PATH = "/api/v1/user/parse/get_download_links"


# !!! IMPORTANT: 填写你在网站上使用的固定的免费解析密码 !!!
# 请在这里填写你的解析密码！
FIXED_PARSE_PASSWORD = "5541"


# --- 辅助函数 ---

def get_random_string(length):
    """生成指定长度的随机字符串 (包含字母和数字)"""
    letters_digits = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters_digits) for i in range(length))

def get_random_hex(length):
    """生成指定长度的随机十六进制字符串"""
    hex_chars = string.hexdigits.lower()
    return ''.join(random.choice(hex_chars) for i in range(length))

def parse_baidu_link_info(link):
    """
    尝试从百度网盘分享链接中提取 shareid, surl 和 uk。
    """
    surl = None
    shareid = None
    uk = None

    try:
        parsed_url = urllib.parse.urlparse(link)

        # 从路径中提取 surl (通常是 /s/ 后面的部分)
        path_parts = parsed_url.path.split('/')
        if 's' in path_parts:
             try:
                 surl_index = path_parts.index('s') + 1
                 if surl_index < len(path_parts):
                     surl = path_parts[surl_index]
                     # surl 可能包含查询参数前的部分，需要进一步处理如果URL像 /s/xxxx?param=...
                     if '?' in surl:
                         surl = surl.split('?')[0]
             except ValueError:
                 pass

        # 从查询参数中提取 shareid 和 uk
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if 'shareid' in query_params and query_params['shareid']:
            shareid = query_params['shareid'][0]
        if 'uk' in query_params and query_params['uk']:
            uk = query_params['uk'][0]

        # 如果 surl 没从路径中提取到，尝试从参数中获取（不常见但以防万一）
        if not surl and 'surl' in query_params and query_params['surl']:
             surl = query_params['surl'][0]

    except Exception as e:
        print(f"Error parsing link {link}: {e}") # 打印到控制台方便调试
        return None, None, None

    return surl, shareid, uk

def get_new_session_with_cookies(base_url, log_callback=None):
    """
    创建一个新的 requests Session，并访问网站主页或解析页以获取初始 Cookies。
    log_callback: 用于向 GUI 日志区域输出信息的回调函数
    """
    session = requests.Session()
    try:
        initial_url = f"{base_url}/user/parse"
        if log_callback:
            log_callback(f"尝试获取新会话 Cookies 从: {initial_url}")
        initial_headers = {
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
             "Accept-Encoding": "gzip, deflate, br, zstd",
             "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
             "Connection": "keep-alive",
             "Upgrade-Insecure-Requests": "1",
        }
        response = session.get(initial_url, headers=initial_headers, timeout=15)
        response.raise_for_status() # 对 4xx 或 5xx 错误抛出异常
        if log_callback:
            log_callback("成功获取新会话 Cookies。")
        return session
    except requests.exceptions.RequestException as e:
        if log_callback:
            log_callback(f"错误：获取初始会话失败: {e}")
        return None

def build_api_payload(api_path, share_link_info, extraction_code, parse_password, fs_ids=None):
    """
    根据 API 路径和信息构建请求负载。
    share_link_info: tuple (surl, shareid, uk) 从 parse_baidu_link_info 获取
    fs_ids: 列表，用于指定需要获取链接的文件 fs_id (只用于 DOWNLOAD_LINKS_API_PATH)
    """
    surl, shareid, uk = share_link_info

    base64_chars = string.ascii_letters + string.digits + '+/'
    randsk_val = ''.join(random.choice(base64_chars) for _ in range(random.randint(30, 40))) + '='

    # 共同参数，根据你提供的两个 Payload 结构来构建
    payload = {
        "parse_password": parse_password,
        "pwd": extraction_code,
        "shareid": shareid,
        "surl": surl,
        "uk": uk,
        "dir": "/", # <-- dir 参数在两个 Payload 中都有
        "token": "guest", # 根据你的截图，使用 guest 作为 token
        "rand1": get_random_hex(32),
        "rand2": get_random_hex(32),
        "rand3": get_random_hex(32),
        "randsk": randsk_val,
        "vcode_input": "",
        "vcode_str": ""
    }

    # 根据 API 路径设置 fs_id
    if api_path == FILE_LIST_API_PATH:
        # 获取文件列表时，根据之前的成功经验，fs_id 为空列表
        payload["fs_id"] = []
    elif api_path == DOWNLOAD_LINKS_API_PATH:
        # 获取下载链接时，fs_id 为选中的文件 fs_id 列表
        if fs_ids is None or not isinstance(fs_ids, list):
             # 理论上不会发生，但在代码中增加检查
             print("Error: DOWNLOAD_LINKS_API_PATH requires a list of fs_ids") # 打印到控制台
             return None # 返回 None 表示 Payload 构建失败
        payload["fs_id"] = fs_ids
        # **移除**之前猜测需要添加的 "ua" 参数！它不在你提供的下载链接 Payload 里。
        # payload["ua"] = "netdisk;P2SP;3.0.20.88" # REMOVED

    # 过滤掉值为 None 的键
    payload = {k: v for k, v in payload.items() if v is not None}

    return payload


def call_api(session: requests.Session, api_path, payload, log_callback=None):
    """
    使用提供的 Session 调用 API。
    log_callback: 用于向 GUI 日志区域输出信息的回调函数
    """
    # --- 构建请求头 (Headers) --- (这部分不变)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/user/parse",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
        "sec-ch-ua": '"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }

    xsrf_token_cookie = session.cookies.get('XSRF-TOKEN')
    if xsrf_token_cookie:
        try:
            headers['X-XSRF-TOKEN'] = urllib.request.unquote(xsrf_token_cookie)
        except Exception as e:
            if log_callback:
                log_callback(f"警告：解码 XSRF-TOKEN Cookie 失败: {e}. 使用原始值。")
            headers['X-XSRF-TOKEN'] = xsrf_token_cookie
    else:
         if log_callback:
             log_callback("警告：Session中未找到XSRF-TOKEN Cookie。可能影响请求。")


    full_api_url = f"{BASE_URL}{api_path}"
    if log_callback:
        log_callback(f"尝试发送请求到: {full_api_url}")
        # log_callback(f"Payload: {json.dumps(payload, indent=2)}") # 可选：打印 Payload 到日志

    try:
        response = session.post(full_api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status() # 对 4xx 或 5xx 状态码抛出异常

        if log_callback:
            log_callback(f"请求完成，状态码: {response.status_code}")

        try:
            return response.json()
        except json.JSONDecodeError:
            if log_callback:
                log_callback("错误：API 响应不是有效的 JSON。")
                log_callback(f"响应内容: {response.text}")
            # 在非JSON响应时，也返回状态码和响应文本
            return {"code": response.status_code, "message": "非JSON响应或解码失败", "response_text": response.text}

    except requests.exceptions.RequestException as e:
        if log_callback:
            # 将请求异常信息直接作为消息返回
            log_callback(f"错误：API 请求期间发生异常: {e}")
            # --- 新增：尝试获取并日志服务器返回的响应体 ---
            if e.response is not None:
                 try:
                     error_response_text = e.response.text
                     if log_callback:
                          log_callback(f"错误响应状态码: {e.response.status_code}")
                          log_callback(f"错误响应体:\n{error_response_text}")
                     # 将错误响应体也包含在返回的字典中
                     return {"code": "request_error", "message": str(e), "error_response_status": e.response.status_code, "error_response_text": error_response_text}
                 except Exception as inner_e:
                      if log_callback:
                           log_callback(f"尝试获取错误响应体失败: {inner_e}")
                      return {"code": "request_error", "message": str(e)} # 无法获取响应体时返回原始错误信息
            else:
                 # 如果 e.response 为 None，表示是连接错误或其他请求层面的异常
                 if log_callback:
                     log_callback("错误：请求未收到服务器响应。")
                 return {"code": "request_error", "message": str(e)} # 未收到响应时返回原始错误信息

        # 如果不是 requests.exceptions.RequestException，则抛出
        raise


# --- GUI 应用程序类 ---

class ParserGUI:
    def __init__(self, root):
        self.root = root
        root.title("千幻云简易解析器 (学习研究)")
        # 设置窗口大小和最小尺寸
        root.geometry("600x550") # 稍微增加高度容纳新按钮
        root.minsize(400, 450)


        # 存储文件列表数据 (包含fs_id等)
        self.file_list_data = []
        # 存储当前会话，用于获取文件列表后获取下载链接 (如果限制基于会话)
        self.current_session = None
        # 存储解析链接信息，用于后续获取下载链接时复用
        self.current_link_info = (None, None, None)
        self.current_extraction_code = ""
        self.current_parse_password = ""

        # 线程间通信队列
        self.queue = queue.Queue()


        # --- GUI 元素布局 ---
        input_frame = ttk.LabelFrame(root, text="输入信息")
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(input_frame, text="网盘链接:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.link_entry = ttk.Entry(input_frame, width=60)
        self.link_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(input_frame, text="提取码:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.code_entry = ttk.Entry(input_frame, width=20)
        self.code_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(input_frame, text="解析密码:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.password_entry = ttk.Entry(input_frame, width=20, show="*") # 密码框隐藏输入
        self.password_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")
        # 自动填充固定的解析密码
        self.password_entry.insert(0, FIXED_PARSE_PASSWORD)


        get_list_button = ttk.Button(input_frame, text="获取文件列表", command=self.on_get_file_list)
        get_list_button.grid(row=3, column=0, columnspan=2, pady=10)

        input_frame.columnconfigure(1, weight=1) # 使输入框列可扩展


        results_frame = ttk.LabelFrame(root, text="文件列表")
        results_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        self.file_listbox = tk.Listbox(results_frame, height=10)
        self.file_listbox.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        # 绑定列表项选择事件
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)

        listbox_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        listbox_scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.config(yscrollcommand=listbox_scrollbar.set)

        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)


        # 显示下载链接区域
        link_frame = ttk.LabelFrame(root, text="下载链接 (选中文件后显示，可复制)")
        link_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.download_link_entry = ttk.Entry(link_frame, state='readonly') # 初始状态为只读
        self.download_link_entry.insert(0, "请在文件列表中选择一个文件")
        self.download_link_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.copy_button = ttk.Button(link_frame, text="复制链接", command=self.copy_link_to_clipboard)
        self.copy_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        link_frame.columnconfigure(0, weight=1) # 让 Entry 列可扩展
        link_frame.columnconfigure(1, weight=0) # 让按钮列保持固定大小


        log_frame = ttk.LabelFrame(root, text="状态日志")
        log_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

        self.log_text = scrolledtext.ScrolledText(log_frame, height=5, state='disabled', wrap='word')
        self.log_text.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # 使主窗口可扩展
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1) # 使文件列表区域可扩展
        root.rowconfigure(3, weight=1) # 使日志区域可扩展


        # 启动队列处理线程
        self.root.after(100, self.process_queue)

        # 检查是否填写了固定解析密码，如果没有，弹出提示框
        if FIXED_PARSE_PASSWORD == "你的固定的解析密码":
             messagebox.showwarning("配置错误", "请编辑代码文件，将 FIXED_PARSE_PASSWORD 替换为你实际的解析密码，否则程序无法工作。")


    def log_message(self, message):
        """向日志文本框添加消息"""
        try:
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
        except UnicodeEncodeError:
             try:
                encoded_message = message.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
                self.log_text.config(state='normal')
                self.log_text.insert(tk.END, f"[Encoding Error Handled] {encoded_message}\n")
                self.log_text.see(tk.END)
             except Exception:
                 self.log_text.config(state='normal')
                 self.log_text.insert(tk.END, "[Unknown Encoding Error]\n")
                 self.log_text.see(tk.END)
        finally:
            self.log_text.config(state='disabled')


    def on_get_file_list(self):
        """点击“获取文件列表”按钮时的事件处理"""
        share_link = self.link_entry.get().strip()
        extraction_code = self.code_entry.get().strip()
        parse_password = self.password_entry.get().strip()

        if not share_link or not parse_password or parse_password == "你的固定的解析密码":
            messagebox.showwarning("输入错误", "网盘链接和解析密码不能为空，或解析密码未配置！")
            return

        # 清空之前的结果
        self.file_listbox.delete(0, tk.END)
        # 重置下载链接显示
        self.download_link_entry.config(state='normal')
        self.download_link_entry.delete(0, tk.END)
        self.download_link_entry.insert(0, "正在获取文件列表...")
        self.download_link_entry.config(state='readonly')

        self.file_list_data = []
        self.current_session = None # 重置会话，每次获取列表都尝试新会话
        self.current_link_info = parse_baidu_link_info(share_link) # 存储链接信息
        self.current_extraction_code = extraction_code
        self.current_parse_password = parse_password

        if self.current_link_info == (None, None, None):
             self.log_message("错误：无法从网盘链接解析所需信息。请检查链接格式。")
             self.download_link_entry.config(state='normal')
             self.download_link_entry.delete(0, tk.END)
             self.download_link_entry.insert(0, "链接解析失败")
             self.download_link_entry.config(state='readonly')
             return


        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END) # 清空日志
        self.log_text.config(state='disabled')
        self.log_message("正在获取文件列表...")

        # 启动一个新线程来执行网络请求
        thread = threading.Thread(
            target=lambda: self.worker_get_file_list(
                self.current_link_info,
                self.current_extraction_code,
                self.current_parse_password
            )
        )
        thread.start()


    def worker_get_file_list(self, link_info, extraction_code, parse_password):
        """在单独线程中执行获取文件列表的网络请求"""
        try:
            # 获取新 Session 模拟新用户
            session = get_new_session_with_cookies(BASE_URL, log_callback=self.log_message)
            if not session:
                self.queue.put(("log", "获取新会话失败，无法继续。"))
                self.queue.put(("update_link_entry", "获取文件列表失败"))
                return

            # 存储当前使用的会话，用于后续获取下载链接
            self.current_session = session

            # 构建 Payload
            payload = build_api_payload(FILE_LIST_API_PATH, link_info, extraction_code, parse_password)
            if payload is None: # 检查 Payload 是否构建失败
                 self.queue.put(("log", "错误：构建文件列表 Payload 失败。"))
                 self.queue.put(("update_link_entry", "构建文件列表请求失败"))
                 return


            # 调用 API
            response_data = call_api(
                session=session,
                api_path=FILE_LIST_API_PATH,
                payload=payload,
                log_callback=self.log_message
            )

            # 将结果放入队列，让主线程处理
            if response_data:
                # 如果 API 调用在 call_api 内部因 requests 异常而返回了错误字典，也传递给主线程处理
                self.queue.put(("api_response", {"api_path": FILE_LIST_API_PATH, "data": response_data}))
            else:
                 self.queue.put(("log", "未收到有效的API响应数据 (获取文件列表)。"))
                 self.queue.put(("update_link_entry", "获取文件列表失败"))

        except Exception as e:
            self.queue.put(("log", f"线程 (获取文件列表) 发生未知错误: {e}"))
            self.queue.put(("update_link_entry", f"获取文件列表发生错误: {e}"))


    def on_file_select(self, event):
        """文件列表框选中文件时的事件处理"""
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            # 没有选中任何项，或者取消了选择
            self.download_link_entry.config(state='normal')
            self.download_link_entry.delete(0, tk.END)
            self.download_link_entry.insert(0, "请在文件列表中选择一个文件")
            self.download_link_entry.config(state='readonly')
            return

        # 获取选中的第一个索引
        index = selected_indices[0]

        # 检查是否有文件列表数据且索引有效
        if not self.file_list_data or not (0 <= index < len(self.file_list_data)):
             self.log_message("错误：无效的文件列表索引。")
             return

        file_info = self.file_list_data[index]
        selected_fs_id = file_info.get("fs_id")
        filename = file_info.get("server_filename", "未知文件名")

        if selected_fs_id is None:
             self.log_message(f"错误：选中文件 '{filename}' 没有找到 fs_id。")
             # 更新下载链接Entry的提示文本
             self.download_link_entry.config(state='normal')
             self.download_link_entry.delete(0, tk.END)
             self.download_link_entry.insert(0, f"无法获取文件 '{filename}' 的 fs_id")
             self.download_link_entry.config(state='readonly')
             return

        # 确保有可用的会话和链接信息来调用获取下载链接 API
        if not self.current_session or not self.current_link_info or not self.current_parse_password:
             self.log_message("错误：缺少会话或链接信息，无法获取下载链接。请先重新获取文件列表。")
             # 更新下载链接Entry的提示文本
             self.download_link_entry.config(state='normal')
             self.download_link_entry.delete(0, tk.END)
             self.download_link_entry.insert(0, "会话失效或信息缺失，请重新获取文件列表")
             self.download_link_entry.config(state='readonly')
             return


        self.log_message(f"正在获取文件 '{filename}' 的下载链接...")
        # 更新下载链接Entry的提示文本
        self.download_link_entry.config(state='normal')
        self.download_link_entry.delete(0, tk.END)
        self.download_link_entry.insert(0, f"获取 '{filename}' 下载链接中...")
        self.download_link_entry.config(state='readonly')


        # 启动一个新线程来执行获取下载链接的网络请求
        thread = threading.Thread(
            target=lambda: self.worker_get_download_link(
                self.current_session, # 复用获取文件列表时的会话
                self.current_link_info,
                self.current_extraction_code,
                self.current_parse_password,
                selected_fs_id # 传入选中的文件fs_id
            )
        )
        thread.start()


    def worker_get_download_link(self, session, link_info, extraction_code, parse_password, fs_id):
        """在单独线程中执行获取下载链接的网络请求"""
        try:
            # 构建 Payload (需要传入 fs_id 列表)
            payload = build_api_payload(DOWNLOAD_LINKS_API_PATH, link_info, extraction_code, parse_password, fs_ids=[fs_id])
            # 如果 build_api_payload 因为 fs_ids 为 None 而返回 None
            if payload is None:
                 self.queue.put(("log", "错误：构建下载链接 Payload 失败。"))
                 self.queue.put(("update_link_entry", "构建下载链接请求失败"))
                 return


            # 调用 API
            response_data = call_api(
                session=session, # 使用获取文件列表时创建的会话
                api_path=DOWNLOAD_LINKS_API_PATH,
                payload=payload,
                log_callback=self.log_message
            )

            # 将结果放入队列，让主线程处理
            if response_data:
                # 如果 API 调用在 call_api 内部因 requests 异常而返回了错误字典，也传递给主线程处理
                self.queue.put(("api_response", {"api_path": DOWNLOAD_LINKS_API_PATH, "data": response_data}))
            else:
                 self.queue.put(("log", "未收到有效的API响应数据 (获取下载链接)。"))
                 self.queue.put(("update_link_entry", "获取下载链接失败"))

        except Exception as e:
            self.queue.put(("log", f"线程 (获取下载链接) 发生未知错误: {e}"))
            self.queue.put(("update_link_entry", f"获取下载链接发生错误: {e}"))


    def copy_link_to_clipboard(self):
        """将下载链接复制到剪贴板"""
        # 从只读 Entry 中获取文本内容
        link_text = self.download_link_entry.get()

        # 检查获取到的文本是否是有效的链接，避免复制提示文字
        if link_text and (link_text.startswith("http://") or link_text.startswith("https://")):
            try:
                self.root.clipboard_clear() # 清空剪贴板
                self.root.clipboard_append(link_text) # 添加新的内容
                self.log_message("下载链接已复制到剪贴板。")
            except Exception as e:
                self.log_message(f"复制到剪贴板失败: {e}")
                messagebox.showerror("复制错误", f"复制到剪贴板失败: {e}")
        else:
            self.log_message("当前没有可复制的有效下载链接。")
            # messagebox.showinfo("复制提示", "当前没有可复制的有效下载链接。")


    def process_queue(self):
        """定期检查队列并处理线程发送的消息"""
        try:
            while True:
                msg_type, msg_data = self.queue.get_nowait()

                if msg_type == "log":
                    self.log_message(msg_data)
                elif msg_type == "api_response":
                    # 将 API 响应数据和是哪个 API 的响应传递给处理函数
                    self.handle_api_response(msg_data["api_path"], msg_data["data"])
                elif msg_type == "update_link_entry":
                    # 处理更新下载链接Entry的消息
                    self.download_link_entry.config(state='normal')
                    self.download_link_entry.delete(0, tk.END)
                    self.download_link_entry.insert(0, msg_data)
                    self.download_link_entry.config(state='readonly')

        except queue.Empty:
            pass # 队列为空，稍后再检查
        except Exception as e:
            self.log_message(f"队列处理错误: {e}")
        finally:
            self.root.after(100, self.process_queue)


    def handle_api_response(self, api_path, response_data):
        """在主线程中处理 API 响应数据，根据 API 路径分发处理"""
        # 检查是否是 requests 异常返回的错误字典
        if isinstance(response_data, dict) and response_data.get("code") == "request_error":
             self.log_message(f"❌ {api_path} API 请求异常: {response_data['message']}")
             # 如果是获取下载链接失败，更新下载链接显示
             if api_path == DOWNLOAD_LINKS_API_PATH:
                 self.download_link_entry.config(state='normal')
                 self.download_link_entry.delete(0, tk.END)
                 # 显示详细错误信息
                 self.download_link_entry.insert(0, f"获取下载链接请求失败: {response_data['message']}")
                 self.download_link_entry.config(state='readonly')
             else: # 获取文件列表请求失败或其他未知请求失败
                 self.file_list_data = []
                 self.file_listbox.delete(0, tk.END)
                 self.download_link_entry.config(state='normal')
                 self.download_link_entry.delete(0, tk.END)
                  # 显示详细错误信息
                 self.download_link_entry.insert(0, f"获取文件列表请求失败: {response_data['message']}")
                 self.download_link_entry.config(state='readonly')
             return


        self.log_message(f"收到 {api_path} 的 API 响应，正在处理...")
        # log_message(f"API 完整响应: {json.dumps(response_data, indent=2, ensure_ascii=False)}") # 可选：打印完整响应到日志

        # 现在只需要处理 code != "request_error" 的响应，也就是服务器返回的响应
        if response_data and response_data.get("code") == 200:
            if api_path == FILE_LIST_API_PATH:
                 self.handle_file_list_response(response_data)
            elif api_path == DOWNLOAD_LINKS_API_PATH:
                 self.handle_download_links_response(response_data)
            else:
                 self.log_message(f"未知 API 响应路径: {api_path}")

        elif isinstance(response_data, dict) and response_data.get("message"):
            msg = response_data['message']
            self.log_message(f"❌ {api_path} API 返回错误消息: {msg}")
            # 根据错误消息判断原因
            if "次数已达上限" in msg or "免费次数" in msg or "limit" in msg.lower():
                self.log_message("--> 检测到次数限制相关的错误。")
            elif "解析密码错误" in msg or "密码无效" in msg or "password" in msg.lower():
                self.log_message("--> 解析密码可能不正确或已失效。")
            # 可以在这里添加更多错误类型的判断和提示

            # 如果是获取文件列表失败，清空文件列表
            if api_path == FILE_LIST_API_PATH:
                self.file_list_data = []
                self.file_listbox.delete(0, tk.END)
                self.download_link_entry.config(state='normal')
                self.download_link_entry.delete(0, tk.END)
                self.download_link_entry.insert(0, f"获取文件列表失败: {msg}")
                self.download_link_entry.config(state='readonly')
            # 如果是获取下载链接失败，更新下载链接显示
            elif api_path == DOWNLOAD_LINKS_API_PATH:
                self.download_link_entry.config(state='normal')
                self.download_link_entry.delete(0, tk.END)
                self.download_link_entry.insert(0, f"获取下载链接失败: {msg}")
                self.download_link_entry.config(state='readonly')
            else:
                 # 未知 API 路径的错误处理
                 self.download_link_entry.config(state='normal')
                 self.download_link_entry.delete(0, tk.END)
                 self.download_link_entry.insert(0, f"未知API错误: {msg}")
                 self.download_link_entry.config(state='readonly')


        else:
            self.log_message(f"❓ {api_path} API 返回未知结构或非预期状态码: {response_data.get('code')}")
            # self.log_message(f"原始响应: {response_data}") # 如果需要可以打印完整原始响应
            # 根据是哪个 API 的响应，更新相应的界面元素
            if api_path == FILE_LIST_API_PATH:
                 self.file_list_data = []
                 self.file_listbox.delete(0, tk.END)
                 self.download_link_entry.config(state='normal')
                 self.download_link_entry.delete(0, tk.END)
                 self.download_link_entry.insert(0, f"获取文件列表失败: 未知响应")
                 self.download_link_entry.config(state='readonly')
            elif api_path == DOWNLOAD_LINKS_API_PATH:
                 self.download_link_entry.config(state='normal')
                 self.download_link_entry.delete(0, tk.END)
                 self.download_link_entry.insert(0, f"获取下载链接失败: 未知响应")
                 self.download_link_entry.config(state='readonly')
            else:
                 self.download_link_entry.config(state='normal')
                 self.download_link_entry.delete(0, tk.END)
                 self.download_link_entry.insert(0, f"未知API错误: 未知响应")
                 self.download_link_entry.config(state='readonly')


    def handle_file_list_response(self, response_data):
        """处理文件列表 API 响应并更新 GUI"""
        # 文件列表在 data.list 字段
        file_list = response_data.get("data", {}).get("list")

        if file_list:
            # 检查 file_list 是否是列表
            if not isinstance(file_list, list):
                 self.log_message("错误：API响应中 'data.list' 字段不是列表结构。")
                 self.file_list_data = []
                 self.file_listbox.delete(0, tk.END)
                 self.download_link_entry.config(state='normal')
                 self.download_link_entry.delete(0, tk.END)
                 self.download_link_entry.insert(0, "获取文件列表失败: 响应结构异常")
                 self.download_link_entry.config(state='readonly')
                 return

            self.file_list_data = file_list # 存储完整的文件数据
            self.file_listbox.delete(0, tk.END) # 清空列表框
            for file_info in file_list:
                # 确保 file_info 是字典且包含必要字段
                if isinstance(file_info, dict):
                    filename = file_info.get("server_filename", "未知文件名")
                    size_bytes = file_info.get("size", 0)
                    size_formatted = self.format_size(size_bytes)
                    try:
                        display_text = f"{filename} ({size_formatted})"
                        self.file_listbox.insert(tk.END, display_text)
                    except UnicodeEncodeError:
                        self.file_listbox.insert(tk.END, f"[编码错误] {filename}") # 使用占位符
                else:
                    self.log_message(f"警告：文件列表包含非字典项: {file_info}")
                    self.file_listbox.insert(tk.END, "[非文件项]")


            self.log_message(f"成功加载 {len(self.file_list_data)} 个文件/文件夹。请在列表中选择文件获取下载链接。")
            # 更新下载链接Entry的提示文本
            self.download_link_entry.config(state='normal')
            self.download_link_entry.delete(0, tk.END)
            if len(self.file_list_data) > 0:
                 self.download_link_entry.insert(0, "请在文件列表中选择一个文件获取下载链接")
            else:
                 self.download_link_entry.insert(0, "文件列表为空")
            self.download_link_entry.config(state='readonly')

        else:
            self.log_message("响应成功 (code 200)，但未在 'data.list' 字段中找到文件列表。")
            self.file_list_data = [] # 清空数据
            self.file_listbox.delete(0, tk.END) # 清空列表框
             # 更新下载链接Entry的提示文本
            self.download_link_entry.config(state='normal')
            self.download_link_entry.delete(0, tk.END)
            self.download_link_entry.insert(0, "未找到文件列表")
            self.download_link_entry.config(state='readonly')


    def handle_download_links_response(self, response_data):
        """处理获取下载链接 API 响应并更新 GUI"""
        # 根据你提供的响应结构，下载链接在 data 列表中的每个对象的 urls 列表中
        download_data_list = response_data.get("data")

        download_link = "未找到下载链接" # 默认值
        error_msg = None # 用于记录错误信息

        if download_data_list and isinstance(download_data_list, list) and len(download_data_list) > 0:
            # 假设我们只处理第一个文件（因为通常一次只获取一个文件的链接）
            # 并且下载链接在 urls 列表的第一个元素
            first_item = download_data_list[0]
            if isinstance(first_item, dict):
                 urls = first_item.get("urls")
                 if urls and isinstance(urls, list) and len(urls) > 0:
                     download_link = urls[0] # 获取第一个链接
                     self.log_message("✔ 成功获取下载链接。")
                 else:
                     error_msg = "错误：在 API 响应中未找到 'urls' 字段或链接列表为空。"
                     self.log_message(error_msg)
                     download_link = "获取链接失败: 未找到链接"
            else:
                 error_msg = "错误：获取下载链接 API 响应 'data' 列表中的项不是字典结构。"
                 self.log_message(error_msg)
                 download_link = "获取链接失败: 响应结构异常"
        else:
            error_msg = "错误：获取下载链接 API 响应结构异常，未找到 'data' 列表或列表为空。"
            self.log_message(error_msg)
            download_link = "获取链接失败: 响应异常"


        # 更新下载链接 Entry
        # 在插入链接前，需要移除转义字符 `\/`
        download_link_cleaned = download_link.replace("\\/", "/")
        self.download_link_entry.config(state='normal')
        self.download_link_entry.delete(0, tk.END)
        self.download_link_entry.insert(0, download_link_cleaned)
        self.download_link_entry.config(state='readonly')


    def format_size(self, size_bytes):
        """将字节数格式化为易读的单位 (KB, MB, GB)"""
        if size_bytes is None or size_bytes < 0:
            return "未知大小"
        if size_bytes == 0:
            return "0 B"
        size = float(size_bytes)
        units = ["B", "KB", "MB", "GB", "TB"]
        for unit in units:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"


# --- 主程序入口 ---

if __name__ == "__main__":
    # 检查是否填写了固定解析密码
    if FIXED_PARSE_PASSWORD == "你的固定的解析密码":
         print("\n!!!!! 错误：请在代码中填写正确的 FIXED_PARSE_PASSWORD !!!!!")
         print("请编辑代码文件，将 FIXED_PARSE_PASSWORD 替换为你实际的解析密码。")
         # 在GUI启动前提示并退出
         root_temp = tk.Tk()
         root_temp.withdraw() # Hide the main window
         messagebox.showwarning("配置错误", "请编辑代码文件，将 FIXED_PARSE_PASSWORD 替换为你实际的解析密码，否则程序无法工作。")
         root_temp.destroy()
         sys.exit(1) # Exit the script


    root = tk.Tk()
    app = ParserGUI(root)
    root.mainloop()