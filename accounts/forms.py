from django import forms
from .models import Account, UserProfile



class RegistrationForm(forms.ModelForm):

    first_name = forms.CharField(max_length=25, widget=forms.TextInput(attrs={

        'class': 'form-control',
        'placeholder': 'First Name',
    }))
     
    last_name = forms.CharField(max_length=25, widget=forms.TextInput(attrs={

        'class': 'form-control',
        'placeholder': 'Last Name',
    }))


    password = forms.CharField(widget=forms.PasswordInput(attrs={

        'class': 'form-control',
        'placeholder': 'Enter Password'
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={

        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))

    
    email = forms.EmailField(widget=forms.EmailInput(attrs={

        'class': 'form-control',
        'placeholder': 'email@.com',

    }))

    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={

        'class': 'form-control',
        'placeholder': 'Phone Number',
    }))




    # class LoginForm(forms.ModelForm):
    #     username = forms.CharField(max_length=15, widget=forms.TextInput(attrs={

    #         'class': 'form-control',
    #         'placeholder':'enter the username',
    #     }))

    #     password = forms.PasswordInput(max_length=15, widget=forms.PasswordInput(attrs={

    #         'class': 'form-control',
    #         'placeholder':'enter password',
    #     }))




  # this tells django which fields to look up from the models
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password')


    def clean(self):
        cleaned_data = super(RegistrationForm,self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("password mismatch")
        


#instead of defining the form-control each time write a func for it 
    # def __init__(self, *args,**kwargs):
    #     super(RegistrationForm, self).__init__(*args, **kwargs)
    #     for field in self.fields:
    #         self.fields[field].widget.attrs['class'] = 'form-control'



class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name','phone_number')

    #instead of defining the form-control each time write a func for it 
    def __init__(self, *args,**kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):

    profile_picture = forms.ImageField(required=False, error_messages={'invalid':("images files only")}, widget=forms.FileInput)

    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2','city','state', 'country', 'profile_picture')

    def __init__(self, *args,**kwargs):
            super(UserProfileForm, self).__init__(*args, **kwargs)
            for field in self.fields:
             self.fields[field].widget.attrs['class'] = 'form-control'


