import os

import zipfile

import shutil

import datetime

import pytz

from PIL import Image, ImageDraw, ImageFont

from django.conf import settings

from django.http import JsonResponse, FileResponse, HttpResponseBadRequest

from django.shortcuts import render

from django.utils.timezone import now, is_naive, make_naive

from docx import Document

from .models import UploadedDocument, BackgroundImage

from .forms import BackgroundImageForm, UploadedDocumentForm



ZIP_OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, 'zips')

RENDER_OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, 'rendered')



selected_background_id = None  # 紀錄已選底圖的 ID

uploaded_document = None       # 紀錄已上傳文件物件



# Create your views here.



def home_view(request):

    return render(request, 'pages/home.html')



def zc_upload_view(request):

    global selected_background_id, uploaded_document



    background_form = BackgroundImageForm()

    document_form = UploadedDocumentForm()

    backgrounds = BackgroundImage.objects.all()



    if request.method == 'POST':

        action = request.POST.get('action')



        # 使用者點選確定，才開始處理

        if action == 'submit':

            if not uploaded_document or not selected_background_id:

                return JsonResponse({'status': 'fail', 'message': '缺少底圖或文件'}, status=400)



            try:

                bg = BackgroundImage.objects.get(id=selected_background_id)

            except BackgroundImage.DoesNotExist:

                return JsonResponse({'status': 'fail', 'message': '找不到底圖'}, status=400)



            doc_path = uploaded_document.file.path

            if doc_path.endswith('.docx'):

                docx = Document(doc_path)

                content = '\n'.join([p.text for p in docx.paragraphs if p.text.strip()])

            else:

                with open(doc_path, 'r', encoding='utf-8') as f:

                    content = f.read()



            os.makedirs(RENDER_OUTPUT_DIR, exist_ok=True)

            generate_text_image(content, bg.image.path, bg.position, RENDER_OUTPUT_DIR)



            os.makedirs(ZIP_OUTPUT_DIR, exist_ok=True)

            zip_filename = f"{os.path.splitext(os.path.basename(uploaded_document.file.name))[0]}.zip"

            zip_path = os.path.join(ZIP_OUTPUT_DIR, zip_filename)

            with zipfile.ZipFile(zip_path, 'w') as zipf:

                for fname in os.listdir(RENDER_OUTPUT_DIR):

                    fpath = os.path.join(RENDER_OUTPUT_DIR, fname)

                    zipf.write(fpath, arcname=fname)



            shutil.rmtree(RENDER_OUTPUT_DIR)

            os.remove(uploaded_document.file.path)

            uploaded_document.delete()



            uploaded_document = None

            selected_background_id = None



            return JsonResponse({'status': 'success'})



        # 使用者上傳文件（但不處理）

        if 'file' in request.FILES:

            document_form = UploadedDocumentForm(request.POST, request.FILES)

            if not document_form.is_valid():

                return JsonResponse({'status': 'fail', 'message': '文件無效'}, status=400)



            uploaded_document = document_form.save()

            return JsonResponse({'status': 'success', 'filename': uploaded_document.file.name})



        # 使用者選擇底圖（AJAX 傳 ID）

        if 'selected_bg_id' in request.POST:

            selected_background_id = request.POST.get('selected_bg_id')

            return JsonResponse({'status': 'success'})



        return JsonResponse({'status': 'fail', 'message': '未知操作'}, status=400)



    return render(request, 'pages/upload.html', {

        'background_form': background_form,

        'document_form': document_form,

        'backgrounds': backgrounds,

    })



def zc_download_view(request):

    os.makedirs(ZIP_OUTPUT_DIR, exist_ok=True)

    zips = []



    for fname in os.listdir(ZIP_OUTPUT_DIR):

        fpath = os.path.join(ZIP_OUTPUT_DIR, fname)

        ctime = datetime.datetime.fromtimestamp(os.path.getctime(fpath), tz=pytz.UTC)

        if (now() - ctime).total_seconds() > 86400:

            os.remove(fpath)

        else:

            zips.append({

                'name': os.path.splitext(fname)[0],

                'path': f"/media/zips/{fname}"

            })



    return render(request, 'pages/download.html', {'zips': zips})



