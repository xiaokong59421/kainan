# 凯南恋爱聊天风格 Skill

一个独立的 Codex Skill，用于分析聊天、改写表达、演练对话和讲解恋爱沟通。它提炼的是可观察的高层次表达特征，不代表凯南本人或官方团队，也不承诺某种话术能改变他人的选择。

## 内容

- `SKILL.md`：入口、工作流、边界和参考资料路由。
- `references/knowledge/`：风格画像、公开来源与证据限制。
- `references/practical/`：场景回复模式和教学练习。
- `agents/openai.yaml`：Codex 技能展示信息。
- `documentation/`：产品定位、架构、流程、权限、变量和知识库治理。
- `scripts/validate_skill.py`：无第三方依赖的结构、链接和敏感文件校验。

资料按“knowledge / practical”分主题组织，按当前问题渐进加载；没有复制其恋爱知识库、论证框架或话术内容。

## 安装

将本仓库内容放到用户 Skill 目录 `~/.codex/skills/kainan-love-coach/`，然后在 Codex 中使用 `$kainan-love-coach`。Windows 默认目录为 `%USERPROFILE%\.codex\skills\kainan-love-coach\`。

## 来源说明

风格分析综合了用户提供的本地逐字稿、用户补充的全平台观察，以及公开可检索的账号/视频元数据。来源台账会注明登录墙、搜索摘要和转载内容等限制。本仓库不包含本地 DOCX 原件、聊天截图、学员资料或未公开课程全文；公开内容也不作为恋爱效果或心理学结论的证明。

详细依据见 [`来源与证据说明`](references/knowledge/来源与证据说明.md)。

## 校验

在仓库根目录运行：

```bash
python3 scripts/validate_skill.py
```

校验器会检查 Skill 入口、界面元数据、必要参考、相对链接、上下文预算、原始资料和常见凭据模式。原始 DOCX、聊天截图、学员资料与本地来源台账不属于发布内容。
