#!/bin/bash
# TrendRadar 启动脚本

# AI 分析配置 (使用美团内部 API - deepseek-chat)
cd ~/Downloads/gitproject/TrendRadar
source venv/bin/activate

export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/4ba9f6d7-d62a-45f4-9898-30012978a49d"
export AI_ANALYSIS_ENABLED="true"
export AI_API_KEY="21913120356400447544"
export AI_MODEL="openai/LongCat-Flash-Thinking-2601"
export AI_API_BASE="https://chat.sankuai.com/v1/openai/native"

python -m trendradar "$@"
