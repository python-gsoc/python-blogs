# Blog e plataforma python-GSoC

Blog e plataforma de gerenciamento do PSF para rodar o GSoC

## Status da ferramenta

[![Status Ferramenta](https://travis-ci.com/sounak98/python-blogs.svg)](https://travis-ci.com/sounak98/python-blogs)

## Instalação

- Testado com python 3.7.3

Para instalar as dependências de desenvolvimento use:

```
$ pip install -r requirements.txt
```

Para definir as configurações, copie settings_local.py.template para a raiz do diretório:
```
cp settings_local.py.template settings_local.py
```

## Use

```python
python manage.py runserver 0.0.0.0:8000
```

Você pode acessar o site com a barra de login: http://127.0.0.1:8000/en/?edit

Usuário padrão/senha é `admin` para o superusuário

Os usuários padrão dos alunos são `Test-Student1`, `Test-Student2` com a senha `^vM7d5*wK2R77V`


## Contribuição
Pull requests são bem-vindos. Para mudanças importantes, por favor, abra uma issue primeiro para discutir o que você gostaria de mudar.


## Git

Para ver o diff's no banco de dados, você precisará executar o seguinte comando:
```
$ git config --local include.path ../.gitconfig
```
Também verifique se o sqlite3 está disponível.

## Virtualenv

O virtual environment é uma ferramenta que ajuda a manter as dependências exigidas por diferentes projetos separados, criando ambientes virtuais em Python isolados para eles. Isso significa que cada projeto pode ter suas próprias dependências, independentemente de quais dependências cada outro projeto possui. Usamos um módulo chamado `virtualenv`, que é uma ferramenta para criar ambientes Python isolados. `virtualenv` cria uma pasta que contém todos os executáveis necessários para usar os pacotes que um projeto Python precisaria.

### Instalando virtualenv

```bash
$ pip install virtualenv
```

### Teste sua instalação

```bash
$ virtualenv --version
```

### Usando virtualenv

Você pode criar um virtualenv usando o seguinte comando:

```bash
$ virtualenv virtualenv_name
```

Depois de executar este comando, um diretório chamado my_name será criado. Este é o diretório que contém todos os executáveis necessários para usar os pacotes que um projeto Python precisaria. É aqui que os pacotes do Python serão instalados.

Agora, depois de criar o virtual environment, você precisa ativá-lo. Lembre-se de ativar o virtual environment relevante toda vez que você trabalha no projeto. Isso pode ser feito usando o seguinte comando:

```
$ source virtualenv_name/bin/activate
```

Depois que o virtual environment for ativado, o nome do seu virtual environment aparecerá no lado esquerdo do terminal. Isso permitirá que você saiba que o virtual environment está ativo no momento.
Agora você pode instalar dependências relacionadas ao projeto no virtual environment. Por exemplo, se você estiver usando o Django 1.9 para um projeto, você pode instalá-lo como você instala outros pacotes.


```
(virtualenv_name) $ pip install Django==1.9
```

Quando terminar o trabalho, você poderá desativar o virtual environment pelo seguinte comando:

```
(virtualenv_name) $ deactivate
```

Agora você voltará à instalação Python padrão do sistema.



