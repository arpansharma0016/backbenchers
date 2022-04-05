from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Confirm, Password, Post
from home.models import Me, Comment, Bookmark, Post_report, Comment_report
import datetime
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import random
import math
from django.contrib.auth.hashers import make_password
import os
import json
from django.utils.text import slugify
from django.core import serializers
from django.db.models import Q


def register(request):
    
    if request.method == 'POST':
        if not request.POST['first_name'] or not request.POST['email'] or not request.POST['password1'] or not request.POST['password2']:
            messages.info(request, "Please enter all the fields!")
            return redirect("register")

        first_name = request.POST['first_name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']

        username = email
        
        
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect("register")
            
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect("register")
            
            
            else:
                for i in username:
                    if i.isupper():
                        messages.info(request, 'Email must be lowercase')
                        return redirect("register")

                    if i == " ":
                        messages.info(request, 'Email must not contain any Spaces')
                        return redirect("register")
                      
                if Confirm.objects.filter(email=email).exists():
                    confirm_user = Confirm.objects.get(email=email)
                    confirm_user.delete()
                    digits = "0123456789"
                    otp = ""
                    for i in range(6):
                        otp += digits[math.floor(random.random()*10)]
                    new_otp = otp
                    print(new_otp)
                    confirm_user = Confirm.objects.create(username=username, name=first_name, email=email, password=password1, otp=new_otp)
                    confirm_user.save()
                    subject = 'Thank You for registering to BackBenchers!'
                    message = 'Hi ' + confirm_user.name + '!\n \nWe have recieved an Account Creation request from you.\n\nYour Email Confirmation Code is '+new_otp+'.\n\nAll the Best\nTeam BackBenchers.'
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [confirm_user.email]
                    send_mail(subject, message, from_email, to_list, fail_silently=True)
                    messages.info(request, "An Account Confirmation email has been sent to "+confirm_user.email+". Please Enter the code here.")
                    return redirect("confirm_email", email)
                else:
                    digits = "0123456789"
                    otp = ""
                    for i in range(6):
                        otp += digits[math.floor(random.random()*10)]
                    new_otp = otp
                    confirm_user = Confirm.objects.create(username=username, name=first_name, email=email, password=password1, otp=new_otp)
                    confirm_user.save()
                    subject = 'Thank You for registering to BackBenchers!'
                    message = 'Hi ' + confirm_user.name + '!\n \nWe have recieved an Account Creation request from you.\n\nYour Email Confirmation Code is '+new_otp+'.\n\nAll the Best\nTeam BackBenchers.'
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [confirm_user.email]
                    send_mail(subject, message, from_email, to_list, fail_silently=True)
                    messages.info(request, "An Account confirmation email has been sent to "+confirm_user.email)
                    return redirect("confirm_email", email)
    
                
        
        else:
            messages.info(request, 'Password doesnt match')
            return redirect("register")
        
    else:
        return render(request, 'register.html')

def confirm_email(request, uname):
    
    if not Confirm.objects.filter(email=uname).exists():
        messages.info(request, "Please register first")
        return redirect("register")
    else:
        confirm_email = Confirm.objects.get(email=uname)
        old_otp = confirm_email.otp
        print(old_otp)
        
        if request.method == 'POST':
            otp = request.POST['otp']
            if otp == old_otp:
                user = User.objects.create_user(username=confirm_email.username, password=confirm_email.password, first_name=confirm_email.name, email=confirm_email.email)
                user.save()
                me = Me.objects.create(user_id=user.id, first_name=user.first_name, email=user.email)
                me.save()
                confirm_email.delete()
                messages.info(request, "Email confirmed successfully!")
                messages.info(request, "Login to continue.")
                return redirect("login")
            else:
                if confirm_email.attempts < 4:
                    confirm_email.attempts +=1
                    confirm_email.save()
                    messages.info(request, "Incorrect Otp, Try Again.")
                    messages.info(request, str((5-confirm_email.attempts))+ " attempts left.")
                    return redirect("confirm_email", uname)
                else:
                    confirm_email.attempts = 0
                    confirm_email.save()
                    messages.info(request, "Maximum Attempts held for this confirmation code.")
                    messages.info("We've sent a new Confirmation code to "+confirm_email.email+".")
                    messages.info("Please enter the new Code.")
                    return redirect("resend_code", confirm_email.email)

        

        return render(request, "confirm_email.html", {'confirm_email':confirm_email})


