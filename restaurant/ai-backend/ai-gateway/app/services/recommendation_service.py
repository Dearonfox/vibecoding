def recommend_menu(keyword: str) -> dict:
    return {
        "keyword": keyword,
        "menus": [
            {"name": "김치볶음밥", "reason": f"{keyword}와 잘 어울리는 든든한 메뉴"},
            {"name": "제육덮밥", "reason": f"{keyword} 키워드에 맞는 인기 메뉴"}
        ]
    }
