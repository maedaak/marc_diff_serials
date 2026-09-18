import re
from typing import List, Union


def fill_all(vols_a: str, vols_b: str) -> str:
    """補充可能な巻をすべて取得する。"""
    a_lib = _check_vol_format(vols_a)
    b_lib = _check_vol_format(vols_b)
    fill_all_array: List[str] = []
    all_vols_array: List[str] = []

    old = fill_old(a_lib, b_lib)
    middle = fill_middle(a_lib, b_lib)
    new = fill_new(a_lib, b_lib)

    if old:
        all_vols_array.append(old)
    if middle:
        all_vols_array.append(middle)
    if new:
        all_vols_array.append(new)

    if not all_vols_array:
        return ""

    all_vols = ",".join(all_vols_array)

    for part in _div_serials(all_vols):
        if re.match(r"^\d+-\d+$", part):
            first = int(_get_first(part))
            last = int(_get_last(part))
            for v in range(first, last + 1):
                fill_all_array.append(str(v))
        else:
            fill_all_array.append(part)

    return _simple_checkin(fill_all_array)


def fill_old(vols_a: str, vols_b: str) -> str:
    """途中欠号のうち補充可能な古い巻を取得する。"""
    a_lib = _check_vol_format(vols_a)
    b_lib = _check_vol_format(vols_b)
    fill_old_array: List[str] = []

    first_a = int(re.sub(r"\(.*\)$", "", _get_first(a_lib)))
    first_b = int(re.sub(r"\(.*\)$", "", _get_first(b_lib)))

    if first_a <= first_b:
        return ""

    for part in _div_serials(b_lib):
        first_part = int(re.sub(r"\(.*\)$", "", _get_first(part)))
        last_part = int(re.sub(r"\(.*\)$", "", _get_last(part)))

        if first_part >= first_a:
            break

        if last_part >= first_a:
            if re.match(r"^\d+-\d+$", part):
                first_a_minus = first_a - 1
                part_first = int(_get_first(part))
                if part_first != first_a_minus:
                    part = re.sub(r"\d+$", str(first_a_minus), part)
                else:
                    part = re.sub(r"-\d+$", "", part)
                fill_old_array.append(part)
            break
        fill_old_array.append(part)

    return ",".join(fill_old_array)


def fill_new(vols_a: str, vols_b: str) -> str:
    """途中欠号のうち補充可能な新しい巻を取得する。"""
    a_lib = _check_vol_format(vols_a)
    b_lib = _check_vol_format(vols_b)
    fill_new_array: List[str] = []

    last_a = int(re.sub(r"\(.*\)$", "", _get_last(a_lib)))
    last_b = int(re.sub(r"\(.*\)$", "", _get_last(b_lib)))

    if last_a >= last_b:
        return ""

    for part in _div_serials(b_lib):
        first_part = int(re.sub(r"\(.*\)$", "", _get_first(part)))
        last_part = int(re.sub(r"\(.*\)$", "", _get_last(part)))

        if last_part > last_a:
            if first_part <= last_a:
                if re.match(r"^\d+-\d+$", part):
                    last_a_plus = last_a + 1
                    part_last = int(_get_last(part))
                    if part_last != last_a_plus:
                        part = re.sub(r"^\d+", str(last_a_plus), part)
                    else:
                        part = re.sub(r"^\d+-", "", part)
                    fill_new_array.append(part)
            else:
                fill_new_array.append(part)

    return ",".join(fill_new_array)


def fill_middle(vols_a: str, vols_b: str) -> str:
    """途中欠号のうち補充可能な中間の巻を取得する。"""
    a_lib = _check_vol_format(vols_a)
    b_lib = _check_vol_format(vols_b)
    fill_middle_array: List[str] = []

    middle_lack_str = middle_lack(a_lib)
    if not middle_lack_str:
        return ""

    for a_lib_part in _div_serials(middle_lack_str):
        if re.match(r"^\d+-\d+$", a_lib_part):
            first = int(_get_first(a_lib_part))
            last = int(_get_last(a_lib_part))
            for vol in range(first, last + 1):
                for b_lib_part in _div_serials(b_lib):
                    if re.match(r"^\d+(-\d+)*$", b_lib_part):
                        if _check_include(b_lib_part, vol):
                            fill_middle_array.append(str(vol))
                    elif re.match(rf"^{vol}\(*", b_lib_part):
                        if not _check_include(b_lib_part, vol):
                            fill_middle_array.append(b_lib_part)
        else:
            m = re.match(r"^(\d+)", a_lib_part)
            if m:
                a_lib_part_vol = m.group(1)
                if _check_include(b_lib, a_lib_part):
                    fill_middle_array.append(a_lib_part_vol)
                for b_lib_part in _div_serials(b_lib):
                    if re.match(rf"^{a_lib_part_vol}\(.*\)$", b_lib_part):
                        fill_middle_array.append(f"{a_lib_part_vol}()")
                        break

    if fill_middle_array:
        return _simple_checkin(fill_middle_array)
    return ""


def middle_lack(vols: str) -> str:
    """途中欠号を取得する。"""
    vol_string = _check_vol_format(vols)
    lack_vol: List[str] = []

    first_vol_str = re.sub(r"\(.*\)$", "", _get_first(vol_string))
    last_vol_str = re.sub(r"\(.*\)$", "", _get_last(vol_string))
    first_vol = int(first_vol_str)
    last_vol = int(last_vol_str)

    for vol in range(first_vol, last_vol + 1):
        found = False
        for part in _div_serials(vol_string):
            if re.match(r"^\d+\(.*\)$", part):
                part_clean = re.sub(r"\(.*\)$", "", part)
                if int(part_clean) == vol:
                    lack_vol.append(f"{vol}()")
                    found = True
                    break
            if _check_include(part, vol):
                found = True
                break
        if not found:
            lack_vol.append(str(vol))

    return _simple_checkin(lack_vol) if lack_vol else ""


