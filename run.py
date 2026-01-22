"""
run.py
Arquivo principal para executar a aplicação
Sistema de Comunicação Alternativa com Pictogramas para TEA
"""

import os
from app import create_app

# Detecta ambiente automaticamente
env = os.environ.get('FLASK_ENV', 'production')
config_name = 'development' if env == 'development' else 'production'

app = create_app(config_name)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎨 Sistema de Comunicação Alternativa com Pictogramas")
    print("   Para crianças com TEA")
    print("="*60)
    print("\n📱 Servidor iniciando...")
    print("🌐 Acesse: http://localhost:5000")
    print("⚠️  Pressione CTRL+C para parar\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )