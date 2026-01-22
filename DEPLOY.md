# 部署指南

## 🌐 Streamlit Cloud 部署

### 步骤1：准备GitHub仓库

1. 在GitHub上创建新仓库
2. 将代码推送到仓库：

```bash
git init
git add .
git commit -m "Initial commit: 锡期现交割成本测算模型"
git branch -M main
git remote add origin https://github.com/your-username/your-repo-name.git
git push -u origin main
```

### 步骤2：部署到Streamlit Cloud

1. 访问 [Streamlit Cloud](https://share.streamlit.io/)
2. 使用GitHub账号登录
3. 点击 "New app"
4. 填写信息：
   - **Repository**: 选择你的仓库
   - **Branch**: main（或master）
   - **Main file path**: `web_app.py`
5. 点击 "Deploy"

### 步骤3：访问应用

部署完成后，Streamlit Cloud会生成一个公开URL，格式：
```
https://your-app-name.streamlit.app
```

你可以：
- 分享这个URL给其他人
- 在任何设备上访问
- 无需本地安装任何软件

## 🔧 配置说明

### requirements.txt

确保 `requirements.txt` 包含所有必需的依赖：

```
pandas>=1.3.0
openpyxl>=3.0.0
PyPDF2>=3.0.0
python-docx>=0.8.11
streamlit>=1.28.0
plotly>=5.17.0
```

### .streamlit/config.toml

配置文件已包含在项目中，用于设置Streamlit主题和服务器配置。

## 🐛 常见问题

### 1. 部署失败

- 检查 `requirements.txt` 是否正确
- 确保 `web_app.py` 在根目录
- 检查Python版本（Streamlit Cloud支持Python 3.7+）

### 2. 模块导入错误

- 确保所有依赖都在 `requirements.txt` 中
- 检查导入路径是否正确

### 3. 应用无法访问

- 检查部署日志
- 确保代码没有语法错误
- 检查Streamlit Cloud的状态页面

## 📝 更新应用

每次推送代码到GitHub后，Streamlit Cloud会自动重新部署：

```bash
git add .
git commit -m "Update: 描述你的更改"
git push
```

## 🔒 隐私和安全

- Streamlit Cloud免费版的应用是公开的
- 如果需要私有部署，考虑使用Streamlit Cloud的付费版本
- 或者使用其他云服务（如Heroku、AWS等）

## 💡 提示

- 首次部署可能需要几分钟时间
- 建议在本地测试通过后再部署
- 定期更新依赖包以保持安全性
