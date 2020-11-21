from django import forms
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from markdown2 import Markdown
from . import util

markdowner = Markdown()

class NewTitleForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Content", widget=forms.Textarea)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def title(request, name):
    markdown = markdowner.convert(util.get_entry(name))

    return render(request, "encyclopedia/title.html", {
        "name": markdown,
    })

def add(request):
    if request.method == "POST":
        form = NewTitleForm(request.POST)
        title = request.POST.get("title")
        content = request.POST.get("content")
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title in util.list_entries():
                return HttpResponseNotFound("Error: Entry already exists.")
            else:
                util.save_entry(title, content)
                return render(request, "encyclopedia/index.html", {
                    "entries": util.list_entries()
                })
        else:
            return HttpResponseNotFound("Error: Form isn't valid.")
    else:
        return render(request, "encyclopedia/add.html", {
            "form":NewTitleForm(),
        })

def search(request):

    if request.method == "GET":
        query = request.GET.get("q")
        matches = []

        for entry in util.list_entries():
            if query in entry:
                matches.append(entry)

        if util.get_entry(query) != None:
            return render(request, "encyclopedia/title.html", {
                "name":util.get_entry(query),
            })
        else:
            if not matches:
                return HttpResponseNotFound("Error: couldn't find an entry")
            else:
                return render(request, "encyclopedia/search.html", {
                    "matches":matches,
                    "query":query,
                    "entries": util.list_entries(),
                })
    else:
        return HttpResponseRedirect(reverse("encyclopedia:index"))    

def edit(request, name):
    if request.method == "POST":
       form = NewTitleForm(request.POST)
       title = request.POST.get("title")
       content = request.POST.get("content")
       if title.is_valid() and content.is_valid():
           content = form.cleaned_data["content"]
           title = form.cleaned_data["title"]

           if title in util.list_entries():
                util.save_entry(title, content)
           else:
               return HttpResponseNotFound("Error: Entry doesn't exist.")

    else:
        return render(request, "encyclopedia/edit.html", {
            "form":NewTitleForm(),
            "name":name,
        }) 
