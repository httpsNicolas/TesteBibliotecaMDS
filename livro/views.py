from datetime import date, datetime
from django.shortcuts import redirect, render
from django.http import HttpResponse
from usuarios.models import Usuario
from .models import Emprestimos, Livros, Categoria
from .forms import CadastroLivro, CategoriaLivro
from django import forms
from django.db.models import Q
# Create your views here.

URL_HOME = "livro/home"

def home(request):
    if request.session.get('usuario'):
        usuario = Usuario.objects.get(id=request.session['usuario'])
        status_categoria = request.GET.get('cadastro_categoria')

        busca_nome = request.GET.get('busca_nome') or ''
        autor = request.GET.get('autor') or ''
        categoria_id = request.GET.get('categoria') or ''
        emprestado = request.GET.get('emprestado') or ''

        livros = Livros.objects.filter(usuario=usuario)

        if busca_nome:
            livros = livros.filter(nome__icontains=busca_nome)

        if autor:
            livros = livros.filter(autor__icontains=autor)

        if categoria_id:
            livros = livros.filter(categoria_id=categoria_id)

        if emprestado == '1': 
            livros = livros.filter(emprestado=True)
        elif emprestado == '0': 
            livros = livros.filter(emprestado=False)

        total_livros = livros.count()

        form = CadastroLivro()
        form.fields['usuario'].initial = request.session['usuario']
        form.fields['categoria'].queryset = Categoria.objects.filter(usuario=usuario)
        form_categoria = CategoriaLivro()
        usuarios = Usuario.objects.all()

        livros_emprestar = Livros.objects.filter(usuario=usuario, emprestado=False)
        livros_emprestados = Livros.objects.filter(usuario=usuario, emprestado=True)

        return render(request, 'home.html', {
            'livros': livros,
            'usuario_logado': request.session.get('usuario'),
            'form': form,
            'status_categoria': status_categoria,
            'form_categoria': form_categoria,
            'usuarios': usuarios,
            'livros_emprestar': livros_emprestar,
            'total_livro': total_livros,
            'livros_emprestados': livros_emprestados,
            'busca_nome': busca_nome.strip(),
            'autor': autor.strip(),
            'categoria_id': categoria_id,
            'emprestado': emprestado,
            'categorias': Categoria.objects.filter(usuario=usuario),
        })
    else:
        return redirect('/auth/login/?status=2')


def ver_livros(request, id):
    if request.session.get('usuario'):
        livro = Livros.objects.get(id = id)
        if request.session.get('usuario') == livro.usuario.id:
            usuario = Usuario.objects.get(id = request.session['usuario'])
            categoria_livro = Categoria.objects.filter(usuario = request.session.get('usuario'))
            emprestimos = Emprestimos.objects.filter(livro = livro)
            form = CadastroLivro()
            form.fields['usuario'].initial = request.session['usuario']
            form.fields['categoria'].queryset = Categoria.objects.filter(usuario = usuario)
            
            form_categoria = CategoriaLivro()
            usuarios = Usuario.objects.all()

            livros_emprestar = Livros.objects.filter(usuario = usuario).filter(emprestado = False)
            livros_emprestados = Livros.objects.filter(usuario = usuario).filter(emprestado = True)
            
            return render(request, 'ver_livro.html', {'livro': livro,
                                                      'categoria_livro': categoria_livro,
                                                      'emprestimos': emprestimos,
                                                      'usuario_logado': request.session.get('usuario'),
                                                      'form': form,
                                                      'id_livro': id,
                                                      'form_categoria': form_categoria,
                                                      'usuarios': usuarios,
                                                      'livros_emprestar': livros_emprestar,
                                                      'livros_emprestados': livros_emprestados})
        else:
            return HttpResponse('Esse livro não é seu')
    return redirect('/auth/login/?status=2')
    

