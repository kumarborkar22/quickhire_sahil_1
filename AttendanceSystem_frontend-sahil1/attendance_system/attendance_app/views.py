import requests
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from io import BytesIO
from PIL import Image
from django.core.cache import cache
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from datetime import datetime
from django.utils.timezone import now
from django.shortcuts import render
from django.http import StreamingHttpResponse ,FileResponse, HttpResponseNotFound
import cv2
from django.http import StreamingHttpResponse, JsonResponse
from django.conf import settings
import os
from .models import Attendance
from django.http import HttpResponse
import csv
from django.utils.timezone import now
import base64
from django.core.files.uploadedfile import InMemoryUploadedFile
import io
from PIL import Image

SPRING_BOOT_API = "https://attendancesystem.up.railway.app"

def index(request):
    return render(request ,  'landing_page.html')
    
    
    
@csrf_exempt
def create_superadmin(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone_no = request.POST.get("phone_no")
        enabled = request.POST.get("enabled") == "on"
        profile_pic = request.FILES.get("profile_pic")

        data = {
            "email": email,
            "password": password,
            "fullName": full_name,
            "phoneNo": phone_no,
            "enabled": enabled,
            "profilePic": profile_pic.name if profile_pic else ""
        }

        url = f"{SPRING_BOOT_API}/home/createSuperadmin"
        response = requests.post(url, json=data)

        try:
            response_data = response.json()
            if response.status_code == 200:
                messages.success(request, "Superadmin created successfully!")
            else:
                messages.error(request, response_data.get("message", "Error creating superadmin"))
        except requests.exceptions.JSONDecodeError:
            messages.error(request, "Created successfully!")

        return render(request, "create_superadmin.html")

    return render(request, "create_superadmin.html")


@csrf_exempt
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Construct API Login URL with credentials in query parameters
        api_url = f"{SPRING_BOOT_API}/home/login?userName={email}&password={password}"

        try:
            response = requests.post(api_url)  # Send POST request
            if response.status_code == 200:
                data = response.json()
                if "token" in data:  # Ensure JWT token exists
                    request.session['is_authenticated'] = True
                    request.session['auth_token'] = data.get("token")
                    request.session['user_data'] = data  # Store full user data
                    return redirect('superadmin_dashboard')
                else:
                    messages.error(request, "Token not received. Please try again.")
            else:
                messages.error(request, "Invalid credentials. Please try again.")

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Failed to connect to the authentication server. Error: {e}")

    return render(request, 'login_page.html')





def dashboard(request):
    if not request.session.get('is_authenticated'):
        return redirect('login')

    user_data = request.session.get('user_data', {})
    name = user_data.get('name', 'User')
    email = user_data.get('email', 'user@example.com')
    profile_picture = user_data.get('profile_picture', '/default_profile.jpg')

    # Timer Logic
    start_time = request.session.get('start_time')
    elapsed_time = request.session.get('elapsed_time', "00:00:00")

    if start_time:
        start_time = datetime.fromisoformat(start_time)
        current_time = now()
        delta = current_time - start_time
        elapsed_time = str(delta).split('.')[0]

        request.session['elapsed_time'] = elapsed_time  # Update session with elapsed time

    return render(request, 'dashboard.html', {
        'name': name,
        'email': email,
        'profile_picture': profile_picture,
        'elapsed_time': elapsed_time
    })

def logout_view(request):
    """ Logs out the user by clearing session data """
    request.session.flush()  # Clear session data
    return redirect('login')


def superadmin_dashboard(request):
    """ Displays the superadmin dashboard if authenticated """
    if not request.session.get('is_authenticated'):
        return redirect('login')

    user_data = request.session.get('user_data', {})  # Retrieve user details from session
    return render(request, 'superadmin_dashboard.html', {'user_data': user_data})


@csrf_exempt
def create_admin(request):
    if request.method == 'POST':
        try:
            full_name = request.POST.get('fullName')
            email = request.POST.get('userName')
            phone_no = request.POST.get('phoneNo')
            password = request.POST.get('password')
            joining_date = request.POST.get('joiningDate')

            enabled = request.POST.get('enabled', '0') == '1'
            address = request.POST.get('address')
            salary = request.POST.get('salary')
            department = request.POST.get('department')
            shift_start_time = request.POST.get('shiftStartTime')
            shift_end_time = request.POST.get('shiftEndTime')
            profile_pic = request.FILES.get('profilePic')

            # Convert image to Base64
            profile_pic_base64 = ""
            image_mime_type = "image/png"  # Default MIME type

            if profile_pic and isinstance(profile_pic, InMemoryUploadedFile):
                image_data = profile_pic.read()
                profile_pic_base64 = base64.b64encode(image_data).decode('utf-8')

                # Detecting MIME type based on file extension
                if profile_pic.name.lower().endswith('.jpg') or profile_pic.name.lower().endswith('.jpeg'):
                    image_mime_type = "image/jpeg"
                elif profile_pic.name.lower().endswith('.png'):
                    image_mime_type = "image/png"

                # Formatting Base64 string properly for retrieval
                profile_pic_base64 = f"data:{image_mime_type};base64,{profile_pic_base64}"
            api_url = f"{SPRING_BOOT_API}/superadmin/createAdmin"

            auth_token = request.session.get('auth_token')
            if not auth_token:
                messages.error(request, "Authentication token is missing. Please log in again.")
                return redirect('login')

            headers = {
                'Authorization': f"Bearer {auth_token}",
                'Content-Type': 'application/json'
            }

            payload = {
                "fullName": full_name,
                "userName": email,
                "phoneNo": phone_no,
                "password": password,
                "joiningDate": joining_date,
                "enabled": enabled,
                "profilePic": profile_pic_base64,
                "address": address,
                "salary": int(salary) if salary else 0,
                "department": department,
                "shiftStartTime": shift_start_time,
                "shiftEndTime": shift_end_time
            }

            response = requests.post(api_url, json=payload, headers=headers)
            response_data = response.json() if response.content else {}

            if response.status_code == 200:
                messages.success(request, "Admin added successfully!")
                return redirect('create_admin')
            else:
                error_message = response_data.get('message', 'Unknown error')
                messages.error(request, f"Failed to add admin: {error_message}")

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error connecting to server: {e}")

        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")

    return render(request, 'create_admin.html')





@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            full_name = request.POST.get('fullName')
            email = request.POST.get('userName')
            phone_no = request.POST.get('phoneNo')
            password = request.POST.get('password')
            joining_date = request.POST.get('joiningDate')

            enabled = request.POST.get('enabled', '0') == '1'
            address = request.POST.get('address')
            salary = request.POST.get('salary')
            department = request.POST.get('department')
            shift_start_time = request.POST.get('shiftStartTime')
            shift_end_time = request.POST.get('shiftEndTime')

            api_url = f"{SPRING_BOOT_API}/superadmin/createUser"

            auth_token = request.session.get('auth_token')
            if not auth_token:
                messages.error(request, "Authentication token is missing. Please log in again.")
                return redirect('login')

            headers = {
                'Authorization': f"Bearer {auth_token}",
                'Content-Type': 'application/json'
            }

            payload = {
                "fullName": full_name,
                "userName": email,
                "phoneNo": phone_no,
                "password": password,
                "joiningDate": joining_date,
                "enabled": enabled,
                "address": address,
                "salary": int(salary) if salary else 0,
                "department": department,
                "shiftStartTime": shift_start_time,
                "shiftEndTime": shift_end_time
            }

            response = requests.post(api_url, json=payload, headers=headers)
            response_data = response.json() if response.content else {}

            if response.status_code == 200:
                messages.success(request, "User added successfully!")
                return redirect('create_user')
            else:
                error_message = response_data.get('message', 'Unknown error')
                messages.error(request, f"Failed to add user: {error_message}")

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error connecting to server: {e}")

        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")

    return render(request, 'create_user.html')



@api_view(['POST'])
def forgot_password(request):
    url = f"{SPRING_BOOT_API}/home/forgotPassword"
    response = requests.post(url, json=request.data)
    return Response(response.json(), status=response.status_code)


@api_view(['POST'])
def reset_password(request):
    url = f"{SPRING_BOOT_API}/home/resetPassword"
    response = requests.post(url, json=request.data)
    return Response(response.json(), status=response.status_code)


@api_view(['GET'])
def get_all_departments(request):
    url = f"{SPRING_BOOT_API}/home/getAllDepartments"
    response = requests.get(url)
    departments = response.json() if response.status_code == 200 else []
    return render(request, 'get_all_departments.html', {'departments': departments})



def admin_dashboard(request):
    if not request.session.get('is_authenticated'):
        return redirect('login')
    return render(request, 'admin_dashboard.html', {'user_data': request.session.get('user_data')})



def user_dashboard(request):
    if not request.session.get('is_authenticated'):
        return redirect('login')
    return render(request, 'user_dashboard.html', {'user_data': request.session.get('user_data')})




camera = cv2.VideoCapture(0)

def start_camera(request=None):
    """Start the camera if not already running."""
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    return JsonResponse({"message": "Camera started"})

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def video_feed(request):
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def profile_image_view(request):
    user_data = request.session.get("user_data", None)
    if not user_data or "profile_image" not in user_data:
        return HttpResponseNotFound("No profile image found")

    profile_image_path = user_data["profile_image"]  # Example: "profile_pics/user1.jpg"
    full_image_path = os.path.join(settings.MEDIA_ROOT, profile_image_path)

    if os.path.exists(full_image_path):
        return FileResponse(open(full_image_path, "rb"), content_type="image/jpeg")
    else:
        return HttpResponseNotFound("Profile image not found")
    
def save_profile_image(request):
    if request.method == "POST":
        image_base64 = request.POST.get("profile_image")  # Ensure this key matches the frontend

        if not image_base64:
            print("🚨 No profile image received from form submission!")
            return redirect("home")

        # Save in session
        user_data = request.session.get("user_data", {})
        user_data["profile_image"] = image_base64  # Store Base64 image in session
        request.session["user_data"] = user_data
        request.session.modified = True  # Ensure session is saved

        print("✅ Profile image saved in session successfully!")
        return redirect("home")  # Redirect to home to see the profile picture

    return redirect("home")

import base64
from django.shortcuts import render, redirect
from django.contrib import messages

def home(request):
    user_data = request.session.get("user_data")

    if not user_data:
        print("🚨 No user data found in session!")
        return redirect("login")

    print("✅ User Data in Session:", user_data)  # Debugging: Print entire session

    image_base64 = user_data.get("profile_image")  

    if not image_base64:
        print("⚠️ No profile image data found in session!")
        image_url = None  # No image available
    else:
        # Ensure the Base64 string is properly formatted for display
        image_url = f"data:image/jpeg;base64,{image_base64}"

    return render(request, "capture.html", {"user_data": user_data, "image_url": image_url})

def capture_image(request):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    success, frame = camera.read()
    
    if success:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50))

        if len(faces) > 0:
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            image_path = os.path.join(settings.MEDIA_ROOT, "captured_face.jpg")
            cv2.imwrite(image_path, frame)

            return JsonResponse({
                "message": "Image saved successfully with face detection!",
                "image_url": settings.MEDIA_URL + "captured_face.jpg"
            })
        else:
            return JsonResponse({"error": "No face detected! Please position yourself in front of the camera."}, status=400)

    return JsonResponse({"error": "Failed to capture image"}, status=500)


