# Data Agent Frontend

一个具有动漫风格和质感的 Vue 3 聊天机器人前端项目。

## 功能特性

- 🔐 用户认证系统（基于 JWT Token）
- 🎨 动漫风格登录界面，带有全屏遮罩和粒子动画效果
- 💬 实时流式对话界面
- 🌐 全局 Token 管理，所有请求自动携带认证信息
- 📱 响应式设计，支持移动端

## 项目结构

```
frontend/
├── src/
│   ├── components/          # 组件
│   │   ├── LoginModal.vue   # 登录遮罩组件
│   │   └── ChatInterface.vue # 聊天界面组件
│   ├── views/               # 页面
│   │   └── ChatView.vue     # 聊天页面
│   ├── stores/              # 状态管理
│   │   └── auth.js          # 认证状态管理
│   ├── router/              # 路由
│   │   └── index.js         # 路由配置
│   ├── utils/               # 工具函数
│   │   └── api.js           # API 请求封装
│   ├── App.vue              # 根组件
│   └── main.js              # 入口文件
├── index.html               # HTML 模板
├── vite.config.js           # Vite 配置
└── package.json             # 项目依赖
```

## 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 `http://localhost:3000`

### 生产构建

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## API 接口

### 登录接口

```
POST /api/user/login
Content-Type: application/json

{
  "username": "用户名"
}

Response:
{
  "message": "登录成功",
  "token": "jwt_token_here"
}
```

### 查询接口

```
POST /api/query
Content-Type: application/json
Authorization: Bearer {token}

{
  "query": "您的问题"
}

Response:
Server-Sent Events (SSE) 流式响应
```

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Vue Router** - 官方路由管理器
- **Pinia** - Vue 3 状态管理库
- **Axios** - HTTP 客户端

## 特色功能

### 1. 动漫风格登录界面
- 全屏渐变背景
- 浮动粒子动画
- 毛玻璃效果模态框
- 闪烁装饰元素
- 平滑的过渡动画

### 2. 全局 Token 管理
- 使用 Pinia 进行状态管理
- Token 自动持久化到 localStorage
- Axios 拦截器自动添加 Authorization 头
- 401 错误自动处理和登出

### 3. 实时流式对话
- 支持 Server-Sent Events (SSE)
- 打字机效果显示回复
- 自动滚动到最新消息
- 消息时间戳显示

### 4. 响应式设计
- 移动端适配
- 触摸友好的交互
- 自适应布局

## 开发说明

### 环境要求

- Node.js >= 16
- npm >= 8

### 配置说明

在 `vite.config.js` 中配置了 API 代理：

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

确保后端服务运行在 `http://localhost:8000`

## 注意事项

1. 确保后端 API 服务正常运行
2. 登录接口返回的 token 格式需要与前端匹配
3. 查询接口需要支持 SSE 流式响应
4. Token 有效期建议设置为 15 天（与前端配置一致）