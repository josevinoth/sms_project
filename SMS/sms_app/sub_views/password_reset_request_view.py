from datetime import datetime, timedelta
import secrets
import smtplib

from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import BadHeaderError, EmailMessage, get_connection
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import constant_time_compare, salted_hmac

OTP_SESSION_KEY = "password_reset_otp_state"
OTP_VALID_MINUTES = 10
OTP_MAX_ATTEMPTS = 5


def _hash_otp(user_id, otp):
    return salted_hmac("password_reset_otp", f"{user_id}:{otp}").hexdigest()


def _clear_otp_state(request):
    if OTP_SESSION_KEY in request.session:
        del request.session[OTP_SESSION_KEY]


def _send_password_reset_otp_email(recipient_email, email_body):
    itadmin_cfg = settings.DEPARTMENT_EMAILS.get("itadmin", {})
    from_email = itadmin_cfg.get("EMAIL_HOST_USER") or settings.PASSWORD_RESET_FROM_EMAIL

    connection = get_connection(
        host=itadmin_cfg.get("EMAIL_HOST", settings.EMAIL_HOST),
        port=itadmin_cfg.get("EMAIL_PORT", settings.EMAIL_PORT),
        username=itadmin_cfg.get("EMAIL_HOST_USER", settings.EMAIL_HOST_USER),
        password=itadmin_cfg.get("EMAIL_HOST_PASSWORD", settings.EMAIL_HOST_PASSWORD),
        use_tls=itadmin_cfg.get("EMAIL_USE_TLS", settings.EMAIL_USE_TLS),
        fail_silently=False,
    )

    message = EmailMessage(
        subject="SMS Password Reset OTP",
        body=email_body,
        from_email=from_email,
        to=[recipient_email],
        connection=connection,
    )
    message.send(fail_silently=False)


def password_reset_request(request):
    entered_username = ""
    if request.method == "POST":
        entered_username = request.POST.get("username", "").strip()
        if not entered_username:
            messages.error(request, "Please enter your username.")
            return render(request, "password/password_reset.html", {"entered_username": entered_username})

        _clear_otp_state(request)

        user = User.objects.filter(username__iexact=entered_username, is_active=True).first()
        if not user:
            messages.error(request, "Username not found. Please check and try again.")
            return render(request, "password/password_reset.html", {"entered_username": entered_username})

        if not user.email:
            messages.error(request, "No email is configured for this username. Please contact admin.")
            return render(request, "password/password_reset.html", {"entered_username": entered_username})

        otp = f"{secrets.randbelow(1000000):06d}"
        request.session[OTP_SESSION_KEY] = {
            "user_id": user.id,
            "username": user.username,
            "user_email": user.email,
            "otp_hash": _hash_otp(user.id, otp),
            "expires_at": (timezone.now() + timedelta(minutes=OTP_VALID_MINUTES)).isoformat(),
            "attempts_left": OTP_MAX_ATTEMPTS,
            "verified": False,
        }

        email_context = {
            "username": user.username,
            "otp": otp,
            "valid_minutes": OTP_VALID_MINUTES,
        }
        email = render_to_string("password/password_reset_email.txt", email_context)

        try:
            _send_password_reset_otp_email(user.email, email)
        except BadHeaderError:
            messages.error(request, "Invalid email header. Please try again.")
            _clear_otp_state(request)
            return redirect("password_reset")
        except smtplib.SMTPAuthenticationError:
            messages.error(request, "IT admin mailbox authentication failed. Please update IT admin email password in settings.")
            _clear_otp_state(request)
            return redirect("password_reset")
        except Exception:
            messages.error(request, "Unable to send OTP email right now. Please contact IT admin.")
            _clear_otp_state(request)
            return redirect("password_reset")

        messages.success(
            request,
            f"Username validated. OTP has been sent to {user.email}.",
        )
        return redirect("password_reset_otp_verify")

    return render(request, "password/password_reset.html", {"entered_username": entered_username})


def password_reset_otp_verify(request):
    otp_state = request.session.get(OTP_SESSION_KEY)
    if not otp_state:
        messages.error(request, "Start by entering your username for password reset.")
        return redirect("password_reset")

    expires_at = datetime.fromisoformat(otp_state["expires_at"])
    if timezone.now() > expires_at:
        _clear_otp_state(request)
        messages.error(request, "OTP has expired. Please request a new OTP.")
        return redirect("password_reset")

    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()
        if not entered_otp.isdigit() or len(entered_otp) != 6:
            messages.error(request, "Enter a valid 6-digit OTP.")
            return redirect("password_reset_otp_verify")

        if otp_state.get("attempts_left", 0) <= 0:
            _clear_otp_state(request)
            messages.error(request, "Too many invalid attempts. Please request a new OTP.")
            return redirect("password_reset")

        expected_hash = otp_state.get("otp_hash") or ""
        actual_hash = _hash_otp(otp_state["user_id"], entered_otp)
        if constant_time_compare(actual_hash, expected_hash):
            otp_state["verified"] = True
            otp_state["verified_at"] = timezone.now().isoformat()
            request.session[OTP_SESSION_KEY] = otp_state
            return redirect("password_reset_confirm")

        otp_state["attempts_left"] = otp_state.get("attempts_left", OTP_MAX_ATTEMPTS) - 1
        request.session[OTP_SESSION_KEY] = otp_state
        messages.error(request, f"Invalid OTP. Attempts left: {max(otp_state['attempts_left'], 0)}")
        return redirect("password_reset_otp_verify")

    return render(
        request,
        "password/password_reset_otp_verify.html",
        {
            "valid_minutes": OTP_VALID_MINUTES,
            "attempts_left": otp_state.get("attempts_left", OTP_MAX_ATTEMPTS),
            "username": otp_state.get("username", ""),
            "user_email": otp_state.get("user_email", ""),
        },
    )


def password_reset_confirm(request):
    otp_state = request.session.get(OTP_SESSION_KEY)
    if not otp_state or not otp_state.get("verified"):
        messages.error(request, "Verify OTP before setting a new password.")
        return redirect("password_reset")

    user = User.objects.filter(id=otp_state.get("user_id"), is_active=True).first()
    if not user:
        _clear_otp_state(request)
        messages.error(request, "Unable to find the user account. Please try again.")
        return redirect("password_reset")

    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            _clear_otp_state(request)
            messages.success(request, "Password reset successful. You can now log in.")
            return redirect("password_reset_complete")
    else:
        form = SetPasswordForm(user)

    return render(request, "password/password_reset_confirm.html", {"form": form})


