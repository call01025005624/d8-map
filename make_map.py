"""미션 ③ 지도 HTML: 장소 검색 결과를 카카오 지도 마커로 찍은 map.html을 만든다.

실행: python make_map.py 성수동
보기: python -m http.server 8000 --bind 127.0.0.1  →  http://localhost:8000/map.html
다른 파일에서: from make_map import kakao_map_html
"""
import json
import os
import sys

from dotenv import load_dotenv

from place import search_places

# 🔌 지도 SDK 주소 (브라우저가 부름, JavaScript 키 사용)
API = {
    "sdk": "https://dapi.kakao.com/v2/maps/sdk.js",
}

MAX_MARKERS = 200


def kakao_map_html(js_key, markers):
    """[{이름, 위도, 경도}, ...] 를 마커로 찍은 지도 HTML 글자를 돌려준다."""
    markers = [
        {"이름": m["이름"], "위도": m["위도"], "경도": m["경도"]}
        for m in markers[:MAX_MARKERS]
    ]
    # json.dumps 결과 속 "</" 가 <script>를 닫지 않게
    data = json.dumps(markers, ensure_ascii=False).replace("</", "<\\/")
    sdk_url = f"{API['sdk']}?appkey={js_key}&autoload=false"

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>카카오 지도</title>
<style>
  body {{ margin: 0; font-family: sans-serif; }}
  #map {{ width: 100%; height: 90vh; }}
  #help {{ padding: 8px 12px; font-size: 14px; color: #555; }}
</style>
</head>
<body>
<div id="map"></div>
<p id="help">지도가 회색이면: ① 카카오맵 사용 설정 ② 지금 주소(포트까지) 등록 ③ 서버 주소로 열기</p>
<script src="{sdk_url}"></script>
<script>
const places = {data};
kakao.maps.load(function () {{
  const map = new kakao.maps.Map(document.getElementById("map"), {{
    center: new kakao.maps.LatLng(37.5665, 126.9780),
    level: 5,
  }});
  if (places.length === 0) return;
  const bounds = new kakao.maps.LatLngBounds();
  places.forEach(function (p) {{
    const pos = new kakao.maps.LatLng(p.위도, p.경도);
    const marker = new kakao.maps.Marker({{ map: map, position: pos }});
    const box = document.createElement("div");
    box.style.padding = "4px 8px";
    box.textContent = p.이름;
    const info = new kakao.maps.InfoWindow({{ content: box }});
    kakao.maps.event.addListener(marker, "click", function () {{
      info.open(map, marker);
    }});
    bounds.extend(pos);
  }});
  map.setBounds(bounds);
}});
</script>
</body>
</html>
"""


def main():
    load_dotenv(override=True)
    js_key = os.getenv("KAKAO_JS_KEY")
    if not js_key:
        print("⛔ .env에 KAKAO_JS_KEY가 없어요 (JavaScript 키)")
        return

    query = " ".join(sys.argv[1:]) or input("찾을 장소: ").strip()
    if not query:
        print("검색어를 입력해 주세요")
        return

    try:
        places = search_places(query, size=15)
    except RuntimeError as e:
        print(e)
        return
    if not places:
        print(f"'{query}'을(를) 찾지 못했어요")
        return

    with open("map.html", "w", encoding="utf-8") as f:
        f.write(kakao_map_html(js_key, places))

    print(f"map.html 을 만들었어요 (마커 {len(places)}개)")
    print("보는 법: 이 폴더에서 python -m http.server 8000 --bind 127.0.0.1")
    print("        → 브라우저에서 http://localhost:8000/map.html")
    print("\n출처: 카카오 로컬 API, 카카오 지도 JavaScript SDK")


if __name__ == "__main__":
    main()
