# Generation Strategy Experiments

## 1. 实验目的

在已经筛选出的 30 张代表性样本（good / medium / bad）上，对 BLIP 的不同生成策略进行对比，观察以下问题：

1. 单纯增大最大生成长度，是否能够补充更多细节并提升 caption 质量；
2. 引入 beam search 后，是否能够改善困难样本上的生成结果；
3. 不同策略对好样本和差样本的影响是否一致。

本实验希望在不改动模型权重的前提下，评估简单 decoding 调整是否值得保留到后续流程中。

---

## 2. 实验设置

### 2.1 数据

- 数据来源：Flickr8k
- 评估样本：30 张最终代表样本
  - good：5 张
  - medium：10 张
  - bad：15 张

### 2.2 模型

- 模型：`Salesforce/blip-image-captioning-base`

### 2.3 对比策略

1. **baseline**
   - `max_new_tokens=20`
   - `num_beams=1`

2. **exp1_longer**
   - `max_new_tokens=30`
   - `num_beams=1`

3. **exp2_beam5**
   - `max_new_tokens=30`
   - `num_beams=5`
   - `early_stopping=True`

### 2.4 评价方式

采用 simple F1 作为快速对比指标。对每张图片，分别将生成 caption 与该图片对应的 5 条人工 caption 进行词级比较，取其中最高值作为该样本的 `best_f1`。

需要说明的是，simple F1 只能反映生成结果与人工标注之间的词汇重合程度，并不能完全代表语义是否正确，因此在分析时还结合了部分个例进行人工判断。

---

## 3. 实验结果

### 3.1 总体结果

三种策略的总体平均 `best_f1` 如下：

| Strategy | Overall mean best_f1 |
|---|---:|
| baseline | 0.3601 |
| exp1_longer | 0.3601 |
| exp2_beam5 | 0.3897 |

从整体结果看：

- `exp1_longer` 与 `baseline` 基本一致；
- `exp2_beam5` 相比 `baseline` 有小幅提升。

### 3.2 分组结果

| Group | baseline | exp1_longer | exp2_beam5 |
|---|---:|---:|---:|
| good | 1.0000 | 1.0000 | 0.8341 |
| medium | 0.5000 | 0.5000 | 0.4802 |
| bad | 0.0535 | 0.0535 | 0.1813 |

从分组结果可以看出：

- 在 **good** 样本上，`baseline` 已经表现很好，beam search 反而可能带来退化；
- 在 **medium** 样本上，beam search 效果不稳定，整体没有明显优势；
- 在 **bad** 样本上，`exp2_beam5` 的提升最明显，说明 beam search 对困难样本有一定纠偏作用。

### 3.3 逐样本比较

以 `baseline` 为参照：

- `exp1_longer`：
  - 30 张样本中，`best_f1` **全部相同**；
  - 30 张样本中，有 **29 张 caption 完全相同**。

- `exp2_beam5`：
  - 更好：8 张
  - 一样：15 张
  - 更差：7 张

这说明：

- 单纯把 `max_new_tokens` 从 20 增加到 30，几乎没有带来实质变化；
- beam search 并不是对所有样本都更优，而是对一部分困难样本有效，但也可能破坏原本已经正确的结果。

---

## 4. 个例分析

### 4.1 beam search 改善较明显的样本

#### 示例 1
- image: `3209620285_edfc479392.jpg`
- baseline: `a man holding a baseball bat`
- exp2_beam5: `two people playing baseball on the beach`
- `best_f1`: `0.0000 -> 0.4444`

该样本中，baseline 对场景理解明显失配，只抓到一个模糊主体；beam search 至少补充出了 `two people` 和 `beach` 等信息，使结果在词汇层面更接近人工描述。不过，这条 caption 仍存在语义偏差，说明自动指标提升不一定等价于语义完全正确。

#### 示例 2
- image: `2529205842_bdcb49d65b.jpg`
- baseline: `a man wearing a black shirt`
- exp2_beam5: `two boys playing basketball`
- `best_f1`: `0.1111 -> 0.4286`

