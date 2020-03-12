import csv


def remove_duplicate_vibes():
    try:
        with open('cogs/general/vibes.csv', 'rt', encoding='utf-8') as file:
            cleaned_list = []
            reader = csv.reader(file)
            for row in reader:
                cleaned_list.append(row[0])
    except:
        print("file not found")

    with open('cogs/general/vibes.csv', 'wt', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        unique_list = set(cleaned_list)
        for vibe in unique_list:
            writer.writerow([vibe])


# remove_duplicate_vibes()
