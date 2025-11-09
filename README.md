# LifeGame MVP

前端：React + TypeScript + Vite  
后端：Django + DRF + PostgreSQL（本地或云端）  
AI：GPT-4o（后端代理，非流式）

## 本地启动
1) 后端
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# 配置 backend/.env（参考 backend/.env.example）
python manage.py migrate
python manage.py seed_defaults
python manage.py runserver 0.0.0.0:8000
```
2) 前端
```bash
cd frontend
npm i
npm run dev
# 打开 http://localhost:5173
```

## OpenAPI → TypeScript
后端提供 schema：`/api/schema/`  
前端生成类型：
```bash
cd frontend
npm run gen:types   # 输出到 src/types/api.d.ts
```

## 云端部署（Render + Neon + Vercel）
1) 数据库：Neon 新建 Postgres，复制 `DATABASE_URL`  
2) 后端（Render）
   - 连接 GitHub 仓库，选择根目录 `render.yaml`  
   - 环境变量：`DATABASE_URL`、`DJANGO_SECRET_KEY`、`OPENAI_API_KEY`（可选）  
3) 前端（Vercel）
   - 连接 `frontend` 目录，`npm run build`，输出 `dist`  
   - 环境变量：`VITE_API_BASE` 指向 Render 后端 `/api/v1`；`VITE_SCHEMA_URL` 指向 `/api/schema/`

## 注意
- `.env` 已被 `.gitignore` 忽略，勿提交密钥。  
- 若使用 OpenAI：建议固定 `httpx==0.27.2`。  
- 任务完成后属性加点：`round(score × weight / 10, 1)`；权重支持先验融合并归一化到 1。


