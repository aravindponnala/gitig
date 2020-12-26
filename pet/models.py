from __future__ import unicode_literals
from django.db import models

# Create your models here.
from django.db import models
from datetime import date, timedelta
from django.contrib.auth.models import User



# Create your models here.

class Customer(models.Model):
	customer_id = models.CharField(max_length=20)
	customer_name = models.CharField(max_length=50)
	email = models.CharField(max_length=50)
	mobile = models.CharField(max_length=15)
	password=models.CharField(max_length=250)
	address=models.TextField()
	subscribed=models.BooleanField(default=False)
	date = models.DateField(default=date.today)

class CustomerSubscribed(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	subscribed_date = models.DateField(default=date.today)
	subscribed_expiry = models.DateField(
		default=date.today() + timedelta(days=365))


class Pet(models.Model):
	customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
	pet_id = models.CharField(max_length=30)
	name = models.CharField(max_length=50)
	breed = models.CharField(max_length=50)
	dob=models.DateField(default=date.today)
	gender = models.CharField(max_length=10)
	address = models.TextField()
	licence_number=models.TextField()
	STATUS_CHOICES = (
            ('Y', 'YES'),
          		('N', 'NO'),
        )
	pet_license = models.CharField(
		max_length=5, choices=STATUS_CHOICES, default='N')


class PurposeAndDiet(models.Model):
	pet_id = models.ForeignKey(Pet, on_delete=models.CASCADE)
	diet = models.CharField(max_length=30)
	diet_state = models.CharField(max_length=30)
	disease = models.CharField(max_length=500)
	vaccination_purpose = models.CharField(max_length=100)
	symptoms_text=models.TextField()
	date = models.DateField(default=date.today)
	STATUS_CHOICES =(
		('A','ACTIVE'),
		('C','CLOSE'),
		)
	status=models.CharField(max_length=5,choices=STATUS_CHOICES,default='A')





class Assessment(models.Model):
	purpose_id = models.OneToOneField(PurposeAndDiet, on_delete=models.CASCADE)
	DERMATOLOGY=models.TextField()
	EYES=models.TextField()
	LUNGS=models.TextField()
	EARS=models.TextField()
	GASTROINTESTINAL=models.TextField()
	NOSE_THROAT=models.TextField()
	UROGENITAL=models.TextField()
	MOUTH_TEETH_GUMS=models.TextField()
	MUSKULOSKELETAL=models.TextField()
	HEART=models.TextField()
	others=models.TextField()
	date = models.DateField(default=date.today)


class Vitals(models.Model):
	purpose_id = models.OneToOneField(PurposeAndDiet, on_delete=models.CASCADE)
	Temperature=models.CharField(max_length=30,blank=True,null=True)
	Height=models.CharField(max_length=30,blank=True,null=True)
	Weight=models.CharField(max_length=20,blank=True,null=True)
	Pulse_rate=models.CharField(max_length=20,blank=True,null=True)
	Respiration_rate=models.CharField(max_length=30,blank=True,null=True)
	Age_of_maturity=models.CharField(max_length=15,blank=True,null=True)
	Oestrus=models.CharField(max_length=15,blank=True,null=True)
	Pregnancy=models.CharField(max_length=15,blank=True,null=True)
	date = models.DateField(default=date.today)


class Deworming(models.Model):
	purpose_id = models.OneToOneField(PurposeAndDiet, on_delete=models.CASCADE)
	pet=models.ForeignKey(Pet,on_delete=models.CASCADE)
	last_date = models.DateField()
	due_date = models.DateField()



class Diagnostics(models.Model):
	purpose_id = models.OneToOneField(PurposeAndDiet, on_delete=models.CASCADE)
	haematology=models.TextField()
	biochemistry=models.TextField()
	harmones=models.TextField()
	microbiology=models.TextField()
	parasitology=models.TextField()
	serology=models.TextField()
	cytology=models.TextField()
	rapid_test=models.TextField()
	radiology=models.TextField()
	others=models.TextField()
	date = models.DateField(default=date.today)

class Vaccination_coustmer(models.Model):
	pet=models.ForeignKey(Pet,on_delete=models.CASCADE)
	last_date_3_in_1_DAPV = models.DateField(default='1000-01-01')
	last_date_4_in_1_DHPP = models.DateField(default='1000-01-01')
	last_date_5_in_1_DA2PP = models.DateField(default='1000-01-01')
	last_date_6_in_1_DA2PPC = models.DateField(default='1000-01-01')
	last_date_7in1_DA2PPVL2 = models.DateField(default='1000-01-01')
	last_date_rabies = models.DateField(default='1000-01-01')
	last_date_distemper = models.DateField(default='1000-01-01')
	last_date_CAV_1 = models.DateField(default='1000-01-01')
	last_date_parovirus = models.DateField(default='1000-01-01')
	last_date_parainfluenza = models.DateField(default='1000-01-01')
	last_date_bordetella = models.DateField(default='1000-01-01')
	last_date_Can_L = models.DateField(default='1000-01-01')
	last_date_lyme = models.DateField(default='1000-01-01')
	last_date_corona = models.DateField(default='1000-01-01')
	last_date_giardia = models.DateField(default='1000-01-01')
	last_date_CAV_2 = models.DateField(default='1000-01-01')
	last_date_leptospirosis = models.DateField(default='1000-01-01')
	last_date_9_in_1_vaccine = models.DateField(default='1000-01-01')
	last_date_10_in_1_vaccine = models.DateField(default='1000-01-01')
	last_date_Feline_vaccine = models.DateField(default='1000-01-01')
	last_deworming = models.DateField(default='1000-01-01')
	date = models.DateField(default=date.today)

class Vaccination(models.Model):
	purpose_id = models.OneToOneField(PurposeAndDiet, on_delete=models.CASCADE)
	pet=models.ForeignKey(Pet,on_delete=models.CASCADE)
	last_date_3_in_1_DAPV = models.DateField()
	due_date_3_in_1_DAPV = models.DateField()
	last_date_4_in_1_DHPP = models.DateField()
	due_date_4_in_1_DHPP = models.DateField()
	last_date_5_in_1_DA2PP = models.DateField()
	due_date_5_in_1_DA2PP = models.DateField()
	last_date_6_in_1_DA2PPC = models.DateField()
	due_date_6_in_1_DA2PPC = models.DateField()
	last_date_7_in_1_DA2PPVL2 = models.DateField()
	due_date_7_in_1_DA2PPVL2 = models.DateField()
	last_date_rabies = models.DateField()
	due_date_rabies = models.DateField()
	last_date_distemper = models.DateField()
	due_date_distemper = models.DateField()
	last_date_CAV_1 = models.DateField()
	due_date_CAV_1 = models.DateField()
	last_date_parovirus = models.DateField()
	due_date_parovirus = models.DateField()
	last_date_parainfluenza = models.DateField()
	due_date_parainfluenza = models.DateField()
	last_date_bordetella = models.DateField()
	due_date_bordetella = models.DateField()
	last_date_CAV_2 = models.DateField()
	due_date_CAV_2 = models.DateField()
	last_date_lyme = models.DateField()
	due_date_lyme = models.DateField()
	last_date_corona = models.DateField()
	due_date_corona = models.DateField()
	last_date_giardia = models.DateField()
	due_date_giardia = models.DateField()
	last_date_Can_L = models.DateField()
	due_date_Can_L = models.DateField()
	last_date_leptospirosis = models.DateField()
	due_date_leptospirosis = models.DateField()
	last_date_9_in_1_vaccine = models.DateField(default='1000-01-01')
	last_date_10_in_1_vaccine = models.DateField(default='1000-01-01')
	last_date_Feline_vaccine = models.DateField(default='1000-01-01')
	due_date_9_in_1_vaccine = models.DateField(default='1000-01-01')
	due_date_10_in_1_vaccine = models.DateField(default='1000-01-01')
	due_date_Feline_vaccine = models.DateField(default='1000-01-01')
	date = models.DateField(default=date.today)


class Prescription(models.Model):
	purpose_id = models.OneToOneField(PurposeAndDiet, on_delete=models.CASCADE)
	medicine1_name=models.CharField(max_length=250)
	medicine1=models.CharField(max_length=500)
	medicine1_quantity=models.CharField(max_length=250)
	medicine2_name=models.CharField(max_length=250)
	medicine2=models.CharField(max_length=500)
	medicine2_quantity=models.CharField(max_length=250)
	medicine3_name=models.CharField(max_length=250)
	medicine3=models.CharField(max_length=500)
	medicine3_quantity=models.CharField(max_length=250)
	medicine4_name=models.CharField(max_length=250)
	medicine4=models.CharField(max_length=500)
	medicine4_quantity=models.CharField(max_length=250)
	medicine5_name=models.CharField(max_length=250)
	medicine5=models.CharField(max_length=500)
	medicine5_quantity=models.CharField(max_length=250)
	medicine6_name=models.CharField(max_length=250)
	medicine6=models.CharField(max_length=500)
	medicine6_quantity=models.CharField(max_length=250)
	medicine_other_name=models.CharField(max_length=250)
	medicine_other=models.CharField(max_length=500)
	medicine_other_quantity=models.CharField(max_length=250)
	Prescription_img=models.FileField(upload_to='doctorpres')
	followup_date = models.DateField(default='1000-01-01',null=True, blank=True)
	followup_date_unit = models.CharField(max_length=10)
	date = models.DateField(default=date.today)

class Symptoms(models.Model):
	purpose_id = models.OneToOneField(PurposeAndDiet, on_delete=models.CASCADE)
	notes = models.TextField()
	date = models.DateField(default=date.today)


class Doctor(models.Model):
	Name_of_doctor=models.CharField(max_length=50)
	Qualification=models.CharField(max_length=30)
	Registration_number = models.CharField(max_length=30)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	Gender = models.CharField(max_length=10)
	Date_of_birth = models.DateField()
	Experience = models.IntegerField()
	Hospital = models.CharField(max_length=50)
	Email = models.CharField(max_length=50)
	Mobile = models.CharField(max_length=15)
	Telephone = models.CharField(max_length=15)
	Address = models.TextField()
	consultation_fee=models.IntegerField()
	subscription_fee=models.IntegerField()
	password = models.CharField(max_length=30)
	mode=models.CharField(max_length=8)
	time_slot=models.TextField()
	stock_management=models.CharField(max_length=5)
	message = models.TextField()
	live_management = models.CharField(max_length=5)
	date = models.DateField(default=date.today)


class Log(models.Model):
	doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
	consultation_fee = models.CharField(max_length=20)
	final_fee = models.CharField(max_length=20)
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	purpose_id = models.OneToOneField(PurposeAndDiet, on_delete=models.CASCADE)
	pet_id=models.CharField(max_length=30)
	mode=models.CharField(max_length=20)
	booking_date = models.DateField(default=date.today)
	booking_expiry=models.DateTimeField()
	time_slot=models.CharField(max_length=20)
	booking_id = models.CharField(max_length=30)
	booking_expiry_date = models.DateField(default=date.today)
	date = models.DateField(default=date.today)
	STATUS_CHOICES =(
		('A','ACTIVE'),
		('C','CLOSE'),
		('CN','CANCEL'),
		('EX','EXPIRED')
		)
	status=models.CharField(max_length=7,choices=STATUS_CHOICES,default='A')

class Summary_analytics(models.Model):
	pet=models.CharField(max_length=30)
	id_pk=models.CharField(max_length=30)
	visit_date=models.DateField()



class DoctorViewLog(models.Model):
	customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE)
	pet_id = models.ForeignKey(Pet,on_delete=models.CASCADE)
	purpose_id = models.ForeignKey(PurposeAndDiet,on_delete=models.CASCADE,related_name='purpose')
	doc_pk = models.ForeignKey(Doctor,on_delete=models.CASCADE)
	payment=models.CharField(max_length=20)
	payment_type = models.CharField(max_length=20,default=None)
	mode=models.CharField(max_length=20)
	consultation_fee = models.CharField(max_length=20)
	subscription_fee = models.CharField(max_length=20)
	time_slot=models.CharField(max_length=20)
	meeting_id=models.TextField()
	booking_date = models.DateField(default=date.today)
	booking_expiry=models.DateTimeField()
	booking_expiry_date = models.DateField(default=date.today)
	date = models.DateField(default=date.today)
	STATUS_CHOICES =(
		('A','ACTIVE'),
		('C','CLOSE'),
		('CN','CANCEL'),
		('EX','EXPIRED')
	)
	status=models.CharField(max_length=7,choices=STATUS_CHOICES,default='A')

