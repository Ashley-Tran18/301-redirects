# import requests
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry

# class RedirectHelper:

#     @staticmethod
#     def requests_redirect(url, timeout=10):
#         session = requests.Session()

#         retries = Retry(
#             total=3,
#             backoff_factor=0.3,
#             status_forcelist=[429, 500, 502, 503, 504],
#             allowed_methods=["GET"]
#         )

#         adapter = HTTPAdapter(max_retries=retries)
#         session.mount("http://", adapter)
#         session.mount("https://", adapter)

#         response = session.get(
#             url,
#             allow_redirects=True,
#             timeout=timeout,
#             headers={"User-Agent": "Mozilla/5.0"}
#         )

#         return {
#             "final_url": response.url,
#             "status_code": response.status_code,
#             "history": [(r.status_code, r.url) for r in response.history]
#         }
