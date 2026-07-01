#!/bin/bash

# 检查是否传入了参数
if [ $# -eq 0 ]; then
    echo "add: $0 <perf file>"
    echo "example: $0 t.perf"
    exit 1
fi

# 使用第一个参数作为输入文件
INPUT_FILE="$1"

# 检查文件是否存在
if [ ! -f "$INPUT_FILE" ]; then
    echo "wrong:  '$INPUT_FILE' does not exit"
    exit 1
fi

# 执行处理
soft/FlameGraph/stackcollapse-perf.pl "$INPUT_FILE" > t.folded
sort -t ' ' -k2 -nr t.folded | head -n50 > ./out.txt

echo "done！output: out.txt"