def attendance_records(request):
    records = Attendance.objects.all().order_by('-timestamp')
    return render(request, 'records.html', {'records': records})


def capture_and_recognize(request):
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    camera.release()

    if ret:
        net = cv2.dnn.readNetFromCaffe(
            "deploy.prototxt",
            "res10_300x300_ssd_iter_140000.caffemodel"
        )

        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
        net.setInput(blob)
        detections = net.forward()

        face_detected = False
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                face_detected = True
                break

        if face_detected:
            _, buffer = cv2.imencode(".jpg", frame)
            captured_image_data = base64.b64encode(buffer).decode("utf-8")

            # 🔥 Store image in session
            request.session["captured_image_data"] = captured_image_data
            request.session.modified = True  # Ensure Django saves the session

            print("✅ Image stored in session!")  # Debugging statement
            print("📸 Session Data:", request.session.get("captured_image_data"))  # Print the stored image

            return JsonResponse({"status": "Face Detected"})

        return JsonResponse({"error": "No Face Detected!"}, status=400)

    return JsonResponse({"error": "Capture Failed!"}, status=400)





def download_attendance_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Timestamp', 'Image'])

    for record in Attendance.objects.all():
        writer.writerow([record.name, record.email, record.timestamp, record.image.url])

    return response

def stop_camera(request):
    global camera
    if camera is not None:
        camera.release()
        camera = None
    return JsonResponse({"message": "Camera stopped"})

