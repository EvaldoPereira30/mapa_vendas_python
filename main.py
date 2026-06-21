from pathlib import Path
from io import StringIO
import pandas as pd


def numero_br(valor):
    if pd.isna(valor):
        return 0.0

    valor = str(valor).strip()

    if valor == "":
        return 0.0

    valor = valor.replace(".", "")
    valor = valor.replace(",", ".")

    try:
        return float(valor)
    except:
        return 0.0


def ler_txt_a_partir_do_cabecalho(caminho: Path) -> pd.DataFrame:
    with open(caminho, encoding="cp1252") as arquivo:
        linhas = arquivo.readlines()

    linha_cabecalho = None

    for i, linha in enumerate(linhas):
        if linha.startswith("CodFilial"):
            linha_cabecalho = i
            break

    if linha_cabecalho is None:
        raise ValueError(f"Cabeçalho CodFilial não encontrado em {caminho.name}")

    conteudo_limpo = "".join(linhas[linha_cabecalho:])

    df = pd.read_csv(StringIO(conteudo_limpo), sep=",", dtype=str)

    df.columns = df.columns.str.strip()
    df["CodFilial"] = df["CodFilial"].ffill()

    return df


def limpar_linhas_sem_produto(df: pd.DataFrame, coluna_produto: str) -> pd.DataFrame:
    df = df[df[coluna_produto].notna()]
    df = df[df[coluna_produto].str.strip() != ""]
    return df


def gerar_lojas(estoque: pd.DataFrame, vendas: pd.DataFrame) -> pd.DataFrame:
    lojas = estoque.merge(
        vendas,
        how="outer",
        left_on=["CodFilial", "CodProduto"],
        right_on=["CodFilial", "CódigoProduto"],
        suffixes=("_est", "_ven"),
    )

    estoque_cd = estoque[estoque["CodFilial"] == "900"][
        ["CodProduto", "QtEstoqueComercial"]
    ].copy()

    estoque_cd = estoque_cd.rename(
        columns={
            "CodProduto": "CD PROD",
            "QtEstoqueComercial": "QUANTIDADE ESTOQUE CD ATUAL",
        }
    )

    lojas["CD PROD"] = lojas["CodProduto"].fillna(lojas["CódigoProduto"])

    lojas = lojas.merge(
        estoque_cd,
        how="left",
        on="CD PROD",
    )

    lojas["PRODUTO"] = lojas["Descricao"].fillna(lojas["DescriçãoProduto"])
    lojas["Ean"] = lojas["EAN_est"].fillna(lojas["EAN_ven"]).fillna("S/ EAN Ativo")
    lojas["FABRICANTE"] = lojas["Fabricante_est"].fillna(lojas["Fabricante_ven"])
    lojas["Linha"] = lojas["Linha_est"].fillna(lojas["Linha_ven"])

    lojas_final = lojas[
        [
            "CodFilial",
            "CD PROD",
            "PRODUTO",
            "Ean",
            "FABRICANTE",
            "Linha",
            "StatusProduto",
            "QtEstoqueComercial",
            "QUANTIDADE ESTOQUE CD ATUAL",
            "MediaF",
            "QtdeItem",
            "VlrLiqVenda",
            "QtdeItem.1",
            "VlrLiqVenda.1",
            "QtdeItem.2",
            "VlrLiqVenda.2",
            "QtdeItem.3",
            "VlrLiqVenda.3",
        ]
    ].copy()

    lojas_final = lojas_final.rename(
        columns={
            "CodFilial": "FILIAL",
            "StatusProduto": "Status Produtos",
            "QtEstoqueComercial": "QUANTIDADE ESTOQUE FILIAL ATUAL",
            "MediaF": "MEDIAF UN",
            "QtdeItem": "QTDE ITENS ATUAL",
            "VlrLiqVenda": "VENDA LIQUIDA ATUAL",
            "QtdeItem.1": "QT MÊS -1",
            "VlrLiqVenda.1": "VLR MÊS -1",
            "QtdeItem.2": "QT MÊS -2",
            "VlrLiqVenda.2": "VLR MÊS -2",
            "QtdeItem.3": "QT MÊS -3",
            "VlrLiqVenda.3": "VLR MÊS -3",
        }
    )

    lojas_final = lojas_final.fillna(0)

    return lojas_final


