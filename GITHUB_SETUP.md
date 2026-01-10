# GitHub 發布指南

## 📋 發布前準備

### 1. 檢查項目狀態

確保以下文件已準備好：
- ✅ `.gitignore` - Git 忽略文件配置
- ✅ `README.md` - 項目說明文檔
- ✅ `requirements.txt` - Python 依賴列表
- ✅ 所有源代碼文件

### 2. 初始化 Git 倉庫

如果還沒有初始化 Git 倉庫，請執行：

```bash
# 初始化 Git 倉庫
git init

# 添加所有文件
git add .

# 創建初始提交
git commit -m "Initial commit: Bazi Streamlit App with personality matrix analysis"
```

### 3. 配置 Git 用戶信息（如果尚未配置）

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## 🚀 發布到 GitHub

### 方法一：使用 GitHub CLI（推薦）

```bash
# 安裝 GitHub CLI（如果尚未安裝）
# Windows: winget install GitHub.cli
# macOS: brew install gh
# Linux: 參考 https://cli.github.com/

# 登錄 GitHub
gh auth login

# 創建倉庫並推送
gh repo create bazi-streamlit-app --public --source=. --remote=origin --push
```

### 方法二：使用網頁界面

1. **創建新倉庫**
   - 訪問 https://github.com/new
   - 填寫倉庫名稱（例如：`bazi-streamlit-app`）
   - 選擇公開（Public）或私有（Private）
   - **不要**初始化 README、.gitignore 或 license（因為我們已經有了）

2. **連接本地倉庫**

```bash
# 添加遠程倉庫
git remote add origin https://github.com/YOUR_USERNAME/bazi-streamlit-app.git

# 重命名主分支為 main（如果使用的是 master）
git branch -M main

# 推送代碼
git push -u origin main
```

### 方法三：使用 SSH（推薦用於頻繁推送）

```bash
# 生成 SSH 密鑰（如果還沒有）
ssh-keygen -t ed25519 -C "your.email@example.com"

# 將公鑰添加到 GitHub
# 複製 ~/.ssh/id_ed25519.pub 的內容
# 在 GitHub Settings > SSH and GPG keys 中添加

# 使用 SSH URL 添加遠程倉庫
git remote add origin git@github.com:YOUR_USERNAME/bazi-streamlit-app.git

# 推送代碼
git push -u origin main
```

## 📝 提交規範

建議使用清晰的提交信息：

```bash
# 功能添加
git commit -m "feat: 添加 12月令×12時辰 人格分析功能"

# 修復問題
git commit -m "fix: 修復午月戌時格式問題"

# 文檔更新
git commit -m "docs: 更新 README 添加人格分析說明"

# 代碼優化
git commit -m "refactor: 優化 personality_matrix 結構"
```

## 🔄 後續更新

```bash
# 查看變更
git status

# 添加變更
git add .

# 提交變更
git commit -m "描述變更內容"

# 推送到 GitHub
git push
```

## 📦 發布版本

創建版本標籤：

```bash
# 創建標籤
git tag -a v1.0.0 -m "第一個版本：包含完整的人格分析功能"

# 推送標籤
git push origin v1.0.0
```

在 GitHub 上：
1. 訪問 Releases 頁面
2. 點擊 "Draft a new release"
3. 選擇標籤並填寫發布說明

## 🌐 Streamlit Cloud 部署（可選）

如果要在 Streamlit Cloud 上部署：

1. 訪問 https://streamlit.io/cloud
2. 連接 GitHub 帳號
3. 選擇倉庫
4. 設置主文件路徑：`streamlit_app.py`
5. 點擊 Deploy

## 📚 相關資源

- [Git 官方文檔](https://git-scm.com/doc)
- [GitHub 文檔](https://docs.github.com/)
- [Streamlit 部署指南](https://docs.streamlit.io/streamlit-cloud)

## ⚠️ 注意事項

1. **不要提交敏感信息**
   - 檢查 `.gitignore` 是否包含 `.env`、`secrets.toml` 等
   - 不要提交 API 密鑰或個人信息

2. **檢查文件大小**
   - GitHub 限制單個文件 100MB
   - 大文件應使用 Git LFS

3. **許可證**
   - 考慮添加 LICENSE 文件
   - 明確項目的使用條款

4. **文檔完整性**
   - 確保 README.md 包含足夠的使用說明
   - 添加必要的示例和截圖

---

**祝發布順利！** 🎉

