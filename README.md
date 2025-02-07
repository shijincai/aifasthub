# AI快站

**AI快站** 是一个专注于提供HuggingFace模型**免费加速下载**服务的平台，旨在为AI开发者解决大模型下载中的常见问题。<br>
我们的服务包括高效的镜像加速和断点续传功能，确保下载过程既快速又稳定。在AI快站，可以体验到高达**10M/s**的下载速度，大幅减少等待时间。我们的平台专为解决HuggingFace大模型下载的缓慢速度和频繁断开问题而设计，提供一个更加便捷、高效的下载体验。

## 🚀 为什么选择AI快站？

### ⚡️ 超快下载速度
独特的加速技术，模型下载速度最高可达10M/s+，比直接下载快10倍以上。

### 🔄 断点续传支持
支持断点续传功能，解决大模型下载中断的烦恼，确保下载100%完成。

### 🆓 免费使用
作为公益项目，下载服务免费使用，让每个开发者都能便捷访问AI资源。

## 📖 HuggingFace加速使用教程

### 1. 网页在线访问
直接通过AI快站搜索并访问模型、数据集页面，所有资源都会自动通过我们的加速节点访问。

### 2. 命令行工具下载
hf-fast.sh，是本站开发的 huggingface 专用下载工具，基于成熟工具 aria2，可以做到稳定高速下载不断线。支持主流Linux、Mac等系统。

hf-fast.py，基于 Python 原生 HTTP 库实现，支持多线程并发下载、断点续传和大文件加速，可在 Windows、Linux、Mac 等主流系统上实现稳定高速下载。

hf-fast.sh和hf-fast.py使用方法相同，请选择一种下载方式即可。

#### 基础使用
```shell
#下载hf-fast.sh
wget https://fast360.xyz/images/hf-fast.sh
chmod a+x hf-fast.sh
#下载hf-fast.py
wget https://fast360.xyz/images/hf-fast.py
chmod a+x hf-fast.py
#下载AI模型
./hf-fast.sh gpt2
#下载数据集
./hf-fast.sh -d squad
```
#### 完整使用说明
```shell
Usage: hf-fast [OPTIONS] REPO_ID
Download files from Hugging Face model hub with acceleration.
Options:
-i, --include PATTERN Include files matching pattern (can be used multiple times)
-e, --exclude PATTERN Exclude files matching pattern (can be used multiple times)
-t, --token TOKEN Hugging Face token for private repos
-r, --revision REV Repository revision/tag (default: main)
-d, --dataset Download dataset instead of model
-j, --jobs N Number of concurrent downloads (default: 4)
-o, --output DIR Output directory (default: current directory)
--endpoint URL API endpoint (default: https://aifasthub.com)
--debug Enable debug mode
-h, --help Display this help message
Examples:
./hf-fast.sh gpt2 # Download gpt2 model
./hf-fast.sh -d squad # Download squad dataset
./hf-fast.sh -i ".bin" -e ".md" gpt2 # Download only .bin files, exclude .md
./hf-fast.sh -t $HF_TOKEN -j 8 llama-2 # Download with token using 8 threads
./hf-fast.sh --debug gpt2 # Download with debug information
```
## ❓ 常见问题

### 需要登录的资源如何下载？
对于需要登录的资源，请先在HuggingFace官网完成登录和授权，然后使用Access Token通过命令行工具下载：
```shell
./hf-fast.sh -t YOUR_TOKEN model_name
```
### 下载速度不稳定怎么办？
建议使用断点续传功能，即使网络不稳定也能确保完整下载。同时我们会持续优化节点性能，提供更稳定的服务。


## 模型资源
- **国内厂商模型**

