from django.urls import path
from medical.views import statReseach,stats,delete,detailMaladie,previewNotModal,searchPreview,base,validation,update_profile,search,user_login,user_logout,user_register,change_password,reset_password


urlpatterns = [
    path('',base, name='base'),
    path('search', search, name='search'),
    path('login', user_login, name='login'),
    path('update', update_profile, name='update'),
    path('register', user_register, name='register'),
    path('logout', user_logout, name='logout'),
    path('change_passeWord', change_password, name='change_passeWord'),
    path('reset', reset_password, name='reset'),
    path('validation', validation, name='validation'),
    path('searchPreview', searchPreview, name='searchPreview'),
    path('previewNotModal', previewNotModal, name='previewNotModal'),
    path('search/<str:slug>', detailMaladie, name='detailMaladie'),
    path('delete', delete, name='delete'),
    path('stats', stats, name='stats'),
    path('statReseach', statReseach, name='statReseach'),
]
handler404 = 'medical.views.error_404'