import csv
import random


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


def distribution_check():
    vibe_count = {}
    for i in range(0, 100000):
        with open('cogs/general/vibes.csv', 'rt', encoding='utf-8') as f:
            # Select a random vibe
            reader = csv.reader(f)
            chosen_vibe = random.choice(list(reader))
            if chosen_vibe[0] in vibe_count:
                vibe_count[chosen_vibe[0]] = vibe_count[chosen_vibe[0]] + 1
            else:
                vibe_count[chosen_vibe[0]] = 1
    for vibe in vibe_count.items():
        print(f"{vibe[0]}: {vibe[1]}")
    print(len(vibe_count))
    print(min(vibe_count.values()))
    print(max(vibe_count.values()))


# distribution_check()
remove_duplicate_vibes()
