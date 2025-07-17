#!/usr/bin/env python3
"""
Teste de sintaxe QML - verifica se os arquivos QML têm sintaxe válida
"""
import os
import sys

def check_qml_syntax():
    """Verifica a sintaxe dos arquivos QML"""
    qml_files = [
        "src/ui/qml/main.qml",
        "src/ui/qml/components/DesignSystem.qml",
        "src/ui/qml/components/ModernButton.qml",
        "src/ui/qml/components/ModernCard.qml",
        "src/ui/qml/components/ModernInput.qml",
        "src/ui/qml/components/ModernDropdown.qml",
        "src/ui/qml/components/ModernChapterList.qml",
        "src/ui/qml/components/MangaCardModern.qml",
        "src/ui/qml/components/ModernUploadWorkflow.qml",
        "src/ui/qml/components/ModernSettingsPanel.qml",
        "test_qml.qml"
    ]
    
    print("🔍 Verificando sintaxe dos arquivos QML...")
    
    for qml_file in qml_files:
        if os.path.exists(qml_file):
            print(f"✅ {qml_file} - Arquivo encontrado")
            # Verificação básica de sintaxe
            with open(qml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Conta chaves
            open_braces = content.count('{')
            close_braces = content.count('}')
            
            if open_braces == close_braces:
                print(f"✅ {qml_file} - Chaves balanceadas ({open_braces}/{close_braces})")
            else:
                print(f"❌ {qml_file} - Chaves desbalanceadas ({open_braces}/{close_braces})")
                return False
                
            # Verifica imports básicos
            if 'import QtQuick' in content:
                print(f"✅ {qml_file} - Import QtQuick OK")
            else:
                print(f"⚠️ {qml_file} - Sem import QtQuick")
                
        else:
            print(f"❌ {qml_file} - Arquivo não encontrado")
            return False
    
    print("\n🎉 Todos os arquivos QML passaram na verificação básica!")
    return True

if __name__ == "__main__":
    success = check_qml_syntax()
    sys.exit(0 if success else 1)