import sqlite3
import math


def calc_play_rating(chart_const, score):
    if score > 1009000:
        return chart_const + 2.15
    elif score > 1007500:
        return chart_const + 2 + (score - 1007500) / (1009000 - 1007500) * 0.15
    elif score > 1005000:
        return chart_const + 1.5 + (score - 1005000) / (1007500 - 1005000) * 0.5
    elif score > 1000000:
        return chart_const + 1 + (score - 1000000) / (1005000 - 1000000) * 0.5
    elif score > 975000:
        return chart_const + 0 + (score - 975000) / (1000000 - 975000) * 1
    elif score > 925000:
        return chart_const + -3 + (score - 925000) / (975000 - 925000) * 3
    elif score > 900000:
        return chart_const + -5 + (score - 900000) / (925000 - 900000) * 2
    elif score > 800000:
        return (chart_const - 5) / 2 + (score - 800000) / (900000 - 800000) * (
                    (chart_const + -5) - (chart_const - 5) / 2)
    elif score > 500000:
        return 0 + (score - 500000) / (800000 - 500000) * (chart_const - 5) / 2
    else:
        return 0


conn = sqlite3.connect('db.sqlite')
cursor = conn.cursor()

cursor.execute('''SELECT level, music_id, score_max, play_count FROM chusan_user_music_detail''')
user_music_details = cursor.fetchall()

array = []
array1 = []
not_found_count = 0

for detail in user_music_details:
    level, music_id, score_max, play_count = detail

    cursor.execute('''SELECT level, level_decimal, diff FROM chusan_music_level WHERE music_id = ?''', (music_id,))
    music_levels = cursor.fetchall()

    rating_constant = None
    for music_level in music_levels:
        if level == music_level[2]:
            rating_constant = float(str(music_level[0]) + '.' + str(music_level[1]))
            break

    cursor.execute('''SELECT name FROM chusan_music WHERE music_id = ?''', (music_id,))
    music_name = cursor.fetchall()

    if rating_constant is not None:
        play_rating = calc_play_rating(rating_constant, score_max)
        if rating_constant > math.floor(rating_constant) + 0.5:
            chart_lvl = str(int(math.floor(rating_constant))) + '+'
        else:
            chart_lvl = str(int(math.floor(rating_constant)))
        array.append([music_name[0], chart_lvl, rating_constant, score_max, round(play_rating, 2), play_count])

    else:
        not_found_count += 1
        array1.append([music_id, score_max])

conn.close()

sorted_matrix = sorted(array, key=lambda x: x[4], reverse=True)

top_30_play_ratings = [row[4] for row in sorted_matrix[:30]]
average_play_rating = sum(top_30_play_ratings) / len(top_30_play_ratings)

print("Top 30 play ratings in descending order:")
for i, row in enumerate(sorted_matrix[:30]):
    name, lvl, score_max, play_rating, play_count = row[0], row[1], row[3], row[4], row[5]
    name = str(name)[2: -3]
    print(
        f"{i + 1}. Music name: {name}, Level {lvl}, Score Max: {score_max}, Play Rating: {play_rating}, Play Count: {play_count}")

print("Your B30 AVG is:", round(average_play_rating, 2))

if not_found_count > 0:
    print()
    print("-----------------------------------------------------------------------------------------")
    print(f"Warning: {not_found_count} entries have been dropped. This is most likely due to outdated aqua database.")
    print("Here are the song_id and the score_max info of the dropped songs:")
    print(array1)
