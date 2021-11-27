from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from .models import question,user_detail,temparory

from random import shuffle

# Create your views here.
c=0
def index(request):
	return render(request,'quiz/index.html')

def login(request):
	if request.method=='POST':
		username=request.POST['username']
		password=request.POST['password']

		user=auth.authenticate(username=username,password=password)

		if user:
			auth.login(request,user)
			if user_detail.objects.filter(username=username).exists():
				pass
			else:
				us=user_detail(username=username,no_of_test=0,total_score=0,t1=0,t2=0,t3=0)
				us.save()
			user=user_detail.objects.get(username=username)
			return redirect('home')
		else:
			messages.info(request,'Incorrect Credentials')
			return redirect('login')
	else:
		if request.user.is_authenticated:
			user=user_detail.objects.get(username=request.user.username)
			return render(request,'quiz/home.html',{'user':user})
		else:
			return render(request,'quiz/login.html')

def registration(request):
	if request.method=='POST':
		first_name=request.POST['first_name']
		last_name=request.POST['last_name']
		username=request.POST['username']
		email=request.POST['email']
		password1=request.POST['password1']
		password2=request.POST['password2']

		if password1==password2:
			if  not User.objects.filter(username=username).exists():
				if not User.objects.filter(email=email).exists():
					user=User.objects.create_user(username=username,email=email,first_name=first_name,last_name=last_name,password=password2)
					user.save()
					messages.info(request,'Registration of user done.')
					u=User.objects.get(username=username).id
					us=user_detail(id=int(u),username=username,no_of_test=0,total_score=0,t1=0,t2=0,t3=0)
					us.save()
					return redirect("login")
				else:
					messages.info(request,'Email is not Unique\nTry Again')
					return redirect("registration")
			else:
				messages.info(request,'UserName is not Unique\nTry Again')
				return redirect("registration")
		else:
			messages.info(request,'Password not Same\nTry Again')
			return redirect("registration")
	else:
		return render(request,'quiz/registration.html')

def home(request):
	if request.user.is_authenticated:
		username=request.user.username
		user=user_detail.objects.get(username=username)
		return render(request,'quiz/home.html',{'user':user})
	else:
		return render(request,'quiz/login.html')

def logout(request):
	temparory.objects.all().delete()
	auth.logout(request)
	return redirect('/')

def quizzing(request):
	if request.method=='GET':
		global c
		q=temparory.objects.all().first()
		if q:
			return render(request,'quiz/quizzing.html',{'question':q,'c':c})
		else:
			username=request.user.username
			u=user_detail.objects.get(username=username)
			u.no_of_test=u.no_of_test+1
			u.t3=u.t2
			u.t2=u.t1
			u.t1=c
			u.save()
			c=0
			return render(request,'quiz/home.html',{'user':u})
	elif request.method=='POST':
		ans=int(request.POST['choice'])
		q=request.POST['question']
		q=temparory.objects.get(question_text=q)
		c=int(request.POST['count'])
		if q.answer==ans:
			temparory.objects.all().first().delete()
			x=temparory.objects.all().count()
			c=c+1
			return redirect('quizzing')
		else:
			x=temparory.objects.all().count()
			username=request.user.username
			u=user_detail.objects.get(username=username)
			u.no_of_test=u.no_of_test+1
			u.t3=u.t2
			u.t2=u.t1
			u.t1=c
			u.save()
			c=0
			return render(request,'quiz/home.html',{'user':u})

def exam(request):
	if request.method=='GET':
		temparory.objects.all().delete()
		q=question.objects.all()
		q=list(q)
		shuffle(q)
		q=q[:5]
		shuffle(q)
		objs = [
		    temparory(
		        question_text=e.question_text,
	        	choice1=e.choice1,
		        choice2=e.choice2,
		        choice3=e.choice3,
	    	    choice4=e.choice4,
		        answer=e.answer
		    )
	    	for e in q
		]
		qt = temparory.objects.bulk_create(objs=objs)
		return redirect('quizzing')


def submit(request):
	q=question.objects.all()
	objs = [
	    temparory(
	        question_text=e.question_text,
	        choice1=e.choice1,
	        choice2=e.choice2,
	        choice3=e.choice3,
	        choice4=e.choice4,
	        answer=e.answer
	    )
	    for e in q
	]
	qt= temparory.objects.bulk_create(objs=objs)
	return HttpResponse("DONE")

def show(request):
	temparory.objects.all().first().delete()
	return HttpResponse(temparory.objects.all().first().question_text)