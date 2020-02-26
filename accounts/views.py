from django.shortcuts import render , redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import jwt
from .models import *
from .manager import *
from django.contrib.auth.models import User
from .forms import *
from .decorators import *

def home(request):
    return render(request,'accounts/home.html')

@login_required(login_url='login')
@allowed_users(allowed_roles = ['admin','hr'])
def dashboard(request):
    return render(request,'accounts/dashboard.html')

@login_required(login_url='login')
@allowed_users(allowed_roles = ['employee'])
def user(request):
    employee = Employee.objects.filter(user=request.user).first()
    context = {'employee':employee}
    return render(request,'accounts/user.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def manager(request):
    employee = Employee.objects.filter(user=request.user).first()
    leaves = Leave.objects.all_pending_leaves()
    context = {'employee':employee,'leave_count':len(leaves)}
    return render(request,'accounts/manager.html',context)

# @login_required(login_url='login')
# def submitleave(request):
#     context = {}
#     if request.method == "POST":
#         print(User.objects.filter(username=request.user).values_list('email',flat=True)[0])
#         print(type(User.objects.filter(username=request.user).values_list('email',flat=True)[0]))

#         employee = Employee.objects.get(Email_Address = User.objects.filter(username=request.user).values_list('email',flat=True)[0])
#         # empMgrDept = EmpMgrDept.objects.get(Emp_No_EmpMgrDept_id=employee)
#         # manager = Employee.objects.get(Emp_No=empMgrDept.Manager_Emp_ID_id)

#         # empleaverequest = EmpLeaveRequest(Emp_ID=employee, Emp_FullName=empMgrDept.Emp_FullName,
#         #                                   Leave_Type=request.POST['leavetype'],
#         #                                   Manager_Emp_No=manager, Manager_FullName=empMgrDept.Manager_FullName,
#         #                                   Begin_Date=request.POST['fromdate'],
#         #                                   End_Date=request.POST['todate'], Requested_Days=request.POST['requesteddays'],
#         #                                   Leave_Status="Pending", Emp_Comments=request.POST['comment'])
#         print(employee)
#     return render(request,'accounts/submitleave.html',context)

@unauthorized_user
def login_(request):
    # form = loginUserForm()
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('dashboard')
        else:
            messages.info(request,message="Invalid credentials!")
            return render(request,'accounts/login.html')
    context = {}
    return render(request,'accounts/login.html',context)

@unauthorized_user
def register(request):
    form = createUserForm()
    if request.method=="POST":
        form = createUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            messages.info(request,message="Invalid credentials!")
    context = {'form':form}
    return render(request,'accounts/register.html',context)

def logout_(request):
    logout(request)
    return redirect('home')

def status(request):
    return HttpResponse("You are in status page")

@login_required(login_url='login')
def applyleave(request):
    if request.method == 'POST':
        form = LeaveCreationForm(request.POST)
        if form.is_valid():
            instance = form.save(commit = False)
            user = request.user
            instance.user = user
            instance.save()
            print("LEAVE APPLIED SUCCESSFULLY!!!")
            print(request.POST['startdate'])
            print(request.POST['enddate'])
            # messages.success(request,"Submitted Successfully! Check <a href=\"{% url 'view_my_leave_table' %}\">STATUS</a>.")
            return redirect('view_my_leave_table')
        messages.error(request,'Failed to request a leave. Please check the dates')
        return redirect('applyleave')
    else:
        dataset = dict()
        form = LeaveCreationForm()
        employee= Employee.objects.filter(user = request.user).first() 
        dataset['form'] = form
        dataset['title'] = 'Apply for Leave'
        context = {'form':form,
                    'dataset':dataset,
                    'employee':employee}
        return render(request,'accounts/leave.html',context)

# @login_required(login_url='login')
# @allowed_users(allowed_roles = ['manager','hr'])
# def leaves_list(request):
# 	leaves = Leave.objects.all_pending_leaves()
# 	return render(request,'accounts/leaves_recent.html',{'leave_list':leaves,'title':'leaves list - pending'})


@login_required(login_url='login')
@allowed_users(allowed_roles = ['employee'])
def view_my_leave_table(request):
    user = request.user
    leaves = Leave.objects.filter(user = user)
    employee = Employee.objects.filter(user = user).first()
    print(leaves)
    context = {}
    dataset = dict()
    dataset['leave_list'] = leaves
    dataset['employee'] = employee
    dataset['title'] = 'Leaves List'
    context={'dataset':dataset}
    print(dataset)
    print(context)
    return render(request,'accounts/leave_status_employee.html',context)


@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def leaves_list_mh(request):
	leaves = Leave.objects.all_pending_leaves()
	return render(request,'accounts/leave_list_mh.html',{'leave_list':leaves,'title':'leaves list - pending'})

@login_required(login_url='login')
def leaves_view(request,id):
	leave = get_object_or_404(Leave, id = id)
	employee = Employee.objects.filter(user = leave.user)[0]
	print(employee)
	return render(request,'accounts/leave_detail_view.html',{'leave':leave,'employee':employee,'title':'{0}-{1} leave'.format(leave.user.username,leave.status)})

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def leaves_view_mh(request,id):
	leave = get_object_or_404(Leave, id = id)
	employee = Employee.objects.filter(user = leave.user)[0]
	print(employee)
	return render(request,'accounts/leave_detail_view_mh.html',{'leave':leave,'employee':employee,'title':'{0}-{1} leave'.format(leave.user.username,leave.status)})


@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def approve_leave(request,id):
	leave = get_object_or_404(Leave, id = id)
	user = leave.user
	employee = Employee.objects.filter(user = user)[0]
	leave.approve_leave
	# messages.error(request,'Leave successfully approved for {0}'.format(employee.get_full_name),extra_tags = 'alert alert-success alert-dismissible show')
	return redirect('leaves_approved_list')

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def reject_leave(request,id):
	leave = get_object_or_404(Leave, id = id)
	leave.reject_leave
	# messages.success(request,'Leave is rejected',extra_tags = 'alert alert-success alert-dismissible show')
	return redirect('leave_rejected_list')

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def leaves_approved_list(request):
	leaves = Leave.objects.all_approved_leaves() #approved leaves -> calling model manager method
	return render(request,'accounts/all_leaves_approved.html',{'leave_list':leaves,'title':'approved leave list'})

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def leaves_rejected_list(request):
	leaves = Leave.objects.all_rejected_leaves() #rejected leaves -> calling model manager method
	return render(request,'accounts/all_leaves_rejected.html',{'leave_list':leaves,'title':'rejected leave list'})

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def unapprove_leave(request,id):
	leave = get_object_or_404(Leave, id = id)
	leave.unapprove_leave
	return redirect('leaves_list_mh') #redirect to unapproved list

@login_required(login_url='login')
@allowed_users(allowed_roles = ['manager'])
def unreject_leave(request,id):
	leave = get_object_or_404(Leave, id = id)
	leave.status = 'pending'
	leave.is_approved = False
	leave.save()
	# messages.success(request,'Leave is now in pending list ',extra_tags = 'alert alert-success alert-dismissible show')
	return redirect('leaves_list_mh')