| 序号 | 厂商                 | 访问地址                            |
|------|----------------------|-----------------------------------|
| 1    | 阿里通义千问         | [https://aifasthub.com/models/Qwen](https://aifasthub.com/models/Qwen) |
| 2    | 百川智能             | [https://aifasthub.com/models/baichuan-inc](https://aifasthub.com/models/baichuan-inc) |
| 3    | CodeFuse             | [https://aifasthub.com/models/codefuse-ai](https://aifasthub.com/models/codefuse-ai) |
| 4    | 上海人工智能实验室   | [https://aifasthub.com/models/internlm](https://aifasthub.com/models/internlm) |
| 5    | 智谱                 | [https://aifasthub.com/models/THUDM](https://aifasthub.com/models/THUDM) |
| 6    | 智源人工智能研究院   | [https://aifasthub.com/models/BAAI](https://aifasthub.com/models/BAAI) |
| 7    | FlagAlpha         | [https://aifasthub.com/models/FlagAlpha](https://aifasthub.com/models/FlagAlpha) |
| 8    | 零一万物         | [https://aifasthub.com/models/01-ai](https://aifasthub.com/models/01-ai) |


- **海外厂商模型**

| 序号 | 厂商                | 访问地址                                                   |
| ---- | ------------------- | ---------------------------------------------------------- |
| 1    | google              | [https://aifasthub.com/models/google](https://aifasthub.com/models/google) |
| 2    | codefuse-ai         | [https://aifasthub.com/models/codefuse-ai](https://aifasthub.com/models/codefuse-ai) |
| 3    | mosaicml            | [https://aifasthub.com/models/mosaicml](https://aifasthub.com/models/mosaicml) |
| 4    | bigcode             | [https://aifasthub.com/models/bigcode](https://aifasthub.com/models/bigcode) |
| 5    | lmsys               | [https://aifasthub.com/models/lmsys](https://aifasthub.com/models/lmsys) |
| 6    | NousResearch        | [https://aifasthub.com/models/NousResearch](https://aifasthub.com/models/NousResearch) |
| 7    | OpenAssistant       | [https://aifasthub.com/models/OpenAssistant](https://aifasthub.com/models/OpenAssistant) |
| 8    | tiiuae              | [https://aifasthub.com/models/tiiuae](https://aifasthub.com/models/tiiuae) |
| 9    | bigscience          | [https://aifasthub.com/models/bigscience](https://aifasthub.com/models/bigscience) |
| 10   | diffusers           | [https://aifasthub.com/models/diffusers](https://aifasthub.com/models/diffusers) |
| 11   | microsoft           | [https://aifasthub.com/models/microsoft](https://aifasthub.com/models/microsoft) |
| 12   | runwayml            | [https://aifasthub.com/models/runwayml](https://aifasthub.com/models/runwayml) |
| 13   | HuggingFaceH4       | [https://aifasthub.com/models/HuggingFaceH4](https://aifasthub.com/models/HuggingFaceH4) |
| 14   | garage-bAInd        | [https://aifasthub.com/models/garage-bAInd](https://aifasthub.com/models/garage-bAInd) |
| 15   | openai              | [https://aifasthub.com/models/openai](https://aifasthub.com/models/openai) |


## 重要提醒
1. 我们的带宽资源有限。为了提供更好下载体验给所有开发者，对每个IP实施了下载速度限制。
2. 为了确保下载稳定性，请**避免使用迅雷**等下载工具。
3. 如果在下载过程中遇到任何问题，欢迎随时通过**yanaimingvov@gmail.com**与我们联系。

## 免责声明
1. 本网站仅作为HuggingFace资源的镜像加速服务平台。所有模型和资源的版权和知识产权均归原作者所有。
2. 我们坚决尊重并遵守所有开源协议。若有任何资源违反其原始开源协议，敬请通知我们，我们将立即采取相应行动。
3. 本网站不对模型或资源的准确性、完整性或可靠性提供任何明示或暗示的保证。
4. 用户在使用任何模型或资源时，应自行判断其适用性，并自行承担所有风险和责任。
5. 本网站不承担因使用或依赖这些模型或资源而导致的任何损失。
6. 本免责声明的解释权归本网站所有。

