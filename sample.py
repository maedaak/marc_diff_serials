import marc_diff_serials

vols_of_lib_a = "3(),4-6,9,10()"
vols_of_lib_b = "2-9"

# 補充可能な全巻
print(marc_diff_serials.fill_all(vols_of_lib_a, "2-11"))  # -> 2,3,7-8,10-11

# 古い巻の補充
print(
    marc_diff_serials.fill_old(vols_of_lib_a, "2(4-5),3-9")
)  # -> 2(4-5)

# 新しい巻の補充
print(
    marc_diff_serials.fill_new(vols_of_lib_a, "2-9,11(3-4)")
)  # -> 11(3-4)

# 途中の欠号の補充
print(marc_diff_serials.fill_middle(vols_of_lib_a, "5-11"))  # -> 7-8,10

# 自館の途中欠号
print(marc_diff_serials.middle_lack(vols_of_lib_a))  # -> 3(),7-8,10()

# 2館の所蔵マージ
print(
    marc_diff_serials.marge_vols(vols_of_lib_a, "8-9,10(4)")
)  # -> 3(),4-6,8-9,10()