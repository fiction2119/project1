from django import forms
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.urls import reverse
from markdown2 import Markdown
from . import util

markdowner = Markdown()

class EditForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Content", widget=forms.Textarea)

class NewForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Content", widget=forms.Textarea)

def index(request):
    if "titles" not in request.session:
        request.session["titles"] = []
        for title in util.list_entries():
            if title not in request.session["titles"]:
                request.session["titles"].append(title)

    return render(request, "encyclopedia/index.html", {
        "entries": request.session["titles"]
    })

def title(request, name):
    markdown = markdowner.convert(util.get_entry(name))

    return render(request, "encyclopedia/title.html", {
        "name": markdown,
    })

def add(request):
    if request.method == "POST":
        form = NewForm(request.POST)
        title = request.POST.get("title")
        content = request.POST.get("content")
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title in util.list_entries():
                return HttpResponseNotFound("Error: Entry already exists.")
            else:
                util.save_entry(title, content)
                request.session["titles"] += [title]
                return render(request, "encyclopedia/index.html", {
                    "entries": util.list_entries()
                })
        else:
            return HttpResponseNotFound("Error: Form isn't valid.")
    else:
        return render(request, "encyclopedia/add.html", {
            "form":NewForm(),
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

def edit(request):
    if request.method == "POST":
        form = EditForm(request.POST)