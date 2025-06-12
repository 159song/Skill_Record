# Markdown 完整使用指南

## 1. 标题

```markdown
# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题
```

## 2. 文本样式

### 基本样式
```markdown
*斜体文本* 或 _斜体文本_
**粗体文本** 或 __粗体文本__
***粗斜体文本*** 或 ___粗斜体文本___
~~删除线文本~~
```

### 引用
```markdown
> 这是一级引用
>> 这是二级引用
>>> 这是三级引用
```

## 3. 列表

### 无序列表
```markdown
- 项目1
- 项目2
  - 子项目2.1
  - 子项目2.2
* 项目3
+ 项目4
```

### 有序列表
```markdown
1. 第一项
2. 第二项
   1. 子项2.1
   2. 子项2.2
3. 第三项
```

### 任务列表
```markdown
- [x] 已完成任务
- [ ] 未完成任务
- [ ] 待办事项
```

## 4. 链接和图片

### 链接
```markdown
[链接文字](URL "可选标题")
[GitHub](https://github.com "访问GitHub")

参考式链接：
[链接文字][id]
[id]: URL "可选标题"
```

### 图片
```markdown
![替代文字](图片URL "可选标题")
![logo](https://example.com/logo.png "Logo")
```

## 5. 代码

### 行内代码
```markdown
这是一段包含 `行内代码` 的文本
```

### 代码块
````markdown
```python
def hello_world():
    print("Hello, World!")
```

```javascript
console.log("Hello, World!");
```
````

## 6. 表格

```markdown
| 表头1 | 表头2 | 表头3 |
|-------|:-----:|------:|
| 左对齐 | 居中  | 右对齐 |
| 内容   | 内容  | 内容   |
```

## 7. 分隔线

```markdown
---
***
___
```

## 8. 转义字符

```markdown
\* 星号
\` 反引号
\[ 方括号
\( 圆括号
\# 井号
\+ 加号
\- 减号
\. 点
\! 感叹号
```

## 9. 注脚

```markdown
这里是一段文字[^1]
[^1]: 这里是注脚的内容
```

## 10. HTML支持

```markdown
<span style="color: red;">红色文字</span>
<div align="center">居中文本</div>
<kbd>Ctrl</kbd>
```

## 11. 数学公式（需要支持LaTeX的编辑器）

```markdown
行内公式：$E = mc^2$

独立公式：
$$
\sum_{i=1}^n a_i = 0
$$
```

## 12. 目录生成

```markdown
[TOC]
或
[[TOC]]
（具体语法取决于编辑器支持）
```

## 13. 折叠内容

```markdown
<details>
<summary>点击展开</summary>

这里是折叠的内容
- 可以包含任何markdown语法
- 列表
- 代码等

</details>
```

## 14. 实际应用示例

### 文档标题示例
```markdown
# 项目名称

[![构建状态](https://travis-ci.org/username/repo.svg?branch=master)](https://travis-ci.org/username/repo)
[![版本](https://img.shields.io/npm/v/package.svg)](https://www.npmjs.com/package/package)

> 项目简短描述

## 安装
\`\`\`bash
npm install package-name
\`\`\`

## 使用方法
...
```

### 表格示例
| 功能 | 基本语法 | 效果 |
|------|----------|------|
| 粗体 | \*\*文本** | **文本** |
| 斜体 | \*文本* | *文本* |
| 链接 | \[文本](URL) | [文本](URL) |

## 注意事项

1. 不同的Markdown解析器可能对某些语法的支持程度不同
2. 某些平台（如GitHub）可能会禁用某些HTML标签
3. 数学公式需要特殊的支持（如MathJax）
4. 建议在标题后面留一个空行
5. 列表项内容较长时，建议使用4个空格或1个制表符缩进