# Встраивание JSON в MSI

Этот документ описывает процесс встраивания configuration.json в MSI файл как Binary ресурс.

## Что было изменено

### 1. Таблица Binary
Добавлена запись для встраивания JSON:
```
ConfigurationJson	ConfigurationJson.ibd
```

### 2. Таблица CustomAction
Упрощено действие извлечения JSON:
```
ExtractConfigJsonFromBinary	3138	ConfigurationJson	[INSTALLFOLDER]configuration.json
```

### 3. Таблица InstallExecuteSequence
Оставлено только действие извлечения:
```
ExtractConfigJsonFromBinary	NOT Installed	4001
```

### 4. Таблица Property
Добавлено свойство для пути к JSON:
```
ConfigurationJsonPath	[INSTALLFOLDER]configuration.json
```

## Как это работает

1. **При сборке MSI**: JSON файл встраивается как Binary ресурс
2. **При установке**: CustomAction извлекает JSON из Binary ресурса в папку установки
3. **Результат**: configuration.json создается автоматически без внешних зависимостей

## Преимущества

- ✅ Один файл (MSI) содержит все необходимое
- ✅ Работает с GPO без дополнительных файлов
- ✅ Работает с Intune как обычное Win32 приложение
- ✅ Не требует PowerShell или внешних скриптов
- ✅ Совместимо с существующей логикой установки

## Использование

### Для GPO
1. Загрузите только install.msi в GPO
2. Настройте развертывание как обычно
3. JSON будет извлечен автоматически

### Для Intune
1. Создайте Win32 приложение с install.msi
2. Install command: `msiexec /i install.msi /quiet`
3. Uninstall command: `msiexec /x {B1DCDB78-5559-4366-8AC6-36F486741444} /quiet`
4. Detection rule: Registry `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{B1DCDB78-5559-4366-8AC6-36F486741444}`

## Пересборка MSI

Для применения изменений выполните:

```bash
# Создание Binary файла из JSON
python3 create_binary_ibd.py

# Пересборка MSI с новыми таблицами
python3 rebuild_msi.py

# Тестирование результата
python3 test_extraction.py
```

## Проверка результата

После пересборки MSI будет:
1. Содержать JSON как встроенный ресурс
2. Автоматически извлекать JSON при установке
3. Работать без внешних зависимостей

## Техническая информация

- **Тип CustomAction**: 3138 (msidbCustomActionTypeBinaryData + msidbCustomActionTypeTextData)
- **Источник**: ConfigurationJson (имя в Binary таблице)
- **Цель**: Путь для сохранения извлеченного файла
- **Последовательность**: 4001 (после CostInitialize, до InstallFiles)