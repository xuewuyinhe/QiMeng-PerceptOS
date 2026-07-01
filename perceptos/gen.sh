#!/bin/bash


if [ $# -ne 1 ]; then
    echo "add: $0 <round>"
    echo "example: $0 1"
    exit 1
fi

name='myconfig'
num=$1
rm output.txt



cp "outputt_${name}_${num}.txt" save


cp "outputt_${name}_${num}.txt" output.txt




python3 append.py "${name}"


file="./files/myconfig"  # Adjust this path based on your actual directory structure

echo ""
echo "=========================================="
echo "System Performance Evaluation"
echo "=========================================="
echo "Please check the system performance and enter your evaluation:"
echo "  [up]   - Performance improves"
echo "  [down] - Performance decreases"
echo "=========================================="

# Loop until valid input is received
while true; do
    read -p "Please enter (up/down): " user_input
    
    case $user_input in
        up)
           
            if [ -f "$file" ]; then
                cp "$file" .config_base
             
            else
                echo "⚠️  Warning: $file does not exist, skipping backup"
            fi
            break
            ;;
        down)
           
            if [ -f ".config_base" ]; then
                cp .config_base "$file"
                echo "✅ Operation complete: .config_base -> ${file}"
            else
                echo "⚠️  Warning: .config_base does not exist, cannot restore"
                echo "Please ensure you have previously run the 'up' option"
            fi
            break
            ;;
        *)
            echo "⚠️  Invalid input. Please enter 'up' or 'down'"
            ;;
    esac
done

echo "Script execution complete!"