def resend_code(request, uname):
    if Confirm.objects.filter(email=uname).exists():
        confirm_user = Confirm.objects.get(email=uname)
        digits = "0123456789"
        otp = ""
        for i in range(6):
            otp += digits[math.floor(random.random()*10)]
        new_otp = otp
        confirm_user.otp = new_otp
        confirm_user.save()
        subject = 'Your new Password Confirmation Code is '+new_otp+'.'
        message = 'Hi ' + confirm_user.name + '!\n \nWe have recieved an Account Creation request from you.\n\nYour New Email Confirmation Code is '+new_otp+'.\n\nAll the Best\nTeam BackBenchers'
        from_email = settings.EMAIL_HOST_USER
        to_list = [confirm_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        messages.info(request, "Account confirmation email has been sent to "+confirm_user.email)
        return redirect("confirm_email", uname)
    else:
        messages.info(request, "Please register first!")
        return redirect("register")
    




def login(request):
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        for i in email:
            if i.isupper():
                messages.info(request, 'Username must be lowercase')
                return redirect("login")

        if User.objects.filter(email=email).exists():
            arpan = User.objects.get(email=email)
            
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('login')
        
        user = auth.authenticate(username=arpan.username, password=password)
        
        if user is not None:
            auth.login(request, user)
            confirm_user = User.objects.get(email=email)
            subject = 'New login activity on your BackBenchers account!'
            message = 'Hi ' + confirm_user.first_name + '!\n \nHope you are having a great time with BackBenchers.\n\nWe have detected a new login activity to your account.\n\nIf it was not you, please secure your account from fraud by changing the account password from the BackBenchers Website.\n\nThank You\nTeam BackBenchers' 
            from_email = settings.EMAIL_HOST_USER
            to_list = [confirm_user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            if Me.objects.get(user_id=arpan.id).username:
                return redirect("/")
            else:
                return redirect("username")
        
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('login')
        
    else:
        return render(request, 'login.html')
    

def logout(request):
    auth.logout(request)
    
    return redirect('/')

def forgot_password(request):
    if request.method == "POST":
        uname = request.POST['email']
        if uname:
            if User.objects.filter(email=uname).exists():
                
                if Password.objects.filter(email=uname).exists():
                    messages.info(request, "We have already sent the confirmation code to the email address "+uname)
                    return redirect("enter_otp", uname)
                else:
                    curr_user = User.objects.get(email=uname)
                    digits = "0123456789"
                    otp = ""
                    for i in range(6):
                        otp += digits[math.floor(random.random()*10)]
                    new_otp = otp
                    print(new_otp)
                    pass_user = Password.objects.create(email=uname, otp=new_otp)
                    pass_user.save()
                    subject = 'Password Reset Request on BackBenchers!'
                    message = 'Hi ' + curr_user.first_name + '!\n \nWe have recieved a password reset request on your account.\n\nYour Password reset code is ' + pass_user.otp +'\n\nThank You.\nTeam BackBenchers'
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [curr_user.email]
                    send_mail(subject, message, from_email, to_list, fail_silently=True)
                    messages.info(request, "Enter the OTP sent to registered email address.")
                    return redirect("enter_otp", uname)
            else:
                messages.info(request, "No user with email " + uname)
                messages.info(request, "Please enter your registered Email address")
                return redirect("forgot_password")
        else:
            messages.info(request, "Enter the Email")
            return redirect("forgot_password")
    return render(request, "forgot_password.html")

def enter_otp(request, uname):
    if Password.objects.filter(email=uname).exists():
        pass_user = Password.objects.get(email=uname)
        curr_user = User.objects.get(email=uname)
        if request.method == "POST":
            curr_otp = request.POST['otp']
            if pass_user.otp == curr_otp:
                pass_user.confirmed = True
                pass_user.save()
                messages.info(request, "Email address confirmed")
                return redirect("new_password", uname)
            else:
                if pass_user.attempts < 4:
                    pass_user.attempts += 1
                    pass_user.save()
                    messages.info(request, "Incorrect otp, try again!" +str(5-pass_user.attempts)+" attempts left.")
                    return redirect("enter_otp", uname)
                else:
                    pass_user.attempts = 0
                    pass_user.save()
                    messages.info(request, "Maximum attempts held for this confirmation code. Sending another code to email associated with "+pass_user.email)
                    return redirect("resend_pass_code", uname)
        return render(request, "enter_otp.html", {'pass_user':pass_user})
    else:
        messages.info(request,"Enter the Registered email address for which you want to change the Account Password.")
        return redirect("forgot_password")

def new_password(request, uname):
    if Password.objects.get(email=uname):
        pass_user = Password.objects.get(email=uname)
        curr_user = User.objects.get(email=uname)
        if request.method == "POST":
            if pass_user.confirmed:
                password1 = request.POST['password1']
                password2 = request.POST['password2']
                if password1:
                    if password1 == password2:
                        password = make_password(password1, hasher='default')
                        curr_user.password = password
                        pass_user.delete()
                        curr_user.save()
                        messages.info(request, "Password changed successfully.")
                        return redirect("login")
                    else:
                        messages.info(request, "Passwords Don't Match. Please re-enter the Passwords.")
                        return redirect("new_password")
                else:
                    messages.info(request, "Password Fields cannot be blank.")
                    return redirect(f"new_password/{uname}")
            else:
                messages.info(request, "Please enter your username registered with Affiliator.in")
                return redirect("forgot_password")
        return render(request, "new_password.html")
    else:
        messages.info(request, "Please enter your username registered with Affiliator.in")
        return redirect("forgot_password")

def resend_pass_code(request, uname):
    if Password.objects.filter(email=uname).exists():
        curr_user = User.objects.get(email=uname)
        pass_user = Password.objects.get(email=uname)
        digits = "0123456789"
        otp = ""
        for i in range(6):
            otp += digits[math.floor(random.random()*10)]
        new_otp = otp
        pass_user.otp = new_otp
        print(new_otp)
        pass_user.save()
        subject = 'Password Reset Request on BackBenchers!'
        message = 'Hi ' + curr_user.first_name + '!\n \nWe have recieved a password reset request on your User Account.\n\nYour Password reset code is ' + pass_user.otp +'\n\nThank You.\nTeam BackBenchers'
        from_email = settings.EMAIL_HOST_USER
        to_list = [curr_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        messages.info(request, "Password reset code has been sent to email address associated with "+uname)
        return redirect("enter_otp", uname)
    else:
        messages.info(request, "Please enter the username first")
        return redirect("forgot_password")


def username(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            m = Me.objects.filter(username=request.POST['username'])
            if m.exists():
                messages.info(request, "Username already exists!")
                return redirect("username")
            else:
                me = Me.objects.get(user_id = request.user.id)
                me.username = request.POST['username']
                me.save()
                return redirect("/")
        return render(request, "username.html")
    else:
        messages.info(request, "You need to login first!")
        return redirect("login")

@csrf_exempt
def check_username(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            if Me.objects.filter(username=request.POST['data']).exists():
                return JsonResponse({'taken':'yes'})
            else:
                return JsonResponse({'taken':'no'})
    else:
        messages.info(request, "You need to login first!")
        return redirect("login")

def index(request):
    post = Post.objects.all().order_by('-id')
    posts = []
    for p in post:
        try:
            me = Me.objects.get(user_id=p.user_id)
        except:
            me = None
        if me:
            posts.append([p, me])
    
    context = {
        'posts':posts
    }

    return render(request, 'index.html', context)

def me(request):
    if request.user.is_authenticated:
        mee = Me.objects.get(user_id=request.user.id)
        if mee.username:
            if request.method == "POST":
                exts = ['png', 'PNG', 'jpeg', 'JPEG', 'jpg', 'JPG']
                if request.FILES.get('image'):
                    if not request.FILES.get('image').name.split('.')[-1] in exts:
                        messages.info(request, "Please use only jpeg or png format images.")
                        return redirect("me")
                    mee.image = request.FILES.get('image')
                if request.POST.get('first_name').replace("<", "\<").replace(">", "\>").replace("'", "\'").replace('"', '\"').strip():
                    mee.first_name = request.POST.get('first_name').replace("<", "\<").replace(">", "\>").replace("'", "\'").replace('"', '\"').strip()
                else:
                    messages.info(request, "Please enter your name!")
                    return redirect("me")
                if request.POST.get('bio'):
                    mee.bio = request.POST.get('bio')
                mee.save()
                return redirect("me")

            posts = Post.objects.filter(user_id=request.user.id).order_by('-id')
            if posts.count() > 0:
                po = True
            else:
                po = False
            context = {
                'mee':mee,
                'first':mee.first_name[0],
                'posts':posts,
                'po':po
            }
            return render(request, "me.html", context)
        else:
            messages.info(request, "Please set your username first!")
            return redirect("username")

    else:
        messages.info(request, "Login first!")
        return redirect("login")

def create(request):
    if request.user.is_authenticated:
        mee = Me.objects.get(user_id=request.user.id)
        posts = Post.objects.filter(user_id=request.user.id)
        category = []
        categories = {}
        for post in posts:
            if post.category:
                cat = post.category
                if cat not in category:
                    category.append(cat)

        for post in posts:
            if post.category:
                cat = post.category
                if cat in categories:
                    categories[cat] +=  1
                else:
                    categories[cat] =  1

        if mee.username:
            context = {
                'mee':mee,
                'first':mee.first_name[0],
                'categories':categories
            }
            return render(request, "create.html", context)

        else:
            return redirect("username")

    else:
        messages.info(request, "Login first!")
        return redirect("login")

def edit(request, id):
    if request.user.is_authenticated:
        mee = Me.objects.get(user_id=request.user.id)
        if mee.username:
            try:
                post = Post.objects.get(id=id)
            except:
                post = None
            if post:
                if post.user_id == mee.user_id:
                    posts = Post.objects.filter(user_id=request.user.id)
                    category = []
                    categories = {}
                    for post in posts:
                        if post.category:
                            cat = post.category
                            if cat not in category:
                                category.append(cat)

                    for post in posts:
                        if post.category:
                            cat = post.category
                            if cat in categories:
                                categories[cat] +=  1
                            else:
                                categories[cat] =  1

                    context = {
                        'mee':mee,
                        'first':mee.first_name[0],
                        'post':post,
                        'categories':categories
                    }
                else:
                    return redirect("me")
            else:
                return redirect("me")
            
            return render(request, "edit.html", context)

        else:
            return redirect("username")

    else:
        messages.info(request, "Login first!")
        return redirect("login")


@csrf_exempt
def save_post(request):
    if request.user.is_authenticated:
        mee = Me.objects.get(user_id=request.user.id)
        if mee.username:
            if request.method == 'POST':
                post = Post.objects.create(user_id=request.user.id)
                if not request.FILES.get('file'):
                    return JsonResponse({'status':'fail', 'message':'Please select a pdf file'})
                else:
                    exts = ['pdf', 'PDF']
                    if request.FILES.get('file'):
                        if not request.FILES.get('file').name.split('.')[-1] in exts:
                            return JsonResponse({'status':'fail', 'message':'Please use only pdf files'})
                    post.upload = request.FILES.get('file')
                if not request.POST.get('heading').replace("<", "\<").replace(">", "\>").replace("'", "\'").replace('"', '\"').strip():
                    return JsonResponse({'status':'fail', 'message':'Plaese write the post heading'})
                else:
                    post.heading = request.POST.get('heading').replace("<", "\<").replace(">", "\>").replace("'", "\'").replace('"', '\"').strip()
                if request.POST.get('caption').replace("<", "\<").replace(">", "\>").replace("'", "\'").replace('"', '\"').strip():
                    post.caption = request.POST.get('caption').replace("<", "\<").replace(">", "\>").replace("'", "\'").replace('"', '\"').strip()
                if request.POST.get('thumbnail'):
                    post.thumbnail = request.POST.get('thumbnail')
                if request.POST.get('category').replace("<", "\<").replace(">", "\>").replace("'", "\'").replace('"', '\"').strip():
                    post.category = request.POST.get('category').replace("<", "\<").replace(">", "\>").replace("'", "\'").replace('"', '\"').strip().lower()
                post.save()
                return JsonResponse({'status':'success'})
        else:
            return JsonResponse({'status':'fail', 'message':'Your username is not set'})

    else:
        return JsonResponse({'status':'fail', 'message':'You are not logged in'})


@csrf_exempt
def edit_post(request, id):
    if request.user.is_authenticated:
        mee = Me.objects.get(user_id=request.user.id)
        if mee.username:
            if request.method == 'POST':
                try:
                    post = Post.objects.get(id=id)
                except:
                    post = None
                if post:
                    if post.user_id == mee.user_id:
                        head = request.POST.get('heading').replace("\\", "").replace("<", "\<").replace(">", "\>").replace("'", "\'").replace('"', '\"').strip()
                        cap = request.POST.get('caption').replace("\\", "").replace("<", "\<").replace(">", "\>").replace("'", "\'").replace('"', '\"').strip()
                        if not head:
                            return JsonResponse({'status':'fail', 'message':'No heading was found!'})
                        else:
                            post.heading = head
                        if cap:
                            post.caption = cap
                        else:
                            post.caption = None
                        if request.POST.get('thumbnail'):
                            post.thumbnail = request.POST.get('thumbnail')
                        else:
                            post.thumbnail = None
                        if request.POST.get('category').replace("<", "\<").replace(">", "\>").replace("'", "\'").replace('"', '\"').strip():
                            post.category = request.POST.get('category').replace("<", "\<").replace(">", "\>").replace("'", "\'").replace('"', '\"').strip().lower()
                        else:
                            post.category = None
                        post.save()
                        return JsonResponse({'status':'success'})
                    else:
                        return JsonResponse({'status':'fail', 'message':'This post does not belong you'})
                else:
                    return JsonResponse({'status':'fail', 'message':'This post does not exist'})
        else:
            return JsonResponse({'status':'fail', 'message':'Your username is not set'})

    else:
        return JsonResponse({'status':'fail', 'message':'You are not logged in'})



def delete_post(request, id):
    if request.user.is_authenticated:
        mee = Me.objects.get(user_id=request.user.id)
        if mee.username:
            try:
                post = Post.objects.get(id=id)
            except:
                post = None
            if post:
                if post.user_id == request.user.id:
                    post.delete()
                    return JsonResponse({'status':'success', 'id':id})
                else:
                    return JsonResponse({'status':'fail', 'message':'This post does not belong to you'})
            else:
                return JsonResponse({'status':'fail', 'message':'This post does not exist'})
        else:
            return JsonResponse({'status':'fail', 'message':'Your username is not set'})
    else:
        return JsonResponse({'status':'fail', 'message':'You are not logged in'})


def user(request, username):
    mee = get_object_or_404(Me, username=username)
    posts = Post.objects.filter(user_id=mee.user_id).order_by('-id')
    if posts.count() > 0:
        po = True
    else:
        po = False
    context = {
        'username':mee.username,
        'name':mee.first_name,
        'mee':mee,
        'posts':posts,
        'po':po
    }
    return render(request, "user.html", context)



def bookmarks(request):
    if request.user.is_authenticated:
        mee = Me.objects.get(user_id=request.user.id)
        bookmark = Bookmark.objects.filter(user_id=mee.user_id).order_by('-id')
        posts = []
        for i in bookmark:
            try:
                post = Post.objects.get(id=i.post_id)
            except:
                post = None
            if post:
                try:
                    m = Me.objects.get(user_id=post.user_id)
                except:
                    m = None
                if m:
                    posts.append([post, m])
                else:
                    i.delete()
            else:
                i.delete()
        if len(posts) > 0:
            po = True
        else:
            po = False
        context = {
            'mee':mee,
            'posts':posts,
            'po':po
        }
        return render(request, "bookmarks.html", context)
    
    else:
        messages.info(request, "Login first!")
        return redirect("login")

def create_bookmark(request, id):
    if request.user.is_authenticated:
        try:
            post = Post.objects.get(id=id)
        except:
            post = None
        if post:
            try:
                bookmark = Bookmark.objects.filter(user_id=request.user.id).get(post_id=post.id)
            except:
                bookmark = None
            if bookmark:
                bookmark.delete()
                book = 'delete'
            else:
                bookmarkk = Bookmark.objects.create(user_id=request.user.id, post_id=id)
                bookmarkk.save()
                book = 'save'
            return JsonResponse({'status':'success', 'book':book})
        else:
            return JsonResponse({'status':'fail', 'message':'This post doen not exist'})
    
    else:
        return JsonResponse({'status':'fail', 'message':'You are not logged in'})


def view_post(request, username, heading, id):
    mee = get_object_or_404(Me, username=username)
    post = get_object_or_404(Post, id=id)
    if request.user.is_authenticated:
        try:
            bookmark = Bookmark.objects.filter(user_id=request.user.id).get(post_id=post.id)
        except:
            bookmark = None
    else:
        bookmark = None

    if mee.user_id == post.user_id:
        posts = Post.objects.filter(user_id=mee.user_id).order_by('-id').exclude(id=post.id)
        if posts.count() > 0:
            co = True
        else:
            co = False
        context = {
            'mee':mee,
            'post':post,
            'posts':posts,
            'first':mee.first_name[0],
            'bookmark':bookmark,
            'co':co
        }
        return render(request, "post.html", context)
    else:
        return redirect(f"/{username}")


def load_comments(request, id):
    try:
        post = Post.objects.get(id=id)
    except:
        post = None
    if post:
        comments = Comment.objects.filter(post_id=post.id).order_by('-pk')
        count = post.comments
        real = list()
        for i in comments:
            mee = Me.objects.get(user_id=i.user_id)
            image = str(mee.image)
            real.append([i.id, mee.first_name, mee.username, mee.user_id, i.post_id, mee.first_name[0], image])

        comments = serializers.serialize('json', comments)
        return JsonResponse({'status':'success', 'comments':comments, 'count':count, 'real':real})

    else:
        return JsonResponse({'status':'fail', 'message':'This post does not exist'})

@csrf_exempt
def write_comment(request, id):
    if request.user.is_authenticated:
        try:
            post = Post.objects.get(id=id)
        except:
            post = None
        if post:
            if request.method == 'POST':
                updatedData=json.loads(request.body.decode('UTF-8'))
                com = updatedData['comment'].replace("<", "&lt;").replace(">", "&gt;").strip()
                if com:
                    comment = Comment.objects.create(user_id=request.user.id, post_id=post.id, comment=com)
                    comment.save()
                    post.comments += 1
                    post.save()
                    mee = Me.objects.get(user_id=request.user.id)
                    image = str(mee.image)
                    real = [comment.id, mee.first_name, mee.username, mee.user_id, post.id, mee.first_name[0], image]
                    return JsonResponse({'status':'success', 'comment':comment.comment, 'name':mee.first_name, 'created':comment.created, 'count':post.comments, 'created':comment.created, 'real':real})
                else:
                    return JsonResponse({'status':'fail'})

            else:
                return JsonResponse({'status':'fail'})
        
        else:
            return JsonResponse({'status':'fail', 'message':'This post does not exist'})

    else:
        return JsonResponse({'status':'fail', 'message':'You are not logged in'})


def delete_comment(request, id, post_id):
    if request.user.is_authenticated:
        try:
            post = Post.objects.get(id=post_id)
        except:
            post = None

        if post:
            try:
                comment = Comment.objects.get(id=id)
            except:
                comment = None

            if comment:
                if comment.user_id == request.user.id and comment.post_id == post.id:
                    comment.delete()
                    post.comments -= 1
                    post.save()
                    return JsonResponse({'status':'success', 'id':id, 'count':post.comments})
                
                else:
                    return JsonResponse({'status':'fail', 'message':'Error deleting this comment'})
            
            else:
                return JsonResponse({'status':'fail', 'message':'This comment does not exist'})

        else:
            return JsonResponse({'status':'fail', 'message':'This post does not exist'})        

    else:
        return JsonResponse({'status':'fail', 'message':'You are not logged in'})

    
def search(request):
    if request.GET.get('query'):
        query = request.GET.get('query').strip()
        if query:
            post = Post.objects.filter(Q(heading__icontains=query) | Q(caption__icontains=query)).order_by('-id')[:10]
            posts = []
            for p in post:
                me = Me.objects.get(user_id=p.user_id)
                posts.append([p, me])

            users = Me.objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query))[:10]

            if len(posts) >= 10:
                mp = True
            else:
                mp = False
            if users.count() >= 10:
                mu = True
            else:
                mu = False

            if len(posts) > 0:
                pe = True
            else:
                pe = False
            if users.count() > 0:
                ue = True
            else:
                ue = False
            

            context = {
                'posts':posts,
                'users':users,
                'query':query,
                'mp':mp,
                'mu':mu,
                'ue':ue,
                'pe':pe
            }
            return render(request, "search.html", context)
        else:
            return redirect("/")

    else:
        return redirect("/")



def search_posts(request):
    if request.GET.get('query'):
        query = request.GET.get('query').strip()
        if query:
            post = Post.objects.filter(Q(heading__icontains=query) | Q(caption__icontains=query)).order_by('-id')
            posts = []
            for p in post:
                me = Me.objects.get(user_id=p.user_id)
                posts.append([p, me])

            if len(posts) > 0:
                pe = True
            else:
                pe = False
            context = {
                'posts':posts,
                'query':query,
                'pe':pe
            }
            return render(request, "search_posts.html", context)
        else:
            return redirect("/")

    else:
        return redirect("/")



def search_users(request):
    if request.GET.get('query'):
        query = request.GET.get('query').strip()
        if query:
            users = Me.objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query))

            if users.count() > 0:
                ue = True
            else:
                ue = False

            context = {
                'users':users,
                'query':query,
                'ue':ue
            }
            return render(request, "search_users.html", context)
        else:
            return redirect("/")

    else:
        return redirect("/")


# def settings(request): the name settings collide with the conf settings, channge it.
#     mee = Me.objects.get(user_id=request.user.id)
#     context = {
#         'mee':mee
#     }
#     return render(request, "settings.html", context)


def report(request):
    return redirect("/")

def report_post(request, id):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=id)
        mee = get_object_or_404(Me, user_id=post.user_id)
        try:
            rep = Post_report.objects.filter(user_id=request.user.id).get(post_id=id)
        except:
            rep = None

        if request.method == "POST":
            con = request.POST['report']
            if rep:
                rep.context = con
                rep.save()
                messages.info(request, "Report edited successfully")
                return redirect("me")
            else:
                rep = Post_report.objects.create(user_id=request.user.id, post_id=id, context=con)
                rep.save()
                messages.info(request, "Report saved successfully")
                return redirect("me")
        
        context = {
            'post':post,
            'mee':mee,
            'rep':rep
        }
        return render(request, "report_post.html", context)

    else:
        messages.info(request, "Login first")
        return redirect("login")


def report_comment(request, id):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, id=id)
        mee = get_object_or_404(Me, user_id=comment.user_id)
        try:
            com = Comment_report.objects.filter(user_id=request.user.id).get(comment_id=id)
        except:
            com = None

        if request.method == "POST":
            con = request.POST['report']
            if com:
                com.context = con
                com.save()
                messages.info(request, "Report edited successfully")
                return redirect("me")
            else:
                com = Comment_report.objects.create(user_id=request.user.id, comment_id=id, context=con)
                com.save()
                messages.info(request, "Report saved successfully")
                return redirect("me")
        
        context = {
            'comment':comment,
            'mee':mee,
            'com':com
        }
        return render(request, "report_comment.html", context)

    else:
        messages.info(request, "Login first")
        return redirect("login")

def category(request, username, category):
    mee = get_object_or_404(Me, username=username)
    posts = Post.objects.filter(user_id=mee.user_id).filter(category=category)
    if posts.exists():
        pe = True
    else:
        pe = False
    
    context = {
        'mee':mee,
        'posts':posts,
        'category':category,
        'pe':pe
    }
    return render(request, "category.html", context)