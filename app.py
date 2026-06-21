import subprocess
import sys
import tkinter as tk
from tkinter import messagebox


def gerar_relatorio():
    modo = modo_var.get()

    try:
        resultado = subprocess.run(
            [sys.executable, "main.py", modo],
            capture_output=True,
            text=True,
            check=True,
        )

        messagebox.showinfo(
            "Relatório gerado",
            "Mapa de Vendas gerado com sucesso!\n\n" + resultado.stdout
        )

    except subprocess.CalledProcessError as erro:
        mensagem_erro = erro.stderr or erro.stdout or "Erro desconhecido."

        messagebox.showerror(
            "Erro ao gerar relatório",
            mensagem_erro
        )


janela = tk.Tk()
janela.title("Mapa de Vendas Python")
janela.geometry("520x320")
janela.resizable(False, False)

titulo = tk.Label(
    janela,
    text="Mapa de Vendas",
    font=("Arial", 18, "bold")
)
titulo.pack(pady=20)

subtitulo = tk.Label(
    janela,
    text="Selecione o tipo de relatório:",
    font=("Arial", 11)
)
subtitulo.pack(pady=5)

modo_var = tk.StringVar(value="padrao")

opcao_padrao = tk.Radiobutton(
    janela,
    text="Padrão - 3 meses",
    variable=modo_var,
    value="padrao",
    font=("Arial", 11)
)
opcao_padrao.pack(anchor="w", padx=80)

opcao_anual = tk.Radiobutton(
    janela,
    text="Anual / todos os meses do arquivo",
    variable=modo_var,
    value="anual",
    font=("Arial", 11)
)
opcao_anual.pack(anchor="w", padx=80)

botao = tk.Button(
    janela,
    text="Gerar Relatório",
    command=gerar_relatorio,
    font=("Arial", 12, "bold"),
    width=20,
    height=2
)
botao.pack(pady=25)

rodape = tk.Label(
    janela,
    text="Arquivos devem estar na pasta entrada/",
    font=("Arial", 9)
)
rodape.pack()

janela.mainloop()