import resend
from app.core.logging import logger
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY


def send_verification_email(
        email : str,
        token : str
):
    logger.info(f"Sending verification email to {email}")
    verification_link = (f"http://localhost:8000/api/v1/auth/verify-email?token={token}")
    resend.Emails.send({
        "from" : "Finance App <onboarding@resend.dev>",
        "to" : [email],
        "subject" : "Verify your email",
        "html" : f"""
            <h2>Welcome to finance app</h2>
                <p> Click below to verify email </p>
            <a href = "{verification_link}">Verify Email</a>"""

    })
    response = resend.Emails.send({
        "from" : "Finance App <onboarding@resend.dev>",
        "to" : [email],
        "subject" : "Verify your email",
        "html" : f"""
            <h2>Welcome to finance app</h2>
                <p> Click below to verify email </p>
            <a href = "{verification_link}">Verify Email</a>"""

    })
    logger.info(response)
    

def send_password_reset_email(email : str, token : str):
    reset_link = reset_link = (f"http://localhost:8000/reset-password?token={token}")
    resend.Emails.send({
        "from": "Finance App <onboarding@resend.dev>",
        "to": [email],
        "subject": "Reset Password",
        "html": f"""
            <h2>Password Reset</h2>

            <a href="{reset_link}">
                Reset Password
            </a>
        """
    })

def send_budget_warning_email(email:str,category_name:str,spent:float,budget:float):
        resend.Emails.send({
        "from": "Finance App <onboarding@resend.dev>",
        "to": email,
        "subject": "Budget Warning",
        "html": f"""
        <h2>Budget Alert</h2>

        <p>You have used 90% of your budget.</p>

        <p>Category: {category_name}</p>
        <p>Spent: ${spent}</p>
        <p>Budget: ${budget}</p>
        """
    })
        
def send_budget_exceeded_email(email:str, category_name, spent:float, budget:float):
    resend.Emails.send({
        "from": "Finance App <onboarding@resend.dev>",
        "to": email,
        "subject": "Budget Exceeded",
        "html": f"""
        <h2>Budget Exceeded</h2>

        <p>You exceeded your budget.</p>

        <p>Category: {category_name}</p>
        <p>Spent: ${spent}</p>
        <p>Budget: ${budget}</p>
        """
    })