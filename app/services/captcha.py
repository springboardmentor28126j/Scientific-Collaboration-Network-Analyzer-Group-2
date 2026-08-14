import random
import string
import time
import uuid
import html


# CAPTCHA storage
# captcha_id -> {
#     answer: str,
#     expires_at: float
# }
captcha_store = {}

CAPTCHA_EXPIRY_SECONDS = 300


def generate_captcha():
    """
    Generate a new CAPTCHA challenge.
    """

    characters = string.ascii_uppercase + string.digits

    answer = "".join(
        random.choices(
            characters,
            k=5
        )
    )

    captcha_id = str(uuid.uuid4())

    captcha_store[captcha_id] = {
        "answer": answer,
        "expires_at": time.time() + CAPTCHA_EXPIRY_SECONDS
    }

    # Escape value before putting it into SVG
    safe_answer = html.escape(answer)

    # Generate random visual noise
    lines = []

    for _ in range(6):

        x1 = random.randint(0, 240)
        y1 = random.randint(10, 80)

        x2 = random.randint(0, 240)
        y2 = random.randint(10, 80)

        lines.append(
            f'<line x1="{x1}" y1="{y1}" '
            f'x2="{x2}" y2="{y2}" '
            f'stroke="#94a3b8" stroke-width="1.5"/>'
        )

    lines_html = "".join(lines)

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg"
         width="250"
         height="90"
         viewBox="0 0 250 90">

        <rect
            width="250"
            height="90"
            rx="10"
            fill="#f8fafc"
        />

        {lines_html}

        <text
            x="125"
            y="58"
            text-anchor="middle"
            font-size="34"
            font-weight="700"
            font-family="Arial"
            letter-spacing="8"
            fill="#1e3a8a">
            {safe_answer}
        </text>

    </svg>
    """

    return {
        "captcha_id": captcha_id,
        "captcha_image": svg
    }


def verify_captcha(
    captcha_id: str,
    captcha_answer: str
):
    """
    Verify CAPTCHA answer.
    """

    if not captcha_id or not captcha_answer:
        return False

    captcha = captcha_store.get(captcha_id)

    if not captcha:
        return False

    # Expired CAPTCHA
    if time.time() > captcha["expires_at"]:

        captcha_store.pop(
            captcha_id,
            None
        )

        return False

    correct_answer = captcha["answer"]

    # CAPTCHA can only be used once
    captcha_store.pop(
        captcha_id,
        None
    )

    return (
        captcha_answer.strip().upper()
        == correct_answer.upper()
    )