def attendance3(request):
    user_data = request.session.get("user_data")
    
    if not user_data:
        print("🚨 No user data found in session!")
        return redirect("login")

    # Ensure user_data contains required keys
    user_data["fullName"] = user_data.get("fullName", "Unknown User")
    user_data["userName"] = user_data.get("userName", "No Email Provided")
    
    fullName = user_data["fullName"]
    email = user_data["userName"]

    # Get the current date and time
    now = datetime.now()
    entry_time = now.strftime("%I:%M %p")  # Format: HH:MM AM/PM
    entry_date = now.strftime("%d/%m/%Y")  # Format: DD/MM/YYYY

    return render(request, 'attendance_3.html', {
        "user_data": user_data,  # Pass user_data as a whole
        "entry_time": entry_time,  # Separate entry time
        "entry_date": entry_date,  # Separate entry date
        "fullName": fullName,
        "email": email,
    })


def attendance1(request):
    user_data = request.session.get("user_data")
    if not user_data:
        print("🚨 No user data found in session!")
        return redirect("login")

    # Ensure user_data contains required keys
    user_data["fullName"] = user_data.get("fullName", "Unknown User")
    user_data["userName"] = user_data.get("userName", "No Email Provided")
    fullName = user_data.get("fullName", "Unknown User")  # Default if not found
    email = user_data.get("userName", "No Email Provided")   # Default if not found
    # Get the current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format: YYYY-MM-DD HH:MM:SS

    return render(request, 'attendance_1.html', {
        "user_data": user_data,  # Pass user_data as a whole
        "current_datetime": current_datetime,
        "fullName": fullName,
        "email": email,
    })
