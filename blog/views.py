from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post,Comment
from .forms import *
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin



    
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Post

def home(request):
    # Fetches all posts and orders them by date
    posts = Post.objects.all().order_by('-date_posted')

    # Create separate query for posts by the logged-in user if authenticated
    if request.user.is_authenticated:
        user_posts = Post.objects.filter(author=request.user).order_by('-date_posted')
        # Prepare context with user-specific posts and additional user info
        context = {
            'user_posts': user_posts,  # Posts created by the logged-in user
            'posts': posts,            # All posts, including user's own
            'username': request.user.username,
            'email': request.user.email
        }
    else:
        # Context for non-authenticated users
        context = {
            'posts': posts
        }

    return render(request, 'home.html', context)



def signup(request):
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log the user in immediately after signing up
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def post_detail(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)
        comment = post.comments.all()
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.post = post
                comment.save()
                return redirect('post-detail', pk=post.pk)
        else:
            form = CommentForm()
        return render(request, 'post_detail.html', {'post': post, 'form': form,"comment":comment})
    
    return redirect('/login')
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'  # specify your template name

    def form_valid(self, form):
        form.instance.author = self.request.user  # set the author of the post to the current user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('home') 

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content',"image"]  # Adjust fields based on your Post model
    template_name = 'post_update.html'
    success_url = reverse_lazy('home') 

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('home')  # Redirect to the home page after deleting

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author