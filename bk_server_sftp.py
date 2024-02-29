import os
import re
import paramiko

# Dados dos servidores SFTP
servidores = ['0.0.0.0', '0.0.0.0', '0.0.0.0']
username = 'user'
password = 'pass'
remote_path = '/bkp'
local_path = '/srv/ftp/BACKUP'

def excluir_arquivos_similares(nome_arquivo):
    # Extrai a parte do identificador do nome do arquivo, ignorando a data e a hora
    match = re.match(r"(cli_emp\d+)-.*", nome_arquivo)
    if match:
        identificador = match.group(1)
        # Lista todos os arquivos no diretório local
        for arquivo_local in os.listdir(local_path):
            # Verifica se o arquivo local contém o identificador
            if re.match(rf"{identificador}.*\.zip", arquivo_local):
                # Caminho completo do arquivo a ser excluído
                arquivo_para_excluir = os.path.join(local_path, arquivo_local)
                print(f"Excluindo arquivo existente: {arquivo_para_excluir}")
                os.remove(arquivo_para_excluir)

# Função para conectar ao servidor e baixar os arquivos encontrados
def baixar_arquivos_sftp(hostname):
    try:
        # Conexão SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)

        # Cliente SFTP
        sftp = ssh.open_sftp()

        # Listar arquivos no diretório remoto
        arquivos = sftp.listdir(remote_path)
        if arquivos:
            for arquivo in arquivos:
                # Antes de baixar, verifica e exclui arquivos similares
                excluir_arquivos_similares(arquivo)

                remote_filepath = os.path.join(remote_path, arquivo)
                local_filepath = os.path.join(local_path, arquivo)

                # Download do arquivo
                print(f'Baixando {arquivo} de {hostname}...')
                sftp.get(remote_filepath, local_filepath)
                print(f'{arquivo} baixado com sucesso.')
        else:
            print(f'Nenhum arquivo encontrado em {hostname}.')

        # Fechamento das conexões
        sftp.close()
        ssh.close()
    except Exception as e:
        print(f'Ocorreu um erro ao acessar {hostname}: {e}')

# Iterar sobre os servidores para verificar e baixar os arquivos
for servidor in servidores:
    print(f'Conectando ao servidor {servidor}...')
    baixar_arquivos_sftp(servidor)
