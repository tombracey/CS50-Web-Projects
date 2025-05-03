import random
from django.shortcuts import render
from markdown import Markdown
from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def convert_to_html(title):
    content = util.get_entry(title)
    markdowner = Markdown()
    if content:
        return markdowner.convert(content)
    else:
        return None
    
def entry(request, title):
    content = convert_to_html(title)
    if content:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": content
        })
    else:
        return render(request, "encyclopedia/not_found.html")
    
def search(request):
    if request.method == "POST":
        entry_search = request.POST['q']
        content = convert_to_html(entry_search)
        if content:
            return render(request, "encyclopedia/entry.html", {
                "title": entry_search,
                "content": content
            })
        else:
            entries = util.list_entries()
            results = []
            for entry in entries:
                if entry_search.lower() in entry.lower():
                    results.append(entry)
            return render(request, "encyclopedia/search.html", {
                "results": results
            })
        
def new_entry(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new_entry.html")
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        existing_title = util.get_entry(title)
        if existing_title:
            return render(request, "encyclopedia/exist_error.html")
        else:
            util.save_entry(title, content)
            content = convert_to_html(title)
            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "content": content
            })
        
def edit_entry(request):
    if request.method == "POST":
        title = request.POST['title']
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit_entry.html", {
            "title": title,
            "content": content
        })
    
def submit_edit(request):
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        util.save_entry(title, content)
        content = convert_to_html(title)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": content
        })
    
def random_entry (request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    content = convert_to_html(random_entry)
    return render(request, "encyclopedia/entry.html", {
        "title": random_entry,
        "content": content
    })