import json 



@csrf_exempt
def attendance_4(request):
    # Debugging: Print session data
    print("✅ Session Data:", request.session.items())

    # Get user data & auth token
    user_data = request.session.get("user_data")
    captured_image = request.session.get("captured_image")  # Base64 image
    auth_token = request.session.get("auth_token")

    # Ensure user is logged in
    if not auth_token:
        print("❌ Missing auth token! Not redirecting, but showing error.")
        return render(request, "attendance_4.html", {
            "error": "Authentication token is missing. Please log in again.",
        })

    # Ensure user data exists
    if not user_data or "userId" not in user_data:
        print("❌ Missing user data or ID!")
        return render(request, "attendance_4.html", {
            "error": "User data not found or missing 'id'.",
        })

    # Ensure image is captured
    if not captured_image:
        print("❌ No captured image found!")
        return render(request, "attendance_4.html", {
            "error": "No captured image found. Please try again.",
        })

    # ✅ Extract User ID Correctly
    user_id = user_data.get("userId")  # Make sure this matches API expectations
    print(f"🔹 Extracted User ID: {user_id}")

    # ✅ Get current date and time
    now = datetime.now()
    checkin_date = now.strftime("%d-%m-%Y")
    checkin_time = now.strftime("%I:%M %p")

    # ✅ Prepare JSON payload
    checkin_data = {
        "userId": user_id,  # Ensure this is an integer
        "checkInTime": checkin_time,
        "checkInDate": checkin_date,
        "checkInImage": captured_image,
    }

    api_url = f"{SPRING_BOOT_API}/user/checkIn"

    # ✅ Add headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
    }

    try:
        print("🔍 Sending check-in data:", checkin_data)  # Debugging
        response = requests.post(api_url, json=checkin_data, headers=headers)
        print("✅ API Response:", response.status_code, response.text)  # Debugging

        if response.status_code == 200:
            response_data = response.json()
            return render(request, "attendance_4.html", {
                "message": "Check-in successful!",
                "user_data": user_data,
                "current_datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
                "fullName": user_data.get("fullName", "User"),
                "email": user_data.get("email", "Not Available"),
            })
        elif response.status_code == 401:
            print("❌ Unauthorized! Invalid or expired token.")
            return render(request, "attendance_4.html", {
                "error": "Unauthorized: Invalid or expired token. Please log in again.",
            })
        else:
            return render(request, "attendance_4.html", {
                "error": f"Failed to check in: {response.text}",
            })

    except requests.exceptions.RequestException as e:
        return render(request, "attendance_4.html", {
            "error": f"API request failed: {e}",
        })


def attendance4(request):
    return render(request, 'attendance/attendance4.html')