class DoctorLogList(models.Model):
	purpose_id = models.ForeignKey(PurposeAndDiet,on_delete=models.CASCADE)
	customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE)
	doc_pk = models.ForeignKey(Doctor,on_delete=models.CASCADE)
	pet_id = models.ForeignKey(Pet,on_delete=models.CASCADE)
	payment=models.CharField(max_length=20)
	color=models.CharField(max_length=20)
	mode=models.CharField(max_length=8)
	time_slot=models.CharField(max_length=20)
	meeting_id=models.TextField()
	booking_date = models.DateField(default=date.today)
	test_field=models.CharField(max_length=5,default='yes')
	date = models.DateField(default=date.today)


class Conferences(models.Model):
	title = models.CharField(max_length=250)
	location = models.CharField(max_length=150)
	content = models.TextField()
	timings = models.TimeField()
	url_link = models.TextField()
	date = models.DateField()


class Seminars(models.Model):
	title = models.CharField(max_length=250)
	location = models.CharField(max_length=150)
	content = models.TextField()
	timings = models.TimeField()
	url_link = models.TextField()
	date = models.DateField()


class Vet_News(models.Model):
	title = models.CharField(max_length=250)
	location = models.CharField(max_length=150)
	content = models.TextField()
	timings = models.TimeField()
	url_link = models.TextField()
	date = models.DateField()



