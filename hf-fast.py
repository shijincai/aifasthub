#!/usr/bin/env python3
import argparse
import hashlib
import http.client
import json
import os
import re
import sys
import threading
import time
import signal
from urllib.parse import urlparse
import ssl
import platform  # 添加platform模块

# 定义颜色
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

# 定义全局变量
DEBUG = 0
ENDPOINT = "https://aifasthub.com"
DEFAULT_REVISION = "main"
DEFAULT_JOBS = 4
DEFAULT_CHUNK_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_TIMEOUT = 30  # 默认超时时间

def format_size(size):
    """格式化文件大小"""
    if size == 0:  # 特殊处理大小为 0 的情况
        return "大小未知"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.1f} {unit}"

def get_system_info():
    """获取系统信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    return {
        'system': system,
        'machine': machine,
        'is_windows': system == 'windows',
        'is_macos': system == 'darwin',
        'is_linux': system == 'linux',
        'is_arm': 'arm' in machine or 'aarch64' in machine
    }

def setup_system_specific():
    """系统特定设置"""
    system_info = get_system_info()
    
    if system_info['is_windows']:
        # Windows特定设置
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass  # 如果设置失败，继续执行
    
    if system_info['is_macos']:
        # macOS特定设置
        os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'
    
    return system_info

def handle_connection_error(error, attempt, max_retries):
    """处理连接错误"""
    if isinstance(error, (http.client.RemoteDisconnected, ssl.SSLError)):
        color_print(YELLOW, f"连接断开 (尝试 {attempt + 1}/{max_retries}): {error}")
        time.sleep(2 ** attempt)  # 指数退避
    elif isinstance(error, TimeoutError):
        color_print(YELLOW, f"连接超时 (尝试 {attempt + 1}/{max_retries})")
        time.sleep(1)
    else:
        color_print(RED, f"未知错误 (尝试 {attempt + 1}/{max_retries}): {error}")
        debug_log(f"错误详情: {type(error)=}, {error.args=}")
        time.sleep(1)

def debug_log(*args):
    """调试输出函数"""
    if DEBUG:
        print(f"{YELLOW}[DEBUG] {' '.join(map(str, args))}{NC}", file=sys.stderr, flush=True)

def color_print(color, *args, **kwargs):
    """带颜色的print"""
    end = kwargs.get('end', '\n')
    print(color + ' '.join(map(str, args)) + NC, end=end, flush=True)

def http_request(method, url, headers=None, data=None, stream=False, timeout=DEFAULT_TIMEOUT, max_redirects=5):
    """发起HTTP请求"""
    debug_log(f"HTTP 请求: {method} {url}")
    parsed_url = urlparse(url)
    retries = 3

    # 检查是否是LFS URL
    is_lfs = any(x in parsed_url.netloc for x in ['cdn-lfs', 'lfs.huggingface.co', 'cdn-lfs.huggingface.co'])
    if is_lfs:
        # 对于LFS URL，使用代理服务器URL
        url = f"{ENDPOINT}/resolve/{parsed_url.path.lstrip('/')}"
        parsed_url = urlparse(url)
        debug_log(f"LFS文件，使用代理URL: {url}")

    for attempt in range(retries):
        try:
            context = ssl.create_default_context()
            if parsed_url.scheme == "https":
                conn = http.client.HTTPSConnection(parsed_url.netloc, timeout=timeout, context=context)
            else:
                conn = http.client.HTTPConnection(parsed_url.netloc, timeout=timeout)

            # 添加必要的请求头
            if headers is None:
                headers = {}
            if 'User-Agent' not in headers:
                headers['User-Agent'] = "aria2/1.36.0 hf-fast-python/0.2"
            if method != "HEAD":  # HEAD请求不需要Accept-Ranges
                headers['Accept-Ranges'] = 'bytes'

            path_with_query = parsed_url.path
            if parsed_url.query:
                path_with_query += "?" + parsed_url.query
            
            conn.request(method, path_with_query, body=data, headers=headers)
            response = conn.getresponse()

            # 创建一个包装的响应对象
            class ResponseWrapper:
                def __init__(self, response):
                    self.response = response
                    self.status = response.status
                    self.headers = dict(response.getheaders())
                    self._content = None

                def read(self, size=None):
                    return self.response.read(size) if size else self.response.read()

                def getheader(self, name, default=None):
                    return self.headers.get(name, default)

            wrapped_response = ResponseWrapper(response)
            
            if 200 <= response.status < 300:
                if stream:
                    return wrapped_response
                return wrapped_response.read()
            elif response.status in (301, 302, 307, 308):
                redirect_url = response.getheader('Location')
                debug_log(f"重定向到 {redirect_url}")
                if max_redirects <= 0:
                    color_print(RED, "重定向次数过多。")
                    return None
                # 如果重定向到LFS URL，使用代理
                if any(x in redirect_url for x in ['cdn-lfs', 'lfs.huggingface.co', 'cdn-lfs.huggingface.co']):
                    parsed_redirect = urlparse(redirect_url)
                    redirect_url = f"{ENDPOINT}/resolve/{parsed_redirect.path.lstrip('/')}"
                    debug_log(f"LFS重定向，使用代理URL: {redirect_url}")
                return http_request(method, redirect_url, headers, data, stream, timeout, max_redirects - 1)
            elif response.status == 416:  # Range Not Satisfiable
                debug_log("收到416响应，返回特殊状态")
                return wrapped_response
            else:
                color_print(RED, f"HTTP 错误: {response.status} {response.reason}")
                return None
                
        except Exception as e:
            handle_connection_error(e, attempt, retries)
            if attempt == retries - 1:  # 最后一次尝试
                color_print(RED, f"连接失败，已达到最大重试次数: {e}")
                return None
            continue
            
    return None

def fetch_metadata(repo_id, revision, hf_token, is_dataset):
    """获取仓库元数据"""
    api_path = "datasets" if is_dataset else "models"
    api_url = f"{ENDPOINT}/api/{api_path}/{repo_id}/revision/{revision}"
    debug_log(f"{api_url=}") # 打印 API URL

    headers = {}
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
    headers["User-Agent"] = "aria2/1.36.0 hf-fast-python/0.2"  # 模拟 aria2

    metadata_str = http_request("GET", api_url, headers=headers)
    if metadata_str:
        try:
            metadata = json.loads(metadata_str)
            debug_log("API 响应:", json.dumps(metadata, indent=2))
            return metadata
        except json.JSONDecodeError:
            color_print(RED, "错误：无法解析元数据 JSON")
            print(metadata_str)
            return None
    else:
        color_print(RED, "错误：无法获取元数据")
        return None

def filter_files(metadata, include_patterns, exclude_patterns):
    """根据模式过滤文件"""
    if not metadata:  # Handle the case where metadata is None
        return []

    filtered_files = []
    for sibling in metadata.get('siblings', []):
        rfilename = sibling.get('rfilename')
        if not rfilename:
            continue

        # 应用包含模式
        if include_patterns:
            included = any(re.search(pattern, rfilename) for pattern in include_patterns)
        else:
            included = True

        # 应用排除模式
        if exclude_patterns:
            excluded = any(re.search(pattern, rfilename) for pattern in exclude_patterns)
        else:
            excluded = False

        if included and not excluded:
            filtered_files.append(sibling)

    return filtered_files

def calculate_total_size(files, metadata=None):
    """计算文件总大小"""
    # 如果metadata中有usedStorage字段，优先使用它
    if metadata and 'usedStorage' in metadata:
        return metadata['usedStorage']
    
    # 否则尝试从文件列表计算总大小
    total_size = 0
    for file_info in files:
        size = file_info.get('size', 0)
        if size > 0:
            total_size += size
    return total_size

class ProgressBar:
    """进度条类"""
    def __init__(self, total_size, filename):
        self.total_size = total_size
        self.filename = filename
        self.last_update = 0
        self.update_interval = 0.1  # 更新间隔（秒）
        
    def update(self, current_size):
        now = time.time()
        if now - self.last_update < self.update_interval:
            return
            
        self.last_update = now
        if self.total_size > 0:
            percent = (current_size / self.total_size) * 100
            bar_length = 30
            filled_length = int(bar_length * current_size // self.total_size)
            bar = '=' * filled_length + '-' * (bar_length - filled_length)
            color_print(GREEN, 
                f"\r[{bar}] {percent:.1f}% - {self.filename} "
                f"({format_size(current_size)}/{format_size(self.total_size)})", 
                end='')
        else:
            color_print(GREEN, 
                f"\r下载中 - {self.filename} ({format_size(current_size)})", 
                end='')

def download_file(url, output_path, hf_token, start_byte=0, end_byte=None, progress_callback=None, stop_event=None):
    """优化的文件下载函数"""
    if stop_event and stop_event.is_set():
        return False
    
    # 创建目录
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    headers = {
        'User-Agent': 'aria2/1.36.0 hf-fast-python/0.2',
        'Accept-Ranges': 'bytes'
    }
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"

    # 检查本地文件
    if os.path.exists(output_path):
        local_size = os.path.getsize(output_path)
        if local_size > 0:
            headers['Range'] = f'bytes={local_size}-'
            start_byte = local_size
    else:
        local_size = 0

    try:
        response = http_request("GET", url, headers=headers, stream=True)
        if not response:
            return False

        # 处理416错误（Range Not Satisfiable）
        if response.status == 416:
            # 先尝试获取完整文件大小
            head_response = http_request("HEAD", url, headers={k: v for k, v in headers.items() if k != 'Range'})
            if head_response:
                total_size = int(head_response.headers.get('content-length', 0))
                if total_size > 0 and local_size == total_size:
                    debug_log(f"文件已完整下载: {output_path}")
                    return True
            
            debug_log("服务器不支持断点续传或本地文件不完整，从头开始下载")
            if os.path.exists(output_path):
                os.remove(output_path)
            headers.pop('Range', None)
            response = http_request("GET", url, headers=headers, stream=True)
            if not response:
                return False
            local_size = 0
            start_byte = 0

        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))
        if total_size == 0 and 'content-range' in response.headers:
            try:
                total_size = int(response.headers['content-range'].split('/')[-1])
            except (IndexError, ValueError):
                pass

        mode = 'ab' if start_byte > 0 else 'wb'
        with open(output_path, mode) as f:
            downloaded = start_byte
            progress_bar = ProgressBar(total_size, os.path.basename(output_path))
            
            while True:
                if stop_event and stop_event.is_set():
                    return False
                    
                chunk = response.read(DEFAULT_CHUNK_SIZE)
                if not chunk:
                    break
                    
                f.write(chunk)
                downloaded += len(chunk)
                progress_bar.update(downloaded)

        print()  # 换行

        # 验证下载完成后的文件大小
        if total_size > 0:
            final_size = os.path.getsize(output_path)
            if final_size != total_size:
                debug_log(f"文件大小不匹配: {output_path} (本地: {final_size}, 远程: {total_size})")
                os.remove(output_path)
                return False

        return True
        
    except Exception as e:
        debug_log(f"下载出错: {e}")
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass
        return False

def download_files(files, output_dir, hf_token, jobs, stop_event):
    """多线程下载文件"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    total_files = len(files)
    completed_files = 0
    failed_files = []
    lock = threading.Lock()

    def worker(file_info):
        """下载线程"""
        nonlocal completed_files
        nonlocal failed_files
        
        if stop_event.is_set():
            return

        rfilename = file_info['rfilename']
        file_url = f"{ENDPOINT}/{file_info['repo_id']}/resolve/{file_info['revision']}/{rfilename}"
        output_path = os.path.join(output_dir, rfilename)
        remote_size = file_info.get('size', 0)

        try:
            # 检查本地文件是否已完整下载
            if os.path.exists(output_path):
                local_size = os.path.getsize(output_path)
                if remote_size > 0 and local_size == remote_size:
                    with lock:
                        completed_files += 1
                        color_print(GREEN, f"已存在: {rfilename}")
                    return

            if not download_file(file_url, output_path, hf_token, progress_callback=None, stop_event=stop_event):
                with lock:
                    failed_files.append(rfilename)
                return

            with lock:
                completed_files += 1
                color_print(GREEN, f"已完成: {rfilename}")
        except Exception as e:
            with lock:
                failed_files.append(rfilename)
                color_print(RED, f"下载失败 {rfilename}: {str(e)}")

    # 创建线程池
    threads = []
    active_threads = []  # 跟踪活动线程

    for file_info in files:
        if stop_event.is_set():
            break

        # 清理已完成的线程
        active_threads = [t for t in active_threads if t.is_alive()]
        
        # 等待直到有可用的线程槽
        while len(active_threads) >= jobs:
            time.sleep(0.1)
            active_threads = [t for t in active_threads if t.is_alive()]
        
        thread = threading.Thread(target=worker, args=(file_info,))
        thread.start()
        active_threads.append(thread)
        threads.append(thread)

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 打印最终结果
    print("\n" + "="*50)
    color_print(GREEN, f"下载完成: {completed_files}/{total_files} 个文件")
    if failed_files:
        color_print(RED, f"下载失败: {len(failed_files)} 个文件")
        for failed_file in failed_files:
            color_print(RED, f"  - {failed_file}")

