#!/usr/bin/env bash

# 跨平台的numfmt包装函数
numfmt_wrapper() {
    local size=$1
    if command -v numfmt >/dev/null 2>&1; then
        numfmt --to=iec-i --suffix=B <<< "$size"
    else
        # 如果没有numfmt，使用awk实现简单的大小格式化
        awk -v size="$size" '
        BEGIN {
            split("B KB MB GB TB PB", units, " ")
            base = 1024
            for (i = 1; size >= base && i < length(units); i++) {
                size = size / base
            }
            printf "%.1f %s\n", size, units[i]
        }'
    fi
}

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Debug模式标志
DEBUG=0

# Debug输出函数
debug_log() {
    if [[ $DEBUG -eq 1 ]]; then
        printf "${YELLOW}[DEBUG] $*${NC}\n"
    fi
}

# 文件处理函数
process_file_list() {
    local metadata="$1"
    local output_file="$2"
    local tmp_file="${TEMP_DIR}/file_list.tmp"
    
    debug_log "Processing metadata to extract file list..."
    debug_log "API response:"
    debug_log "$(echo "$metadata" | jq '.' 2>/dev/null || echo "$metadata")"
    
    # 使用一次jq调用处理所有文件
    jq -r '.siblings[] | select(.rfilename != null) | .rfilename' <<< "$metadata" > "$tmp_file"
    
    debug_log "Found files:"
    debug_log "$(cat "$tmp_file")"
    
    # 如果有包含模式，应用过滤
    if [[ ${#INCLUDE_PATTERNS[@]} -gt 0 ]]; then
        local filtered_file="${TEMP_DIR}/filtered.tmp"
        > "$filtered_file"
        while IFS= read -r file; do
            for pattern in "${INCLUDE_PATTERNS[@]}"; do
                if [[ "$file" == $pattern ]]; then
                    echo "$file" >> "$filtered_file"
                    break
                fi
            done
        done < "$tmp_file"
        mv "$filtered_file" "$tmp_file"
    fi
    
    # 应用排除模式
    if [[ ${#EXCLUDE_PATTERNS[@]} -gt 0 ]]; then
        local filtered_file="${TEMP_DIR}/filtered.tmp"
        > "$filtered_file"
        while IFS= read -r file; do
            local exclude=0
            for pattern in "${EXCLUDE_PATTERNS[@]}"; do
                if [[ "$file" == $pattern ]]; then
                    exclude=1
                    break
                fi
            done
            [[ $exclude -eq 0 ]] && echo "$file" >> "$filtered_file"
        done < "$tmp_file"
        mv "$filtered_file" "$tmp_file"
    fi
    
    # 生成下载列表
    > "$output_file"
    while IFS= read -r file; do
        if [[ $IS_DATASET -eq 1 ]]; then
            echo "$ENDPOINT/datasets/$REPO_ID/resolve/$REVISION/$file" >> "$output_file"
        else
            echo "$ENDPOINT/$REPO_ID/resolve/$REVISION/$file" >> "$output_file"
        fi
        echo " dir=$OUTPUT_DIR" >> "$output_file"
        echo " out=$file" >> "$output_file"
        [[ -n "$HF_TOKEN" ]] && echo " header=Authorization: Bearer $HF_TOKEN" >> "$output_file"
        echo " header=User-Agent: aria2/1.36.0" >> "$output_file"
        echo >> "$output_file"
    done < "$tmp_file"
    
    # 检查是否有文件要下载
    if [[ ! -s "$output_file" ]]; then
        printf "${YELLOW}No files to download${NC}\n"
        exit 0
    fi
    
    # 计算总文件大小
    local total_size=0
    local file_count=0
    while IFS= read -r file; do
        local size
        size=$(jq -r ".siblings[] | select(.rfilename == \"$file\") | .size // 0" <<< "$metadata")
        total_size=$((total_size + size))
        file_count=$((file_count + 1))
    done < "$tmp_file"
    
    printf "${GREEN}Found $file_count files to download, total size: $(numfmt_wrapper $total_size)${NC}\n"
}

trap 'printf "${YELLOW}\nDownload interrupted. You can resume by re-running the command.\n${NC}"; exit 1' INT

display_help() {
    cat << EOF
Usage: ./hf-fast.sh [OPTIONS] REPO_ID
Download files from Hugging Face model hub with acceleration.

Options:
  -i, --include PATTERN   Include files matching pattern (can be used multiple times)
  -e, --exclude PATTERN   Exclude files matching pattern (can be used multiple times)
  -t, --token TOKEN      Hugging Face token for private repos
  -r, --revision REV     Repository revision/tag (default: main)
  -d, --dataset         Download dataset instead of model
  -j, --jobs N          Number of concurrent downloads (default: 4)
  -o, --output DIR      Output directory (default: current directory)
  --endpoint URL        API endpoint (default: https://aifasthub.com)
  --debug              Enable debug mode
  -h, --help           Display this help message

Examples:
  ./hf-fast.sh gpt2                          # Download gpt2 model
  ./hf-fast.sh -d squad                      # Download squad dataset
  ./hf-fast.sh -i "*.bin" -e "*.md" gpt2     # Download only .bin files, exclude .md
  ./hf-fast.sh -t \$HF_TOKEN -j 8 llama-2    # Download with token using 8 threads
  ./hf-fast.sh --debug gpt2                  # Download with debug information
EOF
    exit 1
}

# 参数解析
REPO_ID=""
INCLUDE_PATTERNS=()
EXCLUDE_PATTERNS=()
HF_TOKEN=""
REVISION="main"
IS_DATASET=0
JOBS=4
OUTPUT_DIR="."
ENDPOINT="https://aifasthub.com"

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--include)
            INCLUDE_PATTERNS+=("$2")
            shift 2
            ;;
        -e|--exclude)
            EXCLUDE_PATTERNS+=("$2")
            shift 2
            ;;
        -t|--token)
            HF_TOKEN="$2"
            shift 2
            ;;
        -r|--revision)
            REVISION="$2"
            shift 2
            ;;
        -d|--dataset)
            IS_DATASET=1
            shift
            ;;
        -j|--jobs)
            JOBS="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --endpoint)
            ENDPOINT="$2"
            shift 2
            ;;
        --debug)
            DEBUG=1
            shift
            ;;
        -h|--help)
            display_help
            ;;
        *)
            if [[ -z "$REPO_ID" ]]; then
                REPO_ID="$1"
            else
                printf "${RED}Error: Unexpected argument '$1'${NC}\n"
                exit 1
            fi
            shift
            ;;
    esac
