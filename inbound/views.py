from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import GroupForm, AgentForm
from .models import Agent, Group, GroupFile
from django.forms import formset_factory
from .forms import GroupFileForm, ItineraryForm, ItineraryFormSet
from invoices.models import Invoice, Meal, Attraction, Vehicle, GuideInvoice, Tip, \
                                    MealType, AttractionType, VehicleType, GuideInvoiceType, \
                                    GuideTipType, DriverTipType


@login_required
def index(request): 
    return render(request, 'inbound/index.html')

@login_required
def tariff(request): 
    mealtype_list = MealType.objects.all().order_by('-id')
    attractiontype_list = AttractionType.objects.all().order_by('-id')
    vehicletype_list = VehicleType.objects.all().order_by('-id')
    guideinvoicetype_list = GuideInvoiceType.objects.all().order_by('-id')
    guide_tip = GuideTipType.objects.all().order_by('-id')
    driver_tip = DriverTipType.objects.all().order_by('-id')

    context = {
        'mealtype_list': mealtype_list, 
        'attractiontype_list': attractiontype_list,
        'vehicletype_list': vehicletype_list,
        'guideinvoicetype_list': guideinvoicetype_list,
        'guide_tip': guide_tip,
        'driver_tip': driver_tip
    } 
    return render(request, 'inbound/tariff.html', context)

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
def update_agent(request, pk): 
    agent = get_object_or_404(Agent, pk=pk)

    if agent: 
        if request.method == 'POST': 
            form = AgentForm(request.POST, instance=agent)

            if form.is_valid():
                form.save()

                return redirect('inbound:agent_detail', pk=pk)
            else: 
                return redirect('inbound:update_agent')

        else: 
            
            form = AgentForm(instance=agent) 
            
            context = {
                'agent': agent,
                'form': form
            }
            
            return render(request, 'inbound/create_agent.html', context)
                

@login_required
def delete_agent(request, pk): 
    agent = get_object_or_404(Agent, pk=pk)

    if agent: 
        agent.delete()

    return redirect('inbound:agent_list')

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
    
    if Invoice.objects.filter(pk=pk).exists(): 
        invoice = Invoice.objects.get(pk=pk)
        meals = Meal.objects.filter(invoice=invoice)
        attractions = Attraction.objects.filter(invoice=invoice)
        vehicles = Vehicle.objects.filter(invoice=invoice)
        guideinvoices = GuideInvoice.objects.filter(invoice=invoice)
        tips = Tip.objects.filter(invoice=invoice)

        operation_fee = invoice.agent.operation_fee if invoice.agent and invoice.agent.operation_fee else 0
        invoice.grand_total = invoice.grand_total + operation_fee

        invoice.save()

        context = {
            'group': group,
            'invoice': invoice,
            'meals': meals,
            'attractions': attractions,
            'vehicles': vehicles, 
            'guideinvoices': guideinvoices,
            'tips': tips
        }
        return render(request, 'inbound/group_detail.html', context)

    else:
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



@login_required
def update_group(request, pk): 
    print('pk: ' + str(pk))
    group = get_object_or_404(Group, pk=pk)
    
     
    if request.method == 'POST': 
        form = GroupForm(request.POST)

        if form.is_valid(): 
            group.guide = form.cleaned_data['guide'] if form.cleaned_data['guide'] else group.guide
            group.driver = form.cleaned_data['driver'] if form.cleaned_data['driver'] else group.driver
            group.agent = form.cleaned_data['agent'] if form.cleaned_data['agent'] else group.agent
            group.start_date = form.cleaned_data['start_date'] if form.cleaned_data['start_date'] else group.start_date
            group.agent_ref = form.cleaned_data['agent_ref'] if form.cleaned_data['agent_ref'] else group.agent_ref
            group.adt = form.cleaned_data['adt'] if form.cleaned_data['adt'] else group.adt
            group.chd = form.cleaned_data['chd'] if form.cleaned_data['chd'] else group.chd
            group.tc = form.cleaned_data['tc'] if form.cleaned_data['tc'] else group.tc
        
        group.save()

        return redirect('inbound:group_detail', pk)
    else: 
        initial_group = {
            'guide': group.guide,
            'driver': group.driver,
            'start_date': group.start_date,
            'agent': group.agent,
            'agent_ref': group.agent_ref,
            'adt': group.adt, 
            'chd': group.chd, 
            'tc': group.tc
        }
        form = GroupForm(
            initial = initial_group
        )
        context = {
            'form': form, 
            'group': group
        }
        return render(request, 'inbound/update_group.html', context)


@login_required
def delete_group(request, pk): 
    group = get_object_or_404(Group, pk=pk)
    if group: 
        group.delete()

    return redirect('inbound:index')



@login_required
def create_groupfile(request, pk): 
    
    group = get_object_or_404(Group, pk=pk)

    if request.method == 'POST': 
        form = GroupFileForm(request.POST)

        if form.is_valid():    

            if form.cleaned_data: 

                GroupFile.objects.update_or_create(
                    group=group,
                    defaults = {
                        'hotel': form.cleaned_data['hotel'], 
                        'meeting_board': form.cleaned_data['meeting_board']
                    }
                )

            return redirect('inbound:group_detail', pk=pk)
    
    else: 
        existing_file = getattr(group, 'groupfile', None)
        
        if existing_file: 
            initial_data = {
                'group': existing_file.group,
                'hotel': existing_file.hotel,
                'meeting_board': existing_file.meeting_board
            }
            form = GroupFileForm(initial=initial_data)
        else: 
            form = GroupFileForm()
        return render(request, 'inbound/create_groupfile.html', {'group': group, 'form': form})
        
            

    