def generate_review(menu_name: str, keyword: str) -> dict:
    return {
        "menuName": menu_name,
        "rating": 5,
        "content": f"{menu_name}이(가) 정말 만족스러웠고 {keyword} 느낌이 잘 살아있었습니다."
    }
