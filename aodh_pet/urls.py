"""aodh_pet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import TemplateView


from pet import  views

urlpatterns = [
    path('',views.index,name="index"),
    path('registration/<str:doc_id>/',views.customer_registration, name='customer_registration'),
    path('Home_registration/', views.customer_registration_home, name='customer_registration_home'),
    path('msg/',views.msg,),
    path('msg_reg/',views.msg_reg,),
    path('verify/',views.verifyotpmsg,),
    path('resendotp/',views.resendotp,),
    path('userlogin/', views.login_home_password, name='customer_login_home'),
    path('login/<str:doc_id>/', views.customer_login_hospital, name='customer_login'),
    path('admin/', admin.site.urls),
    path('reg/',views.doctor),
    #Doctor Moduel Urls's
    path('doctorlogin', views.doctor_login, name='doctor_login'),
    path('patients/list/',views.list_patient,name='list_patient'),
    path('vitals/',views.vitals,name='vitals'),
    path('vaccination/',views.vaccination,name='vaccination'),
    path('deworming/',views.deworming,name='deworming'),
    path('symptoms/',views.symptoms,name='symptoms'),
    path('assessment/',views.Assessment_view,name='assessment'),
    path('diagnostic/',views.diagnostic,name='diagnostic_prescription'),
    path('prescription/',views.prescription,name='prescription'),
    path('prescription_nostock/',views.prescription_nostock,name="prescription_nostock"),
    path('summary/',views.summary,name='summary'),
    #Doctor Sidebar  Url's
    path('doctor/history/',
        views.doctor_history,name='doctor_history'),
    path('doctorhistory/summary/',
        views.doctor_history_summary,name='doctor_history_summary'),
    path('bookmarks/',views.bookmarks,name="bookmarks"),
    path('stocks/',views.stocks,name="stocks"),
    path('doctoranalytics/',views.doctoranalytics,name='danalytics'),
    path('analyticssummary/<int:purpose_id>/',
        views.summary_analytics,name='summary_analytics'),
    path('doctorprofile/',views.doctorprofile,name='doctor_profile'),
    path('custmizemessage/<str:customer_id>/',
        views.customize_message,name="customize_message"),
    #Doctor Corner Url's
    path('doctor/articles/', views.doctor_articles, name='articles_sbar'),
    path('doctor/articles/view/', views.doctor_view_article, name='view_article_sbar'),
    path('doctor/casereports/', views.case_reports_sbar, name='case_reports_sbar'),
    path('doctor/conferences/', views.conferences_sbar, name='conferences_sbar'),
    path('doctor/vetnews/', views.vet_news_sbar, name='vet_news_sbar'),
    path('doctor/seminars/', views.seminars_sbar, name='seminars_sbar'),
    path('doctor/viewseminar/', views.view_seminar_sbar, name='view_seminar_sbar'),
    path('doctor/books/', views.books_sbar, name='books_sbar'),
    path('x/',views.articlepk),
    path('casereportspk/',views.casereportspk),
    path('conferencepk/',views.conferencepk),
    path('seminarspk/',views.seminarspk),
    path('vetnewspk/',views.vetnewspk),
    path('bookspk/',views.bookspk),
    path('patients/list/<int:doc_id>/',views.list_patient,name='list_patient'),
    path('visitp/<str:pet_pk>/<str:purpose_pk>/<int:doc_id>/',views.visit_purpose2,name='visit_purpose2'),
    path('last_vaccination/<str:customer_id>/', views.last_vaccination, name='last_vaccination'),
    path('last_deworming/<str:customer_id>/', views.last_deworming, name='last_deworming'),
    path('summary_customer/<str:customer_id>/<pet_id>/',views.customer_previous,name='summary_customer'),
    path('customer_previous_visit/<purpose_id>/',views.summary_customer,name='customer_previous_visit'),
    path('home/login',views.admin, name='admin_home'),
    path('admin_Home',views.admin_home, name='admin_home_page'),
    path('doctor/registration',views.doctor_registration, name='doctor_registration'),
    path('doctor/list',views.doctor_list, name='doctor_list'),
    path('doctor/check/(?P<pk>[0-9]+)/',views.check, name='check'),
    path('registradusers/list',views.registrad_users_list, name='registrad_users_list'),
    path('patients/list',views.patients_list, name='patients_list'),
    path('payment/settement',views.patients_settlement, name='payment_settlement'),
    path('payment_anlytics',views.payment_anlytics, name='payment_anlytics'),
    path('doctorscorner',views.doctor_corner, name='doctors_corner'),
    path('conferences',views.conferences, name='conferences'),
    path('createconfernse',views.create_confernse, name='create_confernse'),
    path('viewconfernse/<int:pk>/',views.view_confernse, name='view_confernse'),
    path('seminars',views.seminars, name='seminars'),
    path('createseminar',views.create_seminar, name='create_seminar'),
    path('viewseminar/<int:pk>/',views.view_seminar, name='view_seminar'),
    path('vetnews',views.vet_news, name='vet_news'),
    path('createvetnews',views.create_vetnews, name='create_vetnews'),
    path('viewvetnews/<int:pk>/',views.view_vetnews, name='view_vetnews'),
    path('articles',views.articles, name='articles'),
    path('createarticle',views.create_article, name='create_article'),
    path('viewarticle/<int:pk>/',views.view_article, name='view_article'),
    path('books',views.books, name='books'),
    path('casereports',views.case_reports, name='case_reports'),
    path('createcasereport',views.create_casereport, name='create_casereport'),
    path('viewcasereport/<int:pk>/',views.view_casereport, name='view_casereport'),
    path('admin/pet/list/<str:customer_id>/', views.admin_pet_list, name='admin_pet_list'),
    path('admin/pet/summery/<str:pet_id>/', views.admin_pet_summery, name='admin_pet_summery'),
    path('admin/pet/summery/date/<str:pet_id>/', views.admin_pet_summery_date, name='admin_pet_summery_date'),
    path('admin/vaccination/',views.VaccinationDewormingReminder,name="vaccination_remainder"),
    path('admin/deworming/',views.deworming_remainder,name="deworming_remainder"),
    #pet details and edit add urls
    path('petdetails/<str:doc_pk>/',views.petdetails,name='petdetails'),
    path('pet_list/',views.pet_list,name='pet_list'),
    path('addpet/<str:doc_pk>/',views.addpet,name='addpet'),
    path('pet_edit/<str:customer_id>/<str:pet_id>/<str:doc_pk>/',views.peteditdetails,name='pet_edit_details'),
    #customer_booking consultation
    path('purpose_visit/',views.customer_purpose_visit,name='purpose_visit'),
    path('select_dite/',views.purpose_and_dite,name='pet_dite'),
    path('booking_summary/<str:booking_date>/',views.booking_summary,name='booking_summary'),
    path('pay_online_conform/<str:customer_id>/<str:doc_pk>/<str:pet_id>/<str:purpose_id>/<str:mode>/<str:url_date>/<str:check_visit>/<str:subscription_status>/',
         views.pay_online_conform, name='pay_online_conform'),
    path('booking_confirm/<str:booking_date>',views.booking_confirm,name='booking_confirm'),
    path('customer/doclist/', views.customer_doc_list, name='customer_doc_list'),
    path('doctor_list/<str:doc_pk>/<str:check_visit>/',views.doc_list,name="doctorlist"),
    path('time_slot/',views.time_slot,name="time_slot"),
    #end


    path('logout',views.logout_customer,name='logout'),
    path('ajax/validate_mobile/', views.validate_mobile, name='validate_mobile'),
    path('petimage/',views.petimageupload),
    path('mybookings/<str:customer_id>/',views.mybookings,name="mybookings"),
    path('mybooking_summary/<str:customer_id>/<str:purpose_id>/',views.mybooking_summary,name="mybooking_summary"),
    path('customerhome/<str:customer_id>/',views.customer_home_page,name="customer_home_page"),
    path('book_consultation/<str:customer_id>/<str:doc_pk>/',views.book_consultation,name='book_consultation'),

    path('terms_and_conditions/',views.terms_conditions,name='terms_conditions'),

    path('gallery/',views.gallery_pet_image,name="gallery_pet_image"),
    path('img/',views.gallery_pet_image,name="img"),
    path('gallery/<str:customer_id>/',views.gallery,name="gallery"),

    path('client/', include('client.urls')),
    path('api/', include('api.urls')),
    path('confo/<str:roomid>/<str:usertype>/<str:userref>/<customerid>/<doctorid>',
         views.confo, name='roomxx'),
    path('videothankyou/<customerid>/<doctorid>/',
         views.video_thankyou, name='videothankyou'),
    path('notifications/<str:customer_id>/',views.notifications,name="notifications"),
    path('anti_dog_whistle',views.anti_dog_whistle,name="anti_dog_whistle"),
    path('videoconsultation/<str:customer_id>/',views.video_consultation,name="video_consultation"),
    path('ip/',views.ip,name="ip"),
    path('onesignalid/',views.onesignalid),
    path('push/',views.webpush),
    path('pet/license/<str:customer_id>/',views.pet_licenseview, name="pet_license_home"),
    path('license/serial/<str:pet_id>/<str:customer_id>/',views.serial_verificetion, name='serial_verificetion'),
    path('license/payment/<str:pet_id>/<str:customer_id>/',views.licence_payment, name='licence_payment'),
    path('license/conform/<str:pet_id>/<str:customer_id>',views.licence_conform, name='licence_conform'),
    path('ajax/formserial/', views.validate_form, name='validate_form'),
    path('verify_licence/',views.verify_licence,name="verify_licence"),
    path('govt_verify_licence/<str:user_name>',views.govt_verify_licence,name="govt_verify_licence"),
    path('verifyed_users/',views.verifyed_users,name='verifyed_users'),
    path('govt_certified_users/<str:user_name>',views.govt_certified_users,name='govt_certified_users'),
    path('aodh_admin_licence_view/',views.aodh_admin_licence_view,name='aodh_admin_licence_view'),
    path('coustomer_pet_licence/<str:customer_id>',views.coustomer_pet_licence,name='coustomer_pet_licence'),
    path('generate_certificate/<str:pet_id>/',views.generate_certificate,name="generate_certificate"),
    path('licence_login/',views.licence_admin,name="licence_admin"),
    path('vidyo/',views.twillo,),
    path('stocks/<str:doc_id>/',views.stocks,name="stocks"),
    path('stockadd/<str:doc_id>/',views.stockadd,name="stockadd"),
    path('quantitycheck/',views.quantitycheck),
    path('stockdelete/',views.stockdelete),
    path('razorpay/dashboard/', views.razorpay_dash,name="razorpaydashboard"),
    path('aboutus/',TemplateView.as_view(template_name='about_us.html'), name='aboutus'),
    path('cancellationpolicy/',TemplateView.as_view(template_name='Customer_cancellation_policy.html'), name='cancellation_policy'),
    path('privacypolicy/',TemplateView.as_view(template_name='Customer_privacy_policy.html'), name='privacypolicy'),
    path('refundpolicy/',TemplateView.as_view(template_name='Customer_refund_policy.html'), name='refundpolicy'),
    path('ajax/validate_mobile/', views.validate_mobile, name='validate_mobile'),
    path('login_home_otp/', views.customer_login_home, name='login_home_otp'),
    path('complete_registration/<str:customer_id>/',views.complete_registration,name="complete_registration"),
    path('logfile/', views.read_log_file, name='loggingfile'),
    path('login_hospital_pw/<str:doc_id>/', views.customer_login_hospital_pw, name='login_hospital_pw'),
    path('followupdate/',views.follow_up_date_reminder,name='follow_up_date_reminder'),
    path('followup_date_send_sms/',views.followup_date_send_sms,name='followup_date_send_sms'),
    path('vaccination_reminder_sms/',views.vaccination_reminder_sms,name='vaccination_reminder_sms'),
    path('deworming_reminnder_sms/',views.deworming_reminnder_sms,name='deworming_reminnder_sms'),
    path('follow_up_date_list_view/',views.follow_up_date_list_view,name='follow_up_date_list_view'),
    path('deworming_reminder_list_view/',views.deworming_reminder_list_view,name='deworming_reminder_list_view'),
    path('vaccination_reminder_list_view/',views.vaccination_reminder_list_view,name='vaccination_reminder_list_view'),
    path('customer_profile/<str:customer_id>/',views.view_profile,name='view_profile'),
    path('view_profile_edit_name/<str:customer_id>/',views.view_profile_edit_name,name='view_profile_edit_name'),
    path('view_profile_edit_email/<str:customer_id>/',views.view_profile_edit_email,name='view_profile_edit_email'),
    path('view_profile_edit_mobile/<str:customer_id>/',views.view_profile_edit_mobile,name='view_profile_edit_mobile'),
    path('view_profile_edit_password/<str:customer_id>/',views.view_profile_edit_password,name='view_profile_edit_password'),
    path('view_profile_edit_address/<str:customer_id>/',views.view_profile_edit_address,name='view_profile_edit_address'),
    path('mypets', views.mypets, name='mypets'),



    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='commons/password-reset/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='commons/password-reset/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='commons/password-reset/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='commons/password-reset/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    path(
        "OneSignalSDKWorker.js",
        TemplateView.as_view(
            template_name="OneSignalSDKWorker.js",
            content_type="application/javascript"
        ),
        name="OneSignalSDKWorker.js",
        ),
    path(
        "OneSignalSDKUpdaterWorker.js",
        TemplateView.as_view(
            template_name="OneSignalSDKUpdaterWorker.js",
            content_type="application/javascript"
        ),
        name="OneSignalSDKUpdaterWorker.js",
        ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += staticfiles_urlpatterns()