done

# 检查必需参数
if [[ -z "$REPO_ID" ]]; then
    printf "${RED}Error: REPO_ID is required${NC}\n"
    display_help
fi

# 检查并安装依赖
install_dependencies() {
    local os_type
    local pkg_manager
    local install_cmd
    
    # 检测操作系统类型
    if [[ "$OSTYPE" == "darwin"* ]]; then
        os_type="macos"
        if command -v brew &>/dev/null; then
            pkg_manager="brew"
            install_cmd="brew install"
        else
            printf "${YELLOW}Homebrew not found. Installing Homebrew...${NC}\n"
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || {
                printf "${RED}Failed to install Homebrew. Please install it manually: https://brew.sh${NC}\n"
                exit 1
            }
            pkg_manager="brew"
            install_cmd="brew install"
        fi
    elif command -v apt-get &>/dev/null; then
        os_type="debian"
        pkg_manager="apt"
        install_cmd="sudo apt-get install -y"
    elif command -v dnf &>/dev/null; then
        os_type="fedora"
        pkg_manager="dnf"
        install_cmd="sudo dnf install -y"
    elif command -v yum &>/dev/null; then
        os_type="centos"
        pkg_manager="yum"
        install_cmd="sudo yum install -y"
    elif command -v pacman &>/dev/null; then
        os_type="arch"
        pkg_manager="pacman"
        install_cmd="sudo pacman -S --noconfirm"
    else
        printf "${RED}Unsupported operating system. Please install dependencies manually: curl, jq, aria2${NC}\n"
        exit 1
    fi
    
    printf "${YELLOW}Detected OS: $os_type with package manager: $pkg_manager${NC}\n"
    
    # 定义每个包管理器对应的包名
    local -A pkg_names=(
        ["brew"]="curl jq aria2"
        ["apt"]="curl jq aria2"
        ["dnf"]="curl jq aria2"
        ["yum"]="curl jq aria2"
        ["pacman"]="curl jq aria2"
    )
    
    # 检查并安装缺失的依赖
    local missing_deps=()
    for cmd in curl jq aria2c; do
        if ! command -v "$cmd" &>/dev/null; then
            case $cmd in
                aria2c) missing_deps+=("aria2") ;;
                *) missing_deps+=("$cmd") ;;
            esac
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        printf "${YELLOW}Installing missing dependencies: ${missing_deps[*]}${NC}\n"
        
        # 如果是 macOS，先更新 Homebrew
        if [[ "$os_type" == "macos" ]]; then
            brew update
        # 如果是 Debian/Ubuntu，先更新包列表
        elif [[ "$os_type" == "debian" ]]; then
            sudo apt-get update
        fi
        
        # 安装缺失的依赖
        for dep in "${missing_deps[@]}"; do
            printf "${YELLOW}Installing $dep...${NC}\n"
            if ! $install_cmd "$dep"; then
                printf "${RED}Failed to install $dep. Please install it manually.${NC}\n"
                exit 1
            fi
        done
        
        printf "${GREEN}All dependencies installed successfully.${NC}\n"
    fi
}