def main():
    """主函数"""
    # 设置全局变量
    global DEBUG, ENDPOINT
    
    # 系统特定初始化
    system_info = setup_system_specific()
    
    # 参数解析
    parser = argparse.ArgumentParser(
        description="从 Hugging Face 模型中心下载文件，支持加速。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s gpt2                          # 下载 gpt2 模型
  %(prog)s -d squad                      # 下载 squad 数据集
  %(prog)s -i "*.bin" -e "*.md" gpt2     # 只下载 .bin 文件，排除 .md 文件
  %(prog)s -t $HF_TOKEN -j 8 llama-2    # 使用令牌下载，8线程
  %(prog)s --debug gpt2                  # 启用调试模式下载
""")
    
    parser.add_argument("repo_id", help="仓库 ID (例如，gpt2 或 username/repo_name)")
    parser.add_argument("-i", "--include", nargs='+', help="包含与模式匹配的文件（可多次使用）")
    parser.add_argument("-e", "--exclude", nargs='+', help="排除与模式匹配的文件（可多次使用）")
    parser.add_argument("-t", "--token", help="用于私有仓库的 Hugging Face 令牌")
    parser.add_argument("-r", "--revision", default=DEFAULT_REVISION, help="仓库修订/标签 (默认: main)")
    parser.add_argument("-d", "--dataset", action="store_true", help="下载数据集而不是模型")
    parser.add_argument("-j", "--jobs", type=int, default=DEFAULT_JOBS, help="并发下载数 (默认: 4)")
    parser.add_argument("-o", "--output", default=".", help="输出目录 (默认: 当前目录)")
    parser.add_argument("--endpoint", default=ENDPOINT, help=f"API 端点 (默认: {ENDPOINT})")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--check", action="store_true", help="检查本地文件")
    
    args = parser.parse_args()
    
    # 设置输出目录
    if args.output == ".":
        args.output = args.repo_id.split('/')[-1]
    
    # 更新全局变量
    DEBUG = args.debug
    ENDPOINT = args.endpoint
    
    # 设置信号处理
    stop_event = threading.Event()
    def signal_handler(sig, frame):
        color_print(YELLOW, "\n检测到中断信号，正在停止下载...")
        stop_event.set()
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # 获取元数据
        metadata = fetch_metadata(args.repo_id, args.revision, args.token, args.dataset)
        if not metadata:
            return 1
            
        # 过滤文件
        files = filter_files(metadata, args.include, args.exclude)
        if not files:
            color_print(YELLOW, "没有要下载的文件。")
            return 1
            
        # 添加必要信息
        for file_info in files:
            file_info['repo_id'] = f"{'datasets' if args.dataset else 'models'}/{args.repo_id}"
            file_info['revision'] = args.revision
        
        # 计算总大小
        total_size = calculate_total_size(files, metadata)
        if total_size > 0:
            color_print(GREEN, f"找到 {len(files)} 个文件，总大小: {format_size(total_size)}")
        else:
            color_print(GREEN, f"找到 {len(files)} 个文件，总大小未知")
        
        # 执行下载或检查
        if args.check:
            check_local_files(files, args.output)
        else:
            download_files(files, args.output, args.token, args.jobs, stop_event)
            
    except KeyboardInterrupt:
        color_print(YELLOW, "\n用户中断下载。")
        stop_event.set()
        return 1
    except Exception as e:
        color_print(RED, f"发生错误: {e}")
        if DEBUG:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

def check_local_files(files, output_dir):
    """检查本地文件与远程文件的一致性"""
    mismatched_files = []

    for file_info in files:
        rfilename = file_info['rfilename']
        local_path = os.path.join(output_dir, rfilename)
        remote_size = file_info.get('size', 0)
        remote_sha256 = file_info.get('sha256')

        if os.path.exists(local_path):
            local_size = os.path.getsize(local_path)
            if local_size != remote_size:
                mismatched_files.append((rfilename, "大小不匹配", local_size, remote_size))
            elif remote_sha256:
                local_sha256 = calculate_sha256(local_path)
                if local_sha256 != remote_sha256:
                    mismatched_files.append((rfilename, "SHA256 不匹配", local_sha256, remote_sha256))
        else:
            mismatched_files.append((rfilename, "未找到", 0, remote_size))

    if mismatched_files:
        color_print(YELLOW, "不匹配的文件：")
        for file, reason, local_val, remote_val in mismatched_files:
            if reason == "大小不匹配":
                color_print(YELLOW, f"  {file}: {reason} (本地: {format_size(local_val)}, 远程: {format_size(remote_val)})")
            else:
                color_print(YELLOW, f"  {file}: {reason} (本地: {local_val}, 远程: {remote_val})")
    else:
        color_print(GREEN, "所有本地文件与远程文件匹配。")

def calculate_sha256(file_path):
    """计算文件的SHA256哈希值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    sys.exit(main()) 
