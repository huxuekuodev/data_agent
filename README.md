# 项目结构
data-agent/
├── app/                        # 代码核心目录
│   ├── agent/                  # 【核心】智能体相关逻辑（如：Agent 定义、Tool 定义、Workflow/Graph 编排）
│   ├── api/                    # 【核心】对外接口层（HTTP FastAPI 端点 / RPC 服务）
│   ├── clients/                # 【核心】客户端三方集成（如：VectorDB 客户端、ES 客户端、LLM API 封装）
│   ├── conf/                   # 【核心配置】配置类、Pydantic Settings 读取与校验
│   ├── core/                   # 【核心底层】基础设施与通用能力（安全校验、中间件、自定义日志、全局异常）
│   ├── models/                 # 数据库实体类（SQLAlchemy / SQLModel 等 ORM 模型）
│   ├── entities/               # 业务实体类（Domain Entity / Pydantic 传输模型）
│   ├── prompt/                 # 提示词管理工具（Prompt Builder / 动态加载器）
│   ├── repositories/           # Repo 数据访问层（数据库底层 CURD 操纵）
│   ├── scripts/                # 运维与辅助脚本（数据初始化 / 数据库迁移 / 工具脚本）
│   └── services/               # Service 业务层（传统的复杂业务逻辑编排）
├── conf/                       # 配置文件根目录（YAML / .env 环境变量等）
├── docker/                     # 本地本地开发与容器化环境
│   ├── elasticsearch/          # ES 检索服务配置
│   ├── embedding/              # 向量化/嵌入模型服务配置
│   └── mysql/                  # 关系型数据库配置
├── logs/                       # 运行时日志输出目录
└── prompts/                    # 静态提示词模版目录（.txt / .json / .yaml 格式）