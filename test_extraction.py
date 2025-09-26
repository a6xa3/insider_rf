#!/usr/bin/env python3
"""
Скрипт для тестирования извлечения JSON из MSI
"""
import os
import subprocess
import tempfile
import json

def test_json_extraction():
    """Тестирует извлечение JSON из MSI файла"""
    
    print("=== Тест извлечения JSON из MSI ===")
    
    # Создаем временную директорию для теста
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Временная директория: {temp_dir}")
        
        try:
            # Извлекаем Binary таблицу из MSI
            cmd = [
                'msidb.exe',
                '-d', 'install.msi',
                '-e', 'Binary'
            ]
            
            result = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"ОШИБКА при извлечении Binary таблицы: {result.stderr}")
                return False
            
            # Проверяем наличие ConfigurationJson.ibd
            ibd_path = os.path.join(temp_dir, 'Binary', 'ConfigurationJson.ibd')
            if not os.path.exists(ibd_path):
                print("ОШИБКА: ConfigurationJson.ibd не найден в Binary таблице")
                return False
            
            # Читаем содержимое .ibd файла
            with open(ibd_path, 'rb') as f:
                json_bytes = f.read()
            
            # Декодируем JSON
            json_content = json_bytes.decode('utf-8')
            print(f"Извлеченный JSON ({len(json_bytes)} байт):")
            print(json_content)
            
            # Проверяем валидность JSON
            try:
                config = json.loads(json_content)
                print("\n✓ JSON валиден")
                
                # Проверяем ключевые поля
                required_fields = ['mode', 'server', 'debug', 'client']
                for field in required_fields:
                    if field in config:
                        print(f"✓ Поле '{field}' найдено")
                    else:
                        print(f"⚠ Поле '{field}' отсутствует")
                
                return True
                
            except json.JSONDecodeError as e:
                print(f"ОШИБКА: JSON невалиден - {e}")
                return False
                
        except Exception as e:
            print(f"ОШИБКА при тестировании: {e}")
            return False

def simulate_installation():
    """Симулирует процесс установки для проверки CustomAction"""
    
    print("\n=== Симуляция установки ===")
    
    # Проверяем CustomAction в таблице
    try:
        cmd = ['msidb.exe', '-d', 'install.msi', '-e', 'CustomAction']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            with open('CustomAction.idt', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'ExtractConfigJsonFromBinary' in content:
                    print("✓ CustomAction для извлечения JSON найден")
                    
                    # Показываем параметры действия
                    lines = content.split('\n')
                    for line in lines:
                        if 'ExtractConfigJsonFromBinary' in line:
                            parts = line.split('\t')
                            if len(parts) >= 4:
                                print(f"  Тип: {parts[1]}")
                                print(f"  Источник: {parts[2]}")
                                print(f"  Цель: {parts[3]}")
                    
                    return True
        
        print("⚠ CustomAction для извлечения JSON не найден")
        return False
        
    except Exception as e:
        print(f"ОШИБКА при проверке CustomAction: {e}")
        return False

if __name__ == "__main__":
    success = True
    
    if not test_json_extraction():
        success = False
    
    if not simulate_installation():
        success = False
    
    if success:
        print("\n✅ Все тесты прошли успешно!")
        print("MSI готов к развертыванию")
    else:
        print("\n❌ Обнаружены проблемы")
        print("Проверьте конфигурацию MSI")