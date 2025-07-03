#!/bin/bash

source /Users/taohong/Programs/codeEvaluator/venv/bin/activate

# 1. 删除数据库
rm db.sqlite3

# 2. 清理迁移文件（可选）
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/__pycache__" -delete

# 3. 重新生成迁移
python3 manage.py makemigrations
python3 manage.py makemigrations analyzer

# 4. 创建数据库并同步表结构
python3 manage.py migrate