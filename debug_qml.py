#!/usr/bin/env python3
"""
Script de debug para testar problemas de QML e tipos de dados
"""
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
    from PySide6.QtCore import QObject, Signal, Slot, Property
    from PySide6.QtQml import QmlElement, QJSValue
    import qasync
    import asyncio
    
    print("✅ Imports PySide6 ok")
    
    # Test QJSValue handling
    class TestBackend(QObject):
        @Slot('QVariant')
        def testConfig(self, config_data):
            print(f"Received: {type(config_data)}")
            if isinstance(config_data, QJSValue):
                config_dict = config_data.toVariant()
                print(f"Converted QJSValue to: {type(config_dict)}")
            else:
                config_dict = config_data
                print(f"Direct type: {type(config_dict)}")
            
            if isinstance(config_dict, dict):
                print(f"Dict keys: {list(config_dict.keys())}")
            
    print("✅ Test backend criado")
    
    # Test basic Qt app creation
    app = QGuiApplication(sys.argv)
    print("✅ QGuiApplication criado")
    
    # Test async setup
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    print("✅ Async loop configurado")
    
    # Test QML engine
    engine = QQmlApplicationEngine()
    print("✅ QML engine criado")
    
    # Test backend registration
    backend = TestBackend()
    engine.rootContext().setContextProperty("testBackend", backend)
    print("✅ Backend registrado")
    
    print("🎉 Todos os testes passaram!")
    
except ImportError as e:
    print(f"❌ Erro de import: {e}")
    print("   Certifique-se de que PySide6 está instalado: pip install PySide6")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()