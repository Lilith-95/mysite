from django.shortcuts import render_to_response, get_object_or_404
from .models import Blog, BlogType
from read_statistics.utils import read_statistics_once_read
from django.core.paginator import Paginator
from django.conf import settings

def get_blog_list_common_date(request, blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER) # 每2页进行分页
    page_num = request.GET.get('page', 1 ) # 获取url页面参数（GET请求）,page是url参数，若需改变，后面blog_list.html也要改变
    page_of_blogs = paginator.get_page(page_num) # 用户输入非符合，都能返回第一页
    currentr_page_num = page_of_blogs.number # 获取当前页码
    # page_range = [i for i in range(currentr_page_num - 2,currentr_page_num+3) if i > 0 and (i <= currentr_page_num)]
    # page_range = [currentr_page_num - 2, currentr_page_num - 1, currentr_page_num, currentr_page_num + 1, currentr_page_num + 2] 
    page_range = list(range(max(currentr_page_num - 2, 1), currentr_page_num )) + \
                 list(range(currentr_page_num, min(currentr_page_num + 2, currentr_page_num) + 1))
    # 加上省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >=2:
        page_range.append('...')
    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1) # 将1插入索引0的位置
    if page_range[-1] != paginator.num_pages: # paginator.num_pages获取总页数
        page_range.append(paginator.num_pages)
    # 获取日期归档对应博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order='DESC') 
    blog_date_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                        created_time__month=blog_date.month).count()
        blog_date_dict[blog_date] = blog_count

    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = BlogType.objects.all() # 这里是控制博客列表页的分类
    context['blog_dates'] = blog_date_dict    
    return context

def blog_list(request): # 博客列表
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_date(request, blogs_all_list)
    return render_to_response('blog/blog_list.html', context)


def blogs_with_type(request, blog_type_pk):  # 博客标签页 这里的blog_type_pk是urls.py中的
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_date(request, blogs_all_list)
    context['blog_type'] = blog_type 
    return render_to_response('blog/blog_with_type.html', context)


def blogs_with_date(request, year, month): # 按月分类
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_list_common_date(request, blogs_all_list)
    context['blogs_with_date'] = '{}年{}月'.format(year, month)
    return render_to_response('blog/blog_with_date.html', context)


def blog_detail(request,  blog_pk): # 博客内容页
    blog = get_object_or_404(Blog, pk=blog_pk)  #Blog是blog下的models.py中的Blog函数,pk是传入的参数
    read_cookie_key = read_statistics_once_read(request, blog)

    context = {}  
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    response = render_to_response('blog/blog_detail.html', context)
    response.set_cookie(read_cookie_key, 'ture') # 阅读cookie标记
    return response