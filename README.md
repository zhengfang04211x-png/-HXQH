# 锡（Sn）期现交割成本测算模型

一个基于Python和Streamlit的锡期货期现套利成本测算工具，支持动态保证金计算、成本明细分析和套利机会判断。

## 🌟 功能特点

- 📊 **交互式Web界面**：基于Streamlit构建，操作简单直观
- 🔢 **自动日期计算**：根据合约代码自动生成相关日期
- 💰 **动态保证金计算**：支持多阶段保证金比例动态计算
- 📈 **成本明细分析**：详细展示每吨成本和总成本
- 🎯 **套利判断**：自动计算套利机会和盈亏平衡点
- ⚙️ **参数可配置**：所有费用参数均可自定义

## 🚀 快速开始

### 方法1：本地运行（推荐）

1. **克隆仓库**
```bash
git clone <your-repo-url>
cd 锡
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行Web应用**
```bash
streamlit run web_app.py
```

浏览器会自动打开 `http://localhost:8501`

### 方法2：Streamlit Cloud部署（异地查看）

1. **准备GitHub仓库**
   - 将代码推送到GitHub
   - 确保 `requirements.txt` 和 `web_app.py` 在根目录

2. **部署到Streamlit Cloud**
   - 访问 [Streamlit Cloud](https://streamlit.io/cloud)
   - 使用GitHub账号登录
   - 点击 "New app"
   - 选择你的仓库和 `web_app.py` 文件
   - 点击 "Deploy"

3. **访问应用**
   - 部署完成后，会生成一个公开的URL
   - 可以通过该URL在任何地方访问应用

## 📁 项目结构

```
锡/
├── web_app.py                          # Streamlit Web应用主文件
├── tin_delivery_cost_calculator.py     # 核心计算模块
├── tin_params_config.py                # 参数配置文件
├── extract_tin_params.py               # 参数提取工具（可选）
├── requirements.txt                    # Python依赖包
├── .streamlit/
│   └── config.toml                     # Streamlit配置
├── README.md                           # 项目说明文档
└── .gitignore                          # Git忽略文件
```

## 📋 使用说明

### 基础参数设置

1. **现货价格**：输入当前现货市场价格（元/吨）
2. **期货价格**：输入期货合约价格（元/吨）
3. **数量**：输入交割数量（吨）

### 合约和时间设置

1. **合约代码**：输入合约代码，如 `sn2603`
   - 系统会自动识别交割日为2026年3月15日
   - 自动生成相关日期（合约挂牌日期、保证金时间点等）

2. **开始日期**：买入现货的日期

3. **交割日期**：合约交割日（可手动调整，如遇法定假日）

### 资金参数

- **资金利率**：年化资金成本利率（默认5%）
- **企业保证金加收比例**：企业额外保证金比例

### 保证金比例设置

支持四个阶段的动态保证金比例：
- **第一阶段**：合约挂牌之日起（默认5%）
- **第二阶段**：交割月前第一月的第一个交易日起（默认10%）
- **第三阶段**：交割月份第一个交易日起（默认15%）
- **第四阶段**：最后交易日前二个交易日起（默认20%）

### 入库/出库方式

- **入库方式**：专用线、非箱式车辆自送、箱式车自送
- **出库方式**：专用线、非箱式车辆自提、箱式车辆自提

### 代办费用（可选）

- **代办车皮申请**：5元/吨
- **代办提运**：2元/吨

## 📊 输出结果

### 第一部分：每吨各项成本

显示每吨的各项成本明细：
- 现货成本（含税）
- 交割杂费
- 仓储费
- 资金成本（现货+期货）

### 第二部分：资金需求

- **购买现货需要资金**：现货价格 × 数量 × (1 + 增值税率)
- **购买期货需要资金（保证金）**：现货价格 × 数量 × 保证金比例
- **总资金需求**：两者之和

### 第三部分：按数量计算总成本

- 总成本明细
- 套利判断结果（可以套利/无法套利）
- 预期利润/亏损
- 关键指标

## 🔧 技术栈

- **Python 3.7+**
- **Streamlit**：Web应用框架
- **Pandas**：数据处理
- **Plotly**：数据可视化（可选）

## 📝 依赖包

所有依赖包都在 `requirements.txt` 中：

```
pandas>=1.3.0
openpyxl>=3.0.0
PyPDF2>=3.0.0
python-docx>=0.8.11
streamlit>=1.28.0
plotly>=5.17.0
```

## 🌐 部署说明

### Streamlit Cloud部署步骤

1. **创建GitHub仓库**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **在Streamlit Cloud部署**
   - 访问 https://share.streamlit.io/
   - 使用GitHub账号登录
   - 点击 "New app"
   - 选择仓库和主文件 `web_app.py`
   - 点击 "Deploy"

3. **访问应用**
   - 部署完成后会生成公开URL
   - 格式：`https://your-app-name.streamlit.app`

### 本地部署

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run web_app.py
```

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

如有问题或建议，请通过GitHub Issues联系。

---

**注意**：本项目基于多晶硅套利表逻辑适配，所有参数请根据实际情况调整。
