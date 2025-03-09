from django.shortcuts import render, HttpResponse
from django.contrib import messages


# Create your views here.
def index(request):
    return HttpResponse("This is homepage!")
from django.shortcuts import render

def index(request):
    return render(request, "index.html")  # Since it's in the global templates folder

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            category = form.cleaned_data['category']

            # Upload file to Firebase Storage
            bucket = storage.bucket()
            blob = bucket.blob(f"{category}/{uploaded_file.name}")
            blob.upload_from_file(uploaded_file, content_type=uploaded_file.content_type)

            # Make file publicly accessible
            blob.make_public()
            file_url = blob.public_url

            # Save file info in Django database
            new_file = UploadedFile(file_name=uploaded_file.name, category=category, file_url=file_url)
            new_file.save()

            messages.success(request, "File uploaded successfully!")
            return ('upload_file')

    else:
        form = FileUploadForm()

    files = UploadedFile.objects.all()
    return render(request, 'upload_download.html', {'form': form, 'files': files})
from django.shortcuts import render

def index(request):
    return render(request, "index.html")  # Change this if your homepage is different

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def courses(request):
    return render(request, "courses.html")

def team(request):
    return render(request, "team.html")

def testimonial(request):
    return render(request, "testimonial.html")

def page_not_found(request, exception):
    return render(request, "404.html", status=404)
