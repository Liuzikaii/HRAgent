---
description: Git 提交规范 - 每次修改后自动提交
---

# Git 提交工作流

## 规则

**每次完成一个功能模块或重要修改后，必须提交 Git 记录。**

---

## 提交时机

1. **功能完成** - 完成一个功能模块后提交
2. **Bug 修复** - 修复 bug 后提交
3. **配置变更** - 修改 docker-compose、环境变量等配置后提交
4. **文档更新** - 更新 README 或其他文档后提交

---

## 提交命令

// turbo-all

```bash
# 1. 添加更改
git add .

# 2. 提交，使用清晰的中文提交信息
git commit -m "feat(模块): 功能描述"

# 3. 推送到远程
git push
```

---

## 提交信息格式

```
类型(范围): 描述

类型:
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码风格
- refactor: 重构
- chore: 构建/工具

范围:
- backend, frontend, infra, data
- 或 all 表示全局修改

示例:
- feat(backend): 添加文档上传API
- feat(frontend): 实现聊天界面
- fix(backend): 修复流式输出中断问题
- docs(readme): 更新部署文档
- chore(infra): 更新docker-compose配置
```

---

## 检查清单

每次重要修改后：
- [ ] `git add .`
- [ ] `git commit -m "描述"`
- [ ] `git push`