该样本中，beam search 较好地抓住了人数关系和运动类型，相比 baseline 的泛化描述更接近参考 caption，属于较为有效的改进。

#### 示例 3
- image: `2723477522_d89f5ac62b.jpg`
- baseline: `a dog chasing a dog`
- exp2_beam5: `two dogs running in the grass`
- `best_f1`: `0.5000 -> 0.8333`

这里 beam search 生成的句子更加自然，也补充了场景信息，属于中等样本上比较成功的例子。

### 4.2 beam search 退化的样本

#### 示例 4
- image: `1662261486_db967930de.jpg`
- baseline: `a dog jumping through a ring`
- exp2_beam5: `a dog jumping in the air`
- `best_f1`: `1.0000 -> 0.5455`

该样本中，baseline 已经准确抓住了关键对象 `ring`，而 beam search 将其泛化为更普通的空中跳跃，导致细节丢失。

#### 示例 5
- image: `2710698257_2e4ca8dd44.jpg`
- baseline: `a man standing on a cliff`
- exp2_beam5: `the sky is clear and blue`
- `best_f1`: `0.5000 -> 0.2353`

该样本中，beam search 的注意力偏向背景描述，忽略了图片中的主体人物和动作，导致 caption 质量下降。

---

## 5. 结果讨论

### 5.1 单纯增大生成长度基本无效

实验结果表明，`exp1_longer` 与 `baseline` 的总体分数完全一致，且绝大多数样本的生成文本也完全相同。这说明当前模型输出较短，并不是因为 `max_new_tokens=20` 过小，而更可能是模型在现有解码路径下已经提前结束生成。因此，后续不必继续把主要精力放在单纯增大生成长度上。

### 5.2 beam search 更像“困难样本纠偏”，而不是“统一增强”

`exp2_beam5` 在总体上略优于 baseline，但这种提升主要集中在 bad 样本中。对于原本表现较差、容易偏题或抓不住主体的图片，beam search 确实有一定帮助；但对于已经生成正确的 good 样本，它反而可能把关键细节替换成更泛化的表达。因此，beam search 更适合作为困难样本上的补充策略，而不宜简单视为 baseline 的统一替代方案。

### 5.3 自动指标需要结合人工判断

部分个例表明，simple F1 的提升有时来自更高的词汇重合度，而不一定意味着语义完全正确。因此，在后续分析中应将自动指标与人工个例分析结合起来，避免仅根据数值变化得出过强结论。

---

## 6. 结论

本次生成策略实验可以得到以下结论：

1. 单纯将 `max_new_tokens` 从 20 提高到 30，基本没有带来可观察的质量提升；
2. 引入 `num_beams=5` 后，整体 `best_f1` 从 0.3601 提高到 0.3897，说明 beam search 在部分样本上具有一定积极作用；
3. beam search 的改进主要集中在 bad 样本中，对困难样本有一定纠偏能力；
4. 对于原本已经生成较准确的 good 样本，beam search 可能引入更泛化的表达，反而损失关键细节；
5. 因此，beam search 更适合作为补充性策略，而不是直接替代 baseline 的统一设置。

一句话概括本次实验结果：

> 增大生成长度基本无效；beam search 对难样本有一定帮助，但稳定性不足，并可能牺牲原本已正确样本的精确性。

---

## 7. 后续工作

基于当前结果，后续可以考虑：

1. 继续尝试更系统的 decoding 设置，而不是只调整 `max_new_tokens`；
2. 增加人工复核，以补充 simple F1 在语义判断上的不足；
3. 若希望获得更稳定的提升，可以进一步尝试针对 Flickr8k 的轻量微调，而不是仅依赖推理阶段的参数调整。

---

## 8. 相关输出文件

本实验对应输出文件如下：

- `results/strategy_experiments/strategy_results_long.csv`
- `results/strategy_experiments/strategy_results_wide.csv`
- `results/strategy_experiments/strategy_summary.csv`

建议将本文档保存在：

- `docs/generation_strategy_experiments.md`

便于后续在 README、项目汇报或与老师交流时直接引用。
