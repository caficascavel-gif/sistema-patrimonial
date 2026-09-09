from app.models import Patrimonio


def calcular_pendencias(patrimonio: Patrimonio) -> list[str]:
    """
    Verifica quais informações do patrimônio ainda faltam ser preenchidas.
    Patrimônio, Equipamento e Localização são considerados o mínimo para existir
    o registro (obrigatórios na criação); as pendências aqui são o restante
    do que o documento pede para considerar o cadastro completo.
    """
    pendencias: list[str] = []

    if not patrimonio.numero_serie:
        pendencias.append("Número de série não informado")

    if not patrimonio.setor_id or not patrimonio.local_id:
        pendencias.append("Localização não informada")

    if not patrimonio.empenho_id:
        pendencias.append("NE não informado")

    if not patrimonio.aquisicao_id:
        pendencias.append("Aquisição não vinculada")
    else:
        aquisicao = patrimonio.aquisicao
        if aquisicao is not None:
            if not aquisicao.fornecedor_id:
                pendencias.append("Fornecedor não informado")
            if not aquisicao.nota_fiscal:
                pendencias.append("Nota fiscal não informada")
    # se não há aquisição vinculada, fornecedor/nota fiscal também estão implicitamente pendentes,
    # mas já cobertos pela pendência "Aquisição não vinculada" acima, para não duplicar o aviso.

    return pendencias


def montar_saida_patrimonio(patrimonio: Patrimonio) -> dict:
    """Monta o dict de resposta da API incluindo os campos calculados de pendência e exibição."""
    from app.schemas.patrimonio import PatrimonioOut

    pendencias = calcular_pendencias(patrimonio)
    dados = PatrimonioOut.model_validate(patrimonio).model_dump()
    dados["pendencias"] = pendencias
    dados["status_cadastro"] = "completo" if not pendencias else "incompleto"
    dados["item_descricao"] = patrimonio.item.descricao if patrimonio.item else None
    if patrimonio.local:
        dados["local_descricao"] = patrimonio.local.nome
    elif patrimonio.setor:
        dados["local_descricao"] = patrimonio.setor.nome
    else:
        dados["local_descricao"] = None
    return dados
