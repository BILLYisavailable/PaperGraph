# 快速开始指南 / Quick Start Guide

## 🎯 5分钟快速启动 / 5-Minute Quick Start

### 前提条件 / Prerequisites

✓ Python 3.9+ 已安装 (当前: 3.10.5)  
⚠ MySQL 8.0+ 需要安装  
⚠ Neo4j Desktop 需要安装  
⚠ Redis/Memurai 需要安装  

---

### 1️⃣ 安装依赖环境

下载并安装（如未安装）/ Download and install (if not installed):

1. MySQL: https://dev.mysql.com/downloads/installer/
2. Neo4j Desktop: https://neo4j.com/download/
3. Memurai (Redis for Windows): https://www.memurai.com/get-memurai
4. Node.js 16+ (for frontend): https://nodejs.org/

### 2️⃣ 一键配置后端环境

```cmd
setup.bat
```

这个脚本会自动完成 / This script will automatically:
- ✓ 创建虚拟环境
- ✓ 安装所有 Python 依赖
- ✓ 创建必要的目录

### 3️⃣ 配置数据库密码

```cmd
# 1. 复制配置文件
copy .env.example .env

# 2. 用记事本编辑 .env
notepad .env

# 3. 修改以下两行：
MYSQL_PASSWORD=你的MySQL密码
NEO4J_PASSWORD=你的Neo4j密码
```

### 4️⃣ 创建 MySQL 数据库

打开 MySQL 命令行 / Open MySQL Command Line:

```sql
CREATE DATABASE paper_kg CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 5️⃣ 启动 Neo4j

1. 打开 Neo4j Desktop
2. 创建一个新项目
3. 添加一个数据库
4. 点击 "Start" 启动数据库
5. 设置密码（与 .env 中的密码一致）

### 6️⃣ 启动 Memurai (Redis)

```cmd
net start Memurai
```

### 7️⃣ 初始化数据库

```cmd
venv\Scripts\activate
python scripts\init_database.py
python scripts\load_sample_data.py
```

### 8️⃣ 启动后端服务

打开两个命令行窗口 / Open two command line windows:

**窗口 1: 启动主服务**
```cmd
start_server.bat
```

**窗口 2: 启动 Celery（可选）**
```cmd
start_celery.bat
```

### 9️⃣ 启动前端服务

打开第三个命令行窗口 / Open third command line window:

```cmd
cd knowledge_graph_system_v2\knowledge_graph_system_v2

# 首次运行需要安装依赖
npm install

# 复制环境配置文件
copy .env.example .env

# 启动前端
npm run serve
```

### 🔟 访问系统

在浏览器中打开 / Open in browser:

- **前端界面**: http://localhost:3000
- **API 文档**: http://localhost:8000/docs

🎉 完成！/ Done!

---

## 🧪 测试 API / Test the API

### 1. 健康检查 / Health Check

```bash
curl http://localhost:8000/health
```

应该返回 / Should return:
```json
{"status": "healthy"}
```

### 2. 获取根节点图谱 / Get Root Graph

```bash
curl http://localhost:8000/api/v1/graph/root?limit=10
```

### 3. 查询统计数据 / Query Statistics

```bash
curl -X POST http://localhost:8000/api/v1/statistics/query -H "Content-Type: application/json" -d "{\"metric\": \"top_authors\", \"limit\": 5}"
```

### 4. 访问 API 文档 / Visit API Docs

在浏览器打开 / Open in browser:

http://localhost:8000/docs

这里有完整的交互式 API 文档！/ Full interactive API documentation here!

---

## ⚠️ 常见错误及解决 / Common Errors & Solutions

### 错误 1: `ModuleNotFoundError: No module named 'fastapi'`

**原因**: 依赖未安装  
**解决**: 
```bash
pip install -r requirements.txt
```

### 错误 2: MySQL 连接失败

**原因**: MySQL 服务未启动或密码错误  
**解决**:
```cmd
net start MySQL
```
检查 `.env` 文件中的密码是否正确

### 错误 3: Neo4j 连接失败

**原因**: Neo4j 数据库未启动  
**解决**: 
1. 打开 Neo4j Desktop
2. 确认数据库状态为 "Active"
3. 检查 `.env` 中的密码

### 错误 4: Redis 连接失败

**原因**: Memurai 服务未启动  
**解决**:
```cmd
net start Memurai
```

### 错误 5: 端口被占用

**原因**: 其他程序占用端口  
**解决**:
```cmd
# 后端端口 8000
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F

# 前端端口 3000
netstat -ano | findstr :3000
taskkill /PID <进程ID> /F
```

### 错误 6: 前端无法连接后端

**原因**: API baseURL 配置错误或后端未启动  
**解决**:
1. 检查 `knowledge_graph_system_v2\knowledge_graph_system_v2\.env` 文件是否存在
2. 确认 `.env` 文件中 `VUE_APP_API_BASE=http://localhost:8000/api/v1`
3. 确认后端服务已启动（http://localhost:8000/health 可访问）
4. 重启前端服务

---

## 📖 API 端点快速参考 / API Endpoints Quick Reference

| 功能 / Feature | 方法 / Method | 端点 / Endpoint | 说明 / Description |
|---------------|--------------|----------------|-------------------|
| 根节点图谱 | GET | `/api/v1/graph/root` | 获取知识图谱根节点 |
| 展开节点 | GET | `/api/v1/graph/children/{node_id}` | 获取子节点 |
| 节点详情 | GET | `/api/v1/graph/node/{node_id}` | 查看节点信息 |
| 保存布局 | POST | `/api/v1/graph/layout/persist` | 保存节点位置 |
| 查询统计 | POST | `/api/v1/statistics/query` | 获取统计数据 |
| 清除缓存 | DELETE | `/api/v1/statistics/cache` | 清除统计缓存 |
| 创建导出 | POST | `/api/v1/export/file` | 创建导出任务 |
| 任务状态 | GET | `/api/v1/export/job/{job_id}` | 查询导出状态 |
| 下载文件 | GET | `/api/v1/export/download/{job_id}` | 下载导出文件 |

---

## 🎓 学习资源 / Learning Resources

- **FastAPI 官方文档**: https://fastapi.tiangolo.com/
- **Neo4j 文档**: https://neo4j.com/docs/
- **SQLAlchemy 文档**: https://docs.sqlalchemy.org/
- **Celery 文档**: https://docs.celeryq.dev/

---

## 💡 提示 / Tips

1. **首次运行**: 建议先运行示例数据脚本，确保系统正常工作
2. **开发模式**: 修改代码后会自动重载（DEBUG=True）
3. **日志文件**: 在 `logs/` 目录查看详细日志
4. **导出文件**: 生成的文件在 `exports/` 目录
5. **API 测试**: 使用 http://localhost:8000/docs 进行交互式测试

---

## 🆘 需要帮助？/ Need Help?

1. 查看 `README.md` 获取完整文档
2. 查看 `PROJECT_STATUS.md` 了解项目状态
3. 检查 `logs/` 目录中的日志文件
4. 访问 http://localhost:8000/health 检查服务状态

---

**祝你使用愉快！/ Enjoy!** 🚀

