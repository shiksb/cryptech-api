from django.http import HttpResponse
import time, hashlib
from cryptech import factom
from cryptech.nacl_sign import *
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.views.generic import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


def index(request):
    return HttpResponse('home')

@login_required
@csrf_exempt
def step_one(request):

    # ext_ids = ['mediachain', str(int(time.time()))]
    # content ='Chain for copyrights, patents, and create asset protection'
    # chain_id = str(factom.create_chain(external_ids=ext_ids, content=content))
    # 'chain id = fb8d30c54e846b2bd7f1f5f68145c309be4c1885def89f05954dc89ce0878206'
    # 'entry hash = 3cbbae26e73cfeaa8d1566bef45b14a5814e018780e965d3a1366f7fa1431bf6'

    context = dict()
    myfile = request.FILES.get('myfile', None)
    image = request.method == "POST" and myfile is not None and myfile != ''
    if image:
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        context['content_hash'] = file_hash(filename)
    else:
        text = request.POST.get('text_content')
        if text is not None:
            context['text_content'] = text
            context['content_hash'] = hash_msg(text)
        else:
            context['content_hash'] = ''

    # fields = ['timestamp', 'msg', 'hmsg','private_key', 'public_key', 'sign', 'verified']
    # params = process_request(request, fields)
    #

    #         print(params['msg'], params['private_key'], params['hmsg'])
    #         s = nacl_sign.Sign(params['msg'], params['private_key'])
    #         params['sign'] = s.sign
    #         params['verified'] = nacl_sign.verify(params['msg'], s, params['public_key'])


    private_key, public_key = generate_keys()
    context['public_key'] = public_key
    context['private_key'] = private_key
    context['raw_nonce'] = request.user.username + User.objects.get(username=request.user.username).email
    context['nonce'] = str(nonce(hash_msg(request.user.username + User.objects.get(username=request.user.username).email)),'utf-8')
    # context['']
    # context['params'] = params
    # print(factom.chain_add_entry(chain_id='fb8d30c54e846b2bd7f1f5f68145c309be4c1885def89f05954dc89ce0878206',
    #                        external_ids=[params['public_key'], params['hmsg']],
    #                        content=params['sign']
    #                        ))

    return render(request, 'upload.html', context)

@login_required
@csrf_exempt
def step_two(request):
    context = dict()
    fields = ['content_hash', 'private_key', 'public_key', 'signature', 'chain_id', 'verified']
    params = process_request(request, fields)
    params['timestamp'] = str(int(time.time()))
    params['chain_id'] = 'fb8d30c54e846b2bd7f1f5f68145c309be4c1885def89f05954dc89ce0878206'
    n = nonce(hash_msg(request.user.username + User.objects.get(username=request.user.username).email))
    print(params['content_hash'], params['private_key'])
    # s = Sign(params['content_hash'], params['private_key'], nonce=n)
    # params['sign'] = s.sign
    # params['verified'] = str(verify(params['msg'], s, params['public_key']))
    context['params'] = params

    return render(request, 'origin.html', context)


@login_required
@csrf_exempt
def step_three(request):
    context = dict()
    dataset = []

    class data(object):
        def __init__(self):
            self.d0 = 'd0'
            self.d1 = 'd1'
            self.d2 = 'd2'
            self.d3 = 'd3'
            self.d4 = 'd4'
            self.d5 = 'd5'

    for i in range(0, 10):
        dataset.append(data())

    context['dataset'] = dataset

    return render(request, 'explore.html', context)


def process_request(request, fields):
    query = dict()
    for f in fields:
        x = request.POST.get(f)
        if not x or len(x) == 0: x = ''
        query[f] = x
    return query


def keys(request=None):
    private_key, public_key = nacl_sign.generate_keys()
    return HttpResponse("Private Key: " + private_key + "<br>Public   Key: " + public_key)


def file_hash(file_name):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(file_name, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class UserFormView(View):
    form_class = UserForm
    template_name = 'records/registration_form.html'

    # blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # process the data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            # saving temporarily
            user = form.save(commit=False)

            # cleaning the fields
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user.set_password(password)
            user.save()

            # returns User objects if correct credentials
            user = authenticate(username= username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)

                    return redirect('index')


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return index(request)

            else:
                return render(request, 'login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'login.html', {'error_message': 'Invalid login'})
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'login.html', context)