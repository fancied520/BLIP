# BLIP 最小本地实验

这是一个尽量简单、今天就能跑通的 BLIP 本地实验项目，目标只有一件事：使用 Hugging Face 上的 `Salesforce/blip-image-captioning-base` 模型做图像描述（image captioning）。

本项目不做训练，不启动 Web 服务，也不依赖复杂框架。你只需要准备一张图片，然后运行一个 Python 脚本，就可以得到 caption。

## 当前功能

- 使用 BLIP 模型完成图像描述（image captioning）
- 支持本地图片输入
- 自动选择 GPU 或 CPU 推理
- 提供基础错误处理与清晰提示
- 便于后续扩展到视觉问答（VQA）

## 技术栈

- Python
- PyTorch
- Hugging Face Transformers
- Pillow

## 项目结构

```text
BLIP/
├─ .gitignore
├─ README.md
├─ requirements.txt
├─ caption.py
└─ images/
```

请把测试图片放到 `images/` 目录中，例如 `images/test.jpg`。

## 环境创建

推荐使用 Python 3.10 或 3.11。如果你的机器上暂时只有 Python 3.12，也可以先运行这个最小实验。

Windows PowerShell 示例：

```powershell
py -3.11 -m venv .venv
```

如果你的机器没有 Python 3.11，可以改成：

```powershell
py -3.12 -m venv .venv
```

激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 提示脚本执行被阻止，可以先临时放行当前终端：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

如果你不想激活虚拟环境，也可以直接使用虚拟环境里的 Python：

```powershell
.\.venv\Scripts\python.exe --version
```

## 安装依赖

项目最小依赖已经写在 `requirements.txt` 中：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

首次运行时，`transformers` 会从 Hugging Face 下载 BLIP 模型权重，所以需要可以访问网络。

## 如何运行

先准备一张测试图片，例如：

```text
images/test.jpg
```

然后执行：

```powershell
.\.venv\Scripts\python.exe caption.py images/test.jpg
```

脚本会自动选择设备：

- 如果检测到可用的 CUDA GPU，就优先使用 GPU
- 如果没有检测到 GPU，就自动回退到 CPU

## 预期输出示例

运行成功后，终端会输出一行 caption，例如：

```text
a dog running through a grassy field
```

或者：

```text
two people sitting at a table with food
```

## 常见报错与解决建议

### 1. `Image not found`

说明图片路径不对。请确认文件确实存在，例如：

```powershell
Get-ChildItem images
```

然后重新运行：

```powershell
.\.venv\Scripts\python.exe caption.py images/test.jpg
```

### 2. `Unable to read image file`

说明文件存在，但不是有效图片，或者图片已损坏。建议换成正常的 JPG 或 PNG。

### 3. `Failed to load BLIP model`

通常表示模型下载失败，常见原因有：

- 当前网络无法访问 Hugging Face
- 代理没有配置好
- 第一次下载被中断

可以先检查网络，再重新运行脚本。

### 4. 激活虚拟环境时报权限错误

这是 Windows PowerShell 常见情况。可以使用下面两种方式之一：

- 临时设置执行策略：`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
- 不激活环境，直接运行：`.\.venv\Scripts\python.exe caption.py images/test.jpg`

### 5. 运行很慢

第一次运行通常最慢，因为要下载模型。没有 GPU 时，CPU 推理也会比 GPU 慢一些，这是正常现象。

## 代码说明

`caption.py` 做了这几件事：

- 从命令行读取图片路径
- 用 `PIL` 打开图片
- 使用 `BlipProcessor` 和 `BlipForConditionalGeneration` 加载模型
- 自动选择 GPU 或 CPU
- 输出生成的 caption
- 对图片不存在、图片损坏、模型加载失败等情况给出清晰提示

## 下一步可以做什么

如果你想从图像描述继续扩展，最自然的下一步就是视觉问答（VQA）：

1. 新建 `vqa.py`
2. 把输入从“只有图片”改成“图片 + 问题文本”
3. 使用 BLIP 的 VQA 模型，例如 `Salesforce/blip-vqa-base`
4. 运行方式改成类似：

```powershell
.\.venv\Scripts\python.exe vqa.py images/test.jpg "What is the person holding?"
```

这样就能从“给整张图一句描述”扩展到“针对图片回答具体问题”。


## 实验结果示例

本项目使用 `Salesforce/blip-image-captioning-base` 模型对多张本地图片进行图像描述实验。以下为部分测试结果：

| 图片名 | 模型输出 | 评价 |
|---|---|---|
| `cat.jpg` | `a gray cat sitting on top of a wooden table` | 描述较准确，能够识别主体“cat”以及所处位置“wooden table” |
| `lake.jpg` | `a body of water` | 能识别出水域场景，但描述较为笼统，缺少更多细节 |
| `blackboard.jpg` | `a blackboard with many equations written on it` | 描述较准确，能够识别黑板以及上面的公式信息 |
| `mcdonald.jpg` | `a tray with food and drinks on it` | 对餐饮场景识别较好，抓住了托盘、食物和饮料等关键元素 |
| `aircraft window.jpg` | `a view of a city from an airplane window` | 描述效果较好，能够识别“airplane window”以及窗外城市景象 |

## 实验结果分析

从目前的实验结果来看，BLIP 在图像描述任务中表现出了较好的基础视觉-语言理解能力。

1. 对于**主体明确、场景集中的图片**，模型通常能够生成较准确的描述。  
   例如 `cat.jpg`、`blackboard.jpg` 和 `mcdonald.jpg` 的结果都比较自然，并且抓住了图像中的主要对象和场景信息。

2. 对于**风景类或大场景图片**，模型虽然能够识别大致类别，但描述会偏向概括化。  
   例如 `lake.jpg` 的输出仅为 `a body of water`，说明模型捕捉到了核心场景，但细节表达能力仍然有限。

3. 对于**带有明显视角特征的图片**，模型也能较好地进行描述。  
   例如 `aircraft window.jpg` 的输出不仅识别出城市，还识别出了“from an airplane window”这一观察视角，说明模型在部分场景关系理解上表现较好。

## 初步结论

本次实验表明，BLIP 可以较稳定地完成基础图像描述任务，尤其在主体清晰、语义明确的图片上表现较好。但在复杂风景场景中，模型输出仍可能较为笼统，细节表达能力有待进一步观察和改进。


