import urllib # Python URL functions
from django.shortcuts import render, redirect,HttpResponse
from .models import *
from django.forms.models import model_to_dict
from django.contrib.auth import login, authenticate ,logout
from django.contrib.auth.forms import UserCreationForm
from hashlib import sha1
from django.contrib.auth.models import User, auth
from django.http import JsonResponse
from datetime import  timedelta, date
import razorpay
from django.views.decorators.csrf import csrf_exempt
from aodh_pet import settings
from django.db.models import Q
import requests
import base64
import json
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from django.conf import settings
import random
import urllib
from urllib.request import urlopen
import http.client
from django.contrib import messages

import hmac
import hashlib
from django.db import IntegrityError
from time import gmtime, strftime
import pytz
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.


# customer views

def index(request):
	return render(request,'aodh_home_page.html',{'pk':None})

import os, ssl
def msg(request):
	if request.method=="POST":
		mobile = request.POST.get('mobile')
		if Customer.objects.filter(mobile__iexact=mobile).exists() :
			if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
			getattr(ssl, '_create_unverified_context', None)):
				ssl._create_default_https_context = ssl._create_unverified_context
			mobile=request.POST.get('mobile')
			conn = http.client.HTTPSConnection("api.msg91.com")

			headers = { 'content-type': "application/json" }

			conn.request("GET", "/api/v5/otp?authkey=334231AXCttMDRD5efc1d91P1&template_id=5f1c27f1d6fc050ffd420ee7&mobile="+"91"+mobile+"&otp=&userip=IPV4%20User%20IP&otp_length=4&otp_expiry=3", headers=headers)
			res = conn.getresponse()
			data = res.read()
		else:
			data = 'NO mobile'
			return JsonResponse(data,safe=False)
	return render(request,'customer/customer_new_registration.html')

def msg_reg(request):
	if request.method=="POST":
		mobile = request.POST.get('mobile')
		if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
		getattr(ssl, '_create_unverified_context', None)):
			ssl._create_default_https_context = ssl._create_unverified_context
		mobile=request.POST.get('mobile')
		conn = http.client.HTTPSConnection("api.msg91.com")

		headers = { 'content-type': "application/json" }

		conn.request("GET", "/api/v5/otp?authkey=334231AXCttMDRD5efc1d91P1&template_id=5f1c27f1d6fc050ffd420ee7&mobile="+"91"+mobile+"&otp=&userip=IPV4%20User%20IP&otp_length=4&otp_expiry=3", headers=headers)
		res = conn.getresponse()
		data = res.read()


	return render(request,'customer/customer_new_registration.html')

def verifyotpmsg(request):
		if request.method=="POST":
			username=request.POST.get('user_name')
			mobile=request.POST.get('mobile')
			user_otp=request.POST.get('otp')
			if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
			getattr(ssl, '_create_unverified_context', None)):
				ssl._create_default_https_context = ssl._create_unverified_context
			conn = http.client.HTTPSConnection("api.msg91.com")

			payload = ""
			conn.request("POST", "/api/v5/otp/verify?mobile="+"91"+mobile+"&otp="+user_otp+"&authkey=334231AXCttMDRD5efc1d91P1", payload)
			res = conn.getresponse()
			data = res.read()
			bytelist=data
			bytelist=bytelist.decode("utf-8")
			res = json.loads(bytelist)
			if res['type']=='success':
				if Customer.objects.filter(mobile=mobile).exists():
					customer_obj=Customer.objects.get(mobile=mobile)
					customer_id=customer_obj.customer_id
					request.session['customer_id']=customer_id
					request.session['visit_check']='Home_visit'
					return redirect('customer_home_page',customer_id=customer_id)
				else:
					customer = Customer()
					customer_id = cust_id()
					customer.customer_id=customer_id
					customer.customer_name=username
					customer.mobile=mobile
					customer.save()
					request.session['customer_id']=customer_id
					request.session['visit_check']='Home_visit'

					return redirect('customer_home_page',customer_id=customer_id)
			elif res['message']=='OTP expired':

				messages.info(request,'OTP expired')
				return redirect('customer_registration_home')
			elif res['message']=='OTP not match':
				messages.info(request,'Invalid OTP Please check your code and try again.')
				return redirect('customer_registration_home')
			else :
				messages.info(request,'Something went wrong! try again.')
				return redirect('customer_registration_home')


		return render(request,'customer/customer_new_registration.html')
def resendotp(request):
	if request.method=="POST":
		mobile=request.POST.get('mobile')
		if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
		getattr(ssl, '_create_unverified_context', None)):
			ssl._create_default_https_context = ssl._create_unverified_context
		conn = http.client.HTTPSConnection("api.msg91.com")

		payload = ""

		conn.request("POST", "https://api.msg91.com/api/v5/otp/retry?mobile="+"91"+mobile+"&authkey=334231AXCttMDRD5efc1d91P1&retrytype=text", payload)

		res = conn.getresponse()
		data = res.read()
		bytelist=data
		bytelist=bytelist.decode("utf-8")
		res = json.loads(bytelist)
		if res['message']=='OTP retry count maxed out':
			res="OTP retry count maxed out"
			return JsonResponse(res,safe=False)

	return HttpResponse('try Again')

def customer_registration_home(request):
	return render(request,'customer/customer_new_registration.html',{'pk':None})

def customer_registration(request,doc_id=None):
	if doc_id=='None' or doc_id=='':
		return HttpResponse('please scan valid Qr code')
	else:
		try:
			doctor=Doctor.objects.get(id=doc_id)
			doctor=doctor.id
		except:
			return HttpResponse('select valid doctor')
		if doc_id==str(doctor):
			if request.method=="POST":
					username=request.POST.get('user_name')
					mobile=request.POST.get('mobile')
					user_otp=request.POST.get('otp')
					print(mobile,user_otp)
					if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
					getattr(ssl, '_create_unverified_context', None)):
						ssl._create_default_https_context = ssl._create_unverified_context
					conn = http.client.HTTPSConnection("api.msg91.com")
					payload = ""
					conn.request("POST", "/api/v5/otp/verify?mobile="+"91"+mobile+"&otp="+user_otp+"&authkey=334231AXCttMDRD5efc1d91P1", payload)
					res = conn.getresponse()
					data = res.read()
					bytelist=data
					bytelist=bytelist.decode("utf-8")
					res = json.loads(bytelist)
					if res['type']=='success':
						if Customer.objects.filter(mobile=mobile).exists():
							customer_obj=Customer.objects.get(mobile=mobile)
							customer_id=customer_obj.customer_id
							request.session['customer_id']=customer_id
							request.session['visit_check']='Hospital_visit'
							request.session['Doctor_pk_hospital']=doctor
							if Pet.objects.filter(customer_id__customer_id=customer_id).exists():
								pet=Pet.objects.filter(customer_id__customer_id=customer_id).last()
								return redirect('pet_list')
							else :
								return redirect('petdetails',doc_pk=doc_id)

						else:
							customer = Customer()
							customer_id = cust_id()
							customer.customer_id=customer_id
							customer.customer_name=username
							customer.mobile=mobile
							customer.save()
							request.session['customer_id']=customer_id
							request.session['visit_check']='Hospital_visit'
							request.session['Doctor_pk_hospital']=doctor
							if Pet.objects.filter(customer_id__customer_id=customer_id).exists():
								pet=Pet.objects.filter(customer_id__customer_id=customer_id).last()
								return redirect('pet_list')
							else :
								return redirect('petdetails',doc_pk=doc_id)
					elif res['message']=='OTP expired':

						messages.info(request,'OTP expired')

					elif res['message']=='OTP not match':
						messages.info(request,'Invalid OTP Please check your code and try again.')

					else :
						messages.info(request,'Something went wrong! try again.')
		else:
			return HttpResponse('select valid doctor')

	return render(request,'customer/customer_registration_hospital.html',{'doc_id':doc_id})


def customer_login_hospital(request,doc_id):
	if request.method=="POST":
		username=request.POST.get('user_name')
		mobile=request.POST.get('mobile')
		user_otp=request.POST.get('otp')
		print(mobile,user_otp,username)
		if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
		getattr(ssl, '_create_unverified_context', None)):
			ssl._create_default_https_context = ssl._create_unverified_context
		conn = http.client.HTTPSConnection("api.msg91.com")
		payload = ""
		conn.request("POST", "/api/v5/otp/verify?mobile="+"91"+mobile+"&otp="+user_otp+"&authkey=334231AXCttMDRD5efc1d91P1", payload)
		res = conn.getresponse()
		data = res.read()
		bytelist=data
		bytelist=bytelist.decode("utf-8")
		res = json.loads(bytelist)
		if res['type']=='success':
			doctor=Doctor.objects.get(id=doc_id)
			doctor=doctor.id
			if Customer.objects.filter(mobile=mobile).exists():
				customer_obj=Customer.objects.get(mobile=mobile)
				customer_id=customer_obj.customer_id
				request.session['customer_id']=customer_id
				request.session['visit_check']='Hospital_visit'
				request.session['Doctor_pk_hospital']=doctor
				if Pet.objects.filter(customer_id__customer_id=customer_id).exists():
					pet=Pet.objects.filter(customer_id__customer_id=customer_id).last()
					return redirect('pet_list')
				else :
					request.session['customer_id']=customer_id
					request.session['visit_check']='Hospital_visit'
					request.session['Doctor_pk_hospital']=doctor
					return redirect('petdetails',doc_pk=doc_id)
			else:
				return render(request,'customer/Customer_user_login_hospital.html',{'doc_id':doc_id})
		elif res['message']=='OTP expired':
			messages.info(request,'OTP expired')
		elif res['message']=='OTP not match':
			messages.info(request,'Invalid OTP Please check your code and try again.')

		else :
			messages.info(request,'Something went wrong! try again.')
	return render(request,'customer/Customer_user_login_hospital.html',{'doc_id':doc_id})
def customer_login_home(request):
	if request.method=="POST":
		username=request.POST.get('user_name')
		mobile=request.POST.get('mobile')
		user_otp=request.POST.get('otp')
		if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
		getattr(ssl, '_create_unverified_context', None)):
			ssl._create_default_https_context = ssl._create_unverified_context
		conn = http.client.HTTPSConnection("api.msg91.com")
		payload = ""
		conn.request("POST", "/api/v5/otp/verify?mobile="+"91"+mobile+"&otp="+user_otp+"&authkey=334231AXCttMDRD5efc1d91P1", payload)
		res = conn.getresponse()
		data = res.read()
		bytelist=data
		bytelist=bytelist.decode("utf-8")
		res = json.loads(bytelist)
		if res['type']=='success':
			if Customer.objects.filter(mobile=mobile).exists():
				customer_obj=Customer.objects.get(mobile=mobile)
				customer_id=customer_obj.customer_id
				request.session['customer_id']=customer_id
				request.session['visit_check']='Home_visit'
				return redirect('customer_home_page',customer_id=customer_id)
		elif res['message']=='OTP expired':
			messages.info(request,'OTP expired')
		elif res['message']=='OTP not match':
			messages.info(request,'Invalid OTP Please check your code and try again.')
		else :
			messages.info(request,'Something went wrong! try again.')
	return render(request,'customer/customer_user_login_home.html',)

def customer_login_hospital_pw(request,doc_id):
	if request.method=="POST":
		mobile_email=request.POST.get('mobile_email')
		password=request.POST.get('password')
		encripted_pass = Customer.objects.get( Q(email=mobile_email) | Q(mobile=mobile_email)).password
		password_check = check_password(password, encripted_pass)
		try:
			user=Customer.objects.get( Q(email=mobile_email) | Q(mobile=mobile_email))
			if password_check == True:
				customer_id=user.customer_id
				request.session['customer_id']=customer_id
				request.session['visit_check']='Hospital_visit'
				request.session['Doctor_pk_hospital']=doc_id
				if Pet.objects.filter(customer_id__customer_id=customer_id).exists():
					pet=Pet.objects.filter(customer_id__customer_id=customer_id).last()
					return redirect('pet_list')
				else :
					request.session['customer_id']=customer_id
					request.session['visit_check']='Hospital_visit'
					request.session['Doctor_pk_hospital']=doc_id
					return redirect('petdetails',doc_pk=doc_id)
		except Customer.DoesNotExist:
			messages.info(request,"Account doesn't exist Please Register")
		else:
			messages.info(request,'Enter valid email/number or password')
	return render(request,'customer/Customer_hospital_login_with_password.html',{'doc_id':doc_id})

def login_home_password(request):
	if request.method=="POST":
		mobile_email=request.POST.get('mobile_email')
		password=request.POST.get('password')
		encripted_pass = Customer.objects.get( Q(email=mobile_email) | Q(mobile=mobile_email)).password
		password_check = check_password(password, encripted_pass)
		try:
			user=Customer.objects.get( Q(email=mobile_email) | Q(mobile=mobile_email))
			if password_check == True:
				customer_id=user.customer_id
				request.session['customer_id']=customer_id
				request.session['visit_check']='Home_visit'
				return redirect('customer_home_page',customer_id=customer_id)
		except Customer.DoesNotExist:
			messages.info(request,"Account doesn't exist Please Register")
		else:
			messages.info(request,'Enter valid email/number or password')


	return render(request,'customer/customer_user_login_home_pw.html')

def complete_registration(request,customer_id):
	if request.method == "GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id :
				return render(request,'customer/complete_registration.html')
			else:
				return redirect ('customer_login_home')
		else:
			return redirect ('customer_login_home')


	if request.method=="POST":
		email=request.POST.get('email')
		if Customer.objects.filter(email=email).exists():

			messages.info(request,'Email already in use')
			return render(request,'customer/complete_registration.html')
		else:
			password=request.POST.get('password')
			encript_pass = make_password(password)
			address=request.POST.get('address')
			address=address.capitalize()
			Customer.objects.filter(customer_id=customer_id).update(email=email,
			password=encript_pass,address=address)
			return redirect('customer_home_page',customer_id=customer_id)

def view_profile(request,customer_id):

	if 'customer_id' in request.session:
		session_id=request.session['customer_id']
		if session_id == customer_id:
			customer_profile=Customer.objects.get(customer_id=customer_id)
			try:
				subscription_status=CustomerSubscribed.objects.get(customer_id__customer_id=customer_id)
			except:
				subscription_status=''
			return render(request,'customer/Customer_view_profile.html',{'customer_profile':customer_profile,'subscription_status':subscription_status,'customer_id':customer_id})
		else:
			return redirect('customer_login_home')
	else:
			return redirect('customer_login_home')
def view_profile_edit_name(request,customer_id):

	if request.method=="POST":
		name=request.POST.get('name')
		Customer.objects.filter(customer_id=customer_id).update(customer_name=name)
		return redirect('view_profile',customer_id=customer_id)
	if request.method =='GET':
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id:
				customer_profile=Customer.objects.get(customer_id=customer_id)
				return render(request,'customer/customer_profile_edit_name.html',{'customer_profile':customer_profile,'customer_id':customer_id})
			else:
				return redirect('customer_login_home')
		else:
			return redirect('customer_login_home')
def view_profile_edit_email(request,customer_id):

	if request.method=="POST":
		email=request.POST.get('email')
		if Customer.objects.filter(email=email).exists():
			messages.info(request,'Email already taken')
			customer_profile=Customer.objects.get(customer_id=customer_id)
			return render(request,'customer/customer_profile_edit_email.html',{'customer_profile':customer_profile,'customer_id':customer_id})
		else:
			Customer.objects.filter(customer_id=customer_id).update(email=email)
			return redirect('view_profile',customer_id=customer_id)
	if request.method =='GET':
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id:
				customer_profile=Customer.objects.get(customer_id=customer_id)
				return render(request,'customer/customer_profile_edit_email.html',{'customer_profile':customer_profile,'customer_id':customer_id})
			else:
				return redirect('customer_login_home')
		else:
			return redirect('customer_login_home')
def view_profile_edit_mobile(request,customer_id):

	if request.method=="POST":
		mobile=request.POST.get('mobile')
		if Customer.objects.filter(mobile=mobile).exists():
			messages.info(request,'Mobile already in use')
			customer_profile=Customer.objects.get(customer_id=customer_id)
			return render(request,'customer/customer_profile_edit_mobile.html',{'customer_profile':customer_profile,'customer_id':customer_id})
		else:
			Customer.objects.filter(customer_id=customer_id).update(mobile=mobile)
			return redirect('view_profile',customer_id=customer_id)
	if request.method =='GET':
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id:
				customer_profile=Customer.objects.get(customer_id=customer_id)
				return render(request,'customer/customer_profile_edit_mobile.html',{'customer_profile':customer_profile,'customer_id':customer_id})
			else:
				return redirect('customer_login_home')
		else:
				return redirect('customer_login_home')

def view_profile_edit_password(request,customer_id):
	if request.method=="POST":
		password=request.POST.get('password')
		encript_pass=make_password(password)
		Customer.objects.filter(customer_id=customer_id).update(password=encript_pass)
		return redirect('view_profile',customer_id=customer_id)
	if request.method =='GET':
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id:
				customer_profile=Customer.objects.get(customer_id=customer_id)
				return render(request,'customer/customer_profile_edit_password.html',{'customer_profile':customer_profile,'customer_id':customer_id})
			else:
				return redirect('customer_login_home')
		else:
			return redirect('customer_login_home')
def view_profile_edit_address(request,customer_id):
	if request.method=="POST":
		address=request.POST.get('address')
		Customer.objects.filter(customer_id=customer_id).update(address=address)
		return redirect('view_profile',customer_id=customer_id)
	if request.method =='GET':
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id:
				customer_profile=Customer.objects.get(customer_id=customer_id)
				return render(request,'customer/customer_profile_edit_address.html',{'customer_profile':customer_profile,'customer_id':customer_id})
			else:
				return redirect('customer_login_home')
		else:
			return redirect('customer_login_home')
#Doctor Moduel Views

#Doctor Module  Sub functions
def customers_list_conversion(customers):
	doc_list_qs=[]
	for customer in customers:
		customers=model_to_dict(customer)
		for k,v in customers.items():
			if k == 'pet_id':
				pet_id= customers.get('pet_id')
				customer_id=customers.get('customer_id')
				pet_dob=Pet.objects.get(id=pet_id)
				customer_name=Customer.objects.get(customer_id=customer_id)
				customer_name=customer_name.customer_name
				pet_breed=pet_dob.breed
				pet_dob=pet_dob.dob
				currentDate = datetime.date.today()
				deadlineDate= pet_dob
				daysLeft = deadlineDate - currentDate
				years = ((daysLeft.total_seconds())/(365.242*24*3600))
				yearsInt=int(years)
				months=(years-yearsInt)*12
				monthsInt=int(months)
				if yearsInt == -1:
					y='year'
				else:
					y='years'
				if monthsInt == -1:
					m='month'
				else:
					m='months'
				if monthsInt == 0:
					agestring=str(yearsInt)+y
					age=agestring.replace('-','')
				else:
					agestring=str(yearsInt)+y+','+str(monthsInt)+m
					age=agestring.replace('-','')
				customers['color']=age
				customers['date']=pet_breed
				customers['customer_id']=customer_name
				doc_list_qs.append(customers)
	return doc_list_qs

def set_id():
	pet = Pet.objects.all()
	if len(pet)==0:
		pet_id = 'PET' + str(len(pet) + 1)
		return pet_id
	else:
		petid=Pet.objects.last().pet_id
		petid=petid[3:]
		petid=int(petid)
		petid=petid + 1
		pet_id='PET' + str(petid)
		return pet_id

def datenone(value):
	if value=="":
		value='1000-01-01'
	else:
		value=value
	return value

def prescription_date_format(val,unit):
	if val == None:
		return None
	else:
		currentdate=datetime.date.today()
		yr=currentdate.year
		mth=currentdate.month
		if val == '':
			dose_date = '1000-01-01'
		if val != '':
			val=int(val)
			if unit == 'week':
				days=val*7
				dose_date=currentdate + datetime.timedelta(days=days)
			elif unit == 'days':
				days=val
				dose_date=currentdate + datetime.timedelta(days=days)
			elif unit == 'year':
				mth=0
				yr=val
				year=yr
				month=mth
				next_dose_year=currentdate.year+year
				currenthmonth=currentdate.month
				next_dose_month=currentdate.month+month
				next_dose_day=currentdate.day
				if next_dose_month >12:
					month_diff=abs(12-next_dose_month)
					next_dose_month=month_diff
					next_dose_year=next_dose_year+1
					if next_dose_month == 2:
						if (next_dose_year % 4) == 0:
							next_dose_day > 29
							next_dose_day=29
						elif (next_dose_year % 4) != 0:
							next_dose_day > 29
							next_dose_day=28
						elif (next_dose_year % 100) == 0:
							next_dose_day > 29
							next_dose_day=29
						elif (next_dose_year % 100) != 0:
							next_dose_day > 29
							next_dose_day=28
				dose_date = datetime.date(next_dose_year, next_dose_month, next_dose_day)
			elif unit == 'month':
				yr=0
				mth=val
				year=yr
				month=mth
				next_dose_year=currentdate.year+year
				currenthmonth=currentdate.month
				next_dose_month=currentdate.month+month
				next_dose_day=currentdate.day
				if next_dose_month >12:
					month_diff=abs(12-next_dose_month)
					next_dose_month=month_diff
					next_dose_year=next_dose_year+1
					if next_dose_month == 2:
						if (next_dose_year % 4) == 0:
							next_dose_day > 29
							next_dose_day=29
						elif (next_dose_year % 4) != 0:
							next_dose_day > 29
							next_dose_day=28
						elif (next_dose_year % 100) == 0:
							next_dose_day > 29
							next_dose_day=29
						elif (next_dose_year % 100) != 0:
							next_dose_day > 29
							next_dose_day=28
				dose_date = datetime.date(next_dose_year, next_dose_month, next_dose_day)
			print(dose_date)
		return dose_date


def prescription_date_format_reverse(val,unt):
	if val != None:
		date_now = date.today()
		date_future = date.strftime(val, "%Y-%m-%d")
		date_future = datetime.datetime.strptime(date_future, "%Y-%m-%d")
		date_future = date_future.date()
		if unt == 'days':
			delta = date_future - date_now
			diff = delta.days
			diff = delta.days
		elif unt == 'week':
			delta = date_future - date_now
			diff = delta.days
			diff = diff//7
		elif unt == 'month':
			diff = (date_future.year - date_now.year) * 12 + (date_future.month - date_now.month)
		elif unt == 'year':
			diff = (date_future.year - date_now.year)
		return diff


def vaccination_dict(dict_data):
	dict_data.pop('purpose_id',None)
	dict_data.pop('id',None)
	clean_dict={}
	for k,v in dict_data.items():
		k=k.replace('_'," ")
		clean_dict[k]=v
	return clean_dict

import datetime
def date_clean(dict_data):
	clean_date={}
	for key,value in [value for value in dict_data if value == '1000-01-01']: del dict_data[key]


def remove_empty_from_dict(d):
    if type(d) is dict:
        return dict((k, remove_empty_from_dict(v)) for k, v in d.items() if v and remove_empty_from_dict(v))
    elif type(d) is list:
        return [remove_empty_from_dict(v) for v in d if v and remove_empty_from_dict(v)]
    else:
        return d


try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

def dict_clean(dict_data):
	dict_data.pop('purpose_id',None)
	dict_data.pop('id',None)
	clean_dict={}
	for k,v in dict_data.items():

		if v != 'NO' and v != '' and v !=None and v != 'no':
			if type(v) == str:
				v=v.replace('[','').replace("'",'').replace(']','').replace('(','').replace(')','')
				k=k.replace('_',' ')
				clean_dict[k]=v
			if type(v) == int:
				clean_dict[k]=v
	return clean_dict


def count_quantity(days,day_time):
	if 'days' in days or 'day' in days:
			test_days=days.strip('days')
			day_time=empty_string_remove(day_time)
			test_time_list=day_time.split(',')
			test_time_list=len(test_time_list)
			quantity=int(test_days)*int(test_time_list)
			return quantity
	elif 'months' in days:
		test_days=days.strip('months')
		day_time=empty_string_remove(day_time)
		test_time_list=day_time.split(',')
		test_time_list=len(test_time_list)
		quantity=int(test_days)*int(test_time_list)*30
		return quantity


#Doctor Module Main Views

def doctor_login(request):
	if request.method == "POST":
		mobile=request.POST.get('username')
		password=request.POST.get('password')
		if Doctor.objects.filter(Mobile=mobile,password=password):
			doc_pk=Doctor.objects.get(Mobile=mobile).id
			request.session['doc_pk']=doc_pk
			return redirect ('list_patient')
	return render (request,'doctor/Doctor_login.html')


def list_patient(request):
	if 'doc_pk' in request.session:
		doc_pk = request.session.get('doc_pk')
		if request.method == "GET":
			try:
				today_date=date.today()
				next_day=today_date+timedelta(1)
				today_date_time = datetime.datetime.now()
				doc_pk=Doctor.objects.get(id=doc_pk)
				doc_list_qs = DoctorViewLog.objects.filter(doc_pk=doc_pk,
					booking_date=today_date)
				unatted_list=DoctorViewLog.objects.filter(doc_pk=doc_pk,
					status='A',booking_expiry_date=today_date)
				expired=[]
				#convert time into naive object
				utc=pytz.UTC
				for i in unatted_list:
					today_date_time_converted=utc.localize(today_date_time)
					if today_date_time_converted < i.booking_expiry :
						pass
					else:
						expired.append(i.pet_id.pet_id)

				for i in unatted_list:
					for x in expired:
						if i.pet_id.pet_id == x :
							DoctorViewLog.objects.filter(id=i.id).update(status="EX")
							Log.objects.filter(id=i.id).update(status="EX")

				updated_patients_list=DoctorViewLog.objects.filter(doc_pk=doc_pk,
				date=today_date)
				# doc_list_qs=customers_list_conversion(doc_list_qs)
				mode=DoctorLogList.objects.filter(mode='online')
				#segregation code
				cancelled_patients=DoctorViewLog.objects.filter(doc_pk=doc_pk,
				status="CN",booking_date=today_date).all()
				completed_patients=DoctorViewLog.objects.filter(doc_pk=doc_pk,
				status="C",booking_date=today_date).all()
				expired_patients=DoctorViewLog.objects.filter(doc_pk=doc_pk,
				status="EX",booking_expiry_date=today_date).all()
				#unclosed visit on next day i.e. on expiry day
				check_unattend_visit=DoctorViewLog.objects.filter(doc_pk=doc_pk,
				status="A",booking_expiry_date=today_date).all()

			except ObjectDoesNotExist:
				return HttpResponse('something went wrong')
			return render(request,'doctor/segregation.html',
			{'doc_list_qs':doc_list_qs,'today_date':today_date,
			'mode':mode,'doc_pk':doc_pk,
			'expired_patients':expired_patients,
			'cancelled_patients':cancelled_patients,
			'completed_patients':completed_patients,
			'expired':expired,'unatted_list':unatted_list,
			'check_unattend_visit':check_unattend_visit})
	else:
		return redirect('doctor_login')
	if request.method=='POST':
		doc_pk = request.session.get('doc_pk')
		if 'view' in request.POST:
			purpose_pk=request.POST.get('purpose_id')
			pet_pk = request.POST.get('pet_id')
			request.session['purpose_pk'] = purpose_pk
			request.session['pet_pk'] = pet_pk
			page_redirect=PurposeAndDiet.objects.filter(id=purpose_pk).last()
			print(page_redirect.vaccination_purpose,'vaccination_purpose')
			check_purpose=page_redirect.vaccination_purpose
			if check_purpose == "VACCINATION":
				return redirect('vaccination')
			elif check_purpose =="DEWORMING":
				return redirect('deworming')
			elif check_purpose == 'DEWORMING,VACCINATION' or check_purpose =='VACCINATION,DEWORMING':
				return redirect('vaccination')
			else:
				return redirect('assessment')
			return redirect ('visit_purpose2')
		else:
			filter_date=request.POST.get('filter_by_date')
			print(filter_date,'filter_datefilter_datefilter_date')
			if filter_date =="" or filter_date is None:
				pass
			else:
				filer_date_list = DoctorViewLog.objects.filter(doc_pk=doc_pk,booking_date=filter_date).all()
				print(filer_date_list)
				cancelled_patients=DoctorViewLog.objects.filter(doc_pk=doc_pk,status="CN",booking_date=filter_date).all()
				completed_patients=DoctorViewLog.objects.filter(doc_pk=doc_pk,status="C",booking_date=filter_date).all()
				#unclosed visit on filer day i.e. on expiry day
				check_unattend_visit=DoctorViewLog.objects.filter(doc_pk=doc_pk,status="A",booking_expiry_date=filter_date).all()
				expired_patients=DoctorViewLog.objects.filter(doc_pk=doc_pk,status="EX",booking_expiry_date=filter_date).all()
				doc_pk = Doctor.objects.get(id=doc_pk)
				return render(request,'doctor/segregation.html',{'doc_pk':doc_pk,
				'doc_list_qs':filer_date_list,'filter_date':filter_date,
				'cancelled_patients':cancelled_patients,
				'completed_patients':completed_patients,
				'check_unattend_visit':check_unattend_visit,
				'expired_patients':expired_patients,})
			doc_list_qs = []
			today_date = date.today()
			doc_pk = doc_pk
		doc_pk = Doctor.objects.get(id=doc_pk)
	return render(request,'doctor/segregation.html',{'doc_list_qs':doc_list_qs,
	'today_date':today_date,'doc_pk':doc_pk})


def vaccination(request):
	doc_pk = request.session.get('doc_pk')
	pet_pk = request.session.get('pet_pk')
	purpose_pk = request.session.get('purpose_pk')
	pet_obj=Pet.objects.filter(id=pet_pk).last()
	pet_obj_convert=pet_age_converter_single(pet_obj)
	purpose_pet_obj_diet=PurposeAndDiet.objects.filter(id=purpose_pk).last()
	pet_obj=Pet.objects.get(id=pet_pk)
	purpose_pet_obj_save=PurposeAndDiet.objects.filter(pet_id=pet_obj).last()
	purpose_pet_obj=PurposeAndDiet.objects.filter(pet_id=pet_obj).last()
	vaccination=Vaccination.objects.filter(pet=pet_obj).exclude(purpose_id__id=purpose_pk)
	last_vaccination=Vaccination_coustmer.objects.filter(pet=pet_obj).last()
	purpose_id=purpose_pk
	doc_pk_stock=Doctor.objects.get(id=doc_pk)
	purpose_pet_obj_onload=PurposeAndDiet.objects.get(id=purpose_pk)
	if pet_pk:
		pet_pk=pet_pk
	try:
		x=Vaccination.objects.filter(purpose_id=purpose_pk).last()
		x=model_to_dict(x)
	except:
		pass

	show_vaccination_list=[]
	for i in vaccination:
		if str(i.last_date_3_in_1_DAPV) !='1000-01-01':
			show_vaccination_list.append('3_in_1_DAPV')

		if str(i.last_date_4_in_1_DHPP) !='1000-01-01':
			show_vaccination_list.append('4_in_1_DHPP')

		if str(i.last_date_5_in_1_DA2PP) !='1000-01-01':
			show_vaccination_list.append('5_in_1_DA2PP')

		if str(i.last_date_6_in_1_DA2PPC) !='1000-01-01':
			show_vaccination_list.append('6_in_1_DA2PPC')

		if str(i.last_date_7_in_1_DA2PPVL2) !='1000-01-01':
			show_vaccination_list.append('7_in_1_DA2PPVL2')

		if str(i.last_date_rabies) !='1000-01-01':
			show_vaccination_list.append('rabies')

		if str(i.last_date_distemper) !='1000-01-01':
			show_vaccination_list.append('distemper')

		if str(i.last_date_CAV_1) !='1000-01-01':
			show_vaccination_list.append('CAV_1')

		if str(i.last_date_parovirus) !='1000-01-01':
			show_vaccination_list.append('parovirus')

		if str(i.last_date_parainfluenza) !='1000-01-01':
			show_vaccination_list.append('parainfluenza')

		if str(i.last_date_bordetella) !='1000-01-01':
			show_vaccination_list.append('bordetella')

		if str(i.last_date_CAV_2) !='1000-01-01':
			show_vaccination_list.append('CAV_2')

		if str(i.last_date_lyme) !='1000-01-01':
			show_vaccination_list.append('lyme')

		if str(i.last_date_corona) !='1000-01-01':
			show_vaccination_list.append('corona')

		if str(i.last_date_giardia) !='1000-01-01':
			show_vaccination_list.append('giardia')

		if str(i.last_date_Can_L) !='1000-01-01':
			show_vaccination_list.append('Can_L')

		if str(i.last_date_leptospirosis) !='1000-01-01':
			show_vaccination_list.append('leptospirosis')

		if str(i.last_date_9_in_1_vaccine) !='1000-01-01':
			show_vaccination_list.append('vaccine_9_in_1')

		if str(i.last_date_10_in_1_vaccine) !='1000-01-01':
			show_vaccination_list.append('10_in_1')

		if str(i.last_date_Feline_vaccine) !='1000-01-01':
			show_vaccination_list.append('Feline')

	show_vaccination_list_customer=[]
	last_vaccination_2=Vaccination_coustmer.objects.filter(pet=pet_obj)
	for i in last_vaccination_2:
		if str(i.last_date_3_in_1_DAPV) !='1000-01-01':
			show_vaccination_list_customer.append('3_in_1_DAPV')

		if str(i.last_date_4_in_1_DHPP) !='1000-01-01':
			show_vaccination_list_customer.append('4_in_1_DHPP')

		if str(i.last_date_5_in_1_DA2PP) !='1000-01-01':
			show_vaccination_list_customer.append('5_in_1_DA2PP')

		if str(i.last_date_6_in_1_DA2PPC) !='1000-01-01':
			show_vaccination_list_customer.append('6_in_1_DA2PPC')

		if str(i.last_date_7in1_DA2PPVL2) !='1000-01-01':
			show_vaccination_list_customer.append('7_in_1_DA2PPVL2')

		if str(i.last_date_rabies) !='1000-01-01':
			show_vaccination_list_customer.append('rabies')

		if str(i.last_date_distemper) !='1000-01-01':
			show_vaccination_list_customer.append('distemper')

		if str(i.last_date_CAV_1) !='1000-01-01':
			show_vaccination_list_customer.append('CAV_1')

		if str(i.last_date_parovirus) !='1000-01-01':
			show_vaccination_list_customer.append('parovirus')

		if str(i.last_date_parainfluenza) !='1000-01-01':
			show_vaccination_list_customer.append('parainfluenza')

		if str(i.last_date_bordetella) !='1000-01-01':
			show_vaccination_list_customer.append('bordetella')

		if str(i.last_date_CAV_2) !='1000-01-01':
			show_vaccination_list_customer.append('CAV_2')

		if str(i.last_date_lyme) !='1000-01-01':
			show_vaccination_list_customer.append('lyme')

		if str(i.last_date_corona) !='1000-01-01':
			show_vaccination_list_customer.append('corona')

		if str(i.last_date_giardia) !='1000-01-01':
			show_vaccination_list_customer.append('giardia')

		if str(i.last_date_Can_L) !='1000-01-01':
			show_vaccination_list_customer.append('Can_L')

		if str(i.last_date_leptospirosis) !='1000-01-01':
			show_vaccination_list_customer.append('leptospirosis')

		if str(i.last_date_9_in_1_vaccine) !='1000-01-01':
			show_vaccination_list_customer.append('vaccine_9_in_1')

		if str(i.last_date_10_in_1_vaccine) !='1000-01-01':
			show_vaccination_list_customer.append('10_in_1')

		if str(i.last_date_Feline_vaccine) !='1000-01-01':
			show_vaccination_list_customer.append('Feline')


	show_vaccination_list_customer=list(dict.fromkeys(show_vaccination_list_customer))
	if request.method == "GET":
		if 'doc_pk' in request.session:
			return render(request,'doctor/Doctor_vaccination.html',
			{'last_vaccination':last_vaccination,'pet_obj':pet_obj_convert,
			'purpose_pet_obj':purpose_pet_obj_onload,'doc_pk':doc_pk,
			'purpose_pet_obj_diet':purpose_pet_obj_diet,'vaccination':vaccination,
			'pet_pk':pet_pk,'purpose_pk':purpose_pk,'x':x,'doc_pk_stock':doc_pk_stock,
			'show_vaccination_list_customer':show_vaccination_list_customer,
			'show_vaccination_list':show_vaccination_list})
		else:
			return redirect('doctor_login')

	if request.method=='POST':
		if 'symptoms_name' in request.POST:
			try:
				vaccination=Vaccination()
				vaccination.purpose_id = purpose_pet_obj_save
				vaccination.pet=pet_obj
				last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
				last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
				vaccination.last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
				due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
				due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
				vaccination.due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
				last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
				last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
				vaccination.last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
				due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
				due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
				vaccination.due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
				last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
				last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
				vaccination.last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
				due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
				due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
				vaccination.due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
				last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
				last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
				vaccination.last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
				due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
				due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
				vaccination.due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
				last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
				last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
				vaccination.last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
				due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
				due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
				vaccination.due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
				last_date_rabies = request.POST.get('l_rabies')
				last_date_rabies = datenone(last_date_rabies)
				vaccination.last_date_rabies=last_date_rabies
				due_date_rabies=request.POST.get('d_rabies')
				due_date_rabies = datenone(due_date_rabies)
				vaccination.due_date_rabies=due_date_rabies
				last_date_distemper=request.POST.get('l_distemper')
				last_date_distemper = datenone(last_date_distemper)
				vaccination.last_date_distemper=last_date_distemper
				d_distemper=request.POST.get('d_distemper')
				d_distemper = datenone(d_distemper)
				vaccination.due_date_distemper=d_distemper
				last_date_hepatitis=request.POST.get('l_hepatitis')
				last_date_hepatitis = datenone(last_date_hepatitis)
				vaccination.last_date_CAV_1=last_date_hepatitis
				d_hepatitis=request.POST.get('d_hepatitis')
				d_hepatitis = datenone(d_hepatitis)
				vaccination.due_date_CAV_1=d_hepatitis
				last_date_parovirus=request.POST.get('l_parovirus')
				last_date_parovirus = datenone(last_date_parovirus)
				vaccination.last_date_parovirus=last_date_parovirus
				d_parovirus=request.POST.get('d_parovirus')
				d_parovirus = datenone(d_parovirus)
				vaccination.due_date_parovirus=d_parovirus
				last_date_parainfluenza=request.POST.get('l_parainfluenza')
				last_date_parainfluenza = datenone(last_date_parainfluenza)
				vaccination.last_date_parainfluenza=last_date_parainfluenza
				d_parainfluenza=request.POST.get('d_parainfluenza')
				d_parainfluenza = datenone(d_parainfluenza)
				vaccination.due_date_parainfluenza=d_parainfluenza
				last_date_bordetella=request.POST.get('l_bordetella')
				last_date_bordetella = datenone(last_date_bordetella)
				vaccination.last_date_bordetella=last_date_bordetella
				d_bordetella=request.POST.get('d_bordetella')
				d_bordetella = datenone(d_bordetella)
				vaccination.due_date_bordetella=d_bordetella
				last_date_l_CAV_2=request.POST.get('l_CAV_2')
				last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
				vaccination.last_date_CAV_2=last_date_l_CAV_2
				d_CAV_2=request.POST.get('d_CAV_2')
				d_CAV_2 = datenone(d_CAV_2)
				vaccination.due_date_CAV_2=d_CAV_2
				last_date_lymedisease=request.POST.get('l_lymedisease')
				last_date_lymedisease = datenone(last_date_lymedisease)
				vaccination.last_date_lyme=last_date_lymedisease
				d_lymedisease=request.POST.get('d_lymedisease')
				d_lymedisease = datenone(d_lymedisease)
				vaccination.due_date_lyme=d_lymedisease
				last_date_coronavirus=request.POST.get('l_coronavirus')
				last_date_coronavirus = datenone(last_date_coronavirus)
				vaccination.last_date_corona=last_date_coronavirus
				d_coronavirus=request.POST.get('d_coronavirus')
				d_coronavirus = datenone(d_coronavirus)
				vaccination.due_date_corona=d_coronavirus
				last_date_giardia=request.POST.get('l_giardia')
				last_date_giardia = datenone(last_date_giardia)
				vaccination.last_date_giardia=last_date_giardia
				d_giardia=request.POST.get('d_giardia')
				d_giardia = datenone(d_giardia)
				vaccination.due_date_giardia=d_giardia
				last_date_dhpp=request.POST.get('l_Can_L')
				last_date_dhpp = datenone(last_date_dhpp)
				vaccination.last_date_Can_L=last_date_dhpp
				d_dhpp=request.POST.get('d_Can_L')
				d_dhpp = datenone(d_dhpp)
				vaccination.due_date_Can_L=d_dhpp
				last_date_leptospirosis=request.POST.get('l_Leptospirosis')
				last_date_leptospirosis = datenone(last_date_leptospirosis)
				vaccination.last_date_leptospirosis=last_date_leptospirosis
				d_leptospirosis=request.POST.get('d_Leptospirosis')
				d_leptospirosis = datenone(d_leptospirosis)
				vaccination.due_date_leptospirosis=d_leptospirosis

				last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
				last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
				vaccination.last_date_9_in_1_vaccine=last_date_9_in_1_vaccine
				due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
				due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
				vaccination.due_date_9_in_1_vaccine=due_date_9_in_1_vaccine

				last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
				last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
				vaccination.last_date_10_in_1_vaccine=last_date_10_in_1_vaccine
				due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
				due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
				vaccination.due_date_10_in_1_vaccine=due_date_10_in_1_vaccine

				last_date_Feline_vaccine=request.POST.get('l_Feline')
				last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
				vaccination.last_date_Feline_vaccine=last_date_Feline_vaccine
				due_date_Feline_vaccine=request.POST.get('d_Feline')
				due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)
				vaccination.due_date_Feline_vaccine=due_date_Feline_vaccine
				vaccination.save()
				return redirect('symptoms')
			except:
				if Vaccination.objects.filter(purpose_id=purpose_pet_obj_save).exists:
					vaccination_id=Vaccination.objects.get(purpose_id=purpose_pet_obj_save).id
					last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
					last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
					last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
					due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
					due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
					due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
					last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
					last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
					due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
					due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
					due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
					last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
					last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
					due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
					due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
					due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
					last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
					last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
					last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
					due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
					due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
					last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
					last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
					last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
					due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
					due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
					due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
					last_date_rabies = request.POST.get('l_rabies')
					last_date_rabies = datenone(last_date_rabies)
					last_date_rabies=last_date_rabies
					due_date_rabies=request.POST.get('d_rabies')
					due_date_rabies = datenone(due_date_rabies)
					due_date_rabies=due_date_rabies
					last_date_distemper=request.POST.get('l_distemper')
					last_date_distemper = datenone(last_date_distemper)
					last_date_distemper=last_date_distemper
					d_distemper=request.POST.get('d_distemper')
					d_distemper = datenone(d_distemper)
					due_date_distemper=d_distemper
					last_date_hepatitis=request.POST.get('l_hepatitis')
					last_date_hepatitis = datenone(last_date_hepatitis)
					last_date_CAV_1=last_date_hepatitis
					d_hepatitis=request.POST.get('d_hepatitis')
					d_hepatitis = datenone(d_hepatitis)
					due_date_CAV_1=d_hepatitis
					last_date_parovirus=request.POST.get('l_parovirus')
					last_date_parovirus = datenone(last_date_parovirus)
					last_date_parovirus=last_date_parovirus
					d_parovirus=request.POST.get('d_parovirus')
					d_parovirus = datenone(d_parovirus)
					due_date_parovirus=d_parovirus
					last_date_parainfluenza=request.POST.get('l_parainfluenza')
					last_date_parainfluenza = datenone(last_date_parainfluenza)
					last_date_parainfluenza=last_date_parainfluenza
					d_parainfluenza=request.POST.get('d_parainfluenza')
					d_parainfluenza = datenone(d_parainfluenza)
					due_date_parainfluenza=d_parainfluenza
					last_date_bordetella=request.POST.get('l_bordetella')
					last_date_bordetella = datenone(last_date_bordetella)
					last_date_bordetella=last_date_bordetella
					d_bordetella=request.POST.get('d_bordetella')
					d_bordetella = datenone(d_bordetella)
					due_date_bordetella=d_bordetella
					last_date_leptospirosis=request.POST.get('l_Leptospirosis')
					last_date_leptospirosis = datenone(last_date_leptospirosis)
					last_date_leptospirosis=last_date_leptospirosis
					d_leptospirosis=request.POST.get('d_Leptospirosis')
					d_leptospirosis = datenone(d_leptospirosis)
					due_date_leptospirosis=d_leptospirosis
					last_date_lymedisease=request.POST.get('l_lymedisease')
					last_date_lymedisease = datenone(last_date_lymedisease)
					last_date_lyme=last_date_lymedisease
					d_lymedisease=request.POST.get('d_lymedisease')
					d_lymedisease = datenone(d_lymedisease)
					due_date_lyme=d_lymedisease
					last_date_coronavirus=request.POST.get('l_coronavirus')
					last_date_coronavirus = datenone(last_date_coronavirus)
					last_date_corona=last_date_coronavirus
					d_coronavirus=request.POST.get('d_coronavirus')
					d_coronavirus = datenone(d_coronavirus)
					due_date_corona=d_coronavirus
					last_date_giardia=request.POST.get('l_giardia')
					last_date_giardia = datenone(last_date_giardia)
					last_date_giardia=last_date_giardia
					d_giardia=request.POST.get('d_giardia')
					d_giardia = datenone(d_giardia)
					due_date_giardia=d_giardia
					last_date_dhpp=request.POST.get('l_Can_L')
					last_date_dhpp = datenone(last_date_dhpp)
					last_date_Can_L=last_date_dhpp
					d_dhpp=request.POST.get('d_Can_L')
					d_dhpp = datenone(d_dhpp)
					due_date_Can_L=d_dhpp
					last_date_l_CAV_2=request.POST.get('l_CAV_2')
					last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
					last_date_CAV_2=last_date_l_CAV_2
					d_CAV_2=request.POST.get('d_CAV_2')
					d_CAV_2 = datenone(d_CAV_2)
					due_date_CAV_2=d_CAV_2

					last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
					last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
					due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
					due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
					last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
					last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
					due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
					due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
					last_date_Feline_vaccine=request.POST.get('l_Feline')
					last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
					due_date_Feline_vaccine=request.POST.get('d_Feline')
					due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)
					Vaccination.objects.filter(id=vaccination_id).update(last_date_bordetella=last_date_bordetella,
					due_date_bordetella=due_date_bordetella,last_date_lyme=last_date_lyme,
					due_date_lyme=due_date_lyme,last_date_leptospirosis=last_date_leptospirosis,
					due_date_leptospirosis=due_date_leptospirosis,
					last_date_CAV_2=last_date_l_CAV_2,due_date_CAV_2=due_date_CAV_2,
					last_date_corona=last_date_corona,due_date_corona=due_date_corona,
					last_date_giardia=last_date_giardia,due_date_giardia=due_date_giardia,
					last_date_Can_L=last_date_Can_L,due_date_Can_L=due_date_Can_L,
					last_date_3_in_1_DAPV=last_date_3_in_1_DAPV,
					due_date_3_in_1_DAPV=due_date_3_in_1_DAPV,
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP,
					due_date_4_in_1_DHPP=due_date_4_in_1_DHPP,
					last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC,
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC,
					last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2,
					due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2,
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP,
					due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP,
					last_date_rabies=last_date_rabies,due_date_rabies=due_date_rabies,
					last_date_distemper=last_date_distemper,due_date_distemper=due_date_distemper,
					last_date_CAV_1=last_date_CAV_1,due_date_CAV_1=due_date_CAV_1,
					last_date_parovirus=last_date_parovirus,due_date_parovirus=due_date_parovirus,
					last_date_parainfluenza=last_date_parainfluenza,
					due_date_parainfluenza=due_date_parainfluenza,last_date_9_in_1_vaccine=last_date_9_in_1_vaccine,due_date_9_in_1_vaccine=due_date_9_in_1_vaccine,
					last_date_10_in_1_vaccine=last_date_10_in_1_vaccine,
					due_date_10_in_1_vaccine=due_date_10_in_1_vaccine,last_date_Feline_vaccine=last_date_Feline_vaccine,due_date_Feline_vaccine=due_date_Feline_vaccine)
					return redirect('symptoms')
		elif 'assessment_name' in request.POST:
			try:
				vaccination=Vaccination()
				vaccination.purpose_id = purpose_pet_obj_save
				vaccination.pet=pet_obj
				last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
				last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
				vaccination.last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
				due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
				due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
				vaccination.due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
				last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
				last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
				vaccination.last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
				due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
				due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
				vaccination.due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
				last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
				last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
				vaccination.last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
				due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
				due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
				vaccination.due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
				last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
				last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
				vaccination.last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
				due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
				due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
				vaccination.due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
				last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
				last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
				vaccination.last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
				due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
				due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
				vaccination.due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
				last_date_rabies = request.POST.get('l_rabies')
				last_date_rabies = datenone(last_date_rabies)
				vaccination.last_date_rabies=last_date_rabies
				due_date_rabies=request.POST.get('d_rabies')
				due_date_rabies = datenone(due_date_rabies)
				vaccination.due_date_rabies=due_date_rabies
				last_date_distemper=request.POST.get('l_distemper')
				last_date_distemper = datenone(last_date_distemper)
				vaccination.last_date_distemper=last_date_distemper
				d_distemper=request.POST.get('d_distemper')
				d_distemper = datenone(d_distemper)
				vaccination.due_date_distemper=d_distemper
				last_date_hepatitis=request.POST.get('l_hepatitis')
				last_date_hepatitis = datenone(last_date_hepatitis)
				vaccination.last_date_CAV_1=last_date_hepatitis
				d_hepatitis=request.POST.get('d_hepatitis')
				d_hepatitis = datenone(d_hepatitis)
				vaccination.due_date_CAV_1=d_hepatitis
				last_date_parovirus=request.POST.get('l_parovirus')
				last_date_parovirus = datenone(last_date_parovirus)
				vaccination.last_date_parovirus=last_date_parovirus
				d_parovirus=request.POST.get('d_parovirus')
				d_parovirus = datenone(d_parovirus)
				vaccination.due_date_parovirus=d_parovirus
				last_date_parainfluenza=request.POST.get('l_parainfluenza')
				last_date_parainfluenza = datenone(last_date_parainfluenza)
				vaccination.last_date_parainfluenza=last_date_parainfluenza
				d_parainfluenza=request.POST.get('d_parainfluenza')
				d_parainfluenza = datenone(d_parainfluenza)
				vaccination.due_date_parainfluenza=d_parainfluenza
				last_date_bordetella=request.POST.get('l_bordetella')
				last_date_bordetella = datenone(last_date_bordetella)
				vaccination.last_date_bordetella=last_date_bordetella
				d_bordetella=request.POST.get('d_bordetella')
				d_bordetella = datenone(d_bordetella)
				vaccination.due_date_bordetella=d_bordetella
				last_date_l_CAV_2=request.POST.get('l_CAV_2')
				last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
				vaccination.last_date_CAV_2=last_date_l_CAV_2
				d_CAV_2=request.POST.get('d_CAV_2')
				d_CAV_2 = datenone(d_CAV_2)
				vaccination.due_date_CAV_2=d_CAV_2
				last_date_lymedisease=request.POST.get('l_lymedisease')
				last_date_lymedisease = datenone(last_date_lymedisease)
				vaccination.last_date_lyme=last_date_lymedisease
				d_lymedisease=request.POST.get('d_lymedisease')
				d_lymedisease = datenone(d_lymedisease)
				vaccination.due_date_lyme=d_lymedisease
				last_date_coronavirus=request.POST.get('l_coronavirus')
				last_date_coronavirus = datenone(last_date_coronavirus)
				vaccination.last_date_corona=last_date_coronavirus
				d_coronavirus=request.POST.get('d_coronavirus')
				d_coronavirus = datenone(d_coronavirus)
				vaccination.due_date_corona=d_coronavirus
				last_date_giardia=request.POST.get('l_giardia')
				last_date_giardia = datenone(last_date_giardia)
				vaccination.last_date_giardia=last_date_giardia
				d_giardia=request.POST.get('d_giardia')
				d_giardia = datenone(d_giardia)
				vaccination.due_date_giardia=d_giardia
				last_date_dhpp=request.POST.get('l_Can_L')
				last_date_dhpp = datenone(last_date_dhpp)
				vaccination.last_date_Can_L=last_date_dhpp
				d_dhpp=request.POST.get('d_Can_L')
				d_dhpp = datenone(d_dhpp)
				vaccination.due_date_Can_L=d_dhpp
				last_date_leptospirosis=request.POST.get('l_Leptospirosis')
				last_date_leptospirosis = datenone(last_date_leptospirosis)
				vaccination.last_date_leptospirosis=last_date_leptospirosis
				d_leptospirosis=request.POST.get('d_Leptospirosis')
				d_leptospirosis = datenone(d_leptospirosis)
				vaccination.due_date_leptospirosis=d_leptospirosis

				last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
				last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
				vaccination.last_date_9_in_1_vaccine=last_date_9_in_1_vaccine
				due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
				due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
				vaccination.due_date_9_in_1_vaccine=due_date_9_in_1_vaccine

				last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
				last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
				vaccination.last_date_10_in_1_vaccine=last_date_10_in_1_vaccine
				due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
				due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
				vaccination.due_date_10_in_1_vaccine=due_date_10_in_1_vaccine

				last_date_Feline_vaccine=request.POST.get('l_Feline')
				last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
				vaccination.last_date_Feline_vaccine=last_date_Feline_vaccine
				due_date_Feline_vaccine=request.POST.get('d_Feline')
				due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)
				vaccination.due_date_Feline_vaccine=due_date_Feline_vaccine
				vaccination.save()
				return redirect('assessment')
			except:
				if Vaccination.objects.filter(purpose_id=purpose_pet_obj_save).exists:
					vaccination_id=Vaccination.objects.get(purpose_id=purpose_pet_obj_save).id
					last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
					last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
					last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
					due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
					due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
					due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
					last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
					last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
					due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
					due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
					due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
					last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
					last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
					due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
					due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
					due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
					last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
					last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
					last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
					due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
					due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
					last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
					last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
					last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
					due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
					due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
					due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
					last_date_rabies = request.POST.get('l_rabies')
					last_date_rabies = datenone(last_date_rabies)
					last_date_rabies=last_date_rabies
					due_date_rabies=request.POST.get('d_rabies')
					due_date_rabies = datenone(due_date_rabies)
					due_date_rabies=due_date_rabies
					last_date_distemper=request.POST.get('l_distemper')
					last_date_distemper = datenone(last_date_distemper)
					last_date_distemper=last_date_distemper
					d_distemper=request.POST.get('d_distemper')
					d_distemper = datenone(d_distemper)
					due_date_distemper=d_distemper
					last_date_hepatitis=request.POST.get('l_hepatitis')
					last_date_hepatitis = datenone(last_date_hepatitis)
					last_date_CAV_1=last_date_hepatitis
					d_hepatitis=request.POST.get('d_hepatitis')
					d_hepatitis = datenone(d_hepatitis)
					due_date_CAV_1=d_hepatitis
					last_date_parovirus=request.POST.get('l_parovirus')
					last_date_parovirus = datenone(last_date_parovirus)
					last_date_parovirus=last_date_parovirus
					d_parovirus=request.POST.get('d_parovirus')
					d_parovirus = datenone(d_parovirus)
					due_date_parovirus=d_parovirus
					last_date_parainfluenza=request.POST.get('l_parainfluenza')
					last_date_parainfluenza = datenone(last_date_parainfluenza)
					last_date_parainfluenza=last_date_parainfluenza
					d_parainfluenza=request.POST.get('d_parainfluenza')
					d_parainfluenza = datenone(d_parainfluenza)
					due_date_parainfluenza=d_parainfluenza
					last_date_bordetella=request.POST.get('l_bordetella')
					last_date_bordetella = datenone(last_date_bordetella)
					last_date_bordetella=last_date_bordetella
					d_bordetella=request.POST.get('d_bordetella')
					d_bordetella = datenone(d_bordetella)
					due_date_bordetella=d_bordetella
					last_date_leptospirosis=request.POST.get('l_Leptospirosis')
					last_date_leptospirosis = datenone(last_date_leptospirosis)
					last_date_leptospirosis=last_date_leptospirosis
					d_leptospirosis=request.POST.get('d_Leptospirosis')
					d_leptospirosis = datenone(d_leptospirosis)
					due_date_leptospirosis=d_leptospirosis
					last_date_lymedisease=request.POST.get('l_lymedisease')
					last_date_lymedisease = datenone(last_date_lymedisease)
					last_date_lyme=last_date_lymedisease
					d_lymedisease=request.POST.get('d_lymedisease')
					d_lymedisease = datenone(d_lymedisease)
					due_date_lyme=d_lymedisease
					last_date_coronavirus=request.POST.get('l_coronavirus')
					last_date_coronavirus = datenone(last_date_coronavirus)
					last_date_corona=last_date_coronavirus
					d_coronavirus=request.POST.get('d_coronavirus')
					d_coronavirus = datenone(d_coronavirus)
					due_date_corona=d_coronavirus
					last_date_giardia=request.POST.get('l_giardia')
					last_date_giardia = datenone(last_date_giardia)
					last_date_giardia=last_date_giardia
					d_giardia=request.POST.get('d_giardia')
					d_giardia = datenone(d_giardia)
					due_date_giardia=d_giardia
					last_date_dhpp=request.POST.get('l_Can_L')
					last_date_dhpp = datenone(last_date_dhpp)
					last_date_Can_L=last_date_dhpp
					d_dhpp=request.POST.get('d_Can_L')
					d_dhpp = datenone(d_dhpp)
					due_date_Can_L=d_dhpp
					last_date_l_CAV_2=request.POST.get('l_CAV_2')
					last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
					last_date_CAV_2=last_date_l_CAV_2
					d_CAV_2=request.POST.get('d_CAV_2')
					d_CAV_2 = datenone(d_CAV_2)
					due_date_CAV_2=d_CAV_2

					last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
					last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
					due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
					due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
					last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
					last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
					due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
					due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
					last_date_Feline_vaccine=request.POST.get('l_Feline')
					last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
					due_date_Feline_vaccine=request.POST.get('d_Feline')
					due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)

					Vaccination.objects.filter(id=vaccination_id).update(last_date_bordetella=last_date_bordetella,
					due_date_bordetella=due_date_bordetella,
					last_date_lyme=last_date_lyme,due_date_lyme=due_date_lyme,
					last_date_leptospirosis=last_date_leptospirosis,
					due_date_leptospirosis=due_date_leptospirosis,
					last_date_CAV_2=last_date_l_CAV_2,due_date_CAV_2=due_date_CAV_2,
					last_date_corona=last_date_corona,due_date_corona=due_date_corona,
					last_date_giardia=last_date_giardia,due_date_giardia=due_date_giardia,
					last_date_Can_L=last_date_Can_L,due_date_Can_L=due_date_Can_L,
					last_date_3_in_1_DAPV=last_date_3_in_1_DAPV,
					due_date_3_in_1_DAPV=due_date_3_in_1_DAPV,
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP,
					due_date_4_in_1_DHPP=due_date_4_in_1_DHPP,
					last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC,
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC,
					last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2,
					due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2,
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP,
					due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP,
					last_date_rabies=last_date_rabies,due_date_rabies=due_date_rabies,
					last_date_distemper=last_date_distemper,
					due_date_distemper=due_date_distemper,last_date_CAV_1=last_date_CAV_1,
					due_date_CAV_1=due_date_CAV_1,last_date_parovirus=last_date_parovirus,
					due_date_parovirus=due_date_parovirus,
					last_date_parainfluenza=last_date_parainfluenza,
					due_date_parainfluenza=due_date_parainfluenza,last_date_9_in_1_vaccine=last_date_9_in_1_vaccine,due_date_9_in_1_vaccine=due_date_9_in_1_vaccine,
					last_date_10_in_1_vaccine=last_date_10_in_1_vaccine,
					due_date_10_in_1_vaccine=due_date_10_in_1_vaccine,last_date_Feline_vaccine=last_date_Feline_vaccine,due_date_Feline_vaccine=due_date_Feline_vaccine)
					return redirect('assessment')
		elif 'vitals_name' in request.POST:
			try:
				vaccination=Vaccination()
				vaccination.purpose_id = purpose_pet_obj_save
				vaccination.pet=pet_obj
				last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
				last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
				vaccination.last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
				due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
				due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
				vaccination.due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
				last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
				last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
				vaccination.last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
				due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
				due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
				vaccination.due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
				last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
				last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
				vaccination.last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
				due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
				due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
				vaccination.due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
				last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
				last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
				vaccination.last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
				due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
				due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
				vaccination.due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
				last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
				last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
				vaccination.last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
				due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
				due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
				vaccination.due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
				last_date_rabies = request.POST.get('l_rabies')
				last_date_rabies = datenone(last_date_rabies)
				vaccination.last_date_rabies=last_date_rabies
				due_date_rabies=request.POST.get('d_rabies')
				due_date_rabies = datenone(due_date_rabies)
				vaccination.due_date_rabies=due_date_rabies
				last_date_distemper=request.POST.get('l_distemper')
				last_date_distemper = datenone(last_date_distemper)
				vaccination.last_date_distemper=last_date_distemper
				d_distemper=request.POST.get('d_distemper')
				d_distemper = datenone(d_distemper)
				vaccination.due_date_distemper=d_distemper
				last_date_hepatitis=request.POST.get('l_hepatitis')
				last_date_hepatitis = datenone(last_date_hepatitis)
				vaccination.last_date_CAV_1=last_date_hepatitis
				d_hepatitis=request.POST.get('d_hepatitis')
				d_hepatitis = datenone(d_hepatitis)
				vaccination.due_date_CAV_1=d_hepatitis
				last_date_parovirus=request.POST.get('l_parovirus')
				last_date_parovirus = datenone(last_date_parovirus)
				vaccination.last_date_parovirus=last_date_parovirus
				d_parovirus=request.POST.get('d_parovirus')
				d_parovirus = datenone(d_parovirus)
				vaccination.due_date_parovirus=d_parovirus
				last_date_parainfluenza=request.POST.get('l_parainfluenza')
				last_date_parainfluenza = datenone(last_date_parainfluenza)
				vaccination.last_date_parainfluenza=last_date_parainfluenza
				d_parainfluenza=request.POST.get('d_parainfluenza')
				d_parainfluenza = datenone(d_parainfluenza)
				vaccination.due_date_parainfluenza=d_parainfluenza
				last_date_bordetella=request.POST.get('l_bordetella')
				last_date_bordetella = datenone(last_date_bordetella)
				vaccination.last_date_bordetella=last_date_bordetella
				d_bordetella=request.POST.get('d_bordetella')
				d_bordetella = datenone(d_bordetella)
				vaccination.due_date_bordetella=d_bordetella
				last_date_l_CAV_2=request.POST.get('l_CAV_2')
				last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
				vaccination.last_date_CAV_2=last_date_l_CAV_2
				d_CAV_2=request.POST.get('d_CAV_2')
				d_CAV_2 = datenone(d_CAV_2)
				vaccination.due_date_CAV_2=d_CAV_2
				last_date_lymedisease=request.POST.get('l_lymedisease')
				last_date_lymedisease = datenone(last_date_lymedisease)
				vaccination.last_date_lyme=last_date_lymedisease
				d_lymedisease=request.POST.get('d_lymedisease')
				d_lymedisease = datenone(d_lymedisease)
				vaccination.due_date_lyme=d_lymedisease
				last_date_coronavirus=request.POST.get('l_coronavirus')
				last_date_coronavirus = datenone(last_date_coronavirus)
				vaccination.last_date_corona=last_date_coronavirus
				d_coronavirus=request.POST.get('d_coronavirus')
				d_coronavirus = datenone(d_coronavirus)
				vaccination.due_date_corona=d_coronavirus
				last_date_giardia=request.POST.get('l_giardia')
				last_date_giardia = datenone(last_date_giardia)
				vaccination.last_date_giardia=last_date_giardia
				d_giardia=request.POST.get('d_giardia')
				d_giardia = datenone(d_giardia)
				vaccination.due_date_giardia=d_giardia
				last_date_dhpp=request.POST.get('l_Can_L')
				last_date_dhpp = datenone(last_date_dhpp)
				vaccination.last_date_Can_L=last_date_dhpp
				d_dhpp=request.POST.get('d_Can_L')
				d_dhpp = datenone(d_dhpp)
				vaccination.due_date_Can_L=d_dhpp
				last_date_leptospirosis=request.POST.get('l_Leptospirosis')
				last_date_leptospirosis = datenone(last_date_leptospirosis)
				vaccination.last_date_leptospirosis=last_date_leptospirosis
				d_leptospirosis=request.POST.get('d_Leptospirosis')
				d_leptospirosis = datenone(d_leptospirosis)
				vaccination.due_date_leptospirosis=d_leptospirosis

				last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
				last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
				vaccination.last_date_9_in_1_vaccine=last_date_9_in_1_vaccine
				due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
				due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
				vaccination.due_date_9_in_1_vaccine=due_date_9_in_1_vaccine

				last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
				last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
				vaccination.last_date_10_in_1_vaccine=last_date_10_in_1_vaccine
				due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
				due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
				vaccination.due_date_10_in_1_vaccine=due_date_10_in_1_vaccine

				last_date_Feline_vaccine=request.POST.get('l_Feline')
				last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
				vaccination.last_date_Feline_vaccine=last_date_Feline_vaccine
				due_date_Feline_vaccine=request.POST.get('d_Feline')
				due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)
				vaccination.due_date_Feline_vaccine=due_date_Feline_vaccine
				vaccination.save()
				return redirect('vitals')
			except:
				if Vaccination.objects.filter(purpose_id=purpose_pet_obj_save).exists:
					vaccination_id=Vaccination.objects.get(purpose_id=purpose_pet_obj_save).id
					last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
					last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
					last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
					due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
					due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
					due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
					last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
					last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
					due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
					due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
					due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
					last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
					last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
					due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
					due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
					due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
					last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
					last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
					last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
					due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
					due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
					last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
					last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
					last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
					due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
					due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
					due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
					last_date_rabies = request.POST.get('l_rabies')
					last_date_rabies = datenone(last_date_rabies)
					last_date_rabies=last_date_rabies
					due_date_rabies=request.POST.get('d_rabies')
					due_date_rabies = datenone(due_date_rabies)
					due_date_rabies=due_date_rabies
					last_date_distemper=request.POST.get('l_distemper')
					last_date_distemper = datenone(last_date_distemper)
					last_date_distemper=last_date_distemper
					d_distemper=request.POST.get('d_distemper')
					d_distemper = datenone(d_distemper)
					due_date_distemper=d_distemper
					last_date_hepatitis=request.POST.get('l_hepatitis')
					last_date_hepatitis = datenone(last_date_hepatitis)
					last_date_CAV_1=last_date_hepatitis
					d_hepatitis=request.POST.get('d_hepatitis')
					d_hepatitis = datenone(d_hepatitis)
					due_date_CAV_1=d_hepatitis
					last_date_parovirus=request.POST.get('l_parovirus')
					last_date_parovirus = datenone(last_date_parovirus)
					last_date_parovirus=last_date_parovirus
					d_parovirus=request.POST.get('d_parovirus')
					d_parovirus = datenone(d_parovirus)
					due_date_parovirus=d_parovirus
					last_date_parainfluenza=request.POST.get('l_parainfluenza')
					last_date_parainfluenza = datenone(last_date_parainfluenza)
					last_date_parainfluenza=last_date_parainfluenza
					d_parainfluenza=request.POST.get('d_parainfluenza')
					d_parainfluenza = datenone(d_parainfluenza)
					due_date_parainfluenza=d_parainfluenza
					last_date_bordetella=request.POST.get('l_bordetella')
					last_date_bordetella = datenone(last_date_bordetella)
					last_date_bordetella=last_date_bordetella
					d_bordetella=request.POST.get('d_bordetella')
					d_bordetella = datenone(d_bordetella)
					due_date_bordetella=d_bordetella
					last_date_leptospirosis=request.POST.get('l_Leptospirosis')
					last_date_leptospirosis = datenone(last_date_leptospirosis)
					last_date_leptospirosis=last_date_leptospirosis
					d_leptospirosis=request.POST.get('d_Leptospirosis')
					d_leptospirosis = datenone(d_leptospirosis)
					due_date_leptospirosis=d_leptospirosis
					last_date_lymedisease=request.POST.get('l_lymedisease')
					last_date_lymedisease = datenone(last_date_lymedisease)
					last_date_lyme=last_date_lymedisease
					d_lymedisease=request.POST.get('d_lymedisease')
					d_lymedisease = datenone(d_lymedisease)
					due_date_lyme=d_lymedisease
					last_date_coronavirus=request.POST.get('l_coronavirus')
					last_date_coronavirus = datenone(last_date_coronavirus)
					last_date_corona=last_date_coronavirus
					d_coronavirus=request.POST.get('d_coronavirus')
					d_coronavirus = datenone(d_coronavirus)
					due_date_corona=d_coronavirus
					last_date_giardia=request.POST.get('l_giardia')
					last_date_giardia = datenone(last_date_giardia)
					last_date_giardia=last_date_giardia
					d_giardia=request.POST.get('d_giardia')
					d_giardia = datenone(d_giardia)
					due_date_giardia=d_giardia
					last_date_dhpp=request.POST.get('l_Can_L')
					last_date_dhpp = datenone(last_date_dhpp)
					last_date_Can_L=last_date_dhpp
					d_dhpp=request.POST.get('d_Can_L')
					d_dhpp = datenone(d_dhpp)
					due_date_Can_L=d_dhpp
					last_date_l_CAV_2=request.POST.get('l_CAV_2')
					last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
					last_date_CAV_2=last_date_l_CAV_2
					d_CAV_2=request.POST.get('d_CAV_2')
					d_CAV_2 = datenone(d_CAV_2)
					due_date_CAV_2=d_CAV_2

					last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
					last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
					due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
					due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
					last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
					last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
					due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
					due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
					last_date_Feline_vaccine=request.POST.get('l_Feline')
					last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
					due_date_Feline_vaccine=request.POST.get('d_Feline')
					due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)

					Vaccination.objects.filter(id=vaccination_id).update(last_date_bordetella=last_date_bordetella,due_date_bordetella=due_date_bordetella,
					last_date_lyme=last_date_lyme,due_date_lyme=due_date_lyme,last_date_leptospirosis=last_date_leptospirosis,due_date_leptospirosis=due_date_leptospirosis,last_date_CAV_2=last_date_l_CAV_2,due_date_CAV_2=due_date_CAV_2,
					last_date_corona=last_date_corona,due_date_corona=due_date_corona,last_date_giardia=last_date_giardia,due_date_giardia=due_date_giardia,
					last_date_Can_L=last_date_Can_L,due_date_Can_L=due_date_Can_L,last_date_3_in_1_DAPV=last_date_3_in_1_DAPV,due_date_3_in_1_DAPV=due_date_3_in_1_DAPV,
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP,due_date_4_in_1_DHPP=due_date_4_in_1_DHPP,last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC,
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC,last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2,due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2,
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP,due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP,last_date_rabies=last_date_rabies,due_date_rabies=due_date_rabies,
					last_date_distemper=last_date_distemper,due_date_distemper=due_date_distemper,last_date_CAV_1=last_date_CAV_1,due_date_CAV_1=due_date_CAV_1,
					last_date_parovirus=last_date_parovirus,due_date_parovirus=due_date_parovirus,last_date_parainfluenza=last_date_parainfluenza,due_date_parainfluenza=due_date_parainfluenza,
					last_date_9_in_1_vaccine=last_date_9_in_1_vaccine,due_date_9_in_1_vaccine=due_date_9_in_1_vaccine,last_date_10_in_1_vaccine=last_date_10_in_1_vaccine,
					due_date_10_in_1_vaccine=due_date_10_in_1_vaccine,last_date_Feline_vaccine=last_date_Feline_vaccine,due_date_Feline_vaccine=due_date_Feline_vaccine)
					return redirect('vitals')
		elif 'diagnostic_name' in request.POST:
			try:
				vaccination=Vaccination()
				vaccination.purpose_id = purpose_pet_obj_save
				vaccination.pet=pet_obj
				last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
				last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
				vaccination.last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
				due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
				due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
				vaccination.due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
				last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
				last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
				vaccination.last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
				due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
				due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
				vaccination.due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
				last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
				last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
				vaccination.last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
				due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
				due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
				vaccination.due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
				last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
				last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
				vaccination.last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
				due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
				due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
				vaccination.due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
				last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
				last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
				vaccination.last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
				due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
				due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
				vaccination.due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
				last_date_rabies = request.POST.get('l_rabies')
				last_date_rabies = datenone(last_date_rabies)
				vaccination.last_date_rabies=last_date_rabies
				due_date_rabies=request.POST.get('d_rabies')
				due_date_rabies = datenone(due_date_rabies)
				vaccination.due_date_rabies=due_date_rabies
				last_date_distemper=request.POST.get('l_distemper')
				last_date_distemper = datenone(last_date_distemper)
				vaccination.last_date_distemper=last_date_distemper
				d_distemper=request.POST.get('d_distemper')
				d_distemper = datenone(d_distemper)
				vaccination.due_date_distemper=d_distemper
				last_date_hepatitis=request.POST.get('l_hepatitis')
				last_date_hepatitis = datenone(last_date_hepatitis)
				vaccination.last_date_CAV_1=last_date_hepatitis
				d_hepatitis=request.POST.get('d_hepatitis')
				d_hepatitis = datenone(d_hepatitis)
				vaccination.due_date_CAV_1=d_hepatitis
				last_date_parovirus=request.POST.get('l_parovirus')
				last_date_parovirus = datenone(last_date_parovirus)
				vaccination.last_date_parovirus=last_date_parovirus
				d_parovirus=request.POST.get('d_parovirus')
				d_parovirus = datenone(d_parovirus)
				vaccination.due_date_parovirus=d_parovirus
				last_date_parainfluenza=request.POST.get('l_parainfluenza')
				last_date_parainfluenza = datenone(last_date_parainfluenza)
				vaccination.last_date_parainfluenza=last_date_parainfluenza
				d_parainfluenza=request.POST.get('d_parainfluenza')
				d_parainfluenza = datenone(d_parainfluenza)
				vaccination.due_date_parainfluenza=d_parainfluenza
				last_date_bordetella=request.POST.get('l_bordetella')
				last_date_bordetella = datenone(last_date_bordetella)
				vaccination.last_date_bordetella=last_date_bordetella
				d_bordetella=request.POST.get('d_bordetella')
				d_bordetella = datenone(d_bordetella)
				vaccination.due_date_bordetella=d_bordetella
				last_date_l_CAV_2=request.POST.get('l_CAV_2')
				last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
				vaccination.last_date_CAV_2=last_date_l_CAV_2
				d_CAV_2=request.POST.get('d_CAV_2')
				d_CAV_2 = datenone(d_CAV_2)
				vaccination.due_date_CAV_2=d_CAV_2
				last_date_lymedisease=request.POST.get('l_lymedisease')
				last_date_lymedisease = datenone(last_date_lymedisease)
				vaccination.last_date_lyme=last_date_lymedisease
				d_lymedisease=request.POST.get('d_lymedisease')
				d_lymedisease = datenone(d_lymedisease)
				vaccination.due_date_lyme=d_lymedisease
				last_date_coronavirus=request.POST.get('l_coronavirus')
				last_date_coronavirus = datenone(last_date_coronavirus)
				vaccination.last_date_corona=last_date_coronavirus
				d_coronavirus=request.POST.get('d_coronavirus')
				d_coronavirus = datenone(d_coronavirus)
				vaccination.due_date_corona=d_coronavirus
				last_date_giardia=request.POST.get('l_giardia')
				last_date_giardia = datenone(last_date_giardia)
				vaccination.last_date_giardia=last_date_giardia
				d_giardia=request.POST.get('d_giardia')
				d_giardia = datenone(d_giardia)
				vaccination.due_date_giardia=d_giardia
				last_date_dhpp=request.POST.get('l_Can_L')
				last_date_dhpp = datenone(last_date_dhpp)
				vaccination.last_date_Can_L=last_date_dhpp
				d_dhpp=request.POST.get('d_Can_L')
				d_dhpp = datenone(d_dhpp)
				vaccination.due_date_Can_L=d_dhpp
				last_date_leptospirosis=request.POST.get('l_Leptospirosis')
				last_date_leptospirosis = datenone(last_date_leptospirosis)
				vaccination.last_date_leptospirosis=last_date_leptospirosis
				d_leptospirosis=request.POST.get('d_Leptospirosis')
				d_leptospirosis = datenone(d_leptospirosis)
				vaccination.due_date_leptospirosis=d_leptospirosis
				last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
				last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
				vaccination.last_date_9_in_1_vaccine=last_date_9_in_1_vaccine
				due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
				due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
				vaccination.due_date_9_in_1_vaccine=due_date_9_in_1_vaccine

				last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
				last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
				vaccination.last_date_10_in_1_vaccine=last_date_10_in_1_vaccine
				due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
				due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
				vaccination.due_date_10_in_1_vaccine=due_date_10_in_1_vaccine

				last_date_Feline_vaccine=request.POST.get('l_Feline')
				last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
				vaccination.last_date_Feline_vaccine=last_date_Feline_vaccine
				due_date_Feline_vaccine=request.POST.get('d_Feline')
				due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)
				vaccination.due_date_Feline_vaccine=due_date_Feline_vaccine
				vaccination.save()
				return redirect('diagnostic_prescription')
			except:
				if Vaccination.objects.filter(purpose_id=purpose_pet_obj_save).exists:
					vaccination_id=Vaccination.objects.get(purpose_id=purpose_pet_obj_save).id
					last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
					last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
					last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
					due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
					due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
					due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
					last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
					last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
					due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
					due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
					due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
					last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
					last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
					due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
					due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
					due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
					last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
					last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
					last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
					due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
					due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
					last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
					last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
					last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
					due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
					due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
					due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
					last_date_rabies = request.POST.get('l_rabies')
					last_date_rabies = datenone(last_date_rabies)
					last_date_rabies=last_date_rabies
					due_date_rabies=request.POST.get('d_rabies')
					due_date_rabies = datenone(due_date_rabies)
					due_date_rabies=due_date_rabies
					last_date_distemper=request.POST.get('l_distemper')
					last_date_distemper = datenone(last_date_distemper)
					last_date_distemper=last_date_distemper
					d_distemper=request.POST.get('d_distemper')
					d_distemper = datenone(d_distemper)
					due_date_distemper=d_distemper
					last_date_hepatitis=request.POST.get('l_hepatitis')
					last_date_hepatitis = datenone(last_date_hepatitis)
					last_date_CAV_1=last_date_hepatitis
					d_hepatitis=request.POST.get('d_hepatitis')
					d_hepatitis = datenone(d_hepatitis)
					due_date_CAV_1=d_hepatitis
					last_date_parovirus=request.POST.get('l_parovirus')
					last_date_parovirus = datenone(last_date_parovirus)
					last_date_parovirus=last_date_parovirus
					d_parovirus=request.POST.get('d_parovirus')
					d_parovirus = datenone(d_parovirus)
					due_date_parovirus=d_parovirus
					last_date_parainfluenza=request.POST.get('l_parainfluenza')
					last_date_parainfluenza = datenone(last_date_parainfluenza)
					last_date_parainfluenza=last_date_parainfluenza
					d_parainfluenza=request.POST.get('d_parainfluenza')
					d_parainfluenza = datenone(d_parainfluenza)
					due_date_parainfluenza=d_parainfluenza
					last_date_bordetella=request.POST.get('l_bordetella')
					last_date_bordetella = datenone(last_date_bordetella)
					last_date_bordetella=last_date_bordetella
					d_bordetella=request.POST.get('d_bordetella')
					d_bordetella = datenone(d_bordetella)
					due_date_bordetella=d_bordetella
					last_date_leptospirosis=request.POST.get('l_Leptospirosis')
					last_date_leptospirosis = datenone(last_date_leptospirosis)
					last_date_leptospirosis=last_date_leptospirosis
					d_leptospirosis=request.POST.get('d_Leptospirosis')
					d_leptospirosis = datenone(d_leptospirosis)
					due_date_leptospirosis=d_leptospirosis
					last_date_lymedisease=request.POST.get('l_lymedisease')
					last_date_lymedisease = datenone(last_date_lymedisease)
					last_date_lyme=last_date_lymedisease
					d_lymedisease=request.POST.get('d_lymedisease')
					d_lymedisease = datenone(d_lymedisease)
					due_date_lyme=d_lymedisease
					last_date_coronavirus=request.POST.get('l_coronavirus')
					last_date_coronavirus = datenone(last_date_coronavirus)
					last_date_corona=last_date_coronavirus
					d_coronavirus=request.POST.get('d_coronavirus')
					d_coronavirus = datenone(d_coronavirus)
					due_date_corona=d_coronavirus
					last_date_giardia=request.POST.get('l_giardia')
					last_date_giardia = datenone(last_date_giardia)
					last_date_giardia=last_date_giardia
					d_giardia=request.POST.get('d_giardia')
					d_giardia = datenone(d_giardia)
					due_date_giardia=d_giardia
					last_date_dhpp=request.POST.get('l_Can_L')
					last_date_dhpp = datenone(last_date_dhpp)
					last_date_Can_L=last_date_dhpp
					d_dhpp=request.POST.get('d_Can_L')
					d_dhpp = datenone(d_dhpp)
					due_date_Can_L=d_dhpp
					last_date_l_CAV_2=request.POST.get('l_CAV_2')
					last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
					last_date_CAV_2=last_date_l_CAV_2
					d_CAV_2=request.POST.get('d_CAV_2')
					d_CAV_2 = datenone(d_CAV_2)
					due_date_CAV_2=d_CAV_2

					last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
					last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
					due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
					due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
					last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
					last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
					due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
					due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
					last_date_Feline_vaccine=request.POST.get('l_Feline')
					last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
					due_date_Feline_vaccine=request.POST.get('d_Feline')
					due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)

					Vaccination.objects.filter(id=vaccination_id).update(last_date_CAV_2=last_date_l_CAV_2,
					due_date_CAV_2=due_date_CAV_2,last_date_bordetella=last_date_bordetella,
					due_date_bordetella=due_date_bordetella,
					last_date_lyme=last_date_lyme,due_date_lyme=due_date_lyme,
					last_date_leptospirosis=last_date_leptospirosis,
					due_date_leptospirosis=due_date_leptospirosis,
					last_date_corona=last_date_corona,due_date_corona=due_date_corona,
					last_date_giardia=last_date_giardia,due_date_giardia=due_date_giardia,
					last_date_Can_L=last_date_Can_L,due_date_Can_L=due_date_Can_L,
					last_date_3_in_1_DAPV=last_date_3_in_1_DAPV,
					due_date_3_in_1_DAPV=due_date_3_in_1_DAPV,
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP,
					due_date_4_in_1_DHPP=due_date_4_in_1_DHPP,
					last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC,
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC,
					last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2,
					due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2,
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP,
					due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP,
					last_date_rabies=last_date_rabies,due_date_rabies=due_date_rabies,
					last_date_distemper=last_date_distemper,due_date_distemper=due_date_distemper,
					last_date_CAV_1=last_date_CAV_1,due_date_CAV_1=due_date_CAV_1,
					last_date_parovirus=last_date_parovirus,due_date_parovirus=due_date_parovirus,
					last_date_parainfluenza=last_date_parainfluenza,
					due_date_parainfluenza=due_date_parainfluenza,last_date_9_in_1_vaccine=last_date_9_in_1_vaccine,due_date_9_in_1_vaccine=due_date_9_in_1_vaccine,
					last_date_10_in_1_vaccine=last_date_10_in_1_vaccine,
					due_date_10_in_1_vaccine=due_date_10_in_1_vaccine,last_date_Feline_vaccine=last_date_Feline_vaccine,due_date_Feline_vaccine=due_date_Feline_vaccine)
					return redirect('diagnostic_prescription')
		elif 'prescription_name' in request.POST:
			try:
				vaccination=Vaccination()
				vaccination.purpose_id = purpose_pet_obj_save
				vaccination.pet=pet_obj
				last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
				last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
				vaccination.last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
				due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
				due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
				vaccination.due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
				last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
				last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
				vaccination.last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
				due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
				due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
				vaccination.due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
				last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
				last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
				vaccination.last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
				due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
				due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
				vaccination.due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
				last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
				last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
				vaccination.last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
				due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
				due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
				vaccination.due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
				last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
				last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
				vaccination.last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
				due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
				due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
				vaccination.due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
				last_date_rabies = request.POST.get('l_rabies')
				last_date_rabies = datenone(last_date_rabies)
				vaccination.last_date_rabies=last_date_rabies
				due_date_rabies=request.POST.get('d_rabies')
				due_date_rabies = datenone(due_date_rabies)
				vaccination.due_date_rabies=due_date_rabies
				last_date_distemper=request.POST.get('l_distemper')
				last_date_distemper = datenone(last_date_distemper)
				vaccination.last_date_distemper=last_date_distemper
				d_distemper=request.POST.get('d_distemper')
				d_distemper = datenone(d_distemper)
				vaccination.due_date_distemper=d_distemper
				last_date_hepatitis=request.POST.get('l_hepatitis')
				last_date_hepatitis = datenone(last_date_hepatitis)
				vaccination.last_date_CAV_1=last_date_hepatitis
				d_hepatitis=request.POST.get('d_hepatitis')
				d_hepatitis = datenone(d_hepatitis)
				vaccination.due_date_CAV_1=d_hepatitis
				last_date_parovirus=request.POST.get('l_parovirus')
				last_date_parovirus = datenone(last_date_parovirus)
				vaccination.last_date_parovirus=last_date_parovirus
				d_parovirus=request.POST.get('d_parovirus')
				d_parovirus = datenone(d_parovirus)
				vaccination.due_date_parovirus=d_parovirus
				last_date_parainfluenza=request.POST.get('l_parainfluenza')
				last_date_parainfluenza = datenone(last_date_parainfluenza)
				vaccination.last_date_parainfluenza=last_date_parainfluenza
				d_parainfluenza=request.POST.get('d_parainfluenza')
				d_parainfluenza = datenone(d_parainfluenza)
				vaccination.due_date_parainfluenza=d_parainfluenza
				last_date_bordetella=request.POST.get('l_bordetella')
				last_date_bordetella = datenone(last_date_bordetella)
				vaccination.last_date_bordetella=last_date_bordetella
				d_bordetella=request.POST.get('d_bordetella')
				d_bordetella = datenone(d_bordetella)
				vaccination.due_date_bordetella=d_bordetella
				last_date_l_CAV_2=request.POST.get('l_CAV_2')
				last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
				vaccination.last_date_CAV_2=last_date_l_CAV_2
				d_CAV_2=request.POST.get('d_CAV_2')
				d_CAV_2 = datenone(d_CAV_2)
				vaccination.due_date_CAV_2=d_CAV_2
				last_date_lymedisease=request.POST.get('l_lymedisease')
				last_date_lymedisease = datenone(last_date_lymedisease)
				vaccination.last_date_lyme=last_date_lymedisease
				d_lymedisease=request.POST.get('d_lymedisease')
				d_lymedisease = datenone(d_lymedisease)
				vaccination.due_date_lyme=d_lymedisease
				last_date_coronavirus=request.POST.get('l_coronavirus')
				last_date_coronavirus = datenone(last_date_coronavirus)
				vaccination.last_date_corona=last_date_coronavirus
				d_coronavirus=request.POST.get('d_coronavirus')
				d_coronavirus = datenone(d_coronavirus)
				vaccination.due_date_corona=d_coronavirus
				last_date_giardia=request.POST.get('l_giardia')
				last_date_giardia = datenone(last_date_giardia)
				vaccination.last_date_giardia=last_date_giardia
				d_giardia=request.POST.get('d_giardia')
				d_giardia = datenone(d_giardia)
				vaccination.due_date_giardia=d_giardia
				last_date_dhpp=request.POST.get('l_Can_L')
				last_date_dhpp = datenone(last_date_dhpp)
				vaccination.last_date_Can_L=last_date_dhpp
				d_dhpp=request.POST.get('d_Can_L')
				d_dhpp = datenone(d_dhpp)
				vaccination.due_date_Can_L=d_dhpp
				last_date_leptospirosis=request.POST.get('l_Leptospirosis')
				last_date_leptospirosis = datenone(last_date_leptospirosis)
				vaccination.last_date_leptospirosis=last_date_leptospirosis
				d_leptospirosis=request.POST.get('d_Leptospirosis')
				d_leptospirosis = datenone(d_leptospirosis)
				vaccination.due_date_leptospirosis=d_leptospirosis

				last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
				last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
				vaccination.last_date_9_in_1_vaccine=last_date_9_in_1_vaccine
				due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
				due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
				vaccination.due_date_9_in_1_vaccine=due_date_9_in_1_vaccine

				last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
				last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
				vaccination.last_date_10_in_1_vaccine=last_date_10_in_1_vaccine
				due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
				due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
				vaccination.due_date_10_in_1_vaccine=due_date_10_in_1_vaccine

				last_date_Feline_vaccine=request.POST.get('l_Feline')
				last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
				vaccination.last_date_Feline_vaccine=last_date_Feline_vaccine
				due_date_Feline_vaccine=request.POST.get('d_Feline')
				due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)
				vaccination.due_date_Feline_vaccine=due_date_Feline_vaccine
				vaccination.save()
				return redirect('prescription')
			except:
				if Vaccination.objects.filter(purpose_id=purpose_pet_obj_save).exists:
					vaccination_id=Vaccination.objects.get(purpose_id=purpose_pet_obj_save).id
					last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
					last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
					last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
					due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
					due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
					due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
					last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
					last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
					due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
					due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
					due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
					last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
					last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
					due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
					due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
					due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
					last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
					last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
					last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
					due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
					due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
					last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
					last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
					last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
					due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
					due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
					due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
					last_date_rabies = request.POST.get('l_rabies')
					last_date_rabies = datenone(last_date_rabies)
					last_date_rabies=last_date_rabies
					due_date_rabies=request.POST.get('d_rabies')
					due_date_rabies = datenone(due_date_rabies)
					due_date_rabies=due_date_rabies
					last_date_distemper=request.POST.get('l_distemper')
					last_date_distemper = datenone(last_date_distemper)
					last_date_distemper=last_date_distemper
					d_distemper=request.POST.get('d_distemper')
					d_distemper = datenone(d_distemper)
					due_date_distemper=d_distemper
					last_date_hepatitis=request.POST.get('l_hepatitis')
					last_date_hepatitis = datenone(last_date_hepatitis)
					last_date_CAV_1=last_date_hepatitis
					d_hepatitis=request.POST.get('d_hepatitis')
					d_hepatitis = datenone(d_hepatitis)
					due_date_CAV_1=d_hepatitis
					last_date_parovirus=request.POST.get('l_parovirus')
					last_date_parovirus = datenone(last_date_parovirus)
					last_date_parovirus=last_date_parovirus
					d_parovirus=request.POST.get('d_parovirus')
					d_parovirus = datenone(d_parovirus)
					due_date_parovirus=d_parovirus
					last_date_parainfluenza=request.POST.get('l_parainfluenza')
					last_date_parainfluenza = datenone(last_date_parainfluenza)
					last_date_parainfluenza=last_date_parainfluenza
					d_parainfluenza=request.POST.get('d_parainfluenza')
					d_parainfluenza = datenone(d_parainfluenza)
					due_date_parainfluenza=d_parainfluenza
					last_date_bordetella=request.POST.get('l_bordetella')
					last_date_bordetella = datenone(last_date_bordetella)
					last_date_bordetella=last_date_bordetella
					d_bordetella=request.POST.get('d_bordetella')
					d_bordetella = datenone(d_bordetella)
					due_date_bordetella=d_bordetella
					last_date_leptospirosis=request.POST.get('l_Leptospirosis')
					last_date_leptospirosis = datenone(last_date_leptospirosis)
					last_date_leptospirosis=last_date_leptospirosis
					d_leptospirosis=request.POST.get('d_Leptospirosis')
					d_leptospirosis = datenone(d_leptospirosis)
					due_date_leptospirosis=d_leptospirosis
					last_date_lymedisease=request.POST.get('l_lymedisease')
					last_date_lymedisease = datenone(last_date_lymedisease)
					last_date_lyme=last_date_lymedisease
					d_lymedisease=request.POST.get('d_lymedisease')
					d_lymedisease = datenone(d_lymedisease)
					due_date_lyme=d_lymedisease
					last_date_coronavirus=request.POST.get('l_coronavirus')
					last_date_coronavirus = datenone(last_date_coronavirus)
					last_date_corona=last_date_coronavirus
					d_coronavirus=request.POST.get('d_coronavirus')
					d_coronavirus = datenone(d_coronavirus)
					due_date_corona=d_coronavirus
					last_date_giardia=request.POST.get('l_giardia')
					last_date_giardia = datenone(last_date_giardia)
					last_date_giardia=last_date_giardia
					d_giardia=request.POST.get('d_giardia')
					d_giardia = datenone(d_giardia)
					due_date_giardia=d_giardia
					last_date_dhpp=request.POST.get('l_Can_L')
					last_date_dhpp = datenone(last_date_dhpp)
					last_date_Can_L=last_date_dhpp
					d_dhpp=request.POST.get('d_Can_L')
					d_dhpp = datenone(d_dhpp)
					due_date_Can_L=d_dhpp
					last_date_l_CAV_2=request.POST.get('l_CAV_2')
					last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
					last_date_CAV_2=last_date_l_CAV_2
					d_CAV_2=request.POST.get('d_CAV_2')
					d_CAV_2 = datenone(d_CAV_2)
					due_date_CAV_2=d_CAV_2

					last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
					last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
					due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
					due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
					last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
					last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
					due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
					due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
					last_date_Feline_vaccine=request.POST.get('l_Feline')
					last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
					due_date_Feline_vaccine=request.POST.get('d_Feline')
					due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)

					Vaccination.objects.filter(id=vaccination_id).update(last_date_bordetella=last_date_bordetella,due_date_bordetella=due_date_bordetella,
					last_date_lyme=last_date_lyme,due_date_lyme=due_date_lyme,last_date_leptospirosis=last_date_leptospirosis,due_date_leptospirosis=due_date_leptospirosis,last_date_CAV_2=last_date_l_CAV_2,due_date_CAV_2=due_date_CAV_2,
					last_date_corona=last_date_corona,due_date_corona=due_date_corona,last_date_giardia=last_date_giardia,due_date_giardia=due_date_giardia,
					last_date_Can_L=last_date_Can_L,due_date_Can_L=due_date_Can_L,last_date_3_in_1_DAPV=last_date_3_in_1_DAPV,due_date_3_in_1_DAPV=due_date_3_in_1_DAPV,
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP,due_date_4_in_1_DHPP=due_date_4_in_1_DHPP,last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC,
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC,last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2,due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2,
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP,due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP,last_date_rabies=last_date_rabies,due_date_rabies=due_date_rabies,
					last_date_distemper=last_date_distemper,due_date_distemper=due_date_distemper,last_date_CAV_1=last_date_CAV_1,due_date_CAV_1=due_date_CAV_1,
					last_date_parovirus=last_date_parovirus,due_date_parovirus=due_date_parovirus,last_date_parainfluenza=last_date_parainfluenza,due_date_parainfluenza=due_date_parainfluenza,
					last_date_9_in_1_vaccine=last_date_9_in_1_vaccine,due_date_9_in_1_vaccine=due_date_9_in_1_vaccine,last_date_10_in_1_vaccine=last_date_10_in_1_vaccine,
					due_date_10_in_1_vaccine=due_date_10_in_1_vaccine,last_date_Feline_vaccine=last_date_Feline_vaccine,due_date_Feline_vaccine=due_date_Feline_vaccine)
					return redirect('prescription')
		elif 'deworming_name' in request.POST:
			try:
				vaccination=Vaccination()
				vaccination.purpose_id = purpose_pet_obj_save
				vaccination.pet=pet_obj
				last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
				last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
				vaccination.last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
				due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
				due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
				vaccination.due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
				last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
				last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
				vaccination.last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
				due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
				due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
				vaccination.due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
				last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
				last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
				vaccination.last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
				due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
				due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
				vaccination.due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
				last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
				last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
				vaccination.last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
				due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
				due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
				vaccination.due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
				last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
				last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
				vaccination.last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
				due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
				due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
				vaccination.due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
				last_date_rabies = request.POST.get('l_rabies')
				last_date_rabies = datenone(last_date_rabies)
				vaccination.last_date_rabies=last_date_rabies
				due_date_rabies=request.POST.get('d_rabies')
				due_date_rabies = datenone(due_date_rabies)
				vaccination.due_date_rabies=due_date_rabies
				last_date_distemper=request.POST.get('l_distemper')
				last_date_distemper = datenone(last_date_distemper)
				vaccination.last_date_distemper=last_date_distemper
				d_distemper=request.POST.get('d_distemper')
				d_distemper = datenone(d_distemper)
				vaccination.due_date_distemper=d_distemper
				last_date_hepatitis=request.POST.get('l_hepatitis')
				last_date_hepatitis = datenone(last_date_hepatitis)
				vaccination.last_date_CAV_1=last_date_hepatitis
				d_hepatitis=request.POST.get('d_hepatitis')
				d_hepatitis = datenone(d_hepatitis)
				vaccination.due_date_CAV_1=d_hepatitis
				last_date_parovirus=request.POST.get('l_parovirus')
				last_date_parovirus = datenone(last_date_parovirus)
				vaccination.last_date_parovirus=last_date_parovirus
				d_parovirus=request.POST.get('d_parovirus')
				d_parovirus = datenone(d_parovirus)
				vaccination.due_date_parovirus=d_parovirus
				last_date_parainfluenza=request.POST.get('l_parainfluenza')
				last_date_parainfluenza = datenone(last_date_parainfluenza)
				vaccination.last_date_parainfluenza=last_date_parainfluenza
				d_parainfluenza=request.POST.get('d_parainfluenza')
				d_parainfluenza = datenone(d_parainfluenza)
				vaccination.due_date_parainfluenza=d_parainfluenza
				last_date_bordetella=request.POST.get('l_bordetella')
				last_date_bordetella = datenone(last_date_bordetella)
				vaccination.last_date_bordetella=last_date_bordetella
				d_bordetella=request.POST.get('d_bordetella')
				d_bordetella = datenone(d_bordetella)
				vaccination.due_date_bordetella=d_bordetella
				last_date_l_CAV_2=request.POST.get('l_CAV_2')
				last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
				vaccination.last_date_CAV_2=last_date_l_CAV_2
				d_CAV_2=request.POST.get('d_CAV_2')
				d_CAV_2 = datenone(d_CAV_2)
				vaccination.due_date_CAV_2=d_CAV_2
				last_date_lymedisease=request.POST.get('l_lymedisease')
				last_date_lymedisease = datenone(last_date_lymedisease)
				vaccination.last_date_lyme=last_date_lymedisease
				d_lymedisease=request.POST.get('d_lymedisease')
				d_lymedisease = datenone(d_lymedisease)
				vaccination.due_date_lyme=d_lymedisease
				last_date_coronavirus=request.POST.get('l_coronavirus')
				last_date_coronavirus = datenone(last_date_coronavirus)
				vaccination.last_date_corona=last_date_coronavirus
				d_coronavirus=request.POST.get('d_coronavirus')
				d_coronavirus = datenone(d_coronavirus)
				vaccination.due_date_corona=d_coronavirus
				last_date_giardia=request.POST.get('l_giardia')
				last_date_giardia = datenone(last_date_giardia)
				vaccination.last_date_giardia=last_date_giardia
				d_giardia=request.POST.get('d_giardia')
				d_giardia = datenone(d_giardia)
				vaccination.due_date_giardia=d_giardia
				last_date_dhpp=request.POST.get('l_Can_L')
				last_date_dhpp = datenone(last_date_dhpp)
				vaccination.last_date_Can_L=last_date_dhpp
				d_dhpp=request.POST.get('d_Can_L')
				d_dhpp = datenone(d_dhpp)
				vaccination.due_date_Can_L=d_dhpp
				last_date_leptospirosis=request.POST.get('l_Leptospirosis')
				last_date_leptospirosis = datenone(last_date_leptospirosis)
				vaccination.last_date_leptospirosis=last_date_leptospirosis
				d_leptospirosis=request.POST.get('d_Leptospirosis')
				d_leptospirosis = datenone(d_leptospirosis)
				vaccination.due_date_leptospirosis=d_leptospirosis

				last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
				last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
				vaccination.last_date_9_in_1_vaccine=last_date_9_in_1_vaccine
				due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
				due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
				vaccination.due_date_9_in_1_vaccine=due_date_9_in_1_vaccine

				last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
				last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
				vaccination.last_date_10_in_1_vaccine=last_date_10_in_1_vaccine
				due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
				due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
				vaccination.due_date_10_in_1_vaccine=due_date_10_in_1_vaccine

				last_date_Feline_vaccine=request.POST.get('l_Feline')
				last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
				vaccination.last_date_Feline_vaccine=last_date_Feline_vaccine
				due_date_Feline_vaccine=request.POST.get('d_Feline')
				due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)
				vaccination.due_date_Feline_vaccine=due_date_Feline_vaccine
				vaccination.save()
				return redirect('deworming')
			except:
				if Vaccination.objects.filter(purpose_id=purpose_pet_obj_save).exists:
					vaccination_id=Vaccination.objects.get(purpose_id=purpose_pet_obj_save).id
					last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
					last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
					last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
					due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
					due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
					due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
					last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
					last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
					due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
					due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
					due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
					last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
					last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
					due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
					due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
					due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
					last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
					last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
					last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
					due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
					due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
					last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
					last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
					last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
					due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
					due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
					due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
					last_date_rabies = request.POST.get('l_rabies')
					last_date_rabies = datenone(last_date_rabies)
					last_date_rabies=last_date_rabies
					due_date_rabies=request.POST.get('d_rabies')
					due_date_rabies = datenone(due_date_rabies)
					due_date_rabies=due_date_rabies
					last_date_distemper=request.POST.get('l_distemper')
					last_date_distemper = datenone(last_date_distemper)
					last_date_distemper=last_date_distemper
					d_distemper=request.POST.get('d_distemper')
					d_distemper = datenone(d_distemper)
					due_date_distemper=d_distemper
					last_date_hepatitis=request.POST.get('l_hepatitis')
					last_date_hepatitis = datenone(last_date_hepatitis)
					last_date_CAV_1=last_date_hepatitis
					d_hepatitis=request.POST.get('d_hepatitis')
					d_hepatitis = datenone(d_hepatitis)
					due_date_CAV_1=d_hepatitis
					last_date_parovirus=request.POST.get('l_parovirus')
					last_date_parovirus = datenone(last_date_parovirus)
					last_date_parovirus=last_date_parovirus
					d_parovirus=request.POST.get('d_parovirus')
					d_parovirus = datenone(d_parovirus)
					due_date_parovirus=d_parovirus
					last_date_parainfluenza=request.POST.get('l_parainfluenza')
					last_date_parainfluenza = datenone(last_date_parainfluenza)
					last_date_parainfluenza=last_date_parainfluenza
					d_parainfluenza=request.POST.get('d_parainfluenza')
					d_parainfluenza = datenone(d_parainfluenza)
					due_date_parainfluenza=d_parainfluenza
					last_date_bordetella=request.POST.get('l_bordetella')
					last_date_bordetella = datenone(last_date_bordetella)
					last_date_bordetella=last_date_bordetella
					d_bordetella=request.POST.get('d_bordetella')
					d_bordetella = datenone(d_bordetella)
					due_date_bordetella=d_bordetella
					last_date_leptospirosis=request.POST.get('l_Leptospirosis')
					last_date_leptospirosis = datenone(last_date_leptospirosis)
					last_date_leptospirosis=last_date_leptospirosis
					d_leptospirosis=request.POST.get('d_Leptospirosis')
					d_leptospirosis = datenone(d_leptospirosis)
					due_date_leptospirosis=d_leptospirosis
					last_date_lymedisease=request.POST.get('l_lymedisease')
					last_date_lymedisease = datenone(last_date_lymedisease)
					last_date_lyme=last_date_lymedisease
					d_lymedisease=request.POST.get('d_lymedisease')
					d_lymedisease = datenone(d_lymedisease)
					due_date_lyme=d_lymedisease
					last_date_coronavirus=request.POST.get('l_coronavirus')
					last_date_coronavirus = datenone(last_date_coronavirus)
					last_date_corona=last_date_coronavirus
					d_coronavirus=request.POST.get('d_coronavirus')
					d_coronavirus = datenone(d_coronavirus)
					due_date_corona=d_coronavirus
					last_date_giardia=request.POST.get('l_giardia')
					last_date_giardia = datenone(last_date_giardia)
					last_date_giardia=last_date_giardia
					d_giardia=request.POST.get('d_giardia')
					d_giardia = datenone(d_giardia)
					due_date_giardia=d_giardia
					last_date_dhpp=request.POST.get('l_Can_L')
					last_date_dhpp = datenone(last_date_dhpp)
					last_date_Can_L=last_date_dhpp
					d_dhpp=request.POST.get('d_Can_L')
					d_dhpp = datenone(d_dhpp)
					due_date_Can_L=d_dhpp
					last_date_l_CAV_2=request.POST.get('l_CAV_2')
					last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
					last_date_CAV_2=last_date_l_CAV_2
					d_CAV_2=request.POST.get('d_CAV_2')
					d_CAV_2 = datenone(d_CAV_2)
					due_date_CAV_2=d_CAV_2

					last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
					last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
					due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
					due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
					last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
					last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
					due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
					due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
					last_date_Feline_vaccine=request.POST.get('l_Feline')
					last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
					due_date_Feline_vaccine=request.POST.get('d_Feline')
					due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)

					Vaccination.objects.filter(id=vaccination_id).update(last_date_CAV_2=last_date_l_CAV_2,due_date_CAV_2=due_date_CAV_2,
					last_date_corona=last_date_corona,due_date_corona=due_date_corona,last_date_giardia=last_date_giardia,due_date_giardia=due_date_giardia,
					last_date_Can_L=last_date_Can_L,due_date_Can_L=due_date_Can_L,last_date_3_in_1_DAPV=last_date_3_in_1_DAPV,due_date_3_in_1_DAPV=due_date_3_in_1_DAPV,
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP,due_date_4_in_1_DHPP=due_date_4_in_1_DHPP,last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC,
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC,last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2,due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2,
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP,due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP,last_date_rabies=last_date_rabies,due_date_rabies=due_date_rabies,
					last_date_distemper=last_date_distemper,due_date_distemper=due_date_distemper,last_date_CAV_1=last_date_CAV_1,due_date_CAV_1=due_date_CAV_1,
					last_date_parovirus=last_date_parovirus,due_date_parovirus=due_date_parovirus,last_date_parainfluenza=last_date_parainfluenza,due_date_parainfluenza=due_date_parainfluenza,
					last_date_9_in_1_vaccine=last_date_9_in_1_vaccine,due_date_9_in_1_vaccine=due_date_9_in_1_vaccine,last_date_10_in_1_vaccine=last_date_10_in_1_vaccine,
					due_date_10_in_1_vaccine=due_date_10_in_1_vaccine,last_date_Feline_vaccine=last_date_Feline_vaccine,due_date_Feline_vaccine=due_date_Feline_vaccine)
					return redirect('deworming')
		elif 'close_visit' in request.POST:
			try:
				vaccination=Vaccination()
				vaccination.purpose_id = purpose_pet_obj_save
				vaccination.pet=pet_obj
				last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
				last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
				vaccination.last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
				due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
				due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
				vaccination.due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
				last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
				last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
				vaccination.last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
				due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
				due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
				vaccination.due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
				last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
				last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
				vaccination.last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
				due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
				due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
				vaccination.due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
				last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
				last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
				vaccination.last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
				due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
				due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
				vaccination.due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
				last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
				last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
				vaccination.last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
				due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
				due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
				vaccination.due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
				last_date_rabies = request.POST.get('l_rabies')
				last_date_rabies = datenone(last_date_rabies)
				vaccination.last_date_rabies=last_date_rabies
				due_date_rabies=request.POST.get('d_rabies')
				due_date_rabies = datenone(due_date_rabies)
				vaccination.due_date_rabies=due_date_rabies
				last_date_distemper=request.POST.get('l_distemper')
				last_date_distemper = datenone(last_date_distemper)
				vaccination.last_date_distemper=last_date_distemper
				d_distemper=request.POST.get('d_distemper')
				d_distemper = datenone(d_distemper)
				vaccination.due_date_distemper=d_distemper
				last_date_hepatitis=request.POST.get('l_hepatitis')
				last_date_hepatitis = datenone(last_date_hepatitis)
				vaccination.last_date_CAV_1=last_date_hepatitis
				d_hepatitis=request.POST.get('d_hepatitis')
				d_hepatitis = datenone(d_hepatitis)
				vaccination.due_date_CAV_1=d_hepatitis
				last_date_parovirus=request.POST.get('l_parovirus')
				last_date_parovirus = datenone(last_date_parovirus)
				vaccination.last_date_parovirus=last_date_parovirus
				d_parovirus=request.POST.get('d_parovirus')
				d_parovirus = datenone(d_parovirus)
				vaccination.due_date_parovirus=d_parovirus
				last_date_parainfluenza=request.POST.get('l_parainfluenza')
				last_date_parainfluenza = datenone(last_date_parainfluenza)
				vaccination.last_date_parainfluenza=last_date_parainfluenza
				d_parainfluenza=request.POST.get('d_parainfluenza')
				d_parainfluenza = datenone(d_parainfluenza)
				vaccination.due_date_parainfluenza=d_parainfluenza
				last_date_bordetella=request.POST.get('l_bordetella')
				last_date_bordetella = datenone(last_date_bordetella)
				vaccination.last_date_bordetella=last_date_bordetella
				d_bordetella=request.POST.get('d_bordetella')
				d_bordetella = datenone(d_bordetella)
				vaccination.due_date_bordetella=d_bordetella
				last_date_l_CAV_2=request.POST.get('l_CAV_2')
				last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
				vaccination.last_date_CAV_2=last_date_l_CAV_2
				d_CAV_2=request.POST.get('d_CAV_2')
				d_CAV_2 = datenone(d_CAV_2)
				vaccination.due_date_CAV_2=d_CAV_2
				last_date_lymedisease=request.POST.get('l_lymedisease')
				last_date_lymedisease = datenone(last_date_lymedisease)
				vaccination.last_date_lyme=last_date_lymedisease
				d_lymedisease=request.POST.get('d_lymedisease')
				d_lymedisease = datenone(d_lymedisease)
				vaccination.due_date_lyme=d_lymedisease
				last_date_coronavirus=request.POST.get('l_coronavirus')
				last_date_coronavirus = datenone(last_date_coronavirus)
				vaccination.last_date_corona=last_date_coronavirus
				d_coronavirus=request.POST.get('d_coronavirus')
				d_coronavirus = datenone(d_coronavirus)
				vaccination.due_date_corona=d_coronavirus
				last_date_giardia=request.POST.get('l_giardia')
				last_date_giardia = datenone(last_date_giardia)
				vaccination.last_date_giardia=last_date_giardia
				d_giardia=request.POST.get('d_giardia')
				d_giardia = datenone(d_giardia)
				vaccination.due_date_giardia=d_giardia
				last_date_dhpp=request.POST.get('l_Can_L')
				last_date_dhpp = datenone(last_date_dhpp)
				vaccination.last_date_Can_L=last_date_dhpp
				d_dhpp=request.POST.get('d_Can_L')
				d_dhpp = datenone(d_dhpp)
				vaccination.due_date_Can_L=d_dhpp
				last_date_leptospirosis=request.POST.get('l_Leptospirosis')
				last_date_leptospirosis = datenone(last_date_leptospirosis)
				vaccination.last_date_leptospirosis=last_date_leptospirosis
				d_leptospirosis=request.POST.get('d_Leptospirosis')
				d_leptospirosis = datenone(d_leptospirosis)
				vaccination.due_date_leptospirosis=d_leptospirosis

				last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
				last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
				vaccination.last_date_9_in_1_vaccine=last_date_9_in_1_vaccine
				due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
				due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
				vaccination.due_date_9_in_1_vaccine=due_date_9_in_1_vaccine

				last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
				last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
				vaccination.last_date_10_in_1_vaccine=last_date_10_in_1_vaccine
				due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
				due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
				vaccination.due_date_10_in_1_vaccine=due_date_10_in_1_vaccine

				last_date_Feline_vaccine=request.POST.get('l_Feline')
				last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
				vaccination.last_date_Feline_vaccine=last_date_Feline_vaccine
				due_date_Feline_vaccine=request.POST.get('d_Feline')
				due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)
				vaccination.due_date_Feline_vaccine=due_date_Feline_vaccine
				vaccination.save()
				if Doctor.objects.get(id=doc_pk).stock_management=='yes':
					if Prescription.objects.filter(purpose_id=purpose_id).exists():
						medicine1_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_name
						medicine1_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_quantity
						medicine2_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_name
						medicine2_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_quantity
						medicine3_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_name
						medicine3_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_quantity
						medicine4_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_name
						medicine4_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_quantity
						medicine5_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_name
						medicine5_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_quantity
						medicine6_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_name
						medicine6_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_quantity
						if stock.objects.filter(doctor__id=doc_id,medicine=medicine1_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_id,medicine=medicine1_name).last().quantity
							present_quantity=medicine1_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_id,medicine=medicine1_name).update(quantity=reduced_quantity)

						if stock.objects.filter(doctor__id=doc_id,medicine=medicine2_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_id,medicine=medicine2_name).last().quantity
							present_quantity=medicine2_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							print(reduced_quantity)
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_id,medicine=medicine2_name).update(quantity=reduced_quantity)

						if stock.objects.filter(doctor__id=doc_id,medicine=medicine3_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_id,medicine=medicine3_name).last().quantity
							present_quantity=medicine3_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_id,medicine=medicine3_name).update(quantity=reduced_quantity)

						if stock.objects.filter(doctor__id=doc_id,medicine=medicine4_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_id,medicine=medicine4_name).last().quantity
							present_quantity=medicine4_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_id,medicine=medicine4_name).update(quantity=reduced_quantity)

						if stock.objects.filter(doctor__id=doc_id,medicine=medicine5_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_id,medicine=medicine5_name).last().quantity
							present_quantity=medicine5_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_id,medicine=medicine5_name).update(quantity=reduced_quantity)

						if stock.objects.filter(doctor__id=doc_id,medicine=medicine6_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_id,medicine=medicine6_name).last().quantity
							present_quantity=medicine6_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_id,medicine=medicine6_name).update(quantity=reduced_quantity)
					else:
						pass
				return redirect('summary')
			except:
				if Vaccination.objects.filter(purpose_id=purpose_pet_obj_save).exists:
					vaccination_id=Vaccination.objects.get(purpose_id=purpose_pet_obj_save).id
					last_date_3_in_1_DAPV=request.POST.get('l_3_DAPV')
					last_date_3_in_1_DAPV=datenone(last_date_3_in_1_DAPV)
					last_date_3_in_1_DAPV=last_date_3_in_1_DAPV
					due_date_3_in_1_DAPV=request.POST.get('d_3_DAPV')
					due_date_3_in_1_DAPV=datenone(due_date_3_in_1_DAPV)
					due_date_3_in_1_DAPV=due_date_3_in_1_DAPV
					last_date_4_in_1_DHPP=request.POST.get('l_4_DHPP')
					last_date_4_in_1_DHPP=datenone(last_date_4_in_1_DHPP)
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP
					due_date_4_in_1_DHPP=request.POST.get('d_4_DHPP')
					due_date_4_in_1_DHPP=datenone(due_date_4_in_1_DHPP)
					due_date_4_in_1_DHPP=due_date_4_in_1_DHPP
					last_date_5_in_1_DA2PP=request.POST.get('l_5_DA2PP')
					last_date_5_in_1_DA2PP=datenone(last_date_5_in_1_DA2PP)
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP
					due_date_5_in_1_DA2PP=request.POST.get('d_5_DA2PP')
					due_date_5_in_1_DA2PP=datenone(due_date_5_in_1_DA2PP)
					due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP
					last_date_6_in_1_DA2PPC=request.POST.get('l_6_DA2PPC')
					last_date_6_in_1_DA2PPC=datenone(last_date_6_in_1_DA2PPC)
					last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC
					due_date_6_in_1_DA2PPC=request.POST.get('d_6_DA2PPC')
					due_date_6_in_1_DA2PPC=datenone(due_date_6_in_1_DA2PPC)
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC
					last_date_7_in_1_DA2PPVL2=request.POST.get('l_7_DA2PPVL2')
					last_date_7_in_1_DA2PPVL2=datenone(last_date_7_in_1_DA2PPVL2)
					last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
					due_date_7_in_1_DA2PPVL2=request.POST.get('d_7_DA2PPVL2')
					due_date_7_in_1_DA2PPVL2=datenone(due_date_7_in_1_DA2PPVL2)
					due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2
					last_date_rabies = request.POST.get('l_rabies')
					last_date_rabies = datenone(last_date_rabies)
					last_date_rabies=last_date_rabies
					due_date_rabies=request.POST.get('d_rabies')
					due_date_rabies = datenone(due_date_rabies)
					due_date_rabies=due_date_rabies
					last_date_distemper=request.POST.get('l_distemper')
					last_date_distemper = datenone(last_date_distemper)
					last_date_distemper=last_date_distemper
					d_distemper=request.POST.get('d_distemper')
					d_distemper = datenone(d_distemper)
					due_date_distemper=d_distemper
					last_date_hepatitis=request.POST.get('l_hepatitis')
					last_date_hepatitis = datenone(last_date_hepatitis)
					last_date_CAV_1=last_date_hepatitis
					d_hepatitis=request.POST.get('d_hepatitis')
					d_hepatitis = datenone(d_hepatitis)
					due_date_CAV_1=d_hepatitis
					last_date_parovirus=request.POST.get('l_parovirus')
					last_date_parovirus = datenone(last_date_parovirus)
					last_date_parovirus=last_date_parovirus
					d_parovirus=request.POST.get('d_parovirus')
					d_parovirus = datenone(d_parovirus)
					due_date_parovirus=d_parovirus
					last_date_parainfluenza=request.POST.get('l_parainfluenza')
					last_date_parainfluenza = datenone(last_date_parainfluenza)
					last_date_parainfluenza=last_date_parainfluenza
					d_parainfluenza=request.POST.get('d_parainfluenza')
					d_parainfluenza = datenone(d_parainfluenza)
					due_date_parainfluenza=d_parainfluenza
					last_date_bordetella=request.POST.get('l_bordetella')
					last_date_bordetella = datenone(last_date_bordetella)
					last_date_bordetella=last_date_bordetella
					d_bordetella=request.POST.get('d_bordetella')
					d_bordetella = datenone(d_bordetella)
					due_date_bordetella=d_bordetella
					last_date_leptospirosis=request.POST.get('l_leptospirosis')
					last_date_leptospirosis = datenone(last_date_leptospirosis)
					last_date_leptospirosis=last_date_leptospirosis
					d_leptospirosis=request.POST.get('d_leptospirosis')
					d_leptospirosis = datenone(d_leptospirosis)
					due_date_leptospirosis=d_leptospirosis
					last_date_lymedisease=request.POST.get('l_lymedisease')
					last_date_lymedisease = datenone(last_date_lymedisease)
					last_date_lyme=last_date_lymedisease
					d_lymedisease=request.POST.get('d_lymedisease')
					d_lymedisease = datenone(d_lymedisease)
					due_date_lyme=d_lymedisease
					last_date_coronavirus=request.POST.get('l_coronavirus')
					last_date_coronavirus = datenone(last_date_coronavirus)
					last_date_corona=last_date_coronavirus
					d_coronavirus=request.POST.get('d_coronavirus')
					d_coronavirus = datenone(d_coronavirus)
					due_date_corona=d_coronavirus
					last_date_giardia=request.POST.get('l_giardia')
					last_date_giardia = datenone(last_date_giardia)
					last_date_giardia=last_date_giardia
					d_giardia=request.POST.get('d_giardia')
					d_giardia = datenone(d_giardia)
					due_date_giardia=d_giardia
					last_date_dhpp=request.POST.get('l_Can_L')
					last_date_dhpp = datenone(last_date_dhpp)
					last_date_Can_L=last_date_dhpp
					d_dhpp=request.POST.get('d_Can_L')
					d_dhpp = datenone(d_dhpp)
					due_date_Can_L=d_dhpp
					last_date_l_CAV_2=request.POST.get('l_CAV_2')
					last_date_l_CAV_2 = datenone(last_date_l_CAV_2)
					last_date_CAV_2=last_date_l_CAV_2
					d_CAV_2=request.POST.get('d_CAV_2')
					d_CAV_2 = datenone(d_CAV_2)
					due_date_CAV_2=d_CAV_2

					last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
					last_date_9_in_1_vaccine = datenone(last_date_9_in_1_vaccine)
					due_date_9_in_1_vaccine=request.POST.get('d_9_in_1')
					due_date_9_in_1_vaccine = datenone(due_date_9_in_1_vaccine)
					last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
					last_date_10_in_1_vaccine = datenone(last_date_10_in_1_vaccine)
					due_date_10_in_1_vaccine=request.POST.get('d_10_in_1')
					due_date_10_in_1_vaccine = datenone(due_date_10_in_1_vaccine)
					last_date_Feline_vaccine=request.POST.get('l_Feline')
					last_date_Feline_vaccine = datenone(last_date_Feline_vaccine)
					due_date_Feline_vaccine=request.POST.get('d_Feline')
					due_date_Feline_vaccine = datenone(due_date_Feline_vaccine)

					Vaccination.objects.filter(id=vaccination_id).update(last_date_CAV_2=last_date_l_CAV_2,due_date_CAV_2=due_date_CAV_2,
					last_date_corona=last_date_corona,due_date_corona=due_date_corona,last_date_giardia=last_date_giardia,due_date_giardia=due_date_giardia,
					last_date_Can_L=last_date_Can_L,due_date_Can_L=due_date_Can_L,last_date_3_in_1_DAPV=last_date_3_in_1_DAPV,due_date_3_in_1_DAPV=due_date_3_in_1_DAPV,
					last_date_4_in_1_DHPP=last_date_4_in_1_DHPP,due_date_4_in_1_DHPP=due_date_4_in_1_DHPP,last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC,
					due_date_6_in_1_DA2PPC=due_date_6_in_1_DA2PPC,last_date_7_in_1_DA2PPVL2=last_date_7_in_1_DA2PPVL2,due_date_7_in_1_DA2PPVL2=due_date_7_in_1_DA2PPVL2,
					last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP,due_date_5_in_1_DA2PP=due_date_5_in_1_DA2PP,last_date_rabies=last_date_rabies,due_date_rabies=due_date_rabies,
					last_date_distemper=last_date_distemper,due_date_distemper=due_date_distemper,last_date_CAV_1=last_date_CAV_1,due_date_CAV_1=due_date_CAV_1,
					last_date_parovirus=last_date_parovirus,due_date_parovirus=due_date_parovirus,last_date_parainfluenza=last_date_parainfluenza,due_date_parainfluenza=due_date_parainfluenza,
					last_date_9_in_1_vaccine=last_date_9_in_1_vaccine,due_date_9_in_1_vaccine=due_date_9_in_1_vaccine,last_date_10_in_1_vaccine=last_date_10_in_1_vaccine,
					due_date_10_in_1_vaccine=due_date_10_in_1_vaccine,last_date_Feline_vaccine=last_date_Feline_vaccine,due_date_Feline_vaccine=due_date_Feline_vaccine)
					if Doctor.objects.get(id=doc_pk).stock_management=='yes':
						if Prescription.objects.filter(purpose_id=purpose_id).exists():
							medicine1_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_name
							medicine1_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_quantity
							medicine2_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_name
							medicine2_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_quantity
							medicine3_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_name
							medicine3_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_quantity
							medicine4_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_name
							medicine4_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_quantity
							medicine5_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_name
							medicine5_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_quantity
							medicine6_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_name
							medicine6_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_quantity
							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).last().quantity
								present_quantity=medicine1_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).last().quantity
								present_quantity=medicine2_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								print(reduced_quantity)
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).last().quantity
								present_quantity=medicine3_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).last().quantity
								present_quantity=medicine4_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).last().quantity
								present_quantity=medicine5_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).last().quantity
								present_quantity=medicine6_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).update(quantity=reduced_quantity)
						else:
							pass
					return redirect('summary')
		else:
			return redirect('vaccination')


def vitals(request):
	doc_pk = request.session.get('doc_pk')
	pet_pk = request.session.get('pet_pk')
	purpose_pk = request.session.get('purpose_pk')
	pet_obj=Pet.objects.filter(id=pet_pk).last()
	pet_obj=pet_age_converter_single(pet_obj)
	purpose_pet_obj_diet=PurposeAndDiet.objects.filter(id=purpose_pk).last()
	purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
	purpose_pet_obj_id=purpose_pet_obj.id
	doc_pk_stock=Doctor.objects.get(id=doc_pk)
	try:
		exist_data=Vitals.objects.filter(purpose_id=purpose_pet_obj).last()
		exist_data=model_to_dict(exist_data)
		print(dict(exist_data))
		for k,v in exist_data.items():
			if v!='':
				print(k,v)
				if chr(176)+'F' in str(v) or 'cm' in str(v) or 'kgs' in str(v) or 'Beats/min' in str(v)  or 'Breaths/min' in str(v) or 'Years' in str(v) or 'Days' in str(v) or 'Months' in str(v):
					v=v.replace(chr(176)+'F','').replace('kgs','').replace('Beats/min','').replace('Breaths/min','').replace('Years','') .replace('Days','').replace('Months','').replace(' ','').replace('cm','')
					exist_data[k]=v
	except :
		pass
	if pet_pk:
		pet_pk=pet_pk
	if request.method == "GET":
		if 'doc_pk' in request.session:
			return render(request,'doctor/Doctor_Vitals.html',{'pet_obj':pet_obj,
			'purpose_pet_obj_diet':purpose_pet_obj_diet,
			'doc_pk':doc_pk,'pet_pk':pet_pk,'purpose_pk':purpose_pk,
			'exist_data':exist_data,'doc_pk_stock':doc_pk_stock,
			'purpose_pet_obj':purpose_pet_obj,})
		else:
			return redirect('doctor_login')
	if pet_pk:
		pet_pk=pet_pk
		if request.method=='POST':
			if 'prescription_name' in request.POST:
				try:
					vitals=Vitals()
					vitals.purpose_id=purpose_pet_obj
					Temperature=request.POST.get('Temperature')
					if Temperature is '':
						pass
					else:
						vitals.Temperature=Temperature+' '+chr(176)+'F'
					Height=request.POST.get('Height')
					if Height is '':
						pass
					else:
						vitals.Height=Height+' '+'cm'
					Weight=request.POST.get('Weight')
					if Weight is '':
						pass
					else:
						vitals.Weight=Weight+' '+'kgs'
					Pulse_rate=request.POST.get('Pulse_rate')
					if Pulse_rate is '':
						pass
					else:
						vitals.Pulse_rate=Pulse_rate+' '+'Beats/min'
					Respiration_rate=request.POST.get('Respiration_rate')
					if Respiration_rate is '':
						pass
					else:
						vitals.Respiration_rate=Respiration_rate+' '+'Breaths/min'
					Age_of_maturity=request.POST.get('Age_of_maturity')
					if Age_of_maturity is '':
						pass
					else:
						vitals.Age_of_maturity=Age_of_maturity+' '+'Years'
					Oestrus=request.POST.get('Oestrus')
					if Oestrus is '':
						pass
					else:
						vitals.Oestrus=Oestrus+' '+'Days'
					Pregnancy=request.POST.get('Pregnancy')
					if Pregnancy is '':
						pass
					else:
						vitals.Pregnancy=Pregnancy+' '+'Months'
					vitals.save()
					return redirect('prescription')


				except:
					if Vitals.objects.filter(purpose_id=purpose_pet_obj).exists:
						vitals=Vitals.objects.get(purpose_id=purpose_pet_obj)
						vitals_id=vitals.id
						if request.method=='POST':
							vitals=Vitals()
							purpose_id1=purpose_pet_obj
							purpose_id=purpose_id1
							Temperature=request.POST.get('Temperature')
							if Temperature is '' or Temperature=='None':
								Temperature=''
							else:
								Temperature=Temperature+' '+chr(176)+'F'
							Height=request.POST.get('Height')
							if Height is '' or Height=='None':
								Height=''
							else:
								Height=Height+' '+'cm'
							Weight=request.POST.get('Weight')
							if Weight is '' or Weight=='None':
								Weight=''
							else:
								Weight=Weight+' '+'kgs'
							Pulse_rate=request.POST.get('Pulse_rate')
							if Pulse_rate is '' or Pulse_rate=='None':
								Pulse_rate=''
							else:
								Pulse_rate=Pulse_rate+' '+'Beats/min'
							Respiration_rate=request.POST.get('Respiration_rate')
							if Respiration_rate is '' or Respiration_rate=='None':
								Respiration_rate=''
							else:
								Respiration_rate=Respiration_rate+' '+'Breaths/min'
							Age_of_maturity=request.POST.get('Age_of_maturity')
							print(Age_of_maturity,'yuyuyu')
							if Age_of_maturity is '' or Age_of_maturity=='None':
								Age_of_maturity=''
							else:
								Age_of_maturity=Age_of_maturity+' '+'Years'
							Oestrus=request.POST.get('Oestrus')
							if Oestrus is '' or Oestrus=='None':
								Oestrus=''
							else:
								Oestrus=Oestrus+' '+'Days'
							Pregnancy=request.POST.get('Pregnancy')
							if Pregnancy is '' or Pregnancy=='None':
								Pregnancy=''
							else:
								Pregnancy=Pregnancy+' '+'Months'
							Vitals.objects.filter(id=vitals_id).update(purpose_id=purpose_id,Temperature=Temperature,
							Height=Height,Weight=Weight,Pulse_rate=Pulse_rate,Respiration_rate=Respiration_rate,
							Age_of_maturity=Age_of_maturity,Oestrus=Oestrus,Pregnancy=Pregnancy)
						return redirect('prescription')

			elif 'assessment_name' in request.POST:
				try:
					vitals=Vitals()
					vitals.purpose_id=purpose_pet_obj
					Temperature=request.POST.get('Temperature')
					if Temperature is '':
						pass
					else:
						vitals.Temperature=Temperature+' '+chr(176)+'F'
					Height=request.POST.get('Height')
					if Height is '':
						pass
					else:
						vitals.Height=Height+' '+'cm'
					Weight=request.POST.get('Weight')
					if Weight is '':
						pass
					else:
						vitals.Weight=Weight+' '+'kgs'
					Pulse_rate=request.POST.get('Pulse_rate')
					if Pulse_rate is '':
						pass
					else:
						vitals.Pulse_rate=Pulse_rate+' '+'Beats/min'
					Respiration_rate=request.POST.get('Respiration_rate')
					if Respiration_rate is '':
						pass
					else:
						vitals.Respiration_rate=Respiration_rate+' '+'Breaths/min'
					Age_of_maturity=request.POST.get('Age_of_maturity')
					if Age_of_maturity is '':
						pass
					else:
						vitals.Age_of_maturity=Age_of_maturity+' '+'Years'
					Oestrus=request.POST.get('Oestrus')
					if Oestrus is '':
						pass
					else:
						vitals.Oestrus=Oestrus+' '+'Days'
					Pregnancy=request.POST.get('Pregnancy')
					if Pregnancy is '':
						pass
					else:
						vitals.Pregnancy=Pregnancy+' '+'Months'
					vitals.save()
					return redirect('assessment')


				except:
					if Vitals.objects.filter(purpose_id=purpose_pet_obj).exists:
						vitals=Vitals.objects.get(purpose_id=purpose_pet_obj)
						vitals_id=vitals.id
						if request.method=='POST':
							vitals=Vitals()
							purpose_id1=purpose_pet_obj
							purpose_id=purpose_id1
							Temperature=request.POST.get('Temperature')
							if Temperature is '' or Temperature=='None':
								Temperature=''
							else:
								Temperature=Temperature+' '+chr(176)+'F'
							Height=request.POST.get('Height')
							if Height is '' or Height=='None':
								Height=''
							else:
								Height=Height+' '+'cm'
							Weight=request.POST.get('Weight')
							if Weight is '' or Weight=='None':
								Weight=''
							else:
								Weight=Weight+' '+'kgs'
							Pulse_rate=request.POST.get('Pulse_rate')
							if Pulse_rate is '' or Pulse_rate=='None':
								Pulse_rate=''
							else:
								Pulse_rate=Pulse_rate+' '+'Beats/min'
							Respiration_rate=request.POST.get('Respiration_rate')
							if Respiration_rate is '' or Respiration_rate=='None':
								Respiration_rate=''
							else:
								Respiration_rate=Respiration_rate+' '+'Breaths/min'
							Age_of_maturity=request.POST.get('Age_of_maturity')
							print(Age_of_maturity,'yuyuyu')
							if Age_of_maturity is '' or Age_of_maturity=='None':
								Age_of_maturity=''
							else:
								Age_of_maturity=Age_of_maturity+' '+'Years'
							Oestrus=request.POST.get('Oestrus')
							if Oestrus is '' or Oestrus=='None':
								Oestrus=''
							else:
								Oestrus=Oestrus+' '+'Days'
							Pregnancy=request.POST.get('Pregnancy')
							if Pregnancy is '' or Pregnancy=='None':
								Pregnancy=''
							else:
								Pregnancy=Pregnancy+' '+'Months'
							Vitals.objects.filter(id=vitals_id).update(purpose_id=purpose_id,Temperature=Temperature,
							Height=Height,Weight=Weight,Pulse_rate=Pulse_rate,Respiration_rate=Respiration_rate,
							Age_of_maturity=Age_of_maturity,Oestrus=Oestrus,Pregnancy=Pregnancy)
						return redirect('assessment')
			elif 'diagnostic_name' in request.POST:
				try:
					vitals=Vitals()
					vitals.purpose_id=purpose_pet_obj
					Temperature=request.POST.get('Temperature')
					if Temperature is '':
						pass
					else:
						vitals.Temperature=Temperature+' '+chr(176)+'F'
					Height=request.POST.get('Height')
					if Height is '':
						pass
					else:
						vitals.Height=Height+' '+'cm'
					Weight=request.POST.get('Weight')
					if Weight is '':
						pass
					else:
						vitals.Weight=Weight+' '+'kgs'
					Pulse_rate=request.POST.get('Pulse_rate')
					if Pulse_rate is '':
						pass
					else:
						vitals.Pulse_rate=Pulse_rate+' '+'Beats/min'
					Respiration_rate=request.POST.get('Respiration_rate')
					if Respiration_rate is '':
						pass
					else:
						vitals.Respiration_rate=Respiration_rate+' '+'Breaths/min'
					Age_of_maturity=request.POST.get('Age_of_maturity')
					if Age_of_maturity is '':
						pass
					else:
						vitals.Age_of_maturity=Age_of_maturity+' '+'Years'
					Oestrus=request.POST.get('Oestrus')
					if Oestrus is '':
						pass
					else:
						vitals.Oestrus=Oestrus+' '+'Days'
					Pregnancy=request.POST.get('Pregnancy')
					if Pregnancy is '':
						pass
					else:
						vitals.Pregnancy=Pregnancy+' '+'Months'
					vitals.save()
					return redirect('diagnostic_prescription')


				except:
					if Vitals.objects.filter(purpose_id=purpose_pet_obj).exists:
						vitals=Vitals.objects.get(purpose_id=purpose_pet_obj)
						vitals_id=vitals.id
						if request.method=='POST':
							vitals=Vitals()
							purpose_id1=purpose_pet_obj
							purpose_id=purpose_id1
							Temperature=request.POST.get('Temperature')
							if Temperature is '' or Temperature=='None':
								Temperature=''
							else:
								Temperature=Temperature+' '+chr(176)+'F'
							Height=request.POST.get('Height')
							if Height is '' or Height=='None':
								Height=''
							else:
								Height=Height+' '+'cm'
							Weight=request.POST.get('Weight')
							if Weight is '' or Weight=='None':
								Weight=''
							else:
								Weight=Weight+' '+'kgs'
							Pulse_rate=request.POST.get('Pulse_rate')
							if Pulse_rate is '' or Pulse_rate=='None':
								Pulse_rate=''
							else:
								Pulse_rate=Pulse_rate+' '+'Beats/min'
							Respiration_rate=request.POST.get('Respiration_rate')
							if Respiration_rate is '' or Respiration_rate=='None':
								Respiration_rate=''
							else:
								Respiration_rate=Respiration_rate+' '+'Breaths/min'
							Age_of_maturity=request.POST.get('Age_of_maturity')
							print(Age_of_maturity,'yuyuyu')
							if Age_of_maturity is '' or Age_of_maturity=='None':
								Age_of_maturity=''
							else:
								Age_of_maturity=Age_of_maturity+' '+'Years'
							Oestrus=request.POST.get('Oestrus')
							if Oestrus is '' or Oestrus=='None':
								Oestrus=''
							else:
								Oestrus=Oestrus+' '+'Days'
							Pregnancy=request.POST.get('Pregnancy')
							if Pregnancy is '' or Pregnancy=='None':
								Pregnancy=''
							else:
								Pregnancy=Pregnancy+' '+'Months'
							Vitals.objects.filter(id=vitals_id).update(purpose_id=purpose_id,Temperature=Temperature,
							Height=Height,Weight=Weight,Pulse_rate=Pulse_rate,Respiration_rate=Respiration_rate,
							Age_of_maturity=Age_of_maturity,Oestrus=Oestrus,Pregnancy=Pregnancy)
						return redirect('diagnostic_prescription')
			elif 'vaccination_name' in request.POST:
				try:
					vitals=Vitals()
					vitals.purpose_id=purpose_pet_obj
					Temperature=request.POST.get('Temperature')
					if Temperature is '':
						pass
					else:
						vitals.Temperature=Temperature+' '+chr(176)+'F'
					Height=request.POST.get('Height')
					if Height is '':
						pass
					else:
						vitals.Height=Height+' '+'cm'
					Weight=request.POST.get('Weight')
					if Weight is '':
						pass
					else:
						vitals.Weight=Weight+' '+'kgs'
					Pulse_rate=request.POST.get('Pulse_rate')
					if Pulse_rate is '':
						pass
					else:
						vitals.Pulse_rate=Pulse_rate+' '+'Beats/min'
					Respiration_rate=request.POST.get('Respiration_rate')
					if Respiration_rate is '':
						pass
					else:
						vitals.Respiration_rate=Respiration_rate+' '+'Breaths/min'
					Age_of_maturity=request.POST.get('Age_of_maturity')
					if Age_of_maturity is '':
						pass
					else:
						vitals.Age_of_maturity=Age_of_maturity+' '+'Years'
					Oestrus=request.POST.get('Oestrus')
					if Oestrus is '':
						pass
					else:
						vitals.Oestrus=Oestrus+' '+'Days'
					Pregnancy=request.POST.get('Pregnancy')
					if Pregnancy is '':
						pass
					else:
						vitals.Pregnancy=Pregnancy+' '+'Months'
					vitals.save()
					return redirect('vaccination')


				except:
					if Vitals.objects.filter(purpose_id=purpose_pet_obj).exists:
						vitals=Vitals.objects.get(purpose_id=purpose_pet_obj)
						vitals_id=vitals.id
						if request.method=='POST':
							vitals=Vitals()
							purpose_id1=purpose_pet_obj
							purpose_id=purpose_id1
							Temperature=request.POST.get('Temperature')
							if Temperature is '' or Temperature=='None':
								Temperature=''
							else:
								Temperature=Temperature+' '+chr(176)+'F'
							Height=request.POST.get('Height')
							if Height is '' or Height=='None':
								Height=''
							else:
								Height=Height+' '+'cm'
							Weight=request.POST.get('Weight')
							if Weight is '' or Weight=='None':
								Weight=''
							else:
								Weight=Weight+' '+'kgs'
							Pulse_rate=request.POST.get('Pulse_rate')
							if Pulse_rate is '' or Pulse_rate=='None':
								Pulse_rate=''
							else:
								Pulse_rate=Pulse_rate+' '+'Beats/min'
							Respiration_rate=request.POST.get('Respiration_rate')
							if Respiration_rate is '' or Respiration_rate=='None':
								Respiration_rate=''
							else:
								Respiration_rate=Respiration_rate+' '+'Breaths/min'
							Age_of_maturity=request.POST.get('Age_of_maturity')
							print(Age_of_maturity,'yuyuyu')
							if Age_of_maturity is '' or Age_of_maturity=='None':
								Age_of_maturity=''
							else:
								Age_of_maturity=Age_of_maturity+' '+'Years'
							Oestrus=request.POST.get('Oestrus')
							if Oestrus is '' or Oestrus=='None':
								Oestrus=''
							else:
								Oestrus=Oestrus+' '+'Days'
							Pregnancy=request.POST.get('Pregnancy')
							if Pregnancy is '' or Pregnancy=='None':
								Pregnancy=''
							else:
								Pregnancy=Pregnancy+' '+'Months'
							Vitals.objects.filter(id=vitals_id).update(purpose_id=purpose_id,Temperature=Temperature,
							Height=Height,Weight=Weight,Pulse_rate=Pulse_rate,Respiration_rate=Respiration_rate,
							Age_of_maturity=Age_of_maturity,Oestrus=Oestrus,Pregnancy=Pregnancy)
						return redirect('vaccination')
			elif 'deworming_name' in request.POST:
				try:
					vitals=Vitals()
					vitals.purpose_id=purpose_pet_obj
					Temperature=request.POST.get('Temperature')
					if Temperature is '':
						pass
					else:
						vitals.Temperature=Temperature+' '+chr(176)+'F'
					Height=request.POST.get('Height')
					if Height is '':
						pass
					else:
						vitals.Height=Height+' '+'cm'
					Weight=request.POST.get('Weight')
					if Weight is '':
						pass
					else:
						vitals.Weight=Weight+' '+'kgs'
					Pulse_rate=request.POST.get('Pulse_rate')
					if Pulse_rate is '':
						pass
					else:
						vitals.Pulse_rate=Pulse_rate+' '+'Beats/min'
					Respiration_rate=request.POST.get('Respiration_rate')
					if Respiration_rate is '':
						pass
					else:
						vitals.Respiration_rate=Respiration_rate+' '+'Breaths/min'
					Age_of_maturity=request.POST.get('Age_of_maturity')
					if Age_of_maturity is '':
						pass
					else:
						vitals.Age_of_maturity=Age_of_maturity+' '+'Years'
					Oestrus=request.POST.get('Oestrus')
					if Oestrus is '':
						pass
					else:
						vitals.Oestrus=Oestrus+' '+'Days'
					Pregnancy=request.POST.get('Pregnancy')
					if Pregnancy is '':
						pass
					else:
						vitals.Pregnancy=Pregnancy+' '+'Months'
					vitals.save()
					return redirect('deworming')


				except:
					if Vitals.objects.filter(purpose_id=purpose_pet_obj).exists:
						vitals=Vitals.objects.get(purpose_id=purpose_pet_obj)
						vitals_id=vitals.id
						if request.method=='POST':
							vitals=Vitals()
							purpose_id1=purpose_pet_obj
							purpose_id=purpose_id1
							Temperature=request.POST.get('Temperature')
							if Temperature is '' or Temperature=='None':
								Temperature=''
							else:
								Temperature=Temperature+' '+chr(176)+'F'
							Height=request.POST.get('Height')
							if Height is '' or Height=='None':
								Height=''
							else:
								Height=Height+' '+'cm'
							Weight=request.POST.get('Weight')
							if Weight is '' or Weight=='None':
								Weight=''
							else:
								Weight=Weight+' '+'kgs'
							Pulse_rate=request.POST.get('Pulse_rate')
							if Pulse_rate is '' or Pulse_rate=='None':
								Pulse_rate=''
							else:
								Pulse_rate=Pulse_rate+' '+'Beats/min'
							Respiration_rate=request.POST.get('Respiration_rate')
							if Respiration_rate is '' or Respiration_rate=='None':
								Respiration_rate=''
							else:
								Respiration_rate=Respiration_rate+' '+'Breaths/min'
							Age_of_maturity=request.POST.get('Age_of_maturity')
							print(Age_of_maturity,'yuyuyu')
							if Age_of_maturity is '' or Age_of_maturity=='None':
								Age_of_maturity=''
							else:
								Age_of_maturity=Age_of_maturity+' '+'Years'
							Oestrus=request.POST.get('Oestrus')
							if Oestrus is '' or Oestrus=='None':
								Oestrus=''
							else:
								Oestrus=Oestrus+' '+'Days'
							Pregnancy=request.POST.get('Pregnancy')
							if Pregnancy is '' or Pregnancy=='None':
								Pregnancy=''
							else:
								Pregnancy=Pregnancy+' '+'Months'
							Vitals.objects.filter(id=vitals_id).update(purpose_id=purpose_id,Temperature=Temperature,
							Height=Height,Weight=Weight,Pulse_rate=Pulse_rate,Respiration_rate=Respiration_rate,
							Age_of_maturity=Age_of_maturity,Oestrus=Oestrus,Pregnancy=Pregnancy)
						return redirect('deworming')
			elif 'symptoms_name' in request.POST:
				try:
					vitals=Vitals()
					vitals.purpose_id=purpose_pet_obj
					Temperature=request.POST.get('Temperature')
					if Temperature is '':
						pass
					else:
						vitals.Temperature=Temperature+' '+chr(176)+'F'
					Height=request.POST.get('Height')
					if Height is '':
						pass
					else:
						vitals.Height=Height+' '+'cm'
					Weight=request.POST.get('Weight')
					if Weight is '':
						pass
					else:
						vitals.Weight=Weight+' '+'kgs'
					Pulse_rate=request.POST.get('Pulse_rate')
					if Pulse_rate is '':
						pass
					else:
						vitals.Pulse_rate=Pulse_rate+' '+'Beats/min'
					Respiration_rate=request.POST.get('Respiration_rate')
					if Respiration_rate is '':
						pass
					else:
						vitals.Respiration_rate=Respiration_rate+' '+'Breaths/min'
					Age_of_maturity=request.POST.get('Age_of_maturity')
					if Age_of_maturity is '':
						pass
					else:
						vitals.Age_of_maturity=Age_of_maturity+' '+'Years'
					Oestrus=request.POST.get('Oestrus')
					if Oestrus is '':
						pass
					else:
						vitals.Oestrus=Oestrus+' '+'Days'
					Pregnancy=request.POST.get('Pregnancy')
					if Pregnancy is '':
						pass
					else:
						vitals.Pregnancy=Pregnancy+' '+'Months'
					vitals.save()
					return redirect('symptoms')


				except:
					if Vitals.objects.filter(purpose_id=purpose_pet_obj).exists:
						vitals=Vitals.objects.get(purpose_id=purpose_pet_obj)
						vitals_id=vitals.id
						if request.method=='POST':
							vitals=Vitals()
							purpose_id1=purpose_pet_obj
							purpose_id=purpose_id1
							Temperature=request.POST.get('Temperature')
							if Temperature is '' or Temperature=='None':
								Temperature=''
							else:
								Temperature=Temperature+' '+chr(176)+'F'
							Height=request.POST.get('Height')
							if Height is '' or Height=='None':
								Height=''
							else:
								Height=Height+' '+'cm'
							Weight=request.POST.get('Weight')
							if Weight is '' or Weight=='None':
								Weight=''
							else:
								Weight=Weight+' '+'kgs'
							Pulse_rate=request.POST.get('Pulse_rate')
							if Pulse_rate is '' or Pulse_rate=='None':
								Pulse_rate=''
							else:
								Pulse_rate=Pulse_rate+' '+'Beats/min'
							Respiration_rate=request.POST.get('Respiration_rate')
							if Respiration_rate is '' or Respiration_rate=='None':
								Respiration_rate=''
							else:
								Respiration_rate=Respiration_rate+' '+'Breaths/min'
							Age_of_maturity=request.POST.get('Age_of_maturity')
							print(Age_of_maturity,'yuyuyu')
							if Age_of_maturity is '' or Age_of_maturity=='None':
								Age_of_maturity=''
							else:
								Age_of_maturity=Age_of_maturity+' '+'Years'
							Oestrus=request.POST.get('Oestrus')
							if Oestrus is '' or Oestrus=='None':
								Oestrus=''
							else:
								Oestrus=Oestrus+' '+'Days'
							Pregnancy=request.POST.get('Pregnancy')
							if Pregnancy is '' or Pregnancy=='None':
								Pregnancy=''
							else:
								Pregnancy=Pregnancy+' '+'Months'
							Vitals.objects.filter(id=vitals_id).update(purpose_id=purpose_id,Temperature=Temperature,
							Height=Height,Weight=Weight,Pulse_rate=Pulse_rate,Respiration_rate=Respiration_rate,
							Age_of_maturity=Age_of_maturity,Oestrus=Oestrus,Pregnancy=Pregnancy)
						return redirect('symptoms')
			elif 'close_visit' in request.POST:
				if Doctor.objects.filter(id=doc_pk).last().stock_management=='yes':
					print('ok')
				else:
					print('no')
				try:
					vitals=Vitals()
					vitals.purpose_id=purpose_pet_obj
					Temperature=request.POST.get('Temperature')
					if Temperature is '':
						pass
					else:
						vitals.Temperature=Temperature+' '+chr(176)+'F'
					Height=request.POST.get('Height')
					if Height is '':
						pass
					else:
						vitals.Height=Height+' '+'cm'
					Weight=request.POST.get('Weight')
					if Weight is '':
						pass
					else:
						vitals.Weight=Weight+' '+'kgs'
					Pulse_rate=request.POST.get('Pulse_rate')
					if Pulse_rate is '':
						pass
					else:
						vitals.Pulse_rate=Pulse_rate+' '+'Beats/min'
					Respiration_rate=request.POST.get('Respiration_rate')
					if Respiration_rate is '':
						pass
					else:
						vitals.Respiration_rate=Respiration_rate+' '+'Breaths/min'
					Age_of_maturity=request.POST.get('Age_of_maturity')
					if Age_of_maturity is '':
						pass
					else:
						vitals.Age_of_maturity=Age_of_maturity+' '+'Years'
					Oestrus=request.POST.get('Oestrus')
					if Oestrus is '':
						pass
					else:
						vitals.Oestrus=Oestrus+' '+'Days'
					Pregnancy=request.POST.get('Pregnancy')
					if Pregnancy is '':
						pass
					else:
						vitals.Pregnancy=Pregnancy+' '+'Months'
					vitals.save()
					if Doctor.objects.get(id=doc_pk).stock_management=='yes':
						if Prescription.objects.filter(purpose_id=purpose_id).exists():
							medicine1_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_name
							medicine1_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_quantity
							medicine2_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_name
							medicine2_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_quantity
							medicine3_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_name
							medicine3_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_quantity
							medicine4_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_name
							medicine4_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_quantity
							medicine5_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_name
							medicine5_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_quantity
							medicine6_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_name
							medicine6_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_quantity
							if stock.objects.filter(doctor__id=doc_id,medicine=medicine1_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_id,medicine=medicine1_name).last().quantity
								present_quantity=medicine1_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).last().quantity
								present_quantity=medicine2_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								print(reduced_quantity)
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).last().quantity
								present_quantity=medicine3_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).last().quantity
								present_quantity=medicine4_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).last().quantity
								present_quantity=medicine5_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).last().quantity
								present_quantity=medicine6_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).update(quantity=reduced_quantity)
						else:
							pass


					return redirect('summary')


				except:
					if Vitals.objects.filter(purpose_id=purpose_pet_obj).exists:

						vitals=Vitals.objects.get(purpose_id=purpose_pet_obj)
						vitals_id=vitals.id
						if request.method=='POST':
							vitals=Vitals()
							purpose_id1=purpose_pet_obj
							purpose_id=purpose_id1
							Temperature=request.POST.get('Temperature')
							if Temperature is '' or Temperature=='None':
								Temperature=''
							else:
								Temperature=Temperature+' '+chr(176)+'F'
							Height=request.POST.get('Height')
							if Height is '' or Height=='None':
								Height=''
							else:
								Height=Height+' '+'cm'
							Weight=request.POST.get('Weight')
							if Weight is '' or Weight=='None':
								Weight=''
							else:
								Weight=Weight+' '+'kgs'
							Pulse_rate=request.POST.get('Pulse_rate')
							if Pulse_rate is '' or Pulse_rate=='None':
								Pulse_rate=''
							else:
								Pulse_rate=Pulse_rate+' '+'Beats/min'
							Respiration_rate=request.POST.get('Respiration_rate')
							if Respiration_rate is '' or Respiration_rate=='None':
								Respiration_rate=''
							else:
								Respiration_rate=Respiration_rate+' '+'Breaths/min'
							Age_of_maturity=request.POST.get('Age_of_maturity')
							print(Age_of_maturity,'yuyuyu')
							if Age_of_maturity is '' or Age_of_maturity=='None':
								Age_of_maturity=''
							else:
								Age_of_maturity=Age_of_maturity+' '+'Years'
							Oestrus=request.POST.get('Oestrus')
							if Oestrus is '' or Oestrus=='None':
								Oestrus=''
							else:
								Oestrus=Oestrus+' '+'Days'
							Pregnancy=request.POST.get('Pregnancy')
							if Pregnancy is '' or Pregnancy=='None':
								Pregnancy=''
							else:
								Pregnancy=Pregnancy+' '+'Months'
							Vitals.objects.filter(id=vitals_id).update(purpose_id=purpose_id,Temperature=Temperature,
							Height=Height,Weight=Weight,Pulse_rate=Pulse_rate,Respiration_rate=Respiration_rate,
							Age_of_maturity=Age_of_maturity,Oestrus=Oestrus,Pregnancy=Pregnancy)
							if Doctor.objects.get(id=doc_pk).stock_management=='yes':
								if Prescription.objects.filter(purpose_id=purpose_id).exists():
									medicine1_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_name
									medicine1_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_quantity
									medicine2_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_name
									medicine2_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_quantity
									medicine3_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_name
									medicine3_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_quantity
									medicine4_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_name
									medicine4_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_quantity
									medicine5_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_name
									medicine5_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_quantity
									medicine6_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_name
									medicine6_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_quantity
									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).last().quantity
										present_quantity=medicine1_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).last().quantity
										present_quantity=medicine2_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										print(reduced_quantity)
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).last().quantity
										present_quantity=medicine3_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).last().quantity
										present_quantity=medicine4_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).last().quantity
										present_quantity=medicine5_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).last().quantity
										present_quantity=medicine6_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).update(quantity=reduced_quantity)
							else:
								pass
							return redirect('summary')
			else:
				return redirect('vitals')

def deworming(request):
	doc_pk = request.session.get('doc_pk')
	pet_pk = request.session.get('pet_pk')
	purpose_pk = request.session.get('purpose_pk')
	pet_obj=Pet.objects.filter(id=pet_pk).last()
	pet_obj_convert=pet_age_converter_single(pet_obj)
	purpose_pet_obj_diet=PurposeAndDiet.objects.filter(id=purpose_pk).last()
	pet_obj=Pet.objects.get(id=pet_pk)
	purpose_pet_obj_save=PurposeAndDiet.objects.filter(pet_id=pet_obj).last()
	purpose_pet_obj=PurposeAndDiet.objects.filter(pet_id=pet_obj).all()
	cust_deworming=Vaccination_coustmer.objects.filter(pet=pet_obj).last()
	deworming=Deworming.objects.filter(pet=pet_obj).exclude(purpose_id__id=purpose_pk)
	purpose_obj=PurposeAndDiet.objects.get(id=purpose_pk)
	purpose_id=purpose_pk
	doc_pk_stock=Doctor.objects.get(id=doc_pk)
	try:
		x=Deworming.objects.filter(purpose_id=purpose_pk).last()
		x=model_to_dict(x)
	except:
		pass
	if pet_pk:
		pet_pk=pet_pk

	if request.method == "GET":
		if 'doc_pk' in request.session:
			return render(request,'doctor/Doctor_deworming.html',
			{'last_deworming':deworming,'pet_obj':pet_obj_convert,
			'purpose_pet_obj':purpose_obj,'doc_pk':doc_pk,
			'purpose_pet_obj_diet':purpose_pet_obj_diet,
			'cust_deworming':cust_deworming,'pet_pk':pet_pk,
			'purpose_pk':purpose_pk,'x':x,'doc_pk_stock':doc_pk_stock})
		else:
			return redirect('doctor_login')

	if request.method=='POST':
		if 'symptoms_name' in request.POST:
			try:
				deworming=Deworming()
				purpose_pet_obj_save=PurposeAndDiet.objects.get(id=purpose_pk)
				deworming.purpose_id=purpose_pet_obj_save
				pet_obj=Pet.objects.filter(id=pet_pk).last()
				deworming.pet=pet_obj
				last_date=request.POST.get('current_date')
				last_date=datenone(last_date)
				deworming.last_date=last_date
				due_date=request.POST.get('due_date')
				due_date=datenone(due_date)
				deworming.due_date=due_date
				deworming.save()
				return redirect('symptoms')
			except:
				if Deworming.objects.filter(purpose_id=purpose_obj).exists():
					deworming_id=Deworming.objects.get(purpose_id=purpose_obj).id
					pet_obj=Pet.objects.filter(id=pet_pk).last()
					deworming.pet=pet_obj
					last_date=request.POST.get('current_date')
					last_date=datenone(last_date)
					last_date=last_date
					due_date=request.POST.get('due_date')
					due_date=datenone(due_date)
					due_date=due_date
					Deworming.objects.filter(id=deworming_id).update(last_date=last_date,due_date=due_date)
					return redirect('symptoms',pet_pk=pet_pk,purpose_pk=purpose_pk,doc_id=doc_id)
		elif 'assessment_name' in request.POST:
			try:
				deworming=Deworming()
				purpose_pet_obj_save=PurposeAndDiet.objects.get(id=purpose_pk)
				deworming.purpose_id=purpose_pet_obj_save
				pet_obj=Pet.objects.filter(id=pet_pk).last()
				deworming.pet=pet_obj
				last_date=request.POST.get('current_date')
				last_date=datenone(last_date)
				deworming.last_date=last_date
				due_date=request.POST.get('due_date')
				due_date=datenone(due_date)
				deworming.due_date=due_date
				deworming.save()
				return redirect('assessment')
			except:
				if Deworming.objects.filter(purpose_id=purpose_obj).exists():
					deworming_id=Deworming.objects.get(purpose_id=purpose_obj).id
					pet_obj=Pet.objects.filter(id=pet_pk).last()
					deworming.pet=pet_obj
					last_date=request.POST.get('current_date')
					last_date=datenone(last_date)
					last_date=last_date
					due_date=request.POST.get('due_date')
					due_date=datenone(due_date)
					due_date=due_date
					Deworming.objects.filter(id=deworming_id).update(last_date=last_date,due_date=due_date)
					return redirect('assessment')

		elif 'vitals_name' in request.POST:
			try:
				deworming=Deworming()
				purpose_pet_obj_save=PurposeAndDiet.objects.get(id=purpose_pk)
				deworming.purpose_id=purpose_pet_obj_save
				pet_obj=Pet.objects.filter(id=pet_pk).last()
				deworming.pet=pet_obj
				last_date=request.POST.get('current_date')
				last_date=datenone(last_date)
				deworming.last_date=last_date
				due_date=request.POST.get('due_date')
				due_date=datenone(due_date)
				deworming.due_date=due_date
				deworming.save()
				return redirect('vitals')
			except:
				if Deworming.objects.filter(purpose_id=purpose_obj).exists():
					deworming_id=Deworming.objects.get(purpose_id=purpose_obj).id
					pet_obj=Pet.objects.filter(id=pet_pk).last()
					deworming.pet=pet_obj
					last_date=request.POST.get('current_date')
					last_date=datenone(last_date)
					last_date=last_date
					due_date=request.POST.get('due_date')
					due_date=datenone(due_date)
					due_date=due_date
					Deworming.objects.filter(id=deworming_id).update(last_date=last_date,due_date=due_date)
					return redirect('vitals')
		elif 'diagnostic_name' in request.POST:
			try:
				deworming=Deworming()
				purpose_pet_obj_save=PurposeAndDiet.objects.get(id=purpose_pk)
				deworming.purpose_id=purpose_pet_obj_save
				pet_obj=Pet.objects.filter(id=pet_pk).last()
				deworming.pet=pet_obj
				last_date=request.POST.get('current_date')
				last_date=datenone(last_date)
				deworming.last_date=last_date
				due_date=request.POST.get('due_date')
				due_date=datenone(due_date)
				deworming.due_date=due_date
				deworming.save()
				return redirect('diagnostic_prescription')
			except:
				if Deworming.objects.filter(purpose_id=purpose_obj).exists():
					deworming_id=Deworming.objects.get(purpose_id=purpose_obj).id
					pet_obj=Pet.objects.filter(id=pet_pk).last()
					deworming.pet=pet_obj
					last_date=request.POST.get('current_date')
					last_date=datenone(last_date)
					last_date=last_date
					due_date=request.POST.get('due_date')
					due_date=datenone(due_date)
					due_date=due_date
					Deworming.objects.filter(id=deworming_id).update(last_date=last_date,due_date=due_date)
					return redirect('diagnostic_prescription')
		elif 'prescription_name' in request.POST:
			try:
				deworming=Deworming()
				purpose_pet_obj_save=PurposeAndDiet.objects.get(id=purpose_pk)
				deworming.purpose_id=purpose_pet_obj_save
				pet_obj=Pet.objects.filter(id=pet_pk).last()
				deworming.pet=pet_obj
				last_date=request.POST.get('current_date')
				last_date=datenone(last_date)
				deworming.last_date=last_date
				due_date=request.POST.get('due_date')
				due_date=datenone(due_date)
				deworming.due_date=due_date
				deworming.save()
				return redirect('prescription')
			except:
				if Deworming.objects.filter(purpose_id=purpose_obj).exists():
					deworming_id=Deworming.objects.get(purpose_id=purpose_obj).id
					pet_obj=Pet.objects.filter(id=pet_pk).last()
					deworming.pet=pet_obj
					last_date=request.POST.get('current_date')
					last_date=datenone(last_date)
					last_date=last_date
					due_date=request.POST.get('due_date')
					due_date=datenone(due_date)
					due_date=due_date
					Deworming.objects.filter(id=deworming_id).update(last_date=last_date,due_date=due_date)
					return redirect('prescription')
		elif 'vaccination_name' in request.POST:
			try:
				deworming=Deworming()
				purpose_pet_obj_save=PurposeAndDiet.objects.get(id=purpose_pk)
				deworming.purpose_id=purpose_pet_obj_save
				pet_obj=Pet.objects.filter(id=pet_pk).last()
				deworming.pet=pet_obj
				last_date=request.POST.get('current_date')
				last_date=datenone(last_date)
				deworming.last_date=last_date
				due_date=request.POST.get('due_date')
				due_date=datenone(due_date)
				deworming.due_date=due_date
				deworming.save()
				return redirect('vaccination')
			except:
				if Deworming.objects.filter(purpose_id=purpose_obj).exists():
					deworming_id=Deworming.objects.get(purpose_id=purpose_obj).id
					pet_obj=Pet.objects.filter(id=pet_pk).last()
					deworming.pet=pet_obj
					last_date=request.POST.get('current_date')
					last_date=datenone(last_date)
					last_date=last_date
					due_date=request.POST.get('due_date')
					due_date=datenone(due_date)
					due_date=due_date
					Deworming.objects.filter(id=deworming_id).update(last_date=last_date,due_date=due_date)
					return redirect('vaccination')
		elif 'close_visit' in request.POST:
			try:
				deworming=Deworming()
				purpose_pet_obj_save=PurposeAndDiet.objects.get(id=purpose_pk)
				deworming.purpose_id=purpose_pet_obj_save
				pet_obj=Pet.objects.filter(id=pet_pk).last()
				deworming.pet=pet_obj
				last_date=request.POST.get('current_date')
				last_date=datenone(last_date)
				deworming.last_date=last_date
				due_date=request.POST.get('due_date')
				due_date=datenone(due_date)
				deworming.due_date=due_date
				deworming.save()
				if Doctor.objects.get(id=doc_id).stock_management=='yes':
					if Prescription.objects.filter(purpose_id=purpose_id).exists():
						medicine1_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_name
						medicine1_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_quantity
						medicine2_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_name
						medicine2_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_quantity
						medicine3_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_name
						medicine3_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_quantity
						medicine4_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_name
						medicine4_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_quantity
						medicine5_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_name
						medicine5_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_quantity
						medicine6_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_name
						medicine6_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_quantity
						if stock.objects.filter(doctor__id=doc_id,medicine=medicine1_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_id,medicine=medicine1_name).last().quantity
							present_quantity=medicine1_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).update(quantity=reduced_quantity)

						if stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).last().quantity
							present_quantity=medicine2_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							print(reduced_quantity)
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).update(quantity=reduced_quantity)

						if stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).last().quantity
							present_quantity=medicine3_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).update(quantity=reduced_quantity)

						if stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).last().quantity
							present_quantity=medicine4_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).update(quantity=reduced_quantity)

						if stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).last().quantity
							present_quantity=medicine5_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).update(quantity=reduced_quantity)

						if stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).last().quantity
							present_quantity=medicine6_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).update(quantity=reduced_quantity)
				else:
					pass
				return redirect('summary')
			except:
				if Deworming.objects.filter(purpose_id=purpose_obj).exists():
					deworming_id=Deworming.objects.get(purpose_id=purpose_obj).id
					pet_obj=Pet.objects.filter(id=pet_pk).last()
					deworming.pet=pet_obj
					last_date=request.POST.get('current_date')
					last_date=datenone(last_date)
					last_date=last_date
					due_date=request.POST.get('due_date')
					due_date=datenone(due_date)
					due_date=due_date
					Deworming.objects.filter(id=deworming_id).update(last_date=last_date,due_date=due_date)
					if Doctor.objects.get(id=doc_pk).stock_management=='yes':
						if Prescription.objects.filter(purpose_id=purpose_id).exists():
							medicine1_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_name
							medicine1_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_quantity
							medicine2_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_name
							medicine2_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_quantity
							medicine3_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_name
							medicine3_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_quantity
							medicine4_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_name
							medicine4_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_quantity
							medicine5_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_name
							medicine5_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_quantity
							medicine6_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_name
							medicine6_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_quantity
							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).last().quantity
								present_quantity=medicine1_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).last().quantity
								present_quantity=medicine2_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								print(reduced_quantity)
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).last().quantity
								present_quantity=medicine3_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).last().quantity
								present_quantity=medicine4_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).last().quantity
								present_quantity=medicine5_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).last().quantity
								present_quantity=medicine6_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).update(quantity=reduced_quantity)
					else:
						pass
					return redirect('summary')
		else:
			return redirect('deworming')
	else:
			return redirect('deworming')

def symptoms(request):
	doc_pk = request.sessions.get('doc_pk')
	purpose_pk = request.sessions.get('purpose_pk')
	pet_pk = request.sessions.get('pet_pk')
	pet_obj=Pet.objects.filter(id=pet_pk).last()
	pet_obj=pet_age_converter_single(pet_obj)
	purpose_pet_obj_diet=PurposeAndDiet.objects.filter(id=purpose_pk).last()
	purpose_pk=purpose_pk
	purpose_id=purpose_pk
	purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
	doc_pk_stock=Doctor.objects.get(id=doc_pk)
	if request.method == "GET":
		if 'doc_pk' in request.session:
			return render(request,'doctor/Doctor_symptoms.html',
			{'pet_pk':pet_pk,'purpose_pet_obj':purpose_pet_obj,
			'purpose_pk':purpose_pk,'pet_obj':pet_obj,
			'purpose_pet_obj_diet':purpose_pet_obj_diet,'doc_pk':doc_pk,
			'doc_pk_stock':doc_pk_stock})
		else:
			return redirect('doctor_login')
	if request.method=='POST':
			if 'close_visit' in request.POST:
				if Doctor.objects.get(id=doc_pk).stock_management=='yes':
						if Prescription.objects.filter(purpose_id=purpose_id).exists():
							medicine1_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_name
							medicine1_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_quantity
							medicine2_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_name
							medicine2_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_quantity
							medicine3_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_name
							medicine3_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_quantity
							medicine4_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_name
							medicine4_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_quantity
							medicine5_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_name
							medicine5_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_quantity
							medicine6_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_name
							medicine6_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_quantity
							if stock.objects.filter(doctor__id=doc_id,medicine=medicine1_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_id,medicine=medicine1_name).last().quantity
								present_quantity=medicine1_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_id,medicine=medicine1_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_id,medicine=medicine2_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_id,medicine=medicine2_name).last().quantity
								present_quantity=medicine2_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								print(reduced_quantity)
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_id,medicine=medicine2_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_id,medicine=medicine3_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_id,medicine=medicine3_name).last().quantity
								present_quantity=medicine3_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).last().quantity
								present_quantity=medicine4_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).last().quantity
								present_quantity=medicine5_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).last().quantity
								present_quantity=medicine6_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).update(quantity=reduced_quantity)
				else:
					pass
				return redirect('summary')

def visit_purpose2(request,pet_pk,purpose_pk,doc_id):
	purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
	pet_obj=Pet.objects.filter(id=pet_pk).last()
	pet_obj=pet_age_converter_single(pet_obj)
	purpose_pet_obj_diet=PurposeAndDiet.objects.filter(id=purpose_pk).last()
	purpose_pk=purpose_pk
	doc_pk_stock=Doctor.objects.get(id=doc_id)
	if request.method == "GET":
		if 'doctor_session_id' in request.session:
			session_id=request.session['doctor_session_id']
			if session_id == doc_id :
				return render(request,'doctor/Doctor_visit_purpose.html'
				,{'pet_pk':pet_pk,'purpose_pk':purpose_pk,
				'purpose_pet_obj':purpose_pet_obj,'pet_obj':pet_obj,
				'purpose_pet_obj_diet':purpose_pet_obj_diet,
				'doc_pk':doc_pk,'doc_pk_stock':doc_pk_stock})
			else:
				return redirect('doctor_login')
		else:
			return redirect('doctor_login')
	if request.method=='POST':
		return redirect('summary')

def Assessment_view(request):
	doc_pk = request.session.get('doc_pk')
	pet_pk = request.session.get('pet_pk')
	purpose_pk = request.session.get('purpose_pk')
	pet_obj=Pet.objects.filter(id=pet_pk).last()
	pet_obj=pet_age_converter_single(pet_obj)
	purpose_pet_obj_diet=PurposeAndDiet.objects.filter(id=purpose_pk).last()
	purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
	doc_pk_stock=Doctor.objects.get(id=doc_pk)
	try:
		x=Assessment.objects.filter(purpose_id=purpose_pet_obj).last()
		x=model_to_dict(x)
	except:
		pass

	if pet_pk:
		pet_pk=pet_pk
	if request.method == "GET":
		if 'doc_pk' in request.session:
			return render(request,'doctor/Doctor_assessment.html',
			{'pet_obj':pet_obj,'purpose_pet_obj_diet':purpose_pet_obj_diet,
			'pet_pk':pet_pk,'pet_pk':pet_pk,'purpose_pk':purpose_pk,
			'x':x,'doc_pk_stock':doc_pk_stock,'purpose_pet_obj':purpose_pet_obj,
			'doc_pk':doc_pk})
		else:
			return redirect('doctor_login')
	if request.method=="POST":
			if 'symptoms_name' in request.POST:
				try:
					assessment=Assessment()
					assessment.purpose_id=purpose_pet_obj
					assessment.DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
					assessment.EYES=request.POST.getlist('EYES')
					assessment.LUNGS=request.POST.getlist('LUNGS')
					assessment.EARS=request.POST.getlist('EARS')
					assessment.GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
					assessment.NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
					assessment.UROGENITAL=request.POST.getlist('UROGENITAL')
					assessment.MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
					assessment.MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
					assessment.HEART=request.POST.getlist('HEART')
					assessment.others=request.POST.get('others')
					assessment.save()
					return redirect('symptoms')
				except:
					if Assessment.objects.filter(purpose_id=purpose_pet_obj).exists:
						assessment=Assessment.objects.get(purpose_id=purpose_pet_obj)
						assessment_id=assessment.id
						if request.method=="POST":
							purpose_id=purpose_pet_obj
							DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
							EYES=request.POST.getlist('EYES')
							LUNGS=request.POST.getlist('LUNGS')
							EARS=request.POST.getlist('EARS')
							GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
							NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
							UROGENITAL=request.POST.getlist('UROGENITAL')
							MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
							MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
							HEART=request.POST.getlist('HEART')
							others=request.POST.get('others')
							Assessment.objects.filter(id=assessment_id).update(DERMATOLOGY=DERMATOLOGY,EYES=EYES,
							LUNGS=LUNGS,EARS=EARS,GASTROINTESTINAL=GASTROINTESTINAL,NOSE_THROAT=NOSE_THROAT,UROGENITAL=UROGENITAL,
							MOUTH_TEETH_GUMS=MOUTH_TEETH_GUMS,MUSKULOSKELETAL=MUSKULOSKELETAL,HEART=HEART,others=others)
							return redirect('symptoms')
			elif 'vitals_name' in request.POST:
				try:
					assessment=Assessment()
					assessment.purpose_id=purpose_pet_obj
					assessment.DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
					assessment.EYES=request.POST.getlist('EYES')
					assessment.LUNGS=request.POST.getlist('LUNGS')
					assessment.EARS=request.POST.getlist('EARS')
					assessment.GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
					assessment.NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
					assessment.UROGENITAL=request.POST.getlist('UROGENITAL')
					assessment.MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
					assessment.MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
					assessment.HEART=request.POST.getlist('HEART')
					assessment.others=request.POST.get('others')
					assessment.save()
					return redirect('vitals')
				except:
					if Assessment.objects.filter(purpose_id=purpose_pet_obj).exists:
						assessment=Assessment.objects.get(purpose_id=purpose_pet_obj)
						assessment_id=assessment.id
						if request.method=="POST":
							purpose_id=purpose_pet_obj
							DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
							EYES=request.POST.getlist('EYES')
							LUNGS=request.POST.getlist('LUNGS')
							EARS=request.POST.getlist('EARS')
							GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
							NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
							UROGENITAL=request.POST.getlist('UROGENITAL')
							MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
							MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
							HEART=request.POST.getlist('HEART')
							others=request.POST.get('others')
							Assessment.objects.filter(id=assessment_id).update(DERMATOLOGY=DERMATOLOGY,EYES=EYES,
							LUNGS=LUNGS,EARS=EARS,GASTROINTESTINAL=GASTROINTESTINAL,NOSE_THROAT=NOSE_THROAT,UROGENITAL=UROGENITAL,
							MOUTH_TEETH_GUMS=MOUTH_TEETH_GUMS,MUSKULOSKELETAL=MUSKULOSKELETAL,HEART=HEART,others=others)
							return redirect('vitals')
			elif 'diagnostic_name' in request.POST:
				try:
					assessment=Assessment()
					assessment.purpose_id=purpose_pet_obj
					assessment.DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
					assessment.EYES=request.POST.getlist('EYES')
					assessment.LUNGS=request.POST.getlist('LUNGS')
					assessment.EARS=request.POST.getlist('EARS')
					assessment.GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
					assessment.NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
					assessment.UROGENITAL=request.POST.getlist('UROGENITAL')
					assessment.MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
					assessment.MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
					assessment.HEART=request.POST.getlist('HEART')
					assessment.others=request.POST.get('others')
					assessment.save()
					return redirect('diagnostic_prescription')
				except:
					if Assessment.objects.filter(purpose_id=purpose_pet_obj).exists:
						assessment=Assessment.objects.get(purpose_id=purpose_pet_obj)
						assessment_id=assessment.id
						if request.method=="POST":
							purpose_id=purpose_pet_obj
							DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
							EYES=request.POST.getlist('EYES')
							LUNGS=request.POST.getlist('LUNGS')
							EARS=request.POST.getlist('EARS')
							GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
							NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
							UROGENITAL=request.POST.getlist('UROGENITAL')
							MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
							MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
							HEART=request.POST.getlist('HEART')
							others=request.POST.get('others')
							Assessment.objects.filter(id=assessment_id).update(DERMATOLOGY=DERMATOLOGY,EYES=EYES,
							LUNGS=LUNGS,EARS=EARS,GASTROINTESTINAL=GASTROINTESTINAL,NOSE_THROAT=NOSE_THROAT,UROGENITAL=UROGENITAL,
							MOUTH_TEETH_GUMS=MOUTH_TEETH_GUMS,MUSKULOSKELETAL=MUSKULOSKELETAL,HEART=HEART,others=others)
							return redirect('diagnostic_prescription')
			elif 'prescription_name' in request.POST:
				try:
					assessment=Assessment()
					assessment.purpose_id=purpose_pet_obj
					assessment.DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
					assessment.EYES=request.POST.getlist('EYES')
					assessment.LUNGS=request.POST.getlist('LUNGS')
					assessment.EARS=request.POST.getlist('EARS')
					assessment.GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
					assessment.NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
					assessment.UROGENITAL=request.POST.getlist('UROGENITAL')
					assessment.MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
					assessment.MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
					assessment.HEART=request.POST.getlist('HEART')
					assessment.others=request.POST.get('others')
					assessment.save()
					return redirect('prescription')
				except:
					if Assessment.objects.filter(purpose_id=purpose_pet_obj).exists:
						assessment=Assessment.objects.get(purpose_id=purpose_pet_obj)
						assessment_id=assessment.id
						if request.method=="POST":
							purpose_id=purpose_pet_obj
							DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
							EYES=request.POST.getlist('EYES')
							LUNGS=request.POST.getlist('LUNGS')
							EARS=request.POST.getlist('EARS')
							GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
							NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
							UROGENITAL=request.POST.getlist('UROGENITAL')
							MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
							MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
							HEART=request.POST.getlist('HEART')
							others=request.POST.get('others')
							Assessment.objects.filter(id=assessment_id).update(DERMATOLOGY=DERMATOLOGY,EYES=EYES,
							LUNGS=LUNGS,EARS=EARS,GASTROINTESTINAL=GASTROINTESTINAL,NOSE_THROAT=NOSE_THROAT,UROGENITAL=UROGENITAL,
							MOUTH_TEETH_GUMS=MOUTH_TEETH_GUMS,MUSKULOSKELETAL=MUSKULOSKELETAL,HEART=HEART,others=others)
							return redirect('prescription')
			elif 'vaccination_name' in request.POST:
				try:
					assessment=Assessment()
					assessment.purpose_id=purpose_pet_obj
					assessment.DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
					assessment.EYES=request.POST.getlist('EYES')
					assessment.LUNGS=request.POST.getlist('LUNGS')
					assessment.EARS=request.POST.getlist('EARS')
					assessment.GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
					assessment.NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
					assessment.UROGENITAL=request.POST.getlist('UROGENITAL')
					assessment.MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
					assessment.MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
					assessment.HEART=request.POST.getlist('HEART')
					assessment.others=request.POST.get('others')
					assessment.save()
					return redirect('vaccination')
				except:
					if Assessment.objects.filter(purpose_id=purpose_pet_obj).exists:
						assessment=Assessment.objects.get(purpose_id=purpose_pet_obj)
						assessment_id=assessment.id
						if request.method=="POST":
							purpose_id=purpose_pet_obj
							DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
							EYES=request.POST.getlist('EYES')
							LUNGS=request.POST.getlist('LUNGS')
							EARS=request.POST.getlist('EARS')
							GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
							NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
							UROGENITAL=request.POST.getlist('UROGENITAL')
							MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
							MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
							HEART=request.POST.getlist('HEART')
							others=request.POST.get('others')
							Assessment.objects.filter(id=assessment_id).update(DERMATOLOGY=DERMATOLOGY,EYES=EYES,
							LUNGS=LUNGS,EARS=EARS,GASTROINTESTINAL=GASTROINTESTINAL,NOSE_THROAT=NOSE_THROAT,UROGENITAL=UROGENITAL,
							MOUTH_TEETH_GUMS=MOUTH_TEETH_GUMS,MUSKULOSKELETAL=MUSKULOSKELETAL,HEART=HEART,others=others)
							return redirect('vaccination')
			elif 'deworming_name' in request.POST:
				try:
					assessment=Assessment()
					assessment.purpose_id=purpose_pet_obj
					assessment.DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
					assessment.EYES=request.POST.getlist('EYES')
					assessment.LUNGS=request.POST.getlist('LUNGS')
					assessment.EARS=request.POST.getlist('EARS')
					assessment.GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
					assessment.NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
					assessment.UROGENITAL=request.POST.getlist('UROGENITAL')
					assessment.MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
					assessment.MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
					assessment.HEART=request.POST.getlist('HEART')
					assessment.others=request.POST.get('others')
					assessment.save()
					return redirect('deworming')
				except:
					if Assessment.objects.filter(purpose_id=purpose_pet_obj).exists:
						assessment=Assessment.objects.get(purpose_id=purpose_pet_obj)
						assessment_id=assessment.id
						if request.method=="POST":
							purpose_id=purpose_pet_obj
							DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
							EYES=request.POST.getlist('EYES')
							LUNGS=request.POST.getlist('LUNGS')
							EARS=request.POST.getlist('EARS')
							GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
							NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
							UROGENITAL=request.POST.getlist('UROGENITAL')
							MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
							MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
							HEART=request.POST.getlist('HEART')
							others=request.POST.get('others')
							Assessment.objects.filter(id=assessment_id).update(DERMATOLOGY=DERMATOLOGY,EYES=EYES,
							LUNGS=LUNGS,EARS=EARS,GASTROINTESTINAL=GASTROINTESTINAL,NOSE_THROAT=NOSE_THROAT,UROGENITAL=UROGENITAL,
							MOUTH_TEETH_GUMS=MOUTH_TEETH_GUMS,MUSKULOSKELETAL=MUSKULOSKELETAL,HEART=HEART,others=others)
							return redirect('deworming')
			elif 'close_visit' in request.POST:
				try:
					assessment=Assessment()
					assessment.purpose_id=purpose_pet_obj
					assessment.DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
					assessment.EYES=request.POST.getlist('EYES')
					assessment.LUNGS=request.POST.getlist('LUNGS')
					assessment.EARS=request.POST.getlist('EARS')
					assessment.GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
					assessment.NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
					assessment.UROGENITAL=request.POST.getlist('UROGENITAL')
					assessment.MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
					assessment.MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
					assessment.HEART=request.POST.getlist('HEART')
					assessment.others=request.POST.get('others')
					assessment.save()
					if Doctor.objects.get(id=doc_pk).stock_management=='yes':
						if Prescription.objects.filter(purpose_id=purpose_id).exists():
							medicine1_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_name
							medicine1_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_quantity
							medicine2_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_name
							medicine2_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_quantity
							medicine3_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_name
							medicine3_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_quantity
							medicine4_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_name
							medicine4_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_quantity
							medicine5_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_name
							medicine5_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_quantity
							medicine6_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_name
							medicine6_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_quantity
							if stock.objects.filter(doctor__id=doc_id,medicine=medicine1_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_id,medicine=medicine1_name).last().quantity
								present_quantity=medicine1_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).last().quantity
								present_quantity=medicine2_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								print(reduced_quantity)
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).last().quantity
								present_quantity=medicine3_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).last().quantity
								present_quantity=medicine4_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).last().quantity
								present_quantity=medicine5_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).last().quantity
								present_quantity=medicine6_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).update(quantity=reduced_quantity)
						else:
							pass
					return redirect('summary')
				except:
					if Assessment.objects.filter(purpose_id=purpose_pet_obj).exists:
						assessment=Assessment.objects.get(purpose_id=purpose_pet_obj)
						assessment_id=assessment.id
						if request.method=="POST":
							purpose_id=purpose_pet_obj
							DERMATOLOGY=request.POST.getlist('DERMATOLOGY')
							EYES=request.POST.getlist('EYES')
							LUNGS=request.POST.getlist('LUNGS')
							EARS=request.POST.getlist('EARS')
							GASTROINTESTINAL=request.POST.getlist('GASTROINTESTINAL')
							NOSE_THROAT=request.POST.getlist('NOSE_THROAT')
							UROGENITAL=request.POST.getlist('UROGENITAL')
							MOUTH_TEETH_GUMS=request.POST.getlist('MOUTH_TEETH_GUMS')
							MUSKULOSKELETAL=request.POST.getlist('MUSKULOSKELETAL')
							HEART=request.POST.getlist('HEART')
							others=request.POST.get('others')
							Assessment.objects.filter(id=assessment_id).update(DERMATOLOGY=DERMATOLOGY,EYES=EYES,
							LUNGS=LUNGS,EARS=EARS,GASTROINTESTINAL=GASTROINTESTINAL,NOSE_THROAT=NOSE_THROAT,UROGENITAL=UROGENITAL,
							MOUTH_TEETH_GUMS=MOUTH_TEETH_GUMS,MUSKULOSKELETAL=MUSKULOSKELETAL,HEART=HEART,others=others)
							if Doctor.objects.get(id=doc_pk).stock_management=='yes':
								if Prescription.objects.filter(purpose_id=purpose_id).exists():
									medicine1_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_name
									medicine1_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_quantity
									medicine2_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_name
									medicine2_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_quantity
									medicine3_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_name
									medicine3_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_quantity
									medicine4_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_name
									medicine4_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_quantity
									medicine5_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_name
									medicine5_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_quantity
									medicine6_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_name
									medicine6_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_quantity
									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).last().quantity
										present_quantity=medicine1_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).last().quantity
										present_quantity=medicine2_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										print(reduced_quantity)
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).last().quantity
										present_quantity=medicine3_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).last().quantity
										present_quantity=medicine4_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).last().quantity
										present_quantity=medicine5_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).last().quantity
										present_quantity=medicine6_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).update(quantity=reduced_quantity)
								else:
									pass
			return redirect('summary')

def diagnostic(request):
	doc_pk = request.session.get('doc_pk')
	pet_pk = request.session.get('pet_pk')
	purpose_pk = request.session.get('purpose_pk')
	pet_obj=Pet.objects.filter(id=pet_pk).last()
	pet_obj=pet_age_converter_single(pet_obj)
	purpose_pet_obj_diet=PurposeAndDiet.objects.filter(id=purpose_pk).last()
	purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
	doc_pk_stock=Doctor.objects.get(id=doc_pk)
	try:
		x=Diagnostics.objects.filter(purpose_id=purpose_pet_obj).last()
		x=model_to_dict(x)
	except:
		pass
	if request.method == "GET":
		if 'doc_pk' in request.session:
			return render(request,'doctor/Doctor_diagnostics_and_prescription.html',
			{'pet_obj':pet_obj,'purpose_pet_obj':purpose_pet_obj,
			'purpose_pet_obj_diet':purpose_pet_obj_diet,
			'doc_pk':doc_pk,'pet_pk':pet_pk,'purpose_pk':purpose_pk,
			'x':x,'doc_pk_stock':doc_pk_stock})
		else:
			return redirect('doctor_login')

	if request.method=='POST':
		if 'symptoms_name' in request.POST:
			try:

				purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
				diagnostic=Diagnostics()
				diagnostic.purpose_id=purpose_pet_obj
				diagnostic.haematology=request.POST.getlist('haematology')
				diagnostic.biochemistry=request.POST.getlist('biochemistry')
				diagnostic.harmones=request.POST.getlist('harmones')
				diagnostic.microbiology=request.POST.getlist('microbiology')
				diagnostic.parasitology=request.POST.getlist('parasitology')
				diagnostic.serology=request.POST.getlist('serology')
				diagnostic.cytology=request.POST.getlist('cytology')
				diagnostic.rapid_test=request.POST.getlist('rapid test')
				diagnostic.radiology=request.POST.getlist('radiology')
				diagnostic.others=request.POST.get('others')
				diagnostic.save()

				return redirect('symptoms')
			except:
				if Diagnostics.objects.filter(purpose_id=purpose_pet_obj).exists :
					diagnostic_id=Diagnostics.objects.get(purpose_id=purpose_pet_obj).id
					if request.method=='POST':
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						diagnostic=Diagnostics()
						purpose_id=purpose_pet_obj
						haematology=request.POST.getlist('haematology')
						biochemistry=request.POST.getlist('biochemistry')
						harmones=request.POST.getlist('harmones')
						microbiology=request.POST.getlist('microbiology')
						parasitology=request.POST.getlist('parasitology')
						serology=request.POST.getlist('serology')
						cytology=request.POST.getlist('cytology')
						rapid_test=request.POST.getlist('rapid test')
						radiology=request.POST.getlist('radiology')
						others=request.POST.get('others')

						Diagnostics.objects.filter(id=diagnostic_id).update(haematology=haematology,biochemistry=biochemistry,
						harmones=harmones,microbiology=microbiology,parasitology=parasitology,serology=serology,cytology=cytology,
						rapid_test=rapid_test,others=others,radiology=radiology)
						return redirect('symptoms')
		elif 'assessment_name' in request.POST:
			try:

				purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
				diagnostic=Diagnostics()
				diagnostic.purpose_id=purpose_pet_obj
				diagnostic.haematology=request.POST.getlist('haematology')
				diagnostic.biochemistry=request.POST.getlist('biochemistry')
				diagnostic.harmones=request.POST.getlist('harmones')
				diagnostic.microbiology=request.POST.getlist('microbiology')
				diagnostic.parasitology=request.POST.getlist('parasitology')
				diagnostic.serology=request.POST.getlist('serology')
				diagnostic.cytology=request.POST.getlist('cytology')
				diagnostic.rapid_test=request.POST.getlist('rapid test')
				diagnostic.radiology=request.POST.getlist('radiology')
				diagnostic.others=request.POST.get('others')
				diagnostic.save()

				return redirect('assessment')
			except:
				if Diagnostics.objects.filter(purpose_id=purpose_pet_obj).exists :
					diagnostic_id=Diagnostics.objects.get(purpose_id=purpose_pet_obj).id
					if request.method=='POST':
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						diagnostic=Diagnostics()
						purpose_id=purpose_pet_obj
						haematology=request.POST.getlist('haematology')
						biochemistry=request.POST.getlist('biochemistry')
						harmones=request.POST.getlist('harmones')
						microbiology=request.POST.getlist('microbiology')
						parasitology=request.POST.getlist('parasitology')
						serology=request.POST.getlist('serology')
						cytology=request.POST.getlist('cytology')
						rapid_test=request.POST.getlist('rapid test')
						radiology=request.POST.getlist('radiology')
						others=request.POST.get('others')

						Diagnostics.objects.filter(id=diagnostic_id).update(haematology=haematology,biochemistry=biochemistry,
						harmones=harmones,microbiology=microbiology,parasitology=parasitology,serology=serology,cytology=cytology,
						rapid_test=rapid_test,others=others,radiology=radiology)
						return redirect('assessment')
		elif 'vitals_name' in request.POST:
			try:

				purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
				diagnostic=Diagnostics()
				diagnostic.purpose_id=purpose_pet_obj
				diagnostic.haematology=request.POST.getlist('haematology')
				diagnostic.biochemistry=request.POST.getlist('biochemistry')
				diagnostic.harmones=request.POST.getlist('harmones')
				diagnostic.microbiology=request.POST.getlist('microbiology')
				diagnostic.parasitology=request.POST.getlist('parasitology')
				diagnostic.serology=request.POST.getlist('serology')
				diagnostic.cytology=request.POST.getlist('cytology')
				diagnostic.rapid_test=request.POST.getlist('rapid test')
				diagnostic.radiology=request.POST.getlist('radiology')
				diagnostic.others=request.POST.get('others')
				diagnostic.save()

				return redirect('vitals')
			except:
				if Diagnostics.objects.filter(purpose_id=purpose_pet_obj).exists :
					diagnostic_id=Diagnostics.objects.get(purpose_id=purpose_pet_obj).id
					if request.method=='POST':
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						diagnostic=Diagnostics()
						purpose_id=purpose_pet_obj
						haematology=request.POST.getlist('haematology')
						biochemistry=request.POST.getlist('biochemistry')
						harmones=request.POST.getlist('harmones')
						microbiology=request.POST.getlist('microbiology')
						parasitology=request.POST.getlist('parasitology')
						serology=request.POST.getlist('serology')
						cytology=request.POST.getlist('cytology')
						rapid_test=request.POST.getlist('rapid test')
						radiology=request.POST.getlist('radiology')
						others=request.POST.get('others')

						Diagnostics.objects.filter(id=diagnostic_id).update(haematology=haematology,biochemistry=biochemistry,
						harmones=harmones,microbiology=microbiology,parasitology=parasitology,serology=serology,cytology=cytology,
						rapid_test=rapid_test,others=others,radiology=radiology)
						return redirect('vitals')
		elif 'prescription_name' in request.POST:
			try:

				purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
				diagnostic=Diagnostics()
				diagnostic.purpose_id=purpose_pet_obj
				diagnostic.haematology=request.POST.getlist('haematology')
				diagnostic.biochemistry=request.POST.getlist('biochemistry')
				diagnostic.harmones=request.POST.getlist('harmones')
				diagnostic.microbiology=request.POST.getlist('microbiology')
				diagnostic.parasitology=request.POST.getlist('parasitology')
				diagnostic.serology=request.POST.getlist('serology')
				diagnostic.cytology=request.POST.getlist('cytology')
				diagnostic.rapid_test=request.POST.getlist('rapid test')
				diagnostic.radiology=request.POST.getlist('radiology')
				diagnostic.others=request.POST.get('others')
				diagnostic.save()

				return redirect('prescription')
			except:
				if Diagnostics.objects.filter(purpose_id=purpose_pet_obj).exists :
					diagnostic_id=Diagnostics.objects.get(purpose_id=purpose_pet_obj).id
					if request.method=='POST':
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						diagnostic=Diagnostics()
						purpose_id=purpose_pet_obj
						haematology=request.POST.getlist('haematology')
						biochemistry=request.POST.getlist('biochemistry')
						harmones=request.POST.getlist('harmones')
						microbiology=request.POST.getlist('microbiology')
						parasitology=request.POST.getlist('parasitology')
						serology=request.POST.getlist('serology')
						cytology=request.POST.getlist('cytology')
						rapid_test=request.POST.getlist('rapid test')
						radiology=request.POST.getlist('radiology')
						others=request.POST.get('others')

						Diagnostics.objects.filter(id=diagnostic_id).update(haematology=haematology,biochemistry=biochemistry,
						harmones=harmones,microbiology=microbiology,parasitology=parasitology,serology=serology,cytology=cytology,
						rapid_test=rapid_test,others=others,radiology=radiology)
						return redirect('prescription')
		elif 'vaccination_name' in request.POST:
			try:

				purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
				diagnostic=Diagnostics()
				diagnostic.purpose_id=purpose_pet_obj
				diagnostic.haematology=request.POST.getlist('haematology')
				diagnostic.biochemistry=request.POST.getlist('biochemistry')
				diagnostic.harmones=request.POST.getlist('harmones')
				diagnostic.microbiology=request.POST.getlist('microbiology')
				diagnostic.parasitology=request.POST.getlist('parasitology')
				diagnostic.serology=request.POST.getlist('serology')
				diagnostic.cytology=request.POST.getlist('cytology')
				diagnostic.rapid_test=request.POST.getlist('rapid test')
				diagnostic.radiology=request.POST.getlist('radiology')
				diagnostic.others=request.POST.get('others')
				diagnostic.save()

				return redirect('vaccination')
			except:
				if Diagnostics.objects.filter(purpose_id=purpose_pet_obj).exists :
					diagnostic_id=Diagnostics.objects.get(purpose_id=purpose_pet_obj).id
					if request.method=='POST':
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						diagnostic=Diagnostics()
						purpose_id=purpose_pet_obj
						haematology=request.POST.getlist('haematology')
						biochemistry=request.POST.getlist('biochemistry')
						harmones=request.POST.getlist('harmones')
						microbiology=request.POST.getlist('microbiology')
						parasitology=request.POST.getlist('parasitology')
						serology=request.POST.getlist('serology')
						cytology=request.POST.getlist('cytology')
						rapid_test=request.POST.getlist('rapid test')
						radiology=request.POST.getlist('radiology')
						others=request.POST.get('others')

						Diagnostics.objects.filter(id=diagnostic_id).update(haematology=haematology,biochemistry=biochemistry,
						harmones=harmones,microbiology=microbiology,parasitology=parasitology,serology=serology,cytology=cytology,
						rapid_test=rapid_test,others=others,radiology=radiology)
						return redirect('vaccination')
		elif 'deworming_name' in request.POST:
			try:

				purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
				diagnostic=Diagnostics()
				diagnostic.purpose_id=purpose_pet_obj
				diagnostic.haematology=request.POST.getlist('haematology')
				diagnostic.biochemistry=request.POST.getlist('biochemistry')
				diagnostic.harmones=request.POST.getlist('harmones')
				diagnostic.microbiology=request.POST.getlist('microbiology')
				diagnostic.parasitology=request.POST.getlist('parasitology')
				diagnostic.serology=request.POST.getlist('serology')
				diagnostic.cytology=request.POST.getlist('cytology')
				diagnostic.rapid_test=request.POST.getlist('rapid test')
				diagnostic.radiology=request.POST.getlist('radiology')
				diagnostic.others=request.POST.get('others')
				diagnostic.save()

				return redirect('deworming')
			except:
				if Diagnostics.objects.filter(purpose_id=purpose_pet_obj).exists :
					diagnostic_id=Diagnostics.objects.get(purpose_id=purpose_pet_obj).id
					if request.method=='POST':
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						diagnostic=Diagnostics()
						purpose_id=purpose_pet_obj
						haematology=request.POST.getlist('haematology')
						biochemistry=request.POST.getlist('biochemistry')
						harmones=request.POST.getlist('harmones')
						microbiology=request.POST.getlist('microbiology')
						parasitology=request.POST.getlist('parasitology')
						serology=request.POST.getlist('serology')
						cytology=request.POST.getlist('cytology')
						rapid_test=request.POST.getlist('rapid test')
						radiology=request.POST.getlist('radiology')
						others=request.POST.get('others')

						Diagnostics.objects.filter(id=diagnostic_id).update(haematology=haematology,biochemistry=biochemistry,
						harmones=harmones,microbiology=microbiology,parasitology=parasitology,serology=serology,cytology=cytology,
						rapid_test=rapid_test,others=others,radiology=radiology)
						return redirect('deworming')
		elif 'close_visit' in request.POST:

			try:

				purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
				diagnostic=Diagnostics()
				diagnostic.purpose_id=purpose_pet_obj
				diagnostic.haematology=request.POST.getlist('haematology')
				diagnostic.biochemistry=request.POST.getlist('biochemistry')
				diagnostic.harmones=request.POST.getlist('harmones')
				diagnostic.microbiology=request.POST.getlist('microbiology')
				diagnostic.parasitology=request.POST.getlist('parasitology')
				diagnostic.serology=request.POST.getlist('serology')
				diagnostic.cytology=request.POST.getlist('cytology')
				diagnostic.rapid_test=request.POST.getlist('rapid test')
				diagnostic.radiology=request.POST.getlist('radiology')
				diagnostic.others=request.POST.get('others')
				diagnostic.save()
				if Doctor.objects.get(id=doc_pk).stock_management=='yes':
						if Prescription.objects.filter(purpose_id=purpose_id).exists():
							medicine1_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_name
							medicine1_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_quantity
							medicine2_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_name
							medicine2_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_quantity
							medicine3_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_name
							medicine3_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_quantity
							medicine4_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_name
							medicine4_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_quantity
							medicine5_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_name
							medicine5_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_quantity
							medicine6_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_name
							medicine6_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_quantity
							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).last().quantity
								present_quantity=medicine1_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).last().quantity
								present_quantity=medicine2_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								print(reduced_quantity)
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).last().quantity
								present_quantity=medicine3_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).last().quantity
								present_quantity=medicine4_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).last().quantity
								present_quantity=medicine5_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).last().quantity
								present_quantity=medicine6_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).update(quantity=reduced_quantity)
						else:
							pass

				return redirect('summary')
			except:
				if Diagnostics.objects.filter(purpose_id=purpose_pet_obj).exists :
					diagnostic_id=Diagnostics.objects.get(purpose_id=purpose_pet_obj).id
					if request.method=='POST':
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						diagnostic=Diagnostics()
						purpose_id=purpose_pet_obj
						haematology=request.POST.getlist('haematology')
						biochemistry=request.POST.getlist('biochemistry')
						harmones=request.POST.getlist('harmones')
						microbiology=request.POST.getlist('microbiology')
						parasitology=request.POST.getlist('parasitology')
						serology=request.POST.getlist('serology')
						cytology=request.POST.getlist('cytology')
						rapid_test=request.POST.getlist('rapid test')
						radiology=request.POST.getlist('radiology')
						others=request.POST.get('others')

						Diagnostics.objects.filter(id=diagnostic_id).update(haematology=haematology,biochemistry=biochemistry,
						harmones=harmones,microbiology=microbiology,parasitology=parasitology,serology=serology,cytology=cytology,
						rapid_test=rapid_test,others=others,radiology=radiology)
						if Doctor.objects.get(id=doc_pk).stock_management=='yes':
								if Prescription.objects.filter(purpose_id=purpose_id).exists():
									medicine1_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_name
									medicine1_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine1_quantity
									medicine2_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_name
									medicine2_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine2_quantity
									medicine3_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_name
									medicine3_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine3_quantity
									medicine4_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_name
									medicine4_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine4_quantity
									medicine5_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_name
									medicine5_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine5_quantity
									medicine6_name=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_name
									medicine6_quantity=Prescription.objects.filter(purpose_id=purpose_id).last().medicine6_quantity
									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).last().quantity
										present_quantity=medicine1_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).last().quantity
										present_quantity=medicine2_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										print(reduced_quantity)
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).last().quantity
										present_quantity=medicine3_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).last().quantity
										present_quantity=medicine4_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).last().quantity
										present_quantity=medicine5_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).update(quantity=reduced_quantity)

									if stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).exists():
										quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).last().quantity
										present_quantity=medicine6_quantity
										quantity=int(quantity)
										present_quantity=int(present_quantity)
										reduced_quantity=quantity-present_quantity
										if reduced_quantity<=0:
											reduced_quantity=0
										else:
											reduced_quantity=reduced_quantity
										stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).update(quantity=reduced_quantity)
								else:
									pass


						return redirect('summary')


		else:
			return redirect('diagnostic_prescription')

def prescription(request):
	doc_pk = request.session.get('doc_pk')
	pet_pk = request.session.get('pet_pk')
	purpose_pk = request.session.get('purpose_pk')
	stock_management_check=Doctor.objects.get(id=doc_pk).stock_management #check for stock option
	if stock_management_check=='yes':
		pet_obj=Pet.objects.filter(id=pet_pk).last()
		pet_obj=pet_age_converter_single(pet_obj)
		purpose_pet_obj_diet=PurposeAndDiet.objects.filter(id=purpose_pk).last()
		purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
		st=stock.objects.filter(doctor__id=doc_pk)
		doc_pk_stock=Doctor.objects.get(id=doc_pk)
		try:
			x=Prescription.objects.filter(purpose_id=purpose_pet_obj).last()
			val=x.followup_date
			unt=x.followup_date_unit
			reverse_date_num = prescription_date_format_reverse(val,unt)
			x=model_to_dict(x)
		except :
			reverse_date_num = None
			unt = ''

		if request.method == "GET":
			if 'doc_pk' in request.session:
				return render(request,'doctor/doctor_prescription.html',
				{'pet_obj':pet_obj,'purpose_pet_obj':purpose_pet_obj,
				'doc_pk_stock':doc_pk_stock,'doc_pk':doc_pk,'st':st,
				'purpose_pet_obj_diet':purpose_pet_obj_diet,'pet_pk':pet_pk,
				'purpose_pk':purpose_pk,'x':x,'unt':unt,
				'reverse_date_num':reverse_date_num})
			else:
				return redirect('doctor_login')

		if request.method=='POST':
			if 'assessment_name' in request.POST:
				try:
					#if prescription data exists in prescription table
					if Prescription.objects.filter(purpose_id=purpose_pet_obj).exists() :

						if request.method=='POST':
							Prescription.objects.filter(purpose_id=purpose_pet_obj).delete()
							purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
							prescription=Prescription()
							prescription.purpose_id=purpose_pet_obj

							#for medicine 1
							medicine1=request.POST.get('medicine1')
							medicine1_time=request.POST.get('medicine1_time')
							medicine1_days=request.POST.get('medicine1_days')
							medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
							if medicine1=='':
								pass
							else:
								prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
								prescription.medicine1_quantity=medicine1_quantity

							#for medicine 2
							medicine2=request.POST.get('medicine2')
							medicine2_time=request.POST.get('medicine2_time')
							medicine2_days=request.POST.get('medicine2_days')
							medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
							if medicine2=='':
								pass
							else:
								prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
								prescription.medicine2_quantity=medicine2_quantity

							#for medicine 3
							medicine3=request.POST.get('medicine3')
							medicine3_time=request.POST.get('medicine3_time')
							medicine3_days=request.POST.get('medicine3_days')
							medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
							if medicine3=='':
								pass
							else:
								prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
								prescription.medicine3_quantity=medicine3_quantity

							#for medicine 4
							medicine4=request.POST.get('medicine4')
							medicine4_time=request.POST.get('medicine4_time')
							medicine4_days=request.POST.get('medicine4_days')
							medicine4_quantity=count_quantity(medicine4_days,medicine4_time)

							if medicine4=='':
								pass
							else:
								prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
								prescription.medicine4_quantity=medicine4_quantity

							#for medicine 5
							medicine5=request.POST.get('medicine5')
							medicine5_time=request.POST.get('medicine5_time')
							medicine5_days=request.POST.get('medicine5_days')
							medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
							if medicine5=='':
								pass
							else:
								prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
								prescription.medicine5_quantity=medicine5_quantity
							#for medicine 6
							medicine6=request.POST.get('medicine6')
							medicine6_time=request.POST.get('medicine6_time')
							medicine6_days=request.POST.get('medicine6_days')
							medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
							if medicine6=='':
								pass
							else:
								prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
								prescription.medicine6_quantity=medicine6_quantity

							medicine_other=request.POST.get('medicine_other')
							if medicine_other=='':
								pass
							else:
								prescription.medicine_other=request.POST.get('medicine_other')
							prescription.medicine1_name=request.POST.get('medicine1')
							prescription.medicine2_name=request.POST.get('medicine2')
							prescription.medicine3_name=request.POST.get('medicine3')
							prescription.medicine4_name=request.POST.get('medicine4')
							prescription.medicine5_name=request.POST.get('medicine5')
							prescription.medicine6_name=request.POST.get('medicine6')

							#image saving
							prescription.Prescription_img=request.FILES.get('file')
							#follwup_date
							follow_up_date=request.POST.get('followup_date')
							followup_date_unit = request.POST.get('followup_date_unit')
							if follow_up_date == '':
								follow_up_date = None
							prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
							prescription.followup_date_unit = followup_date_unit
							prescription.followup_date = prescription_followup_date
							prescription.save()
							medicine_other=request.POST.get('medicine_other')
							medicine1_name=request.POST.get('medicine1')
							medicine2_name=request.POST.get('medicine2')
							medicine3_name=request.POST.get('medicine3')
							medicine4_name=request.POST.get('medicine4')
							medicine5_name=request.POST.get('medicine5')
							medicine6_name=request.POST.get('medicine6')
							return redirect('assessment')
					else:
						#if object is not existed in prescription database
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						prescription=Prescription()
						prescription.purpose_id=purpose_pet_obj

						#for medicine 1
						medicine1=request.POST.get('medicine1')
						medicine1_time=request.POST.get('medicine1_time')
						medicine1_days=request.POST.get('medicine1_days')
						medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
						if medicine1=='':
							pass
						else:
							prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
							prescription.medicine1_quantity=medicine1_quantity

						#for medicine 2
						medicine2=request.POST.get('medicine2')
						medicine2_time=request.POST.get('medicine2_time')
						medicine2_days=request.POST.get('medicine2_days')
						medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
						if medicine2=='':
							pass
						else:
							prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
							prescription.medicine2_quantity=medicine2_quantity

						#for medicine 3
						medicine3=request.POST.get('medicine3')
						medicine3_time=request.POST.get('medicine3_time')
						medicine3_days=request.POST.get('medicine3_days')
						medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
						if medicine3=='':
							pass
						else:
							prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
							prescription.medicine3_quantity=medicine3_quantity

						#for medicine 4
						medicine4=request.POST.get('medicine4')
						medicine4_time=request.POST.get('medicine4_time')
						medicine4_days=request.POST.get('medicine4_days')
						medicine4_quantity=count_quantity(medicine4_days,medicine4_time)
						if medicine4=='':
							pass
						else:
							prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
							prescription.medicine4_quantity=medicine4_quantity

						#for medicine 5
						medicine5=request.POST.get('medicine5')
						medicine5_time=request.POST.get('medicine5_time')
						medicine5_days=request.POST.get('medicine5_days')
						medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
						if medicine5=='':
							pass
						else:
							prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
							prescription.medicine5_quantity=medicine5_quantity
						#for medicine 6
						medicine6=request.POST.get('medicine6')
						medicine6_time=request.POST.get('medicine6_time')
						medicine6_days=request.POST.get('medicine6_days')
						medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
						if medicine6=='':
							pass
						else:
							prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
							prescription.medicine6_quantity=medicine6_quantity

						medicine_other=request.POST.get('medicine_other')
						if medicine_other=='':
							pass
						else:
							prescription.medicine_other=request.POST.get('medicine_other')
						prescription.medicine1_name=request.POST.get('medicine1')
						prescription.medicine2_name=request.POST.get('medicine2')
						prescription.medicine3_name=request.POST.get('medicine3')
						prescription.medicine4_name=request.POST.get('medicine4')
						prescription.medicine5_name=request.POST.get('medicine5')
						prescription.medicine6_name=request.POST.get('medicine6')

						#image saving
						prescription.Prescription_img=request.FILES.get('file')
						#follwup_date
						follow_up_date=request.POST.get('followup_date')
						followup_date_unit = request.POST.get('followup_date_unit')
						if follow_up_date == '':
							follow_up_date = None
						prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
						prescription.followup_date_unit = followup_date_unit
						prescription.followup_date = prescription_followup_date
						prescription.save()
						return redirect('assessment')
				except IntegrityError :
					messages.info(request,'select medicine and days')
					return redirect('prescription',)
			elif 'close_visit' in request.POST:
				try:
				#if prescription data exists in prescription table
					if Prescription.objects.filter(purpose_id=purpose_pet_obj).exists() :

						if request.method=='POST':
							Prescription.objects.filter(purpose_id=purpose_pet_obj).delete()
							purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
							prescription=Prescription()
							prescription.purpose_id=purpose_pet_obj

							#for medicine 1
							medicine1=request.POST.get('medicine1')
							medicine1_time=request.POST.get('medicine1_time')
							medicine1_days=request.POST.get('medicine1_days')
							medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
							if medicine1=='':
								pass
							else:
								prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
								prescription.medicine1_quantity=medicine1_quantity

							#for medicine 2
							medicine2=request.POST.get('medicine2')
							medicine2_time=request.POST.get('medicine2_time')
							medicine2_days=request.POST.get('medicine2_days')
							medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
							if medicine2=='':
								pass
							else:
								prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
								prescription.medicine2_quantity=medicine2_quantity

							#for medicine 3
							medicine3=request.POST.get('medicine3')
							medicine3_time=request.POST.get('medicine3_time')
							medicine3_days=request.POST.get('medicine3_days')
							medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
							if medicine3=='':
								pass
							else:
								prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
								prescription.medicine3_quantity=medicine3_quantity

							#for medicine 4
							medicine4=request.POST.get('medicine4')
							medicine4_time=request.POST.get('medicine4_time')
							medicine4_days=request.POST.get('medicine4_days')
							medicine4_quantity=count_quantity(medicine4_days,medicine4_time)

							if medicine4=='':
								pass
							else:
								prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
								prescription.medicine4_quantity=medicine4_quantity

							#for medicine 5
							medicine5=request.POST.get('medicine5')
							medicine5_time=request.POST.get('medicine5_time')
							medicine5_days=request.POST.get('medicine5_days')
							medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
							if medicine5=='':
								pass
							else:
								prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
								prescription.medicine5_quantity=medicine5_quantity
							#for medicine 6
							medicine6=request.POST.get('medicine6')
							medicine6_time=request.POST.get('medicine6_time')
							medicine6_days=request.POST.get('medicine6_days')
							medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
							if medicine6=='':
								pass
							else:
								prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
								prescription.medicine6_quantity=medicine6_quantity

							medicine_other=request.POST.get('medicine_other')
							if medicine_other=='':
								pass
							else:
								prescription.medicine_other=request.POST.get('medicine_other')
							prescription.medicine1_name=request.POST.get('medicine1')
							prescription.medicine2_name=request.POST.get('medicine2')
							prescription.medicine3_name=request.POST.get('medicine3')
							prescription.medicine4_name=request.POST.get('medicine4')
							prescription.medicine5_name=request.POST.get('medicine5')
							prescription.medicine6_name=request.POST.get('medicine6')

							#image saving
							prescription.Prescription_img=request.FILES.get('file')
							#follwup_date
							follow_up_date=request.POST.get('followup_date')
							followup_date_unit = request.POST.get('followup_date_unit')
							if follow_up_date == '':
								follow_up_date = None
							prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
							prescription.followup_date_unit = followup_date_unit
							prescription.followup_date = prescription_followup_date
							prescription.save()
							medicine_other=request.POST.get('medicine_other')
							medicine1_name=request.POST.get('medicine1')
							medicine2_name=request.POST.get('medicine2')
							medicine3_name=request.POST.get('medicine3')
							medicine4_name=request.POST.get('medicine4')
							medicine5_name=request.POST.get('medicine5')
							medicine6_name=request.POST.get('medicine6')

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).last().quantity
								present_quantity=medicine1_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).last().quantity
								present_quantity=medicine2_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								print(reduced_quantity)
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).last().quantity
								present_quantity=medicine3_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).last().quantity
								present_quantity=medicine4_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).last().quantity
								present_quantity=medicine5_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).update(quantity=reduced_quantity)

							if stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).exists():
								quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).last().quantity
								present_quantity=medicine6_quantity
								quantity=int(quantity)
								present_quantity=int(present_quantity)
								reduced_quantity=quantity-present_quantity
								if reduced_quantity<=0:
									reduced_quantity=0
								else:
									reduced_quantity=reduced_quantity
								stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).update(quantity=reduced_quantity)
							return redirect('summary')
					else:
						#if object is not existed in prescription database
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						prescription=Prescription()
						prescription.purpose_id=purpose_pet_obj

						#for medicine 1
						medicine1=request.POST.get('medicine1')
						medicine1_time=request.POST.get('medicine1_time')
						medicine1_days=request.POST.get('medicine1_days')
						medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
						if medicine1=='':
							pass
						else:
							prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
							prescription.medicine1_quantity=medicine1_quantity

						#for medicine 2
						medicine2=request.POST.get('medicine2')
						medicine2_time=request.POST.get('medicine2_time')
						medicine2_days=request.POST.get('medicine2_days')
						medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
						if medicine2=='':
							pass
						else:
							prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
							prescription.medicine2_quantity=medicine2_quantity

						#for medicine 3
						medicine3=request.POST.get('medicine3')
						medicine3_time=request.POST.get('medicine3_time')
						medicine3_days=request.POST.get('medicine3_days')
						medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
						if medicine3=='':
							pass
						else:
							prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
							prescription.medicine3_quantity=medicine3_quantity

						#for medicine 4
						medicine4=request.POST.get('medicine4')
						medicine4_time=request.POST.get('medicine4_time')
						medicine4_days=request.POST.get('medicine4_days')
						medicine4_quantity=count_quantity(medicine4_days,medicine4_time)
						if medicine4=='':
							pass
						else:
							prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
							prescription.medicine4_quantity=medicine4_quantity

						#for medicine 5
						medicine5=request.POST.get('medicine5')
						medicine5_time=request.POST.get('medicine5_time')
						medicine5_days=request.POST.get('medicine5_days')
						medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
						if medicine5=='':
							pass
						else:
							prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
							prescription.medicine5_quantity=medicine5_quantity
						#for medicine 6
						medicine6=request.POST.get('medicine6')
						medicine6_time=request.POST.get('medicine6_time')
						medicine6_days=request.POST.get('medicine6_days')
						medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
						if medicine6=='':
							pass
						else:
							prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
							prescription.medicine6_quantity=medicine6_quantity

						medicine_other=request.POST.get('medicine_other')
						if medicine_other=='':
							pass
						else:
							prescription.medicine_other=request.POST.get('medicine_other')
						prescription.medicine1_name=request.POST.get('medicine1')
						prescription.medicine2_name=request.POST.get('medicine2')
						prescription.medicine3_name=request.POST.get('medicine3')
						prescription.medicine4_name=request.POST.get('medicine4')
						prescription.medicine5_name=request.POST.get('medicine5')
						prescription.medicine6_name=request.POST.get('medicine6')

						#image saving
						prescription.Prescription_img=request.FILES.get('file')
						#follwup_date
						follow_up_date=request.POST.get('followup_date')
						followup_date_unit = request.POST.get('followup_date_unit')
						if follow_up_date == '':
							follow_up_date = None
						prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
						prescription.followup_date_unit = followup_date_unit
						prescription.followup_date = prescription_followup_date
						prescription.save()
						medicine_other=request.POST.get('medicine_other')
						medicine1_name=request.POST.get('medicine1')
						medicine2_name=request.POST.get('medicine2')
						medicine3_name=request.POST.get('medicine3')
						medicine4_name=request.POST.get('medicine4')
						medicine5_name=request.POST.get('medicine5')
						medicine6_name=request.POST.get('medicine6')

						if stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).last().quantity
							present_quantity=medicine1_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_pk,medicine=medicine1_name).update(quantity=reduced_quantity)
						else:
							pass

						if stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).last().quantity
							present_quantity=medicine2_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							print(reduced_quantity)
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_pk,medicine=medicine2_name).update(quantity=reduced_quantity)
						else:
							pass

						if stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).last().quantity
							present_quantity=medicine3_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_pk,medicine=medicine3_name).update(quantity=reduced_quantity)
						else:
							pass

						if stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).last().quantity
							present_quantity=medicine4_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_pk,medicine=medicine4_name).update(quantity=reduced_quantity)
						else:
							pass

						if stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).last().quantity
							present_quantity=medicine5_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_pk,medicine=medicine5_name).update(quantity=reduced_quantity)
						else:
							pass

						if stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).exists():
							quantity=stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).last().quantity
							present_quantity=medicine6_quantity
							quantity=int(quantity)
							present_quantity=int(present_quantity)
							reduced_quantity=quantity-present_quantity
							if reduced_quantity<=0:
								reduced_quantity=0
							else:
								reduced_quantity=reduced_quantity
							stock.objects.filter(doctor__id=doc_pk,medicine=medicine6_name).update(quantity=reduced_quantity)
						else:
							pass
						return redirect('summary')
				except IntegrityError :
					messages.info(request,'select medicine and days')
					return redirect('prescription')
			elif 'vitals_name' in request.POST:
				try:
					#if prescription data exists in prescription table
					if Prescription.objects.filter(purpose_id=purpose_pet_obj).exists() :

						if request.method=='POST':
							Prescription.objects.filter(purpose_id=purpose_pet_obj).delete()
							purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
							prescription=Prescription()
							prescription.purpose_id=purpose_pet_obj

							#for medicine 1
							medicine1=request.POST.get('medicine1')
							medicine1_time=request.POST.get('medicine1_time')
							medicine1_days=request.POST.get('medicine1_days')
							medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
							if medicine1=='':
								pass
							else:
								prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
								prescription.medicine1_quantity=medicine1_quantity

							#for medicine 2
							medicine2=request.POST.get('medicine2')
							medicine2_time=request.POST.get('medicine2_time')
							medicine2_days=request.POST.get('medicine2_days')
							medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
							if medicine2=='':
								pass
							else:
								prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
								prescription.medicine2_quantity=medicine2_quantity

							#for medicine 3
							medicine3=request.POST.get('medicine3')
							medicine3_time=request.POST.get('medicine3_time')
							medicine3_days=request.POST.get('medicine3_days')
							medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
							if medicine3=='':
								pass
							else:
								prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
								prescription.medicine3_quantity=medicine3_quantity

							#for medicine 4
							medicine4=request.POST.get('medicine4')
							medicine4_time=request.POST.get('medicine4_time')
							medicine4_days=request.POST.get('medicine4_days')
							medicine4_quantity=count_quantity(medicine4_days,medicine4_time)

							if medicine4=='':
								pass
							else:
								prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
								prescription.medicine4_quantity=medicine4_quantity

							#for medicine 5
							medicine5=request.POST.get('medicine5')
							medicine5_time=request.POST.get('medicine5_time')
							medicine5_days=request.POST.get('medicine5_days')
							medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
							if medicine5=='':
								pass
							else:
								prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
								prescription.medicine5_quantity=medicine5_quantity
							#for medicine 6
							medicine6=request.POST.get('medicine6')
							medicine6_time=request.POST.get('medicine6_time')
							medicine6_days=request.POST.get('medicine6_days')
							medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
							if medicine6=='':
								pass
							else:
								prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
								prescription.medicine6_quantity=medicine6_quantity

							medicine_other=request.POST.get('medicine_other')
							if medicine_other=='':
								pass
							else:
								prescription.medicine_other=request.POST.get('medicine_other')
							prescription.medicine1_name=request.POST.get('medicine1')
							prescription.medicine2_name=request.POST.get('medicine2')
							prescription.medicine3_name=request.POST.get('medicine3')
							prescription.medicine4_name=request.POST.get('medicine4')
							prescription.medicine5_name=request.POST.get('medicine5')
							prescription.medicine6_name=request.POST.get('medicine6')

							#image saving
							prescription.Prescription_img=request.FILES.get('file')
							#follwup_date
							follow_up_date=request.POST.get('followup_date')
							followup_date_unit = request.POST.get('followup_date_unit')
							if follow_up_date == '':
								follow_up_date = None
							prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
							prescription.followup_date_unit = followup_date_unit
							prescription.followup_date = prescription_followup_date
							prescription.save()
							medicine_other=request.POST.get('medicine_other')
							medicine1_name=request.POST.get('medicine1')
							medicine2_name=request.POST.get('medicine2')
							medicine3_name=request.POST.get('medicine3')
							medicine4_name=request.POST.get('medicine4')
							medicine5_name=request.POST.get('medicine5')
							medicine6_name=request.POST.get('medicine6')
							return redirect('vitals')
					else:
						#if object is not existed in prescription database
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						prescription=Prescription()
						prescription.purpose_id=purpose_pet_obj

						#for medicine 1
						medicine1=request.POST.get('medicine1')
						medicine1_time=request.POST.get('medicine1_time')
						medicine1_days=request.POST.get('medicine1_days')
						medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
						if medicine1=='':
							pass
						else:
							prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
							prescription.medicine1_quantity=medicine1_quantity

						#for medicine 2
						medicine2=request.POST.get('medicine2')
						medicine2_time=request.POST.get('medicine2_time')
						medicine2_days=request.POST.get('medicine2_days')
						medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
						if medicine2=='':
							pass
						else:
							prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
							prescription.medicine2_quantity=medicine2_quantity

						#for medicine 3
						medicine3=request.POST.get('medicine3')
						medicine3_time=request.POST.get('medicine3_time')
						medicine3_days=request.POST.get('medicine3_days')
						medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
						if medicine3=='':
							pass
						else:
							prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
							prescription.medicine3_quantity=medicine3_quantity

						#for medicine 4
						medicine4=request.POST.get('medicine4')
						medicine4_time=request.POST.get('medicine4_time')
						medicine4_days=request.POST.get('medicine4_days')
						medicine4_quantity=count_quantity(medicine4_days,medicine4_time)
						if medicine4=='':
							pass
						else:
							prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
							prescription.medicine4_quantity=medicine4_quantity

						#for medicine 5
						medicine5=request.POST.get('medicine5')
						medicine5_time=request.POST.get('medicine5_time')
						medicine5_days=request.POST.get('medicine5_days')
						medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
						if medicine5=='':
							pass
						else:
							prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
							prescription.medicine5_quantity=medicine5_quantity
						#for medicine 6
						medicine6=request.POST.get('medicine6')
						medicine6_time=request.POST.get('medicine6_time')
						medicine6_days=request.POST.get('medicine6_days')
						medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
						if medicine6=='':
							pass
						else:
							prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
							prescription.medicine6_quantity=medicine6_quantity

						medicine_other=request.POST.get('medicine_other')
						if medicine_other=='':
							pass
						else:
							prescription.medicine_other=request.POST.get('medicine_other')
						prescription.medicine1_name=request.POST.get('medicine1')
						prescription.medicine2_name=request.POST.get('medicine2')
						prescription.medicine3_name=request.POST.get('medicine3')
						prescription.medicine4_name=request.POST.get('medicine4')
						prescription.medicine5_name=request.POST.get('medicine5')
						prescription.medicine6_name=request.POST.get('medicine6')

						#image saving
						prescription.Prescription_img=request.FILES.get('file')
						#follwup_date
						follow_up_date=request.POST.get('followup_date')
						followup_date_unit = request.POST.get('followup_date_unit')
						if follow_up_date == '':
							follow_up_date = None
						prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
						prescription.followup_date_unit = followup_date_unit
						prescription.followup_date = prescription_followup_date
						prescription.save()
						return redirect('vitals')
				except IntegrityError :
					messages.info(request,'select medicine and days')
					return redirect('prescription')
			elif 'diagnostic_name' in request.POST:
				try:
					#if prescription data exists in prescription table
					if Prescription.objects.filter(purpose_id=purpose_pet_obj).exists() :

						if request.method=='POST':
							Prescription.objects.filter(purpose_id=purpose_pet_obj).delete()
							purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
							prescription=Prescription()
							prescription.purpose_id=purpose_pet_obj

							#for medicine 1
							medicine1=request.POST.get('medicine1')
							medicine1_time=request.POST.get('medicine1_time')
							medicine1_days=request.POST.get('medicine1_days')
							medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
							if medicine1=='':
								pass
							else:
								prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
								prescription.medicine1_quantity=medicine1_quantity

							#for medicine 2
							medicine2=request.POST.get('medicine2')
							medicine2_time=request.POST.get('medicine2_time')
							medicine2_days=request.POST.get('medicine2_days')
							medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
							if medicine2=='':
								pass
							else:
								prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
								prescription.medicine2_quantity=medicine2_quantity

							#for medicine 3
							medicine3=request.POST.get('medicine3')
							medicine3_time=request.POST.get('medicine3_time')
							medicine3_days=request.POST.get('medicine3_days')
							medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
							if medicine3=='':
								pass
							else:
								prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
								prescription.medicine3_quantity=medicine3_quantity

							#for medicine 4
							medicine4=request.POST.get('medicine4')
							medicine4_time=request.POST.get('medicine4_time')
							medicine4_days=request.POST.get('medicine4_days')
							medicine4_quantity=count_quantity(medicine4_days,medicine4_time)

							if medicine4=='':
								pass
							else:
								prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
								prescription.medicine4_quantity=medicine4_quantity

							#for medicine 5
							medicine5=request.POST.get('medicine5')
							medicine5_time=request.POST.get('medicine5_time')
							medicine5_days=request.POST.get('medicine5_days')
							medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
							if medicine5=='':
								pass
							else:
								prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
								prescription.medicine5_quantity=medicine5_quantity
							#for medicine 6
							medicine6=request.POST.get('medicine6')
							medicine6_time=request.POST.get('medicine6_time')
							medicine6_days=request.POST.get('medicine6_days')
							medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
							if medicine6=='':
								pass
							else:
								prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
								prescription.medicine6_quantity=medicine6_quantity

							medicine_other=request.POST.get('medicine_other')
							if medicine_other=='':
								pass
							else:
								prescription.medicine_other=request.POST.get('medicine_other')
							prescription.medicine1_name=request.POST.get('medicine1')
							prescription.medicine2_name=request.POST.get('medicine2')
							prescription.medicine3_name=request.POST.get('medicine3')
							prescription.medicine4_name=request.POST.get('medicine4')
							prescription.medicine5_name=request.POST.get('medicine5')
							prescription.medicine6_name=request.POST.get('medicine6')

							#image saving
							prescription.Prescription_img=request.FILES.get('file')
							#follwup_date
							follow_up_date=request.POST.get('followup_date')
							followup_date_unit = request.POST.get('followup_date_unit')
							if follow_up_date == '':
								follow_up_date = None
							prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
							prescription.followup_date_unit = followup_date_unit
							prescription.followup_date = prescription_followup_date
							prescription.save()
							medicine_other=request.POST.get('medicine_other')
							medicine1_name=request.POST.get('medicine1')
							medicine2_name=request.POST.get('medicine2')
							medicine3_name=request.POST.get('medicine3')
							medicine4_name=request.POST.get('medicine4')
							medicine5_name=request.POST.get('medicine5')
							medicine6_name=request.POST.get('medicine6')
							return redirect('diagnostic_prescription')
					else:
						#if object is not existed in prescription database
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						prescription=Prescription()
						prescription.purpose_id=purpose_pet_obj

						#for medicine 1
						medicine1=request.POST.get('medicine1')
						medicine1_time=request.POST.get('medicine1_time')
						medicine1_days=request.POST.get('medicine1_days')
						medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
						if medicine1=='':
							pass
						else:
							prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
							prescription.medicine1_quantity=medicine1_quantity

						#for medicine 2
						medicine2=request.POST.get('medicine2')
						medicine2_time=request.POST.get('medicine2_time')
						medicine2_days=request.POST.get('medicine2_days')
						medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
						if medicine2=='':
							pass
						else:
							prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
							prescription.medicine2_quantity=medicine2_quantity

						#for medicine 3
						medicine3=request.POST.get('medicine3')
						medicine3_time=request.POST.get('medicine3_time')
						medicine3_days=request.POST.get('medicine3_days')
						medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
						if medicine3=='':
							pass
						else:
							prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
							prescription.medicine3_quantity=medicine3_quantity

						#for medicine 4
						medicine4=request.POST.get('medicine4')
						medicine4_time=request.POST.get('medicine4_time')
						medicine4_days=request.POST.get('medicine4_days')
						medicine4_quantity=count_quantity(medicine4_days,medicine4_time)
						if medicine4=='':
							pass
						else:
							prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
							prescription.medicine4_quantity=medicine4_quantity

						#for medicine 5
						medicine5=request.POST.get('medicine5')
						medicine5_time=request.POST.get('medicine5_time')
						medicine5_days=request.POST.get('medicine5_days')
						medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
						if medicine5=='':
							pass
						else:
							prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
							prescription.medicine5_quantity=medicine5_quantity
						#for medicine 6
						medicine6=request.POST.get('medicine6')
						medicine6_time=request.POST.get('medicine6_time')
						medicine6_days=request.POST.get('medicine6_days')
						medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
						if medicine6=='':
							pass
						else:
							prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
							prescription.medicine6_quantity=medicine6_quantity

						medicine_other=request.POST.get('medicine_other')
						if medicine_other=='':
							pass
						else:
							prescription.medicine_other=request.POST.get('medicine_other')
						prescription.medicine1_name=request.POST.get('medicine1')
						prescription.medicine2_name=request.POST.get('medicine2')
						prescription.medicine3_name=request.POST.get('medicine3')
						prescription.medicine4_name=request.POST.get('medicine4')
						prescription.medicine5_name=request.POST.get('medicine5')
						prescription.medicine6_name=request.POST.get('medicine6')

						#image saving
						prescription.Prescription_img=request.FILES.get('file')
						#follwup_date
						follow_up_date=request.POST.get('followup_date')
						followup_date_unit = request.POST.get('followup_date_unit')
						if follow_up_date == '':
							follow_up_date = None
						prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
						prescription.followup_date_unit = followup_date_unit
						prescription.followup_date = prescription_followup_date
						prescription.save()
						return redirect('diagnostic_prescription')
				except IntegrityError :
					messages.info(request,'select medicine and days')
					return redirect('prescription')
			elif 'vaccination_name' in request.POST:
				try:
					#if prescription data exists in prescription table
					if Prescription.objects.filter(purpose_id=purpose_pet_obj).exists() :

						if request.method=='POST':
							Prescription.objects.filter(purpose_id=purpose_pet_obj).delete()
							purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
							prescription=Prescription()
							prescription.purpose_id=purpose_pet_obj

							#for medicine 1
							medicine1=request.POST.get('medicine1')
							medicine1_time=request.POST.get('medicine1_time')
							medicine1_days=request.POST.get('medicine1_days')
							medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
							if medicine1=='':
								pass
							else:
								prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
								prescription.medicine1_quantity=medicine1_quantity

							#for medicine 2
							medicine2=request.POST.get('medicine2')
							medicine2_time=request.POST.get('medicine2_time')
							medicine2_days=request.POST.get('medicine2_days')
							medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
							if medicine2=='':
								pass
							else:
								prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
								prescription.medicine2_quantity=medicine2_quantity

							#for medicine 3
							medicine3=request.POST.get('medicine3')
							medicine3_time=request.POST.get('medicine3_time')
							medicine3_days=request.POST.get('medicine3_days')
							medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
							if medicine3=='':
								pass
							else:
								prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
								prescription.medicine3_quantity=medicine3_quantity

							#for medicine 4
							medicine4=request.POST.get('medicine4')
							medicine4_time=request.POST.get('medicine4_time')
							medicine4_days=request.POST.get('medicine4_days')
							medicine4_quantity=count_quantity(medicine4_days,medicine4_time)

							if medicine4=='':
								pass
							else:
								prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
								prescription.medicine4_quantity=medicine4_quantity

							#for medicine 5
							medicine5=request.POST.get('medicine5')
							medicine5_time=request.POST.get('medicine5_time')
							medicine5_days=request.POST.get('medicine5_days')
							medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
							if medicine5=='':
								pass
							else:
								prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
								prescription.medicine5_quantity=medicine5_quantity
							#for medicine 6
							medicine6=request.POST.get('medicine6')
							medicine6_time=request.POST.get('medicine6_time')
							medicine6_days=request.POST.get('medicine6_days')
							medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
							if medicine6=='':
								pass
							else:
								prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
								prescription.medicine6_quantity=medicine6_quantity

							medicine_other=request.POST.get('medicine_other')
							if medicine_other=='':
								pass
							else:
								prescription.medicine_other=request.POST.get('medicine_other')
							prescription.medicine1_name=request.POST.get('medicine1')
							prescription.medicine2_name=request.POST.get('medicine2')
							prescription.medicine3_name=request.POST.get('medicine3')
							prescription.medicine4_name=request.POST.get('medicine4')
							prescription.medicine5_name=request.POST.get('medicine5')
							prescription.medicine6_name=request.POST.get('medicine6')

							#image saving
							prescription.Prescription_img=request.FILES.get('file')
							#follwup_date
							follow_up_date=request.POST.get('followup_date')
							followup_date_unit = request.POST.get('followup_date_unit')
							if follow_up_date == '':
								follow_up_date = None
							prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
							prescription.followup_date_unit = followup_date_unit
							prescription.followup_date = prescription_followup_date
							prescription.save()
							medicine_other=request.POST.get('medicine_other')
							medicine1_name=request.POST.get('medicine1')
							medicine2_name=request.POST.get('medicine2')
							medicine3_name=request.POST.get('medicine3')
							medicine4_name=request.POST.get('medicine4')
							medicine5_name=request.POST.get('medicine5')
							medicine6_name=request.POST.get('medicine6')
							return redirect('vaccination')
					else:
						#if object is not existed in prescription database
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						prescription=Prescription()
						prescription.purpose_id=purpose_pet_obj

						#for medicine 1
						medicine1=request.POST.get('medicine1')
						medicine1_time=request.POST.get('medicine1_time')
						medicine1_days=request.POST.get('medicine1_days')
						medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
						if medicine1=='':
							pass
						else:
							prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
							prescription.medicine1_quantity=medicine1_quantity

						#for medicine 2
						medicine2=request.POST.get('medicine2')
						medicine2_time=request.POST.get('medicine2_time')
						medicine2_days=request.POST.get('medicine2_days')
						medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
						if medicine2=='':
							pass
						else:
							prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
							prescription.medicine2_quantity=medicine2_quantity

						#for medicine 3
						medicine3=request.POST.get('medicine3')
						medicine3_time=request.POST.get('medicine3_time')
						medicine3_days=request.POST.get('medicine3_days')
						medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
						if medicine3=='':
							pass
						else:
							prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
							prescription.medicine3_quantity=medicine3_quantity

						#for medicine 4
						medicine4=request.POST.get('medicine4')
						medicine4_time=request.POST.get('medicine4_time')
						medicine4_days=request.POST.get('medicine4_days')
						medicine4_quantity=count_quantity(medicine4_days,medicine4_time)
						if medicine4=='':
							pass
						else:
							prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
							prescription.medicine4_quantity=medicine4_quantity

						#for medicine 5
						medicine5=request.POST.get('medicine5')
						medicine5_time=request.POST.get('medicine5_time')
						medicine5_days=request.POST.get('medicine5_days')
						medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
						if medicine5=='':
							pass
						else:
							prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
							prescription.medicine5_quantity=medicine5_quantity
						#for medicine 6
						medicine6=request.POST.get('medicine6')
						medicine6_time=request.POST.get('medicine6_time')
						medicine6_days=request.POST.get('medicine6_days')
						medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
						if medicine6=='':
							pass
						else:
							prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
							prescription.medicine6_quantity=medicine6_quantity

						medicine_other=request.POST.get('medicine_other')
						if medicine_other=='':
							pass
						else:
							prescription.medicine_other=request.POST.get('medicine_other')
						prescription.medicine1_name=request.POST.get('medicine1')
						prescription.medicine2_name=request.POST.get('medicine2')
						prescription.medicine3_name=request.POST.get('medicine3')
						prescription.medicine4_name=request.POST.get('medicine4')
						prescription.medicine5_name=request.POST.get('medicine5')
						prescription.medicine6_name=request.POST.get('medicine6')

						#image saving
						prescription.Prescription_img=request.FILES.get('file')
						#follwup_date
						follow_up_date=request.POST.get('followup_date')
						followup_date_unit = request.POST.get('followup_date_unit')
						if follow_up_date == '':
							follow_up_date = None
						prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
						prescription.followup_date_unit = followup_date_unit
						prescription.followup_date = prescription_followup_date
						prescription.save()
						return redirect('vaccination')
				except IntegrityError :
					messages.info(request,'select medicine and days')
					return redirect('prescription')
			elif 'deworming_name' in request.POST:
				try:
					#if prescription data exists in prescription table
					if Prescription.objects.filter(purpose_id=purpose_pet_obj).exists() :

						if request.method=='POST':
							Prescription.objects.filter(purpose_id=purpose_pet_obj).delete()
							purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
							prescription=Prescription()
							prescription.purpose_id=purpose_pet_obj

							#for medicine 1
							medicine1=request.POST.get('medicine1')
							medicine1_time=request.POST.get('medicine1_time')
							medicine1_days=request.POST.get('medicine1_days')
							medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
							if medicine1=='':
								pass
							else:
								prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
								prescription.medicine1_quantity=medicine1_quantity

							#for medicine 2
							medicine2=request.POST.get('medicine2')
							medicine2_time=request.POST.get('medicine2_time')
							medicine2_days=request.POST.get('medicine2_days')
							medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
							if medicine2=='':
								pass
							else:
								prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
								prescription.medicine2_quantity=medicine2_quantity

							#for medicine 3
							medicine3=request.POST.get('medicine3')
							medicine3_time=request.POST.get('medicine3_time')
							medicine3_days=request.POST.get('medicine3_days')
							medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
							if medicine3=='':
								pass
							else:
								prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
								prescription.medicine3_quantity=medicine3_quantity

							#for medicine 4
							medicine4=request.POST.get('medicine4')
							medicine4_time=request.POST.get('medicine4_time')
							medicine4_days=request.POST.get('medicine4_days')
							medicine4_quantity=count_quantity(medicine4_days,medicine4_time)

							if medicine4=='':
								pass
							else:
								prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
								prescription.medicine4_quantity=medicine4_quantity

							#for medicine 5
							medicine5=request.POST.get('medicine5')
							medicine5_time=request.POST.get('medicine5_time')
							medicine5_days=request.POST.get('medicine5_days')
							medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
							if medicine5=='':
								pass
							else:
								prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
								prescription.medicine5_quantity=medicine5_quantity
							#for medicine 6
							medicine6=request.POST.get('medicine6')
							medicine6_time=request.POST.get('medicine6_time')
							medicine6_days=request.POST.get('medicine6_days')
							medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
							if medicine6=='':
								pass
							else:
								prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
								prescription.medicine6_quantity=medicine6_quantity

							medicine_other=request.POST.get('medicine_other')
							if medicine_other=='':
								pass
							else:
								prescription.medicine_other=request.POST.get('medicine_other')
							prescription.medicine1_name=request.POST.get('medicine1')
							prescription.medicine2_name=request.POST.get('medicine2')
							prescription.medicine3_name=request.POST.get('medicine3')
							prescription.medicine4_name=request.POST.get('medicine4')
							prescription.medicine5_name=request.POST.get('medicine5')
							prescription.medicine6_name=request.POST.get('medicine6')

							#image saving
							prescription.Prescription_img=request.FILES.get('file')
							#follwup_date
							follow_up_date=request.POST.get('followup_date')
							followup_date_unit = request.POST.get('followup_date_unit')
							if follow_up_date == '':
								follow_up_date = None
							prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
							prescription.followup_date_unit = followup_date_unit
							prescription.followup_date = prescription_followup_date
							prescription.save()
							medicine_other=request.POST.get('medicine_other')
							medicine1_name=request.POST.get('medicine1')
							medicine2_name=request.POST.get('medicine2')
							medicine3_name=request.POST.get('medicine3')
							medicine4_name=request.POST.get('medicine4')
							medicine5_name=request.POST.get('medicine5')
							medicine6_name=request.POST.get('medicine6')
							return redirect('deworming')
					else:
						#if object is not existed in prescription database
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						prescription=Prescription()
						prescription.purpose_id=purpose_pet_obj

						#for medicine 1
						medicine1=request.POST.get('medicine1')
						medicine1_time=request.POST.get('medicine1_time')
						medicine1_days=request.POST.get('medicine1_days')
						medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
						if medicine1=='':
							pass
						else:
							prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
							prescription.medicine1_quantity=medicine1_quantity

						#for medicine 2
						medicine2=request.POST.get('medicine2')
						medicine2_time=request.POST.get('medicine2_time')
						medicine2_days=request.POST.get('medicine2_days')
						medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
						if medicine2=='':
							pass
						else:
							prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
							prescription.medicine2_quantity=medicine2_quantity

						#for medicine 3
						medicine3=request.POST.get('medicine3')
						medicine3_time=request.POST.get('medicine3_time')
						medicine3_days=request.POST.get('medicine3_days')
						medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
						if medicine3=='':
							pass
						else:
							prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
							prescription.medicine3_quantity=medicine3_quantity

						#for medicine 4
						medicine4=request.POST.get('medicine4')
						medicine4_time=request.POST.get('medicine4_time')
						medicine4_days=request.POST.get('medicine4_days')
						medicine4_quantity=count_quantity(medicine4_days,medicine4_time)
						if medicine4=='':
							pass
						else:
							prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
							prescription.medicine4_quantity=medicine4_quantity

						#for medicine 5
						medicine5=request.POST.get('medicine5')
						medicine5_time=request.POST.get('medicine5_time')
						medicine5_days=request.POST.get('medicine5_days')
						medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
						if medicine5=='':
							pass
						else:
							prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
							prescription.medicine5_quantity=medicine5_quantity
						#for medicine 6
						medicine6=request.POST.get('medicine6')
						medicine6_time=request.POST.get('medicine6_time')
						medicine6_days=request.POST.get('medicine6_days')
						medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
						if medicine6=='':
							pass
						else:
							prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
							prescription.medicine6_quantity=medicine6_quantity

						medicine_other=request.POST.get('medicine_other')
						if medicine_other=='':
							pass
						else:
							prescription.medicine_other=request.POST.get('medicine_other')
						prescription.medicine1_name=request.POST.get('medicine1')
						prescription.medicine2_name=request.POST.get('medicine2')
						prescription.medicine3_name=request.POST.get('medicine3')
						prescription.medicine4_name=request.POST.get('medicine4')
						prescription.medicine5_name=request.POST.get('medicine5')
						prescription.medicine6_name=request.POST.get('medicine6')

						#image saving
						prescription.Prescription_img=request.FILES.get('file')
						#follwup_date
						follow_up_date=request.POST.get('followup_date')
						followup_date_unit = request.POST.get('followup_date_unit')
						if follow_up_date == '':
							follow_up_date = None
						prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
						prescription.followup_date_unit = followup_date_unit
						prescription.followup_date = prescription_followup_date
						prescription.save()
						return redirect('deworming')
				except IntegrityError :
					messages.info(request,'select medicine and days')
					return redirect('prescription')
			else:
				return redirect('prescription')
	else:
		#if stock management not opted
		return redirect('prescription_nostock')

def prescription_nostock(request):
	doc_pk = request.session.get('doc_pk')
	purpose_pk = request.session.get('purpose_pk')
	pet_pk = request.session.get('pet_pk')
	pet_obj=Pet.objects.filter(id=pet_pk).last()
	pet_obj=pet_age_converter_single(pet_obj)
	purpose_pet_obj_diet=PurposeAndDiet.objects.filter(id=purpose_pk).last()
	purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
	st=stock.objects.filter(doctor__id=doc_pk)
	try:
		x=Prescription.objects.filter(purpose_id=purpose_pet_obj).last()
		val=x.followup_date
		unt=x.followup_date_unit
		reverse_date_num = prescription_date_format_reverse(val,unt)
		x=model_to_dict(x)
	except :
		reverse_date_num = None
		unt = ''
	if request.method == "GET":
		if 'doc_pk' in request.session:
			return render(request,'doctor/doctor_prescription_without_stock.html',
			{'pet_obj':pet_obj,'purpose_pet_obj_diet':purpose_pet_obj_diet,
			'doc_pk':doc_pk,'st':st,'pet_pk':pet_pk,'purpose_pk':purpose_pk,'x':x,
			'reverse_date_num':reverse_date_num,'unt':unt})
		else:
			return redirect('doctor_login')

	if request.method=='POST':

			if 'assessment_name' in request.POST:
				try:
					#if prescription data exists in prescription table
					if Prescription.objects.filter(purpose_id=purpose_pet_obj).exists() :

						if request.method=='POST':
							Prescription.objects.filter(purpose_id=purpose_pet_obj).delete()
							purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
							prescription=Prescription()
							prescription.purpose_id=purpose_pet_obj

							#for medicine 1
							medicine1=request.POST.get('medicine1')
							medicine1_time=request.POST.get('medicine1_time')
							medicine1_days=request.POST.get('medicine1_days')
							medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
							if medicine1=='':
								pass
							else:
								prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
								prescription.medicine1_quantity=medicine1_quantity

							#for medicine 2
							medicine2=request.POST.get('medicine2')
							medicine2_time=request.POST.get('medicine2_time')
							medicine2_days=request.POST.get('medicine2_days')
							medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
							if medicine2=='':
								pass
							else:
								prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
								prescription.medicine2_quantity=medicine2_quantity

							#for medicine 3
							medicine3=request.POST.get('medicine3')
							medicine3_time=request.POST.get('medicine3_time')
							medicine3_days=request.POST.get('medicine3_days')
							medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
							if medicine3=='':
								pass
							else:
								prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
								prescription.medicine3_quantity=medicine3_quantity

							#for medicine 4
							medicine4=request.POST.get('medicine4')
							medicine4_time=request.POST.get('medicine4_time')
							medicine4_days=request.POST.get('medicine4_days')
							medicine4_quantity=count_quantity(medicine4_days,medicine4_time)

							if medicine4=='':
								pass
							else:
								prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
								prescription.medicine4_quantity=medicine4_quantity

							#for medicine 5
							medicine5=request.POST.get('medicine5')
							medicine5_time=request.POST.get('medicine5_time')
							medicine5_days=request.POST.get('medicine5_days')
							medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
							if medicine5=='':
								pass
							else:
								prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
								prescription.medicine5_quantity=medicine5_quantity
							#for medicine 6
							medicine6=request.POST.get('medicine6')
							medicine6_time=request.POST.get('medicine6_time')
							medicine6_days=request.POST.get('medicine6_days')
							medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
							if medicine6=='':
								pass
							else:
								prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
								prescription.medicine6_quantity=medicine6_quantity

							medicine_other=request.POST.get('medicine_other')
							if medicine_other=='':
								pass
							else:
								prescription.medicine_other=request.POST.get('medicine_other')
							prescription.medicine1_name=request.POST.get('medicine1')
							prescription.medicine2_name=request.POST.get('medicine2')
							prescription.medicine3_name=request.POST.get('medicine3')
							prescription.medicine4_name=request.POST.get('medicine4')
							prescription.medicine5_name=request.POST.get('medicine5')
							prescription.medicine6_name=request.POST.get('medicine6')

							#image saving
							prescription.Prescription_img=request.FILES.get('file')
							#follwup_date
							follow_up_date=request.POST.get('followup_date')
							followup_date_unit = request.POST.get('followup_date_unit')
							if follow_up_date == '':
								follow_up_date = None
							prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
							prescription.followup_date_unit = followup_date_unit
							prescription.followup_date = prescription_followup_date
							prescription.save()
							medicine_other=request.POST.get('medicine_other')
							medicine1_name=request.POST.get('medicine1')
							medicine2_name=request.POST.get('medicine2')
							medicine3_name=request.POST.get('medicine3')
							medicine4_name=request.POST.get('medicine4')
							medicine5_name=request.POST.get('medicine5')
							medicine6_name=request.POST.get('medicine6')
							return redirect('assessment')
					else:
						#if object is not existed in prescription database
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						prescription=Prescription()
						prescription.purpose_id=purpose_pet_obj

						#for medicine 1
						medicine1=request.POST.get('medicine1')
						medicine1_time=request.POST.get('medicine1_time')
						medicine1_days=request.POST.get('medicine1_days')
						medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
						if medicine1=='':
							pass
						else:
							prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
							prescription.medicine1_quantity=medicine1_quantity

						#for medicine 2
						medicine2=request.POST.get('medicine2')
						medicine2_time=request.POST.get('medicine2_time')
						medicine2_days=request.POST.get('medicine2_days')
						medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
						if medicine2=='':
							pass
						else:
							prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
							prescription.medicine2_quantity=medicine2_quantity

						#for medicine 3
						medicine3=request.POST.get('medicine3')
						medicine3_time=request.POST.get('medicine3_time')
						medicine3_days=request.POST.get('medicine3_days')
						medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
						if medicine3=='':
							pass
						else:
							prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
							prescription.medicine3_quantity=medicine3_quantity

						#for medicine 4
						medicine4=request.POST.get('medicine4')
						medicine4_time=request.POST.get('medicine4_time')
						medicine4_days=request.POST.get('medicine4_days')
						medicine4_quantity=count_quantity(medicine4_days,medicine4_time)
						if medicine4=='':
							pass
						else:
							prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
							prescription.medicine4_quantity=medicine4_quantity

						#for medicine 5
						medicine5=request.POST.get('medicine5')
						medicine5_time=request.POST.get('medicine5_time')
						medicine5_days=request.POST.get('medicine5_days')
						medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
						if medicine5=='':
							pass
						else:
							prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
							prescription.medicine5_quantity=medicine5_quantity
						#for medicine 6
						medicine6=request.POST.get('medicine6')
						medicine6_time=request.POST.get('medicine6_time')
						medicine6_days=request.POST.get('medicine6_days')
						medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
						if medicine6=='':
							pass
						else:
							prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
							prescription.medicine6_quantity=medicine6_quantity

						medicine_other=request.POST.get('medicine_other')
						if medicine_other=='':
							pass
						else:
							prescription.medicine_other=request.POST.get('medicine_other')
						prescription.medicine1_name=request.POST.get('medicine1')
						prescription.medicine2_name=request.POST.get('medicine2')
						prescription.medicine3_name=request.POST.get('medicine3')
						prescription.medicine4_name=request.POST.get('medicine4')
						prescription.medicine5_name=request.POST.get('medicine5')
						prescription.medicine6_name=request.POST.get('medicine6')

						#image saving
						prescription.Prescription_img=request.FILES.get('file')
						#follwup_date
						follow_up_date=request.POST.get('followup_date')
						followup_date_unit = request.POST.get('followup_date_unit')
						if follow_up_date == '':
							follow_up_date = None
						prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
						prescription.followup_date_unit = followup_date_unit
						prescription.followup_date = prescription_followup_date
						prescription.save()
						return redirect('assessment')
				except IntegrityError :
					messages.info(request,'select medicine and days')
					return redirect('prescription_nostock')
			elif 'close_visit' in request.POST:
				try:
				#if prescription data exists in prescription table
					if Prescription.objects.filter(purpose_id=purpose_pet_obj).exists() :

						if request.method=='POST':
							Prescription.objects.filter(purpose_id=purpose_pet_obj).delete()
							purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
							prescription=Prescription()
							prescription.purpose_id=purpose_pet_obj

							#for medicine 1
							medicine1=request.POST.get('medicine1')
							medicine1_time=request.POST.get('medicine1_time')
							medicine1_days=request.POST.get('medicine1_days')
							medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
							if medicine1=='':
								pass
							else:
								prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
								prescription.medicine1_quantity=medicine1_quantity

							#for medicine 2
							medicine2=request.POST.get('medicine2')
							medicine2_time=request.POST.get('medicine2_time')
							medicine2_days=request.POST.get('medicine2_days')
							medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
							if medicine2=='':
								pass
							else:
								prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
								prescription.medicine2_quantity=medicine2_quantity

							#for medicine 3
							medicine3=request.POST.get('medicine3')
							medicine3_time=request.POST.get('medicine3_time')
							medicine3_days=request.POST.get('medicine3_days')
							medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
							if medicine3=='':
								pass
							else:
								prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
								prescription.medicine3_quantity=medicine3_quantity

							#for medicine 4
							medicine4=request.POST.get('medicine4')
							medicine4_time=request.POST.get('medicine4_time')
							medicine4_days=request.POST.get('medicine4_days')
							medicine4_quantity=count_quantity(medicine4_days,medicine4_time)

							if medicine4=='':
								pass
							else:
								prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
								prescription.medicine4_quantity=medicine4_quantity

							#for medicine 5
							medicine5=request.POST.get('medicine5')
							medicine5_time=request.POST.get('medicine5_time')
							medicine5_days=request.POST.get('medicine5_days')
							medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
							if medicine5=='':
								pass
							else:
								prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
								prescription.medicine5_quantity=medicine5_quantity
							#for medicine 6
							medicine6=request.POST.get('medicine6')
							medicine6_time=request.POST.get('medicine6_time')
							medicine6_days=request.POST.get('medicine6_days')
							medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
							if medicine6=='':
								pass
							else:
								prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
								prescription.medicine6_quantity=medicine6_quantity

							medicine_other=request.POST.get('medicine_other')
							if medicine_other=='':
								pass
							else:
								prescription.medicine_other=request.POST.get('medicine_other')
							prescription.medicine1_name=request.POST.get('medicine1')
							prescription.medicine2_name=request.POST.get('medicine2')
							prescription.medicine3_name=request.POST.get('medicine3')
							prescription.medicine4_name=request.POST.get('medicine4')
							prescription.medicine5_name=request.POST.get('medicine5')
							prescription.medicine6_name=request.POST.get('medicine6')

							#image saving
							prescription.Prescription_img=request.FILES.get('file')
							#follwup_date
							follow_up_date=request.POST.get('followup_date')
							followup_date_unit = request.POST.get('followup_date_unit')
							if follow_up_date == '':
								follow_up_date = None
							prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
							prescription.followup_date_unit = followup_date_unit
							prescription.followup_date = prescription_followup_date
							prescription.save()

							return redirect('summary')
					else:
						#if object is not existed in prescription database
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						prescription=Prescription()
						prescription.purpose_id=purpose_pet_obj

						#for medicine 1
						medicine1=request.POST.get('medicine1')
						medicine1_time=request.POST.get('medicine1_time')
						medicine1_days=request.POST.get('medicine1_days')
						medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
						if medicine1=='':
							pass
						else:
							prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
							prescription.medicine1_quantity=medicine1_quantity

						#for medicine 2
						medicine2=request.POST.get('medicine2')
						medicine2_time=request.POST.get('medicine2_time')
						medicine2_days=request.POST.get('medicine2_days')
						medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
						if medicine2=='':
							pass
						else:
							prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
							prescription.medicine2_quantity=medicine2_quantity

						#for medicine 3
						medicine3=request.POST.get('medicine3')
						medicine3_time=request.POST.get('medicine3_time')
						medicine3_days=request.POST.get('medicine3_days')
						medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
						if medicine3=='':
							pass
						else:
							prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
							prescription.medicine3_quantity=medicine3_quantity

						#for medicine 4
						medicine4=request.POST.get('medicine4')
						medicine4_time=request.POST.get('medicine4_time')
						medicine4_days=request.POST.get('medicine4_days')
						medicine4_quantity=count_quantity(medicine4_days,medicine4_time)
						if medicine4=='':
							pass
						else:
							prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
							prescription.medicine4_quantity=medicine4_quantity

						#for medicine 5
						medicine5=request.POST.get('medicine5')
						medicine5_time=request.POST.get('medicine5_time')
						medicine5_days=request.POST.get('medicine5_days')
						medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
						if medicine5=='':
							pass
						else:
							prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
							prescription.medicine5_quantity=medicine5_quantity
						#for medicine 6
						medicine6=request.POST.get('medicine6')
						medicine6_time=request.POST.get('medicine6_time')
						medicine6_days=request.POST.get('medicine6_days')
						medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
						if medicine6=='':
							pass
						else:
							prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
							prescription.medicine6_quantity=medicine6_quantity

						medicine_other=request.POST.get('medicine_other')
						if medicine_other=='':
							pass
						else:
							prescription.medicine_other=request.POST.get('medicine_other')
						prescription.medicine1_name=request.POST.get('medicine1')
						prescription.medicine2_name=request.POST.get('medicine2')
						prescription.medicine3_name=request.POST.get('medicine3')
						prescription.medicine4_name=request.POST.get('medicine4')
						prescription.medicine5_name=request.POST.get('medicine5')
						prescription.medicine6_name=request.POST.get('medicine6')

						#image saving
						prescription.Prescription_img=request.FILES.get('file')
						#follwup_date
						follow_up_date=request.POST.get('followup_date')
						followup_date_unit = request.POST.get('followup_date_unit')
						if follow_up_date == '':
							follow_up_date = None
						prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
						prescription.followup_date_unit = followup_date_unit
						prescription.followup_date = prescription_followup_date
						prescription.save()

						return redirect('summary')
				except IntegrityError :
					messages.info(request,'select medicine and days')
					return redirect('prescription_nostock')
			elif 'vitals_name' in request.POST:
				try:
					#if prescription data exists in prescription table
					if Prescription.objects.filter(purpose_id=purpose_pet_obj).exists() :

						if request.method=='POST':
							Prescription.objects.filter(purpose_id=purpose_pet_obj).delete()
							purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
							prescription=Prescription()
							prescription.purpose_id=purpose_pet_obj

							#for medicine 1
							medicine1=request.POST.get('medicine1')
							medicine1_time=request.POST.get('medicine1_time')
							medicine1_days=request.POST.get('medicine1_days')
							medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
							if medicine1=='':
								pass
							else:
								prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
								prescription.medicine1_quantity=medicine1_quantity

							#for medicine 2
							medicine2=request.POST.get('medicine2')
							medicine2_time=request.POST.get('medicine2_time')
							medicine2_days=request.POST.get('medicine2_days')
							medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
							if medicine2=='':
								pass
							else:
								prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
								prescription.medicine2_quantity=medicine2_quantity

							#for medicine 3
							medicine3=request.POST.get('medicine3')
							medicine3_time=request.POST.get('medicine3_time')
							medicine3_days=request.POST.get('medicine3_days')
							medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
							if medicine3=='':
								pass
							else:
								prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
								prescription.medicine3_quantity=medicine3_quantity

							#for medicine 4
							medicine4=request.POST.get('medicine4')
							medicine4_time=request.POST.get('medicine4_time')
							medicine4_days=request.POST.get('medicine4_days')
							medicine4_quantity=count_quantity(medicine4_days,medicine4_time)

							if medicine4=='':
								pass
							else:
								prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
								prescription.medicine4_quantity=medicine4_quantity

							#for medicine 5
							medicine5=request.POST.get('medicine5')
							medicine5_time=request.POST.get('medicine5_time')
							medicine5_days=request.POST.get('medicine5_days')
							medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
							if medicine5=='':
								pass
							else:
								prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
								prescription.medicine5_quantity=medicine5_quantity
							#for medicine 6
							medicine6=request.POST.get('medicine6')
							medicine6_time=request.POST.get('medicine6_time')
							medicine6_days=request.POST.get('medicine6_days')
							medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
							if medicine6=='':
								pass
							else:
								prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
								prescription.medicine6_quantity=medicine6_quantity

							medicine_other=request.POST.get('medicine_other')
							if medicine_other=='':
								pass
							else:
								prescription.medicine_other=request.POST.get('medicine_other')
							prescription.medicine1_name=request.POST.get('medicine1')
							prescription.medicine2_name=request.POST.get('medicine2')
							prescription.medicine3_name=request.POST.get('medicine3')
							prescription.medicine4_name=request.POST.get('medicine4')
							prescription.medicine5_name=request.POST.get('medicine5')
							prescription.medicine6_name=request.POST.get('medicine6')

							#image saving
							prescription.Prescription_img=request.FILES.get('file')
							#follwup_date
							follow_up_date=request.POST.get('followup_date')
							followup_date_unit = request.POST.get('followup_date_unit')
							if follow_up_date == '':
								follow_up_date = None
							prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
							prescription.followup_date_unit = followup_date_unit
							prescription.followup_date = prescription_followup_date
							prescription.save()
							medicine_other=request.POST.get('medicine_other')
							medicine1_name=request.POST.get('medicine1')
							medicine2_name=request.POST.get('medicine2')
							medicine3_name=request.POST.get('medicine3')
							medicine4_name=request.POST.get('medicine4')
							medicine5_name=request.POST.get('medicine5')
							medicine6_name=request.POST.get('medicine6')
							return redirect('vitals')
					else:
						#if object is not existed in prescription database
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						prescription=Prescription()
						prescription.purpose_id=purpose_pet_obj

						#for medicine 1
						medicine1=request.POST.get('medicine1')
						medicine1_time=request.POST.get('medicine1_time')
						medicine1_days=request.POST.get('medicine1_days')
						medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
						if medicine1=='':
							pass
						else:
							prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
							prescription.medicine1_quantity=medicine1_quantity

						#for medicine 2
						medicine2=request.POST.get('medicine2')
						medicine2_time=request.POST.get('medicine2_time')
						medicine2_days=request.POST.get('medicine2_days')
						medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
						if medicine2=='':
							pass
						else:
							prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
							prescription.medicine2_quantity=medicine2_quantity

						#for medicine 3
						medicine3=request.POST.get('medicine3')
						medicine3_time=request.POST.get('medicine3_time')
						medicine3_days=request.POST.get('medicine3_days')
						medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
						if medicine3=='':
							pass
						else:
							prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
							prescription.medicine3_quantity=medicine3_quantity

						#for medicine 4
						medicine4=request.POST.get('medicine4')
						medicine4_time=request.POST.get('medicine4_time')
						medicine4_days=request.POST.get('medicine4_days')
						medicine4_quantity=count_quantity(medicine4_days,medicine4_time)
						if medicine4=='':
							pass
						else:
							prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
							prescription.medicine4_quantity=medicine4_quantity

						#for medicine 5
						medicine5=request.POST.get('medicine5')
						medicine5_time=request.POST.get('medicine5_time')
						medicine5_days=request.POST.get('medicine5_days')
						medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
						if medicine5=='':
							pass
						else:
							prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
							prescription.medicine5_quantity=medicine5_quantity
						#for medicine 6
						medicine6=request.POST.get('medicine6')
						medicine6_time=request.POST.get('medicine6_time')
						medicine6_days=request.POST.get('medicine6_days')
						medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
						if medicine6=='':
							pass
						else:
							prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
							prescription.medicine6_quantity=medicine6_quantity

						medicine_other=request.POST.get('medicine_other')
						if medicine_other=='':
							pass
						else:
							prescription.medicine_other=request.POST.get('medicine_other')
						prescription.medicine1_name=request.POST.get('medicine1')
						prescription.medicine2_name=request.POST.get('medicine2')
						prescription.medicine3_name=request.POST.get('medicine3')
						prescription.medicine4_name=request.POST.get('medicine4')
						prescription.medicine5_name=request.POST.get('medicine5')
						prescription.medicine6_name=request.POST.get('medicine6')

						#image saving
						prescription.Prescription_img=request.FILES.get('file')
						#follwup_date
						follow_up_date=request.POST.get('followup_date')
						followup_date_unit = request.POST.get('followup_date_unit')
						if follow_up_date == '':
							follow_up_date = None
						prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
						prescription.followup_date_unit = followup_date_unit
						prescription.followup_date = prescription_followup_date
						prescription.save()
						return redirect('vitals')
				except IntegrityError :
					messages.info(request,'select medicine and days')
					return redirect('prescription_nostock')
			elif 'diagnostic_name' in request.POST:
				try:
					#if prescription data exists in prescription table
					if Prescription.objects.filter(purpose_id=purpose_pet_obj).exists() :

						if request.method=='POST':
							Prescription.objects.filter(purpose_id=purpose_pet_obj).delete()
							purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
							prescription=Prescription()
							prescription.purpose_id=purpose_pet_obj

							#for medicine 1
							medicine1=request.POST.get('medicine1')
							medicine1_time=request.POST.get('medicine1_time')
							medicine1_days=request.POST.get('medicine1_days')
							medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
							if medicine1=='':
								pass
							else:
								prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
								prescription.medicine1_quantity=medicine1_quantity

							#for medicine 2
							medicine2=request.POST.get('medicine2')
							medicine2_time=request.POST.get('medicine2_time')
							medicine2_days=request.POST.get('medicine2_days')
							medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
							if medicine2=='':
								pass
							else:
								prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
								prescription.medicine2_quantity=medicine2_quantity

							#for medicine 3
							medicine3=request.POST.get('medicine3')
							medicine3_time=request.POST.get('medicine3_time')
							medicine3_days=request.POST.get('medicine3_days')
							medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
							if medicine3=='':
								pass
							else:
								prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
								prescription.medicine3_quantity=medicine3_quantity

							#for medicine 4
							medicine4=request.POST.get('medicine4')
							medicine4_time=request.POST.get('medicine4_time')
							medicine4_days=request.POST.get('medicine4_days')
							medicine4_quantity=count_quantity(medicine4_days,medicine4_time)

							if medicine4=='':
								pass
							else:
								prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
								prescription.medicine4_quantity=medicine4_quantity

							#for medicine 5
							medicine5=request.POST.get('medicine5')
							medicine5_time=request.POST.get('medicine5_time')
							medicine5_days=request.POST.get('medicine5_days')
							medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
							if medicine5=='':
								pass
							else:
								prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
								prescription.medicine5_quantity=medicine5_quantity
							#for medicine 6
							medicine6=request.POST.get('medicine6')
							medicine6_time=request.POST.get('medicine6_time')
							medicine6_days=request.POST.get('medicine6_days')
							medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
							if medicine6=='':
								pass
							else:
								prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
								prescription.medicine6_quantity=medicine6_quantity

							medicine_other=request.POST.get('medicine_other')
							if medicine_other=='':
								pass
							else:
								prescription.medicine_other=request.POST.get('medicine_other')
							prescription.medicine1_name=request.POST.get('medicine1')
							prescription.medicine2_name=request.POST.get('medicine2')
							prescription.medicine3_name=request.POST.get('medicine3')
							prescription.medicine4_name=request.POST.get('medicine4')
							prescription.medicine5_name=request.POST.get('medicine5')
							prescription.medicine6_name=request.POST.get('medicine6')

							#image saving
							prescription.Prescription_img=request.FILES.get('file')
							#follwup_date
							follow_up_date=request.POST.get('followup_date')
							followup_date_unit = request.POST.get('followup_date_unit')
							if follow_up_date == '':
								follow_up_date = None
							prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
							prescription.followup_date_unit = followup_date_unit
							prescription.followup_date = prescription_followup_date
							prescription.save()
							medicine_other=request.POST.get('medicine_other')
							medicine1_name=request.POST.get('medicine1')
							medicine2_name=request.POST.get('medicine2')
							medicine3_name=request.POST.get('medicine3')
							medicine4_name=request.POST.get('medicine4')
							medicine5_name=request.POST.get('medicine5')
							medicine6_name=request.POST.get('medicine6')
							return redirect('diagnostic_prescription')
					else:
						#if object is not existed in prescription database
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						prescription=Prescription()
						prescription.purpose_id=purpose_pet_obj

						#for medicine 1
						medicine1=request.POST.get('medicine1')
						medicine1_time=request.POST.get('medicine1_time')
						medicine1_days=request.POST.get('medicine1_days')
						medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
						if medicine1=='':
							pass
						else:
							prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
							prescription.medicine1_quantity=medicine1_quantity

						#for medicine 2
						medicine2=request.POST.get('medicine2')
						medicine2_time=request.POST.get('medicine2_time')
						medicine2_days=request.POST.get('medicine2_days')
						medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
						if medicine2=='':
							pass
						else:
							prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
							prescription.medicine2_quantity=medicine2_quantity

						#for medicine 3
						medicine3=request.POST.get('medicine3')
						medicine3_time=request.POST.get('medicine3_time')
						medicine3_days=request.POST.get('medicine3_days')
						medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
						if medicine3=='':
							pass
						else:
							prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
							prescription.medicine3_quantity=medicine3_quantity

						#for medicine 4
						medicine4=request.POST.get('medicine4')
						medicine4_time=request.POST.get('medicine4_time')
						medicine4_days=request.POST.get('medicine4_days')
						medicine4_quantity=count_quantity(medicine4_days,medicine4_time)
						if medicine4=='':
							pass
						else:
							prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
							prescription.medicine4_quantity=medicine4_quantity

						#for medicine 5
						medicine5=request.POST.get('medicine5')
						medicine5_time=request.POST.get('medicine5_time')
						medicine5_days=request.POST.get('medicine5_days')
						medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
						if medicine5=='':
							pass
						else:
							prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
							prescription.medicine5_quantity=medicine5_quantity
						#for medicine 6
						medicine6=request.POST.get('medicine6')
						medicine6_time=request.POST.get('medicine6_time')
						medicine6_days=request.POST.get('medicine6_days')
						medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
						if medicine6=='':
							pass
						else:
							prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
							prescription.medicine6_quantity=medicine6_quantity

						medicine_other=request.POST.get('medicine_other')
						if medicine_other=='':
							pass
						else:
							prescription.medicine_other=request.POST.get('medicine_other')
						prescription.medicine1_name=request.POST.get('medicine1')
						prescription.medicine2_name=request.POST.get('medicine2')
						prescription.medicine3_name=request.POST.get('medicine3')
						prescription.medicine4_name=request.POST.get('medicine4')
						prescription.medicine5_name=request.POST.get('medicine5')
						prescription.medicine6_name=request.POST.get('medicine6')

						#image saving
						prescription.Prescription_img=request.FILES.get('file')
						#follwup_date
						follow_up_date=request.POST.get('followup_date')
						followup_date_unit = request.POST.get('followup_date_unit')
						if follow_up_date == '':
							follow_up_date = None
						prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
						prescription.followup_date_unit = followup_date_unit
						prescription.followup_date = prescription_followup_date
						prescription.save()
						return redirect('diagnostic_prescription')
				except IntegrityError :
					messages.info(request,'select medicine and days')
					return redirect('prescription_nostock')
			elif 'vaccination_name' in request.POST:
				try:
					#if prescription data exists in prescription table
					if Prescription.objects.filter(purpose_id=purpose_pet_obj).exists() :

						if request.method=='POST':
							Prescription.objects.filter(purpose_id=purpose_pet_obj).delete()
							purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
							prescription=Prescription()
							prescription.purpose_id=purpose_pet_obj

							#for medicine 1
							medicine1=request.POST.get('medicine1')
							medicine1_time=request.POST.get('medicine1_time')
							medicine1_days=request.POST.get('medicine1_days')
							medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
							if medicine1=='':
								pass
							else:
								prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
								prescription.medicine1_quantity=medicine1_quantity

							#for medicine 2
							medicine2=request.POST.get('medicine2')
							medicine2_time=request.POST.get('medicine2_time')
							medicine2_days=request.POST.get('medicine2_days')
							medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
							if medicine2=='':
								pass
							else:
								prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
								prescription.medicine2_quantity=medicine2_quantity

							#for medicine 3
							medicine3=request.POST.get('medicine3')
							medicine3_time=request.POST.get('medicine3_time')
							medicine3_days=request.POST.get('medicine3_days')
							medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
							if medicine3=='':
								pass
							else:
								prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
								prescription.medicine3_quantity=medicine3_quantity

							#for medicine 4
							medicine4=request.POST.get('medicine4')
							medicine4_time=request.POST.get('medicine4_time')
							medicine4_days=request.POST.get('medicine4_days')
							medicine4_quantity=count_quantity(medicine4_days,medicine4_time)

							if medicine4=='':
								pass
							else:
								prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
								prescription.medicine4_quantity=medicine4_quantity

							#for medicine 5
							medicine5=request.POST.get('medicine5')
							medicine5_time=request.POST.get('medicine5_time')
							medicine5_days=request.POST.get('medicine5_days')
							medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
							if medicine5=='':
								pass
							else:
								prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
								prescription.medicine5_quantity=medicine5_quantity
							#for medicine 6
							medicine6=request.POST.get('medicine6')
							medicine6_time=request.POST.get('medicine6_time')
							medicine6_days=request.POST.get('medicine6_days')
							medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
							if medicine6=='':
								pass
							else:
								prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
								prescription.medicine6_quantity=medicine6_quantity

							medicine_other=request.POST.get('medicine_other')
							if medicine_other=='':
								pass
							else:
								prescription.medicine_other=request.POST.get('medicine_other')
							prescription.medicine1_name=request.POST.get('medicine1')
							prescription.medicine2_name=request.POST.get('medicine2')
							prescription.medicine3_name=request.POST.get('medicine3')
							prescription.medicine4_name=request.POST.get('medicine4')
							prescription.medicine5_name=request.POST.get('medicine5')
							prescription.medicine6_name=request.POST.get('medicine6')

							#image saving
							prescription.Prescription_img=request.FILES.get('file')
							#follwup_date
							follow_up_date=request.POST.get('followup_date')
							followup_date_unit = request.POST.get('followup_date_unit')
							if follow_up_date == '':
								follow_up_date = None
							prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
							prescription.followup_date_unit = followup_date_unit
							prescription.followup_date = prescription_followup_date
							prescription.save()
							medicine_other=request.POST.get('medicine_other')
							medicine1_name=request.POST.get('medicine1')
							medicine2_name=request.POST.get('medicine2')
							medicine3_name=request.POST.get('medicine3')
							medicine4_name=request.POST.get('medicine4')
							medicine5_name=request.POST.get('medicine5')
							medicine6_name=request.POST.get('medicine6')
							return redirect('vaccination')
					else:
						#if object is not existed in prescription database
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						prescription=Prescription()
						prescription.purpose_id=purpose_pet_obj

						#for medicine 1
						medicine1=request.POST.get('medicine1')
						medicine1_time=request.POST.get('medicine1_time')
						medicine1_days=request.POST.get('medicine1_days')
						medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
						if medicine1=='':
							pass
						else:
							prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
							prescription.medicine1_quantity=medicine1_quantity

						#for medicine 2
						medicine2=request.POST.get('medicine2')
						medicine2_time=request.POST.get('medicine2_time')
						medicine2_days=request.POST.get('medicine2_days')
						medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
						if medicine2=='':
							pass
						else:
							prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
							prescription.medicine2_quantity=medicine2_quantity

						#for medicine 3
						medicine3=request.POST.get('medicine3')
						medicine3_time=request.POST.get('medicine3_time')
						medicine3_days=request.POST.get('medicine3_days')
						medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
						if medicine3=='':
							pass
						else:
							prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
							prescription.medicine3_quantity=medicine3_quantity

						#for medicine 4
						medicine4=request.POST.get('medicine4')
						medicine4_time=request.POST.get('medicine4_time')
						medicine4_days=request.POST.get('medicine4_days')
						medicine4_quantity=count_quantity(medicine4_days,medicine4_time)
						if medicine4=='':
							pass
						else:
							prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
							prescription.medicine4_quantity=medicine4_quantity

						#for medicine 5
						medicine5=request.POST.get('medicine5')
						medicine5_time=request.POST.get('medicine5_time')
						medicine5_days=request.POST.get('medicine5_days')
						medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
						if medicine5=='':
							pass
						else:
							prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
							prescription.medicine5_quantity=medicine5_quantity
						#for medicine 6
						medicine6=request.POST.get('medicine6')
						medicine6_time=request.POST.get('medicine6_time')
						medicine6_days=request.POST.get('medicine6_days')
						medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
						if medicine6=='':
							pass
						else:
							prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
							prescription.medicine6_quantity=medicine6_quantity

						medicine_other=request.POST.get('medicine_other')
						if medicine_other=='':
							pass
						else:
							prescription.medicine_other=request.POST.get('medicine_other')
						prescription.medicine1_name=request.POST.get('medicine1')
						prescription.medicine2_name=request.POST.get('medicine2')
						prescription.medicine3_name=request.POST.get('medicine3')
						prescription.medicine4_name=request.POST.get('medicine4')
						prescription.medicine5_name=request.POST.get('medicine5')
						prescription.medicine6_name=request.POST.get('medicine6')

						#image saving
						prescription.Prescription_img=request.FILES.get('file')
						#follwup_date
						follow_up_date=request.POST.get('followup_date')
						followup_date_unit = request.POST.get('followup_date_unit')
						if follow_up_date == '':
							follow_up_date = None
						prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
						prescription.followup_date_unit = followup_date_unit
						prescription.followup_date = prescription_followup_date
						prescription.save()
						return redirect('vaccination')
				except IntegrityError :
					messages.info(request,'select medicine and days')
					return redirect('prescription_nostock')
			elif 'deworming_name' in request.POST:
				try:
					#if prescription data exists in prescription table
					if Prescription.objects.filter(purpose_id=purpose_pet_obj).exists() :

						if request.method=='POST':
							Prescription.objects.filter(purpose_id=purpose_pet_obj).delete()
							purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
							prescription=Prescription()
							prescription.purpose_id=purpose_pet_obj

							#for medicine 1
							medicine1=request.POST.get('medicine1')
							medicine1_time=request.POST.get('medicine1_time')
							medicine1_days=request.POST.get('medicine1_days')
							medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
							if medicine1=='':
								pass
							else:
								prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
								prescription.medicine1_quantity=medicine1_quantity

							#for medicine 2
							medicine2=request.POST.get('medicine2')
							medicine2_time=request.POST.get('medicine2_time')
							medicine2_days=request.POST.get('medicine2_days')
							medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
							if medicine2=='':
								pass
							else:
								prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
								prescription.medicine2_quantity=medicine2_quantity

							#for medicine 3
							medicine3=request.POST.get('medicine3')
							medicine3_time=request.POST.get('medicine3_time')
							medicine3_days=request.POST.get('medicine3_days')
							medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
							if medicine3=='':
								pass
							else:
								prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
								prescription.medicine3_quantity=medicine3_quantity

							#for medicine 4
							medicine4=request.POST.get('medicine4')
							medicine4_time=request.POST.get('medicine4_time')
							medicine4_days=request.POST.get('medicine4_days')
							medicine4_quantity=count_quantity(medicine4_days,medicine4_time)

							if medicine4=='':
								pass
							else:
								prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
								prescription.medicine4_quantity=medicine4_quantity

							#for medicine 5
							medicine5=request.POST.get('medicine5')
							medicine5_time=request.POST.get('medicine5_time')
							medicine5_days=request.POST.get('medicine5_days')
							medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
							if medicine5=='':
								pass
							else:
								prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
								prescription.medicine5_quantity=medicine5_quantity
							#for medicine 6
							medicine6=request.POST.get('medicine6')
							medicine6_time=request.POST.get('medicine6_time')
							medicine6_days=request.POST.get('medicine6_days')
							medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
							if medicine6=='':
								pass
							else:
								prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
								prescription.medicine6_quantity=medicine6_quantity

							medicine_other=request.POST.get('medicine_other')
							if medicine_other=='':
								pass
							else:
								prescription.medicine_other=request.POST.get('medicine_other')
							prescription.medicine1_name=request.POST.get('medicine1')
							prescription.medicine2_name=request.POST.get('medicine2')
							prescription.medicine3_name=request.POST.get('medicine3')
							prescription.medicine4_name=request.POST.get('medicine4')
							prescription.medicine5_name=request.POST.get('medicine5')
							prescription.medicine6_name=request.POST.get('medicine6')

							#image saving
							prescription.Prescription_img=request.FILES.get('file')
							#follwup_date
							follow_up_date=request.POST.get('followup_date')
							followup_date_unit = request.POST.get('followup_date_unit')
							if follow_up_date == '':
								follow_up_date = None
							prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
							prescription.followup_date_unit = followup_date_unit
							prescription.followup_date = prescription_followup_date
							prescription.save()
							medicine_other=request.POST.get('medicine_other')
							medicine1_name=request.POST.get('medicine1')
							medicine2_name=request.POST.get('medicine2')
							medicine3_name=request.POST.get('medicine3')
							medicine4_name=request.POST.get('medicine4')
							medicine5_name=request.POST.get('medicine5')
							medicine6_name=request.POST.get('medicine6')
							return redirect('deworming')
					else:
						#if object is not existed in prescription database
						purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
						prescription=Prescription()
						prescription.purpose_id=purpose_pet_obj

						#for medicine 1
						medicine1=request.POST.get('medicine1')
						medicine1_time=request.POST.get('medicine1_time')
						medicine1_days=request.POST.get('medicine1_days')
						medicine1_quantity=count_quantity(medicine1_days,medicine1_time)
						if medicine1=='':
							pass
						else:
							prescription.medicine1=medicine1+'  '+' '+medicine1_time+' '+medicine1_days+' '+str(medicine1_quantity) +' '+'Tablets'
							prescription.medicine1_quantity=medicine1_quantity

						#for medicine 2
						medicine2=request.POST.get('medicine2')
						medicine2_time=request.POST.get('medicine2_time')
						medicine2_days=request.POST.get('medicine2_days')
						medicine2_quantity=count_quantity(medicine2_days,medicine2_time)
						if medicine2=='':
							pass
						else:
							prescription.medicine2=medicine2+'  '+' '+medicine2_time+' '+medicine2_days+' '+str(medicine2_quantity) +' '+'Tablets'
							prescription.medicine2_quantity=medicine2_quantity

						#for medicine 3
						medicine3=request.POST.get('medicine3')
						medicine3_time=request.POST.get('medicine3_time')
						medicine3_days=request.POST.get('medicine3_days')
						medicine3_quantity=count_quantity(medicine3_days,medicine3_time)
						if medicine3=='':
							pass
						else:
							prescription.medicine3=medicine3+'  '+' '+medicine3_time+' '+medicine3_days+' '+str(medicine3_quantity)+' '+'Tablets'
							prescription.medicine3_quantity=medicine3_quantity

						#for medicine 4
						medicine4=request.POST.get('medicine4')
						medicine4_time=request.POST.get('medicine4_time')
						medicine4_days=request.POST.get('medicine4_days')
						medicine4_quantity=count_quantity(medicine4_days,medicine4_time)
						if medicine4=='':
							pass
						else:
							prescription.medicine4=medicine4+'  '+' '+medicine4_time+' '+medicine4_days+' '+str(medicine4_quantity)+' '+'Tablets'
							prescription.medicine4_quantity=medicine4_quantity

						#for medicine 5
						medicine5=request.POST.get('medicine5')
						medicine5_time=request.POST.get('medicine5_time')
						medicine5_days=request.POST.get('medicine5_days')
						medicine5_quantity=count_quantity(medicine5_days,medicine5_time)
						if medicine5=='':
							pass
						else:
							prescription.medicine5=medicine5+' '+' '+medicine5_time+' '+medicine5_days+' '+str(medicine5_quantity)+' '+'Tablets'
							prescription.medicine5_quantity=medicine5_quantity
						#for medicine 6
						medicine6=request.POST.get('medicine6')
						medicine6_time=request.POST.get('medicine6_time')
						medicine6_days=request.POST.get('medicine6_days')
						medicine6_quantity=count_quantity(medicine6_days,medicine6_time)
						if medicine6=='':
							pass
						else:
							prescription.medicine6=medicine6+'  '+' '+medicine6_time+' '+medicine6_days+' '+str(medicine6_quantity)+' '+'Tablets'
							prescription.medicine6_quantity=medicine6_quantity

						medicine_other=request.POST.get('medicine_other')
						if medicine_other=='':
							pass
						else:
							prescription.medicine_other=request.POST.get('medicine_other')
						prescription.medicine1_name=request.POST.get('medicine1')
						prescription.medicine2_name=request.POST.get('medicine2')
						prescription.medicine3_name=request.POST.get('medicine3')
						prescription.medicine4_name=request.POST.get('medicine4')
						prescription.medicine5_name=request.POST.get('medicine5')
						prescription.medicine6_name=request.POST.get('medicine6')

						#image saving
						prescription.Prescription_img=request.FILES.get('file')
						#follwup_date
						follow_up_date=request.POST.get('followup_date')
						followup_date_unit = request.POST.get('followup_date_unit')
						if follow_up_date == '':
							follow_up_date = None
						prescription_followup_date=prescription_date_format(follow_up_date,followup_date_unit)
						prescription.followup_date_unit = followup_date_unit
						prescription.followup_date = prescription_followup_date
						prescription.save()
						return redirect('deworming')
				except IntegrityError :
					messages.info(request,'select medicine and days')
					return redirect('prescription_nostock')
			else:
				return redirect('prescription_nostock')

def summary(request):
	doc_pk = request.session.get('doc_pk')
	purpose_pk = request.session.get('purpose_pk')
	pet_pk = request.session.get('pet_pk')
	purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
	visite_on=date.today()
	if pet_pk:
		pet_pk=pet_pk
	else:
		pass

	try:
		vitals=Vitals.objects.filter(purpose_id=purpose_pet_obj,date=visite_on).last()
		vitals=model_to_dict(vitals)
		clean_dict = dict_clean(vitals)
		vitals = clean_dict

	except:
		pass

	try:
		assessment=Assessment.objects.filter(purpose_id=purpose_pet_obj,date=visite_on).last()
		assessment=model_to_dict(assessment)
		clean_dict = dict_clean(assessment)
		clean_dict=remove_empty_from_dict(clean_dict)
		assessment = clean_dict
	except:
		pass

	try:

		symptoms=purpose_pet_obj
		symptoms=model_to_dict(symptoms)
		symptoms.pop('purpose_id',None)
		symptoms.pop('id',None)
		symptoms.pop('pet_id',None)

		symptoms.pop('vaccination_purpose',None)
		symptoms.pop('deworming_purpose',None)
		symptoms.pop('last_deworming',None)
		symptoms.pop('status',None)
		symptoms = dict_clean(symptoms)
	except:
		pass

	try:

		diagnostic=Diagnostics.objects.filter(purpose_id=purpose_pet_obj,date=visite_on).last()
		diagnostic=model_to_dict(diagnostic)
		clean_dict = dict_clean(diagnostic)
		diagnostic = remove_empty_from_dict(clean_dict)
	except:
		pass

	try:
		prescription=Prescription.objects.filter(purpose_id=purpose_pet_obj).last()
		prescription_image=Prescription.objects.filter(purpose_id=purpose_pet_obj).last()
		prescription=model_to_dict(prescription)
		clean_dict=dict_clean(prescription)
		prescription=remove_empty_from_dict(prescription)
		prescription.pop('purpose_id',None)
		prescription.pop('id',None)
		prescription.pop('date',None)
		prescription.pop('medicine1_name',None)
		prescription.pop('medicine2_name',None)
		prescription.pop('medicine3_name',None)
		prescription.pop('medicine4_name',None)
		prescription.pop('medicine5_name',None)
		prescription.pop('medicine6_name',None)
		prescription.pop('medicine1_quantity',None)
		prescription.pop('medicine2_quantity',None)
		prescription.pop('medicine3_quantity',None)
		prescription.pop('medicine4_quantity',None)
		prescription.pop('medicine5_quantity',None)
		prescription.pop('medicine6_quantity',None)
		prescription.pop('followup_date_unit',None)


	except:
		pass

	try:
		vaccination=Vaccination.objects.filter(purpose_id=purpose_pet_obj).last()
		vaccination=model_to_dict(vaccination)
		vaccination.pop('purpose_id',None)
		vaccination.pop('id',None)
		vaccination.pop('date',None)
		vaccination.pop('pet',None)
		vaccination = { k:v for k,v in vaccination.items() if v!= datetime.date(1000, 1, 1) }
		vaccination=vaccination_dict(vaccination)
	except:
		pass
	try:
		deworming=Deworming.objects.filter(purpose_id=purpose_pet_obj).last()
		deworming=model_to_dict(deworming)
		deworming.pop('purpose_id',None)
		deworming.pop('id',None)
		deworming.pop('date',None)
		deworming.pop('pet',None)
		deworming = { k:v for k,v in deworming.items() if v!= datetime.date(1000, 1, 1) }
		deworming=vaccination_dict(deworming)

	except:
		pass

	if request.method == "GET":
		if 'doc_pk' in request.session:
			return render(request,'doctor/Doctor_summary.html',
			{'symptoms':symptoms,'vitals':vitals,'assessment':assessment,
			'symptoms':symptoms,'diagnostic':diagnostic,
			'prescription':prescription,'vaccination':vaccination,
			'deworming':deworming,'visite_on':visite_on,
			'prescription_image':prescription_image,'media_url':settings.MEDIA_URL,})
		else:
			return redirect('doctor_login')

	if request.method=='POST':
		PurposeAndDiet.objects.filter(id=purpose_pk).update(status='C')
		Log.objects.filter(purpose_id=purpose_pet_obj).update(status='C')
		DoctorViewLog.objects.filter(purpose_id=purpose_pet_obj).update(status='C')
		doc_id = DoctorViewLog.objects.filter(
			purpose_id=purpose_pet_obj).last().doc_pk
		doc_id = doc_id.id
		try:
			customer_mobile = Pet.objects.get(id=pet_pk).customer_id.mobile
			doctor_clinic = Doctor.objects.get(id=doc_id).Hospital
			purpose_obj = PurposeAndDiet.objects.get(id=purpose_pk).id
			followup_date = Prescription.objects.get(
				purpose_id=purpose_obj).followup_date
			database_message = Doctor.objects.get(id=doc_id).message
			if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
			getattr(ssl, '_create_unverified_context', None)):
				ssl._create_default_https_context = ssl._create_unverified_context
			authkey = "334231AXCttMDRD5efc1d91P1"
			mobiles = customer_mobile
			message = 'thanks for visiting'+doctor_clinic+','+database_message+'your folowup date is ' + \
						str(followup_date)+'you can book appointment at' + \
						'https://aodhpet.com/registration/' + \
						str(doc_id)+'/'
			sender = "AODHPC"
			route = "4"  # Define route
			print(followup_date)
			if str(followup_date) == '1000-01-01':
				message = 'thanks for visiting'+doctor_clinic+','+database_message+'you can book appointment at'+'https://aodhpet.com/registration/'+str(doc_id)+'/'
			values = {
						'authkey': authkey,
						'mobiles': mobiles,
						'message': message,
						'sender': sender,
						'route': route
					}
			url = "http://api.msg91.com/api/sendhttp.php"  # API URL

			# URL encoding the data here.
			postdata = urllib.parse.urlencode(values).encode("utf-8")

			req = urllib2.Request(url, postdata)

			response = urllib.request.urlopen(req)
			output = response.read()  # Get Response
		except:
			pass
		return redirect	('list_patient')

#Main Visit views completed

##############################################################
#Doctor side bar view_seminar
##############################################################
#Doctor Profile view

def doctorprofile(request):
	if 'doc_pk' in request.session:
		doc_pk = request.session.get('doc_pk')
		doc_obj=Doctor.objects.get(id=doc_pk)
		return render(request,'doctor/doctor_profile.html',
			{'doc':doc_obj,'doc_pk':doc_pk,'doc_obj':doc_obj})
	else:
		return redirect('doctor_login')
	if request.method=="POST":
		if 'change_password' in request.POST:
			cuurent_password=request.POST.get('current_password')
			new_password=request.POST.get('confirm_password')
			previous_password=doc.password
			if cuurent_password==previous_password:
				Doctor.objects.filter(id=doc_pk).update(password=new_password)
				return redirect('doctor_login')
			else:
				messages.info(request,'current password is wrong')
				return redirect('doctor_profile',doc_pk=doc_pk)

def doctor_articles(request):
	if 'doc_pk' in request.session:
		doc_id = request.session.get('doc_pk')
		doctor=Doctor.objects.get(id=doc_id)
		article=Articles.objects.all()
		bookmark=bookmarks_article.objects.filter(doc=doctor).all()
		x=[]
		for i in bookmark:
			x.append(i.article_id.id)
		return render(request,'doctor_corner/Doctors_corner_articles.html',
		{'article':article,'doc_id':doc_id,'bookmark':bookmark,'y':x})
	else:
		return redirect('doctor_login')

def doctor_view_article(request):
	if 'doc_pk' in request.session:
		pk = request.session.get('doc_pk')
		if pk:
			article = Articles.objects.filter(id=pk)
			for i in article:
				print(i.article_title)
			return render (request, 'doctor_corner/Doctors_corner_viewarticle.html',{'article':article})
		return render (request, 'doctor_corner/Doctors_corner_viewarticle.html')
	else:
		return redirect('doctor_login')

def case_reports_sbar(request):
	if 'doc_pk' in request.session:
		doc_id = request.session.get('doc_pk')
		doctor=Doctor.objects.get(id=doc_id)
		case_reports=Case_Reports.objects.all()
		bookmark=bookmarks_case_reports.objects.filter(doc=doctor).all()
		x=[]
		for i in bookmark:
			x.append(i.case_reports.id)
		if request.method == 'POST':
			report_pk = request.POST.get('report_pk')
		return render(request,'doctor_corner/Doctors_corner_case_reports.html',
			{'case_reports':case_reports,'doc_id':doc_id,'x':x})
	else:
		return redirect('doctor_login')

def conferences_sbar(request):
	if 'doc_pk' in request.session:
		doc_id = request.session.get('doc_pk')
		doctor=Doctor.objects.get(id=doc_id)
		conferences=Conferences.objects.all()
		bookmark=bookmarks_conferences.objects.filter(doc=doctor).all()
		x=[]
		for i in bookmark:
			x.append(i.conferences.id)
		if request.method == 'POST':
			con_pk = request.POST.get('con_pk')
		return render(request,'doctor_corner/doctors_corner_conferences.html',
			{'conferences':conferences,'doc_id':doc_id,'x':x})
	else:
		return redirect('doctor_login')

def vet_news_sbar(request):
	if 'doc_pk' in request.session:
		doc_id = request.session.get('doc_pk')
		doctor=Doctor.objects.get(id=doc_id)
		vetnewsobj=Vet_News.objects.all()
		bookmark=bookmarks_vet_news.objects.filter(doc=doctor).all()
		x=[]
		for i in bookmark:
			x.append(i.vet_news.id)
		if request.method == 'POST':
			vn_pk = request.POST.get('vn_pk')
		return render(request,'doctor_corner/Doctors_corner_vet_news.html',
			{'vetnewsobj':vetnewsobj,'doc_id':doc_id,'x':x})
	else:
		return redirect('doctor_login')

def seminars_sbar(request):
	if 'doc_pk' in request.session:
		doc_id = request.session.get('doc_pk')
		doctor=Doctor.objects.get(id=doc_id)
		seminars=Seminars.objects.all()
		bookmark=bookmarks_seminars.objects.filter(doc=doctor).all()
		x=[]
		for i in bookmark:
			x.append(i.seminars.id)
		if request.method == 'POST':
			sem_pk = request.POST.get('sem_pk')

		return render(request,'doctor_corner/Doctors_corner_seminars.html',
			{'seminars':seminars,'doc_id':doc_id,'x':x})
	else:
		return redirect('doctor_login')

def view_seminar_sbar(request,pk):
	if 'doc_pk' in request.session:
		if request.method == 'GET':
			return render (request, 'doctor_corner/Doctors_corner_view_seminar.html')
	else:
		return redirect('doctor_login')
	if request.method == 'POST':
	    if pk:
	        seminar = Seminars.objects.filter(id=pk)
	        return render (request, 'doctor_corner/Doctors_corner_view_seminar.html',{'seminars':seminar,})

def books_sbar(request):
	if 'doc_pk' in request.session:
		doc_id = request.session.get('doc_pk')
		doctor=Doctor.objects.get(id=doc_id)
		book=Book.objects.all()
		bookmark=bookmarks_books.objects.filter(doc=doctor).all()
		x=[]
		for i in bookmark:
			x.append(i.books.id)
		return render(request,'doctor_corner/Doctors_corner_books.html',
			{'book':book,'doc_id':doc_id,'x':x,'media_url':settings.MEDIA_URL,})
	else:
		return redirect('doctor_login')

def articlepk(request):
	if 'doc_pk' in request.session:
		x=request.POST.get('obj',None)
		y=request.POST.get('doc',None)
		bmark=bookmarks_article()
		doc=Doctor.objects.get(id=y)
		article_id=Articles.objects.get(id=x)
		if bookmarks_article.objects.filter(article_id=article_id,doc=doc).exists():
			bookmarks_article.objects.filter(doc=doc,article_id=article_id).last().delete()
		else:
			bmark.doc=Doctor.objects.get(id=y)
			bmark.article_id=Articles.objects.get(id=x)
			bmark.save()
		data ={
			'hello':'hello'
		}
		return JsonResponse(data)
	else:
		return redirect('doctor_login')

def casereportspk(request):
	if 'doc_pk' in request.session:
		x=request.POST.get('obj',None)
		y=request.POST.get('doc',None)
		bmark=bookmarks_case_reports()
		doc=Doctor.objects.get(id=y)
		Case_Reports_id=Case_Reports.objects.get(id=x)
		if bookmarks_case_reports.objects.filter(case_reports=Case_Reports_id,doc=doc).exists():
			bookmarks_case_reports.objects.filter(doc=doc,case_reports=Case_Reports_id).last().delete()
		else:
			bmark.doc=Doctor.objects.get(id=y)
			bmark.case_reports=Case_Reports.objects.get(id=x)
			bmark.save()
		data ={
			'hello':'hello'
		}
		return JsonResponse(data)
	else:
		return redirect('doctor_login')

def conferencepk(request):
	if 'doc_pk' in request.session:
		x=request.POST.get('obj',None)
		y=request.POST.get('doc',None)
		bmark=bookmarks_conferences()
		doc=Doctor.objects.get(id=y)
		conference_id=Conferences.objects.get(id=x)
		if bookmarks_conferences.objects.filter(conferences=conference_id,doc=doc).exists():
			bookmarks_conferences.objects.filter(doc=doc,conferences=conference_id).last().delete()
		else:
			bmark.doc=Doctor.objects.get(id=y)
			bmark.conferences=Conferences.objects.get(id=x)
			bmark.save()
		data ={
			'hello':'hello'
		}
		return JsonResponse(data)
	else:
		return redirect('doctor_login')

def seminarspk(request):
	if 'doc_pk' in request.session:
		x=request.POST.get('obj',None)
		y=request.POST.get('doc',None)
		bmark=bookmarks_seminars()
		doc=Doctor.objects.get(id=y)
		seminars_id=Seminars.objects.get(id=x)
		if bookmarks_seminars.objects.filter(seminars=seminars_id,doc=doc).exists():
			bookmarks_seminars.objects.filter(doc=doc,seminars=seminars_id).last().delete()
		else:
			bmark.doc=Doctor.objects.get(id=y)
			bmark.seminars=Seminars.objects.get(id=x)
			bmark.save()
		data ={
			'hello':'hello'
		}
		return JsonResponse(data)
	else:
		return redirect('doctor_login')

def vetnewspk(request):
	if 'doc_pk' in request.session:
		x=request.POST.get('obj',None)
		y=request.POST.get('doc',None)
		bmark=bookmarks_vet_news()
		doc=Doctor.objects.get(id=y)
		vet_news_id=Vet_News.objects.get(id=x)
		if bookmarks_vet_news.objects.filter(vet_news=vet_news_id,
			doc=doc).exists():
			bookmarks_vet_news.objects.filter(doc=doc,
				vet_news=vet_news_id).last().delete()
		else:
			bmark.doc=Doctor.objects.get(id=y)
			bmark.vet_news=Vet_News.objects.get(id=x)
			bmark.save()
		data ={
			'hello':'hello'
		}
		return JsonResponse(data)
	else:
		return redirect('doctor_login')

def bookspk(request):
	if 'doc_pk' in request.session:
		x=request.POST.get('obj',None)
		y=request.POST.get('doc',None)
		bmark=bookmarks_books()
		doc=Doctor.objects.get(id=y)
		books_id=Book.objects.get(id=x)
		if bookmarks_books.objects.filter(books=books_id,doc=doc).exists():
			bookmarks_books.objects.filter(doc=doc,books=books_id).last().delete()
		else:
			bmark.doc=Doctor.objects.get(id=y)
			bmark.books=Book.objects.get(id=x)
			bmark.save()
		data ={
			'hello':'hello'
		}
		return JsonResponse(data)
	else:
		return redirect('doctor_login')

def bookmarks(request):
	if 'doc_pk' in request.session:
		doc_id = request.session.get('doc_pk')
		doctor=doc_id
		doc_pk=Doctor.objects.get(id=doc_id)
		try:
			articles=bookmarks_article.objects.filter(doc=doctor).all()
		except:
			pass
		try:
			case_reports=bookmarks_case_reports.objects.filter(doc=doctor).all()
		except:
			pass
		try:
			conferences=bookmarks_conferences.objects.filter(doc=doctor).all()
		except:
			pass
		try:
			vet_news=bookmarks_vet_news.objects.filter(doc=doctor).all()
		except:
			pass
		try:
			seminars=bookmarks_seminars.objects.filter(doc=doctor).all()
		except:
			pass
		try:
			books=bookmarks_books.objects.filter(doc=doctor).all()
		except:
			pass
		return render(request,'doctor_corner/bookmarks.html',
			{'articles':articles,'case_reports':case_reports,
			'conferences':conferences,'vet_news':vet_news,'seminars':seminars,
			'books':books,'doc_id':doc_id,'doc_pk':doc_pk,
			'media_url':settings.MEDIA_URL})
	else:
		return redirect('doctor_login')

def doctoranalytics(request):
	if 'doc_pk' in request.session:
		doc_pk = request.session.get('doc_pk')
		previous_chat_all=doctor_message.objects.filter(doctor__id=doc_pk).all()
		all_customers=DoctorViewLog.objects.filter(doc_pk=doc_pk,status='C').all()
		total_message_list=doctor_message.objects.filter(doctor__id=doc_pk).all()
		if request.method == "GET":
			return render(request,'doctor/doctor_analytics.html',
			{'doc_pk':doc_pk,'total_message_list':total_message_list,
			'all_customers':all_customers,})
	else:
		return redirect('doctor_login')
	if request.method=='POST':
		visit_date=request.POST.get('visit_date')
		visit_date=datetime.datetime.strptime(visit_date, "%d/%m/%Y").date()
		fee=DoctorViewLog.objects.filter(booking_date=visit_date,
			doc_pk=doc_pk,status='C').all()
		return render(request,'doctor/doctor_analytics.html',
			{'visit_date':visit_date,'all_customers':fee,
			'doc_pk':doc_pk,
			'previous_chat_all':previous_chat_all,})


def summary_analytics(request,purpose_id):
	doc_pk = request.session.get('doc_pk')
	try:
		symptoms=PurposeAndDiet.objects.get(id=purpose_id)
		print(symptoms)
		symptoms=model_to_dict(symptoms)
		symptoms.pop('purpose_id',None)
		symptoms.pop('pet_id',None)
		symptoms.pop('id',None)
		symptoms.pop('date',None)
		symptoms.pop('status',None)
		symptoms.pop('vaccination_purpose',None)
		clean_dict = dict_clean(symptoms)
		symptoms=remove_empty_from_dict(clean_dict)
	except:
		symptoms=''
	try:
		vitals=Vitals.objects.get(purpose_id__id=purpose_id)
		vitals=model_to_dict(vitals)
		vitals.pop('purpose_id',None)
		vitals.pop('id',None)
		vitals.pop('date',None)
		clean_dict = dict_clean(vitals)
		vitals=remove_empty_from_dict(clean_dict)
	except:
		vitals=''
	try:
		diagnostics=Diagnostics.objects.get(purpose_id__id=purpose_id)
		diagnostics=model_to_dict(diagnostics)
		diagnostics.pop('purpose_id',None)
		diagnostics.pop('id',None)
		diagnostics.pop('date',None)
		clean_dict = dict_clean(diagnostics)
		diagnostics=remove_empty_from_dict(clean_dict)
	except:
		diagnostics=''
	try:
		prescription=Prescription.objects.get(purpose_id__id=purpose_id)
		prescription_image=Prescription.objects.get(purpose_id__id=purpose_id)
		prescription=model_to_dict(prescription)
		prescription.pop('purpose_id',None)
		prescription.pop('id',None)
		prescription.pop('date',None)
		prescription.pop('medicine1_name',None)
		prescription.pop('medicine2_name',None)
		prescription.pop('medicine3_name',None)
		prescription.pop('medicine4_name',None)
		prescription.pop('medicine5_name',None)
		prescription.pop('medicine6_name',None)
		prescription.pop('medicine1_quantity',None)
		prescription.pop('medicine2_quantity',None)
		prescription.pop('medicine3_quantity',None)
		prescription.pop('medicine4_quantity',None)
		prescription.pop('medicine5_quantity',None)
		prescription.pop('medicine6_quantity',None)
		prescription.pop('medicine1_dosage_quantity',None)
		prescription.pop('medicine2_dosage_quantity',None)
		prescription.pop('medicine3_dosage_quantity',None)
		prescription.pop('medicine4_dosage_quantity',None)
		prescription.pop('medicine5_dosage_quantity',None)
		prescription.pop('medicine6_dosage_quantity',None)
		prescription.pop('followup_date_unit',None)
		# clean_dict = dict_clean(prescription)
		prescription=remove_empty_from_dict(prescription)

	except:
		prescription=''
		prescription_image=''
	try:
		assessment=Assessment.objects.get(purpose_id__id=purpose_id)
		assessment=model_to_dict(assessment)
		assessment.pop('purpose_id',None)
		assessment.pop('id',None)
		assessment.pop('date',None)
		clean_dict = dict_clean(assessment)
		assessment=remove_empty_from_dict(clean_dict)
	except:
		assessment=''
	try:
		deworming=Deworming.objects.get(purpose_id__id=purpose_id)
		deworming=model_to_dict(deworming)
		deworming.pop('purpose_id',None)
		deworming.pop('id',None)
		deworming.pop('date',None)
		deworming.pop('pet',None)
		deworming = { k:v for k,v in deworming.items() if v!= datetime.date(1000, 1, 1) }
		deworming=vaccination_dict(deworming)
	except:
		deworming=''
	try:
		vaccination=Vaccination.objects.get(purpose_id__id=purpose_id)
		vaccination=model_to_dict(vaccination)
		vaccination.pop('purpose_id',None)
		vaccination.pop('id',None)
		vaccination.pop('date',None)
		vaccination.pop('pet',None)
		vaccination = { k:v for k,v in vaccination.items() if v!= datetime.date(1000, 1, 1) }
		vaccination=vaccination_dict(vaccination)
	except:
		vaccination=''
	if request.method == "GET":
		if 'doc_pk' in request.session:
			return render (request,'doctor/summary_analytics.html',
				{'symptoms':symptoms,'vitals':vitals,'diagnostic':diagnostics,
				'prescription':prescription,'assessment':assessment,
				'deworming':deworming,'doc_pk':doc_pk,
				'vaccination':vaccination,'prescription_image':prescription_image,
				'media_url':settings.MEDIA_URL,})

		else:
			return redirect('doctor_login')


def stocks(request):
	if 'doc_pk' in request.session:
		doc_id = request.session.get('doc_pk')
		x=stock.objects.filter(doctor__id=doc_id)
		doc_pk=Doctor.objects.get(id=doc_id)
		if request.method=="POST":
			meda=request.POST.get('medicine1')
			medb=request.POST.get('drug1_mg_quantity')
			othermed=request.POST.get('other_medicine')
			other_med_quantity=request.POST.get('other_medicine_quantity')
			doc=Doctor.objects.get(id=doc_id)
			stock.objects.filter(doctor__id=doc_id).create(other_medicine=othermed)
			if stock.objects.filter(doctor__id=doc_id).exists():
				stock.objects.filter(doctor__id=doc_id).update(other_medicine=othermed,
					other_medicine_quantity=other_med_quantity)
		return render(request,'doctor/stock_management.html',
			{'x':x,'doc_id':doc_id,'doc_pk':doc_pk})
	else:
		return redirect('doctor_login')

def stockadd(request,doc_id):
	if 'doc_pk' in request.session:
		stoc=stock.objects.filter(doctor__id=doc_id)
		if request.method=='POST':
			doc=Doctor.objects.get(id=doc_id)
			ourid = json.loads(request.POST.get('z'))
			print(ourid)
			b = {ourid[i]: ourid[i+1] for i in range(0, len(ourid), 2)}
			print(b)
			for key, value in b.items():
				if key!="" and value!="":
					if stock.objects.filter(doctor__id=doc_id,medicine=key).exists():
						z=stock.objects.filter(doctor__id=doc_id,
							medicine=key).last().quantity
						z=int(z)
						medb=int(value)
						added=z+medb
						stock.objects.filter(doctor__id=doc_id,
							medicine=key).update(quantity=added)
					else:
						st=stock()
						st.doctor=doc
						st.medicine=key
						st.quantity=value
						st.save()

			return redirect('stocks')
		return redirect('stocks')
	else:
		return redirect('doctor_login')

def stockdelete(request):
	if 'doc_pk' in request.session:
		if request.method=="POST":
				doc_id=request.POST.get('doc_id')
				del_medicine=json.loads(request.POST.get('del_medicine'))
				print(del_medicine)
				try:
					for i in del_medicine:
						stock.objects.filter(doctor__id=doc_id,medicine=i).delete()
				except:
					pass
		return HttpResponse('ok')
	else:
		return redirect('doctor_login')

def customer_previous(request,customer_id,pet_id):

	if request.method == "GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id :
				customer_id=customer_id
				pet_obj=Pet.objects.get(pet_id=pet_id)
				purpose_pet_obj=PurposeAndDiet.objects.filter(pet_id=pet_obj,status='C').all()

				visite_on=date.today()
				return render(request,'customer/Customer_previous_visit.html',{'purpose_pet_obj':purpose_pet_obj})
			else:
				return redirect('customer_login_home')
		else:
			return redirect('customer_login_home')

def summary_customer(request,purpose_id):

	purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_id)
	visite_on=date.today()

	try:
		vitals=Vitals.objects.filter(purpose_id=purpose_pet_obj).last()
		vitals=model_to_dict(vitals)
		clean_dict = dict_clean(vitals)
		vitals = clean_dict

	except:
		pass

	try:
		assessment=Assessment.objects.filter(purpose_id=purpose_pet_obj).last()
		assessment=model_to_dict(assessment)
		clean_dict = dict_clean(assessment)
		clean_dict=remove_empty_from_dict(clean_dict)
		assessment = clean_dict
	except:
		pass

	try:

		symptoms=purpose_pet_obj
		symptoms=model_to_dict(symptoms)
		symptoms.pop('purpose_id',None)
		symptoms.pop('id',None)
		symptoms.pop('pet_id',None)

		symptoms.pop('vaccination_purpose',None)
		symptoms.pop('deworming_purpose',None)
		symptoms.pop('last_deworming',None)
		symptoms.pop('status',None)
		symptoms = dict_clean(symptoms)
	except:
		pass

	try:

		diagnostic=Diagnostics.objects.filter(purpose_id=purpose_pet_obj).last()
		diagnostic=model_to_dict(diagnostic)
		clean_dict = dict_clean(diagnostic)
		diagnostic = remove_empty_from_dict(clean_dict)
	except:
		pass

	try:
		prescription=Prescription.objects.filter(purpose_id=purpose_pet_obj).last()
		prescription_image=Prescription.objects.filter(purpose_id=purpose_pet_obj).last()
		prescription=model_to_dict(prescription)
		clean_dict=dict_clean(prescription)
		prescription=remove_empty_from_dict(prescription)
		prescription.pop('purpose_id',None)
		prescription.pop('id',None)
		prescription.pop('date',None)
		prescription.pop('medicine1_name',None)
		prescription.pop('medicine2_name',None)
		prescription.pop('medicine3_name',None)
		prescription.pop('medicine4_name',None)
		prescription.pop('medicine5_name',None)
		prescription.pop('medicine6_name',None)
		prescription.pop('medicine1_quantity',None)
		prescription.pop('medicine2_quantity',None)
		prescription.pop('medicine3_quantity',None)
		prescription.pop('medicine4_quantity',None)
		prescription.pop('medicine5_quantity',None)
		prescription.pop('medicine6_quantity',None)
		prescription.pop('medicine1_dosage_quantity',None)
		prescription.pop('medicine2_dosage_quantity',None)
		prescription.pop('medicine3_dosage_quantity',None)
		prescription.pop('medicine4_dosage_quantity',None)
		prescription.pop('medicine5_dosage_quantity',None)
		prescription.pop('medicine6_dosage_quantity',None)
		prescription.pop('followup_date_unit',None)

	except:
		pass
		prescription_image=''

	try:
		vaccination=Vaccination.objects.filter(purpose_id=purpose_pet_obj).last()
		vaccination=model_to_dict(vaccination)
		vaccination.pop('purpose_id',None)
		vaccination.pop('id',None)
		vaccination.pop('date',None)
		vaccination.pop('pet',None)
		vaccination = { k:v for k,v in vaccination.items() if v!= datetime.date(1000, 1, 1) }
		vaccination=vaccination_dict(vaccination)
	except:
		pass
	try:
		deworming=Deworming.objects.filter(purpose_id=purpose_pet_obj).last()
		deworming=model_to_dict(deworming)
		deworming.pop('purpose_id',None)
		deworming.pop('id',None)
		deworming.pop('date',None)
		deworming.pop('pet',None)
		deworming = { k:v for k,v in deworming.items() if v!= datetime.date(1000, 1, 1) }
		deworming=vaccination_dict(deworming)

	except:
		pass

	if request.method == "GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			return render(request,'customer/Customer_previous_visit_summary.html',{'symptoms':symptoms,'vitals':vitals,'assessment':assessment,'symptoms':symptoms,
				'diagnostic':diagnostic,'purpose_pet_obj':purpose_pet_obj,'vaccination':vaccination,'deworming':deworming,'prescription':prescription,'prescription_image':prescription_image,'media_url':settings.MEDIA_URL,})
		elif 'aodh_admin' in request.session:
			return render(request,'customer/Customer_previous_visit_summary.html',{'symptoms':symptoms,'vitals':vitals,'assessment':assessment,'symptoms':symptoms,
				'diagnostic':diagnostic,'purpose_pet_obj':purpose_pet_obj,'vaccination':vaccination,'deworming':deworming,'prescription':prescription,'prescription_image':prescription_image,'media_url':settings.MEDIA_URL,})
		else:
			return redirect('customer_login_home')


def doctor(request):
	doclist=Doctor.objects.last()
	doclist=model_to_dict(doclist)
	if request.method == "GET":
		if 'doctor_session_id' in request.session:
			return render(request,'doctorreg.html',{'doclist':doclist})
		else:
			return redirect('doctor_login')
	if request.method=='POST':
		doctor=Doctor()
		doctor.Name_of_doctor=request.POST.get('Name_of_doctor')
		doctor.Qualification=request.POST.get('Qualification')
		doctor.Registration_number=request.POST.get('Registration_number')
		doctor.Gender=request.POST.get('Gender')
		doctor.Date_of_birth=request.POST.get('Date_of_birth')
		doctor.Experience=request.POST.get('Experience')
		doctor.Hospital=request.POST.get('Hospital')
		doctor.Email=request.POST.get('Email')
		doctor.Mobile=request.POST.get('Mobile')
		doctor.Telephone=request.POST.get('Telephone')
		doctor.Address=request.POST.get('Address')
		doctor.save()
		return render(request,'doctorreg.html')



def doctor_history(request):
	doc_pk = request.session.get('doc_pk')
	pet_pk = request.session.get('pet_pk')
	purpose_pk = request.session.get('purpose_pk')
	today_date=date.today()
	pet_obj=Pet.objects.get(id=pet_pk)
	pet_obj=pet_obj
	purpose_obj=PurposeAndDiet.objects.filter(pet_id=pet_obj,status="C").all()
	doc_obj=Doctor.objects.get(id=doc_pk)
	if request.method == "GET":
		if 'doc_pk' in request.session:
			return render(request,'doctor/Doctor_previous_visit.html',
			{'purpose_obj':purpose_obj,'doc_pk':doc_pk,'doc_obj':doc_obj})
		else:
			return redirect('doctor_login')
	if request.method=='POST':
		visite_on=request.POST.get('date')
		obj=request.POST.get('obj')
		request.session['history_purpose_pk']=obj
		return redirect('doctor_history_summary')

def doctor_history_summary(request):
	pet_pk = request.session.get('pet_pk')
	purpose_pk = request.session.get('history_purpose_pk')
	print(purpose_pk,'ljhfgjhlfgjhlfgjhlfgjhlfkj')
	purpose_pet_obj=PurposeAndDiet.objects.get(id=purpose_pk)
	print(purpose_pet_obj,'645654654654654')
	try:
		vitals=Vitals.objects.filter(purpose_id=purpose_pet_obj).last()
		vitals=model_to_dict(vitals)
		clean_dict = dict_clean(vitals)
		vitals = remove_empty_from_dict(clean_dict)
	except:
		pass
	try:
		assessment=Assessment.objects.filter(purpose_id=purpose_pet_obj).last()
		assessment=model_to_dict(assessment)
		print(type(assessment))
		clean_dict = dict_clean(assessment)
		assessment = remove_empty_from_dict(clean_dict)
	except:
		pass
	try:
		symptoms=purpose_pet_obj
		symptoms=model_to_dict(symptoms)
		symptoms.pop('purpose_id',None)
		symptoms.pop('id',None)
		symptoms.pop('pet_id',None)
		symptoms.pop('set1',None)
		symptoms.pop('set2',None)
		symptoms.pop('vaccination_purpose',None)
		symptoms.pop('new_diet',None)
		symptoms.pop('new_diet_state',None)
		symptoms.pop('deworming_purpose',None)
		symptoms.pop('last_deworming',None)
		symptoms.pop('status',None)
		clean_dict=dict_clean(symptoms)
		symptoms=remove_empty_from_dict(clean_dict)
	except:
		pass
	try:
		diagnostic=Diagnostics.objects.filter(purpose_id=purpose_pet_obj).last()
		diagnostic=model_to_dict(diagnostic)
		clean_dict = dict_clean(diagnostic)
		diagnostic = remove_empty_from_dict(clean_dict)
	except:
		pass
	try:
		prescription=Prescription.objects.filter(purpose_id=purpose_pet_obj).last()
		prescription_image=Prescription.objects.filter(purpose_id=purpose_pet_obj).last()
		prescription=model_to_dict(prescription)
		prescription.pop('purpose_id',None)
		prescription.pop('id',None)
		prescription.pop('date',None)
		prescription.pop('medicine1_name',None)
		prescription.pop('medicine2_name',None)
		prescription.pop('medicine3_name',None)
		prescription.pop('medicine4_name',None)
		prescription.pop('medicine5_name',None)
		prescription.pop('medicine6_name',None)
		prescription.pop('medicine1_quantity',None)
		prescription.pop('medicine2_quantity',None)
		prescription.pop('medicine3_quantity',None)
		prescription.pop('medicine4_quantity',None)
		prescription.pop('medicine5_quantity',None)
		prescription.pop('medicine6_quantity',None)
		prescription.pop('medicine1_dosage_quantity',None)
		prescription.pop('medicine2_dosage_quantity',None)
		prescription.pop('medicine3_dosage_quantity',None)
		prescription.pop('medicine4_dosage_quantity',None)
		prescription.pop('medicine5_dosage_quantity',None)
		prescription.pop('medicine6_dosage_quantity',None)
		prescription.pop('followup_date_unit',None)
		clean_dict=dict_clean(prescription)
		prescription=remove_empty_from_dict(prescription)
	except:
		pass
	try:
		vaccination=Vaccination.objects.filter(purpose_id=purpose_pet_obj).last()
		vaccination=model_to_dict(vaccination)
		vaccination.pop('purpose_id',None)
		vaccination.pop('id',None)
		vaccination.pop('date',None)
		vaccination.pop('pet',None)
		vaccination = { k:v for k,v in vaccination.items() if v!= datetime.date(1000, 1, 1) }
		vaccination=vaccination_dict(vaccination)
	except:
		pass
	try:
		deworming=Deworming.objects.filter(purpose_id=purpose_pet_obj).last()
		deworming=model_to_dict(deworming)
		deworming.pop('purpose_id',None)
		deworming.pop('id',None)
		deworming.pop('date',None)
		deworming.pop('pet',None)
		deworming = { k:v for k,v in deworming.items() if v!= datetime.date(1000, 1, 1) }
		deworming=vaccination_dict(deworming)
	except:
		pass
	if request.method == "GET":
		if 'doc_pk' in request.session:
			return render(request,'doctor/doctor_history_summary.html',
			{'symptoms':symptoms,'vitals':vitals,'assessment':assessment,
			'diagnostic':diagnostic,'prescription':prescription,
			'vaccination':vaccination,'deworming':deworming,
			'prescription_image':prescription_image,
			'media_url':settings.MEDIA_URL,})
		else:
			return redirect('doctor_login')


#############################################################################
#Doctor Module views Ended
#############################################################################


def pet_age_converter(pet_obj):
	pets=pet_obj
	list=[]
	for petss in pets:
		petdict=model_to_dict(petss)
		for k,v in petdict.items():
			if k == 'dob':
				currentDate = datetime.date.today()
				deadlineDate= petdict.get('dob')
				print((type(deadlineDate)))
				daysLeft = deadlineDate - currentDate
				years = ((daysLeft.total_seconds())/(365.242*24*3600))
				yearsInt=int(years)
				months=(years-yearsInt)*12
				monthsInt=int(months)
				if yearsInt == -1:
					y='year'
				else:
					y='years'
				if monthsInt == -1:
					m='month'
				else:
					m='months'
				if monthsInt == 0:
					agestring=str(yearsInt)+y
					age=agestring.replace('-','')
				else:
					agestring=str(yearsInt)+y+','+str(monthsInt)+m
					age=agestring.replace('-','')
				petdict['dob']=age
		list.append(petdict)
	return list

def pet_age_converter_single(pet_obj):
	pets=pet_obj
	petdict=model_to_dict(pets)
	for k,v in petdict.items():
		if k == 'dob':
			currentDate = datetime.date.today()
			deadlineDate= petdict.get('dob')
			print((type(deadlineDate)))
			daysLeft = deadlineDate - currentDate
			years = ((daysLeft.total_seconds())/(365.242*24*3600))
			yearsInt=int(years)
			months=(years-yearsInt)*12
			monthsInt=int(months)
			if yearsInt == -1:
				y='year'
			else:
				y='years'
			if monthsInt == -1:
				m='month'
			else:
				m='months'
			if monthsInt == 0:
				agestring=str(yearsInt)+y
				age=agestring.replace('-','')
			else:
				agestring=str(yearsInt)+y+','+str(monthsInt)+m
				age=agestring.replace('-','')
			petdict['dob']=age
	return petdict

def customer_purpose_visit(request):
	#getting parameters from session
	check_visit=request.session['visit_check']
	url_parameters=request.session['pass_dict_session']
	customer_pk=url_parameters['customer_pk']
	consulted_pet=url_parameters['consulted_pet']
	doc_pk=url_parameters['doctor_pk']
	purpose_id=url_parameters['purpose_id']

	#pet age conversion for sidebar
	customer_id=Customer.objects.get(id=customer_pk).customer_id
	x = Pet.objects.filter(pet_id=consulted_pet).last()
	#side bar petimage code
	if request.method == "GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id :
				return render(request,'customer/Customer_purpose_of_the_visit.html',
				{'customer_id':customer_id,
				'check_visit':check_visit,'doc_pk_org':doc_pk})
			else:
				return redirect ('customer_login_home')
		else:
			return redirect('customer_login_home')
	if request.method=='POST':
		check_visit=request.session['visit_check']
		vaccination_purpose=request.POST.get('purpose')
		vaccination_purpose=empty_string_remove (vaccination_purpose)
		disease=request.POST.get('disease')
		disease=empty_string_remove (disease)
		symptoms_text=request.POST.get('symptoms_text')
		hello = PurposeAndDiet.objects.filter(id=purpose_id).update(vaccination_purpose=vaccination_purpose,
		symptoms_text=symptoms_text,disease=disease)
		#checking hospital visit or Home visit
		if check_visit == 'Home_visit':
			return redirect('doctorlist',doc_pk=None,check_visit=None)
		elif check_visit == 'Hospital_visit':
			return redirect('booking_summary',booking_date=None)
		else:
			return render(request,'customer/Customer_purpose_of_the_visit.html',
			{'customer_id':customer_id})
def empty_string_remove(values):
    values=values.split(',')
    if ('' in values):
        values.remove('')
    else:
        values=values
    return ','.join(values)

# razorpay_client = razorpay.Client(auth=("rzp_live_KzOTrbFmBHrpSH", "Nqx87ucnyev4U3K71PGXObGf"))
razorpay_client = razorpay.Client(auth=("rzp_test_Ir71bWIgPS3Pqe", "dcPKyHodTxl0fLI8Urv48PhJ"))

def booking_summary(request,booking_date):
	#getting parameters from session
	check_visit=request.session['visit_check']
	url_parameters=request.session['pass_dict_session']
	customer_pk=url_parameters['customer_pk']
	consulted_pet=url_parameters['consulted_pet']
	doc_pk=url_parameters['doctor_pk']
	purpose_id=url_parameters['purpose_id']
	customer_obj=Customer.objects.get(id=customer_pk)
	customer_id=customer_obj.customer_id
	pets_obj=Pet.objects.filter(customer_id__customer_id=customer_id).all()
	pets_obj=pet_age_converter(pets_obj)
	mobile=customer_obj.mobile
	email=customer_obj.email
	if email == '':
		email = mobile+'@aodhpayment.com'
	customer_name = customer_obj.customer_name
	address = customer_obj.address
	doctor_obj=Doctor.objects.get(id=doc_pk)
	doctor_name=doctor_obj.Name_of_doctor
	pets=Pet.objects.filter(pet_id=consulted_pet).last()
	visit_purpose=PurposeAndDiet.objects.filter(id=purpose_id).last()
	visit_purpose=model_to_dict (visit_purpose)
	visit_purpose.pop("id", None)
	visit_purpose.pop("pet_id", None)
	visit_purpose.pop("deworming_purpose", None)
	visit_purpose.pop("date", None)
	visit_purpose.pop("diet", None)
	visit_purpose.pop("diet_state", None)
	visit_purpose.pop("disease",None)
	visit_purpose.pop("symptoms_text",None)
	visit_purpose.pop("status",None)
	diet=PurposeAndDiet.objects.filter(id=purpose_id).last()
	diet=model_to_dict (diet)
	diet.pop("id", None)
	diet.pop("pet_id", None)
	diet.pop("deworming_purpose", None)
	diet.pop("date", None)
	diet.pop("disease",None)
	diet.pop("vaccination_purpose",None)
	diet.pop("symptoms_text",None)
	diet.pop("status",None)
	disease_pet=PurposeAndDiet.objects.filter(id=purpose_id).last()
	disease_pet=model_to_dict (disease_pet)
	disease_pet.pop("id", None)
	disease_pet.pop("pet_id", None)
	disease_pet.pop("deworming_purpose", None)
	disease_pet.pop("date", None)
	disease_pet.pop("diet",None)
	disease_pet.pop("diet_state",None)
	disease_pet.pop("symptoms_text",None)
	disease_pet.pop("vaccination_purpose",None)
	disease_pet.pop("status",None)
	disease_pet_enter=PurposeAndDiet.objects.filter(id=purpose_id).last()
	disease_pet_enter=model_to_dict (disease_pet_enter)
	disease_pet_enter.pop("id", None)
	disease_pet_enter.pop("pet_id", None)
	disease_pet_enter.pop("deworming_purpose", None)
	disease_pet_enter.pop("date", None)
	disease_pet_enter.pop("diet",None)
	disease_pet_enter.pop("diet_state",None)
	disease_pet_enter.pop("disease",None)
	disease_pet_enter.pop("vaccination_purpose",None)
	disease_pet_enter.pop("status",None)
	fee=doctor_obj.consultation_fee
	doctor_live_status = doctor_obj.live_management
	customer_subscription_status = customer_obj.subscribed
	if customer_subscription_status == True:
		if doctor_live_status == 'yes':
			subscription_fee = 0
			subscription_status = 'subscribed'
		elif doctor_live_status == 'no':
			subscription_fee = 0
			subscription_status = 'subscribed'
	elif customer_subscription_status == False:
		if doctor_live_status == 'yes':
			subscription_fee = doctor_obj.subscription_fee
			subscription_status = True
		elif doctor_live_status == 'no':
			subscription_fee = 0
			subscription_status = False
	request.session['subscription_status']=subscription_status
	request.session['subscription_fee']=subscription_fee
	sub_total = fee+subscription_fee
	sub_total_razor = sub_total*100
	if sub_total_razor == 0:
		sub_total_razor = 1*100
	DATA={
	"amount": sub_total_razor,
	"currency": "INR",
	"payment_capture":'1',
	"notes" : {'Shipping address':'hrllll, hyd'}
	}
	order=razorpay_client.order.create(data=DATA)
	order_id=order.get("id","")
	request.session['aodh_razorpay_order_id'] = order_id
	request.session['aodh_razorpay_order_amount'] = sub_total_razor
	z=request.session.items()
	if request.method == "GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id :
				if check_visit =='Hospital_visit':
					booking_date='None'
				else:
					booking_date=booking_date

				return render(request,'customer/Customer_booking_summary.html',
				{'customer_id':customer_id,'doctor_name':doctor_name,
				'visit_purpose':visit_purpose,'fee':fee,'check_visit':check_visit,
				'sub_total':sub_total,'pets':pets_obj,'order_id':order_id,
				"email":email,'mobile':mobile,'doc_pk':doc_pk,'purpose_id':purpose_id,
				'pet_id':consulted_pet,'diet':diet,'disease_pet':disease_pet,
				'disease_pet_enter':disease_pet_enter,'url_date':booking_date,
				'subscription_fee':subscription_fee,'mode':check_visit,
				'subscription_status':subscription_status,'customer_name':customer_name})
			else:
				return redirect ('customer_login_home')
		else:
			return redirect('customer_login_home')
	if request.method == "POST":
		if "pay_at_clinic" in request.POST:
			if check_visit =='Hospital_visit':
				booking_date=date.today()
			else:
				booking_date=booking_date

			return redirect('booking_confirm',booking_date)
		else:
			if check_visit =='Hospital_visit':

				booking_date='None'
			else:
				booking_date=booking_date

			return redirect('pay_online_conform',customer_id=customer_id,
			doc_pk=doc_pk, pet_id=consulted_pet, purpose_id=purpose_id, mode=check_visit,
			url_date=booking_date, check_visit=check_visit,
			subscription_status=subscription_status)

def booking_id_generation(cus_id,pet_id):
	now = datetime.datetime.now()
	booking_id = cus_id + pet_id + now.strftime("%Y%m%d%H%M%S")
	return booking_id

@csrf_exempt
def booking_confirm(request,booking_date):
	#getting parameters from session
	check_visit=request.session['visit_check']
	url_parameters=request.session['pass_dict_session']
	customer_pk=url_parameters['customer_pk']
	consulted_pet=url_parameters['consulted_pet']
	doc_pk=url_parameters['doctor_pk']
	purpose_id=url_parameters['purpose_id']
	customer_obj=Customer.objects.get(id=customer_pk)
	customer_id=customer_obj.customer_id
	subscription_status=request.session['subscription_status']
	print(subscription_status,'46464654654')
	subscription_fee = request.session['subscription_fee']
	url_date=date.today()
	if 'customer_id' in request.session:
		session_id=request.session['customer_id']
		if session_id == customer_id :
			purpose=PurposeAndDiet.objects.get(id=purpose_id)
			#if page refreshed
			if DoctorViewLog.objects.filter(purpose_id__id=purpose_id).exists():
				razorpay_payment_obj=Razorpay_Dashboard.objects.filter(customer_mobile=customer_obj.mobile,pet=consulted_pet,payment_date=url_date).last()
				booking_id=razorpay_payment_obj.booking_id
				final_fee = razorpay_payment_obj.amount_paid
			else:
				#first time saving into table

				# url_date=url_date.replace('-','/')
				url_date=datetime.datetime.strptime(booking_date, "%Y-%m-%d").date()
				booking_expiry_date=url_date+timedelta(1)
				current_time=datetime.datetime.now().time()
				# today_date_time = datetime.datetime.now()
				url_date=datetime.datetime.combine(url_date,current_time)
				today_date_time_added=url_date+timedelta(hours=24)
				doctorviewlog=DoctorViewLog()
				#customer object
				Customer_obj = Customer.objects.get(customer_id=customer_id)
				doctorviewlog.purpose_id=PurposeAndDiet.objects.get(id=purpose_id)
				doctorviewlog.customer_id=Customer_obj
				doctorviewlog.doc_pk=Doctor.objects.get(id=doc_pk)
				doctorviewlog.pet_id=Pet.objects.get(pet_id=consulted_pet)
				doctorviewlog.mode=check_visit
				doctor_obj=Doctor.objects.get(id=doc_pk)
				doctorviewlog.payment=doctor_obj.consultation_fee
				doctorviewlog.consultation_fee=doctor_obj.consultation_fee
				doctorviewlog.booking_expiry=today_date_time_added
				doctorviewlog.booking_date=url_date
				doctorviewlog.booking_expiry_date=booking_expiry_date
				doctorviewlog.payment_type='offline'
				if subscription_status == True:
					subscription_fee = Doctor.objects.get(id=doc_pk).subscription_fee
					subscription_fee = subscription_fee
					customersubscribed=CustomerSubscribed()
					customersubscribed.customer=Customer.objects.get(customer_id=customer_id)
					customersubscribed.save()
				elif subscription_status == 'subscribed':
					subscription_fee = 0
				if subscription_status == False:
					subscription_fee = 0
				doctorviewlog.subscription_fee = subscription_fee
				doctorviewlog.save()
				customer = Customer()
				print(type(subscription_status),'7987987987987987987987987')
				if subscription_status == 'subscribed':
					print('subscribed')
					subscription_fee=0
					customer = Customer()
					subscription_status=True
					Customer.objects.filter(customer_id=customer_id).update(subscribed=subscription_status)
				elif subscription_status == True:
					subscription_fee=Doctor.objects.get(id=doc_pk).subscription_fee
					customer = Customer()
					subscription_status=True
					Customer.objects.filter(customer_id=customer_id).update(subscribed=subscription_status)
				else:
					print('ghkdfhgkjdhgkjdfhgkjdfh')
					subscription_fee=0
				fee=doctor_obj.consultation_fee
				final_fee = fee+subscription_fee
				razorpay_dashboard =Razorpay_Dashboard()
				booking_id = booking_id_generation(customer_id,consulted_pet)
				razorpay_dashboard.Payment_id = booking_id
				razorpay_dashboard.order_id = 'None'
				razorpay_dashboard.booking_id = booking_id
				razorpay_dashboard.payment_status = 'success'
				razorpay_dashboard.amount_paid = final_fee
				razorpay_dashboard.doctor_name = doctor_obj.first_name
				razorpay_dashboard.doctor_mobile = doctor_obj.Mobile
				razorpay_dashboard.customer_name = Customer_obj.customer_name
				razorpay_dashboard.customer_mobile = Customer_obj.mobile
				razorpay_dashboard.pet = consulted_pet
				razorpay_dashboard.save()
				log=Log()
				log.doctor=doctor_obj
				log.consultation_fee=fee
				log.final_fee=fee+subscription_fee
				log.customer=customer_obj
				log.purpose_id=PurposeAndDiet.objects.get(id=purpose_id)
				log.pet_id=consulted_pet
				log.mode=check_visit
				log.booking_expiry=today_date_time_added
				log.booking_id = booking_id
				log.booking_date=url_date
				log.booking_expiry_date=booking_expiry_date
				log.save()
			return render(request,'customer/Customer_booking__confirmed.html',
			{'customer_id':customer_id,'doc_pk':doc_pk,'final_fee':final_fee,'check_visit':check_visit,
			'booking_id':booking_id})
		else:
			return redirect ('customer_login_home')
	else:
		return redirect('customer_login_home')


from django.utils.datastructures import MultiValueDictKeyError

@csrf_exempt
def pay_online_conform(request,customer_id,doc_pk,pet_id,purpose_id,mode,
	url_date,check_visit,subscription_status):
	request.session['customer_id'] = customer_id
	request.session['visit_check'] = check_visit
	request.session['Doctor_pk_hospital']=doc_pk
	customer_obj=Customer.objects.get(customer_id=customer_id)
	if 'customer_id' in request.session:
		session_id=request.session['customer_id']
		if session_id == customer_id :
			razorpay_payment_id = request.POST.get('razorpay_payment_id')
			razorpay_order_id = request.POST.get('razorpay_order_id')
			razorpay_signature = request.POST.get('razorpay_signature')
			if razorpay_payment_id is not None:
				if Consultation_Payment.objects.filter(Q(razorpay_payment_id=razorpay_payment_id)
				| Q(razorpay_order_id=razorpay_order_id)):
					return render(request,'customer/payment_faild.html',
					{'customer_id':customer_id,'razorpay_order_id':razorpay_order_id})
				else:
					params_dict = {
						'razorpay_payment_id': razorpay_payment_id,
						'razorpay_order_id' : razorpay_order_id,
						'razorpay_signature': razorpay_signature
					}
					secret_key = 'dcPKyHodTxl0fLI8Urv48PhJ'
					msg = "{}|{}".format(razorpay_order_id, razorpay_payment_id)
					key = bytes(secret_key, 'utf-8')
					body = bytes(msg, 'utf-8')
					dig = hmac.new(key=key,
						msg=body,
						digestmod=hashlib.sha256)
					generated_signature = dig.hexdigest()
					if generated_signature == razorpay_signature:
						razorpay_payment_obj = razorpay_client.payment.fetch(razorpay_payment_id)
						razorpay_payment_status = razorpay_payment_obj['status']
						razorpay_payment_amount = razorpay_payment_obj['amount']
						doctor_obj = Doctor.objects.get(id=doc_pk)
						razorpay_payment_amount = razorpay_payment_amount/100
						purpose=PurposeAndDiet.objects.get(id=purpose_id)
						if DoctorViewLog.objects.filter(purpose_id__id=purpose_id).exists():
							if url_date == 'None':
								url_date=date.today()
								url_date=str(url_date)
							else:
								url_date=url_date
							razorpay_payment_obj=Razorpay_Dashboard.objects.filter(customer_mobile=customer_obj.mobile,pet=pet_id,payment_date=url_date).last()
							booking_id=razorpay_payment_obj.booking_id
							final_fee = razorpay_payment_obj.amount_paid
						else:
							consultation_payment=Consultation_Payment()
							consultation_payment.pet_id = pet_id
							consultation_payment.razorpay_payment_id = razorpay_payment_id
							consultation_payment.razorpay_order_id = razorpay_order_id
							consultation_payment.razorpay_signature = razorpay_signature
							consultation_payment.razorpay_payment_status = razorpay_payment_status
							consultation_payment.save()
							razorpay_dashboard = Razorpay_Dashboard()
							razorpay_dashboard.Payment_id = razorpay_payment_id
							razorpay_dashboard.order_id = razorpay_order_id
							booking_id = booking_id_generation(customer_id,pet_id)
							razorpay_dashboard.booking_id = booking_id
							razorpay_dashboard.payment_status = razorpay_payment_status
							razorpay_dashboard.amount_paid = razorpay_payment_amount
							doctor_obj_raz = Doctor.objects.get(id=doc_pk)
							doctor_name = doctor_obj_raz.first_name
							doctor_mobile = doctor_obj_raz.Mobile
							razorpay_dashboard.doctor_name = doctor_name
							razorpay_dashboard.doctor_mobile = doctor_mobile
							customer_obj_raz = Customer.objects.get(customer_id=customer_id)
							customer_name = customer_obj_raz.customer_name
							customer_mobile = customer_obj_raz.mobile
							razorpay_dashboard.customer_name = customer_name
							razorpay_dashboard.customer_mobile = customer_mobile
							pet = Pet.objects.get(pet_id=pet_id)
							pet = pet.name
							razorpay_dashboard.pet = pet
							razorpay_dashboard.save()
							if url_date == 'None':
								url_date=date.today()
								url_date=str(url_date)
							else:
								url_date=url_date
							# url_date=url_date.replace('-','/')
							url_date=datetime.datetime.strptime(url_date, "%Y-%m-%d").date()
							booking_expiry_date=url_date+timedelta(1)
							current_time=datetime.datetime.now().time()
							# today_date_time = datetime.datetime.now()
							url_date=datetime.datetime.combine(url_date,current_time)
							today_date_time_added=url_date+timedelta(hours=24)
							doctorviewlog=DoctorViewLog()
							doctorviewlog.purpose_id=purpose
							doctorviewlog.customer_id=Customer.objects.get(customer_id=customer_id)
							doctorviewlog.doc_pk=Doctor.objects.get(id=doc_pk)
							doctorviewlog.pet_id=Pet.objects.get(pet_id=pet_id)
							doctorviewlog.mode=mode
							doc=Doctor.objects.get(id=doc_pk)
							doctorviewlog.consultation_fee=doc.consultation_fee
							doctorviewlog.booking_expiry=today_date_time_added
							doctorviewlog.booking_date=url_date
							doctorviewlog.payment='Paid'
							doctorviewlog.booking_expiry_date=booking_expiry_date
							doctorviewlog.payment_type='online'
							if subscription_status == 'True':
								subscription_fee = Doctor.objects.get(id=doc_pk).subscription_fee
								subscription_fee = subscription_fee
								customersubscribed=CustomerSubscribed()
								customersubscribed.customer=Customer.objects.get(customer_id=customer_id)
								customersubscribed.save()
							elif subscription_status == 'subscribed':
								subscription_fee = 0
							if subscription_status == 'False':
								subscription_fee = 0
							doctorviewlog.subscription_fee = subscription_fee
							doctorviewlog.save()
							customer = Customer()
							if subscription_status == 'subscribed':
								subscription_fee=0
								customer = Customer()
								subscription_status=True
								Customer.objects.filter(customer_id=customer_id).update(subscribed=subscription_status)
							elif subscription_status == 'True':
								subscription_fee=doc.subscription_fee
								customer = Customer()
								subscription_status=True
								Customer.objects.filter(customer_id=customer_id).update(subscribed=subscription_status)
							else:
								subscription_fee=0
							log=Log()

							log.doctor=doc
							fee=doc.consultation_fee
							log.consultation_fee=fee
							final_fee = fee+subscription_fee
							log.final_fee=fee+subscription_fee
							log.customer=Customer.objects.get(customer_id=customer_id)
							log.purpose_id=PurposeAndDiet.objects.get(id=purpose_id)
							log.pet_id=pet_id
							log.mode=mode
							log.booking_expiry=today_date_time_added
							log.booking_id = booking_id
							log.booking_date=url_date
							log.booking_expiry_date=booking_expiry_date
							# log.save()
						id_pet=pet_id

						return render(request,'customer/Customer_booking__confirmed.html',
						{'customer_id':customer_id,'doc_pk':doc_pk,
						'razorpay_order_id':razorpay_order_id,
						'razorpay_payment_status':razorpay_payment_status,
						'razorpay_payment_amount':razorpay_payment_amount,
						'check_visit':check_visit,'booking_id':booking_id})
			elif not request.POST:
				booking_id = booking_id_generation(customer_id,pet_id)
				consultation_payment=Consultation_Payment()
				consultation_payment.pet_id = pet_id
				consultation_payment.razorpay_payment_id = 'cancled'+booking_id
				razorpay_order_id = 'cancled'+booking_id
				consultation_payment.razorpay_order_id = razorpay_order_id
				consultation_payment.razorpay_signature = 'cancled'+booking_id
				consultation_payment.razorpay_payment_status = "cancled"
				consultation_payment.save()
				razorpay_dashboard = Razorpay_Dashboard()
				razorpay_dashboard.Payment_id = 'cancled'+booking_id
				razorpay_dashboard.order_id = 'cancled'+booking_id
				razorpay_dashboard.booking_id = booking_id
				razorpay_dashboard.payment_status = 'cancled'
				razorpay_dashboard.amount_paid = 0
				doctor_obj_raz = Doctor.objects.get(id=doc_pk)
				doctor_name = doctor_obj_raz.first_name
				doctor_mobile = doctor_obj_raz.Mobile
				razorpay_dashboard.doctor_name = doctor_name
				razorpay_dashboard.doctor_mobile = doctor_mobile
				customer_obj_raz = Customer.objects.get(customer_id=customer_id)
				customer_name = customer_obj_raz.customer_name
				customer_mobile = customer_obj_raz.mobile
				razorpay_dashboard.customer_name = customer_name
				razorpay_dashboard.customer_mobile = customer_mobile
				pet = Pet.objects.get(pet_id=pet_id)
				pet = pet.name
				razorpay_dashboard.pet = pet
				razorpay_dashboard.save()
				return render(request, 'customer/payment_faild.html',
				{'customer_id': customer_id,
					'razorpay_order_id': razorpay_order_id,'booking_id':booking_id})
			else:
				response = request.POST
				response_data = response['error[metadata]']
				print(response_data)
				response_data = json.loads(response_data)
				razorpay_payment_id = response_data['payment_id']
				razorpay_order_id = response_data['order_id']
				razorpay_payment_obj = razorpay_client.payment.fetch(razorpay_payment_id)
				razorpay_payment_status = razorpay_payment_obj['status']
				razorpay_payment_amount = razorpay_payment_obj['amount']
				razorpay_payment_amount = razorpay_payment_amount/100
				consultation_payment=Consultation_Payment()
				consultation_payment.pet_id = pet_id
				consultation_payment.razorpay_payment_id = razorpay_payment_id
				consultation_payment.razorpay_order_id = razorpay_order_id
				consultation_payment.razorpay_signature = 'None'
				consultation_payment.razorpay_payment_status = razorpay_payment_status
				consultation_payment.save()
				razorpay_dashboard = Razorpay_Dashboard()
				razorpay_dashboard.Payment_id = razorpay_payment_id
				razorpay_dashboard.order_id = razorpay_order_id
				booking_id = booking_id_generation(customer_id,pet_id)
				razorpay_dashboard.booking_id = booking_id
				razorpay_dashboard.payment_status = razorpay_payment_status
				razorpay_dashboard.amount_paid = razorpay_payment_amount
				doctor_obj_raz = Doctor.objects.get(id=doc_pk)
				doctor_name = doctor_obj_raz.first_name
				doctor_mobile = doctor_obj_raz.Mobile
				razorpay_dashboard.doctor_name = doctor_name
				razorpay_dashboard.doctor_mobile = doctor_mobile
				customer_obj_raz = Customer.objects.get(customer_id=customer_id)
				customer_name = customer_obj_raz.customer_name
				customer_mobile = customer_obj_raz.mobile
				razorpay_dashboard.customer_name = customer_name
				razorpay_dashboard.customer_mobile = customer_mobile
				pet = Pet.objects.get(pet_id=pet_id)
				pet = pet.name
				razorpay_dashboard.pet = pet
				razorpay_dashboard.save()
				return render(request, 'customer/payment_faild.html',
				{'customer_id': customer_id, 'razorpay_order_id': razorpay_order_id,'booking_id':booking_id})
			# except MultiValueDictKeyError:
			# 	return redirect('petlist')
		else:
			return redirect ('customer_login_home')
	else:
		return redirect('customer_login_home')



def last_vaccination(request,customer_id):
	if request.method == "GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			pet_id=customer_id
			pet_obj=Pet.objects.filter(pet_id=pet_id).last()
			purpose_pet_obj=PurposeAndDiet.objects.filter(pet_id=pet_obj).last()
			vaccination=Vaccination.objects.filter(pet=pet_obj)
			x=['Jan. 1, 1000']
			last_vaccination=Vaccination_coustmer.objects.filter(pet=pet_obj).last()
			return render(request,'customer/Customer_vaccination_history.html',{'last_vaccination':last_vaccination,'vaccination':vaccination,'x':x})

		else:
			return redirect('customer_login_home')

def last_deworming(request,customer_id):
	if request.method == "GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			pet_id=customer_id
			pet_obj=Pet.objects.filter(pet_id=pet_id).last()
			purpose_pet_obj=Vaccination_coustmer.objects.filter(pet=pet_obj).last()
			last_deworming=Deworming.objects.filter(pet=pet_obj)
			return render(request,'customer/Customer_deworming_history.html',{'last_deworming':last_deworming,'purpose_pet_obj':purpose_pet_obj})

		else:
			return redirect('customer_login_home')


def cust_id():
	coustmer_id = Customer.objects.all()
	if len(coustmer_id)==0:
		coustmer_id = 'AODH' + str(len(coustmer_id) + 1)
		return coustmer_id
	else:
		cust=Customer.objects.last().customer_id
		cust=cust[4:]
		cust=int(cust)
		cust=cust + 1
		coustmer_id='AODH' + str(cust)
		return coustmer_id


# def validate_mobile(request):
# 	mobile = request.GET.get('mobile', None)
# 	data = {
# 	'is_taken': Customer.objects.filter(mobile__iexact=mobile).exists()
# 	}
# 	return JsonResponse(data)
def validate_mobile(request):
	if request.method=="POST":
		mobile = request.POST.get('mobile')
	if Customer.objects.filter(mobile__iexact=mobile).exists() :
		pass
	else:
		data = 'NO mobile'
		return JsonResponse(data,safe=False)
	return HttpResponse('Please Tr again')


def pet_list(request):
	customer_id=request.session['customer_id']
	check_visit = request.session['visit_check']
	if check_visit =='Hospital_visit':
		doc_pk=request.session['Doctor_pk_hospital']
	else:
		doc_pk='none'
	if request.method == "GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']

			if session_id == customer_id :
				customer = Customer.objects.get(customer_id=customer_id)
				pets = Pet.objects.filter(customer_id__customer_id=customer_id).all()
				pets = pet_age_converter(pets)
				doctorloglist=DoctorViewLog.objects.filter(customer_id__customer_id=customer_id,status="A").all()
				x=[]
				for pet in doctorloglist:
					pet_id=pet.pet_id.pet_id
					x.append(pet_id)
				return render(request,'customer/Customer_pet_details_second_visit.html',
				{'customer_id':customer_id,'pets':pets,'doc_pk':doc_pk,
				'doctorloglist':doctorloglist,'x':x,
				'check_visit':check_visit})
			else:
				return redirect ('customer_login_home')
		else:
			return redirect('customer_login_home')
	if request.method=='POST':
		consulted_pet=request.POST.get('petid')
		purpose=PurposeAndDiet()
		pet_id1=Pet.objects.get(pet_id=consulted_pet)
		purpose.pet_id=Pet.objects.get(pet_id=consulted_pet)
		purpose.save()
		purpose_id=PurposeAndDiet.objects.filter(pet_id=pet_id1).last()
		purpose_id=purpose_id.id
		customer = Customer.objects.get(customer_id=customer_id)
		request.session['pass_dict_session']={'customer_pk':customer.id,'doctor_pk':doc_pk,'purpose_id':purpose_id,'consulted_pet':consulted_pet}
		return redirect('pet_dite')


def peteditdetails(request,pet_id,doc_pk,customer_id):
	pet_obj=Pet.objects.filter(pet_id=pet_id)
	pet_obj = pet_age_converter(pet_obj)
	if request.method=='POST':
		name=request.POST.get('name')
		breed=request.POST.get('breed')
		gender=request.POST.get('gender')
		year=request.POST.get("dob_year")

		month=request.POST.get("dob_month")
		if year=='' or month=='':
			dob=Pet.objects.filter(pet_id=pet_id).last()
			dob=dob.dob
		else:
			year=int(year)
			month=int(month)
			currentdate=date.today()
			birthyear=currentdate.year-year
			currenthmonth=currentdate.month
			birtmonth=currentdate.month-month
			birtday=currentdate.day
			if birtmonth <0:
				month=month-1
				birtmonth=12-month
				if birtmonth == 2:
					if (birthyear % 4) == 0:
						birtday > 29
						birtday=29
					elif (birthyear % 4) != 0:
						birtday > 29
						birtday=28
					elif (birthyear % 100) == 0:

						birtday > 29
						birtday=29
					elif (birthyear % 100) != 0:
						birtday > 29
						birtday=28
			elif birtmonth == 0:
				birtmonth = 12
			else:
				birtmonth=birtmonth
				if birtmonth == 2:
					if (birthyear % 4) == 0:
						birtday > 29
						birtday=29
					elif (birthyear % 4) != 0:
						birtday > 29
						birtday=28
					elif (birthyear % 100) == 0:
						birtday > 29
						birtday=29
					elif (birthyear % 100) != 0:
						birtday > 29
						birtday=28
			pet_birth = datetime.date(birthyear, birtmonth, birtday)
			dob=pet_birth
		Pet.objects.filter(pet_id=pet_id).update(name=name,breed=breed,gender=gender,dob=dob)
		return redirect('pet_list')
	return render(request,'customer/edit_pet_details.html',{'pet_obj':pet_obj})



def petdetails(request,doc_pk=None):
	if request.method == "GET":
		customer_id=request.session['customer_id']
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id :

				return render (request,'customer/Customer_pet_details.html',{'customer_id':customer_id,'doc_pk':doc_pk})
			else:
				return redirect ('customer_login_home')
		else:
			return redirect('customer_login_home')
	if request.method=='POST':
		customer_id=request.session['customer_id']
		if 'addpet' in request.POST:
			pet=Pet()
			coustmer_obj=Customer.objects.get(customer_id=customer_id)
			pet.customer_id=coustmer_obj
			pet.name=request.POST.get('name')
			pet.breed=request.POST.get('breed')
			year=request.POST.get('age_year')
			year=int(year)
			month=request.POST.get('age_month')
			month=int(month)
			currentdate=date.today()
			birthyear=currentdate.year-year
			currenthmonth=currentdate.month
			birtmonth=currentdate.month-month
			birtday=currentdate.day
			if birtmonth <0:
				month=month-1
				birtmonth=12-month
				if birtmonth == 2:
					if (birthyear % 4) == 0:
						birtday > 29
						birtday=29
					elif (birthyear % 4) != 0:
						birtday > 29
						birtday=28
					elif (birthyear % 100) == 0:

						birtday > 29
						birtday=29
					elif (birthyear % 100) != 0:
						birtday > 29
						birtday=28
			elif birtmonth == 0:
				birtmonth = 12
			else:
				birtmonth=birtmonth
				if birtmonth == 2:
					if (birthyear % 4) == 0:
						birtday > 29
						birtday=29
					elif (birthyear % 4) != 0:
						birtday > 29
						birtday=28
					elif (birthyear % 100) == 0:
						birtday > 29
						birtday=29
					elif (birthyear % 100) != 0:
						birtday > 29
						birtday=28
			pet_birth = datetime.date(birthyear, birtmonth, birtday)
			pet.dob=pet_birth
			pet.gender=request.POST.get('gender')
			pet_id_created=set_id()
			pet.pet_id=pet_id_created
			pet.save()
			purpose=PurposeAndDiet()
			pet_obj=Pet.objects.filter(pet_id=pet_id_created).last()
			purpose.pet_id=pet_obj
			vac_coustmer=Vaccination_coustmer()
			last_deworming=request.POST.get('last_date')
			last_deworming=last_deworming
			if last_deworming=="":
				vac_coustmer.last_deworming='1000-01-01'
			else:
				vac_coustmer.last_deworming=last_deworming
			purpose.save()
			main_purpose_id=PurposeAndDiet.objects.get(pet_id=pet_obj).id


			purpose_id=PurposeAndDiet.objects.filter(pet_id__customer_id__customer_id=customer_id).last()

			pet_obj=Pet.objects.filter(pet_id=pet_id_created).last()
			vac_coustmer.pet=pet_obj
			last_date_3_in_1_DAPV=request.POST.get('last_date_3_in_1_DAPV')
			if last_date_3_in_1_DAPV=="":

				vac_coustmer.last_date_3_in_1_DAPV='1000-01-01'
			else:
				vac_coustmer.last_date_3_in_1_DAPV=last_date_3_in_1_DAPV

			last_date_4_in_1_DHPP=request.POST.get('last_date_4_in_1_DHPP')
			if last_date_4_in_1_DHPP=="":

				vac_coustmer.last_date_4_in_1_DHPP='1000-01-01'
			else:
				vac_coustmer.last_date_4_in_1_DHPP=last_date_4_in_1_DHPP

			last_date_5_in_1_DA2PP=request.POST.get('last_date_5_in_1_DA2PP')
			if last_date_5_in_1_DA2PP=="":

				vac_coustmer.last_date_5_in_1_DA2PP='1000-01-01'
			else:
				vac_coustmer.last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP

			last_date_6_in_1_DA2PPC=request.POST.get('last_date_6_in_1_DA2PPC')
			if last_date_6_in_1_DA2PPC=="":

				vac_coustmer.last_date_6_in_1_DA2PPC='1000-01-01'
			else:
				vac_coustmer.last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC

			last_date_7_in_1_DA2PPVL2=request.POST.get('last_date_7_in_1_DA2PPVL2')
			if last_date_7_in_1_DA2PPVL2=="":

				vac_coustmer.last_date_7in1_DA2PPVL2='1000-01-01'
			else:
				vac_coustmer.last_date_7in1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
			last_date_rabies=request.POST.get('l_rabies')
			if last_date_rabies=="":
				vac_coustmer.last_date_rabies='1000-01-01'
			else:
				vac_coustmer.last_date_rabies=last_date_rabies
			last_date_distemper=request.POST.get('l_distemper')
			if last_date_distemper=="":
				vac_coustmer.last_date_distemper='1000-01-01'
			else:
				vac_coustmer.last_date_distemper=last_date_distemper
			last_date_hepatitis=request.POST.get('l_hepatitis')
			if last_date_hepatitis=="":
				vac_coustmer.last_date_CAV_1='1000-01-01'
			else:
				vac_coustmer.last_date_CAV_1=last_date_hepatitis
			last_date_parovirus=request.POST.get('l_parovirus')
			if last_date_parovirus=="":
				vac_coustmer.last_date_parovirus='1000-01-01'
			else:
				vac_coustmer.last_date_parovirus=last_date_parovirus
			last_date_parainfluenza=request.POST.get('l_parainfluenza')
			if last_date_parainfluenza=="":
				vac_coustmer.last_date_parainfluenza='1000-01-01'
			else:
				vac_coustmer.last_date_parainfluenza=last_date_parainfluenza
			last_date_bordetella=request.POST.get('l_bordetella')
			if last_date_bordetella=="":
				vac_coustmer.last_date_bordetella='1000-01-01'
			else:
				vac_coustmer.last_date_bordetella=last_date_bordetella
			last_date_Can_L=request.POST.get('Can_L')
			if last_date_Can_L=="":
				vac_coustmer.last_date_Can_L='1000-01-01'
			else:
				vac_coustmer.last_date_Can_L=last_date_Can_L
			last_date_lyme=request.POST.get('l_lymedisease')
			if last_date_lyme=="":
				vac_coustmer.last_date_lyme='1000-01-01'
			else:
				vac_coustmer.last_date_lyme=last_date_lyme
			last_date_coronavirus=request.POST.get('l_coronavirus')
			if last_date_coronavirus=="":
				vac_coustmer.last_date_corona='1000-01-01'
			else:
				vac_coustmer.last_date_corona=last_date_coronavirus
			last_date_giardia=request.POST.get('l_giardia')
			if last_date_giardia=="":
				vac_coustmer.last_date_giardia='1000-01-01'
			else:
				vac_coustmer.last_date_giardia=last_date_giardia
			last_date_dhpp=request.POST.get('l_dhpp')
			if last_date_dhpp=="":
				vac_coustmer.last_date_CAV_2='1000-01-01'
			else:
				vac_coustmer.last_date_CAV_2=last_date_dhpp
			last_date_leptospirosis=request.POST.get('l_Leptospirosis')
			if last_date_leptospirosis=="":
				vac_coustmer.last_date_leptospirosis='1000-01-01'
			else:
				vac_coustmer.last_date_leptospirosis=last_date_leptospirosis

			last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
			last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
			last_date_Feline_vaccine=request.POST.get('l_Feline')
			if last_date_9_in_1_vaccine=="":
				vac_coustmer.last_date_9_in_1_vaccine='1000-01-01'
			else:
				vac_coustmer.last_date_9_in_1_vaccine=last_date_9_in_1_vaccine
			if last_date_10_in_1_vaccine=="":
				vac_coustmer.last_date_10_in_1_vaccine='1000-01-01'
			else:
				vac_coustmer.last_date_10_in_1_vaccine=last_date_10_in_1_vaccine
			if last_date_Feline_vaccine=="":
				vac_coustmer.last_date_Feline_vaccine='1000-01-01'
			else:
				vac_coustmer.last_date_Feline_vaccine=last_date_Feline_vaccine
			vac_coustmer.save()

			return redirect('addpet',customer_id=customer_id,doc_pk=doc_pk)
		else:
			pet=Pet()
			coustmer_obj=Customer.objects.get(customer_id=customer_id)
			pet.customer_id=coustmer_obj
			petname=request.POST.get('name')
			pet.name=request.POST.get('name')
			pet.breed=request.POST.get('breed')
			year=request.POST.get('age_year')
			year=int(year)
			month=request.POST.get('age_month')
			month=int(month)
			currentdate=date.today()
			birthyear=currentdate.year-year
			currenthmonth=currentdate.month
			birtmonth=currentdate.month-month
			birtday=currentdate.day
			if birtmonth <0:
				month=month-1
				birtmonth=12-month
				if birtmonth == 2:
					if (birthyear % 4) == 0:
						birtday > 29
						birtday=29
					elif (birthyear % 4) != 0:
						birtday > 29
						birtday=28
					elif (birthyear % 100) == 0:
						birtday > 29
						birtday=29
					elif (birthyear % 100) != 0:
						birtday > 29
						birtday=28
			elif birtmonth == 0:
				birtmonth = 12
			else:
				birtmonth=birtmonth
				if birtmonth == 2:
					if (birthyear % 4) == 0:

						birtday > 29
						birtday=29
					elif (birthyear % 4) != 0:

						birtday > 29
						birtday=28
					elif (birthyear % 100) == 0:

						birtday > 29
						birtday=29
					elif (birthyear % 100) != 0:

						birtday > 29
						birtday=28
			pet_birth = datetime.date(birthyear, birtmonth, birtday)
			pet.dob=pet_birth
			pet.gender=request.POST.get('gender')
			breed=request.POST.get('breed')
			age_year=birthyear
			age_month=birtmonth
			gender=request.POST.get('gender')
			if Pet.objects.filter(customer_id__customer_id=customer_id,name=petname).exists():
				petid=Pet.objects.filter(customer_id__customer_id=customer_id).last()
				petid_objid=petid.id
				petid=petid.pet_id
				updte=Pet.objects.filter(id=petid_objid).update(pet_id=petid,breed=breed,dob=pet_birth,gender=gender)
				vac_coustmer=Vaccination_coustmer()
				last_deworming=request.POST.get('last_date')
				last_deworming=last_deworming
				if last_deworming=="":
					vac_coustmer.last_deworming='1000-01-01'
				else:
					vac_coustmer.last_deworming=last_deworming

				pet_obj=Pet.objects.filter(pet_id=petid).last()
				vac_coustmer.pet=pet_obj
				last_date_3_in_1_DAPV=request.POST.get('last_date_3_in_1_DAPV')
				if last_date_3_in_1_DAPV=="":

					vac_coustmer.last_date_3_in_1_DAPV='1000-01-01'
				else:
					vac_coustmer.last_date_3_in_1_DAPV=last_date_3_in_1_DAPV

				last_date_4_in_1_DHPP=request.POST.get('last_date_4_in_1_DHPP')
				if last_date_4_in_1_DHPP=="":

					vac_coustmer.last_date_4_in_1_DHPP='1000-01-01'
				else:
					vac_coustmer.last_date_4_in_1_DHPP=last_date_4_in_1_DHPP

				last_date_5_in_1_DA2PP=request.POST.get('last_date_5_in_1_DA2PP')
				if last_date_5_in_1_DA2PP=="":

					vac_coustmer.last_date_5_in_1_DA2PP='1000-01-01'
				else:
					vac_coustmer.last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP

				last_date_6_in_1_DA2PPC=request.POST.get('last_date_6_in_1_DA2PPC')
				if last_date_6_in_1_DA2PPC=="":

					vac_coustmer.last_date_6_in_1_DA2PPC='1000-01-01'
				else:
					vac_coustmer.last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC

				last_date_7_in_1_DA2PPVL2=request.POST.get('last_date_7_in_1_DA2PPVL2')
				if last_date_7_in_1_DA2PPVL2=="":

					vac_coustmer.last_date_7in1_DA2PPVL2='1000-01-01'
				else:
					vac_coustmer.last_date_7in1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
				last_date_rabies=request.POST.get('l_rabies')
				if last_date_rabies=="":
					vac_coustmer.last_date_rabies='1000-01-01'
				else:
					vac_coustmer.last_date_rabies=last_date_rabies
				last_date_distemper=request.POST.get('l_distemper')
				if last_date_distemper=="":
					vac_coustmer.last_date_distemper='1000-01-01'
				else:
					vac_coustmer.last_date_distemper=last_date_distemper
				last_date_hepatitis=request.POST.get('l_hepatitis')
				if last_date_hepatitis=="":
					vac_coustmer.last_date_CAV_1='1000-01-01'
				else:
					vac_coustmer.last_date_CAV_1=last_date_hepatitis
				last_date_parovirus=request.POST.get('l_parovirus')
				if last_date_parovirus=="":
					vac_coustmer.last_date_parovirus='1000-01-01'
				else:
					vac_coustmer.last_date_parovirus=last_date_parovirus
				last_date_parainfluenza=request.POST.get('l_parainfluenza')
				if last_date_parainfluenza=="":
					vac_coustmer.last_date_parainfluenza='1000-01-01'
				else:
					vac_coustmer.last_date_parainfluenza=last_date_parainfluenza
				last_date_bordetella=request.POST.get('l_bordetella')
				if last_date_bordetella=="":
					vac_coustmer.last_date_bordetella='1000-01-01'
				else:
					vac_coustmer.last_date_bordetella=last_date_bordetella
				last_date_Can_L=request.POST.get('Can_L')
				if last_date_Can_L=="":
					vac_coustmer.last_date_Can_L='1000-01-01'
				else:
					vac_coustmer.last_date_Can_L=last_date_Can_L
				last_date_lyme=request.POST.get('l_lymedisease')
				if last_date_lyme=="":
					vac_coustmer.last_date_lyme='1000-01-01'
				else:
					vac_coustmer.last_date_lyme=last_date_lyme
				last_date_coronavirus=request.POST.get('l_coronavirus')
				if last_date_coronavirus=="":
					vac_coustmer.last_date_corona='1000-01-01'
				else:
					vac_coustmer.last_date_corona=last_date_coronavirus
				last_date_giardia=request.POST.get('l_giardia')
				if last_date_giardia=="":
					vac_coustmer.last_date_giardia='1000-01-01'
				else:
					vac_coustmer.last_date_giardia=last_date_giardia
				last_date_dhpp=request.POST.get('l_dhpp')
				if last_date_dhpp=="":
					vac_coustmer.last_date_CAV_2='1000-01-01'
				else:
					vac_coustmer.last_date_CAV_2=last_date_dhpp
				last_date_leptospirosis=request.POST.get('l_Leptospirosis')
				if last_date_leptospirosis=="":
					vac_coustmer.last_date_leptospirosis='1000-01-01'
				else:
					vac_coustmer.last_date_leptospirosis=last_date_leptospirosis

				last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
				last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
				last_date_Feline_vaccine=request.POST.get('l_Feline')
				if last_date_9_in_1_vaccine=="":
					vac_coustmer.last_date_9_in_1_vaccine='1000-01-01'
				else:
					vac_coustmer.last_date_9_in_1_vaccine=last_date_9_in_1_vaccine
				if last_date_10_in_1_vaccine=="":
					vac_coustmer.last_date_10_in_1_vaccine='1000-01-01'
				else:
					vac_coustmer.last_date_10_in_1_vaccine=last_date_10_in_1_vaccine
				if last_date_Feline_vaccine=="":
					vac_coustmer.last_date_Feline_vaccine='1000-01-01'
				else:
					vac_coustmer.last_date_Feline_vaccine=last_date_Feline_vaccine
				vac_coustmer.save()



				return redirect('pet_list')
			else:
				pet_id_created=set_id()
				pet.pet_id=pet_id_created
				pet.save()
				purpose=PurposeAndDiet()
				pet_obj=Pet.objects.filter(pet_id=pet_id_created).last()
				purpose.pet_id=pet_obj


				vac_coustmer=Vaccination_coustmer()
				last_deworming=request.POST.get('last_date')
				last_deworming=last_deworming
				if last_deworming=="":
					vac_coustmer.last_deworming='1000-01-01'
				else:
					vac_coustmer.last_deworming=last_deworming
				purpose.save()
				main_purpose_id=PurposeAndDiet.objects.get(pet_id=pet_obj).id


				purpose_id=PurposeAndDiet.objects.filter(pet_id__customer_id__customer_id=customer_id).last()
				vac_coustmer.purpose_id=purpose_id
				pet_obj=Pet.objects.filter(pet_id=pet_id_created).last()
				vac_coustmer.pet=pet_obj
				last_date_3_in_1_DAPV=request.POST.get('last_date_3_in_1_DAPV')
				if last_date_3_in_1_DAPV=="":

					vac_coustmer.last_date_3_in_1_DAPV='1000-01-01'
				else:
					vac_coustmer.last_date_3_in_1_DAPV=last_date_3_in_1_DAPV

				last_date_4_in_1_DHPP=request.POST.get('last_date_4_in_1_DHPP')
				if last_date_4_in_1_DHPP=="":

					vac_coustmer.last_date_4_in_1_DHPP='1000-01-01'
				else:
					vac_coustmer.last_date_4_in_1_DHPP=last_date_4_in_1_DHPP

				last_date_5_in_1_DA2PP=request.POST.get('last_date_5_in_1_DA2PP')
				if last_date_5_in_1_DA2PP=="":

					vac_coustmer.last_date_5_in_1_DA2PP='1000-01-01'
				else:
					vac_coustmer.last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP

				last_date_6_in_1_DA2PPC=request.POST.get('last_date_6_in_1_DA2PPC')
				if last_date_6_in_1_DA2PPC=="":

					vac_coustmer.last_date_6_in_1_DA2PPC='1000-01-01'
				else:
					vac_coustmer.last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC

				last_date_7in1_DA2PPVL2=request.POST.get('last_date_7_in_1_DA2PPVL2')
				if last_date_7in1_DA2PPVL2=="":

					vac_coustmer.last_date_7in1_DA2PPVL2='1000-01-01'
				else:
					vac_coustmer.last_date_7in1_DA2PPVL2=last_date_7in1_DA2PPVL2
				last_date_rabies=request.POST.get('l_rabies')
				if last_date_rabies=="":
					vac_coustmer.last_date_rabies='1000-01-01'
				else:
					vac_coustmer.last_date_rabies=last_date_rabies
				last_date_distemper=request.POST.get('l_distemper')
				if last_date_distemper=="":
					vac_coustmer.last_date_distemper='1000-01-01'
				else:
					vac_coustmer.last_date_distemper=last_date_distemper
				last_date_hepatitis=request.POST.get('l_hepatitis')
				if last_date_hepatitis=="":
					vac_coustmer.last_date_CAV_1='1000-01-01'
				else:
					vac_coustmer.last_date_CAV_1=last_date_hepatitis
				last_date_parovirus=request.POST.get('l_parovirus')
				if last_date_parovirus=="":
					vac_coustmer.last_date_parovirus='1000-01-01'
				else:
					vac_coustmer.last_date_parovirus=last_date_parovirus
				last_date_parainfluenza=request.POST.get('l_parainfluenza')
				if last_date_parainfluenza=="":
					vac_coustmer.last_date_parainfluenza='1000-01-01'
				else:
					vac_coustmer.last_date_parainfluenza=last_date_parainfluenza
				last_date_bordetella=request.POST.get('l_bordetella')
				if last_date_bordetella=="":
					vac_coustmer.last_date_bordetella='1000-01-01'
				else:
					vac_coustmer.last_date_bordetella=last_date_bordetella
				last_date_Can_L=request.POST.get('Can_L')
				if last_date_Can_L=="":
					vac_coustmer.last_date_Can_L='1000-01-01'
				else:
					vac_coustmer.last_date_Can_L=last_date_Can_L
				last_date_lyme=request.POST.get('l_lymedisease')
				if last_date_lyme=="":
					vac_coustmer.last_date_lyme='1000-01-01'
				else:
					vac_coustmer.last_date_lyme=last_date_lyme
				last_date_coronavirus=request.POST.get('l_coronavirus')
				if last_date_coronavirus=="":
					vac_coustmer.last_date_corona='1000-01-01'
				else:
					vac_coustmer.last_date_corona=last_date_coronavirus
				last_date_giardia=request.POST.get('l_giardia')
				if last_date_giardia=="":
					vac_coustmer.last_date_giardia='1000-01-01'
				else:
					vac_coustmer.last_date_giardia=last_date_giardia
				last_date_dhpp=request.POST.get('l_dhpp')
				if last_date_dhpp=="":
					vac_coustmer.last_date_CAV_2='1000-01-01'
				else:
					vac_coustmer.last_date_CAV_2=last_date_dhpp

				last_date_leptospirosis=request.POST.get('l_Leptospirosis')
				if last_date_leptospirosis=="":
					vac_coustmer.last_date_leptospirosis='1000-01-01'
				else:
					vac_coustmer.last_date_leptospirosis=last_date_leptospirosis

				last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
				last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
				last_date_Feline_vaccine=request.POST.get('l_Feline')
				if last_date_9_in_1_vaccine=="":
					vac_coustmer.last_date_9_in_1_vaccine='1000-01-01'
				else:
					vac_coustmer.last_date_9_in_1_vaccine=last_date_9_in_1_vaccine
				if last_date_10_in_1_vaccine=="":
					vac_coustmer.last_date_10_in_1_vaccine='1000-01-01'
				else:
					vac_coustmer.last_date_10_in_1_vaccine=last_date_10_in_1_vaccine
				if last_date_Feline_vaccine=="":
					vac_coustmer.last_date_Feline_vaccine='1000-01-01'
				else:
					vac_coustmer.last_date_Feline_vaccine=last_date_Feline_vaccine
				vac_coustmer.save()

				customer_pk=Customer.objects.get(customer_id=customer_id).id
				request.session['pass_dict_session']={'customer_pk':customer_pk,'doctor_pk':doc_pk,'purpose_id':main_purpose_id,'consulted_pet':pet_id_created}


				return redirect('pet_dite')



def purpose_and_dite(request):
	check_visit = request.session['visit_check']
	url_parameters=request.session['pass_dict_session']
	customer_pk=url_parameters['customer_pk']
	consulted_pet=url_parameters['consulted_pet']
	doc_pk=url_parameters['doctor_pk']
	purpose_id=url_parameters['purpose_id']
	customer_id=request.session['customer_id']
	if request.method =="GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id :
				return render(request,'customer/Customer_diet.html',
				{'customer_id':customer_id,'doc_pk':doc_pk,'check_visit':check_visit})
			else:
				return redirect('customer_login_home')
		else:
			return redirect('customer_login_home')
	if request.method == "POST":

		diet=request.POST.get('set1')
		diet=empty_string_remove(diet)
		diet_state=request.POST.get('set2')
		diet_state=empty_string_remove (diet_state)
		diet = PurposeAndDiet.objects.filter(id=purpose_id).update(diet=diet,
		diet_state=diet_state)
		return redirect('purpose_visit')



def addpet(request,doc_pk=None):
	if request.method =="GET":
		customer_id=request.session['customer_id']
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id :
				return render(request,'customer/Customer_addpet.html',{'customer_id':customer_id,'doc_pk':doc_pk})
			else:
				return redirect ('customer_login_home')
		else:
			return redirect('customer_login_home')
	if request.method=='POST':
		customer_id=request.session['customer_id']
		pet=Pet()
		coustmer_obj=Customer.objects.get(customer_id=customer_id)
		pet.customer_id=coustmer_obj
		petname=request.POST.get('name')
		pet.name=request.POST.get('name')
		pet.breed=request.POST.get('breed')
		petyears=request.POST.get('age_year')
		year=int(petyears)
		print(year,'uearrrrrrrr')
		month=request.POST.get('age_month')
		month=int(month)
		currentdate=date.today()
		birthyear=currentdate.year-year
		print(birthyear)
		currenthmonth=currentdate.month
		birtmonth=currentdate.month-month
		birtday=currentdate.day
		print(birtmonth,'month')
		if birtmonth <0:
			month=month-1
			birtmonth=12-month
			if birtmonth == 2:
				if (birthyear % 4) == 0:
					print('%4')
					birtday > 29
					birtday=29
				elif (birthyear % 4) != 0:
					print('!%4')
					birtday > 29
					birtday=28
				elif (birthyear % 100) == 0:
					print('%100')
					birtday > 29
					birtday=29
				elif (birthyear % 100) != 0:
					print('!%100')
					birtday > 29
					birtday=28
		elif birtmonth == 0:
			birtmonth = 12
		else:
			birtmonth=birtmonth
			print('regural')
			if birtmonth == 2:
				if (birthyear % 4) == 0:
					print('%4')
					birtday > 29
					birtday=29
				elif (birthyear % 4) != 0:
					print('!%4')
					birtday > 29
					birtday=28
				elif (birthyear % 100) == 0:
					print('%100')
					birtday > 29
					birtday=29
				elif (birthyear % 100) != 0:
					print('!%100')
					birtday > 29
					birtday=28
		pet_birth = datetime.date(birthyear, birtmonth, birtday)
		print(pet_birth,'4444444444444444444444444444444')
		pet.dob=pet_birth
		pet.gender=request.POST.get('gender')

		breed=request.POST.get('breed')
		age_year=birthyear
		age_month=birtmonth
		gender=request.POST.get('gender')
		if Pet.objects.filter(customer_id__customer_id=customer_id,name=petname).exists():
			petid=Pet.objects.filter(customer_id__customer_id=customer_id).last()
			petid_objid=petid.id
			petid=petid.pet_id
			updte=Pet.objects.filter(id=petid_objid).update(pet_id=petid,breed=breed,dob=pet_birth,gender=gender)
			purpose=PurposeAndDiet()
			pet_obj=Pet.objects.filter(customer_id__customer_id=customer_id).last()
			purpose.pet_id=Pet.objects.filter(customer_id__customer_id=customer_id).last()
			vac_coustmer=Vaccination_coustmer()
			last_deworming=request.POST.get('last_date')
			last_deworming=last_deworming
			if last_deworming=="":
				vac_coustmer.last_deworming='1000-01-01'
			else:
				vac_coustmer.last_deworming=last_deworming

			pet_obj=Pet.objects.filter(pet_id=petid).last()
			vac_coustmer.pet=pet_obj
			last_date_3_in_1_DAPV=request.POST.get('last_date_3_in_1_DAPV')
			if last_date_3_in_1_DAPV=="":

				vac_coustmer.last_date_3_in_1_DAPV='1000-01-01'
			else:
				vac_coustmer.last_date_3_in_1_DAPV=last_date_3_in_1_DAPV

			last_date_4_in_1_DHPP=request.POST.get('last_date_4_in_1_DHPP')
			if last_date_4_in_1_DHPP=="":

				vac_coustmer.last_date_4_in_1_DHPP='1000-01-01'
			else:
				vac_coustmer.last_date_4_in_1_DHPP=last_date_4_in_1_DHPP

			last_date_5_in_1_DA2PP=request.POST.get('last_date_5_in_1_DA2PP')
			if last_date_5_in_1_DA2PP=="":

				vac_coustmer.last_date_5_in_1_DA2PP='1000-01-01'
			else:
				vac_coustmer.last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP

			last_date_6_in_1_DA2PPC=request.POST.get('last_date_6_in_1_DA2PPC')
			if last_date_6_in_1_DA2PPC=="":

				vac_coustmer.last_date_6_in_1_DA2PPC='1000-01-01'
			else:
				vac_coustmer.last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC

			last_date_7_in_1_DA2PPVL2=request.POST.get('last_date_7_in_1_DA2PPVL2')
			if last_date_7_in_1_DA2PPVL2=="":

				vac_coustmer.last_date_7in1_DA2PPVL2='1000-01-01'
			else:
				vac_coustmer.last_date_7in1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
			last_date_rabies=request.POST.get('l_rabies')
			if last_date_rabies=="":
				vac_coustmer.last_date_rabies='1000-01-01'
			else:
				vac_coustmer.last_date_rabies=last_date_rabies
			last_date_distemper=request.POST.get('l_distemper')
			if last_date_distemper=="":
				vac_coustmer.last_date_distemper='1000-01-01'
			else:
				vac_coustmer.last_date_distemper=last_date_distemper
			last_date_hepatitis=request.POST.get('l_hepatitis')
			if last_date_hepatitis=="":
				vac_coustmer.last_date_CAV_1='1000-01-01'
			else:
				vac_coustmer.last_date_CAV_1=last_date_hepatitis
			last_date_parovirus=request.POST.get('l_parovirus')
			if last_date_parovirus=="":
				vac_coustmer.last_date_parovirus='1000-01-01'
			else:
				vac_coustmer.last_date_parovirus=last_date_parovirus
			last_date_parainfluenza=request.POST.get('l_parainfluenza')
			if last_date_parainfluenza=="":
				vac_coustmer.last_date_parainfluenza='1000-01-01'
			else:
				vac_coustmer.last_date_parainfluenza=last_date_parainfluenza
			last_date_bordetella=request.POST.get('l_bordetella')
			if last_date_bordetella=="":
				vac_coustmer.last_date_bordetella='1000-01-01'
			else:
				vac_coustmer.last_date_bordetella=last_date_bordetella
			last_date_Can_L=request.POST.get('Can_L')
			if last_date_Can_L=="":
				vac_coustmer.last_date_Can_L='1000-01-01'
			else:
				vac_coustmer.last_date_Can_L=last_date_Can_L
			last_date_lyme=request.POST.get('l_lymedisease')
			if last_date_lyme=="":
				vac_coustmer.last_date_lyme='1000-01-01'
			else:
				vac_coustmer.last_date_lyme=last_date_lyme
			last_date_coronavirus=request.POST.get('l_coronavirus')
			if last_date_coronavirus=="":
				vac_coustmer.last_date_corona='1000-01-01'
			else:
				vac_coustmer.last_date_corona=last_date_coronavirus
			last_date_giardia=request.POST.get('l_giardia')
			if last_date_giardia=="":
				vac_coustmer.last_date_giardia='1000-01-01'
			else:
				vac_coustmer.last_date_giardia=last_date_giardia
			last_date_dhpp=request.POST.get('l_dhpp')
			if last_date_dhpp=="":
				vac_coustmer.last_date_CAV_2='1000-01-01'
			else:
				vac_coustmer.last_date_CAV_2=last_date_dhpp
			last_date_leptospirosis=request.POST.get('l_Leptospirosis')
			if last_date_leptospirosis=="":
				vac_coustmer.last_date_leptospirosis='1000-01-01'
			else:
				vac_coustmer.last_date_leptospirosis=last_date_leptospirosis

			last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
			last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
			last_date_Feline_vaccine=request.POST.get('l_Feline')
			if last_date_9_in_1_vaccine=="":
				vac_coustmer.last_date_9_in_1_vaccine='1000-01-01'
			else:
				vac_coustmer.last_date_9_in_1_vaccine=last_date_9_in_1_vaccine
			if last_date_10_in_1_vaccine=="":
				vac_coustmer.last_date_10_in_1_vaccine='1000-01-01'
			else:
				vac_coustmer.last_date_10_in_1_vaccine=last_date_10_in_1_vaccine
			if last_date_Feline_vaccine=="":
				vac_coustmer.last_date_Feline_vaccine='1000-01-01'
			else:
				vac_coustmer.last_date_Feline_vaccine=last_date_Feline_vaccine
			vac_coustmer.save()

			return redirect('pet_list')
		else:
			pet_id_created=set_id()
			pet.pet_id=pet_id_created
			pet.save()
			purpose=PurposeAndDiet()
			pet_obj=Pet.objects.filter(pet_id=pet_id_created).last()
			purpose.pet_id=pet_obj
			vac_coustmer=Vaccination_coustmer()
			last_deworming=request.POST.get('last_date')
			last_deworming=last_deworming
			if last_deworming=="":
				vac_coustmer.last_deworming='1000-01-01'
			else:
				vac_coustmer.last_deworming=last_deworming
			pet_obj=Pet.objects.filter(pet_id=pet_id_created).last()
			vac_coustmer.pet=pet_obj
			last_date_3_in_1_DAPV=request.POST.get('last_date_3_in_1_DAPV')
			if last_date_3_in_1_DAPV=="":

				vac_coustmer.last_date_3_in_1_DAPV='1000-01-01'
			else:
				vac_coustmer.last_date_3_in_1_DAPV=last_date_3_in_1_DAPV

			last_date_4_in_1_DHPP=request.POST.get('last_date_4_in_1_DHPP')
			if last_date_4_in_1_DHPP=="":

				vac_coustmer.last_date_4_in_1_DHPP='1000-01-01'
			else:
				vac_coustmer.last_date_4_in_1_DHPP=last_date_4_in_1_DHPP

			last_date_5_in_1_DA2PP=request.POST.get('last_date_5_in_1_DA2PP')
			if last_date_5_in_1_DA2PP=="":

				vac_coustmer.last_date_5_in_1_DA2PP='1000-01-01'
			else:
				vac_coustmer.last_date_5_in_1_DA2PP=last_date_5_in_1_DA2PP

			last_date_6_in_1_DA2PPC=request.POST.get('last_date_6_in_1_DA2PPC')
			if last_date_6_in_1_DA2PPC=="":

				vac_coustmer.last_date_6_in_1_DA2PPC='1000-01-01'
			else:
				vac_coustmer.last_date_6_in_1_DA2PPC=last_date_6_in_1_DA2PPC

			last_date_7_in_1_DA2PPVL2=request.POST.get('last_date_7_in_1_DA2PPVL2')
			if last_date_7_in_1_DA2PPVL2=="":

				vac_coustmer.last_date_7in1_DA2PPVL2='1000-01-01'
			else:
				vac_coustmer.last_date_7in1_DA2PPVL2=last_date_7_in_1_DA2PPVL2
			last_date_rabies=request.POST.get('l_rabies')
			if last_date_rabies=="":
				vac_coustmer.last_date_rabies='1000-01-01'
			else:
				vac_coustmer.last_date_rabies=last_date_rabies
			last_date_distemper=request.POST.get('l_distemper')
			if last_date_distemper=="":
				vac_coustmer.last_date_distemper='1000-01-01'
			else:
				vac_coustmer.last_date_distemper=last_date_distemper
			last_date_hepatitis=request.POST.get('l_hepatitis')
			if last_date_hepatitis=="":
				vac_coustmer.last_date_CAV_1='1000-01-01'
			else:
				vac_coustmer.last_date_CAV_1=last_date_hepatitis
			last_date_parovirus=request.POST.get('l_parovirus')
			if last_date_parovirus=="":
				vac_coustmer.last_date_parovirus='1000-01-01'
			else:
				vac_coustmer.last_date_parovirus=last_date_parovirus
			last_date_parainfluenza=request.POST.get('l_parainfluenza')
			if last_date_parainfluenza=="":
				vac_coustmer.last_date_parainfluenza='1000-01-01'
			else:
				vac_coustmer.last_date_parainfluenza=last_date_parainfluenza
			last_date_bordetella=request.POST.get('l_bordetella')
			if last_date_bordetella=="":
				vac_coustmer.last_date_bordetella='1000-01-01'
			else:
				vac_coustmer.last_date_bordetella=last_date_bordetella
			last_date_Can_L=request.POST.get('Can_L')
			if last_date_Can_L=="":
				vac_coustmer.last_date_Can_L='1000-01-01'
			else:
				vac_coustmer.last_date_Can_L=last_date_Can_L
			last_date_lyme=request.POST.get('l_lymedisease')
			if last_date_lyme=="":
				vac_coustmer.last_date_lyme='1000-01-01'
			else:
				vac_coustmer.last_date_lyme=last_date_lyme
			last_date_coronavirus=request.POST.get('l_coronavirus')
			if last_date_coronavirus=="":
				vac_coustmer.last_date_corona='1000-01-01'
			else:
				vac_coustmer.last_date_corona=last_date_coronavirus
			last_date_giardia=request.POST.get('l_giardia')
			if last_date_giardia=="":
				vac_coustmer.last_date_giardia='1000-01-01'
			else:
				vac_coustmer.last_date_giardia=last_date_giardia
			last_date_dhpp=request.POST.get('l_dhpp')
			if last_date_dhpp=="":
				vac_coustmer.last_date_CAV_2='1000-01-01'
			else:
				vac_coustmer.last_date_CAV_2=last_date_dhpp
			last_date_leptospirosis=request.POST.get('l_Leptospirosis')
			if last_date_leptospirosis=="":
				vac_coustmer.last_date_leptospirosis='1000-01-01'
			else:
				vac_coustmer.last_date_leptospirosis=last_date_leptospirosis

			last_date_9_in_1_vaccine=request.POST.get('l_9_in_1')
			last_date_10_in_1_vaccine=request.POST.get('l_10_in_1')
			last_date_Feline_vaccine=request.POST.get('l_Feline')
			if last_date_9_in_1_vaccine=="":
				vac_coustmer.last_date_9_in_1_vaccine='1000-01-01'
			else:
				vac_coustmer.last_date_9_in_1_vaccine=last_date_9_in_1_vaccine
			if last_date_10_in_1_vaccine=="":
				vac_coustmer.last_date_10_in_1_vaccine='1000-01-01'
			else:
				vac_coustmer.last_date_10_in_1_vaccine=last_date_10_in_1_vaccine
			if last_date_Feline_vaccine=="":
				vac_coustmer.last_date_Feline_vaccine='1000-01-01'
			else:
				vac_coustmer.last_date_Feline_vaccine=last_date_Feline_vaccine
			vac_coustmer.save()

			return redirect('pet_list')


def customer_doc_list(request):
    return render (request, 'customer_doc_list.html')


def pet_details(request):
    return render (request, 'pet_details_1.html')

###############################################################################################################
# ADMIN VIEWS:

def admin(request):
	if request.method == 'POST':
		username=request.POST.get('username')
		request.session['aodh_admin'] = username
		password=request.POST.get('password')
		users=User.objects.all()
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_superuser:
				request.session['admin_user']=user.username
				request.session['admin_user_check']=True
				return redirect('admin_home_page')
			if user.is_staff:
				request.session['admin_user']=user.username
				request.session['admin_user_check']=False
				return render(request,'admin/admin_home.html',{'username':user.username,'superuser':False})
	return render (request,'admin/admin_login.html')

def admin_home(request):
	username=request.session['admin_user']
	superuser=request.session['admin_user_check']
	return render(request,'admin/admin_home.html',{'username':username,'superuser':superuser})



def doctor_registration(request):

	if request.method == 'POST':
		doctor=Doctor()
		doctor.Name_of_doctor=request.POST.get('first_name')
		doctor.first_name=request.POST.get('first_name')
		doctor.last_name=request.POST.get('last_name')
		doctor.Gender=request.POST.get('gender')
		doctor.Date_of_birth=request.POST.get('dob')
		doctor.Experience=request.POST.get('experience')
		doctor.Hospital=request.POST.get('hospital')
		doctor.Email=request.POST.get('email')
		doctor.Mobile=request.POST.get('mobile')
		doctor.Telephone=request.POST.get('telephone')
		doctor.Address=request.POST.get('address')
		doctor.Registration_number=request.POST.get('reg_no')
		doctor.password=request.POST.get('password')
		doctor.Qualification=request.POST.get('Qualification')
		doctor.consultation_fee=request.POST.get('consultation_fee')
		doctor.subscription_fee=request.POST.get('subscription_fee')
		doctor.mode=request.POST.get('Mode')
		doctor.stock_management=request.POST.get('stock_management')
		doctor.live_management=request.POST.get('live_management')
		doctor.save()
		return render(request,'admin/admin_doc_registration.html')
	if request.method=='GET':
		if 'admin_user' in request.session:

			return render(request,'admin/admin_doc_registration.html')
		else:
			return redirect('admin_home')


def doctor_list(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			doctor_list=Doctor.objects.all()
			return render(request,'admin/doctor_list.html',{'doctor_list':doctor_list})
		else:
			return redirect('admin_home')
	if request.method == 'POST':
	    doc_pk=request.POST.get('doc_pk')
	    doctor=Doctor.objects.filter(pk=doc_pk)
	    return render(request,'admin/doctor_details.html',{'doctor':doctor})

def check(request,pk):
    if pk:
        pk=pk
        return render(request,'admin/check.html',{'pk':pk})
    return render(request,'admin/check.html',)

def registrad_users_list(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			users=Customer.objects.all().order_by('-date')
			return render(request,'admin/registred_users_list.html',{'user':users})
		else:
			return redirect('admin_home')
	if request.method=='POST':
		filter_date=request.POST.get('filter_date')
		users=Customer.objects.filter(date=filter_date).order_by('-date')
		return render(request,'admin/registred_users_list.html',{'user':users,'filter_date':filter_date})

def patients_list(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			doctor_list=Doctor.objects.all()
			return render(request,'admin/patients_list.html',{'doctor_list':doctor_list})
		else:
			return redirect('admin_home')
	if request.method == 'POST':
		doc_pk=request.POST.get('doc_pk')
		doct_object=Doctor.objects.get(id=doc_pk)
		from_date=request.POST.get('from_date')
		to_date=request.POST.get('to_date')
		doctorviewlog=DoctorViewLog.objects.filter(booking_date__range=(from_date, to_date),
			doc_pk=doct_object)
		return render(request,'admin/patients_list_detail.html',
			{'doctorviewlog':doctorviewlog})

def payment_anlytics(request):
    return render(request,'admin/payment_anlytics.html')

def doctor_corner(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render (request,'admin/doctors_corner.html')
		else:
			return redirect('admin_home')

def view_confernse(request,pk):
	if request.method=='GET':
		if 'admin_user' in request.session:
			if pk:
				conference = Conferences.objects.filter(id=pk)
				return render (request, 'admin/view_confernse.html',{'conferences':conference})
			else:
				return render (request, 'admin/view_confernse.html')

		else:
			return redirect('admin_home')


def conferences(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			conferences=Conferences.objects.all()
			return render(request,'admin/conferences.html',{'conferences':conferences})
		else:
			return redirect('admin_home')
	if request.method == 'POST':
	    con_pk = request.POST.get('con_pk')
	    conference = Conferences.objects.filter(id=con_pk).delete()
	    return redirect('conferences')



def create_confernse(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render(request,'admin/create_confernse.html')
		else:
			return redirect('admin_home')
	if request.method == 'POST':
		conferences=Conferences()
		conferences.title = request.POST.get('title')
		conferences.location = request.POST.get('location')
		conferences.date = request.POST.get('posted_date')
		timings=request.POST.get('posted_time')
		conferences.timings = timings
		conferences.content = request.POST.get('content')
		conferences.url_link = request.POST.get('link')
		conferences.save()
		return redirect('conferences')


def seminars(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			seminars=Seminars.objects.all()
			return render(request,'admin/seminars.html',{'seminars':seminars})
		else:
			return redirect('admin_home')
	if request.method == 'POST':
		sem_pk = request.POST.get('sem_pk')
		seminar = Seminars.objects.filter(id=sem_pk).delete()
		return redirect('seminars')


def view_seminar(request,pk):
	if request.method=='GET':
		if 'admin_user' in request.session:
			if pk:
				seminar = Seminars.objects.filter(id=pk)
				return render (request, 'admin/view_seminar.html',{'seminars':seminar})
			else:
				return render (request, 'admin/view_seminar.html')
		else:
			return redirect('admin_home')


def create_seminar(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render(request,'admin/create_seminar.html')
		else:
			return redirect('admin_home')

	if request.method == 'POST':
		seminars=Seminars()
		seminars.title = request.POST.get('title')
		seminars.location = request.POST.get('location')
		seminars.date = request.POST.get('posted_date')
		timings=request.POST.get('posted_time')
		seminars.timings = timings
		seminars.content = request.POST.get('content')
		seminars.url_link = request.POST.get('link')
		seminars.save()
		return redirect('seminars')

def vet_news(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			vetnewsobj=Vet_News.objects.all()
			return render(request,'admin/vet_news.html', {'vetnewsobj':vetnewsobj})
		else:
			return redirect('admin_home')

	if request.method == 'POST':

		vn_pk = request.POST.get('vn_pk')
		vetnews = Vet_News.objects.filter(id=vn_pk).delete()
		return redirect('vet_news')


def view_vetnews(request,pk):
	if request.method=='GET':
		if 'admin_user' in request.session:
			if pk:
				vetnews = Vet_News.objects.filter(id=pk)
				return render (request, 'admin/view_vetnews.html',{'vetnews':vetnews})
			else:
				return render (request, 'admin/view_vetnews.html')
		else:
			return redirect('admin_home')


def create_vetnews(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render(request,'admin/create_vetnews.html')
		else:
			return redirect('admin_home')

	if request.method == 'POST':
		vet_news=Vet_News()
		vet_news.title = request.POST.get('title')
		vet_news.location = request.POST.get('location')
		vet_news.date = request.POST.get('posted_date')
		timings=request.POST.get('posted_time')
		vet_news.timings = timings
		vet_news.content = request.POST.get('content')
		vet_news.url_link = request.POST.get('link')
		vet_news.save()
		return redirect('vet_news')

def articles(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			articles=Articles.objects.all()
			return render(request,'admin/articles.html',{'articles':articles})
		else:
			return redirect('admin_home')
	if request.method == 'POST':
		art_pk = request.POST.get('art_pk')
		article = Articles.objects.filter(id=art_pk).delete()
		return redirect('articles')


def view_article(request,pk):
	if request.method=='GET':
		if 'admin_user' in request.session:
			if pk:
				article = Articles.objects.filter(id=pk)
				return render (request, 'admin/view_article.html',{'article':article})
			else:
				return render (request, 'admin/view_article.html')
		else:
			return redirect('admin_home')


def create_article(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render(request,'admin/create_article.html')
		else:
			return redirect('admin_home')
	if request.method == 'POST':
		article=Articles()
		article.article_title = request.POST.get('title')
		article.summery = request.POST.get('summery')
		article.published_on = request.POST.get('posted_date')
		article.authors = request.POST.get('author')
		article.content = request.POST.get('content')
		article.save()
		return redirect('articles')


def case_reports(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			case_reports=Case_Reports.objects.all()
			return render(request,'admin/case_reports.html',{'case_reports':case_reports})
		else:
			return redirect('admin_home')
	if request.method == 'POST':
		report_pk = request.POST.get('report_pk')
		case_report = Case_Reports.objects.filter(id=report_pk).delete()
		return redirect('case_reports')



def view_casereport(request,pk):
	if request.method=='GET':
		if 'admin_user' in request.session:
			if pk:
				casereport = Case_Reports.objects.filter(id=pk)
				return render (request, 'admin/view_casereport.html',{'casereport':casereport})
			else:
				return render (request, 'admin/view_casereport.html')
		else:
			return redirect('admin_home')




def create_casereport(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render(request,'admin/create_casereport.html')
		else:
			return redirect('admin_home')

	if request.method == 'POST':
		casereport=Case_Reports()
		casereport.title = request.POST.get('title')
		casereport.email = request.POST.get('email')
		casereport.published_on = request.POST.get('posted_date')
		casereport.author = request.POST.get('author')
		casereport.content = request.POST.get('content')
		casereport.link = request.POST.get('link')
		casereport.save()
		return redirect('case_reports')

def books(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render(request,'admin/books.html')
		else:
			return redirect('admin_home')
	if request.method == 'POST' and request.FILES['myfile']:
		book = Book()
		book.title = request.POST.get('title')
		book.file =  request.FILES['myfile']
		book.summary = request.POST.get('summary')
		book.save()
		return redirect('books')


def razorpay_dash(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render(request, 'admin/payment_search.html')
		else:
			return redirect('admin_home')
	if request.method == "POST":
		mobile = request.POST.get('mobile')
		filter_date = request.POST.get('filter_date')
		razorpay_data = Razorpay_Dashboard.objects.filter(
				doctor_mobile=mobile, payment_date=filter_date)
		doctor=Doctor.objects.get(Mobile=mobile)

		return render(request, 'admin/payment_dashboard.html', {'data': razorpay_data,'doctor':doctor})

def admin_pet_list(request,customer_id):
	if request.method=='GET':
		if 'admin_user' in request.session:
			customer_obj=Customer.objects.get(customer_id=customer_id)
			pet_list=Pet.objects.filter(customer_id=customer_obj)
			return render(request,'admin/customer_pets_list.html',{'pet_list':pet_list,'customer_obj':customer_obj})
		else:
			return redirect('admin_home')

def admin_pet_summery(request,pet_id):
	if request.method=='GET':
		if 'admin_user' in request.session:
			pet_obj=Pet.objects.get(pet_id=pet_id)
			dates=PurposeAndDiet.objects.filter(pet_id=pet_obj)
			return render(request,'admin/admin_pet_summery.html',{'dates':dates,'pet_id':pet_id})
		else:
			return redirect('admin_home')
	if request.method == "POST":
		purpose_id=request.POST.get('datename')
		pet_obj=Pet.objects.get(pet_id=pet_id)

		purpose_ids=PurposeAndDiet.objects.filter(id=purpose_id,pet_id=pet_obj).last()
		purpose_obj=PurposeAndDiet.objects.get(id=purpose_ids.id)
		try:
			vitals=Vitals.objects.filter(purpose_id=purpose_obj).last()
			vitals=model_to_dict(vitals)
			clean_dict = dict_clean(vitals)
			vitals = clean_dict

		except:
			vitals=''

		try:
			assessment=Assessment.objects.filter(purpose_id=purpose_obj).last()
			assessment=model_to_dict(assessment)
			clean_dict = dict_clean(assessment)
			clean_dict=remove_empty_from_dict(clean_dict)
			assessment = clean_dict
		except:
			assessment=''

		try:

			symptoms=purpose_obj
			symptoms=model_to_dict(symptoms)
			symptoms.pop('purpose_id',None)
			symptoms.pop('id',None)
			symptoms.pop('pet_id',None)

			symptoms.pop('vaccination_purpose',None)
			symptoms.pop('deworming_purpose',None)
			symptoms.pop('last_deworming',None)
			symptoms.pop('status',None)
			symptoms = dict_clean(symptoms)
		except:
			symptoms=''

		try:

			diagnostic=Diagnostics.objects.filter(purpose_id=purpose_obj).last()
			diagnostic=model_to_dict(diagnostic)
			clean_dict = dict_clean(diagnostic)
			diagnostic = remove_empty_from_dict(clean_dict)
		except:
			diagnostic=''

		try:
			prescription=Prescription.objects.filter(purpose_id=purpose_obj).last()
			prescription_image=Prescription.objects.filter(purpose_id=purpose_obj).last()
			prescription=model_to_dict(prescription)
			clean_dict=dict_clean(prescription)
			prescription=remove_empty_from_dict(prescription)
			prescription.pop('purpose_id',None)
			prescription.pop('id',None)
			prescription.pop('date',None)
			prescription.pop('medicine1_name',None)
			prescription.pop('medicine2_name',None)
			prescription.pop('medicine3_name',None)
			prescription.pop('medicine4_name',None)
			prescription.pop('medicine5_name',None)
			prescription.pop('medicine6_name',None)
			prescription.pop('medicine1_quantity',None)
			prescription.pop('medicine2_quantity',None)
			prescription.pop('medicine3_quantity',None)
			prescription.pop('medicine4_quantity',None)
			prescription.pop('medicine5_quantity',None)
			prescription.pop('medicine6_quantity',None)
			prescription.pop('medicine1_dosage_quantity',None)
			prescription.pop('medicine2_dosage_quantity',None)
			prescription.pop('medicine3_dosage_quantity',None)
			prescription.pop('medicine4_dosage_quantity',None)
			prescription.pop('medicine5_dosage_quantity',None)
			prescription.pop('medicine6_dosage_quantity',None)
			prescription.pop('followup_date_unit',None)

		except:
			prescription=''
			prescription_image=''

		try:
			vaccination=Vaccination.objects.filter(purpose_id=purpose_obj).last()
			vaccination=model_to_dict(vaccination)
			vaccination.pop('purpose_id',None)
			vaccination.pop('id',None)
			vaccination.pop('date',None)
			vaccination.pop('pet',None)
			vaccination = { k:v for k,v in vaccination.items() if v!= datetime.date(1000, 1, 1) }
			vaccination=vaccination_dict(vaccination)
		except:
			vaccination=''
		try:
			deworming=Deworming.objects.filter(purpose_id=purpose_obj).last()
			deworming=model_to_dict(deworming)
			deworming.pop('purpose_id',None)
			deworming.pop('id',None)
			deworming.pop('date',None)
			deworming.pop('pet',None)
			deworming = { k:v for k,v in deworming.items() if v!= datetime.date(1000, 1, 1) }
			deworming=vaccination_dict(deworming)

		except:
			deworming=''

		return render(request,'admin/admin_pet_summery_date.html',{'symptoms':symptoms,'vitals':vitals,'assessment':assessment,'media_url':settings.MEDIA_URL,
		'diagnostic':diagnostic,'prescription':prescription,'vaccination':vaccination,'deworming':deworming,'prescription_image':prescription_image})

def admin_pet_summery_date(request,pet_id,date):
	pet_obj=Pet.objects.get(pet_id=pet_id)
	return render(request,'admin/admin_pet_summery_date.html',)

def pet_details(request,customer_id):
	customer_id=customer_id
	pet = Pet()
	if request.method =="GET":
		if 'customer_id' in request.session:
			return render (request, 'pet_details.html',{'customer_id':customer_id})
		else:
			return redirect ('customer_login_home')
		if request.method == 'POST':
			pet.name = request.POST.get('petname')
			pet.save()
			return render (request, 'pet_details.html')

def logout_customer(request):
	# logout(request)
	# return redirect('customer_login_home')

	try:
		if request.session.has_key('customer_id'):
			del request.session['customer_id']
			logout(request)
			return redirect('customer_login_home')
       # request.session.flush(
		if request.session.has_key('doctor_session_id'):
			del request.session['doctor_session_id']
			logout(request)
			return redirect('doctor_login')
	except KeyError:
		pass


#----------------------------------------------------------------------
#doctor corner side bar views

def articles_sbar(request,doc_id):
	doctor=Doctor.objects.get(id=doc_id)
	article=Articles.objects.all()
	bookmark=bookmarks_article.objects.filter(doc=doctor).all()
	x=[]
	for i in bookmark:
		x.append(i.article_id.id)
	return render(request,'doctor_corner/Doctors_corner_articles.html',{'article':article,'doc_id':doc_id,'bookmark':bookmark,'y':x})



def VaccinationDewormingReminder(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render(request,'admin/vaccination.html')
		else:
			return redirect('admin_home')
	if request.method == "POST":
		if '2_days' in request.POST:
			print('2_days')
			remiander_days=2
			last_dict={}
			dict={}
			vacanation_list=[]
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=remiander_days)
			print(remindar_date)
			date_3_in_1_DAPV=Vaccination.objects.filter(due_date_3_in_1_DAPV=remindar_date)
			for r_q in date_3_in_1_DAPV:
				due_3_in_1_DAPV=r_q.due_date_3_in_1_DAPV
				petid_key=r_q.pet.pet_id
				if due_3_in_1_DAPV == remindar_date:
					dict[petid_key] = ['3 in 1 DAPV']
				else:
					pass
			date_4_in_1_DHPP=Vaccination.objects.filter(due_date_4_in_1_DHPP=remindar_date)
			for d_q in date_4_in_1_DHPP:
				due_4_in_1_DHPP=d_q.due_date_4_in_1_DHPP
				petid_key=d_q.pet.pet_id
				if petid_key in dict:
					if due_4_in_1_DHPP == remindar_date:
						x=dict.get(petid_key,"")
						x.append("4 in 1 DHPP")
					else:
						pass
				else:
					dict[petid_key] = ['4 in 1 DHPP']
			date_5_in_1_DA2PP=Vaccination.objects.filter(due_date_5_in_1_DA2PP=remindar_date)
			for h_q in date_5_in_1_DA2PP:
				due_5_in_1_DA2PP=h_q.due_date_5_in_1_DA2PP
				petid_key=h_q.pet.pet_id
				if petid_key in dict:
					if due_5_in_1_DA2PP == remindar_date:
						x=dict.get(petid_key,"")
						x.append("5 in 1 DA2PP")
					else:
						pass
				else:
					dict[petid_key] = ['5 in 1 DA2PP']
			date_6_in_1_DA2PPC=Vaccination.objects.filter(due_date_6_in_1_DA2PPC=remindar_date)
			for p_q in date_6_in_1_DA2PPC:
				due_6_in_1_DA2PPC = p_q.due_date_6_in_1_DA2PPC
				petid_key=p_q.pet.pet_id
				if petid_key in dict:
					if due_6_in_1_DA2PPC == remindar_date:
						x=dict.get(petid_key,"")
						x.append("6 in 1 DA2PPC")
					else:
						pass
				else:
					dict[petid_key] = ['6 in 1 DA2PPC']
			date_7_in_1_DA2PPVL2=Vaccination.objects.filter(due_date_7_in_1_DA2PPVL2=remindar_date)
			for para_q in date_7_in_1_DA2PPVL2:
				due_7_in_1_DA2PPVL2=para_q.due_date_7_in_1_DA2PPVL2
				petid_key=para_q.pet.pet_id
				if petid_key in dict:
					if due_7_in_1_DA2PPVL2 == remindar_date:
						x=dict.get(petid_key,"")
						x.append("7 in 1 DA2PPVL2")
					else:
						pass
				else:
					dict[petid_key] = ['7 in 1 DA2PPVL2']
			date_rabies=Vaccination.objects.filter(due_date_rabies=remindar_date)
			for b_q in date_rabies:
				due_rabies=b_q.due_date_rabies
				petid_key=b_q.pet.pet_id
				if petid_key in dict:
					if due_rabies == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Rabies")
					else:
						pass
				else:
					dict[petid_key] = ['Rabies']
			date_distemper=Vaccination.objects.filter(due_date_distemper=remindar_date)
			for l_q in date_distemper:
				due_distemper=l_q.due_date_distemper
				petid_key=l_q.pet.pet_id
				if petid_key in dict:
					if due_distemper == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Distemper")
					else:
						pass
				else:
					dict[petid_key] = ['Distemper']
			date_CAV_1=Vaccination.objects.filter(due_date_CAV_1=remindar_date)
			for ly_q in date_CAV_1:
				due_CAV_1=ly_q.due_date_CAV_1
				petid_key=ly_q.pet.pet_id
				if petid_key in dict:
					if due_CAV_1 == remindar_date:
						x=dict.get(petid_key,"")
						x.append("CAV 1")
					else:
						pass
				else:
					dict[petid_key] = ['CAV 1']
			date_parovirus=Vaccination.objects.filter(due_date_parovirus=remindar_date)
			for c_q in date_parovirus:
				due_parovirus=c_q.due_date_parovirus
				petid_key=c_q.pet.pet_id
				if petid_key in dict:
					if due_parovirus == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Parovirus")
					else:
						pass
				else:
					dict[petid_key] = ['Parovirus']
			date_parainfluenza=Vaccination.objects.filter(due_date_parainfluenza=remindar_date)
			for q_q in date_parainfluenza:
				due_parainfluenza=q_q.due_date_parainfluenza
				petid_key=q_q.pet.pet_id
				if petid_key in dict:
					if due_parainfluenza == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Parainfluenza")
					else:
						pass
				else:
					dict[petid_key] = ['Parainfluenza']
			# print('ok1')
			dhpp_qs=Vaccination.objects.filter(due_date_CAV_2=remindar_date)
			for dh_q in dhpp_qs:
				dhpp_due_date=dh_q.due_date_CAV_2
				petid_key=dh_q.pet.pet_id
				if petid_key in dict:
					if dhpp_due_date == remindar_date:
						x=dict.get(petid_key,"")
						x.append("CAV 2")
					else:
						pass
				else:
					dict[petid_key] = ['CAV 2']

			dhpp_qs=Vaccination.objects.filter(due_date_Can_L=remindar_date)
			for dh_q in dhpp_qs:
				dhpp_due_date=dh_q.due_date_Can_L
				petid_key=dh_q.pet.pet_id
				if petid_key in dict:
					if dhpp_due_date == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Can L")
					else:
						pass
				else:
					dict[petid_key] = ['Can L']
			date_bordetella=Vaccination.objects.filter(due_date_bordetella=remindar_date)
			for dapv in date_bordetella:
				due_bordetella=dapv.due_date_bordetella
				petid_key=dapv.pet.pet_id
				if petid_key in dict:
					if due_bordetella == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Bordetella")
					else:
						pass
				else:
					dict[petid_key] = ['Bordetella']

			date_lyme=Vaccination.objects.filter(due_date_lyme=remindar_date)
			for dahpp in date_lyme:
				due_lyme=dahpp.due_date_lyme
				petid_key=dahpp.pet.pet_id
				if petid_key in dict:
					if due_lyme == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Lyme")
					else:
						pass
				else:
					dict[petid_key] = ['Lyme']

			date_corona=Vaccination.objects.filter(due_date_corona=remindar_date)
			for da2pp in date_corona:
				due_corona=da2pp.due_date_corona
				petid_key=da2pp.pet.pet_id
				if petid_key in dict:
					if due_corona == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Corona")
					else:
						pass
				else:
					dict[petid_key] = ['Corona']

			date_giardia=Vaccination.objects.filter(due_date_giardia=remindar_date)
			for da2ppc in date_giardia:
				due_giardia=da2ppc.due_date_giardia
				petid_key=da2ppc.pet.pet_id
				if petid_key in dict:
					if due_giardia == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Giardia")
					else:
						pass
				else:
					dict[petid_key] = ['Giardia']

			date_leptospirosis=Vaccination.objects.filter(due_date_leptospirosis=remindar_date)
			for da2ppvl2 in date_leptospirosis:
				due_leptospirosis=da2ppvl2.due_date_leptospirosis
				petid_key=da2ppvl2.pet.pet_id
				if petid_key in dict:
					if due_leptospirosis == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Leptospirosis")
					else:
						pass
				else:
					dict[petid_key] = ['Leptospirosis']
			dict_keys=dict.keys()
			print(dict_keys,'ffhfhfhffh')
			for item in dict_keys:
				print(item,'hfajkshfkjahfkjahdfkjahskjfhasjkh')
				doctor=DoctorViewLog.objects.filter(pet_id__pet_id=item).last().doc_pk.Name_of_doctor
				hospital_name=DoctorViewLog.objects.filter(pet_id__pet_id=item).last().doc_pk.Hospital

				pet=Pet.objects.get(pet_id=item)
				if Vccination_Remainder.objects.filter(pet_id=pet,remiander_date=remindar_date,date=today_date).exists():
					pass
				else:
					vaccinations=dict.get(item,"")
					vaccination_remainder=Vccination_Remainder()
					customer_obj=pet.customer_id
					vaccination_remainder.pet=pet
					vaccination_remainder.customer=customer_obj
					vaccinations =list(dict.fromkeys(vaccinations))
					vaccination_remainder.vacanation_list=vaccinations
					vaccination_remainder.doctor=doctor
					vaccination_remainder.remiander_date=remindar_date
					vaccination_remainder.hospital=hospital_name
					vaccination_remainder.save()
			#showing vacanation list_patient
			vacanation_list_rem=Vccination_Remainder.objects.filter(date=today_date,remiander_date=remindar_date)



			return render(request,'admin/vaccination.html',{'vacanation_list_rem':vacanation_list_rem,'remindar_date':remindar_date,'generated_day':'before_two'})
		elif '1_day' in request.POST:
			print('1_day')
			remiander_days=1
			last_dict={}
			dict={}
			vacanation_list=[]
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=remiander_days)
			date_3_in_1_DAPV=Vaccination.objects.filter(due_date_3_in_1_DAPV=remindar_date)
			for r_q in date_3_in_1_DAPV:
				due_3_in_1_DAPV=r_q.due_date_3_in_1_DAPV
				petid_key=r_q.pet.pet_id
				if due_3_in_1_DAPV == remindar_date:
					dict[petid_key] = ['3 in 1 DAPV']
				else:
					pass
			date_4_in_1_DHPP=Vaccination.objects.filter(due_date_4_in_1_DHPP=remindar_date)
			for d_q in date_4_in_1_DHPP:
				due_4_in_1_DHPP=d_q.due_date_4_in_1_DHPP
				petid_key=d_q.pet.pet_id
				if petid_key in dict:
					if due_4_in_1_DHPP == remindar_date:
						x=dict.get(petid_key,"")
						x.append("4 in 1 DHPP")
					else:
						pass
				else:
					dict[petid_key] = ['4 in 1 DHPP']
			date_5_in_1_DA2PP=Vaccination.objects.filter(due_date_5_in_1_DA2PP=remindar_date)
			for h_q in date_5_in_1_DA2PP:
				due_5_in_1_DA2PP=h_q.due_date_5_in_1_DA2PP
				petid_key=h_q.pet.pet_id
				if petid_key in dict:
					if due_5_in_1_DA2PP == remindar_date:
						x=dict.get(petid_key,"")
						x.append("5 in 1 DA2PP")
					else:
						pass
				else:
					dict[petid_key] = ['5 in 1 DA2PP']
			date_6_in_1_DA2PPC=Vaccination.objects.filter(due_date_6_in_1_DA2PPC=remindar_date)
			for p_q in date_6_in_1_DA2PPC:
				due_6_in_1_DA2PPC = p_q.due_date_6_in_1_DA2PPC
				petid_key=p_q.pet.pet_id
				if petid_key in dict:
					if due_6_in_1_DA2PPC == remindar_date:
						x=dict.get(petid_key,"")
						x.append("6 in 1 DA2PPC")
					else:
						pass
				else:
					dict[petid_key] = ['6 in 1 DA2PPC']
			date_7_in_1_DA2PPVL2=Vaccination.objects.filter(due_date_7_in_1_DA2PPVL2=remindar_date)
			for para_q in date_7_in_1_DA2PPVL2:
				due_7_in_1_DA2PPVL2=para_q.due_date_7_in_1_DA2PPVL2
				petid_key=para_q.pet.pet_id
				if petid_key in dict:
					if due_7_in_1_DA2PPVL2 == remindar_date:
						x=dict.get(petid_key,"")
						x.append("7 in 1 DA2PPVL2")
					else:
						pass
				else:
					dict[petid_key] = ['7 in 1 DA2PPVL2']
			date_rabies=Vaccination.objects.filter(due_date_rabies=remindar_date)
			for b_q in date_rabies:
				due_rabies=b_q.due_date_rabies
				petid_key=b_q.pet.pet_id
				if petid_key in dict:
					if due_rabies == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Rabies")
					else:
						pass
				else:
					dict[petid_key] = ['Rabies']
			date_distemper=Vaccination.objects.filter(due_date_distemper=remindar_date)
			for l_q in date_distemper:
				due_distemper=l_q.due_date_distemper
				petid_key=l_q.pet.pet_id
				if petid_key in dict:
					if due_distemper == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Distemper")
					else:
						pass
				else:
					dict[petid_key] = ['Distemper']
			date_CAV_1=Vaccination.objects.filter(due_date_CAV_1=remindar_date)
			for ly_q in date_CAV_1:
				due_CAV_1=ly_q.due_date_CAV_1
				petid_key=ly_q.pet.pet_id
				if petid_key in dict:
					if due_CAV_1 == remindar_date:
						x=dict.get(petid_key,"")
						x.append("CAV 1")
					else:
						pass
				else:
					dict[petid_key] = ['CAV 1']
			date_parovirus=Vaccination.objects.filter(due_date_parovirus=remindar_date)
			for c_q in date_parovirus:
				due_parovirus=c_q.due_date_parovirus
				petid_key=c_q.pet.pet_id
				if petid_key in dict:
					if due_parovirus == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Parovirus")
					else:
						pass
				else:
					dict[petid_key] = ['Parovirus']
			date_parainfluenza=Vaccination.objects.filter(due_date_parainfluenza=remindar_date)
			for q_q in date_parainfluenza:
				due_parainfluenza=q_q.due_date_parainfluenza
				petid_key=q_q.pet.pet_id
				if petid_key in dict:
					if due_parainfluenza == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Parainfluenza")
					else:
						pass
				else:
					dict[petid_key] = ['Parainfluenza']
			dhpp_qs=Vaccination.objects.filter(due_date_CAV_2=remindar_date)
			for dh_q in dhpp_qs:
				dhpp_due_date=dh_q.due_date_CAV_2
				petid_key=dh_q.pet.pet_id
				if petid_key in dict:
					if dhpp_due_date == remindar_date:
						x=dict.get(petid_key,"")
						x.append("CAV 2")
					else:
						pass
				else:
					dict[petid_key] = ['CAV 2']

			dhpp_qs=Vaccination.objects.filter(due_date_Can_L=remindar_date)
			for dh_q in dhpp_qs:
				dhpp_due_date=dh_q.due_date_Can_L
				petid_key=dh_q.pet.pet_id
				if petid_key in dict:
					if dhpp_due_date == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Can L")
					else:
						pass
				else:
					dict[petid_key] = ['Can L']
			date_bordetella=Vaccination.objects.filter(due_date_bordetella=remindar_date)
			for dapv in date_bordetella:
				due_bordetella=dapv.due_date_bordetella
				petid_key=dapv.pet.pet_id
				if petid_key in dict:
					if due_bordetella == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Bordetella")
					else:
						pass
				else:
					dict[petid_key] = ['Bordetella']

			date_lyme=Vaccination.objects.filter(due_date_lyme=remindar_date)
			for dahpp in date_lyme:
				due_lyme=dahpp.due_date_lyme
				petid_key=dahpp.pet.pet_id
				if petid_key in dict:
					if due_lyme == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Lyme")
					else:
						pass
				else:
					dict[petid_key] = ['Lyme']

			date_corona=Vaccination.objects.filter(due_date_corona=remindar_date)
			for da2pp in date_corona:
				due_corona=da2pp.due_date_corona
				petid_key=da2pp.pet.pet_id
				if petid_key in dict:
					if due_corona == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Corona")
					else:
						pass
				else:
					dict[petid_key] = ['Corona']

			date_giardia=Vaccination.objects.filter(due_date_giardia=remindar_date)
			for da2ppc in date_giardia:
				due_giardia=da2ppc.due_date_giardia
				petid_key=da2ppc.pet.pet_id
				if petid_key in dict:
					if due_giardia == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Giardia")
					else:
						pass
				else:
					dict[petid_key] = ['Giardia']

			date_leptospirosis=Vaccination.objects.filter(due_date_leptospirosis=remindar_date)
			for da2ppvl2 in date_leptospirosis:
				due_leptospirosis=da2ppvl2.due_date_leptospirosis
				petid_key=da2ppvl2.pet.pet_id
				if petid_key in dict:
					if due_leptospirosis == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Leptospirosis")
					else:
						pass
				else:
					dict[petid_key] = ['Leptospirosis']
			dict_keys=dict.keys()
			for item in dict_keys:
				print(item,'hfajkshfkjahfkjahdfkjahskjfhasjkh')
				doctor=DoctorViewLog.objects.filter(pet_id__pet_id=item).last().doc_pk.Name_of_doctor
				hospital_name=DoctorViewLog.objects.filter(pet_id__pet_id=item).last().doc_pk.Hospital

				pet=Pet.objects.get(pet_id=item)

				if Vccination_Remainder.objects.filter(pet_id=pet,remiander_date=remindar_date,date=today_date).exists():
					pass
				else:
					vaccination_remainder=Vccination_Remainder()
					vaccinations=dict.get(item,"")

					customer_obj=pet.customer_id
					vaccination_remainder.pet=pet
					vaccination_remainder.customer=customer_obj
					vaccinations =list(dict.fromkeys(vaccinations))
					vaccination_remainder.vacanation_list=vaccinations
					vaccination_remainder.doctor=doctor
					vaccination_remainder.remiander_date=remindar_date
					vaccination_remainder.hospital=hospital_name
					vaccination_remainder.save()
			#showing vacanation list_patient
			vacanation_list_rem=Vccination_Remainder.objects.filter(date=today_date,remiander_date=remindar_date)
			return render(request,'admin/vaccination.html',{'vacanation_list_rem':vacanation_list_rem,'remindar_date':remindar_date,'generated_day':'before_one'})

		elif 'on_day' in request.POST:
			print('on_day')

			last_dict={}
			dict={}
			vacanation_list=[]
			today_date=date.today()
			remindar_date = date.today()
			date_3_in_1_DAPV=Vaccination.objects.filter(due_date_3_in_1_DAPV=remindar_date)
			for r_q in date_3_in_1_DAPV:
				due_3_in_1_DAPV=r_q.due_date_3_in_1_DAPV
				petid_key=r_q.pet.pet_id
				if due_3_in_1_DAPV == remindar_date:
					dict[petid_key] = ['3 in 1 DAPV']
				else:
					pass
			date_4_in_1_DHPP=Vaccination.objects.filter(due_date_4_in_1_DHPP=remindar_date)
			for d_q in date_4_in_1_DHPP:
				due_4_in_1_DHPP=d_q.due_date_4_in_1_DHPP
				petid_key=d_q.pet.pet_id
				if petid_key in dict:
					if due_4_in_1_DHPP == remindar_date:
						x=dict.get(petid_key,"")
						x.append("4 in 1 DHPP")
					else:
						pass
				else:
					dict[petid_key] = ['4 in 1 DHPP']
			date_5_in_1_DA2PP=Vaccination.objects.filter(due_date_5_in_1_DA2PP=remindar_date)
			for h_q in date_5_in_1_DA2PP:
				due_5_in_1_DA2PP=h_q.due_date_5_in_1_DA2PP
				petid_key=h_q.pet.pet_id
				if petid_key in dict:
					if due_5_in_1_DA2PP == remindar_date:
						x=dict.get(petid_key,"")
						x.append("5 in 1 DA2PP")
					else:
						pass
				else:
					dict[petid_key] = ['5 in 1 DA2PP']
			date_6_in_1_DA2PPC=Vaccination.objects.filter(due_date_6_in_1_DA2PPC=remindar_date)
			for p_q in date_6_in_1_DA2PPC:
				due_6_in_1_DA2PPC = p_q.due_date_6_in_1_DA2PPC
				petid_key=p_q.pet.pet_id
				if petid_key in dict:
					if due_6_in_1_DA2PPC == remindar_date:
						x=dict.get(petid_key,"")
						x.append("6 in 1 DA2PPC")
					else:
						pass
				else:
					dict[petid_key] = ['6 in 1 DA2PPC']
			date_7_in_1_DA2PPVL2=Vaccination.objects.filter(due_date_7_in_1_DA2PPVL2=remindar_date)
			for para_q in date_7_in_1_DA2PPVL2:
				due_7_in_1_DA2PPVL2=para_q.due_date_7_in_1_DA2PPVL2
				petid_key=para_q.pet.pet_id
				if petid_key in dict:
					if due_7_in_1_DA2PPVL2 == remindar_date:
						x=dict.get(petid_key,"")
						x.append("7 in 1 DA2PPVL2")
					else:
						pass
				else:
					dict[petid_key] = ['7 in 1 DA2PPVL2']
			date_rabies=Vaccination.objects.filter(due_date_rabies=remindar_date)
			for b_q in date_rabies:
				due_rabies=b_q.due_date_rabies
				petid_key=b_q.pet.pet_id
				if petid_key in dict:
					if due_rabies == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Rabies")
					else:
						pass
				else:
					dict[petid_key] = ['Rabies']
			date_distemper=Vaccination.objects.filter(due_date_distemper=remindar_date)
			for l_q in date_distemper:
				due_distemper=l_q.due_date_distemper
				petid_key=l_q.pet.pet_id
				if petid_key in dict:
					if due_distemper == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Distemper")
					else:
						pass
				else:
					dict[petid_key] = ['Distemper']
			date_CAV_1=Vaccination.objects.filter(due_date_CAV_1=remindar_date)
			for ly_q in date_CAV_1:
				due_CAV_1=ly_q.due_date_CAV_1
				petid_key=ly_q.pet.pet_id
				if petid_key in dict:
					if due_CAV_1 == remindar_date:
						x=dict.get(petid_key,"")
						x.append("CAV 1")
					else:
						pass
				else:
					dict[petid_key] = ['CAV 1']
			date_parovirus=Vaccination.objects.filter(due_date_parovirus=remindar_date)
			for c_q in date_parovirus:
				due_parovirus=c_q.due_date_parovirus
				petid_key=c_q.pet.pet_id
				if petid_key in dict:
					if due_parovirus == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Parovirus")
					else:
						pass
				else:
					dict[petid_key] = ['Parovirus']
			date_parainfluenza=Vaccination.objects.filter(due_date_parainfluenza=remindar_date)
			for q_q in date_parainfluenza:
				due_parainfluenza=q_q.due_date_parainfluenza
				petid_key=q_q.pet.pet_id
				if petid_key in dict:
					if due_parainfluenza == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Parainfluenza")
					else:
						pass
				else:
					dict[petid_key] = ['Parainfluenza']
			dhpp_qs=Vaccination.objects.filter(due_date_CAV_2=remindar_date)
			for dh_q in dhpp_qs:
				dhpp_due_date=dh_q.due_date_CAV_2
				petid_key=dh_q.pet.pet_id
				if petid_key in dict:
					if dhpp_due_date == remindar_date:
						x=dict.get(petid_key,"")
						x.append("CAV 2")
					else:
						pass
				else:
					dict[petid_key] = ['CAV 2']

			dhpp_qs=Vaccination.objects.filter(due_date_Can_L=remindar_date)
			for dh_q in dhpp_qs:
				dhpp_due_date=dh_q.due_date_Can_L
				petid_key=dh_q.pet.pet_id
				if petid_key in dict:
					if dhpp_due_date == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Can L")
					else:
						pass
				else:
					dict[petid_key] = ['Can L']
			date_bordetella=Vaccination.objects.filter(due_date_bordetella=remindar_date)
			for dapv in date_bordetella:
				due_bordetella=dapv.due_date_bordetella
				petid_key=dapv.pet.pet_id
				if petid_key in dict:
					if due_bordetella == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Bordetella")
					else:
						pass
				else:
					dict[petid_key] = ['Bordetella']

			date_lyme=Vaccination.objects.filter(due_date_lyme=remindar_date)
			for dahpp in date_lyme:
				due_lyme=dahpp.due_date_lyme
				petid_key=dahpp.pet.pet_id
				if petid_key in dict:
					if due_lyme == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Lyme")
					else:
						pass
				else:
					dict[petid_key] = ['Lyme']

			date_corona=Vaccination.objects.filter(due_date_corona=remindar_date)
			for da2pp in date_corona:
				due_corona=da2pp.due_date_corona
				petid_key=da2pp.pet.pet_id
				if petid_key in dict:
					if due_corona == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Corona")
					else:
						pass
				else:
					dict[petid_key] = ['Corona']

			date_giardia=Vaccination.objects.filter(due_date_giardia=remindar_date)
			for da2ppc in date_giardia:
				due_giardia=da2ppc.due_date_giardia
				petid_key=da2ppc.pet.pet_id
				if petid_key in dict:
					if due_giardia == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Giardia")
					else:
						pass
				else:
					dict[petid_key] = ['Giardia']

			date_leptospirosis=Vaccination.objects.filter(due_date_leptospirosis=remindar_date)
			for da2ppvl2 in date_leptospirosis:
				due_leptospirosis=da2ppvl2.due_date_leptospirosis
				petid_key=da2ppvl2.pet.pet_id
				if petid_key in dict:
					if due_leptospirosis == remindar_date:
						x=dict.get(petid_key,"")
						x.append("Leptospirosis")
					else:
						pass
				else:
					dict[petid_key] = ['Leptospirosis']
			dict_keys=dict.keys()
			for item in dict_keys:
				print(item,'hfajkshfkjahfkjahdfkjahskjfhasjkh')
				doctor=DoctorViewLog.objects.filter(pet_id__pet_id=item).last().doc_pk.Name_of_doctor
				hospital_name=DoctorViewLog.objects.filter(pet_id__pet_id=item).last().doc_pk.Hospital
				pet=Pet.objects.get(pet_id=item)
				if Vccination_Remainder.objects.filter(pet_id=pet,remiander_date=remindar_date,date=today_date).exists():
					pass
				else:
					vaccination_remainder=Vccination_Remainder()
					vaccinations=dict.get(item,"")

					customer_obj=pet.customer_id
					vaccination_remainder.pet=pet
					vaccination_remainder.customer=customer_obj
					vaccinations =list(dict.fromkeys(vaccinations))
					vaccination_remainder.vacanation_list=vaccinations
					vaccination_remainder.doctor=doctor
					vaccination_remainder.remiander_date=remindar_date
					vaccination_remainder.hospital=hospital_name
					vaccination_remainder.save()
			#showing vacanation list_patient
			vacanation_list_rem=Vccination_Remainder.objects.filter(date=today_date,remiander_date=remindar_date)

			return render(request,'admin/vaccination.html',{'vacanation_list_rem':vacanation_list_rem,'remindar_date':remindar_date,'generated_day':'on_day'})


def vaccination_reminder_sms(request):
	if request.method == "POST":
		if 'before_two' in request.POST:
			remiander_days=2
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=remiander_days)
			sms_list=Vccination_Remainder.objects.filter(remiander_date=remindar_date).all()
			print(sms_list)
			if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
			getattr(ssl, '_create_unverified_context', None)):
				ssl._create_default_https_context = ssl._create_unverified_context
				for i in sms_list:
					msg ='''Dear proud pet owner,

					'''+'Your pet'+' '+str(i.pet.name).upper()+' '+'is due for Vaccination'+' '+str(i.vacanation_list) +' '+'on'+' '+str(remindar_date)+' '+'at'+' '+ i.hospital.upper()+'. '+'Please consult'+' '+str(i.doctor).upper()+'\n'+'Regards,'+'\n'+'Aodh Petcare.'
					authkey = "334231AXCttMDRD5efc1d91P1" # Your authentication key.

					mobiles = i.customer.mobile # Multiple mobiles numbers separated by comma.
					print(mobiles,'3333333333333333333333333333333333333')
					message = msg # Your message to send.

					sender = "AODHPC" # Sender ID,While using route4 sender id should be 6 characters long.

					route = "4" # Define route

					# Prepare you post parameters
					values = {
							'authkey' : authkey,
							'mobiles' : mobiles,
							'message' : message,
							'sender' : sender,
							'route' : route
							}


					url = "http://api.msg91.com/api/sendhttp.php" # API URL

					postdata = urllib.parse.urlencode(values).encode("utf-8") # URL encoding the data here.

					req = urllib2.Request(url, postdata)

					response = urllib.request.urlopen(req)

					output = response.read() # Get Response


		elif 'before_one' in request.POST:
			remiander_days=1
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=remiander_days)
			sms_list=Vccination_Remainder.objects.filter(remiander_date=remindar_date)
			if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
			getattr(ssl, '_create_unverified_context', None)):
				ssl._create_default_https_context = ssl._create_unverified_context
				for i in sms_list:
					print(i.doctor)
					msg ='''Dear proud pet owner,

					'''+'Your pet'+' '+str(i.pet.name).upper()+' '+'is due for Vaccination'+' '+str(i.vacanation_list) +' '+'on'+' '+str(remindar_date)+' '+'at'+' '+ i.hospital.upper()+'. '+'Please consult'+' '+str(i.doctor).upper()+'\n'+'Regards,'+'\n'+'Aodh Petcare.'
					authkey = "334231AXCttMDRD5efc1d91P1" # Your authentication key.

					mobiles = i.customer.mobile # Multiple mobiles numbers separated by comma.

					message = msg # Your message to send.

					sender = "AODHPC" # Sender ID,While using route4 sender id should be 6 characters long.

					route = "4" # Define route

					# Prepare you post parameters
					values = {
							'authkey' : authkey,
							'mobiles' : mobiles,
							'message' : message,
							'sender' : sender,
							'route' : route
							}


					url = "http://api.msg91.com/api/sendhttp.php" # API URL

					postdata = urllib.parse.urlencode(values).encode("utf-8") # URL encoding the data here.

					req = urllib2.Request(url, postdata)

					response = urllib.request.urlopen(req)

					output = response.read() # Get Response

		elif 'on_day' in request.POST:

			today_date=date.today()
			remindar_date = date.today()
			sms_list=Vccination_Remainder.objects.filter(remiander_date=remindar_date)
			if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
			getattr(ssl, '_create_unverified_context', None)):
				ssl._create_default_https_context = ssl._create_unverified_context
				for i in sms_list:
					msg ='''Dear proud pet owner,

					'''+'Your pet'+' '+str(i.pet.name).upper()+' '+'is due for Vaccination'+' '+str(i.vacanation_list) +' '+'TODAY'+' '+'at'+' '+ i.hospital.upper()+'. '+'Please consult'+' '+str(i.doctor).upper()+'\n'+'Regards,'+'\n'+'Aodh Petcare.'
					authkey = "334231AXCttMDRD5efc1d91P1" # Your authentication key.

					mobiles = i.customer.mobile # Multiple mobiles numbers separated by comma.

					message = msg # Your message to send.

					sender = "AODHPC" # Sender ID,While using route4 sender id should be 6 characters long.

					route = "4" # Define route

					# Prepare you post parameters
					values = {
							'authkey' : authkey,
							'mobiles' : mobiles,
							'message' : message,
							'sender' : sender,
							'route' : route
							}


					url = "http://api.msg91.com/api/sendhttp.php" # API URL

					postdata = urllib.parse.urlencode(values).encode("utf-8") # URL encoding the data here.

					req = urllib2.Request(url, postdata)

					response = urllib.request.urlopen(req)

					output = response.read() # Get Response

	return HttpResponse('Messages has been sent successfully')

def deworming_remainder(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render(request,'admin/deworming.html')
		else:
			return redirect('admin_home')
	if request.method =="POST":
		if '2_days' in request.POST:
			remiander_days=2
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=remiander_days)
			deworming_qs=Deworming.objects.filter(due_date=remindar_date,)
			for i in deworming_qs:
				doctor=DoctorViewLog.objects.get(purpose_id=i.purpose_id)
				pet=doctor.pet_id
				deworming_remainder=deworming_Remainder()
				if deworming_Remainder.objects.filter(pet_id=pet,remiander_date=remindar_date,date=today_date).exists():
					pass
				else:
					deworming_remainder.doctor=doctor.doc_pk.Name_of_doctor
					deworming_remainder.remiander_date=remindar_date
					deworming_remainder.hospital=doctor.doc_pk.Hospital
					customer_obj=doctor.customer_id
					deworming_remainder.pet_id=pet
					deworming_remainder.customer=customer_obj
					deworming_remainder.save()
			return render(request,'admin/deworming.html',{'deworming_list_rem':deworming_qs,'remindar_date':remindar_date,'generated_day':'before_two','today_date':today_date})
		elif '1_day' in request.POST:
			remiander_days=1
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=remiander_days)
			deworming_qs=Deworming.objects.filter(due_date=remindar_date)
			for i in deworming_qs:
				doctor=DoctorViewLog.objects.get(purpose_id=i.purpose_id)
				pet=doctor.pet_id
				deworming_remainder=deworming_Remainder()
				if deworming_Remainder.objects.filter(pet_id=pet,remiander_date=remindar_date,date=today_date).exists():
					pass
				else:
					deworming_remainder.doctor=doctor.doc_pk.Name_of_doctor
					deworming_remainder.remiander_date=remindar_date
					deworming_remainder.hospital=doctor.doc_pk.Hospital
					customer_obj=doctor.customer_id
					deworming_remainder.pet_id=pet
					deworming_remainder.customer=customer_obj
					deworming_remainder.save()

			return render(request,'admin/deworming.html',{'deworming_list_rem':deworming_qs,'remindar_date':remindar_date,'generated_day':'before_one','today_date':today_date})
		elif 'on_day' in request.POST:
			today_date=date.today()
			deworming_qs=Deworming.objects.filter(due_date=today_date)
			for i in deworming_qs:
				doctor=DoctorViewLog.objects.get(purpose_id=i.purpose_id)
				pet=doctor.pet_id
				deworming_remainder=deworming_Remainder()
				if deworming_Remainder.objects.filter(pet_id=pet,remiander_date=today_date,date=today_date).exists():
					pass
				else:
					deworming_remainder.doctor=doctor.doc_pk.Name_of_doctor
					deworming_remainder.remiander_date=today_date
					deworming_remainder.hospital=doctor.doc_pk.Hospital
					customer_obj=doctor.customer_id
					deworming_remainder.pet_id=pet
					deworming_remainder.customer=customer_obj
					deworming_remainder.save()

			return render(request,'admin/deworming.html',{'deworming_list_rem':deworming_qs,'remindar_date':today_date,'generated_day':'on_day','today_date':today_date})


def deworming_reminnder_sms(request):
	if request.method =="POST":
		if 'before_two' in request.POST:
			remiander_days=2
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=remiander_days)
			deworming_list_rem=deworming_Remainder.objects.filter(remiander_date=remindar_date)
			sms_list=deworming_Remainder.objects.filter(remiander_date=remindar_date)
			if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
			getattr(ssl, '_create_unverified_context', None)):
				ssl._create_default_https_context = ssl._create_unverified_context
				for i in sms_list:

					msg ='''Dear proud pet owner,

					'''+'Your pet'+' '+str(i.pet_id.name)+' '+'is due for Deworming'+' '+'on'+' '+str(i.remiander_date)+' '+'at'+' '+ i.hospital.upper()+'. '+'Please consult'+' '+i.doctor.upper()+'\n'+'Regards,'+'\n'+'Aodh Petcare.'

					authkey = "334231AXCttMDRD5efc1d91P1" # Your authentication key.

					mobiles = i.customer.mobile # Multiple mobiles numbers separated by comma.

					message = msg # Your message to send.

					sender = "AODHPC" # Sender ID,While using route4 sender id should be 6 characters long.

					route = "4" # Define route

					# Prepare you post parameters
					values = {
					          'authkey' : authkey,
					          'mobiles' : mobiles,
					          'message' : message,
					          'sender' : sender,
					          'route' : route
					          }


					url = "http://api.msg91.com/api/sendhttp.php" # API URL

					postdata = urllib.parse.urlencode(values).encode("utf-8") # URL encoding the data here.

					req = urllib2.Request(url, postdata)

					response = urllib.request.urlopen(req)

					output = response.read() # Get Response
		elif 'before_one' in request.POST:
			remiander_days=1
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=remiander_days)
			deworming_list_rem=deworming_Remainder.objects.filter(remiander_date=remindar_date)
			sms_list=deworming_Remainder.objects.filter(remiander_date=remindar_date)
			if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
			getattr(ssl, '_create_unverified_context', None)):
				ssl._create_default_https_context = ssl._create_unverified_context
				for i in sms_list:

					msg ='''Dear proud pet owner,

					'''+'Your pet'+' '+str(i.pet_id.name)+' '+'is due for Deworming'+' '+'on'+' '+str(i.remiander_date)+' '+'at'+' '+ i.hospital.upper()+'. '+'Please consult'+' '+i.doctor.upper()+'\n'+'Regards,'+'\n'+'Aodh Petcare.'

					authkey = "334231AXCttMDRD5efc1d91P1" # Your authentication key.

					mobiles = i.customer.mobile # Multiple mobiles numbers separated by comma.

					message = msg # Your message to send.

					sender = "AODHPC" # Sender ID,While using route4 sender id should be 6 characters long.

					route = "4" # Define route

					# Prepare you post parameters
					values = {
					          'authkey' : authkey,
					          'mobiles' : mobiles,
					          'message' : message,
					          'sender' : sender,
					          'route' : route
					          }


					url = "http://api.msg91.com/api/sendhttp.php" # API URL

					postdata = urllib.parse.urlencode(values).encode("utf-8") # URL encoding the data here.

					req = urllib2.Request(url, postdata)

					response = urllib.request.urlopen(req)

					output = response.read() # Get Response

		elif 'on_day' in request.POST:
			today_date=date.today()
			remindar_date = date.today()
			deworming_list_rem=deworming_Remainder.objects.filter(remiander_date=remindar_date)
			sms_list=deworming_Remainder.objects.filter(remiander_date=remindar_date)
			if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
			getattr(ssl, '_create_unverified_context', None)):
				ssl._create_default_https_context = ssl._create_unverified_context
				for i in sms_list:

					msg ='''Dear proud pet owner,

					'''+'Your pet'+' '+str(i.pet_id.name)+' '+'is due for Deworming'+' '+'TODAY'+' '+'at'+' '+ i.hospital.upper()+'. '+'Please consult'+' '+i.doctor.upper()+'\n'+'Regards,'+'\n'+'Aodh Petcare.'

					authkey = "334231AXCttMDRD5efc1d91P1" # Your authentication key.

					mobiles = i.customer.mobile # Multiple mobiles numbers separated by comma.

					message = msg # Your message to send.

					sender = "AODHPC" # Sender ID,While using route4 sender id should be 6 characters long.

					route = "4" # Define route

					# Prepare you post parameters
					values = {
					          'authkey' : authkey,
					          'mobiles' : mobiles,
					          'message' : message,
					          'sender' : sender,
					          'route' : route
					          }


					url = "http://api.msg91.com/api/sendhttp.php" # API URL

					postdata = urllib.parse.urlencode(values).encode("utf-8") # URL encoding the data here.

					req = urllib2.Request(url, postdata)

					response = urllib.request.urlopen(req)

					output = response.read() # Get Response

	return HttpResponse('Messages has been sent successfully')

def follow_up_date_reminder(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render(request,'admin/followup_date_reminder.html')
		else:
			return redirect('admin_home')
	if request.method =="POST":
		if '2_days' in request.POST:
			print('2')
			reminding_days=2
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=reminding_days)
			print(remindar_date,'o')
			generate_followup_date_list=Prescription.objects.filter(followup_date=remindar_date)
			for i in generate_followup_date_list:
				doctor=DoctorViewLog.objects.get(purpose_id=i.purpose_id)
				pet=doctor.pet_id
				if followup_Remainder.objects.filter(pet_id=pet,remiander_date=remindar_date,date=today_date).exists():
					pass
				else:
					follow_up_save=followup_Remainder()
					follow_up_save.doctor=doctor.doc_pk.Name_of_doctor
					follow_up_save.customer=doctor.customer_id
					follow_up_save.pet_id=doctor.pet_id
					follow_up_save.hospital=doctor.doc_pk.Hospital
					follow_up_save.remiander_date=remindar_date
					follow_up_save.save()

			return render(request,'admin/followup_date_reminder.html',{'generate_followup_date_list':generate_followup_date_list,'today_date':today_date,'generated_day':'two_day'})

		elif '1_day' in request.POST:
			reminding_days=1
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=reminding_days)
			print(remindar_date,'o')
			generate_followup_date_list=Prescription.objects.filter(followup_date=remindar_date)
			for i in generate_followup_date_list:
				follow_up_save=followup_Remainder()
				doctor=DoctorViewLog.objects.get(purpose_id=i.purpose_id)
				pet=doctor.pet_id
				if followup_Remainder.objects.filter(pet_id=pet,remiander_date=remindar_date,date=today_date).exists():
					pass
				else:
					follow_up_save.doctor=doctor.doc_pk.Name_of_doctor
					follow_up_save.customer=doctor.customer_id
					follow_up_save.pet_id=doctor.pet_id
					follow_up_save.hospital=doctor.doc_pk.Hospital
					follow_up_save.remiander_date=remindar_date
					follow_up_save.save()

			return render(request,'admin/followup_date_reminder.html',{'generate_followup_date_list':generate_followup_date_list,'today_date':today_date,'generated_day':'before_one'})

		elif 'on_day' in request.POST:
			today_date=date.today()
			remindar_date = date.today()
			print(remindar_date,'o')
			generate_followup_date_list=Prescription.objects.filter(followup_date=remindar_date)
			print(generate_followup_date_list,'p')

			for i in generate_followup_date_list:
				follow_up_save=followup_Remainder()
				doctor=DoctorViewLog.objects.get(purpose_id=i.purpose_id)
				pet=doctor.pet_id
				if followup_Remainder.objects.filter(pet_id=pet,remiander_date=remindar_date,date=today_date).exists():
					pass
				else:
					follow_up_save.doctor=doctor.doc_pk.Name_of_doctor
					follow_up_save.customer=doctor.customer_id
					follow_up_save.pet_id=doctor.pet_id
					follow_up_save.hospital=doctor.doc_pk.Hospital
					follow_up_save.remiander_date=remindar_date
					follow_up_save.save()


			return render(request,'admin/followup_date_reminder.html',{'generate_followup_date_list':generate_followup_date_list,'today_date':today_date,'generated_day':'on_day'})


def followup_date_send_sms(request):
	if request.method =="POST":
		if 'before_one' in request.POST:
			print('before_one','2')
			reminding_days=1
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=reminding_days)
			generate_followup_date_list=Prescription.objects.filter(followup_date=remindar_date)
			for i in generate_followup_date_list :
				customer_mobile=i.purpose_id.pet_id.customer_id.mobile
				if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
				getattr(ssl, '_create_unverified_context', None)):
					ssl._create_default_https_context = ssl._create_unverified_context
					doctor=DoctorViewLog.objects.get(purpose_id=i.purpose_id)

					msg ='''Dear proud pet owner,

						Your next follow-up visit date is on '''+str(i.followup_date)+". Please consult"+" "+doctor.doc_pk.Name_of_doctor.upper() +". You can book an appointment at https://aodhpet.com/registration/"+str(doctor.doc_pk.id)+"/" +"\n"+"\n"+"Regards,"+"\n"+"Aodh Petcare"



					authkey = "334231AXCttMDRD5efc1d91P1" # Your authentication key.

					mobiles = customer_mobile # Multiple mobiles numbers separated by comma.

					message = msg # Your message to send.

					sender = "AODHPC" # Sender ID,While using route4 sender id should be 6 characters long.

					route = "4" # Define route

					# Prepare you post parameters
					values = {
							'authkey' : authkey,
							'mobiles' : mobiles,
							'message' : message,
							'sender' : sender,
							'route' : route
							}


					url = "http://api.msg91.com/api/sendhttp.php" # API URL

					postdata = urllib.parse.urlencode(values).encode("utf-8") # URL encoding the data here.

					req = urllib2.Request(url, postdata)

					response = urllib.request.urlopen(req)

					output = response.read() # Get Response
					print(output)
		elif 'on_day' in request.POST:
			print('on_day','2')
			remindar_date = date.today()
			print(remindar_date,'o')
			generate_followup_date_list=Prescription.objects.filter(followup_date=remindar_date)
			print(generate_followup_date_list,'p')
			for i in generate_followup_date_list :
				customer_mobile=i.purpose_id.pet_id.customer_id.mobile
				if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
				getattr(ssl, '_create_unverified_context', None)):
					ssl._create_default_https_context = ssl._create_unverified_context
					doctor=DoctorViewLog.objects.get(purpose_id=i.purpose_id)

					msg ='''Dear proud pet owner,

						Your next follow-up visit date is on '''+str(i.followup_date)+". Please consult"+" "+doctor.doc_pk.Name_of_doctor.upper() +". You can book an appointment at https://aodhpet.com/registration/"+str(doctor.doc_pk.id)+"/" +"\n"+"\n"+"Regards,"+"\n"+"Aodh Petcare"



					authkey = "334231AXCttMDRD5efc1d91P1" # Your authentication key.

					mobiles = customer_mobile # Multiple mobiles numbers separated by comma.

					message = msg # Your message to send.

					sender = "AODHPC" # Sender ID,While using route4 sender id should be 6 characters long.

					route = "4" # Define route

					# Prepare you post parameters
					values = {
							'authkey' : authkey,
							'mobiles' : mobiles,
							'message' : message,
							'sender' : sender,
							'route' : route
							}


					url = "http://api.msg91.com/api/sendhttp.php" # API URL

					postdata = urllib.parse.urlencode(values).encode("utf-8") # URL encoding the data here.

					req = urllib2.Request(url, postdata)

					response = urllib.request.urlopen(req)

					output = response.read() # Get Response

		elif 'two_day' in request.POST:
			print('two_day','2')
			reminding_days=2
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=reminding_days)
			generate_followup_date_list=Prescription.objects.filter(followup_date=remindar_date)
			for i in generate_followup_date_list :
				doctor=DoctorViewLog.objects.get(purpose_id=i.purpose_id)
				customer_mobile=doctor.customer_id.mobile

				if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
				getattr(ssl, '_create_unverified_context', None)):
					ssl._create_default_https_context = ssl._create_unverified_context

					msg ='''Dear proud pet owner,

						Your next follow-up visit date is on '''+str(i.followup_date)+". Please consult"+" "+doctor.doc_pk.Name_of_doctor.upper() +". You can book an appointment at https://aodhpet.com/registration/"+str(doctor.doc_pk.id)+"/" +"\n"+"\n"+"Regards,Aodh Petcare"



					authkey = "334231AXCttMDRD5efc1d91P1" # Your authentication key.

					mobiles = customer_mobile # Multiple mobiles numbers separated by comma.

					message = msg # Your message to send.

					sender = "AODHPC" # Sender ID,While using route4 sender id should be 6 characters long.

					route = "4" # Define route

					# Prepare you post parameters
					values = {
							'authkey' : authkey,
							'mobiles' : mobiles,
							'message' : message,
							'sender' : sender,
							'route' : route
							}


					url = "http://api.msg91.com/api/sendhttp.php" # API URL

					postdata = urllib.parse.urlencode(values).encode("utf-8") # URL encoding the data here.

					req = urllib2.Request(url, postdata)

					response = urllib.request.urlopen(req)

					output = response.read() # Get Response

	return HttpResponse('Messages has been sent successfully')

def follow_up_date_list_view(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render(request,'admin/follow_up_date_list_view.html')
		else:
			return redirect('admin_home')
	if request.method=="POST":
		search_date=request.POST.get('search_date')
		follwup_date_list=followup_Remainder.objects.filter(date=search_date)
		return render(request,'admin/follow_up_date_list_view.html',{'follwup_date_list':follwup_date_list})


def deworming_reminder_list_view(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render(request,'admin/deworming_reminder_list_view.html')
		else:
			return redirect('admin_home')
	if request.method=="POST":
		search_date=request.POST.get('search_date')
		dewormin_date_list=deworming_Remainder.objects.filter(date=search_date)

		return render(request,'admin/deworming_reminder_list_view.html',{'dewormin_date_list':dewormin_date_list})

def vaccination_reminder_list_view(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			return render(request,'admin/vaccination_reminder_list_view.html')
		else:
			return redirect('admin_home')
	if request.method=="POST":
		search_date=request.POST.get('search_date')
		vaccination_date_list=Vccination_Remainder.objects.filter(date=search_date)

		return render(request,'admin/vaccination_reminder_list_view.html',{'vaccination_date_list':vaccination_date_list})


def petimageupload(request):
	if request.method=='POST':
		customer_id=request.POST.get('customer_id')
		pet_id=request.POST.get('petid')
		pet=Pet.objects.get(pet_id=pet_id)

		if petimage.objects.filter(customer_id=customer_id,pet_id=pet).exists():
			petimage.objects.filter(customer_id=customer_id,pet_id=pet).delete()

			petimg=petimage()
			petimg.pet_image= request.FILES.get('file')
			petimg.customer_id=customer_id
			petimg.pet_id=pet
			petimg.save()
		else:
			petimg=petimage()
			petimg.pet_image= request.FILES.get('file')
			petimg.customer_id=customer_id
			petimg.pet_id=pet
			petimg.save()
	return redirect('mypets')

def mybookings(request,customer_id):
		current=DoctorViewLog.objects.filter(customer_id__customer_id=customer_id,status="A").all().order_by('-date')
		completed=DoctorViewLog.objects.filter(customer_id__customer_id=customer_id,status="C").all().order_by('-date')
		cancelled=DoctorViewLog.objects.filter(customer_id__customer_id=customer_id,status="CN").all().order_by('-date')
		expired=DoctorViewLog.objects.filter(customer_id__customer_id=customer_id,status="EX").all().order_by('-date')
		if request.method=="POST":
			cancelbook=cancel_booking()
			x=request.POST.get('purpose')
			cancel_appointment=PurposeAndDiet.objects.filter(id=x)
			purpose=PurposeAndDiet.objects.filter(id=x).last()
			cancelbook.purpose_id=purpose
			cancelbook.customer_id=customer_id
			cancelbook.pet_id=purpose.pet_id
			doctor=request.POST.get('doctor')
			cancelbook.doctor=Doctor.objects.get(id=doctor)
			cancelbook.save()
			# cancel=DoctorLogList.objects.filter(purpose_id__id=x).delete()
			Log.objects.filter(purpose_id__id=x).update(status='CN')
			DoctorViewLog.objects.filter(purpose_id__id=x).update(status='CN')
			cancel_appointment=PurposeAndDiet.objects.filter(id=x)

			return render(request,'customer/my_bookings_new.html',{'current':current,'completed':completed,
			'customer_id':customer_id,'cancelled':cancelled})
		if request.method == "GET":
			if 'customer_id' in request.session:
				session_id=request.session['customer_id']
				if session_id == customer_id :
					return render(request,'customer/my_bookings_new.html',{'current':current,'completed':completed,
					'customer_id':customer_id,'cancelled':cancelled,'expired':expired,})
				else:
					return redirect('customer_login_home')
			else:
					return redirect('customer_login_home')

def mybooking_summary(request,customer_id,purpose_id):


	if request.method == "GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id :
				purpose=Log.objects.filter(purpose_id__id=purpose_id).last()
				return render(request,'customer/mybooking_summary.html',
				{'purpose':purpose,'customer_id':customer_id})
			else:
				return redirect('customer_login_home')
		else:
				return redirect('customer_login_home')


def customer_home_page(request,customer_id,doc_pk=None):
	try:
		check_complete_reg=Customer.objects.get(customer_id=customer_id)
		if request.method =="GET":
			customer_id=customer_id
			if 'customer_id' in request.session:
				print(customer_id,'get')
				session_id=request.session['customer_id']
				if session_id == customer_id :
					return render(request,'customer/home_page_try.html',
					{'customer_id':customer_id,'check_complete_reg':check_complete_reg,'doc_pk':doc_pk})
				else:
					return redirect ('customer_login_home')
			else:
				return redirect('customer_login_home')
	except Customer.DoesNotExist:
		return redirect('customer_login_home')



def book_consultation(request,customer_id,doc_pk=None):
	if doc_pk == None:
		if Pet.objects.filter(customer_id__customer_id=customer_id).last() is not None:
			return redirect('pet_list')
		else:
			return redirect('petdetails',doc_pk=doc_pk)
	elif doc_pk != None:
		if Pet.objects.filter(customer_id__customer_id=customer_id).last() is not None:
			return redirect('pet_list')
		else:
			return redirect('petdetails',doc_pk=doc_pk)


def doc_list(request,doc_pk,check_visit):

	url_parameters=request.session['pass_dict_session']
	customer_pk=url_parameters['customer_pk']
	consulted_pet=url_parameters['consulted_pet']

	purpose_id=url_parameters['purpose_id']
	print(customer_pk,consulted_pet,purpose_id,'sess,doc')
	#pet age conversion for sidebar
	customer_obj=Customer.objects.get(id=customer_pk)
	customer_id=Customer.objects.get(id=customer_pk).customer_id

	if request.method == "GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id :
				online_doc=Doctor.objects.filter(Q(mode='online') | Q(mode='both'))
				offline_doc=Doctor.objects.filter(Q(mode='offline') | Q(mode='both'))
				if doc_pk == "None" and check_visit=="None":
					pass
				else:
					request.session['pass_dict_session']['doctor_pk']=doc_pk
					request.session['visit_check']=check_visit
					return redirect('time_slot')

				return render(request,'customer/select_visit_type.html',{'offline_doc':offline_doc,'online_doc':online_doc,'doc_pk':doc_pk,'check_visit':check_visit,
				'customer_id':customer_id,'pet_id':consulted_pet,'purpose_id':purpose_id})
			else:
				return redirect ('customer_login_home')
		else:
			return redirect('customer_login_home')
def terms_conditions(request):
	return render(request,'customer/terms_and_conditions.html')

def time_slot(request):
	#getting parameters from session
	check_visit=request.session['visit_check']
	url_parameters=request.session['pass_dict_session']
	customer_pk=url_parameters['customer_pk']
	consulted_pet=url_parameters['consulted_pet']
	doc_pk=url_parameters['doctor_pk']
	purpose_id=url_parameters['purpose_id']

	customer_obj=Customer.objects.get(id=customer_pk)
	customer_id=customer_obj.customer_id

	if request.method == "GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id :
				slelcted_date=datetime.datetime.today().strftime('%Y-%m-%d')
				return render(request,'customer/time_slot.html',{'pet_id':consulted_pet,'purpose_id':purpose_id,'doc_pk':doc_pk,'slelcted_date':slelcted_date,
					'customer_id':customer_id})
			else:
				return redirect ('customer_login_home')
		else:
			return redirect('customer_login_home')
	if request.method=="POST":

		url_date=request.POST.get('date')


		return redirect('booking_summary',booking_date=url_date)



def gallery_pet_image(request):
	customer_id=request.POST.get('customer_id_sec')
	if request.method=='POST':
		gal=gallery_image()
		img=request.FILES.get('gallery_image')
		gal.gal_img=img
		gal.customer_id=request.POST.get('customer_id_sec')
		gal.save()

	return redirect('customer_home_page',customer_id=customer_id)

def gallery(request,customer_id):
	pets=Pet.objects.filter(customer_id__customer_id=customer_id).all()
	pets=pet_age_converter(pets)

	try:
		petimg=petimage.objects.filter(customer_id=customer_id).all()
		petlist=[]
		for l in petimg:
			pet_id_img=l.pet_id.pet_id
			petlist.append(pet_id_img)
	except:
		pass

	if request.method == "GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id :
				images=gallery_image.objects.filter(customer_id=customer_id)
				return render(request,'customer/testgallery.html',{'images':images,'media_url':settings.MEDIA_URL,'customer_id':customer_id,'pets':pets,'petimg':petimg,'petlist':petlist})
			else:
				return redirect ('customer_login_home')
		else:
			return redirect('customer_login_home')
	if request.method=="POST":
		x=request.POST.get('img')
		obj=gallery_image.objects.filter(id=x).delete()
		return redirect('gallery',customer_id=customer_id)






authbasic = 'Basic '
authbasicconv = base64.b64encode(
    (settings.ENABLEX_APP_ID + ':' + settings.ENABLEX_APP_KEY).encode("utf-8"))
authx = (authbasic + authbasicconv.decode())

headers = {"Content-Type": "application/json",
           'Authorization': 'Basic %s' % authbasicconv.decode()}
random_name = str(random.randint(100000, 999999))
payload = {
    'name': 'Sample Room: ' + random_name,
    'owner_ref': random_name,
    'settings': {
        'description': '',
        'quality': 'SD',
        'mode': 'group',
        'participants': '2',
        'duration': '10',
        'scheduled': False,
        'auto_recording': False,
        'active_talker': True,
        'wait_moderator': False,
        'adhoc': True,
    },
    'sip': {
        'enabled': False,
    }
}
encode_payload = json.JSONEncoder().encode(payload)



def client(request):
    template = loader.get_template('login/login.html')
    context = {
        'msg': 'Welcome to login page',
    }
    return HttpResponse(template.render(context, request))


def video_thankyou(request, customerid=None, doctorid=None):
	return render (request,'customer/videothankyou.html',{'customerid':customerid,'doctorid':doctorid})


def confo(request, roomid, usertype, userref, customerid=None, doctorid=None):
    template = loader.get_template('confo/index.html')
    context = {
        'roomId': roomid,
        'user_ref': userref,
        'usertype': usertype,
      	'customerid': customerid,
      	'doctorid': doctorid,
    }
    return HttpResponse(template.render(context, request))

def video_consultation(request,customer_id):
	pets=Pet.objects.filter(customer_id__customer_id=customer_id).all()
	pets=pet_age_converter(pets)
	try:
		petimg=petimage.objects.filter(customer_id=customer_id).all()
		petlist=[]
		for l in petimg:
			pet_id_img=l.pet_id.pet_id
			petlist.append(pet_id_img)
	except:
		pass

	video_list=DoctorLogList.objects.filter(customer_id__customer_id=customer_id,mode='online')

	return render(request,'customer/video_consultation.html',{'video_list':video_list,'petimg':petimg,'media_url':settings.MEDIA_URL,'petlist':petlist,'pets':pets,'customer_id':customer_id})



import requests
import base64
import json
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from django.conf import settings
import random

def notifications(request,customer_id):
	if Vaccination.objects.filter(pet_id__customer_id__customer_id=customer_id):
		pass
	else:
		pass
	remiander_days=2
	last_dict={}
	dict={}
	vacanation_list=[]
	today_date=date.today()
	remindar_date = date.today() + timedelta(days=remiander_days)
	print(remindar_date)
	due_date_3_in_1_DAPV_qs=Vaccination.objects.filter(due_date_3_in_1_DAPV=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for r_q in due_date_3_in_1_DAPV_qs:
		rabies_due_date=r_q.due_date_3_in_1_DAPV
		petid_key=r_q.pet.pet_id
		if rabies_due_date == remindar_date:
			dict[petid_key] = ['3 in 1 DAPV']
		else:
			pass
	a_4_in_1_DHPP_qs=Vaccination.objects.filter(due_date_4_in_1_DHPP=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for d_q in a_4_in_1_DHPP_qs:
		distemper_due_date=d_q.due_date_4_in_1_DHPP
		petid_key=d_q.pet.pet_id
		if petid_key in dict:
			if distemper_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("4 in 1 DHPP")
			else:
				pass
		else:
			dict[petid_key] = ['4 in 1 DHPP']
	b_5_in_1_DA2PP_qs=Vaccination.objects.filter(due_date_5_in_1_DA2PP=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for h_q in b_5_in_1_DA2PP_qs:
		hepatitis_due_date=h_q.due_date_5_in_1_DA2PP
		petid_key=h_q.pet.pet_id
		if petid_key in dict:
			if hepatitis_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("5 in 1 DA2PP")
			else:
				pass
		else:
			dict[petid_key] = ['5 in 1 DA2PP']
	c_6_in_1_DA2PPC_qs=Vaccination.objects.filter(due_date_6_in_1_DA2PPC=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for p_q in c_6_in_1_DA2PPC_qs:
		parovirus_due_date=p_q.due_date_6_in_1_DA2PPC
		petid_key=p_q.pet.pet_id
		if petid_key in dict:
			if parovirus_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("6 in 1 DA2PPC")
			else:
				pass
		else:
			if parovirus_due_date == remindar_date:
				dict[petid_key] = ['6 in 1 DA2PPC']
			else:
				pass
	d_7_in_1_DA2PPVL2_qs=Vaccination.objects.filter(due_date_7_in_1_DA2PPVL2=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for para_q in d_7_in_1_DA2PPVL2_qs:
		parainfluenza_due_date=para_q.due_date_7_in_1_DA2PPVL2
		petid_key=para_q.pet.pet_id
		if petid_key in dict:
			if parainfluenza_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("7 in 1 DA2PPVL2")
			else:
				pass
		else:
			dict[petid_key] = ['7 in 1 DA2PPVL2']
	date_rabies_qs=Vaccination.objects.filter(due_date_rabies=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for b_q in date_rabies_qs:
		bordetella_due_date=b_q.due_date_rabies
		petid_key=b_q.pet.pet_id
		if petid_key in dict:
			if bordetella_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("rabies")
			else:
				pass
		else:
			dict[petid_key] = ['date_rabies']
	distemper_qs=Vaccination.objects.filter(due_date_distemper=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for l_q in distemper_qs:
		leptospirosis_due_date=l_q.due_date_distemper
		petid_key=l_q.pet.pet_id
		if petid_key in dict:
			if leptospirosis_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("distemper")
			else:
				pass
		else:
			dict[petid_key] = ['distemper']
	date_CAV_1_qs=Vaccination.objects.filter(due_date_CAV_1=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for ly_q in date_CAV_1_qs:
		lymedisease_due_date=ly_q.due_date_CAV_1
		petid_key=ly_q.pet.pet_id
		if petid_key in dict:
			if lymedisease_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("CAV 1")
			else:
				pass
		else:
			dict[petid_key] = ['CAV 1']
	parovirus_qs=Vaccination.objects.filter(due_date_parovirus=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for c_q in parovirus_qs:
		coronavirus_due_date=c_q.due_date_parovirus
		petid_key=c_q.pet.pet_id
		if petid_key in dict:
			if coronavirus_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("parovirus")
			else:
				pass
		else:
			dict[petid_key] = ['parovirus']
	parainfluenza_qs=Vaccination.objects.filter(due_date_parainfluenza=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for q_q in parainfluenza_qs:
		giardia_due_date=q_q.due_date_parainfluenza
		petid_key=q_q.pet.pet_id
		if petid_key in dict:
			if giardia_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("parainfluenza")
			else:
				pass
		else:
			dict[petid_key] = ['parainfluenza']
	bordetella_qs=Vaccination.objects.filter(due_date_bordetella=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for dh_q in bordetella_qs:
		dhpp_due_date=dh_q.due_date_bordetella
		petid_key=dh_q.pet.pet_id
		if petid_key in dict:
			if dhpp_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("bordetella")
			else:
				pass
		else:
			dict[petid_key] = ['bordetella']

	CAV_2_qs=Vaccination.objects.filter(due_date_CAV_2=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for dh_q in CAV_2_qs:
		dhpp_due_date=dh_q.due_date_CAV_2
		petid_key=dh_q.pet.pet_id
		if petid_key in dict:
			if dhpp_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("CAV 2")
			else:
				pass
		else:
			dict[petid_key] = ['CAV 2']
	lyme_qs=Vaccination.objects.filter(due_date_lyme=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for dapv in lyme_qs:
		dapv_due_date=dapv.due_date_lyme
		petid_key=dapv.pet.pet_id
		if petid_key in dict:
			if dapv_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("lyme")
			else:
				pass
		else:
			dict[petid_key] = ['lyme']

	corona_qs=Vaccination.objects.filter(due_date_corona=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for dahpp in corona_qs:
		dahpp_due_date=dahpp.due_date_corona
		petid_key=dahpp.pet.pet_id
		if petid_key in dict:
			if dahpp_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("corona")
			else:
				pass
		else:
			dict[petid_key] = ['corona']

	giardia_qs=Vaccination.objects.filter(due_date_giardia=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for da2pp in giardia_qs:
		da2pp_due_date=da2pp.due_date_giardia
		petid_key=da2pp.pet.pet_id
		if petid_key in dict:
			if da2pp_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("giardia")
			else:
				pass
		else:
			dict[petid_key] = ['giardia']

	Can_L_qs=Vaccination.objects.filter(due_date_Can_L=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for da2ppc in Can_L_qs:
		da2ppc_due_date=da2ppc.due_date_Can_L
		petid_key=da2ppc.pet.pet_id
		if petid_key in dict:
			if da2ppc_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("Can L")
			else:
				pass
		else:
			dict[petid_key] = ['Can L']

	leptospirosis_qs=Vaccination.objects.filter(due_date_leptospirosis=remindar_date,pet_id__customer_id__customer_id=customer_id)
	for da2ppc in leptospirosis_qs:
		da2ppc_due_date=da2ppc.due_date_leptospirosis
		petid_key=da2ppc.pet.pet_id
		if petid_key in dict:
			if da2ppc_due_date == remindar_date:
				x=dict.get(petid_key,"")
				x.append("leptospirosis")
			else:
				pass
		else:
			dict[petid_key] = ['leptospirosis']


	dict_keys=dict.keys()
	update=notification.objects.all()
	data=''
	for i in dict_keys:
			doctor=DoctorViewLog.objects.filter(pet_id__pet_id=i).last().doc_pk.Name_of_doctor
			hospital_name=DoctorViewLog.objects.filter(pet_id__pet_id=i).last().doc_pk.Hospital
			vaccination_remainder=Vccination_Remainder()
			vaccinations=dict.get(i,"")
			pet=Pet.objects.get(pet_id=i)
			pet_id=pet.name
			vaccinations=dict.get(i,"")
			vaccinations =list(dict.fromkeys(vaccinations))
			vaccinations=','.join(str(e) for e in vaccinations)

			data = ('Dear Customer,'+' '+'Your pet'+' '+str(pet_id)+' '+'is due for his/her Vaccination'+' '+str(vaccinations) +' '+'on'+' '+str(remindar_date)+'.'+' '+'Please visit Dr.'+' '+doctor+'at'+' '+ hospital_name+' '+'Hospital'+' ')


	return render(request,'customer/notification.html',{'update':update,'data':data})

def anti_dog_whistle(request):
	return render(request,'customer/Customer_anti_dog_whistle.html',{'media_url':settings.MEDIA_URL})




def ip(request):
	ips=get_client_ip(request)
	return render(request,'ip.html',{'ips':ips})


def onesignalid(request):
	if request.method=='POST':
		userId=request.POST.get('userId')

		customer_id=request.POST.get('customer_id')
		noti=notification()
		noti.customer_id=customer_id
		noti.palyerid=userId
		noti.save()

		data = {

	}
	return JsonResponse(data)

def webpush(request):
	remiander_days=2
	today_date=date.today()
	remindar_date = date.today() + timedelta(days=remiander_days)

	push_notification_list=Vccination_Remainder.objects.filter(remiander_date=remindar_date)
	playerid_list=notification.objects.all()


	for i in push_notification_list:

			data = ('Dear Customer,'+' '+'Your pet'+str(i.pet_id)+'is due for his/her Vaccination'+str(i.vacanation_list) +'on'+str(remindar_date)+'at'+' '+ i.hospital+' '+'doctor name :'+' '+i.doctor+'    ')

			print(data)
			print(i.customer_id)
			for z in playerid_list :
				if z.customer_id==i.customer_id:
					header = {"Content-Type": "application/json; charset=utf-8",
					          "Authorization": "Basic MzRhZmY2ZjYtNzk2ZC00MjUyLWJhZTAtZDQxODMyZTQ5MWQ5"}

					payload = {"app_id": "901212c5-efbc-496e-9354-857960f6b8d9",
					           "include_player_ids": [z.palyerid],
					           "contents": {"en": data}}

					req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))


	return HttpResponse('sucess')

# pet licencing views


def pet_licenseview(request, customer_id):
	pets=Pet.objects.filter(customer_id__customer_id=customer_id).all()
	pets=pet_age_converter(pets)
	try:
		petimg=petimage.objects.filter(customer_id=customer_id).all()
		petlist1=[]
		for l in petimg:
			pet_id_img=l.pet_id.pet_id
			petlist1.append(pet_id_img)
	except:
		pass
	if 'customer_id' in request.session:
		session_id = request.session['customer_id']
		if session_id == customer_id:
			pet_list = Pet.objects.filter(customer_id__customer_id=customer_id)
			pet_list=pet_age_converter(pet_list)
			return render(request, 'customer/pet_license_list.html', {'pet_list': pet_list, 'customer_id': customer_id,'petimg':petimg,'media_url':settings.MEDIA_URL,'petlist1':petlist1,'pets':pets})
		else:
			return redirect('customer_login_home')
	else:
		return redirect('customer_login_home')


def serial_verificetion(request, pet_id,customer_id):
	pets=Pet.objects.filter(customer_id__customer_id=customer_id).all()
	pets=pet_age_converter(pets)
	try:
		petimg=petimage.objects.filter(customer_id=customer_id).all()
		petlist=[]
		for l in petimg:
			pet_id_img=l.pet_id.pet_id
			petlist.append(pet_id_img)
	except:
		pass
	if request.method == 'GET':
		if 'customer_id' in request.session:
			return render(request, 'customer/serial_verificetion.html', {'pet_id': pet_id,'petimg':petimg,'media_url':settings.MEDIA_URL,'petlist':petlist,'pets':pets,'customer_id':customer_id})
		else:
			return redirect('customer_login_home')
	if request.method == 'POST' and request.FILES['myfile']:
		license_pet = License_Pet()
		pet_obj = Pet.objects.get(pet_id=pet_id)
		address = request.POST.get('address')
		pet = Pet.objects.filter(pet_id=pet_id).update(address=address)
		license_pet.pet_id = pet_obj
		filelist = request.FILES.getlist('myfile')
		license_pet.file1 = filelist[0]
		license_pet.file2 = filelist[1]
		license_pet.file3 = filelist[2]
		license_pet.file4 = filelist[3]
		license_pet.save()
		pet_id = pet_id
		return redirect('licence_payment', pet_id=pet_id,customer_id=customer_id)



def licence_payment(request, pet_id,customer_id):
	pets=Pet.objects.filter(customer_id__customer_id=customer_id).all()
	pets=pet_age_converter(pets)
	try:
		petimg=petimage.objects.filter(customer_id=customer_id).all()
		petlist=[]
		for l in petimg:
			pet_id_img=l.pet_id.pet_id
			petlist.append(pet_id_img)
	except:
		pass
	if 'customer_id' in request.session:
		customer_id = Pet.objects.get(pet_id=pet_id).customer_id
		licence_fee = 100
		sub_total = licence_fee+20
		sub_total_razor = sub_total*100
		DATA ={
			"amount": sub_total_razor,
			"currency": "INR",
			"payment_capture": '1',
			"notes" : {'Shipping address': 'hrllll, hyd'}
		}
		order = razorpay_client.order.create(data=DATA)
		order_id = order.get("id","")
		return render(request, 'customer/licence_payment.html', {'pet_id': pet_id, 'sub_total': sub_total, 'order_id': order_id, 'customer_id': customer_id.customer_id,'petimg':petimg,'media_url':settings.MEDIA_URL,'petlist':petlist,'pets':pets,'licence_fee':licence_fee})
	else:
		return redirect('customer_login_home')


@csrf_exempt
def licence_conform(request, pet_id,customer_id):
	pets=Pet.objects.filter(customer_id__customer_id=customer_id).all()
	pets=pet_age_converter(pets)
	try:
		petimg=petimage.objects.filter(customer_id=customer_id).all()
		petlist=[]
		for l in petimg:
			pet_id_img=l.pet_id.pet_id
			petlist.append(pet_id_img)
	except:
		pass
	razorpay_payment_id = request.POST.get('razorpay_payment_id')
	razorpay_order_id = request.POST.get('razorpay_order_id')
	razorpay_signature = request.POST.get('razorpay_signature')
	if razorpay_payment_id == None:
		return HttpResponse('<h1>Paymet_id not generated</h1>')
	else:
		razorpay_payment_status_obj = razorpay_client.payment.fetch(razorpay_payment_id)
		razorpay_payment_status = razorpay_payment_status_obj['status']
		razorpay_payment_amount = razorpay_payment_status_obj['amount']
		razorpay_payment_amount = razorpay_payment_amount/100
		if razorpay_payment_status == 'captured':
			license_payment=License_Payment()
			license_payment.pet_id = pet_id
			license_payment.razorpay_payment_id = razorpay_payment_id
			license_payment.razorpay_order_id = razorpay_order_id
			license_payment.razorpay_signature = razorpay_signature
			license_payment.razorpay_payment_status = razorpay_payment_status
			license_payment.save()
			pet = Pet.objects.filter(pet_id=pet_id).update(pet_license='Y')
			return render(request, 'customer/pet_licence_conform.html', {'pet_id': pet_id, 'customer_id': customer_id,'razorpay_order_id':razorpay_order_id,'razorpay_payment_status':razorpay_payment_status,'razorpay_payment_amount':razorpay_payment_amount,'petimg':petimg,'media_url':settings.MEDIA_URL,'petlist':petlist,'pets':pets})
		elif razorpay_payment_status == 'authorized':
			return HttpResponse('<h1>Authoised but not captured</h1>')
		else:
			return HttpResponse('<h1>Payment Failed</h1>')



def validate_form(request):
	serial_num = request.GET.get('formserialver', None)
	data = {
            'is_taken': Form_Unic_Number.objects.filter(form_number__iexact=serial_num).exists()
	}
	return JsonResponse(data)


#pet licencing viewss completed
def licence_admin(request):
	if request.method == 'POST':
		username=request.POST.get('username')
		password=request.POST.get('password')
		users=User.objects.all()
		user = authenticate(username=username, password=password)
		if user is not None:
			user_name=user.username
			request.session['user']=user.username
			if user.is_superuser:
				return redirect('govt_verify_licence',user_name=user_name)
			if user.is_staff:
				return redirect('govt_verify_licence',user_name=user_name)
	return render (request,'admin/admin_login.html')
#pet verifiying vew

def verify_licence(request):
	verify=License_Pet.objects.all()
	if request.method=="POST":
		petid=request.POST.get('petid')
		print(petid)
		pet = License_Pet.objects.filter(pet_id__id=petid).update(license_aprrove='Y')

	return render(request,'verify_licence.html',{'verify':verify,'media_url':settings.MEDIA_URL})

import random
def ran_gen(size, chars):
	string='AODH'
	s=Pet.objects.all()
	listt=[]
	for i in s:
		listt.append(i.licence_number)

	x=''.join(random.choice(chars) for x in range(size))
	if x not in listt:
		return string+x
	elif x in listt:
		y=ran_gen(8, "123456789")
		return y
#pet licence verifiying govt view
def govt_verify_licence(request,user_name):
	if request.method == "GET":
		if 'user' in request.session:
			session_id=request.session['user']
			if session_id == user_name :
				verify=License_Pet.objects.filter(license_aprrove='y')
				return render(request,'govt_verify_licence.html',{'verify':verify,'media_url':settings.MEDIA_URL,'user_name':user_name})
			else:
				return redirect ('licence_admin')
		else:
			return redirect('licence_admin')

	if request.method=="POST":
		petid=request.POST.get('petid')
		random_license=ran_gen(8, "123456789")
		Pet.objects.filter(id=petid).update(licence_number=random_license)
		pet = License_Pet.objects.filter(pet_id__id=petid).update(govt_certified_users='Y')
		x=License_Pet.objects.filter(pet_id__id=petid)
		today_date=date.today()
		return render(request,'generate_certificate.html',{'pet':pet,'x':x,'today_date':today_date})

#verifyed users licence aodh admin part
def verifyed_users(request):
	verify=License_Pet.objects.filter(license_aprrove='y')
	return render(request,'verifiyed_users_licence.html',{'verify':verify,'media_url':settings.MEDIA_URL})

#verifyed users licence governament part
def govt_certified_users(request,user_name):
	if request.method == "GET":
		if 'user' in request.session:
			session_id=request.session['user']
			if session_id == user_name :
				verify=License_Pet.objects.filter(govt_certified_users='y')
				return render(request,'govt_certified_users_licence.html',{'verify':verify,'media_url':settings.MEDIA_URL,'user_name':user_name})

			else:
				return redirect ('licence_admin')
		else:
			return redirect('licence_admin')

#pet licence for coustomer view
def coustomer_pet_licence(request,customer_id):
	if request.method =="GET":
		if 'customer_id' in request.session:
			session_id=request.session['customer_id']
			if session_id == customer_id :
				verify=License_Pet.objects.filter(pet_id__customer_id__customer_id=customer_id,govt_certified_users='y')
				return render(request,'customer/pet_licence.html',{'verify':verify})
			else:
				return redirect ('customer_login_home')
		else:
			return redirect('customer_login_home')

	if request.method=="POST":
		petid=request.POST.get('petid')

		return redirect('generate_certificate',pet_id=petid)
#aodh admin licence view
def aodh_admin_licence_view(request):
	verify=License_Pet.objects.filter(govt_certified_users='y')
	return render(request,'aodh_admin_licence_view.html',{'verify':verify,'media_url':settings.MEDIA_URL})

#licence certificate
def generate_certificate(request,pet_id):
	x=License_Pet.objects.filter(pet_id__id=pet_id)
	for i in x:

		z=i.valid_date

	startDate=z
	# reconstruct date fully
	#endDate = date(startDate.year + 1, startDate.month, startDate.day)
	# replace year only
	endDate = startDate.replace(startDate.year + 1)

	return render(request,'generate_certificate.html',{'x':x,'today_date':startDate,'endDate':endDate})


import urllib # Python URL functions
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
def customize_message(request,customer_id):
	doc_pk = request.session.get('doc_pk')
	previous_chat=doctor_message.objects.filter(doctor__id=doc_pk,customer__customer_id=customer_id)
	if request.method=="POST":
		msg=request.POST.get('msg')
		save_meesage=doctor_message()
		save_meesage.doctor=Doctor.objects.get(id=doc_pk)
		save_meesage.customer=Customer.objects.get(customer_id=customer_id)
		save_meesage.message=msg
		save_meesage.save()
		customer=Customer.objects.get(customer_id=customer_id)
		mobilenumber=customer.mobile
		if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
		getattr(ssl, '_create_unverified_context', None)):
			ssl._create_default_https_context = ssl._create_unverified_context
		authkey = "334231AXCttMDRD5efc1d91P1" # Your authentication key.
		mobiles = mobilenumber # Multiple mobiles numbers separated by comma.
		message = msg # Your message to send.
		sender = "AODHPC" # Sender ID,While using route4 sender id should be 6 characters long.
		route = "4" # Define route
		# Prepare you post parameters
		values = {
		          'authkey' : authkey,
		          'mobiles' : mobiles,
		          'message' : message,
		          'sender' : sender,
		          'route' : route
		          }
		url = "http://api.msg91.com/api/sendhttp.php" # API URL
		postdata = urllib.parse.urlencode(values).encode("utf-8") # URL encoding the data here.
		req = urllib2.Request(url, postdata)
		response = urllib.request.urlopen(req)
		output = response.read() # Get Response
	return render(request,'doctor/customize_message.html',
		{'doc_id':doc_pk,'customer_id':customer_id,'previous_chat':previous_chat})


def twillo(request):
	return render (request,'admin/twillo.html')

def mypets(request):
	customer_id = request.session['customer_id']
	try:
		petimg=petimage.objects.filter(customer_id=customer_id).all()
		petlist=[]
		for l in petimg:
			pet_id_img=l.pet_id.pet_id
			petlist.append(pet_id_img)
	except:
		pass
	customer_obj = Customer.objects.get(customer_id=customer_id)
	pets = Pet.objects.filter(customer_id=customer_obj)
	pets=pet_age_converter(pets)
	return render(request,'customer/mypet.html',{'pets':pets, 'customer_id':customer_id,'petimg':petimg,'petlist':petlist,'media_url':settings.MEDIA_URL,})

@csrf_exempt
def quantitycheck(request):
	if request.method=="POST":
		medicine=request.POST.get('medicine_name')
		doc_id=request.POST.get('doc_id')
		print(medicine,doc_id)
		data=stock.objects.filter(doctor__id=doc_id,medicine=medicine).last().quantity

		return JsonResponse(data,safe=False)
	return HttpResponse('ok')



import re
import datetime
def read_log_file(request):
    log_file_path = r"/home/ubuntu/aodhlog.log"
    f = open(log_file_path, 'r')
    file_content = f.read()
    file_content = re.split(
        '[0-9]{10}.[0-9]{6} ', file_content)
    print(file_content[2])
    datet = datetime.datetime.now()
    return render(request, "admin/logfile.html", {'file_content': file_content, 'datetime': datet})

def follow_up_date_reminder(request):
	if request.method =="POST":
		if '2_days' in request.POST:
			reminding_days=2
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=reminding_days)
			generate_followup_date_list=Prescription.objects.filter(followup_date=remindar_date)

			return render(request,'admin/followup_date_reminder.html',{'generate_followup_date_list':generate_followup_date_list,'today_date':today_date,'generated_day':'two_day'})

		elif '1_day' in request.POST:
			reminding_days=1
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=reminding_days)
			generate_followup_date_list=Prescription.objects.filter(followup_date=remindar_date)

			return render(request,'admin/followup_date_reminder.html',{'generate_followup_date_list':generate_followup_date_list,'today_date':today_date,'generated_day':'before_one'})

		elif 'on_day' in request.POST:
			today_date=date.today()
			remindar_date = date.today()
			generate_followup_date_list=Prescription.objects.filter(followup_date=remindar_date)

			return render(request,'admin/followup_date_reminder.html',{'generate_followup_date_list':generate_followup_date_list,'today_date':today_date,'generated_day':'on_day'})
	return render(request,'admin/followup_date_reminder.html')

def followup_date_send_sms(request):
	if request.method =="POST":
		if 'before_one' in request.POST:
			reminding_days=1
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=reminding_days)
			generate_followup_date_list=Prescription.objects.filter(followup_date=remindar_date)
			for i in generate_followup_date_list :
				customer_mobile=i.purpose_id.pet_id.customer_id.mobile
				if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
				getattr(ssl, '_create_unverified_context', None)):
					ssl._create_default_https_context = ssl._create_unverified_context
					doctor=DoctorViewLog.objects.get(purpose_id=i.purpose_id)

					msg ='''Dear proud pet owner,

						Your next follow-up visit date is on '''+str(i.followup_date)+". Please consult"+" "+doctor.doc_pk.Name_of_doctor.upper() +". You can book an appointment at https://aodhpet.com/registration/"+str(doctor.doc_pk.id)+"/" +"\n"+"\n"+"Regards,"+"\n"+"Aodh Petcare"



					authkey = "334231AXCttMDRD5efc1d91P1" # Your authentication key.

					mobiles = customer_mobile # Multiple mobiles numbers separated by comma.

					message = msg # Your message to send.

					sender = "AODHPC" # Sender ID,While using route4 sender id should be 6 characters long.

					route = "4" # Define route

					# Prepare you post parameters
					values = {
							'authkey' : authkey,
							'mobiles' : mobiles,
							'message' : message,
							'sender' : sender,
							'route' : route
							}


					url = "http://api.msg91.com/api/sendhttp.php" # API URL

					postdata = urllib.parse.urlencode(values).encode("utf-8") # URL encoding the data here.

					req = urllib2.Request(url, postdata)

					response = urllib.request.urlopen(req)

					output = response.read() # Get Response
					print(output)
		elif 'on_day' in request.POST:
			remindar_date = date.today()

			generate_followup_date_list=Prescription.objects.filter(followup_date=remindar_date)
			for i in generate_followup_date_list :
				customer_mobile=i.purpose_id.pet_id.customer_id.mobile
				if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
				getattr(ssl, '_create_unverified_context', None)):
					ssl._create_default_https_context = ssl._create_unverified_context
					doctor=DoctorViewLog.objects.get(purpose_id=i.purpose_id)

					msg ='''Dear proud pet owner,

						Your next follow-up visit date is TODAY'''+". Please consult"+" "+doctor.doc_pk.Name_of_doctor.upper() +". You can book an appointment at https://aodhpet.com/registration/"+str(doctor.doc_pk.id)+"/" +"\n"+"\n"+"Regards,"+"\n"+"Aodh Petcare"



					authkey = "334231AXCttMDRD5efc1d91P1" # Your authentication key.

					mobiles = customer_mobile # Multiple mobiles numbers separated by comma.

					message = msg # Your message to send.

					sender = "AODHPC" # Sender ID,While using route4 sender id should be 6 characters long.

					route = "4" # Define route

					# Prepare you post parameters
					values = {
							'authkey' : authkey,
							'mobiles' : mobiles,
							'message' : message,
							'sender' : sender,
							'route' : route
							}


					url = "http://api.msg91.com/api/sendhttp.php" # API URL

					postdata = urllib.parse.urlencode(values).encode("utf-8") # URL encoding the data here.

					req = urllib2.Request(url, postdata)

					response = urllib.request.urlopen(req)

					output = response.read() # Get Response

		elif 'two_day' in request.POST:
			reminding_days=2
			today_date=date.today()
			remindar_date = date.today() + timedelta(days=reminding_days)
			generate_followup_date_list=Prescription.objects.filter(followup_date=remindar_date)
			for i in generate_followup_date_list :
				doctor=DoctorViewLog.objects.get(purpose_id=i.purpose_id)
				customer_mobile=doctor.customer_id.mobile

				if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
				getattr(ssl, '_create_unverified_context', None)):
					ssl._create_default_https_context = ssl._create_unverified_context

					msg ='''Dear proud pet owner,

						Your next follow-up visit date is on '''+str(i.followup_date)+". Please consult"+" "+doctor.doc_pk.Name_of_doctor.upper() +". You can book an appointment at https://aodhpet.com/registration/"+str(doctor.doc_pk.id)+"/" +"\n"+"\n"+"Regards,Aodh Petcare"



					authkey = "334231AXCttMDRD5efc1d91P1" # Your authentication key.

					mobiles = customer_mobile # Multiple mobiles numbers separated by comma.

					message = msg # Your message to send.

					sender = "AODHPC" # Sender ID,While using route4 sender id should be 6 characters long.

					route = "4" # Define route

					# Prepare you post parameters
					values = {
							'authkey' : authkey,
							'mobiles' : mobiles,
							'message' : message,
							'sender' : sender,
							'route' : route
							}


					url = "http://api.msg91.com/api/sendhttp.php" # API URL

					postdata = urllib.parse.urlencode(values).encode("utf-8") # URL encoding the data here.

					req = urllib2.Request(url, postdata)

					response = urllib.request.urlopen(req)

					output = response.read() # Get Response

	return HttpResponse('Messages has been sent successfully')


# from Crypto.Cipher import AES
# from Crypto.Hash import SHA256
# key = 'AODH$444'
# hash_obj = SHA256.new(key.encode('utf-8'))
# hkey = hash_obj.digest()
#
#
# def encript(info):
#     msg = info
#     BLOCK_SIZE = 16
#     PAD = '{'
#     padding = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PAD
#     cipher = AES.new(hkey, AES.MODE_ECB)
#     result = cipher.encrypt(padding(msg).encode('utf-8'))
#     return result
#
# def decript(info):
#     msg = info
#     PAD = '{'
#     decipher = AES.new(hkey, AES.MODE_ECB)
#     pt = decipher.decrypt(msg).decode('utf-8')
#     pad_index = pt.find(PAD)
#     result = pt[:pad_index]
#     return result
#
# def enc(request):
# 	en = Encript()
# 	name='aravind'
# 	en_txt = encript(name)
# 	en.name = en_txt
# 	en.save()
# 	print(decript(en_txt))
# 	return HttpResponse('done')



def patients_settlement(request):
	if request.method=='GET':
		if 'admin_user' in request.session:
			doctor_list=Doctor.objects.all()
			return render(request,'admin/patients_list.html',{'doctor_list':doctor_list})
		else:
			return redirect('admin_home')
	if request.method == 'POST':
		doc_pk=request.POST.get('doc_pk')
		doct_object=Doctor.objects.get(id=doc_pk)
		from_date=request.POST.get('from_date')
		to_date=request.POST.get('to_date')
		doctorviewlog=DoctorViewLog.objects.filter(booking_date__range=(from_date, to_date),
			doc_pk=doct_object)
		return render(request,'admin/patients_settlement.html',
			{'doctorviewlog':doctorviewlog})
