#!/usr/bin/env python3
"""
Sends completion notification to Discord via Webhook.
"""

import os
import json
import urllib.request
import urllib.error


def send_discord_notification(webhook_url: str, files_processed: str, status: str) -> bool:
    if status == "success":
        color = 0x00FF00
        title = "テスト完了"
        description = f"デザイン画像からのHTML/CSS生成が完了しました。\n処理ファイル: `{files_processed}`"
    else:
        color = 0xFF0000
        title = "処理失敗"
        description = f"HTML/CSS生成中にエラーが発生しました。\n処理対象: `{files_processed}`"

    payload = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "footer": {"text": "Design-to-Code Automation"}
        }]
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


def main():
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")
    files_processed = os.environ.get("FILES_PROCESSED", "unknown")
    job_status = os.environ.get("JOB_STATUS", "success")

    if not webhook_url:
        print("DISCORD_WEBHOOK_URL not set")
        return

    send_discord_notification(webhook_url, files_processed, job_status)


if __name__ == "__main__":
    main()
