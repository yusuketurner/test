#!/usr/bin/env python3
"""
Sends completion notifications via Discord Webhook and Gmail SMTP.
"""

import os
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.request
import urllib.error


def send_discord_notification(webhook_url: str, files_processed: str, status: str) -> bool:
    """Send notification to Discord channel via Webhook."""
    if status == "success":
        color = 0x00FF00  # green
        title = "テスト完了"
        description = f"デザイン画像からのHTML/CSS生成が完了しました。\n\n処理ファイル: `{files_processed}`"
    else:
        color = 0xFF0000  # red
        title = "処理失敗"
        description = f"HTML/CSS生成中にエラーが発生しました。\n\n処理対象: `{files_processed}`"

    payload = {
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color,
                "footer": {
                    "text": "Design-to-Code Automation"
                }
            }
        ]
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            print(f"Discord notification sent. Status: {response.status}")
            return True
    except urllib.error.HTTPError as e:
        print(f"Discord notification failed: {e.code} {e.reason}")
        return False
    except Exception as e:
        print(f"Discord notification error: {e}")
        return False


def send_email_notification(
    gmail_from: str,
    app_password: str,
    to_email: str,
    files_processed: str,
    status: str
) -> bool:
    """Send notification email via Gmail SMTP."""
    subject = "テスト完了"

    if status == "success":
        body = f"""テスト完了

デザイン画像からのHTML/CSS自動生成が正常に完了しました。

処理ファイル: {files_processed}

生成されたコードはGitHubリポジトリの output/ ディレクトリに保存されました。

---
Design-to-Code Automation System
"""
    else:
        body = f"""処理失敗の通知

HTML/CSS自動生成中にエラーが発生しました。

処理対象: {files_processed}

GitHubActionsのログをご確認ください。

---
Design-to-Code Automation System
"""

    msg = MIMEMultipart()
    msg["From"] = gmail_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_from, app_password)
            server.sendmail(gmail_from, to_email, msg.as_string())
        print(f"Email sent to {to_email}")
        return True
    except smtplib.SMTPAuthenticationError:
        print("Email failed: Authentication error. Check GMAIL_FROM and GMAIL_APP_PASSWORD.")
        return False
    except Exception as e:
        print(f"Email notification error: {e}")
        return False


def main():
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")
    gmail_from = os.environ.get("GMAIL_FROM", "")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD", "")
    to_email = os.environ.get("NOTIFY_TO_EMAIL", "choooolu47@gmail.com")
    files_processed = os.environ.get("FILES_PROCESSED", "unknown")
    job_status = os.environ.get("JOB_STATUS", "success")

    print(f"Sending notifications (status: {job_status})")
    print(f"Files processed: {files_processed}")

    discord_ok = False
    email_ok = False

    if webhook_url:
        discord_ok = send_discord_notification(webhook_url, files_processed, job_status)
    else:
        print("DISCORD_WEBHOOK_URL not set, skipping Discord notification")

    if gmail_from and gmail_app_password:
        email_ok = send_email_notification(
            gmail_from, gmail_app_password, to_email, files_processed, job_status
        )
    else:
        print("GMAIL_FROM or GMAIL_APP_PASSWORD not set, skipping email notification")

    if not discord_ok and not email_ok:
        print("Warning: All notifications failed")


if __name__ == "__main__":
    main()
