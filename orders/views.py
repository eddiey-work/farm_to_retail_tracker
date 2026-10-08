from django.shortcuts import render

# Create your views here.
# from django.db.models import ProtectedError

# if request.method == 'POST':
#     name = crop.crop_name
#     try:
#         crop.delete()
#         messages.success(request, f"'{name}' has been deleted.")
#     except ProtectedError:
#         messages.error(request, f"'{name}' has orders and cannot be deleted. Mark it unavailable instead.")
#     return redirect('my_crops')