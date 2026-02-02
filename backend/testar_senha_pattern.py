def gerar_senha_temporaria(nome_completo: str) -> str:
    """
    Gera senha temporária no padrão: IOS2026 + iniciais do nome
    Exemplo: Fabiana Pinto Coelho → IOS2026fpc
    """
    # Pegar primeira letra de cada palavra do nome
    palavras = nome_completo.strip().split()
    iniciais = ''.join([p[0].lower() for p in palavras if p])
    
    # Limitar a 5 iniciais para não ficar muito longo
    iniciais = iniciais[:5]
    
    return f"IOS2026{iniciais}"

# Testar com os nomes dos usuários
print("📋 EXEMPLOS DE SENHAS TEMPORÁRIAS:\n")
print("=" * 60)

nomes_teste = [
    "Fabiana Pinto Coelho",
    "Juliete Pereira",
    "Luana Cristina Soares",
    "Jesiel Junior",
    "Administrador",
    "Rickson Leite Vilela Fontes",
    "Iago Herbert dos Santos",
    "José Marcos Valério da Silva"
]

for nome in nomes_teste:
    senha = gerar_senha_temporaria(nome)
    print(f"{nome:<40} → {senha}")

print("=" * 60)
print("\n✅ Padrão: IOS2026 + iniciais do nome (máximo 5 letras)")
print("📝 Fácil de lembrar e ainda relativamente seguro!")
