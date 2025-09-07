from django import forms
from .models import BackgroundImage, UploadedDocument

class BackgroundImageForm(forms.ModelForm):
    class Meta:
        model = BackgroundImage
        fields = ['image', 'position']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise forms.ValidationError('只接受 jpg 或 png 圖片')
        return image

class UploadedDocumentForm(forms.ModelForm):
    class Meta:
        model = UploadedDocument
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file.name.lower().endswith(('.txt', '.docx')):
            raise forms.ValidationError('只接受 txt 或 docx 文件')
        return file