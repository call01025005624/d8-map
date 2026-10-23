"""미션 ① 장소 검색: 키워드로 카카오 로컬 API에서 장소를 찾는다.

실행: python place.py 성수동
다른 파일에서: from place import search_places
              places = search_places("성수동", size=5)
"""
import os
import sys

import requests
from dotenv import load_dotenv

# 🔌 API 주소는 여기 한 곳에만
API = {
    "keyword": "https://dapi.kakao.com/v2/local/search/keyword.json",
}


def search_places(query, size=5):
    """키워드로 장소를 찾아 [{이름, 주소, 위도, 경도, 전화, 분류, 링크}, ...] 로 돌려준다.

    실패하면 '⛔'로 시작하는 RuntimeError를 낸다. 결과가 없으면 빈 목록.
    """
    load_dotenv(override=True)
    key = os.getenv("KAKAO_REST_API_KEY")
    if not key:
        raise RuntimeError("⛔ .env에 KAKAO_REST_API_KEY가 없어요")

    try:
        res = requests.get(  # 🔌 API 호출
            API["keyword"],
            headers={"Authorization": f"KakaoAK {key}"},
            params={"query": query, "size": size},
            timeout=10,
        )
    except requests.RequestException:
        raise RuntimeError("⛔ 카카오 서버에 연결하지 못했어요. 인터넷을 확인해 주세요")

    if res.status_code == 401:
        raise RuntimeError("⛔ 카카오 REST API 키가 틀렸어요")
    if res.status_code == 403:
        raise RuntimeError("⛔ 카카오맵 사용 설정을 켜 주세요")
    if res.status_code != 200:
        raise RuntimeError(f"⛔ 장소 검색에 실패했어요 (상태 코드 {res.status_code})")

    places = []
    for doc in res.json().get("documents", []):
        # x = 경도, y = 위도, 둘 다 글자라서 float()
        lat = float(doc["y"])
        lng = float(doc["x"])
        # 한국 밖 좌표는 잘못된 값으로 보고 건너뛴다
        if not (33 <= lat <= 39 and 124 <= lng <= 132):
            continue
        places.append({
            "이름": doc["place_name"],
            # 도로명 주소가 비어 있으면 지번 주소
            "주소": doc.get("road_address_name") or doc.get("address_name", ""),
            "위도": lat,
            "경도": lng,
            "전화": doc.get("phone", ""),
            "분류": doc.get("category_name", ""),
            "링크": doc.get("place_url", ""),
        })
    return places


def main():
    query = " ".join(sys.argv[1:]) or input("찾을 장소: ").strip()
    if not query:
        print("검색어를 입력해 주세요")
        return

    try:
        places = search_places(query)
    except RuntimeError as e:
        print(e)
        return

    if not places:
        print(f"'{query}'을(를) 찾지 못했어요")
    else:
        print(f"'{query}' 검색 결과 {len(places)}곳\n")
        for i, p in enumerate(places, 1):
            print(f"{i}. {p['이름']}, {p['주소']}, {p['위도']}, {p['경도']}")

    print("\n출처: 카카오 로컬 API (키워드로 장소 검색)")


if __name__ == "__main__":
    main()
