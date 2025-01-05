#!/bin/bash

CONFIG_FILES=(
    ".gitignore"
    ".eslintrc.json"
    "next.config.mjs"
    "tsconfig.json"
    "package.json"
    "postcss.config.mjs"
)

show_usage() {
    echo "Usage: ./manage-config.sh [command]"
    echo "Commands:"
    echo "  lock      - Lock all configuration files"
    echo "  unlock    - Unlock all configuration files"
    echo "  backup    - Create backups of all configuration files"
    echo "  restore   - Restore all configuration files from backups"
    echo "  status    - Show lock status of all configuration files"
    echo "  help      - Show this help message"
}

lock_files() {
    echo "🔒 Locking configuration files..."
    for file in "${CONFIG_FILES[@]}"; do
        if [ -f "$file" ]; then
            git update-index --assume-unchanged "$file"
            echo "  ✓ Locked: $file"
        else
            echo "  ⚠️  Warning: $file not found"
        fi
    done
}

unlock_files() {
    echo "🔓 Unlocking configuration files..."
    for file in "${CONFIG_FILES[@]}"; do
        if [ -f "$file" ]; then
            git update-index --no-assume-unchanged "$file"
            echo "  ✓ Unlocked: $file"
        else
            echo "  ⚠️  Warning: $file not found"
        fi
    done
}

backup_files() {
    echo "📦 Creating backups..."
    for file in "${CONFIG_FILES[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "${file}.backup"
            echo "  ✓ Backed up: $file → ${file}.backup"
        else
            echo "  ⚠️  Warning: $file not found"
        fi
    done
}

restore_files() {
    echo "📂 Restoring from backups..."
    for file in "${CONFIG_FILES[@]}"; do
        if [ -f "${file}.backup" ]; then
            cp "${file}.backup" "$file"
            echo "  ✓ Restored: ${file}.backup → $file"
        else
            echo "  ⚠️  Warning: ${file}.backup not found"
        fi
    done
}

show_status() {
    echo "📊 Configuration files status:"
    for file in "${CONFIG_FILES[@]}"; do
        if [ -f "$file" ]; then
            if git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
                if git check-ignore -q "$file"; then
                    echo "  🔒 $file (locked, ignored)"
                else
                    echo "  🔓 $file (unlocked)"
                fi
            else
                echo "  ⚠️  $file (untracked)"
            fi
        else
            echo "  ❌ $file (missing)"
        fi
    done
}

case "$1" in
    "lock")
        lock_files
        ;;
    "unlock")
        unlock_files
        ;;
    "backup")
        backup_files
        ;;
    "restore")
        restore_files
        ;;
    "status")
        show_status
        ;;
    "help"|"")
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $1"
        show_usage
        exit 1
        ;;
esac