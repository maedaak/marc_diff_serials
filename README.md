# marc_diff_serials

図書館目録における雑誌包括所蔵形のデータをもとに、 同一雑誌タイトルについての２館間の所蔵を比較する
  ※ 自作のPerlモジュールMMARC::diffSerials (https://mbc.dl.itc.u-tokyo.ac.jp/MARC-diffSerials/ )をPyton化したもの

同一雑誌タイトルについて、2 館の所蔵状況を文字列として表し、補充可能な巻や欠号、マージ結果を計算します。

## 使い方

```python
import marc_diff_serials

vols_of_lib_a = "3(),4-6,9,10()"
vols_of_lib_b = "2-9"

print(marc_diff_serials.fill_all(vols_of_lib_a, "2-11"))
print(marc_diff_serials.fill_old(vols_of_lib_a, "2(4-5),3-9"))
print(marc_diff_serials.fill_new(vols_of_lib_a, "2-9,11(3-4)"))
print(marc_diff_serials.fill_middle(vols_of_lib_a, "5-11"))
print(marc_diff_serials.middle_lack(vols_of_lib_a))
print(marc_diff_serials.marge_vols(vols_of_lib_a, "8-9,10(4)"))
```

## 例と出力

```python
vols_of_lib_a = "3(),4-6,9,10()"

# 補充可能な全巻
print(marc_diff_serials.fill_all(vols_of_lib_a, "2-11"))
# -> 2,3,7-8,10-11

# 古い巻の補充
print(marc_diff_serials.fill_old(vols_of_lib_a, "2(4-5),3-9"))
# -> 2(4-5)

# 新しい巻の補充
print(marc_diff_serials.fill_new(vols_of_lib_a, "2-9,11(3-4)"))
# -> 11(3-4)

# 途中欠号の補充
print(marc_diff_serials.fill_middle(vols_of_lib_a, "5-11"))
# -> 7-8,10

# 自館の途中欠号
print(marc_diff_serials.middle_lack(vols_of_lib_a))
# -> 3(),7-8,10()

# 2 館の所蔵をマージ
print(marc_diff_serials.marge_vols(vols_of_lib_a, "8-9,10(4)"))
# -> 3(),4-6,8-9,10()
```

## 記法

所蔵情報は次の形式を持つ文字列で表します。

- 数字: `3`
- 連続巻: `4-6`
- 不完全巻: `3()`
- 複数要素: `3(),4-6,9,10()`
- 数字と括弧の組み合わせ: `2(4-5)`

この実装では、`()` は「巻はあるが号や号の範囲は不明・未確定」を意味する表現として扱います。

## 関数一覧

### `fill_all(vols_a: str, vols_b: str) -> str`

図書館 A へ図書館 B から補充できる巻をまとめて返します。

### `fill_old(vols_a: str, vols_b: str) -> str`

図書館 A の最古巻より古い時期にあって、補充可能な巻を返します。

### `fill_new(vols_a: str, vols_b: str) -> str`

図書館 A の最新巻より新しい時期にあって、補充可能な巻を返します。

### `fill_middle(vols_a: str, vols_b: str) -> str`

図書館 A の途中欠号に該当する巻で、図書館 B に所蔵があるものを返します。

### `middle_lack(vols: str) -> str`

指定した所蔵表現に含まれる途中欠号を返します。

### `marge_vols(vols_a: str, vols_b: str) -> str`

2 館の所蔵を結合し、統合した所蔵表現を返します。

## 制約

- 巻号体系が途中で変わる形式（例: `45-54;1-4+`）には対応していません。
- 書式が不正な文字列は `ValueError` を送出します。
- 文字列の前後にある空白は自動的に除去されます。

## 参考

実際の使用例は `sample.py` を参照してください。
