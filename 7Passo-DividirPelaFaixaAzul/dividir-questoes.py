from PIL import Image
import os

def verificar_padrao_no_pixel(pixels, x, y, altura_maxima):
    """
    Verifica se a partir da coordenada (x, y) existe o padrão vertical:
    - Faixa 1: cor (35, 31, 32) com altura 7px (tolerando de 5 a 9px)
    - Faixa 2: cor (255, 255, 255) com altura 4px (tolerando de 2 a 6px)
    - Faixa 3: cor (35, 31, 32) com altura 2px (tolerando de 0 a 4px, mínimo 1px)
    Retorna o total de pixels ocupados pelo padrão se encontrado, ou 0 caso contrário.
    """
    tolerancia_cor = 15  # Tolerância para variações sutis no tom do RGB
    
    cor_escura = (35, 31, 32)
    cor_branca = (255, 255, 255)
    
    def cor_valida(pixel, cor_alvo):
        r, g, b = pixel[:3]
        return (abs(r - cor_alvo[0]) <= tolerancia_cor and 
                abs(g - cor_alvo[1]) <= tolerancia_cor and 
                abs(b - cor_alvo[2]) <= tolerancia_cor)

    curr_y = y

    # --- FAIXA 1: Escura (Alvo: 7px, Margem: 5 a 9px) ---
    cont_f1 = 0
    while curr_y < altura_maxima and cor_valida(pixels[x, curr_y], cor_escura):
        cont_f1 += 1
        curr_y += 1
        if cont_f1 > 9:  # Ultrapassou a margem máxima
            return 0
    if cont_f1 < 5:  # Não atingiu a margem mínima
        return 0

    # --- FAIXA 2: Branca (Alvo: 4px, Margem: 2 a 6px) ---
    cont_f2 = 0
    while curr_y < altura_maxima and cor_valida(pixels[x, curr_y], cor_branca):
        cont_f2 += 1
        curr_y += 1
        if cont_f2 > 6:
            return 0
    if cont_f2 < 2:
        return 0

    # --- FAIXA 3: Escura (Alvo: 2px, Margem: 0 a 4px -> consideramos mínimo 1px para validação) ---
    cont_f3 = 0
    while curr_y < altura_maxima and cor_valida(pixels[x, curr_y], cor_escura):
        cont_f3 += 1
        curr_y += 1
        if cont_f3 > 4:
            return 0
    if cont_f3 < 1:  
        return 0

    # Se passou por todas as etapas validando os intervalos, padrão encontrado!
    return cont_f1 + cont_f2 + cont_f3


def encontrar_padrao_questoes(imagem):
    """
    Percorre a imagem de cima para baixo pela coluna central (meio)
    procurando pelo padrão de faixas estruturado.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    x_meio = 500  # Analisa o pixel do MEIO horizontalmente
    posicoes_corte = []
    
    y = 0
    while y < altura:
        tamanho_padrao = verificar_padrao_no_pixel(pixels, x_meio, y, altura)
        
        if tamanho_padrao > 0:
            # Encontrou o padrão! Corta-se 13 pixels antes do início detectado
            posicao_corte = y - 17
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Padrão visual encontrado começando em y={y}, cortando em y={posicao_corte} (Largura total detectada: {tamanho_padrao}px)")
            
            # Pula todo o tamanho do padrão detectado para evitar múltiplas detecções no mesmo lugar
            y += tamanho_padrao
        else:
            y += 1
            
    return posicoes_corte


def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando ANTES dos padrões visuais localizados
    """
    if not os.path.exists(caminho_imagem):
        print(f"Erro: O arquivo '{caminho_imagem}' não foi encontrado.")
        return

    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições com base na análise do pixel central
    posicoes_corte = encontrar_padrao_questoes(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão visual foi encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} padrões visuais para corte")
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima seção começa imediatamente no ponto do corte
        posicao_anterior = posicao_corte
    
    # Corta a seção final restante após o último ponto detectado
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")


if __name__ == "__main__":
    # --- CONFIGURAÇÃO PARA COLUNAS CONCATENADAS ---
    caminho_imagem = "pagina_enem_6.png"
    pasta_saida = "pagina_6"

    # --- CONFIGURAÇÃO PARA PÁGINAS INTEIRAS (Descomente para usar) ---
    # caminho_imagem = "./inteiras/pagina_enem_15.png"
    # pasta_saida = "pagina_15"
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    print("Divisão concluída!")