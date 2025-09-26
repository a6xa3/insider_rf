#!/usr/bin/env node
/**
 * Скрипт для пересборки MSI файла с встроенным JSON
 * Версия для Node.js (совместимость с WebContainer)
 */
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

function rebuildMsi() {
    console.log("Пересборка MSI файла...");
    
    // Проверяем наличие необходимых файлов
    const requiredFiles = [
        'Binary.idt',
        'CustomAction.idt', 
        'InstallExecuteSequence.idt',
        'Property.idt',
        'Binary/ConfigurationJson.ibd'
    ];
    
    for (const file of requiredFiles) {
        if (!fs.existsSync(file)) {
            console.log(`ОШИБКА: Файл ${file} не найден!`);
            return false;
        }
    }
    
    // Создаем резервную копию оригинального MSI
    if (fs.existsSync('install.msi')) {
        fs.copyFileSync('install.msi', 'install_backup.msi');
        console.log("Создана резервная копия: install_backup.msi");
    }
    
    try {
        // Используем msidb для обновления таблиц в MSI
        const tablesToUpdate = [
            'Binary',
            'CustomAction', 
            'InstallExecuteSequence',
            'Property'
        ];
        
        for (const table of tablesToUpdate) {
            try {
                const cmd = `msidb.exe -d install.msi -i ${table}.idt`;
                execSync(cmd, { stdio: 'pipe' });
                console.log(`Таблица ${table} успешно обновлена`);
            } catch (error) {
                console.log(`ОШИБКА при обновлении таблицы ${table}: ${error.message}`);
                return false;
            }
        }
        
        console.log("MSI файл успешно пересобран!");
        console.log("\nТеперь install.msi содержит встроенный configuration.json");
        console.log("Файл готов для развертывания через GPO или Intune");
        
        return true;
        
    } catch (error) {
        console.log(`ОШИБКА при пересборке MSI: ${error.message}`);
        return false;
    }
}

function verifyMsi() {
    console.log("Проверка содержимого MSI файла...");
    try {
        // Извлекаем список таблиц для проверки
        const listCmd = 'msidb.exe -d install.msi -l';
        const listResult = execSync(listCmd, { encoding: 'utf8' });
        
        if (listResult.includes('Binary')) {
            console.log("✓ Таблица Binary найдена в MSI");
        }
        
        // Проверяем наличие ConfigurationJson в Binary таблице
        try {
            const exportCmd = 'msidb.exe -d install.msi -e Binary';
            execSync(exportCmd, { stdio: 'pipe' });
            
            if (fs.existsSync('Binary.idt')) {
                const content = fs.readFileSync('Binary.idt', 'utf-8');
                if (content.includes('ConfigurationJson')) {
                    console.log("✓ ConfigurationJson найден в таблице Binary");
                    return true;
                }
            }
        } catch (error) {
            console.log(`Предупреждение при проверке Binary таблицы: ${error.message}`);
        }
        
        return false;
        
    } catch (error) {
        console.log(`ОШИБКА при проверке MSI: ${error.message}`);
        return false;
    }
}

// Основная функция
function main() {
    console.log("=== Пересборка MSI с встроенным JSON ===");
    
    if (rebuildMsi()) {
        console.log("\n=== Проверка результата ===");
        if (verifyMsi()) {
            console.log("\n✓ MSI файл успешно создан и проверен!");
            console.log("\nИнструкции по использованию:");
            console.log("1. Для GPO: используйте install.msi как обычно");
            console.log("2. Для Intune: загрузите install.msi в приложение Win32");
            console.log("3. JSON будет автоматически извлечен при установке");
        } else {
            console.log("\n⚠ Проверка не прошла, возможны проблемы");
        }
    } else {
        console.log("\n❌ Пересборка не удалась");
    }
}

// Запуск скрипта
if (require.main === module) {
    main();
}

module.exports = { rebuildMsi, verifyMsi };