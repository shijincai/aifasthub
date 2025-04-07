# AI快站 - Hugging Face Hub 加速下载

## 🚀 为什么选择AI快站？

* **⚡️ 超快下载速度**
  独特的加速技术，模型下载速度最高可达 **10M/s+**，比直接下载快 **10 倍**以上。
* **🔄 断点续传支持**
  支持断点续传功能，解决大模型下载中断的烦恼，确保下载 **100%** 完成。
* **🆓 免费使用**
  作为公益项目，下载服务**免费使用**，让每个开发者都能便捷访问AI资源。

---

## 📖 HuggingFace加速使用教程

### 1. 网页在线访问

直接通过AI快站搜索并访问模型、数据集页面，所有资源都会自动通过我们的加速节点访问。

### 2. 命令行工具下载 (`hf-fast.sh`)

`hf-fast.sh`，是本站开发的 huggingface 专用下载工具，基于成熟工具 `aria2`，可以做到稳定高速下载不断线。支持主流Linux、Mac等系统。

**基础使用**

```bash
# 下载hf-fast.sh
wget https://fast360.xyz/images/hf-fast.sh
chmod a+x hf-fast.sh

# 下载AI模型
./hf-fast.sh gpt2

# 下载数据集
./hf-fast.sh -d squad
```

### 3.Hugging Face CLI

使用官方的`huggingface-cli`命令行工具，通过设置环境变量即可高速下载模型或数据集。

```bash
# 安装依赖

pip install -U huggingface_hub

# 设置环境变量

## Linux/Mac

export HF_ENDPOINT=https://aifasthub.com

## Windows PowerShell

$env:HF_ENDPOINT = "https://aifasthub.com"

# 下载模型

huggingface-cli download --resume-download gpt2 --local-dir gpt2

# 下载数据集

huggingface-cli download --repo-type dataset --resume-download wikitext --local-dir wikitext
```

### 4.环境变量（非侵入式）

为Python脚本设置环境变量，无需修改代码即可加速下载。

```bash
#在运行Python脚本时设置环境变量

HF_ENDPOINT=https://aifasthub.com

#Python脚本直接加载模型ID
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('BAAI/bge-large-zh-v1.5')
```

### 5. Git Clone

加速Git克隆Hugging Face仓库。

```bash
# 完整克隆模型仓库
git clone https://aifasthub.com/gpt2
```

### 6. Ollama下载

快速从Hugging Face下载GGUF格式模型到Ollama，无需额外设置。

```bash
# 基本格式
ollama run aifasthub.com/{username}/{reponame}:{GGUF格式参数}

# 示例
ollama run aifasthub.com/bartowski/Llama-3.2-1B-Instruct-GGUF:Q8_0
ollama run aifasthub.com/Qwen/Qwen2.5-3B-Instruct-GGUF:Q3_K_M
```

## ❓ 常见问题

### 需要登录的资源如何下载？

对于需要登录的资源，请先在HuggingFace官网完成登录和授权，然后使用Access Token通过命令行工具下载：

```bash
# 使用hf-fast.sh工具
./hf-fast.sh -t YOUR_TOKEN model_name

# 使用huggingface-cli

export HF_TOKEN=YOUR_TOKEN
huggingface-cli download --token YOUR_TOKEN model_name --local-dir ./model_name
```

### 下载速度不稳定怎么办？

建议使用断点续传功能，即使网络不稳定也能确保完整下载。同时我们会持续优化节点性能，提供更稳定的服务。

对于大文件下载，推荐以下解决方案：

```bash
# 增加并发下载线程
./hf-fast.sh -j 8 model_name

# 使用huggingface-cli的断点续传
huggingface-cli download --resume-download model_name --local-dir ./model_name
```

### 如何在Python脚本中使用加速服务？

有两种方式在Python脚本中使用加速服务，无需修改现有代码：

```bash
# 方式1: 运行脚本时设置环境变量
HF_ENDPOINT=https://aifasthub.com python your_script.py

# 方式2: 在脚本中临时设置环境变量
import os
os.environ['HF_ENDPOINT'] = 'https://aifasthub.com'
# 之后正常使用transformers或huggingface_hub
```

### Ollama使用加速服务有哪些限制？

使用Ollama通过加速服务下载模型时，请注意：

* 仅支持GGUF格式的模型文件
* 需要使用完整的模型ID路径
* 必须指定量化参数（如Q4\_K\_M、Q8\_0等）

示例用法：

```bash
# 正确的用法
ollama run aifasthub.com/TheBloke/Llama-2-7B-Chat-GGUF:Q4_K_M

# 错误的用法（缺少量化参数）
ollama run aifasthub.com/TheBloke/Llama-2-7B-Chat-GGUF
```






## 免责声明
1. 本网站仅作为HuggingFace资源的镜像加速服务平台。所有模型和资源的版权和知识产权均归原作者所有。
2. 我们坚决尊重并遵守所有开源协议。若有任何资源违反其原始开源协议，敬请通知我们，我们将立即采取相应行动。
3. 本网站不对模型或资源的准确性、完整性或可靠性提供任何明示或暗示的保证。
4. 用户在使用任何模型或资源时，应自行判断其适用性，并自行承担所有风险和责任。
5. 本网站不承担因使用或依赖这些模型或资源而导致的任何损失。
6. 本免责声明的解释权归本网站所有。

