# Streamlit 应用部署指南

## 为什么应用不会自动更新？

### 常见原因：

1. **Streamlit Cloud 设置问题**
   - Auto-deploy 未启用
   - 连接了错误的分支
   - 文件路径配置错误

2. **本地运行**
   - 需要手动 `git pull` 和重启

3. **缓存问题**
   - Streamlit 可能缓存了旧版本

## 解决方案

### 方案 1：Streamlit Cloud 自动部署（推荐）

#### 步骤 1：检查 Streamlit Cloud 设置

1. 登录 [Streamlit Cloud](https://share.streamlit.io/)
2. 进入你的应用设置
3. 确认以下设置：

```
Repository: fantasy-library/bazi
Branch: main
Main file: streamlit_app.py
Python version: 3.10+
Auto-deploy: Always redeploy
```

#### 步骤 2：确保 GitHub 仓库设置正确

- 确保仓库是公开的（Public），或已授权 Streamlit Cloud 访问
- 确保 `main` 分支包含最新的 `streamlit_app.py`

#### 步骤 3：手动触发重新部署

如果自动部署未触发，可以：

1. 在 Streamlit Cloud 控制台点击 "Reboot app"
2. 或者在 GitHub 仓库中创建一个空提交来触发部署：
   ```bash
   git commit --allow-empty -m "Trigger redeploy"
   git push
   ```

### 方案 2：本地运行和更新

#### 更新应用：

```bash
# 1. 拉取最新代码
cd bazi-master
git pull origin main

# 2. 重启 Streamlit 应用
# 按 Ctrl+C 停止当前应用，然后：
streamlit run streamlit_app.py
```

#### 或者使用 Python 模块方式：

```bash
python -m streamlit run streamlit_app.py
```

### 方案 3：使用 GitHub Actions 自动部署（高级）

如果需要更复杂的 CI/CD，可以创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy Streamlit App

on:
  push:
    branches: [ main ]
    paths:
      - 'streamlit_app.py'
      - 'requirements.txt'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Deploy to Streamlit Cloud
        # 这里需要配置 Streamlit Cloud 的部署方式
```

## 故障排除

### 问题 1：应用显示旧版本

**解决方案**：
- 清除浏览器缓存（Ctrl+Shift+Delete）
- 在 Streamlit Cloud 点击 "Reboot app"
- 检查是否推送到正确的分支

### 问题 2：更改未生效

**解决方案**：
- 确认文件已保存并推送到 GitHub
- 检查 Streamlit Cloud 的部署日志
- 查看是否有错误信息

### 问题 3：依赖问题

**解决方案**：
- 检查 `requirements.txt` 是否包含所有依赖
- 确认 Python 版本兼容性
- 查看 Streamlit Cloud 的构建日志

## 验证部署

1. **检查 GitHub 提交**：确认最新更改已推送到 `main` 分支
2. **检查 Streamlit Cloud 日志**：查看最近的部署活动
3. **测试应用**：访问应用 URL，确认更改已生效

## 快速检查清单

- [ ] 代码已推送到 GitHub `main` 分支
- [ ] Streamlit Cloud 连接到正确的仓库和分支
- [ ] Auto-deploy 设置为 "Always redeploy"
- [ ] `streamlit_app.py` 路径正确
- [ ] `requirements.txt` 包含所有依赖
- [ ] 没有构建错误（检查 Streamlit Cloud 日志）

## 联系支持

如果问题持续存在：
1. 查看 [Streamlit Cloud 文档](https://docs.streamlit.io/streamlit-cloud)
2. 检查 [Streamlit 社区论坛](https://discuss.streamlit.io/)
3. 查看 GitHub Issues





