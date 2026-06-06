from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from guides.models import Guide
from guides.forms import GuideProfileForm

@login_required
def mypage(request): 
    try: 
        current_guide = request.user.guide_profile

        context = {"guide": current_guide}
        return render(request, "mypage/index.html", context)
    except Guide.DoesNotExist: 
        if request.method == "POST": 
            form = GuideProfileForm(request.POST)
            if form.is_valid(): 
                new_guide = form.save(commit=False)
                new_guide.user = request.user
                new_guide.save()

                return redirect('mypage')
        else: 
            form = GuideProfileForm()
        
        return render(request, "mypage/create_profile.html", {"form": form})

