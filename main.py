import csv
import os


def sort_list(dicts: list) -> list:
    if not dicts:
        return []

    first_key = next(iter(dicts[0]))

    dicts.sort(key=lambda d: d[first_key])


def file_names_generator(directory_path) -> str:
    try:
        files = os.listdir(directory_path)
        for f in files:
            if os.path.isfile(os.path.join(directory_path, f)):
                yield f"{directory_path}/{f}"
    except Exception:
        return


def process_report(path: str) -> dict:
    res = {
        "Заявки": 0,
        "Потери": 0,
        "Длина очереди": 0,
        "Загрузка": 0,
        "Среднее время ожидания": 0,
        "СКО": 0,
    }

    with open(path, 'r', encoding='utf-8', errors="replace") as file:
        lines = file.readlines()

        for i in range(len(lines)):
            line = lines[i].strip()

            # заявки | потери
            if line.startswith("LABEL"):
                applications = float(lines[i + 1].strip().split()[2])
                res["Заявки"] = applications

                lost1 = float(lines[i + 17].strip().split()[3])
                lost2 = float(lines[i + 18].strip().split()[3])
                res["Потери"] = lost1 + lost2

            # загрузка
            if line.startswith("FACILITY"):
                util1 = float(lines[i + 1].strip().split()[2])
                util2 = float(lines[i + 2].strip().split()[2])
                res["Загрузка"] = (util1 + util2) / 2

            # длина очереди | среднее время ожидания
            if line.startswith("QUEUE"):
                queue_size1 = float(lines[i + 1].strip().split()[5])
                queue_size2 = float(lines[i + 2].strip().split()[5])
                res["Длина очереди"] = queue_size1 + queue_size2

                mean_time_wait1 = float(lines[i + 1].strip().split()[6])
                mean_time_wait2 = float(lines[i + 2].strip().split()[6])
                res["Среднее время ожидания"] = (mean_time_wait1 + mean_time_wait2) / 2

            # СКО
            if line.startswith("TU_BUF_1") and len(lines[i].strip().split()) > 2:
                std1 = float(lines[i].strip().split()[2])
            if line.startswith("TU_BUF_2") and len(lines[i].strip().split()) > 2:
                std2 = float(lines[i].strip().split()[2])

                res["СКО"] = (std1 + std2) / 2
                break

    return res


result = []
for file_path in file_names_generator("./reports"):
    result.append(process_report(file_path))

sort_list(result)

csv_file_path = "output.csv"
with open(csv_file_path, mode='w', encoding='utf-8', newline='') as csvfile:
    fieldnames = ["Заявки", "Потери", "Длина очереди", "Загрузка", "Среднее время ожидания", "СКО"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for row in result:
        writer.writerow(row)

print(f"Данные сохранены в файл {csv_file_path}")