def cadastrar_livro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        autor = request.POST.get('autor')
        co_autor = request.POST.get('co_autor')
        categoria_id = request.POST.get('categoria')
        id_usuario = request.session.get('usuario') 

        if not id_usuario:
            return HttpResponse('Usuário não autenticado.')

        if int(id_usuario) == int(request.POST.get('usuario', 0)):
            try:
                user = Usuario.objects.get(id=id_usuario)
                categoria = Categoria.objects.get(id=categoria_id)
            except Usuario.DoesNotExist:
                return HttpResponse('Usuário inválido.')
            except Categoria.DoesNotExist:
                return HttpResponse('Categoria inválida.')

            livro = Livros(
                nome=nome,
                autor=autor,
                co_autor=co_autor,
                data_cadastro=date.today(),
                emprestado=False,
                categoria=categoria,
                usuario=user
            )
            livro.save()
            return redirect(URL_HOME)
        else:
            return HttpResponse('Pare de ser um usuário malandrinho. Não foi desta vez.')
    else:
        return HttpResponse('Método inválido.')
def excluir_livro(id):
    Livros.objects.get(id = id).delete()
    return redirect(URL_HOME)

def cadastrar_categoria(request):
    form = CategoriaLivro(request.POST)
    nome = form.data['nome']
    descricao = form.data['descricao']
    id_usuario = request.POST.get('usuario')
    if int(id_usuario) == int(request.session.get('usuario')):
        user = Usuario.objects.get(id = id_usuario)
        categoria = Categoria(nome = nome, descricao = descricao, usuario = user )
        categoria.save()
        return redirect('/livro/home?cadastro_categoria=1')
    else:
        return HttpResponse('Pare de ser um usuário malandrinho. Não foi desta vez.')

    
def cadastrar_emprestimo(request):
    if request.method == 'POST':
        nome_emprestado = request.POST.get('nome_emprestado')
        nome_emprestado_anonimo = request.POST.get('nome_emprestado_anonimo')
        livro_emprestado = request.POST.get('livro_emprestado')
        
        if nome_emprestado_anonimo:
            emprestimo = Emprestimos(nome_emprestado_anonimo = nome_emprestado_anonimo,
                                    livro_id = livro_emprestado)
        else:
            emprestimo = Emprestimos(nome_emprestado_id=nome_emprestado,
                                    livro_id = livro_emprestado)
        emprestimo.save()

        livro = Livros.objects.get(id = livro_emprestado)
        livro.emprestado = True
        livro.save()


        return redirect(URL_HOME)

def devolver_livro(request):
    livro_id = request.POST.get('id_livro_devolver')
    livro_devolver = Livros.objects.get(id = id)
    livro_devolver.emprestado = False
    livro_devolver.save()
    
    emprestimo_devolver = Emprestimos.objects.get(Q(livro = livro_devolver) & Q(data_devolucao = None) )
    emprestimo_devolver.data_devolucao = datetime.now() 
    emprestimo_devolver.save()

    return redirect(URL_HOME)

def alterar_livro(request):
    livro_id = request.POST.get('livro_id')
    nome_livro = request.POST.get('nome_livro')
    autor = request.POST.get('autor')
    co_autor = request.POST.get('co_autor')
    categoria_id = request.POST.get('categoria_id')

    categoria = Categoria.objects.get(id = categoria_id)
    livro = Livros.objects.get(id = livro_id)
    if livro.usuario.id == request.session['usuario']:
        livro.nome = nome_livro
        livro.autor = autor
        livro.co_autor = co_autor
        livro.categoria = categoria
        livro.save()
        return redirect(f'/livro/ver_livro/{livro_id}')
    else:
        return redirect('/auth/sair')

def seus_emprestimos(request):
    usuario = Usuario.objects.get(id = request.session['usuario'])
    emprestimos = Emprestimos.objects.filter(nome_emprestado = usuario)
    


    return render(request, 'seus_emprestimos.html', {'usuario_logado': request.session['usuario'],
                                                    'emprestimos': emprestimos})

def processa_avaliacao(request):
    id_emprestimo = request.POST.get('id_emprestimo')
    opcoes = request.POST.get('opcoes')
    id_livro = request.POST.get('id_livro')
    #Falta: Verificar segurança
    #Falta: Não permitir avaliação de livro nao devolvido
    #Falta: Colocar as estrelas
    emprestimo = Emprestimos.objects.get(id = id_emprestimo)
    emprestimo.avaliacao = opcoes
    emprestimo.save()
    return redirect(f'/livro/ver_livro/{id_livro}')