# 检查依赖工具
check_dependencies() {
    # 检查基础工具
    for cmd in curl jq; do
        if ! command -v "$cmd" &>/dev/null; then
            printf "${RED}Error: Required command '$cmd' not found. Please install it first.${NC}\n"
            exit 1
        fi
    done
    
    # 检查下载工具
    if command -v aria2c &>/dev/null; then
        DOWNLOADER="aria2c"
    elif command -v wget &>/dev/null; then
        DOWNLOADER="wget"
    else
        # 尝试安装aria2
        printf "${YELLOW}Attempting to install aria2...${NC}\n"
        install_dependencies
        if ! command -v aria2c &>/dev/null; then
            if ! command -v wget &>/dev/null; then
                printf "${RED}Error: Neither aria2c nor wget is available. Please install one of them manually.${NC}\n"
                exit 1
            fi
            DOWNLOADER="wget"
        else
            DOWNLOADER="aria2c"
        fi
    fi
}

# 检查依赖
check_dependencies

# 设置默认输出目录为REPO_ID的最后一部分
if [[ "$OUTPUT_DIR" == "." ]]; then
    OUTPUT_DIR="${REPO_ID##*/}"
fi

# 创建输出目录（不再进入目录）
mkdir -p "$OUTPUT_DIR"

# 构建API URL
if [[ $IS_DATASET -eq 1 ]]; then
    API_PATH="datasets/$REPO_ID"
else
    API_PATH="models/$REPO_ID"
fi

if [[ "$REVISION" != "main" ]]; then
    API_PATH="$API_PATH/revision/$REVISION"
fi

API_URL="$ENDPOINT/api/$API_PATH"

# 获取仓库元数据
printf "${YELLOW}Fetching repository metadata...${NC}\n"
if [[ -n "$HF_TOKEN" ]]; then
    METADATA=$(curl -s -H "Authorization: Bearer $HF_TOKEN" "$API_URL")
else
    METADATA=$(curl -s "$API_URL")
fi

