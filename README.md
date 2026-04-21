# BLIP 图像描述实验项目

这是一个基于 Hugging Face `Salesforce/blip-image-captioning-base` 的图像描述实验项目。

本项目以 Flickr8k 数据集为实验对象，围绕 **单图 caption 生成、批量实验、代表样本筛选与生成策略比较** 搭建了一个可运行、可分析、可扩展的多模态视觉入门实验流程。项目重点不在于重新训练模型，而在于观察预训练图像描述模型在真实数据集上的表现，并通过结果分析逐步推进后续改进。

---

## 1. 项目内容

当前项目主要完成了以下工作：

- 对单张本地图片生成 caption
- 在 Flickr8k 数据集上进行批量推理
- 将模型输出与 5 条人工 captions 保存到 CSV
- 基于 simple F1 与人工复核筛选代表样本
- 在代表样本上比较不同生成策略的效果

---

## 2. 项目功能

当前项目支持：

- 使用 BLIP 模型对单张图片生成描述
- 自动选择 GPU 或 CPU 进行推理
- 对 Flickr8k 进行批量 caption 生成
- 保存模型输出与人工 captions 的对比结果
- 构造好 / 中 / 差三类代表样本
- 比较不同 decoding 参数对 caption 结果的影响

---

## 3. 项目结构

```text
BLIP/
├─ .gitignore
├─ README.md
├─ requirements.txt
├─ caption.py
├─ run_flickr8k_batch.py
├─ select_samples_by_f1.py
├─ export_final_samples.py
├─ run_generation_strategy_experiments.py
├─ compare_captions.py
├─ docs/
│  ├─ sample_selection.md
│  └─ generation_strategy_experiments.md
├─ results/
│  ├─ .gitkeep
│  ├─ results.csv
│  ├─ sample_selection/
│  │  ├─ all_with_best_f1.csv
│  │  ├─ good_candidates.csv
│  │  ├─ medium_candidates.csv
│  │  └─ bad_candidates.csv
│  ├─ final_samples/
│  │  ├─ final_good_samples.csv
│  │  ├─ final_medium_samples.csv
│  │  ├─ final_bad_samples.csv
│  │  ├─ final_all_samples.csv
│  │  ├─ good/
│  │  ├─ medium/
│  │  └─ bad/
│  └─ strategy_experiments/
│     ├─ strategy_results_long.csv
│     ├─ strategy_results_wide.csv
│     └─ strategy_summary.csv
├─ data/
│  ├─ captions.txt
│  └─ images/
└─ .venv/
````

各主要文件作用如下：

* `caption.py`：对单张图片生成 caption
* `run_flickr8k_batch.py`：批量处理 Flickr8k 图片并保存结果
* `select_samples_by_f1.py`：计算 simple F1 并导出候选样本
* `export_final_samples.py`：导出最终代表样本并复制对应图片
* `run_generation_strategy_experiments.py`：对最终样本运行不同生成策略
* `compare_captions.py`：辅助查看模型输出与人工 captions 的差异
* `docs/sample_selection.md`：记录代表样本筛选思路与结果
* `docs/generation_strategy_experiments.md`：记录生成策略实验设计与结论

---

## 4. 环境配置

建议使用虚拟环境。

### 4.1 创建虚拟环境

```powershell
py -3.12 -m venv .venv
```

### 4.2 激活虚拟环境

```powershell
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 提示执行权限问题，可以先运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

然后再次执行激活命令。

### 4.3 安装依赖

```powershell
python -m pip install -r requirements.txt
```

如果你希望使用 GPU，需要安装与本机 CUDA 兼容的 PyTorch 版本。

---

## 5. 使用方法

### 5.1 单张图片生成 caption

```powershell
python caption.py data/images/1000268201_693b08cb0e.jpg
```

运行成功后，会输出一条图像描述，例如：

```text
a little girl in a pink dress
```

---

### 5.2 Flickr8k 批量实验

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

### 5.3 代表样本筛选

先根据批量实验结果计算 simple F1 并导出候选样本：

```powershell
python select_samples_by_f1.py
```

再根据人工确认的名单导出最终代表样本：

```powershell
python export_final_samples.py
```

运行后会生成：

```text
results/final_samples/final_good_samples.csv
results/final_samples/final_medium_samples.csv
results/final_samples/final_bad_samples.csv
results/final_samples/final_all_samples.csv
```

并将对应图片复制到：

```text
results/final_samples/good/
results/final_samples/medium/
results/final_samples/bad/
```

---

### 5.4 生成策略实验

在最终代表样本上比较不同生成参数：

```powershell
python run_generation_strategy_experiments.py
```

当前实验比较了三种设置：

* `baseline`：`max_new_tokens=20`
* `exp1_longer`：`max_new_tokens=30`
* `exp2_beam5`：`num_beams=5, max_new_tokens=30`

运行完成后，结果会保存到：

```text
results/strategy_experiments/strategy_results_long.csv
results/strategy_experiments/strategy_results_wide.csv
results/strategy_experiments/strategy_summary.csv
```

---

## 6. 批量实验结果示例

以图片 `1000268201_693b08cb0e.jpg` 为例：

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

从这个例子可以看出，BLIP 能较好识别图片中的主体和关键属性，但输出通常较短，容易省略动作和场景细节。

---

## 7. 当前实验结论

在 Flickr8k 数据集上的批量实验中，BLIP 对主体明确、场景典型的图片通常能够给出较准确的描述；但整体输出偏短，常常省略动作、人物关系、数量信息和背景细节。在复杂场景中，模型更容易生成较泛化的表述，或者被背景信息带偏。

在代表样本上的生成策略比较中，还得到以下结果：

* 单纯增大 `max_new_tokens` 基本没有带来实质改进
* 引入 `num_beams=5` 后，整体词面匹配分数有一定提升
* beam search 的提升主要体现在原本生成较差的样本上
* 对原本已经生成较好的样本，beam search 有时会把准确描述改写成更泛化的表达

因此，beam search 更适合作为困难样本上的补充策略，而不是对 baseline 的统一替代。

---

## 8. 文档说明

为了避免 README 过长，项目将较详细的实验说明拆分到了 `docs/` 目录下：

* `docs/sample_selection.md`：代表样本筛选流程、simple F1 定义、人工复核标准与最终样本说明
* `docs/generation_strategy_experiments.md`：生成策略实验设计、结果汇总与典型样本分析

README 主要保留项目总览、核心流程和关键结论。

---

## 9. 项目定位

本项目的重点不在于从零训练模型，而在于：

* 搭建一个完整可运行的多模态实验流程
* 观察预训练图像描述模型在真实数据集上的表现
* 通过样本分析和小规模实验提出改进方向
* 为后续扩展到更复杂的多模态任务打下基础

因此，这个项目更适合作为多模态视觉任务的入门实验与后续扩展基础。