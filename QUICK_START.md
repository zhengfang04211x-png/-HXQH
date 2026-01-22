# 🚀 快速部署指南

## 一键部署到Streamlit Cloud

### 步骤1：准备代码

确保以下文件在项目根目录：

```
✅ web_app.py                    # Web应用主文件
✅ tin_delivery_cost_calculator.py  # 计算模块
✅ tin_params_config.py          # 配置文件
✅ requirements.txt               # 依赖包
✅ .streamlit/config.toml        # Streamlit配置
```

### 步骤2：创建GitHub仓库

1. 登录GitHub
2. 点击右上角 "+" → "New repository"
3. 填写仓库名称（如：`tin-delivery-cost-calculator`）
4. 选择 Public（免费版Streamlit Cloud需要公开仓库）
5. 点击 "Create repository"

### 步骤3：上传代码

#### 方法A：使用Git命令行

```bash
# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 锡期现交割成本测算模型"

# 添加远程仓库（替换为你的仓库URL）
git remote add origin https://github.com/your-username/your-repo-name.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

#### 方法B：使用GitHub Desktop

1. 下载并安装 [GitHub Desktop](https://desktop.github.com/)
2. 登录GitHub账号
3. 点击 "File" → "Add Local Repository"
4. 选择项目文件夹
5. 填写提交信息
6. 点击 "Publish repository"

#### 方法C：使用GitHub网页上传

1. 在GitHub仓库页面点击 "uploading an existing file"
2. 拖拽所有文件到页面
3. 填写提交信息
4. 点击 "Commit changes"

### 步骤4：部署到Streamlit Cloud

1. 访问 [Streamlit Cloud](https://share.streamlit.io/)
2. 点击 "Sign in" 使用GitHub账号登录
3. 点击 "New app"
4. 填写信息：
   - **Repository**: 选择你的仓库
   - **Branch**: `main`（或`master`）
   - **Main file path**: `web_app.py`
5. 点击 "Deploy"

### 步骤5：访问应用

部署完成后（通常需要1-2分钟），你会看到：

- ✅ 应用URL（格式：`https://your-app-name.streamlit.app`）
- ✅ 可以分享给任何人访问
- ✅ 支持手机、平板、电脑访问

## 🔄 更新应用

每次修改代码后，只需推送到GitHub：

```bash
git add .
git commit -m "Update: 描述你的更改"
git push
```

Streamlit Cloud会自动检测更改并重新部署（通常需要1-2分钟）。

## 📱 分享应用

部署完成后，你可以：

1. **分享URL**：直接发送应用URL给其他人
2. **嵌入网页**：使用iframe嵌入到其他网站
3. **收藏书签**：保存到浏览器书签

## ⚠️ 注意事项

1. **免费版限制**：
   - 应用必须是公开的
   - 有资源使用限制
   - 适合个人和小型项目

2. **私有部署**：
   - 如需私有部署，考虑付费版Streamlit Cloud
   - 或使用其他云服务（Heroku、AWS等）

3. **文件大小**：
   - 避免上传大型数据文件
   - 使用`.gitignore`排除不需要的文件

## 🐛 常见问题

### Q: 部署失败怎么办？
A: 检查：
- `requirements.txt`是否正确
- `web_app.py`是否在根目录
- 代码是否有语法错误

### Q: 如何查看部署日志？
A: 在Streamlit Cloud页面点击应用，查看"Manage app" → "Logs"

### Q: 如何停止应用？
A: 在Streamlit Cloud页面点击"Settings" → "Delete app"

## 📞 需要帮助？

- 查看 [DEPLOY.md](DEPLOY.md) 获取详细部署说明
- 查看 [README.md](README.md) 了解项目详情
- 访问 [Streamlit文档](https://docs.streamlit.io/) 了解更多
