from app import create_app, db
from app.models import Usuario, Categoria, Pictograma

def inicializar_banco():
    app = create_app()
    
    with app.app_context():
        print("Criando tabelas...")
        db.create_all()
        print("Tabelas criadas!")
        
        # Criar usuário admin padrão se não existir
        admin = Usuario.query.filter_by(login='admin').first()
        if not admin:
            print("Criando usuário admin padrão...")
            admin = Usuario(
                nome='Administrador',
                login='admin',
                senha='1234',
                cargo='Administrador'
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuário admin criado! Login: admin | Senha: 1234")
        
        print("Populando banco...")
        
        # Verifica se já existem categorias
        if Categoria.query.count() > 0:
            print("Categorias já existem. Pulando...")
            return
        
        categorias_dados = [
            {'nome': 'Comida', 'cor': '#FF6B6B', 'icone': '🍎', 'ordem': 1},
            {'nome': 'Emoções', 'cor': '#4ECDC4', 'icone': '😊', 'ordem': 2},
            {'nome': 'Necessidades', 'cor': '#95E1D3', 'icone': '🔔', 'ordem': 3},
            {'nome': 'Ações', 'cor': '#F38181', 'icone': '✨', 'ordem': 4},
        ]
        
        categorias = {}
        for cat_data in categorias_dados:
            cat = Categoria(**cat_data)
            db.session.add(cat)
            categorias[cat_data['nome']] = cat
        
        db.session.commit()
        print("Categorias criadas!")
        
        # URLs padrão usando placeholder do Cloudinary
        # Em produção, recomenda-se fazer upload das imagens reais via interface /gerenciar
        pictogramas = [
            # COMIDA
            {'nome': 'Água', 'cat': 'Comida', 'audio': 'Água', 'ordem': 1, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},
            {'nome': 'Pão', 'cat': 'Comida', 'audio': 'Pão', 'ordem': 2, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},
            {'nome': 'Fruta', 'cat': 'Comida', 'audio': 'Fruta', 'ordem': 3, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},
            {'nome': 'Suco', 'cat': 'Comida', 'audio': 'Suco', 'ordem': 4, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},

            # EMOÇÕES
            {'nome': 'Feliz', 'cat': 'Emoções', 'audio': 'Feliz', 'ordem': 1, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},
            {'nome': 'Triste', 'cat': 'Emoções', 'audio': 'Triste', 'ordem': 2, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},
            {'nome': 'Raiva', 'cat': 'Emoções', 'audio': 'Raiva', 'ordem': 3, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},
            {'nome': 'Medo', 'cat': 'Emoções', 'audio': 'Medo', 'ordem': 4, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},

            # NECESSIDADES
            {'nome': 'Banheiro', 'cat': 'Necessidades', 'audio': 'Banheiro', 'ordem': 1, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},
            {'nome': 'Ajuda', 'cat': 'Necessidades', 'audio': 'Ajuda', 'ordem': 2, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},
            {'nome': 'Descanso', 'cat': 'Necessidades', 'audio': 'Descanso', 'ordem': 3, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},
            {'nome': 'Sede', 'cat': 'Necessidades', 'audio': 'Sede', 'ordem': 4, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},

            # AÇÕES
            {'nome': 'Brincar', 'cat': 'Ações', 'audio': 'Brincar', 'ordem': 1, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},
            {'nome': 'Comer', 'cat': 'Ações', 'audio': 'Comer', 'ordem': 2, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},
            {'nome': 'Dormir', 'cat': 'Ações', 'audio': 'Dormir', 'ordem': 3, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},
            {'nome': 'Sair', 'cat': 'Ações', 'audio': 'Sair', 'ordem': 4, 'img': 'https://res.cloudinary.com/demo/image/upload/v1/docs/sample.jpg'},

        ]
        
        for p in pictogramas:
            pict = Pictograma(
                nome=p['nome'],
                categoria_id=categorias[p['cat']].id,
                audio_texto=p['audio'],
                ordem=p['ordem'],
                imagem_url=p['img']
            )
            db.session.add(pict)
        
        db.session.commit()
        print("Pictogramas criados!")
        print("Concluido!")

if __name__ == '__main__':
    inicializar_banco()