class Articles(models.Model):
	article_title = models.CharField(max_length=250)
	summery = models.CharField(max_length=1000)
	authors = models.CharField(max_length=150)
	content = models.TextField()
	published_on = models.DateField()



class Case_Reports(models.Model):
	title = models.CharField(max_length=250)
	author = models.CharField(max_length=50)
	email = models.CharField(max_length=50)
	published_on = models.DateField()
	content = models.TextField()
	link = models.CharField(max_length=600)

class Book(models.Model):
	title = models.CharField(max_length=50)
	summary = models.TextField()
	file = models.FileField(upload_to='books/%Y/%m/%d/')

class bookmarks_article(models.Model):
	doc= models.ForeignKey(Doctor,on_delete=models.CASCADE)
	article_id= models.ForeignKey(Articles, verbose_name="Articles",on_delete=models.CASCADE)

class bookmarks_case_reports(models.Model):
	doc= models.ForeignKey(Doctor,on_delete=models.CASCADE)
	case_reports= models.ForeignKey(Case_Reports, verbose_name="Case_Reports",on_delete=models.CASCADE)

class bookmarks_conferences(models.Model):
	doc= models.ForeignKey(Doctor,on_delete=models.CASCADE)
	conferences= models.ForeignKey(Conferences, verbose_name="Conferences",on_delete=models.CASCADE)

