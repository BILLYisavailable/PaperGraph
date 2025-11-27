# 论文知识图谱系统 / Paper Knowledge Graph System

基于 FastAPI、Neo4j、MySQL 和 Redis 的论文知识图谱展示系统。

A complete backend system for paper knowledge graph visualization based on FastAPI, Neo4j, MySQL, and Redis.

## 📑 项目说明 / Project Overview

本项目实现了一个完整的论文知识图谱后端系统，包括：

This project implements a complete backend system for paper knowledge graph with the following features:

- 📊 图谱可视化展示（节点展开/折叠、详情查看） / Graph Visualization (node expansion/collapse, detail view)
- 📈 数据统计分析（多维度统计、图表展示） / Statistical Analysis (multi-dimensional statistics, charts)
- 📥 数据导出功能（CSV/Excel格式） / Data Export (CSV/Excel formats)
- ⚡ 异步任务处理（Celery） / Asynchronous Task Processing (Celery)
- 🔄 Redis缓存优化 / Redis Caching Optimization

## 🛠 技术栈 / Tech Stack

- **后端框架 / Backend**: FastAPI 0.104.1
- **图数据库 / Graph Database**: Neo4j 5.14+
- **关系数据库 / Relational Database**: MySQL 8.0+
- **缓存 / Cache**: Redis 7.0+
- **任务队列 / Task Queue**: Celery 5.3+
- **Python**: 3.9+

## 🚀 快速开始 / Quick Start

### Prerequisites / 前置要求

安装以下软件 / Install the following software:

