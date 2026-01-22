# 项目结构说明

## 📁 推荐的项目结构

```
锡/
├── web_app.py                          # ⭐ Streamlit Web应用主文件（必需）
├── tin_delivery_cost_calculator.py     # ⭐ 核心计算模块（必需）
├── tin_params_config.py                # ⭐ 参数配置文件（必需）
├── requirements.txt                    # ⭐ Python依赖包（必需）
├── .streamlit/                         # Streamlit配置目录
│   └── config.toml                     # Streamlit配置文件
├── .gitignore                          # Git忽略文件
├── README.md                            # 项目说明文档
├── DEPLOY.md                           # 部署指南
├── PROJECT_STRUCTURE.md                 # 本文件
│
├── extract_tin_params.py               # 参数提取工具（可选）
├── update_tin_params.py                # 参数更新工具（可选）
├── example_usage.py                     # 使用示例（可选）
│
└── [其他文档和配置文件]
```

## 📋 文件说明

### ⭐ 必需文件（GitHub部署）

这些文件是Streamlit Cloud部署所必需的：

1. **web_app.py**
   - Streamlit应用的主入口文件
   - 必须位于项目根目录

2. **tin_delivery_cost_calculator.py**
   - 核心计算逻辑
   - 被web_app.py导入

3. **tin_params_config.py**
   - 参数配置文件
   - 被计算器模块导入

4. **requirements.txt**
   - Python依赖包列表
   - Streamlit Cloud会自动安装这些包

5. **.streamlit/config.toml**
   - Streamlit配置文件
   - 设置主题和服务器配置

### 📝 可选文件

这些文件有助于项目管理和使用，但不是部署必需的：

- `extract_tin_params.py` - 参数提取工具
- `update_tin_params.py` - 参数更新工具
- `example_usage.py` - 使用示例
- `README.md` - 项目说明
- `DEPLOY.md` - 部署指南
- `.gitignore` - Git忽略文件

## 🚀 最小化部署结构

如果只想部署Web应用，最小结构只需要：

```
锡/
├── web_app.py
├── tin_delivery_cost_calculator.py
├── tin_params_config.py
├── requirements.txt
└── .streamlit/
    └── config.toml
```

## 📦 打包说明

### 1. 清理不需要的文件

在推送到GitHub之前，可以删除：
- `__pycache__/` 目录
- `*.pyc` 文件
- 临时文件（`~$*.xlsx`等）
- 大型数据文件（如果不需要）

### 2. 确保必需文件存在

检查以下文件是否存在：
- ✅ `web_app.py`
- ✅ `tin_delivery_cost_calculator.py`
- ✅ `tin_params_config.py`
- ✅ `requirements.txt`

### 3. 检查导入路径

确保所有导入都是相对导入或标准库导入：
- ✅ `from tin_delivery_cost_calculator import ...`
- ✅ `import streamlit as st`
- ✅ `import pandas as pd`

## 🔍 验证清单

在部署前，请确认：

- [ ] `web_app.py` 在根目录
- [ ] `requirements.txt` 包含所有依赖
- [ ] 所有Python文件没有语法错误
- [ ] `.gitignore` 已配置
- [ ] `README.md` 已更新
- [ ] 测试本地运行：`streamlit run web_app.py`

## 📝 注意事项

1. **不要上传敏感信息**
   - 使用 `.gitignore` 排除敏感文件
   - 不要在代码中硬编码API密钥等

2. **文件大小限制**
   - GitHub单个文件限制100MB
   - Streamlit Cloud有资源限制

3. **依赖管理**
   - 确保 `requirements.txt` 中的版本号兼容
   - 避免使用过新的包版本

4. **路径问题**
   - 使用相对路径
   - 不要使用Windows特定的路径分隔符
