#!/usr/bin/env python3
"""技リスト(CSV)をHTMLテンプレートに埋め込み、配布用の単一HTMLを作る。

使い方:
    python build.py skills.csv
    python build.py skills.csv -t scoresheet.html -o dist/scoresheet_2027.html

CSV:
    1行目はヘッダー(中身は何でもよい)。列順は  レベル, No., 技名, 英語名
    4列目(英語名)は空でもよい（英語表示ではその技だけ日本語名を使う）。
    文字コードは UTF-8 (BOM付き可) または Shift_JIS(CP932)。
    レベルは 1〜13、No.はレベル内で 1〜10。得点はレベルと同値なので書かない。

版名(画面右上に出る文字)はHTML内の  const EDITION = "...";  を直接編集する。
このスクリプトは技リストの部分(SKILLS_START〜SKILLS_END)だけを書き換える。
"""
import argparse
import csv
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

START, END = "/*SKILLS_START*/", "/*SKILLS_END*/"
MAX_LEVEL, MAX_NO = 13, 10


def read_text(path):
    raw = Path(path).read_bytes()
    for enc in ("utf-8-sig", "cp932"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    sys.exit(f"エラー: {path} の文字コードを判定できません（UTF-8 か Shift_JIS で保存してください）")


def load_skills(path):
    reader = csv.reader(io.StringIO(read_text(path)))
    skills, seen, errors = [], {}, []
    first = True
    for row in reader:
        line = reader.line_num
        if not any(c.strip() for c in row):
            continue  # 空行は無視
        if first:
            first = False
            if not row[0].strip().lstrip("-").isdigit():
                continue  # ヘッダー行
        if len(row) < 3:
            errors.append(f"{line}行目: 列が足りません（レベル, No., 技名 の3列が必要）")
            continue
        if any(c.strip() for c in row[4:]):
            errors.append(f"{line}行目: 列が多すぎます（レベル, No., 技名, 英語名 の4列まで。技名にカンマがある場合は \" で囲んでください）")
            continue
        level_s, no_s, name = row[0].strip(), row[1].strip(), row[2].strip()
        en = row[3].strip() if len(row) > 3 else ""
        try:
            level, no = int(level_s), int(no_s)
        except ValueError:
            errors.append(f"{line}行目: レベルまたはNo.が数値ではありません（{level_s!r}, {no_s!r}）")
            continue
        if not 1 <= level <= MAX_LEVEL:
            errors.append(f"{line}行目: レベルは1〜{MAX_LEVEL}です（{level}）")
            continue
        if not 1 <= no <= MAX_NO:
            errors.append(f"{line}行目: No.は1〜{MAX_NO}です（Lv{level}-{no}）")
            continue
        if not name:
            errors.append(f"{line}行目: 技名が空です（Lv{level}-{no}）")
            continue
        if (level, no) in seen:
            errors.append(f"{line}行目: Lv{level}-{no} が重複しています（{seen[(level, no)]}行目と同じ）")
            continue
        seen[(level, no)] = line
        skills.append((level, no, name, en))
    if not skills and not errors:
        errors.append("技が1件も読み込めませんでした")
    if errors:
        print("CSVにエラーがあります。ビルドを中止しました。", file=sys.stderr)
        for e in errors:
            print("  " + e, file=sys.stderr)
        sys.exit(1)
    return sorted(skills)


def to_js_array(skills):
    """JSの配列リテラルを作る（レベルごとに改行）。"""
    lines, cur, buf = [], None, []
    for level, no, name, en in skills:
        if cur is not None and level != cur:
            lines.append(",".join(buf))
            buf = []
        cur = level
        buf.append("[%d,%d,%s,%s]" % (level, no, json.dumps(name, ensure_ascii=False), json.dumps(en, ensure_ascii=False)))
    lines.append(",".join(buf))
    text = "[\n" + ",\n".join(lines) + "\n]"
    # <script>内で安全にする
    return text.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def main():
    ap = argparse.ArgumentParser(description="技リストCSVをHTMLに埋め込んで配布版を作る")
    ap.add_argument("csv", help="技リストのCSV")
    ap.add_argument("-t", "--template", default=str(Path(__file__).with_name("scoresheet.html")),
                    help="HTMLテンプレート（既定: build.pyと同じ場所の scoresheet.html）")
    ap.add_argument("-o", "--output", default="dist/scoresheet.html", help="出力先（既定: dist/scoresheet.html）")
    a = ap.parse_args()

    tpl_path, out_path = Path(a.template), Path(a.output)
    if tpl_path.resolve() == out_path.resolve():
        sys.exit("エラー: 出力先がテンプレートと同じです")
    html = tpl_path.read_text(encoding="utf-8")
    if html.count(START) != 1 or html.count(END) != 1:
        sys.exit(f"エラー: テンプレートに {START} と {END} が1組だけ必要です")
    i, j = html.index(START) + len(START), html.index(END)
    if i > j:
        sys.exit("エラー: SKILLS_START が SKILLS_END より後ろにあります")

    skills = load_skills(a.csv)
    out = html[:i] + to_js_array(skills) + html[j:]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out, encoding="utf-8")

    m = re.search(r'^const\s+EDITION\s*=\s*"(.*?)"', out, re.M)
    counts = Counter(sk[0] for sk in skills)
    print(f"作成しました: {out_path}")
    print(f"  版名: {m.group(1) if m else '（EDITION が見つかりません）'}")
    print(f"  技数: {len(skills)}  （" + " / ".join(f"Lv{l}:{counts[l]}" for l in sorted(counts)) + "）")
    no_en = sum(1 for sk in skills if not sk[3])
    if no_en:
        print(f"  英語名なし: {no_en}件（英語表示ではその技だけ日本語名を表示）")


if __name__ == "__main__":
    main()
