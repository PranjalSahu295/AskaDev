from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.generic import TemplateView, View, UpdateView, ListView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import UserProfile,ProgrammingLanguage
from questions.models import Question
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
import base64, secrets, io, os, datetime

class TopDevelopers(ListView):
	model = UserProfile
	template_name = 'accounts/top_developers.html'
	context_object_name = 'developers'

	def get_context_data(self,*args, **kwargs):
		context = super(TopDevelopers, self).get_context_data()
		context['asked_questions'] = Question.objects.filter(user=User.objects.get(username=self.request.user)).count()
		return context

	def get_queryset(self, *args, **kwargs):
		queryset = UserProfile.objects.all().order_by('-points').exclude(points__lte=10)
		return queryset

@csrf_exempt
def followUser(request, user):
	usr = User.objects.filter(username=user)
	rusr = User.objects.filter(username=request.user) 
	if usr.exists() and rusr.exists():
		usr = User.objects.get(username=user)
		rusr = User.objects.get(username=request.user)
		userProfile = UserProfile.objects.filter(user=usr)
		ruser = UserProfile.objects.filter(user=rusr)
		if userProfile.exists() and ruser.exists():
			usr = User.objects.get(username=user)
			rusr = User.objects.get(username=request.user)
			userProfile = UserProfile.objects.get(user=usr)
			ruser = UserProfile.objects.get(user=rusr)
			ruser.follows.add(userProfile)
			ruser.save()
			userProfile.followers.add(ruser)
			userProfile.save()
		else:
			return HttpResponse("User Profile Does Not Exist")
	else:
		return HttpResponse("User Does Not Exist")
	return HttpResponse(ruser.follows.all())

@csrf_exempt
def unfollowUser(request, user):
	usr = User.objects.filter(username=user)
	rusr = User.objects.filter(username=request.user) 
	if usr.exists() and rusr.exists():
		usr = User.objects.get(username=user)
		rusr = User.objects.get(username=request.user)
		userProfile = UserProfile.objects.filter(user=usr)
		ruser = UserProfile.objects.filter(user=rusr)
		if userProfile.exists() and ruser.exists():
			usr = User.objects.get(username=user)
			rusr = User.objects.get(username=request.user)
			userProfile = UserProfile.objects.get(user=usr)
			ruser = UserProfile.objects.get(user=rusr)
			ruser.follows.remove(userProfile)
			ruser.save()
			userProfile.followers.remove(ruser)
			userProfile.save()
		else:
			return HttpResponse("User Profile Does Not Exist")
	else:
		return HttpResponse("User Does Not Exist")
	return HttpResponse(ruser.follows.all())

def get_image_from_data_url( data_url, resize=True, base_width=600 ):
    _format, _dataurl       = data_url.split(';base64,')
    _filename, _extension   = secrets.token_hex(20), _format.split('/')[-1]
    file = ContentFile(base64.b64decode(_dataurl), name=f"{_filename}.{_extension}")
    if resize:
        image = Image.open(file)
        image_io = io.BytesIO()
        w_percent = (base_width/float(image.size[0]))
        h_size = int((float(image.size[1])*float(w_percent)))
        image = image.resize((base_width,h_size), Image.ANTIALIAS)
        image.save(image_io, format=_extension)
        file = ContentFile( image_io.getvalue(), name=f"{_filename}.{_extension}" )
    return file, ( _filename, _extension )

class HomePage(TemplateView):
	template_name = 'accounts/home.html'

	def get_context_data(self, *args, **kwargs):
		context = super(HomePage, self).get_context_data(*args,**kwargs)
		if self.request.user.is_authenticated:
			user = User.objects.get(username=self.request.user.username)
			qs = Question.objects.filter(user=user).order_by('-asked_on')
			context['q_list'] = qs
			last_login = user.last_login
			date_joined = user.date_joined
			check_last_login = last_login - date_joined
			if check_last_login < datetime.timedelta(seconds=10):
				context['first_login'] = True
			return context
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            u = User.objects.get(username=username)
            up = UserProfile(
				user=user,
				bio="",
				website=None,
				experience=1,	
				profile_picture=f'static/images/profile_picture/default.jpg'			
			)
            up.save()
            up.languages.add(ProgrammingLanguage.objects.get(language='C'))
            up.follows.add(UserProfile.objects.get(user=User.objects.get(username='AskaDev')))
            admin = UserProfile.objects.get(user=User.objects.get(username='AskaDev'))
            up.save()
            admin.followers.add(up)
            admin.save()
            return redirect(f'/{u.id}/edit-profile')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

class UserProfileView(View):
	template_name = 'accounts/user_profile.html'
	def get(self,request, uname, *args, **kwargs):
		get_object_or_404(User, username=uname)
		u = UserProfile.objects.filter(
			user=User.objects.get(username=uname)
		)
		q = Question.objects.filter(
			user=User.objects.get(username=uname)
			).order_by('-asked_on')
		if u.exists():
			user = UserProfile.objects.get(user=User.objects.get(username=uname))
			rusr = get_object_or_404(User, username=request.user.username)
			ruser = get_object_or_404(UserProfile, user=rusr)
			u = u[0]
			if user == ruser:
				sameUser = True
			else:
				sameUser = False
			if user in ruser.follows.all():
				print("Following")
				canFollow = False
				following = "true"
				text = "Following"
			else:
				print("Not following")
				canFollow = True
				following = "false"
				text = "Follow"
			if user in ruser.followers.all() and user not in ruser.following.all():
				canFollow = True
				following = "false"
				text = "Follow Back"
			context = {"canFollow":canFollow,
	 				"sameUser":sameUser,
					"following":following,
					"text":text,
					"profile":u,
					'questions':q
			}
			return render(request, self.template_name, context)
		else:
			return HttpResponse('User Does not Exist')

class UserProfileUpdateView(UpdateView):
	model = UserProfile
	fields = ['experience',
			 'languages',
			 'bio',
			 'website'
	]
	def get(self,request, *args, **kwargs):
		user = User.objects.get(username=self.request.user)
		requested_user = UserProfile.objects.filter(id=self.kwargs['pk'])
		if requested_user.exists():
			if not user==requested_user[0].user:
				return redirect('/')
			else:
				return super(UserProfileUpdateView, self).get(request,*args,**kwargs) 
		else:
			return HttpResponse("Requested Profile Doesn't Exist")
		

	def form_valid(self, form):
		redirect_url = super(UserProfileUpdateView, self).form_valid(form)
		pp_url = self.request.POST.get('pp_url')
		try:
			img = get_image_from_data_url(pp_url)[0]
			form.instance.profile_picture = img
			form.instance.save()
			return redirect_url
		except ValueError:
			form.save()
			return redirect_url

	def get_success_url(self):
		return reverse('profile', args=[str(self.request.user)])

	def get_context_data(self,*args,**kwargs):
		context = super().get_context_data(*args, **kwargs)
		up = UserProfile.objects.get(id=self.kwargs['pk'])
		context['profile'] = up
		im = up.profile_picture.read()
		bs64_url = base64.b64encode(im)
		context['c_pp_url'] = bs64_url.decode()
		return context