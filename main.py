import re
import json
from itertools import combinations
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from models import Rid, RaiArticleDetail, Section, Conf, engine


"""
Алгоритм поиска совпадений ключевых слов между статьями:

1. Получаем статьи вместе с их ключевыми словами (rus + eng),
   а также данными по секции и конференции.
2. Нормализуем keywords:
   - приводим к нижнему регистру
   - разбиваем по разделителям (, ;)
   - удаляем лишние пробелы
   - формируем множество уникальных слов.
3. Для каждой пары статей вычисляем коэффициент Жаккара:
      similarity = |A ∩ B| / |A ∪ B| * 100
4. Если процент сходства превышает заданный порог (например, 30%),
   считаем статьи потенциально похожими.
"""
SIMILARITY_THRESHOLD = 10  # порог в процентах


def normalize_keywords(text: str) -> set:
    if not text:
        return set()
    words = re.split(r"[;,]", text.lower())
    return {w.strip() for w in words if w.strip()}


def calculate_similarity(set1: set, set2: set) -> float:
    if not set1 and not set2:
        return 0.0
    return round(len(set1 & set2) / len(set1 | set2) * 100, 2)


def main():
    with Session(engine) as session:
        stmt = (
            select(
                Rid.id,
                Rid.key_words_rus,
                Rid.key_words_eng,
                Section.short_title,
                Conf.short_title.label("conf_title"),
                RaiArticleDetail.pages
            )
            .join(RaiArticleDetail, RaiArticleDetail.id_rid == Rid.id)
            .join(Section, RaiArticleDetail.id_section == Section.id)
            .join(Conf, Section.id_conf == Conf.id)
            .where(or_(Conf.short_title == "РИИ-2023"))
        )
        results = session.execute(stmt).all()

    articles = {}
    sections_map = defaultdict(list)
    conf_article_map = defaultdict(list)

    # ───── Назначение prop по секциям ─────
    section_prop_map = {}
    current_prop = 0

    for row in results:
        if row.short_title not in section_prop_map:
            section_prop_map[row.short_title] = current_prop
            current_prop += 1

        combined = f"{row.key_words_rus or ''},{row.key_words_eng or ''}"

        articles[row.id] = {
            "section": row.short_title,
            "conference": row.conf_title,
            "keywords": normalize_keywords(combined),
            "prop": section_prop_map[row.short_title],
            "pages":row.pages,
        }

        sections_map[row.short_title].append(row.id)
        conf_article_map[row.conf_title].append(row.id)

    nodes_articles = []
    nodes_sections = []
    nodes_confs = []
    id_map = {}
    current_index = 0

    # ───── Уровень 0 — статьи ─────
    for article_id, data in articles.items():
        id_map[article_id] = current_index
        nodes_articles.append({
            "id": current_index,
            "prop": data["prop"],
            "typeText": "A",
            "numText": data["pages"].split(".")[-1],
            "type": "circle",
            "num": 1,
            "score": 1,
            "isBase": True,
            "connections": [],
            "secStart": True,
            "secEnd": True,
            "fontStyle": "normal",
            "arrowOut": False,
            "arrowIn": False,
            "level": 0,
            "isLabel": True,
            "secLength": 1,
            "grey": False,
            "yellow": False,
            "sectorName": data["section"]
        })
        current_index += 1

    # ───── Уровень 1 — секции ─────
    for section_name, article_ids in sections_map.items():
        nodes_sections.append({
            "id": current_index,
            "prop": section_prop_map[section_name],
            "typeText": "P",
            "numText": section_name,
            "type": "circle",
            "num": 1,
            "score": 1,
            "isBase": True,
            "connections": [],
            "secStart": True,
            "secEnd": True,
            "fontStyle": "normal",
            "arrowOut": False,
            "arrowIn": False,
            "level": 1,
            "isLabel": True,
            "secLength": len(article_ids),
            "grey": False,
            "yellow": False,
            "sectorName": section_name
        })
        current_index += 1

    # ───── Уровень 2 — конференции ─────
    for conf_name, article_ids in conf_article_map.items():
        nodes_confs.append({
            "id": current_index,
            "prop": 0,
            "typeText": "C",
            "numText": conf_name,
            "type": "circle",
            "num": 1,
            "score": 1,
            "isBase": True,
            "connections": [],
            "secStart": True,
            "secEnd": True,
            "fontStyle": "normal",
            "arrowOut": False,
            "arrowIn": False,
            "level": 2,
            "isLabel": True,
            "secLength": len(article_ids),  # количество статей
            "grey": False,
            "yellow": False,
            "sectorName": conf_name
        })
        current_index += 1

    # ───── Связи статья ↔ статья по сходству ─────
    for (id1, a1), (id2, a2) in combinations(articles.items(), 2):
        similarity = calculate_similarity(a1["keywords"], a2["keywords"])
        if similarity >= SIMILARITY_THRESHOLD:
            idx1 = id_map[id1]
            idx2 = id_map[id2]
            nodes_articles[idx1]["connections"].append(idx2)
            nodes_articles[idx2]["connections"].append(idx1)

    result_json = [nodes_articles, nodes_sections, nodes_confs]

    with open("similarity_graph.json", "w", encoding="utf-8") as f:
        json.dump(result_json, f, ensure_ascii=False, indent=2)

    print("JSON успешно создан.")


if __name__ == "__main__":
    main()