1. **Python 3.9+** - [Download](https://www.python.org/downloads/)
2. **MySQL 8.0+** - [Download](https://dev.mysql.com/downloads/installer/)
3. **Neo4j Desktop** - [Download](https://neo4j.com/download/)
4. **Memurai (Redis for Windows)** - [Download Memurai](https://www.memurai.com/get-memurai)

### 1️⃣ Clone and Setup Environment / 克隆并设置环境

```bash
# Run setup script (creates venv and installs dependencies)
# 运行设置脚本（创建虚拟环境并安装依赖）
setup.bat
```

### 2️⃣ Configure Environment / 配置环境

Copy `.env.example` to `.env` and update with your credentials:

复制 `.env.example` 为 `.env` 并填入你的配置：

```bash
# Copy example file / 复制示例文件
cp .env.example .env

# Edit .env file / 编辑 .env 文件
# Update the following:
# - MYSQL_PASSWORD (your MySQL password)
# - NEO4J_PASSWORD (your Neo4j password)
```

### 3️⃣ Setup Databases / 设置数据库

#### MySQL:
```bash
# Connect to MySQL / 连接到MySQL
mysql -u root -p

# Create database / 创建数据库
CREATE DATABASE paper_kg CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

#### Neo4j:
1. Open Neo4j Desktop / 打开 Neo4j Desktop
2. Create a new database / 创建新数据库
3. Start the database / 启动数据库
4. Set password in `.env` file / 在 `.env` 文件中设置密码

#### Redis (Memurai):
启动 Memurai 服务 / Start Memurai service:
```bash
net start Memurai
```

### 4️⃣ Initialize Databases / 初始化数据库

```bash
# Activate virtual environment / 激活虚拟环境
venv\Scripts\activate

# Initialize all databases (creates tables, indexes, constraints)
# 初始化所有数据库（创建表、索引、约束）
python scripts\init_database.py

# Load sample data (optional)
# 加载示例数据（可选）
python scripts\load_sample_data.py
```

### 5️⃣ Start Services / 启动服务

```bash
# Terminal 1: Start main server / 终端1：启动主服务
start_server.bat

# Terminal 2: Start Celery worker (for export功能)
# 终端2：启动 Celery worker（用于导出功能）
start_celery.bat
```

### 6️⃣ Start Frontend / 启动前端

```bash
# Navigate to frontend directory / 进入前端目录
cd knowledge_graph_system_v2\knowledge_graph_system_v2

# Install dependencies (first time only) / 安装依赖（仅首次）
npm install

# Copy environment file / 复制环境配置文件
copy .env.example .env

# Start frontend development server / 启动前端开发服务器
npm run serve
```

前端将运行在 http://localhost:3000

The frontend will run at http://localhost:3000

### 7️⃣ Access System / 访问系统

- **Frontend / 前端界面**: http://localhost:3000
- **API Documentation / API文档**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check / 健康检查**: http://localhost:8000/health

## 📚 核心API接口 / Core API Endpoints

### 图谱接口 / Graph APIs
- `GET /api/v1/graph/root` - 获取根节点图谱 / Get root graph
- `GET /api/v1/graph/children/{node_id}` - 展开子节点 / Expand child nodes
- `GET /api/v1/graph/node/{node_id}` - 查看节点详情 / Get node details
- `POST /api/v1/graph/layout/persist` - 保存布局 / Persist layout

### 统计接口 / Statistics APIs
- `POST /api/v1/statistics/query` - 查询统计数据 / Query statistics
- `DELETE /api/v1/statistics/cache` - 清除缓存 / Clear cache

### 导出接口 / Export APIs
- `POST /api/v1/export/file` - 创建导出任务 / Create export job
- `GET /api/v1/export/job/{job_id}` - 查询任务状态 / Get job status
- `GET /api/v1/export/download/{job_id}` - 下载文件 / Download file

## 📁 项目结构 / Project Structure

```
PaperGraph/
├── app/                    # 应用主目录 / Main application
│   ├── api/v1/            # API接口 / API endpoints
│   │   ├── graph.py       # 图谱API / Graph APIs
│   │   ├── statistics.py  # 统计API / Statistics APIs
│   │   └── export.py      # 导出API / Export APIs
│   ├── models/            # 数据模型 / Data models
│   │   └── mysql_models.py # MySQL表模型 / MySQL table models
│   ├── repositories/      # 数据访问层 / Data access layer
│   │   ├── mysql_dao.py   # MySQL DAO
│   │   └── neo4j_dao.py   # Neo4j DAO
│   ├── schemas/           # 请求/响应格式 / Request/Response schemas
│   ├── services/          # 业务逻辑 / Business logic
│   │   ├── graph_service.py      # 图谱服务 / Graph service
│   │   ├── statistics_service.py # 统计服务 / Statistics service
│   │   └── export_service.py     # 导出服务 / Export service
│   ├── tasks/             # 异步任务 / Async tasks
│   │   ├── celery_app.py  # Celery配置 / Celery config
│   │   └── export_tasks.py # 导出任务 / Export tasks
│   ├── database.py        # 数据库连接 / Database connections
│   └── main.py            # 应用入口 / Application entry
├── scripts/               # 工具脚本 / Utility scripts
│   ├── init_database.py   # 数据库初始化 / Database initialization
│   └── load_sample_data.py # 示例数据 / Sample data loader
├── logs/                  # 日志目录 / Log directory
├── exports/               # 导出文件目录 / Export files directory
├── config.py              # 配置文件 / Configuration
├── requirements.txt       # 依赖列表 / Dependencies
├── .env.example           # 环境变量示例 / Environment variables example
├── setup.bat              # 环境设置脚本 / Setup script (Windows)
├── start_server.bat       # 启动服务器 / Start server (Windows)
└── start_celery.bat       # 启动Worker / Start worker (Windows)
```

## 🔧 常见问题 / Troubleshooting

### MySQL连接失败 / MySQL Connection Failed
- 确认MySQL服务已启动 / Ensure MySQL service is running:
  ```bash
  net start MySQL
  ```
- 检查`.env`中的密码是否正确 / Check password in `.env`
- 确认数据库已创建 / Verify database is created

### Neo4j连接失败 / Neo4j Connection Failed
- 确认Neo4j Desktop中数据库已启动 / Ensure database is started in Neo4j Desktop
- 检查端口7687是否被占用 / Check if port 7687 is available
- 确认用户名和密码正确 / Verify username and password

### Redis连接失败 / Redis Connection Failed
- 确认Memurai服务已启动 / Ensure Memurai service is running:
  ```bash
  net start Memurai
  ```
- 检查端口6379是否被占用 / Check if port 6379 is available

### Celery在Windows上报错 / Celery Error on Windows
- 必须使用`--pool=solo`参数 / Must use `--pool=solo` parameter:
  ```bash
  celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
  ```
- 已在`start_celery.bat`中配置 / Already configured in `start_celery.bat`

### 端口被占用 / Port Already in Use
```bash
# Find and kill process / 查找并结束进程
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# For frontend port / 前端端口
netstat -ano | findstr :3000
taskkill /PID <process_id> /F
```

## 📖 API使用示例 / API Usage Examples

### 获取图谱数据 / Get Graph Data
```bash
# Get root graph with 50 nodes
curl http://localhost:8000/api/v1/graph/root?limit=50

# Get children of a specific node
curl http://localhost:8000/api/v1/graph/children/123

# Get node details
curl http://localhost:8000/api/v1/graph/node/123
```

### 查询统计数据 / Query Statistics
```bash
# Paper count by year
curl -X POST http://localhost:8000/api/v1/statistics/query \
  -H "Content-Type: application/json" \
  -d '{"metric": "paper_count_by_year", "start_year": 2020, "end_year": 2023}'

# Top authors
curl -X POST http://localhost:8000/api/v1/statistics/query \
  -H "Content-Type: application/json" \
  -d '{"metric": "top_authors", "limit": 10}'
```

### 创建导出任务 / Create Export Job
```bash
# Create export job
curl -X POST http://localhost:8000/api/v1/export/file \
  -H "Content-Type: application/json" \
  -d '{"export_type": "papers", "format": "csv"}'

# Check job status
curl http://localhost:8000/api/v1/export/job/{job_id}

# Download file
curl http://localhost:8000/api/v1/export/download/{job_id} -o export.csv
```

## 🧪 测试 / Testing

访问 API 文档进行交互式测试 / Visit API docs for interactive testing:

http://localhost:8000/docs

## 🎯 下一步 / Next Steps

1. 根据需求导入真实的论文数据 / Import real paper data based on your needs
2. 开发前端界面 / Develop frontend interface (React/Vue + G6/D3.js)
3. 定制化统计指标和导出格式 / Customize statistics metrics and export formats
4. 添加用户认证系统 / Add user authentication system
5. 部署到生产环境 / Deploy to production environment

## 📊 数据库表结构 / Database Schema

### MySQL Tables
- `paper_info` - 论文信息 / Paper information
- `author_info` - 作者信息 / Author information
- `organization_info` - 机构信息 / Organization information
- `paper_author_relation` - 论文-作者关系 / Paper-Author relations
- `paper_citation_relation` - 论文引用关系 / Paper citation relations
- `graph_node_mapping` - 图节点映射 / Graph node mapping
- `statistics_data` - 统计数据 / Statistics data
- `export_log` - 导出日志 / Export logs

### Neo4j Node Types
- `Paper` - 论文节点 / Paper nodes
- `Author` - 作者节点 / Author nodes
- `Organization` - 机构节点 / Organization nodes

### Neo4j Relationship Types
- `AUTHORED` - 作者撰写论文 / Author wrote paper
- `AFFILIATED_WITH` - 作者隶属机构 / Author affiliated with organization
- `CITES` - 论文引用论文 / Paper cites paper

## 🔐 安全建议 / Security Recommendations

1. 生产环境请修改 `SECRET_KEY` / Change `SECRET_KEY` in production
2. 使用强密码保护数据库 / Use strong passwords for databases
3. 配置防火墙规则 / Configure firewall rules
4. 定期备份数据 / Regular data backups
5. 启用 HTTPS / Enable HTTPS

## 📄 许可证 / License

MIT License

## 📮 联系方式 / Contact

如有问题或建议，请提交 Issue / For questions or suggestions, please submit an Issue.

---

**注意 / Note**: 这是一个完整实现的后端系统，所有功能模块已完整开发。/ This is a fully implemented backend system with all functional modules completed.

