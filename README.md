# BLIP 图像描述实验项目

这是一个基于 Hugging Face `Salesforce/blip-image-captioning-base` 的图像描述实验项目。

本项目主要完成了两部分内容：

1. 对单张本地图片生成 caption  
2. 在 Flickr8k 数据集上进行批量实验，并将模型输出与人工 captions 保存到 CSV 文件中

项目目标不是训练模型，而是完成一个可运行、可分析、可扩展的多模态视觉入门实验。

---

## 一、项目功能

当前项目支持：

- 使用 BLIP 模型对单张图片生成描述
- 自动选择 GPU 或 CPU 进行推理
- 在 Flickr8k 数据集上批量生成 caption
- 保存模型输出与人工 captions 的对比结果
- 为后续扩展到 VQA（视觉问答）提供基础

---

## 二、项目结构

```text
BLIP/
├─ .gitignore
├─ README.md
├─ requirements.txt
├─ caption.py
├─ run_flickr8k_batch.py
├─ results/
│  └─ results.csv
├─ data/
│  ├─ captions.txt
│  └─ images/
````

各文件作用如下：

* `caption.py`：对单张图片生成 caption
* `run_flickr8k_batch.py`：批量处理 Flickr8k 图片并保存结果
* `data/captions.txt`：Flickr8k 的人工标注文件
* `data/images/`：Flickr8k 图片数据
* `results/results.csv`：批量实验输出结果

---

## 三、环境配置

建议使用虚拟环境。

### 1. 创建虚拟环境

```powershell
py -3.12 -m venv .venv
```

### 2. 激活虚拟环境

```powershell
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 提示执行权限问题，可以先运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

然后再次激活虚拟环境。

### 3. 安装依赖

```powershell
python -m pip install -r requirements.txt
```

如果希望使用 GPU，需要安装支持 CUDA 的 PyTorch 版本。

---

## 四、使用方法

### 1. 单张图片生成 caption

示例命令：

```powershell
python caption.py data/images/1000268201_693b08cb0e.jpg
```

运行成功后会输出一条图像描述，例如：

```text
a little girl in a pink dress
```

---

### 2. Flickr8k 批量实验

先做小规模测试：

```powershell
python run_flickr8k_batch.py --limit 10
```

如果测试无误，再进行全量运行：

```powershell
python run_flickr8k_batch.py
```

运行完成后，结果会保存到：

```text
results/results.csv
```

结果表包含以下字段：

* `image_name`
* `blip_caption`
* `human_caption_1`
* `human_caption_2`
* `human_caption_3`
* `human_caption_4`
* `human_caption_5`

---

## 五、实验结果示例

### 图片：1000268201_693b08cb0e.jpg

**BLIP 输出：**

```text
a little girl in a pink dress
```

**人工 captions：**

1. A child in a pink dress is climbing up a set of stairs in an entry way .
2. A girl going into a wooden building .
3. A little girl climbing into a wooden playhouse .
4. A little girl climbing the stairs to her playhouse .
5. A little girl in a pink dress going into a wooden cabin .

**简单分析：**

BLIP 能较好识别图片中的主体和关键属性，如“小女孩”和“粉色裙子”；
但相比人工 captions，模型输出更短，缺少“爬楼梯”“进入木屋”等动作和场景细节。

---

## 六、初步实验结论

在 Flickr8k 数据集上的实验表明：

* 对主体明确、场景典型的图片，BLIP 通常能够给出较准确的描述
* 模型输出整体偏短，常常省略动作、关系和场景细节
* 在复杂场景下，模型有时会生成较泛化的描述
* 与人工 captions 相比，BLIP 更擅长抓住“主要对象”，但细节表达能力仍有限

---

## 七、后续改进方向

接下来可以继续从以下几个方向扩展：

1. 对代表性样本做更系统的误差分析
2. 调整生成参数，如 `max_new_tokens`、`num_beams`
3. 比较不同 BLIP 模型版本的效果
4. 尝试扩展到视觉问答（VQA）任务
5. 后续考虑在小规模数据集上进行微调实验

---

## 八、说明

本项目的重点不在于从零训练模型，而在于：

* 搭建一个完整可运行的多模态实验流程
* 观察模型在真实数据集上的表现
* 通过结果分析提出后续改进方向

因此，这个项目更适合作为多模态视觉任务的入门实验与后续扩展基础。

```
```
