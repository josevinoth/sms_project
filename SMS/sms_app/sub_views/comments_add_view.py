from django.contrib.auth.decorators import login_required
from ..forms import commentsaddForm
from ..models import User_extInfo,commentsInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def comments_add(request,comments_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    if request.method == "GET":
        if comments_id == 0:
            form = commentsaddForm()
        else:
            comments=commentsInfo.objects.get(pk=comments_id)
            form = commentsaddForm(instance=comments)
        return render(request, "asset_mgt_app/comments_add.html", {'form': form,'first_name': first_name,'role':role,'user_id':user_id,})
    else:
        if comments_id == 0:
            form = commentsaddForm(request.POST)
        else:
            comments = commentsInfo.objects.get(pk=comments_id)
            form = commentsaddForm(request.POST,instance=comments)
        if form.is_valid():
            form.save()
            na_assessment_num_id = request.session.get('na_assessment_id')
            last_id = commentsInfo.objects.latest('id').id
            commentsInfo.objects.filter(pk=last_id).update(comments_ref=na_assessment_num_id)
        return redirect('/SMS/comments_cancel')

# List comments
@login_required(login_url='login_page')
def comments_list(request):
    first_name = request.session.get('first_name')
    context = {'comments_list' : commentsInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/comments_list_WOH.html",context)

#Delete comments
@login_required(login_url='login_page')
def comments_delete(request,comments_id):
    comments = commentsInfo.objects.get(pk=comments_id)
    comments.delete()
    # return redirect('/SMS/comments_list')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def comments_cancel(request):
    na_assessment_num_id = request.session.get('na_assessment_id')
    print(na_assessment_num_id)
    return redirect('/SMS/needassessment_update/'+ str(na_assessment_num_id))