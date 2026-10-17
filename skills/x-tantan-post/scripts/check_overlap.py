#!/usr/bin/env python3
"""新しい投稿案が過去の投稿と内容的に被っていないかを機械的にチェックする。

文字bigramのJaccard係数で類似度を出し、しきい値以上を「被り」として警告する。
文字が似ていなくても趣旨が同じケースは拾えないので、最終判断は目視で行うこと。

使い方:
  python3 check_overlap.py 新しい投稿.txt 過去投稿ファイル1 [過去投稿ファイル2 ...] [--threshold 0.18]

- 新しい投稿.txt は1行1投稿
- 過去投稿ファイルは .md ならコードブロック（```〜```）の中身を、それ以外は1行1投稿として読む
- 新しい投稿同士の被りもチェックする
"""
import argparse
import re
import sys

PUNCT = re.compile(r"[\s、。，．,.!！?？「」『』（）()・:：;；…ー〜~\-]")
CODE_BLOCK = re.compile(r"```\n(.*?)\n```", re.S)


def load_posts(path: str) -> list[str]:
    text = open(path, encoding="utf-8").read()
    if path.endswith(".md"):
        return [b.strip() for b in CODE_BLOCK.findall(text) if b.strip()]
    return [line.strip() for line in text.splitlines() if line.strip()]


def bigrams(text: str) -> set[str]:
    s = PUNCT.sub("", text)
    return {s[i : i + 2] for i in range(len(s) - 1)}


def similarity(a: str, b: str) -> float:
    x, y = bigrams(a), bigrams(b)
    return len(x & y) / len(x | y) if x and y else 0.0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("candidates")
    p.add_argument("history", nargs="+")
    p.add_argument("--threshold", type=float, default=0.18)
    args = p.parse_args()

    cands = load_posts(args.candidates)
    history = [(f, post) for f in args.history for post in load_posts(f)]
    flagged = 0
    for i, cand in enumerate(cands, 1):
        pool = history + [("今回の案", c) for j, c in enumerate(cands, 1) if j != i]
        score, src, match = max(((similarity(cand, h), f, h) for f, h in pool), default=(0.0, "", ""))
        mark = "被りの疑い" if score >= args.threshold else "OK"
        flagged += score >= args.threshold
        print(f"{i:>2}: {mark} 最大類似度 {score:.2f}  {cand[:20]}…")
        if score >= args.threshold:
            print(f"    似ている投稿（{src}）: {match[:40]}…")
    print(f"過去投稿 {len(history)} 本と照合。被りの疑い {flagged} 本（しきい値 {args.threshold}）")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