class bookmarks_vet_news(models.Model):
	doc= models.ForeignKey(Doctor,on_delete=models.CASCADE)
	vet_news= models.ForeignKey(Vet_News, verbose_name="Vet_News",on_delete=models.CASCADE)
class bookmarks_seminars(models.Model):
	doc= models.ForeignKey(Doctor,on_delete=models.CASCADE)
	seminars= models.ForeignKey(Seminars, verbose_name="Seminars",on_delete=models.CASCADE)

class bookmarks_books(models.Model):
	doc= models.ForeignKey(Doctor,on_delete=models.CASCADE)
	books= models.ForeignKey(Book, verbose_name="Book",on_delete=models.CASCADE)

class Vccination_Remainder(models.Model):
	pet = models.ForeignKey(Pet,on_delete=models.CASCADE)
	vacanation_list=models.TextField()
	customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
	hospital=models.CharField(max_length=50)
	doctor=models.CharField(max_length=30)
	remiander_date = models.DateField(default=date.today)
	date = models.DateField(default=date.today)

class deworming_Remainder(models.Model):
	pet_id = models.ForeignKey(Pet,on_delete=models.CASCADE)
	deworming_list=models.TextField()
	customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
	hospital=models.CharField(max_length=50)
	doctor=models.CharField(max_length=30)
	remiander_date = models.DateField(default=date.today)
	date = models.DateField(default=date.today)