def delete_zip_file(request, filename):

    filepath = os.path.join(ZIP_OUTPUT_DIR, f"{filename}.zip")

    if os.path.exists(filepath):

        os.remove(filepath)

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'fail'}, status=404)



def generate_text_image(content, background_path, position, output_dir):

    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'ChenYuluoyan-Thin-Monospaced.ttf')

    font_size = 68 if position == 'normal' else 50

    group_nword = 12

    end_char = '。，！？!?'

    end_pair = ['。」', '？」', '！」', '?」', '!」', '」。', '」，', '」？', '」！', '」?', '」!']

    while '\n\n' in content:

        content = content.replace('\n\n', '\n')

    contents = content.split('\n')

    new_contents = list()

    for segment in contents:

        line = segment

        word_count = 0

        while len(line) > 120:

            append_line = line[:80]

            flag = True

            while flag:
            
                if line[80 + word_count: 80 + word_count + 2] in end_pair:

                    append_line += line[80 + word_count: 80 + word_count + 2]

                    line = line[80 + word_count + 2:]

                    flag = False

                elif line[80 + word_count] in end_char:

                    append_line += line[80 + word_count]

                    line = line[80 + word_count + 1:]

                    flag = False

                else:

                    append_line += line[80 + word_count]

                    word_count += 1

            new_contents.append(append_line)

        new_contents.append(line)


    contents = new_contents

    count = 1

    for section in contents:

        lines = [section[group_nword * i: group_nword * (i + 1)] for i in range((len(section) // group_nword) + 1)]
                                                                                 
        lens = [len(line) for line in lines if line]

        maxlen = max(lens) if lens else 10

        nrow = len(lines)

        img = Image.open(background_path)

        font = ImageFont.truetype(font_path, font_size)

        draw = ImageDraw.Draw(img)

        for idx, line in enumerate(lines):

            if not line:
            
                continue

            if position == 'normal':

                x = img.width / 2 - maxlen * font_size / 2

                y = img.height / 2 - nrow * (font_size + 5) / 2 + idx * (font_size + 5)

            elif position == 'left':

                x = font_size * 1.8

                y = img.height / 2 - nrow * font_size / 2 + idx * font_size

            elif position == 'right':

                x = img.width - font_size * (maxlen + 1.4)

                y = img.height / 2 - nrow * font_size / 2 + idx * font_size

            draw.text((x, y), line, fill=(0, 0, 0), font=font)

        filename = f'written_letter_{position}_{count}.png'

        img.save(os.path.join(output_dir, filename))

        count += 1 



def upload_background_ajax(request):

    if request.method == 'POST' and request.FILES.get('image'):

        if BackgroundImage.objects.count() >= 6:

            return JsonResponse({'status': 'fail', 'message': '最多只能有 6 張底圖'}, status=400)



        form = BackgroundImageForm(request.POST, request.FILES)

        if form.is_valid():

            image = form.save()

            return JsonResponse({

                'status': 'success',

                'id': image.id,

                'url': image.image.url,

                'position': image.position

            })

        else:

            return JsonResponse({'status': 'fail', 'message': '格式錯誤'}, status=400)



    return HttpResponseBadRequest()





def delete_background(request, bg_id):

    if request.method == 'POST':

        try:

            bg = BackgroundImage.objects.get(id=bg_id)

            image_path = bg.image.path

            bg.delete()

            if os.path.exists(image_path):

                os.remove(image_path)

            return JsonResponse({'status': 'success'})

        except BackgroundImage.DoesNotExist:

            return JsonResponse({'status': 'fail', 'message': '圖片不存在'}, status=404)



    return HttpResponseBadRequest()