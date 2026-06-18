# Data Agent

Data Agent 是一个面向数据分析与智能问答场景的 Agent 服务框架，提供元数据管理、数据检索、LLM 调用、智能体编排等能力，支持基于数据库元数据实现自然语言数据查询与分析。

---

## 项目结构

```text
data-agent/
├── app/                        # 代码核心目录
│   ├── agent/                  # Agent 定义、Tool 定义、Workflow/Graph 编排
│   ├── api/                    # 对外接口层（FastAPI / RPC）
│   ├── clients/                # 第三方客户端集成（LLM、ES、VectorDB 等）
│   ├── conf/                   # 配置读取与校验（Pydantic Settings）
│   ├── core/                   # 基础设施层（日志、中间件、安全校验、异常处理）
│   ├── models/                 # ORM 数据模型（SQLAlchemy / SQLModel）
│   ├── entities/               # 业务实体与 Pydantic DTO
│   ├── prompt/                 # Prompt 管理与动态加载
│   ├── repositories/           # 数据访问层（Repository）
│   ├── scripts/                # 运维与辅助脚本
│   └── services/               # 业务服务层
│
├── conf/                       # 配置文件目录（YAML / .env）
│
├── docker/                     # 容器化与本地开发环境
│   ├── elasticsearch/          # Elasticsearch 配置
│   ├── embedding/              # Embedding 服务配置
│   └── mysql/                  # MySQL 配置
│
├── logs/                       # 日志输出目录
│
└── prompts/                    # Prompt 模板目录
```

---
## 元数据配置

系统通过 `meta_config.yaml` 管理业务元数据。

配置内容主要分为：

1. 表信息（Table Metadata）
2. 指标信息（Metric Metadata）

---

### 表信息（Tables）

用于描述数据库表结构及业务语义。

示例：

```yaml
tables:
  - name: dim_region
    role: dim
    description: 地区维度表，用于描述订单发生的地理区域信息。
    columns:
      - name: region_id
        role: primary_key
        description: 地区唯一标识。
        alias: [地区ID, 区域ID]
        sync: false

      - name: province
        role: dimension
        description: 订单所属的省份名称。
        alias: [省份, 省, 所在省份]
        sync: true
```

---

### 表字段说明

| 字段          | 类型     | 说明            |
| ----------- | ------ | ------------- |
| name        | string | 表名称，唯一标识一个数据表 |
| role        | string | 表角色           |
| description | string | 表说明           |
| columns     | list   | 字段列表          |

---

### 表角色（role）

#### dim（维度表）

用于描述业务对象的属性信息。

例如：

* 用户信息
* 商品信息
* 门店信息
* 地区信息

特点：

* 数据变化频率较低
* 用于分析维度切分
* 通常包含描述性字段

示例：

```text
user_info
product_info
store_info
```

---

#### fact（事实表）

用于记录业务事件或业务事实。

例如：

* 订单
* 支付
* 浏览行为
* 点击行为

特点：

* 数据量大
* 持续增长
* 包含指标数据

示例：

```text
order_fact
payment_fact
user_behavior_fact
```

---

### 列信息（Columns）

每个字段支持以下配置：

| 字段          | 类型     | 说明            |
| ----------- | ------ | ------------- |
| name        | string | 字段名称          |
| role        | string | 字段角色          |
| description | string | 字段说明          |
| alias       | list   | 字段别名，用于自然语言匹配 |

示例：

```yaml
metrics:
  - name: GMV
    description: 全称Gross Merchandise Value，表示所有订单的成交金额总和。
    relevant_columns:
      - fact_order.order_amount
    alias: [成交总额, 订单总额]
  - name: AOV
    description: 全称Average Order Value，表示所有订单的成交金额平均值。
    relevant_columns:
      - fact_order.order_quantity
    alias: [平均单价, 平均订单金额]

```

