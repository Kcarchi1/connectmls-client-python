import time
import re

import requests
from requests import Response
from requests.sessions import RequestsCookieJar, Session

from connectmlsconnector.exceptions import InvalidCredentialsError
from connectmlsconnector.utils import extract_baseurl


def _find_csrf(text: str):
    match = re.search(r'name="_csrf" value="([^"]+)" />', text)
    if match:
        return match.group(1)

    return None


def _get_login_page_html(session: Session) -> str:
    response = session.get("https://connectmls.mredllc.com/slogin.jsp", allow_redirects=False)

    # Setting needed cookie for login page access.
    login_page = session.get(response.headers["Location"], allow_redirects=True)

    return login_page.text


def _check_credentials(session: Session, username: str, password: str, csrf_token: str) -> Response:
    response = session.post(
        url="https://connectmls-api.mredllc.com/oid/j_spring_security_check",
        params={
            "_csrf": csrf_token,
            "screenHeight": "",
            "screenWidth": "",
            "visitorid": "",
            "deviceType": "",
            "fromurl": "login.jsp",
            "j_username": username,
            "j_password": password,
            "bd": None,
            "nc": None,
            "loginInfo": ""
        },
        allow_redirects=False
    )

    if response.headers["Location"] == "https://connectmls-api.mredllc.com/oid/login?error=failure":
        raise InvalidCredentialsError("invalid username/password, double check your credentials.")

    return response


def _get_slogin_code(session: Session, referer: Response) -> str:
    authorize_response = session.get(url=referer.headers["Location"], allow_redirects=True)

    match = re.search(r"&code=([^']+)", authorize_response.text)

    return match.group(1)


def _sign_in(session, code):
    session.get(
        url=f"https://{extract_baseurl(session.cookies.list_domains())}/slogin.jsp?",
        params={
            "swidth": "1440",
            "sheight": "900",
            "deviceType": "desktop",
            "visitorid": str(int(time.time() * 1000)),
            "code": code
        },
        allow_redirects=True
    )

    return None


def get_auth_cookies(username: str, password: str) -> RequestsCookieJar:
    with requests.Session() as session:
        session.headers.update({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/119.0.0.0 Safari/537.36",
        })

        login_html = _get_login_page_html(session)
        csrf_token = _find_csrf(login_html)

        response = _check_credentials(session, username, password, csrf_token)

        code = _get_slogin_code(session, response)
        _sign_in(session, code)

        return session.cookies
