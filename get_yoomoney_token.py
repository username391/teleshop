from typing import List
import requests

from yoomoney.exceptions import (
InvalidRequest,
UnauthorizedClient,
InvalidGrant,
EmptyToken
)


def get_auth_url(client_id: str, redirect_uri: str, scope: list[str]) -> str:
    url = 'https://yoomoney.ru/oauth/authorize'
    scope = '%20'.join([str(elem) for elem in scope])
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, params=params, headers=headers)
    return response.url


def auth_by_code(client_id: str, code: str, redirect_uri: str) -> str:
    url = 'https://yoomoney.ru/oauth/token'
    params = {
        'code': code,
        'client_id': client_id,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(url, params=params, headers=headers)

    return response.json()


url = get_auth_url(
      client_id="B2CF05A64AEFC38A6C1B3D8AAF2D91522903EC3931E98DA27C62B11671BAFE14",
      redirect_uri="https://localhost.ru",
      scope=["account-info",
             "operation-history",
             "operation-details",
             "incoming-transfers",
             "payment-p2p",
             "payment-shop",
             ]
      )
print(url)
