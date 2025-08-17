import json
import time
import requests

url = "https://api.hh.ru/vacancies"


def filter_vacancies(vacancies_data: list) -> list:
    # Оставляет только вакансии с указанной зарплатой (от 100 000 руб.)
    filtered = []
    for vacancy in vacancies_data:
        salary = vacancy.get("salary")
        if salary and salary.get("currency") == "RUR":
            salary_from = salary.get("from")
            if salary_from is not None and int(salary_from) >= 500000:
                filtered.append(vacancy)
    return filtered


def extract_important_fields(vacancy: dict) -> dict:
    # Оставляет только важные поля вакансии
    return {
        "id": vacancy.get("id"),
        "name": vacancy.get("name"),
        "salary": vacancy.get("salary"),
        "url": vacancy.get("alternate_url"),
        "company": vacancy.get("employer", {}).get("name"),
        "experience": vacancy.get("experience", {}).get("name"),
        "skills": vacancy.get("snippet", {}).get("requirement"),
        "city": vacancy.get("area", {}).get("name"),
        "published_at": vacancy.get("published_at"),
    }


def fetch_hh_vacancies(url: str, page: int = 0):
    query_params = {
        "text": "django OR flask OR fastapi OR aiohttp OR litestar",
        "per_page": 100,
        "page": page,
    }
    resp = requests.get(url, query_params)
    if resp.status_code != 200:
        print("Запрос упал  с ошибкой", resp.text())
    print(f"Данные получены, страница: {page}")
    result = resp.json()
    return result


def fetch_all_hh_vacancies(url: str):
    page = 0
    vacancies_data = []
    while True:
        if page == 20:
            break
        vacancies = fetch_hh_vacancies(url, page)
        if len(vacancies["items"]) == 0:
            break
        vacancies_data.extend(vacancies["items"])
        time.sleep(0.2)
        page += 1
    filtered_vacancies = filter_vacancies(vacancies_data)
    simplified_vacancies = [extract_important_fields(v) for v in filtered_vacancies]

    with open("vacancies.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(simplified_vacancies, ensure_ascii=False, indent=4))


def main():
    fetch_all_hh_vacancies(url)


if __name__ == "__main__":
    main()