class followup_Remainder(models.Model):
	pet_id = models.ForeignKey(Pet,on_delete=models.CASCADE)
	customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
	hospital=models.CharField(max_length=50)
	doctor=models.CharField(max_length=30)
	remiander_date = models.DateField(default=date.today)
	date = models.DateField(default=date.today)

class petimage(models.Model):
	pet_id=models.ForeignKey(Pet,on_delete=models.CASCADE)
	customer_id=models.CharField(max_length=20)
	pet_image=models.FileField(upload_to='petimage/%Y/%m/%d/')
	img=models.CharField(max_length=20)

class cancel_booking(models.Model):
	customer_id=models.CharField(max_length=20)
	pet_id=models.ForeignKey(Pet,on_delete=models.CASCADE)
	purpose_id = models.ForeignKey(PurposeAndDiet,on_delete=models.CASCADE)
	doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
	date = models.DateField(default=date.today)

class gallery_image(models.Model):
	customer_id=models.CharField(max_length=20)
	gal_img=models.FileField(upload_to='gallery/%Y/%m/%d/')

class notification(models.Model):
	notification=models.TextField()
	customer_id=models.CharField(max_length=20)
	palyerid=models.TextField()


class License_Pet(models.Model):
	pet_id = models.ForeignKey(Pet, on_delete=models.CASCADE)
	file1 = models.FileField(upload_to='license/')
	file2 = models.FileField(upload_to='license/')
	file3 = models.FileField(upload_to='license/')
	file4 = models.FileField(upload_to='license/')
	STATUS_CHOICES = (
            ('Y', 'YES'),
          		('N', 'NO'),
        )
	license_aprrove = models.CharField(
		max_length=5, choices=STATUS_CHOICES, default='N')
	govt_certified_users = models.CharField(max_length=5, choices=STATUS_CHOICES, default='N')
	valid_date = models.DateField(default=date.today)



class Form_Unic_Number(models.Model):
	form_number = models.CharField(max_length=30)

class stock(models.Model):
	doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
	medicine=models.TextField()
	quantity=models.TextField()

class Consultation_Payment(models.Model):
	pet_id = models.CharField(max_length=30)
	razorpay_payment_id = models.CharField(max_length=100)
	razorpay_order_id = models.CharField(max_length=100)
	razorpay_signature = models.TextField()
	razorpay_payment_status = models.CharField(max_length=10)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['razorpay_order_id', 'razorpay_payment_id'], name='consultat_dashbo')
	]


class License_Payment(models.Model):
	pet_id = models.CharField(max_length=30)
	razorpay_payment_id = models.CharField(max_length=20)
	razorpay_order_id = models.CharField(max_length=20)
	razorpay_signature = models.TextField()
	razorpay_payment_status = models.CharField(max_length=30)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['razorpay_order_id', 'razorpay_payment_id'], name='license_dashbo')
	]

class Razorpay_Dashboard(models.Model):
	Payment_id = models.CharField(max_length=100)
	order_id = models.CharField(max_length=100)
	booking_id = models.CharField(max_length=100)
	payment_status = models.CharField(max_length=30)
	amount_paid = models.IntegerField(max_length=7)
	doctor_name = models.CharField(max_length=30)
	doctor_mobile = models.BigIntegerField(max_length=15)
	customer_name = models.CharField(max_length=30)
	customer_mobile = models.BigIntegerField(max_length=15)
	pet = models.CharField(max_length=50)
	payment_date = models.DateTimeField(default=date.today)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['order_id', 'Payment_id'], name='razorpay_dashbo')
	]

class doctor_message(models.Model):
	doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
	customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
	message=models.TextField()
	date = models.DateField(default=date.today)


class Encript(models.Model):
	name = models.TextField()
