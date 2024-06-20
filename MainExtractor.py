import os
import requests
from urllib.parse import urljoin, urlparse
import bs4
import tkinter as tk
from tkinter import messagebox, filedialog, Menu
from tkinter import ttk

# Função para baixar e salvar arquivos
def baixar_e_salvar(url_arquivo, caminho_download, progress_var):
    try:
        resposta = requests.get(url_arquivo, stream=True)
        total_size = int(resposta.headers.get('content-length', 0))
        block_size = 1024
        wrote = 0
        if resposta.status_code == 200:
            with open(caminho_download, "wb") as f:
                for data in resposta.iter_content(block_size):
                    wrote = wrote + len(data)
                    f.write(data)
                    progress_var.set((wrote / total_size) * 100)
                    root.update_idletasks()
            print(f"Arquivo {url_arquivo} salvo em {caminho_download}")
        else:
            print(f"Falha ao baixar {url_arquivo}")
    except Exception as e:
        print(f"Erro ao baixar {url_arquivo}: {e}")

# Função para iniciar o download
def iniciar_download():
    url = entry_url.get()
    if not url:
        messagebox.showerror("Erro", "Por favor, insira uma URL")
        return

    diretorio_download = filedialog.askdirectory()
    if not diretorio_download:
        messagebox.showerror("Erro", "Por favor, selecione um diretório para salvar os arquivos")
        return

    os.makedirs(diretorio_download, exist_ok=True)

    resposta = requests.get(url)
    if resposta.status_code != 200:
        messagebox.showerror("Erro", f"Falha ao carregar a página {url}")
        return

    conteudo = resposta.content

    caminho_html = os.path.join(diretorio_download, "index.html")
    with open(caminho_html, "wb") as f:
        f.write(conteudo)
    print(f"HTML da página salvo em {caminho_html}")

    sopa = bs4.BeautifulSoup(conteudo, "html.parser")

    extensoes_arquivo = {
        "css": "text/css",
        "js": "application/javascript",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "svg": "image/svg+xml",
        "woff": "font/woff",
        "woff2": "font/woff2",
        "ttf": "font/ttf",
        "eot": "application/vnd.ms-fontobject",
        "mp4": "video/mp4",
        "webm": "video/webm",
        "ogg": "video/ogg"
    }

    diretorios = {
        "css": os.path.join(diretorio_download, "css"),
        "js": os.path.join(diretorio_download, "js"),
        "imagens": os.path.join(diretorio_download, "imagens"),
        "fonts": os.path.join(diretorio_download, "fonts"),
        "videos": os.path.join(diretorio_download, "videos")
    }

    for nome_diretorio in diretorios.values():
        os.makedirs(nome_diretorio, exist_ok=True)

    recursos = (
        sopa.find_all("link", href=True) +
        sopa.find_all("script", src=True) +
        sopa.find_all("img", src=True) +
        sopa.find_all("source", src=True) +
        sopa.find_all("video", src=True)
    )

    progress_bar["maximum"] = len(recursos)
    for i, recurso in enumerate(recursos):
        atributo = "href" if recurso.name == "link" else "src"
        url_arquivo = urljoin(url, recurso.get(atributo))
        extensao_arquivo = os.path.splitext(url_arquivo)[-1].lower().lstrip('.')

        if extensao_arquivo in extensoes_arquivo:
            if extensao_arquivo in ["jpg", "jpeg", "png", "gif", "svg"]:
                nome_diretorio = diretorios["imagens"]
            elif extensao_arquivo in ["woff", "woff2", "ttf", "eot"]:
                nome_diretorio = diretorios["fonts"]
            elif extensao_arquivo in ["mp4", "webm", "ogg"]:
                nome_diretorio = diretorios["videos"]
            else:
                nome_diretorio = diretorios[extensao_arquivo]

            caminho_download = os.path.join(nome_diretorio, os.path.basename(urlparse(url_arquivo).path))
            baixar_e_salvar(url_arquivo, caminho_download, progress_var)
            progress_bar["value"] = i + 1
            root.update_idletasks()

    messagebox.showinfo("Concluído", "Download concluído")

# Funções para as opções do menu
def abrir_configuracoes():
    messagebox.showinfo("Configurações", "Aqui você pode configurar o programa.")

def abrir_sobre():
    messagebox.showinfo("Sobre", "Este é um programa para baixar arquivos de uma página web.")

def abrir_contato():
    messagebox.showinfo("Entre em Contato", "Entre em contato conosco pelo e-mail: exemplo@email.com")

# Interface gráfica
root = tk.Tk()
root.title("Web Page Downloader - Desenvolvido por: Davi Felipe")
root.geometry("500x300")

# Menu
menubar = Menu(root)
root.config(menu=menubar)

menu_arquivo = Menu(menubar)
menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
menu_arquivo.add_command(label="Configurações", command=abrir_configuracoes)
menu_arquivo.add_separator()
menu_arquivo.add_command(label="Sair", command=root.quit)

menu_ajuda = Menu(menubar)
menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
menu_ajuda.add_command(label="Sobre", command=abrir_sobre)
menu_ajuda.add_command(label="Entre em Contato", command=abrir_contato)

# Conteúdo da janela principal
tk.Label(root, text="Insira a URL da página web:").pack(pady=10)
entry_url = tk.Entry(root, width=50)
entry_url.pack(pady=5)

tk.Button(root, text="Iniciar Download", command=iniciar_download).pack(pady=20)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum
= 100)
progress_bar.pack(pady=10, fill=tk.X, padx=20)

root.mainloop()
