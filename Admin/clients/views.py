from django.contrib.auth import authenticate,update_session_auth_hash,login as login_django,logout as logout_django
from .forms import LoginUserForm,CreateUserForm,EditUserForm,EditPasswordForm,EditClientForm,EditSocialForm
from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.generic import View,DetailView,CreateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .models import Client,SocialNetwork


class ShowView(DetailView):
	model = User
	template_name = 'clients/show.html'
	slug_field ='username'
	slug_url_kwarg = 'username_url'

class LoginView(View):
	form = LoginUserForm()
	message = None
	template = 'clients/login.html'

	def get(self,request,*args,**kwargs):
		if request.user.is_authenticated():
			return redirect('client:dashboard')
		return render(request,self.template, self.get_context())

	def post(self,request,*args,**kwargs):
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username,password=password)	
		if user is not None:
			login_django(request,user)
			return redirect('client:dashboard')
		else:
			self.message = "User or password incorrect"
		return render(request,'clients/login.html', self.get_context())

	def get_context(self):
		return {'form':self.form,'message':self.message}

class DashboardView(LoginRequiredMixin,View):
	login_url = 'client:login'
	def get(self,request,*args,**kwargs):
		return render(request,'clients/dashboard.html', {})
		
class Create(CreateView):
	success_url = reverse_lazy('client:login')
	template_name = 'clients/create.html'
	model = User
	form_class = CreateUserForm

	def form_valid(self,form):
		self.object = form.save(commit=False)
		self.object.set_password(self.object.password)
		self.object.save()
		return HttpResponseRedirect(self.get_success_url())

class EditSocialClass(LoginRequiredMixin,UpdateView,SuccessMessageMixin):
	login_url ='client:login'
	model = SocialNetwork
	template_name = 'clients/edit_social.html'
	form_class = EditSocialForm
	success_url = reverse_lazy('client:edit_social')
	success_message = "Datos actualizados exitosamente"

	def get_object(self, queryset = None):
		return self.get_social_instance()

	def get_social_instance(self):
		try:
			return self.request.user.socialnetwork
		except:
			return SocialNetwork(user = self.request.user)


def edit_password(request):
	message = None
	form = EditPasswordForm(request.POST or None)
	if request.method =='POST':
		if form.is_valid():
			current_password = form.cleaned_data['password']
			new_password = form.cleaned_data['new_password']
			if authenticate(username=request.user.username, password=current_password):
				request.user.set_password( new_password )
				request.user.save()
				update_session_auth_hash(request,request.user)
				messages.success(request,'password actualizado !')
			else:
				messages.error(request,'No se puede actualizar el password')
	context = {'form':form}
	return render(request,'clients/edit_password.html',context)

@login_required(login_url = 'client:login')	
def logout(request):
	logout_django(request)
	return redirect('client:login')

@login_required(login_url = 'client:login')
def edit(request):
	form_client = EditClientForm(request.POST or None, instance = client_instance(request.user))	#esto es en shell
	form_user = EditUserForm(request.POST or None, instance = request.user)
	if request.method =='POST':
		if form_client.is_valid() and form_user.is_valid():
			form_client.save()
			form_user.save()
			messages.success(request,'Se actualizarón los datos !')

	context = {
		'form_client':form_client,
		'form_user':form_user
	}
	return render(request,'clients/edit.html',context)


def client_instance(user):
	try:
		return user.client
	except:
		return Client(user1 = user)
	


