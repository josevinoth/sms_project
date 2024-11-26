

@login_required(login_url='login_page')
def expense_ext(request, expense_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')