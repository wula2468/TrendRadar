#!/bin/bash
# TrendRadar HTML 清理脚本
# 功能：清理过期的 HTML 报告文件

# 配置
OUTPUT_DIR="output/html"
KEEP_DAYS=3  # 保留最近 3 天的 HTML 文件
KEEP_LATEST=5  # 每天保留最新的 5 个文件

echo "🧹 开始清理 HTML 报告..."

# 检查目录是否存在
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "❌ 目录不存在: $OUTPUT_DIR"
    exit 1
fi

# 1. 删除超过 N 天的旧目录
echo "📅 清理 $KEEP_DAYS 天前的旧报告..."
find "$OUTPUT_DIR" -type d -name "20*" -mtime +$KEEP_DAYS -exec rm -rf {} \; 2>/dev/null

# 2. 对于每天的目录，只保留最新的 N 个文件
echo "🗂️  每天只保留最新的 $KEEP_LATEST 个文件..."
for day_dir in "$OUTPUT_DIR"/*/ ; do
    if [ -d "$day_dir" ]; then
        # 获取目录中的文件数量
        file_count=$(find "$day_dir" -type f -name "*.html" | wc -l)

        if [ "$file_count" -gt "$KEEP_LATEST" ]; then
            # 删除最旧的文件，只保留最新的 N 个
            cd "$day_dir"
            ls -t *.html | tail -n +$((KEEP_LATEST + 1)) | xargs rm -f 2>/dev/null
            deleted=$((file_count - KEEP_LATEST))
            echo "  ✓ $(basename "$day_dir"): 删除 $deleted 个旧文件"
        fi
    fi
done

# 3. 统计结果
total_files=$(find "$OUTPUT_DIR" -type f -name "*.html" | wc -l)
total_size=$(du -sh "$OUTPUT_DIR" | cut -f1)

echo "✅ 清理完成！"
echo "📊 当前状态："
echo "  - HTML 文件数: $total_files"
echo "  - 占用空间: $total_size"
echo "  - 保留策略: 最近 $KEEP_DAYS 天，每天最多 $KEEP_LATEST 个文件"
