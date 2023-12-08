# AI快站

**AI快站** 是一个专注于提供HuggingFace模型**免费加速下载**服务的平台，旨在为AI开发者解决大模型下载中的常见问题。<br>
我们的服务包括高效的镜像加速和断点续传功能，确保下载过程既快速又稳定。在AI快站，可以体验到高达**4M/s**的下载速度，大幅减少等待时间。我们的平台专为解决HuggingFace大模型下载的缓慢速度和频繁断开问题而设计，提供一个更加便捷、高效的下载体验。

<p align="center">
    <img src="https://aifasthub.com/models/webdata/speed.png"/>
<p>

## 加速下载
关注微信公众号回复消息 **“AI快站”** ，获取高达**4M/s**的模型加速下载通道。
<p align="center">
    <img src="https://aifasthub.com/models/webdata/gongzonghao.jpg" width="200"/>
<p>


## 技术交流群
如有未收录模型文件，请在微信群提交。
<p align="center">
    <img src="https://aifasthub.com/models/webdata/aifasthub-weixin.png" width="200"/>
<p>

## 模型下载
### 方法1：下载器批量下载
1. 下载器客户端
   支持Linux、Windows、Mac系统，可批量下载模型目录里所有文件，**目前仅支持单线程下载**。
   
   下载地址：  [Linux](https://aifasthub.com/models/webdata/aifasthubdl.linux.zip)  [Windows](https://aifasthub.com/models/webdata/aifasthubdl.exe.zip)  [Mac](https://aifasthub.com/models/webdata/aifasthubdl.mac.zip)

2.  使用方法
```shell
./aifasthubdl.linux -h
Usage: aifasthubdl.linux [OPTIONS] --m <M>

Options:
  -m, --m <M>
          模型地址，例如： https://aifasthub.com/models/01-ai/Yi-6B
  -o, --o <O>
          保存目录，例如： ./ [default: ./]
  -h, --help
          Print help
  -V, --version
          Print version

#例如
./aifasthubdl.linux -o ./test -m https://aifasthub.com/models/01-ai/Yi-6B
#-o 指定模型本地保存目录
#-m AI快站模型URL
```

### 方法2：从网站页面直接下载
查找确认模型文件后，复制模型URL逐个下载模型文件。


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