def marge_vols(vols_a: str, vols_b: str) -> str:
    """2館の雑誌所蔵をマージする。"""
    a_lib = _check_vol_format(vols_a)
    b_lib = _check_vol_format(vols_b)

    fill_middle_str = fill_middle(a_lib, b_lib)
    fill_old_str = fill_old(a_lib, b_lib)
    fill_new_str = fill_new(a_lib, b_lib)

    a_lib_array = _div_serials(a_lib) if a_lib else []
    fill_old_array = _div_serials(fill_old_str) if fill_old_str else []
    fill_middle_array = _div_serials(fill_middle_str) if fill_middle_str else []
    fill_new_array = _div_serials(fill_new_str) if fill_new_str else []

    vols = {}
    combined = fill_old_array + a_lib_array + fill_middle_array + fill_new_array
    for part in combined:
        if re.match(r"^\d+-\d+$", part):
            first = int(_get_first(part))
            last = int(_get_last(part))
            for v in range(first, last + 1):
                vols[v] = str(v)
        else:
            m = re.match(r"^(\d+)", part)
            if m:
                vol = int(m.group(1))
                if (
                    vol in vols
                    and re.match(r"^\d+\(.*\)$", str(vols[vol]))
                    and re.match(r"^\d+\(.*\)$", part)
                ):
                    vols[vol] = f"{vol}()"
                else:
                    vols[vol] = part

    middle_vols_array = [vols[k] for k in sorted(vols.keys())]
    return _simple_checkin(middle_vols_array)


# --- 内部関数 ---


def _div_serials(vols: str) -> List[str]:
    parts = vols.split(",")
    div_serials: List[str] = []
    keep = ""
    switch = False

    for part in parts:
        if "(" in part and not part.endswith(")"):
            keep += part + ","
            switch = True
            continue
        if switch:
            if "(" not in part and part.endswith(")"):
                part = keep + part
                switch = False
                keep = ""
            else:
                keep += part + ","
                continue

        if not (
            re.match(r"^\d+\(.*\)$", part)
            or re.match(r"^\d+$", part)
            or re.match(r"^\d+-\d+$", part)
        ):
            raise ValueError("not a volume format!")
        div_serials.append(part)

    if keep or not div_serials:
        raise ValueError("not a volume format!")
    return div_serials


def _get_first(vols: str) -> str:
    parts = _div_serials(vols)
    first_part = parts[0]
    m = re.match(r"^(\d+(\(.*\))*)", first_part)
    if m:
        return m.group(1)
    raise ValueError("not a volume format!")


def _get_last(vols: str) -> str:
    parts = _div_serials(vols)
    last_part = parts[-1]
    if re.match(r"^\d+-\d+$", last_part):
        m = re.search(r"(\d+)$", last_part)
        if m:
            return m.group(1)
    elif re.match(r"^\d+(\(.*\))*$", last_part):
        return last_part

    raise ValueError("not a volume format!")


def _simple_checkin(vol_array: List[Union[str, int]]) -> str:
    if not vol_array:
        return ""
    str_vol_array = [str(v) for v in vol_array]

    if re.match(r"^\d+$", str_vol_array[0]):
        status = "S1"
    else:
        status = "S2"

    vol_string = str_vol_array[0]

    for i in range(1, len(str_vol_array)):
        curr = str_vol_array[i]
        prev = str_vol_array[i - 1]

        if status == "Cont":
            if re.match(r"^\d+$", curr):
                if int(prev) != int(curr) - 1:
                    vol_string += f"-{prev},{curr}"
                    status = "S1"
                elif i == len(str_vol_array) - 1:
                    vol_string += f"-{curr}"
            else:
                vol_string += f"-{prev},{curr}"
                status = "S2"
        elif status == "S1":
            if re.match(r"^\d+$", curr):
                if int(prev) == int(curr) - 1:
                    status = "Cont"
                    if i == len(str_vol_array) - 1:
                        vol_string += f"-{curr}"
                else:
                    vol_string += f",{curr}"
            else:
                vol_string += f",{curr}"
                status = "S2"
        elif status == "S2":
            vol_string += f",{curr}"
            if re.match(r"^\d+$", curr):
                status = "S1"
            else:
                status = "S2"

    return vol_string


def _check_include(vol_string: str, vol: Union[str, int]) -> bool:
    vol_str = re.sub(r"\(.*\)$", "", str(vol))
    if not vol_str.isdigit():
        return False
    vol_num = int(vol_str)

    for part in _div_serials(vol_string):
        if re.match(r"^\d+\(.*\)$", part):
            continue
        first_m = re.search(r"(\d+)", _get_first(part))
        last_m = re.search(r"(\d+)", _get_last(part))
        if first_m and last_m:
            first = int(first_m.group(1))
            last = int(last_m.group(1))
            if first <= vol_num <= last:
                return True
    return False


def _check_vol_format(vol: str) -> str:
    if not vol:
        raise ValueError("not a volume format!")
    vol = re.sub(r"\+$", "", vol)
    vol = re.sub(r"\s+", "", vol)
    if ";" in vol:
        raise ValueError("not support change volume!")
    if not re.match(r"^[\d(),-]+$", vol):
        raise ValueError("not a volume format!")

    first = _get_first(vol)
    first_vol_m = re.search(r"(\d+)", first)
    last = _get_last(vol)
    last_vol_m = re.search(r"(\d+)", last)

    if first_vol_m and last_vol_m:
        if int(first_vol_m.group(1)) > int(last_vol_m.group(1)):
            raise ValueError("first vol is larger than last vol!")
    return vol