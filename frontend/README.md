# Agent-ZY Frontend

基于 Vue3 + Vite + Element Plus 的智能体管理系统前端项目。

## 功能特性

- 🚀 基于 Vue3 + Vite 构建，快速响应
- 🎨 使用 Element Plus 组件库，美观易用
- 🔐 完整的用户认证系统（登录、注册、个人中心）
- 🤖 智能体管理（创建、编辑、删除）
- 💬 智能对话功能
- 📚 知识库管理（支持文件上传和URL学习）
- 📱 响应式设计，支持移动端

## 技术栈

- Vue 3
- Vite
- Element Plus
- Vue Router
- Axios
- Pinia (状态管理)

## 开发环境要求

- Node.js >= 16.0.0
- npm >= 7.0.0

## 快速开始

1. 克隆项目
```bash
git clone [项目地址]
cd agent-zy-frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

4. 构建生产版本
```bash
npm run build
```

## 项目结构

```
src/
├── api/          # API 接口封装
├── assets/       # 静态资源
├── components/   # 公共组件
├── router/       # 路由配置
├── store/        # 状态管理
├── utils/        # 工具函数
└── views/        # 页面组件
```

## 主要功能模块

### 用户认证
- 登录/注册
- 个人中心
- Token 管理

### 智能体管理
- 智能体列表
- 创建智能体
- 编辑智能体信息
- 删除智能体
- 智能体头像上传

### 对话功能
- 实时对话
- 历史记录
- 上下文管理

### 知识库管理
- 文件上传（支持 PDF、TXT、DOCX、XLSX）
- URL 学习
- 知识库内容管理

## 开发指南

### 环境变量
项目使用 `.env` 文件管理环境变量，主要配置项：
- VITE_API_BASE_URL: API 基础地址
- VITE_APP_TITLE: 应用标题

### 代码规范
- 使用 ESLint 进行代码检查
- 遵循 Vue3 组合式 API 风格
- 组件命名采用 PascalCase
- 文件名采用 kebab-case

## 部署

1. 构建生产版本
```bash
npm run build
```

2. 部署 dist 目录到 Web 服务器

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交改动
4. 推送到分支
5. 创建 Pull Request

## 许可证

[MIT License](LICENSE)
