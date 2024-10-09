from taggit.models import Tag
from django.core.mail import send_mail
from .forms import EmailBlogForm
from django.shortcuts import render, get_object_or_404, redirect
from . models import *
from django.core.paginator import Paginator
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from django.contrib.postgres.search import TrigramSimilarity
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login, logout
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after signing up
            return redirect('blog_list')
    else:
        form = UserCreationForm()
    return render(request, 'blog/signup.html', {'form': form})




def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('blog_list')  # Redirect to blog list after login
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'blog/login.html')



def custom_logout(request):
    logout(request)
    messages.success(request,'You have logged out Successfully!')
    return redirect('login') 

def blog_list(request):
    blogs = Blog.objects.all()
    paginator = Paginator(blogs, 5)  # 5 blogs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/blog_list.html', {'page_obj': page_obj})

def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'blog/blog_detail.html', {'blog': blog})



def search_by_tag(request, tag_slug=None):
    tag = get_object_or_404(Tag, slug=tag_slug)
    blogs = Blog.objects.filter(tags__in=[tag])
    return render(request, 'blog/blog_list.html', {'blogs': blogs})

def search_blog(request):
    query = request.GET.get('q')
    search_vector = SearchVector('title', 'body')
    search_query = SearchQuery(query)
    blogs = Blog.objects.annotate(rank=SearchRank(search_vector, search_query)) \
                        .filter(rank__gte=0.1).order_by('-rank')
    return render(request, 'blog/blog_search_results.html', {'blogs': blogs})



def trigram_search(request):
    query = request.GET.get('q')
    blogs = Blog.objects.annotate(similarity=TrigramSimilarity('title', query)) \
                        .filter(similarity__gt=0.3).order_by('-similarity')
    return render(request, 'blog/blog_search_results.html', {'blogs': blogs})



def add_comment(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        comment = Comment.objects.create(blog=blog, user=request.user, content=content)
        return redirect('blog_detail', pk=pk)

def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    return JsonResponse({'likes_count': comment.likes.count()})




def share_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        form = EmailBlogForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            blog_url = request.build_absolute_uri(blog.get_absolute_url())
            subject = f"{cd['name']} recommends you read {blog.title}"
            message = f"Read {blog.title} at {blog_url}\n\n{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@myblog.com', [cd['to']])
            return redirect('blog_detail', pk=pk)
    else:
        form = EmailBlogForm()
    return render(request, 'blog/share_blog.html', {'blog': blog, 'form': form})
