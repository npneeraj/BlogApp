from . import views
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('tag/<slug:tag_slug>/', views.search_by_tag, name='search_by_tag'),
    path('search/', views.search_blog, name='search_blog'),
    path('trigram_search/', views.trigram_search, name='trigram_search'),
    path('blog/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('blog/<int:pk>/share/', views.share_blog, name='share_blog'),
]
