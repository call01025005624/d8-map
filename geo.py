"""미션 ② 주소↔좌표: 주소를 위도·경도로 바꾸고, 그 좌표를 다시 주소로 바꾼다.

실행: python geo.py 서울 성동구 뚝섬로 273
다른 파일에서: from geo import address_to_coord, coord_to_address
              lat, lng = address_to_coord("서울 성동구 뚝섬로 273")
              addr = coord_to_address(lat, lng)
"""
import os
import sys

import requests
from dotenv import load_dotenv

# 🔌 API 주소는 여기 한 곳에만
API = {
    "address": "https://dapi.kakao.com/v2/local/search/address.json",
    "coord2address": "https://dapi.kakao.com/v2/local/geo/coord2address.json",
}


def _kakao_get(url, params):
    """카카오 로컬 API를 불러 documents 목록을 돌려준다. 실패하면 '⛔' RuntimeError."""
    load_dotenv(override=True)
    key = os.getenv("KAKAO_REST_API_KEY")
    if not key:
        raise RuntimeError("⛔ .env에 KAKAO_REST_API_KEY가 없어요")

    try:
        res = requests.get(  # 🔌 API 호출
            url,
            headers={"Authorization": f"KakaoAK {key}"},
            params=params,
            timeout=10,
        )
    except requests.RequestException:
        raise RuntimeError("⛔ 카카오 서버에 연결하지 못했어요. 인터넷을 확인해 주세요")

    if res.status_code == 401:
        raise RuntimeError("⛔ 카카오 REST API 키가 틀렸어요")
    if res.status_code == 403:
        raise RuntimeError("⛔ 카카오맵 사용 설정을 켜 주세요")
    if res.status_code != 200:
        raise RuntimeError(f"⛔ 카카오 API 요청에 실패했어요 (상태 코드 {res.status_code})")
    return res.json().get("documents", [])


def address_to_coord(address):
    """주소 → (위도, 경도). 찾지 못하면 None."""
    docs = _kakao_get(API["address"], {"query": address})
    if not docs:
        return None
    # x = 경도, y = 위도, 둘 다 글자라서 float()
    lat = float(docs[0]["y"])
    lng = float(docs[0]["x"])
    # 한국 밖 좌표는 잘못된 값으로 본다
    if not (33 <= lat <= 39 and 124 <= lng <= 132):
        return None
    return lat, lng


def coord_to_address(lat, lng):
    """(위도, 경도) → 도로명 주소. 도로명이 없으면 지번 주소. 찾지 못하면 None."""
    # 보낼 때는 x = 경도, y = 위도
    docs = _kakao_get(API["coord2address"], {"x": lng, "y": lat})
    if not docs:
        return None
    # road_address 는 null 일 수 있다
    road = docs[0].get("road_address")
    if road:
        return road["address_name"]
    jibun = docs[0].get("address")
    return jibun["address_name"] if jibun else None


def main():
    address = " ".join(sys.argv[1:]) or input("주소: ").strip()
    if not address:
        print("주소를 입력해 주세요")
        return

    try:
        coord = address_to_coord(address)
        if coord is None:
            print(f"'{address}'을(를) 찾지 못했어요")
            return
        lat, lng = coord
        print(f"1) 주소 → 좌표: 위도 {lat}, 경도 {lng}")

        back = coord_to_address(lat, lng)
        if back is None:
            print("2) 좌표 → 주소: 주소를 찾지 못했어요")
        else:
            print(f"2) 좌표 → 주소: {back}")
    except RuntimeError as e:
        print(e)
        return

    print("\n출처: 카카오 로컬 API (주소로 좌표 변환, 좌표로 주소 변환)")


if __name__ == "__main__":
    main()