def gerar_rede(estoque: pd.DataFrame, vendas: pd.DataFrame) -> pd.DataFrame:
    estoque_lojas = estoque[estoque["CodFilial"] != "900"]
    estoque_cd = estoque[estoque["CodFilial"] == "900"]

    estoque_agrupado = estoque_lojas.groupby("CodProduto", as_index=False).agg(
        {"QtEstoqueComercial": "sum"}
    )

    estoque_agrupado = estoque_agrupado.rename(
        columns={"QtEstoqueComercial": "EST UN FILIAL GERAL"}
    )

    estoque_cd_base = estoque_cd[
        [
            "CodProduto",
            "EAN",
            "Descricao",
            "Fabricante",
            "Linha",
            "StatusProduto",
            "MediaF",
            "QtEstoqueComercial",
        ]
    ].copy()

    estoque_cd_base = estoque_cd_base.rename(
        columns={
            "CodProduto": "CD PROD",
            "EAN": "Ean",
            "Descricao": "PRODUTO",
            "Fabricante": "FABRICANTE",
            "StatusProduto": "Status Produtos",
            "MediaF": "MEDIAF UN GERAL",
            "QtEstoqueComercial": "EST UN CD GERAL",
        }
    )

    vendas_agrupadas = vendas.groupby("CódigoProduto", as_index=False).agg(
        {
            "QtdeItem": "sum",
            "VlrLiqVenda": "sum",
            "QtdeItem.1": "sum",
            "VlrLiqVenda.1": "sum",
            "QtdeItem.2": "sum",
            "VlrLiqVenda.2": "sum",
            "QtdeItem.3": "sum",
            "VlrLiqVenda.3": "sum",
        }
    )

    vendas_agrupadas = vendas_agrupadas.rename(
        columns={
            "CódigoProduto": "CD PROD",
            "QtdeItem": "QTDE ITENS ATUAL",
            "VlrLiqVenda": "VENDA LIQUIDA ATUAL",
            "QtdeItem.1": "QT MÊS -1",
            "VlrLiqVenda.1": "VLR MÊS -1",
            "QtdeItem.2": "QT MÊS -2",
            "VlrLiqVenda.2": "VLR MÊS -2",
            "QtdeItem.3": "QT MÊS -3",
            "VlrLiqVenda.3": "VLR MÊS -3",
        }
    )

    rede = estoque_cd_base.merge(
        estoque_agrupado,
        how="outer",
        left_on="CD PROD",
        right_on="CodProduto",
    )

    rede = rede.merge(vendas_agrupadas, how="outer", on="CD PROD")

    rede["Ean"] = rede["Ean"].fillna("S/ EAN Ativo")

    rede = rede[
        [
            "Ean",
            "CD PROD",
            "PRODUTO",
            "FABRICANTE",
            "Linha",
            "Status Produtos",
            "EST UN FILIAL GERAL",
            "EST UN CD GERAL",
            "MEDIAF UN GERAL",
            "QTDE ITENS ATUAL",
            "VENDA LIQUIDA ATUAL",
            "QT MÊS -1",
            "VLR MÊS -1",
            "QT MÊS -2",
            "VLR MÊS -2",
            "QT MÊS -3",
            "VLR MÊS -3",
        ]
    ].copy()

    rede = rede.fillna(0)

    return rede


arquivo_estoque = Path("entrada/Estoque Abbott.txt")
arquivo_vendas = Path("entrada/Vendas Abbott.txt")

estoque = ler_txt_a_partir_do_cabecalho(arquivo_estoque)
estoque = limpar_linhas_sem_produto(estoque, "CodProduto")

vendas = ler_txt_a_partir_do_cabecalho(arquivo_vendas)
vendas = limpar_linhas_sem_produto(vendas, "CódigoProduto")

estoque["MediaF"] = estoque["MediaF"].apply(numero_br)
estoque["QtEstoqueComercial"] = estoque["QtEstoqueComercial"].apply(numero_br)

colunas_vendas = [
    "QtdeItem",
    "VlrLiqVenda",
    "QtdeItem.1",
    "VlrLiqVenda.1",
    "QtdeItem.2",
    "VlrLiqVenda.2",
    "QtdeItem.3",
    "VlrLiqVenda.3",
]

for coluna in colunas_vendas:
    vendas[coluna] = vendas[coluna].apply(numero_br)

lojas = gerar_lojas(estoque, vendas)
rede = gerar_rede(estoque, vendas)

pasta_saida = Path("saida")
pasta_saida.mkdir(exist_ok=True)

arquivo_saida = pasta_saida / "Mapa de Vendas Teste.xlsx"

with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
    rede.to_excel(writer, sheet_name="Rede", index=False)
    lojas.to_excel(writer, sheet_name="Lojas", index=False)

print("Rede gerada:", len(rede), "linhas")
print("Lojas geradas:", len(lojas), "linhas")
print()
print(f"Arquivo gerado com sucesso: {arquivo_saida}")