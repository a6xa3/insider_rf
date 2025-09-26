#!/usr/bin/env python3
"""
Скрипт для пересборки MSI файла с встроенным JSON
"""
import os
import subprocess
import shutil

def rebuild_msi():
    """Пересобирает MSI файл с обновленными таблицами"""
    
    print("Пересборка MSI файла...")
    
    # Проверяем наличие необходимых файлов
    required_files = [
        'Binary.idt',
        'CustomAction.idt', 
        'InstallExecuteSequence.idt',
        'Property.idt',
        'Binary/ConfigurationJson.ibd'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"ОШИБКА: Файл {file} не найден!")
            return False
    
    # Создаем резервную копию оригинального MSI
    if os.path.exists('install.msi'):
        shutil.copy2('install.msi', 'install_backup.msi')
        print("Создана резервная копия: install_backup.msi")
    
    try:
        # Используем msidb для обновления таблиц в MSI
        tables_to_update = [
            'Binary',
            'CustomAction', 
            'InstallExecuteSequence',
            'Property'
        ]
        
        for table in tables_to_update:
            cmd = [
                'msidb.exe',
                '-d', 'install.msi',
                '-i', f'{table}.idt'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"ОШИБКА при обновлении таблицы {table}: {result.stderr}")
                return False
            else:
                print(f"Таблица {table} успешно обновлена")
        
        print("MSI файл успешно пересобран!")
        print("\nТеперь install.msi содержит встроенный configuration.json")
        print("Файл готов для развертывания через GPO или Intune")
        
        return True
        
    except Exception as e:
        print(f"ОШИБКА при пересборке MSI: {e}")
        return False

def verify_msi():
    """Проверяет содержимое MSI файла"""
    try:
        # Извлекаем список таблиц для проверки
        cmd = ['msidb.exe', '-d', 'install.msi', '-l']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if 'Binary' in result.stdout:
            print("✓ Таблица Binary найдена в MSI")
        
        # Проверяем наличие ConfigurationJson в Binary таблице
        cmd = ['msidb.exe', '-d', 'install.msi', '-e', 'Binary']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            with open('Binary.idt', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'ConfigurationJson' in content:
                    print("✓ ConfigurationJson найден в таблице Binary")
                    return True
        
        return False
        
    except Exception as e:
        print(f"ОШИБКА при проверке MSI: {e}")
        return False

if __name__ == "__main__":
    print("=== Пересборка MSI с встроенным JSON ===")
    
    if rebuild_msi():
        print("\n=== Проверка результата ===")
        if verify_msi():
            print("\n✓ MSI файл успешно создан и проверен!")
            print("\nИнструкции по использованию:")
            print("1. Для GPO: используйте install.msi как обычно")
            print("2. Для Intune: загрузите install.msi в приложение Win32")
            print("3. JSON будет автоматически извлечен при установке")
        else:
            print("\n⚠ Проверка не прошла, возможны проблемы")
    else:
        print("\n❌ Пересборка не удалась")