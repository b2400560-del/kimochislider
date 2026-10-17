#!/usr/bin/env python3
"""X（無料版）の加重文字数を数える。1行=1投稿として読み、上限280を超えていないか判定する。

使い方:
  python3 count_x.py posts.txt
  echo "投稿本文" | python3 count_x.py
"""
import re
import sys

LIMIT = 280
# twitter-text v3 の重み1の範囲。これ以外（日本語・全角記号・絵文字など）は重み2
WEIGHT1 = [(0, 4351), (8192, 8205), (8208, 8223), (8242, 8247)]
URL = re.compile(r"https?://\S+")


def weighted_len(text: str) -> int:
    text = URL.sub("x" * 23, text)  # URLは長さに関係なく23
    return sum(1 if any(a <= ord(c) <= b for a, b in WEIGHT1) else 2 for c in text)


def main() -> int:
    src = open(sys.argv[1], encoding="utf-8") if len(sys.argv) > 1 else sys.stdin
    posts = [line.rstrip("\n") for line in src if line.strip()]
    over = 0
    for i, post in enumerate(posts, 1):
        n = weighted_len(post)
        status = "OK" if n <= LIMIT else "OVER"
        over += n > LIMIT
        print(f"{i:>2}: {n:>3}/{LIMIT} {status}  {post[:20]}…")
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
