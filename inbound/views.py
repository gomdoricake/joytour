from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import GroupForm, AgentForm
from .models import Agent, Group


@login_required
def index(request): 
    return render(request, 'inbound/index.html')\

@login_required
def agent_list(request): 
    agent_list = Agent.objects.all()

    context = {
        'agent_list': agent_list,
    }
    return render(request, 'inbound/agent_list.html', context)

@login_required
def agent_detail(request, pk): 
    agent = Agent.objects.get(pk=pk)

    context = {
        'agent': agent
    }
    return render(request, 'inbound/agent_detail.html', context)

@login_required
def create_agent(request): 
    form = AgentForm(request.POST)
    if request.method == 'POST': 
        
        if form.is_valid(): 
            code = form.cleaned_data['code']
            form.save()

            return redirect('inbound:agent_list')
    else: 
        context = {
            'form': form
        }
        return render(request, 'inbound/create_agent.html', context)

@login_required
def group_list(request): 
    group_list = Group.objects.all()

    context = {
        'group_list': group_list
    }
    return render(request, 'inbound/group_list.html', context)

@login_required
def group_detail(request, pk): 
    group = Group.objects.get(pk=pk)

    context = {
        'group': group
    }
    return render(request, 'inbound/group_detail.html', context)

@login_required
def create_group(request): 
    form = GroupForm(request.POST)
    if request.method == 'POST': 
        if form.is_valid(): 
            form.save() 

            return redirect('inbound:group_list')
        
    else: 
        context = {
            'form': form,
        }
        return render(request, 'inbound/create_group.html', context)
