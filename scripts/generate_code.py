#!/usr/bin/env python3
"""
Analyzes a JPEG design image using Claude Vision API
and generates responsive HTML/CSS code.
"""

import sys
import os
import base64
from pathlib import Path
import anthropic

SYSTEM_PROMPT = """You are an expert front-end developer specializing in converting UI/UX design mockups into clean, production-ready HTML and CSS code.

Your task:
1. Analyze the provided design image carefully
2. Generate a complete, single HTML file with embedded CSS that faithfully reproduces the design
3. The code must be:
   - Fully responsive (mobile-first approach)
   - Semantic HTML5
   - Modern CSS (Flexbox/Grid as appropriate)
   - Cross-browser compatible
   - Clean and well-commented

Output ONLY the complete HTML file content, starting with <!DOCTYPE html> and ending with </html>.
Do not include any explanation or markdown code blocks - just the raw HTML."""

USER_PROMPT = """Please analyze this design image and generate a complete, responsive HTML/CSS implementation.

Requirements:
- Mobile-first responsive design
- Pixel-perfect recreation of the layout
- Use CSS custom properties for colors and spacing
- Include hover states for interactive elements
- Optimize for readability and maintainability

Output the complete HTML file only."""


def encode_image(image_path: str) -> tuple[str, str]:
    """Encode image to base64 and detect media type from file header."""
    with open(image_path, "rb") as f:
        raw = f.read()

    # Detect actual format from magic bytes
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        media_type = "image/webp"
    elif raw[:3] == b"\xff\xd8\xff":
        media_type = "image/jpeg"
    elif raw[:8] == b"\x89PNG\r\n\x1a\n":
        media_type = "image/png"
    elif raw[:6] in (b"GIF87a", b"GIF89a"):
        media_type = "image/gif"
    else:
        ext = Path(image_path).suffix.lower()
        media_type = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"

    return base64.standard_b64encode(raw).decode("utf-8"), media_type


def generate_html_css(image_path: str) -> str:
    """Call Claude Vision API to generate HTML/CSS from design image."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    image_data, media_type = encode_image(image_path)
    print(f"Detected media type: {media_type}")

    print(f"Calling Claude Vision API for: {image_path}")

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": USER_PROMPT,
                    },
                ],
            }
        ],
    )

    return message.content[0].text


def save_output(image_path: str, html_content: str) -> str:
    """Save generated HTML to output directory."""
    image_name = Path(image_path).stem
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"{image_name}.html"
    output_path.write_text(html_content, encoding="utf-8")

    print(f"Saved: {output_path}")
    return str(output_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_code.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    if not Path(image_path).exists():
        print(f"Error: File not found: {image_path}")
        sys.exit(1)

    print(f"Processing design image: {image_path}")

    html_content = generate_html_css(image_path)
    output_path = save_output(image_path, html_content)

    print(f"Successfully generated: {output_path}")


if __name__ == "__main__":
    main()