# 检查API响应
if [[ $(echo "$METADATA" | jq -r 'if type=="object" then "yes" else "no" end') != "yes" ]]; then
    printf "${RED}Error: Failed to fetch metadata${NC}\n"
    echo "$METADATA"
    exit 1
fi

# 检查认证
if [[ $(echo "$METADATA" | jq -r '.gated // false') != "false" ]] && [[ -z "$HF_TOKEN" ]]; then
    printf "${RED}Error: This repository requires authentication. Please provide a token with --token${NC}\n"
    exit 1
fi

# 创建临时目录
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# 生成下载列表
DOWNLOAD_LIST="${TEMP_DIR}/download_list"
process_file_list "$METADATA" "$DOWNLOAD_LIST"

# 开始下载
printf "${GREEN}Starting download with $JOBS concurrent connections using ${DOWNLOADER}...${NC}\n"

# 设置下载线程数
THREADS=4

if [[ "$DOWNLOADER" == "aria2c" ]]; then
    debug_log "Using aria2c for download"
    debug_log "Download list content:"
    debug_log "$(cat "$DOWNLOAD_LIST")"
    
    # 根据debug模式设置aria2c的日志级别
    LOG_LEVEL="warn"
    [[ $DEBUG -eq 1 ]] && LOG_LEVEL="info"
    
    # 使用aria2c下载
    aria2c --console-log-level="$LOG_LEVEL" \
           --file-allocation=none \
           -x "$THREADS" \
           -j "$JOBS" \
           -s "$THREADS" \
           -k 1M \
           -c \
           --auto-file-renaming=false \
           --allow-overwrite=true \
           --always-resume=true \
           --remove-control-file=true \
           --check-integrity=false \
           -i "$DOWNLOAD_LIST"
    
    DOWNLOAD_STATUS=$?
else
    debug_log "Using wget for download"
    # 使用wget下载
    # 准备wget的下载列表
    WGET_LIST=$(mktemp)
    trap 'rm -f $WGET_LIST' EXIT
    
    # 从aria2格式转换为wget格式
    while IFS= read -r line || [[ -n "$line" ]]; do
        if [[ "$line" =~ ^http ]]; then
            url="$line"
        elif [[ "$line" =~ ^[[:space:]]*out=(.+)$ ]]; then
            filename="${BASH_REMATCH[1]}"
            # 创建目标目录
            mkdir -p "$OUTPUT_DIR/$(dirname "$filename")"
            # 将URL和输出文件路径写入wget列表
            printf "%s\n" "$url" >> "$WGET_LIST.urls"
            printf "%s/%s\n" "$OUTPUT_DIR" "$filename" >> "$WGET_LIST.paths"
        fi
    done < "$DOWNLOAD_LIST"
    
    # 使用wget下载
    paste "$WGET_LIST.urls" "$WGET_LIST.paths" | while IFS=$'\t' read -r url output_path; do
        wget --no-verbose \
             ${HF_TOKEN:+--header="Authorization: Bearer $HF_TOKEN"} \
             --output-document="$output_path" \
             --continue \
             "$url"
    done
    
    DOWNLOAD_STATUS=$?
    rm -f "$WGET_LIST.urls" "$WGET_LIST.paths"
fi

# 显示下载结果
if [[ $DOWNLOAD_STATUS -eq 0 ]]; then
    printf "\n${GREEN}Download completed successfully to: $OUTPUT_DIR${NC}\n"
    # 显示下载的文件列表和大小
    printf "${GREEN}Downloaded files:${NC}\n"
    find "$OUTPUT_DIR" -type f -printf "%s %p\n" | \
        numfmt --to=iec --field=1 | \
        sort -h | \
        while read size file; do
            printf "${GREEN}%10s${NC} %s\n" "$size" "${file#$OUTPUT_DIR/}"
        done
else
    printf "\n${RED}Download failed with status: $DOWNLOAD_STATUS${NC}\n"
    exit 1
fi
