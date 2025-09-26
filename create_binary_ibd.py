#!/usr/bin/env python3
"""
Скрипт для создания .ibd файла из JSON конфигурации
"""
import json
import struct

def create_ibd_from_json(json_file_path, output_ibd_path):
    """Создает .ibd файл из JSON файла"""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_content = f.read()
    
    # Конвертируем в байты
    json_bytes = json_content.encode('utf-8')
    
    # Записываем в .ibd файл (простой бинарный формат)
    with open(output_ibd_path, 'wb') as f:
        f.write(json_bytes)
    
    print(f"Создан {output_ibd_path} размером {len(json_bytes)} байт")

if __name__ == "__main__":
    create_ibd_from_json("configuration.json", "Binary/ConfigurationJson.ibd")